"""IPAM-tjenester (IPv4 prefiks, scoped per site)."""

from __future__ import annotations

import ipaddress

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.dcim import (
    DeviceInstance,
    DeviceInterface,
    InterfaceIpAssignment,
    Rack,
    RackPlacement,
    Room,
)
from app.models.ipam import IpamIpv4Prefix
from app.schemas.ipam import Ipv4PrefixCreate, Ipv4PrefixRead, Ipv4PrefixUpdate
from app.services import dcim as dcim_svc


def _ipv4_address_total(cidr: str) -> int:
    net = ipaddress.ip_network(cidr, strict=False)
    if net.version != 4:
        return 0
    return int(net.num_addresses)


def _ipv4_assignments_with_site(db: Session) -> list[tuple[ipaddress.IPv4Address, int]]:
    """IPv4-tildelinger på plasserte enheter: (adresse, site_id)."""
    q = (
        select(InterfaceIpAssignment.address, Room.site_id)
        .join(DeviceInterface, DeviceInterface.id == InterfaceIpAssignment.interface_id)
        .join(DeviceInstance, DeviceInstance.id == DeviceInterface.device_id)
        .join(RackPlacement, RackPlacement.device_id == DeviceInstance.id)
        .join(Rack, Rack.id == RackPlacement.rack_id)
        .join(Room, Room.id == Rack.room_id)
        .where(InterfaceIpAssignment.family == "ipv4")
    )
    out: list[tuple[ipaddress.IPv4Address, int]] = []
    for addr, sid in db.execute(q).all():
        try:
            ip = ipaddress.ip_address(str(addr).strip())
            if isinstance(ip, ipaddress.IPv4Address):
                out.append((ip, int(sid)))
        except ValueError:
            continue
    return out


def _used_count_in_network(
    cidr: str,
    site_id: int,
    cache: list[tuple[ipaddress.IPv4Address, int]],
) -> int:
    try:
        net = ipaddress.ip_network(cidr, strict=False)
    except ValueError:
        return 0
    if net.version != 4:
        return 0
    return sum(1 for ip, sid in cache if sid == site_id and ip in net)


def ipv4_prefix_read(
    db: Session,
    row: IpamIpv4Prefix,
    *,
    _cache: list[tuple[ipaddress.IPv4Address, int]] | None = None,
) -> Ipv4PrefixRead:
    cache = _ipv4_assignments_with_site(db) if _cache is None else _cache
    used = _used_count_in_network(row.cidr, row.site_id, cache)
    return Ipv4PrefixRead(
        id=row.id,
        site_id=row.site_id,
        name=row.name,
        cidr=row.cidr,
        description=row.description,
        created_at=row.created_at,
        used_count=used,
        address_total=_ipv4_address_total(row.cidr),
    )


def _normalize_ipv4_cidr(raw: str) -> str:
    try:
        net = ipaddress.ip_network(raw.strip(), strict=False)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"ugyldig IPv4 CIDR: {e}") from e
    if net.version != 4:
        raise HTTPException(status_code=400, detail="kun IPv4-støtte i denne endepunktet")
    return f"{net.network_address}/{net.prefixlen}"


def list_ipv4_prefixes(db: Session, *, site_id: int | None) -> list[Ipv4PrefixRead]:
    q = select(IpamIpv4Prefix).order_by(IpamIpv4Prefix.site_id, IpamIpv4Prefix.cidr)
    if site_id is not None:
        q = q.where(IpamIpv4Prefix.site_id == site_id)
    rows = list(db.execute(q).scalars().all())
    cache = _ipv4_assignments_with_site(db)
    return [ipv4_prefix_read(db, r, _cache=cache) for r in rows]


def get_ipv4_prefix(db: Session, prefix_id: int) -> IpamIpv4Prefix | None:
    return db.get(IpamIpv4Prefix, prefix_id)


def create_ipv4_prefix(db: Session, data: Ipv4PrefixCreate) -> Ipv4PrefixRead:
    if dcim_svc.get_site(db, data.site_id) is None:
        raise HTTPException(status_code=404, detail="site ikke funnet")
    cidr = _normalize_ipv4_cidr(data.cidr)
    row = IpamIpv4Prefix(
        site_id=data.site_id,
        name=data.name.strip(),
        cidr=cidr,
        description=data.description,
    )
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="prefiks med samme CIDR finnes allerede på denne siten",
        ) from None
    db.refresh(row)
    return ipv4_prefix_read(db, row)


def update_ipv4_prefix(db: Session, row: IpamIpv4Prefix, data: Ipv4PrefixUpdate) -> Ipv4PrefixRead:
    patch = data.model_dump(exclude_unset=True)
    if not patch:
        raise HTTPException(status_code=400, detail="ingen felter å oppdatere")
    if "name" in patch and patch["name"] is not None:
        row.name = str(patch["name"]).strip()
    if "description" in patch:
        v = patch["description"]
        row.description = None if v is None else (str(v).strip() or None)
    if "cidr" in patch and patch["cidr"] is not None:
        row.cidr = _normalize_ipv4_cidr(patch["cidr"])
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="prefiks med samme CIDR finnes allerede på denne siten",
        ) from None
    db.refresh(row)
    return ipv4_prefix_read(db, row)


def delete_ipv4_prefix(db: Session, row: IpamIpv4Prefix) -> None:
    db.delete(row)
    db.commit()
