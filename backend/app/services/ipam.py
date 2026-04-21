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
from app.schemas.ipam import (
    Ipv4AssignmentInPrefixRead,
    Ipv4PrefixCreate,
    Ipv4PrefixExploreRead,
    Ipv4PrefixRead,
    Ipv4PrefixUpdate,
)
from app.services import dcim as dcim_svc
from app.services import tenant as tenant_svc
from app.services import ipam_facilities as fac_svc


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


def _prefix_sort_key(row: IpamIpv4Prefix) -> tuple[int, str]:
    """Bredeste prefiks først (lavest prefixlen), deretter adresse."""
    net = ipaddress.ip_network(row.cidr, strict=False)
    return (net.prefixlen, str(net.network_address))


def _child_prefix_orms(
    parent: IpamIpv4Prefix,
    same_site_rows: list[IpamIpv4Prefix],
) -> list[IpamIpv4Prefix]:
    """Andre prefiks på samme site som er strengere delnett av parent."""
    try:
        parent_net = ipaddress.ip_network(parent.cidr, strict=False)
    except ValueError:
        return []
    if parent_net.version != 4:
        return []
    out: list[IpamIpv4Prefix] = []
    for o in same_site_rows:
        if o.id == parent.id:
            continue
        try:
            on = ipaddress.ip_network(o.cidr, strict=False)
        except ValueError:
            continue
        if on.version != 4:
            continue
        if on.prefixlen <= parent_net.prefixlen:
            continue
        if on.subnet_of(parent_net):
            out.append(o)
    out.sort(key=_prefix_sort_key)
    return out


def _assignment_rows_in_prefix(db: Session, parent: IpamIpv4Prefix) -> list[Ipv4AssignmentInPrefixRead]:
    try:
        parent_net = ipaddress.ip_network(parent.cidr, strict=False)
    except ValueError:
        return []
    if parent_net.version != 4:
        return []
    q = (
        select(
            InterfaceIpAssignment.id,
            InterfaceIpAssignment.address,
            InterfaceIpAssignment.ipv4_prefix_id,
            DeviceInterface.id,
            DeviceInterface.name,
            DeviceInstance.id,
            DeviceInstance.name,
        )
        .join(DeviceInterface, DeviceInterface.id == InterfaceIpAssignment.interface_id)
        .join(DeviceInstance, DeviceInstance.id == DeviceInterface.device_id)
        .join(RackPlacement, RackPlacement.device_id == DeviceInstance.id)
        .join(Rack, Rack.id == RackPlacement.rack_id)
        .join(Room, Room.id == Rack.room_id)
        .where(InterfaceIpAssignment.family == "ipv4", Room.site_id == parent.site_id)
    )
    out: list[Ipv4AssignmentInPrefixRead] = []
    for a_id, addr, pfx_id, if_id, if_name, dev_id, dev_name in db.execute(q).all():
        try:
            ip = ipaddress.ip_address(str(addr).strip())
            if not isinstance(ip, ipaddress.IPv4Address) or ip not in parent_net:
                continue
            out.append(
                Ipv4AssignmentInPrefixRead(
                    assignment_id=int(a_id),
                    address=str(ip),
                    ipv4_prefix_id=pfx_id,
                    interface_id=int(if_id),
                    interface_name=str(if_name),
                    device_id=int(dev_id),
                    device_name=str(dev_name),
                )
            )
        except ValueError:
            continue
    out.sort(key=lambda x: ipaddress.ip_address(x.address))
    return out


def ipv4_assignments_for_prefix_id(db: Session, prefix_id: int) -> list[Ipv4AssignmentInPrefixRead]:
    """DCIM IPv4-tildelinger innenfor et prefiks (for adressegitter m.m.)."""
    row = get_ipv4_prefix(db, prefix_id)
    if row is None:
        raise HTTPException(status_code=404, detail="prefiks ikke funnet")
    return _assignment_rows_in_prefix(db, row)


