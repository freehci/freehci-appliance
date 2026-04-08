"""IPAM-tjenester (IPv4 prefiks, scoped per site)."""

from __future__ import annotations

import ipaddress

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.dcim import InterfaceIpAssignment
from app.models.ipam import IpamIpv4Prefix
from app.schemas.ipam import Ipv4PrefixCreate, Ipv4PrefixRead, Ipv4PrefixUpdate
from app.services import dcim as dcim_svc


def _ipv4_address_total(cidr: str) -> int:
    net = ipaddress.ip_network(cidr, strict=False)
    if net.version != 4:
        return 0
    return int(net.num_addresses)


def _assignment_counts_by_prefix(db: Session) -> dict[int, int]:
    q = (
        select(InterfaceIpAssignment.ipv4_prefix_id, func.count(InterfaceIpAssignment.id))
        .where(InterfaceIpAssignment.ipv4_prefix_id.is_not(None))
        .group_by(InterfaceIpAssignment.ipv4_prefix_id)
    )
    return {int(pid): int(n) for pid, n in db.execute(q).all() if pid is not None}


def _count_assignments_for_prefix(db: Session, prefix_id: int) -> int:
    q = select(func.count()).select_from(InterfaceIpAssignment).where(
        InterfaceIpAssignment.ipv4_prefix_id == prefix_id,
    )
    return int(db.execute(q).scalar_one())


def ipv4_prefix_read(db: Session, row: IpamIpv4Prefix) -> Ipv4PrefixRead:
    used = _count_assignments_for_prefix(db, row.id)
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
    counts = _assignment_counts_by_prefix(db)
    return [
        Ipv4PrefixRead(
            id=r.id,
            site_id=r.site_id,
            name=r.name,
            cidr=r.cidr,
            description=r.description,
            created_at=r.created_at,
            used_count=counts.get(r.id, 0),
            address_total=_ipv4_address_total(r.cidr),
        )
        for r in rows
    ]


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