def explore_ipv4_prefix(db: Session, prefix_id: int) -> Ipv4PrefixExploreRead:
    row = get_ipv4_prefix(db, prefix_id)
    if row is None:
        raise HTTPException(status_code=404, detail="prefiks ikke funnet")
    same_site = list(
        db.execute(select(IpamIpv4Prefix).where(IpamIpv4Prefix.site_id == row.site_id)).scalars().all(),
    )
    cache = _ipv4_assignments_with_site(db)
    children = _child_prefix_orms(row, same_site)
    child_reads = [ipv4_prefix_read(db, c, _cache=cache) for c in children]
    assigns = _assignment_rows_in_prefix(db, row)
    return Ipv4PrefixExploreRead(
        prefix=ipv4_prefix_read(db, row, _cache=cache),
        child_prefixes=child_reads,
        assignments=assigns,
    )


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
        tenant_id=row.tenant_id,
        vlan_id=getattr(row, "vlan_id", None),
        name=row.name,
        cidr=row.cidr,
        description=row.description,
        created_at=row.created_at,
        used_count=used,
        address_total=_ipv4_address_total(row.cidr),
        subnet_services=getattr(row, "subnet_services", None),
    )


def _normalize_ipv4_cidr(raw: str) -> str:
    try:
        net = ipaddress.ip_network(raw.strip(), strict=False)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"ugyldig IPv4 CIDR: {e}") from e
    if net.version != 4:
        raise HTTPException(status_code=400, detail="kun IPv4-støtte i denne endepunktet")
    return f"{net.network_address}/{net.prefixlen}"


def list_ipv4_prefixes(db: Session, *, site_id: int | None, tenant_id: int | None = None) -> list[Ipv4PrefixRead]:
    q = select(IpamIpv4Prefix).order_by(IpamIpv4Prefix.site_id, IpamIpv4Prefix.cidr)
    if site_id is not None:
        q = q.where(IpamIpv4Prefix.site_id == site_id)
    if tenant_id is not None:
        q = q.where(IpamIpv4Prefix.tenant_id == tenant_id)
    rows = list(db.execute(q).scalars().all())
    rows.sort(key=_prefix_sort_key)
    cache = _ipv4_assignments_with_site(db)
    return [ipv4_prefix_read(db, r, _cache=cache) for r in rows]


def get_ipv4_prefix(db: Session, prefix_id: int) -> IpamIpv4Prefix | None:
    return db.get(IpamIpv4Prefix, prefix_id)


def create_ipv4_prefix(db: Session, data: Ipv4PrefixCreate) -> Ipv4PrefixRead:
    if dcim_svc.get_site(db, data.site_id) is None:
        raise HTTPException(status_code=404, detail="site ikke funnet")
    if data.tenant_id is not None and tenant_svc.get_tenant(db, data.tenant_id) is None:
        raise HTTPException(status_code=404, detail="tenant ikke funnet")
    if data.vlan_id is not None:
        v = fac_svc.get_vlan(db, int(data.vlan_id))
        if v is None:
            raise HTTPException(status_code=404, detail="vlan ikke funnet")
        if v.site_id != data.site_id:
            raise HTTPException(status_code=400, detail="vlan tilhører ikke samme site")
    cidr = _normalize_ipv4_cidr(data.cidr)
    row = IpamIpv4Prefix(
        site_id=data.site_id,
        tenant_id=data.tenant_id,
        vlan_id=data.vlan_id,
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
    if "subnet_services" in patch:
        row.subnet_services = patch["subnet_services"]
    if "tenant_id" in patch:
        tid = patch["tenant_id"]
        if tid is not None and tenant_svc.get_tenant(db, int(tid)) is None:
            raise HTTPException(status_code=404, detail="tenant ikke funnet")
        row.tenant_id = tid
    if "vlan_id" in patch:
        vid = patch["vlan_id"]
        if vid is None:
            row.vlan_id = None
        else:
            v = fac_svc.get_vlan(db, int(vid))
            if v is None:
                raise HTTPException(status_code=404, detail="vlan ikke funnet")
            if v.site_id != row.site_id:
                raise HTTPException(status_code=400, detail="vlan tilhører ikke samme site")
            row.vlan_id = int(vid)
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
