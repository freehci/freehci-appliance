"""IPAM-tjenester (IPv4 prefiks, scoped per site)."""

from __future__ import annotations

import datetime as dt
import ipaddress
import re

from fastapi import HTTPException
from sqlalchemy import func, select
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
from app.models.ipam import IpamIpv4Address, IpamIpv4Prefix
from app.schemas.ipam import (
    NO_HOST_ALLOC_ROLES,
    NO_HOST_ALLOC_STATUSES,
    NO_VLAN_ROLES,
    Ipv4AssignmentInPrefixRead,
    Ipv4PrefixCreate,
    Ipv4PrefixEnsure,
    Ipv4PrefixExploreRead,
    Ipv4PrefixRead,
    Ipv4PrefixUpdate,
    SubnetServices,
    parse_subnet_services,
)
from app.services import dcim as dcim_svc
from app.services import tenant as tenant_svc
from app.services import ipam_facilities as fac_svc
from app.services.ipam_errors import ipam_error
from app.services import ipam_audit as audit_svc
from app.services import ipam_etag as etag_svc

_INVENTORY_USED_STATUSES = frozenset({"reserved", "assigned"})
OVERLAP_POLICIES = frozenset({"site-local", "global-unique"})
GLOBAL_UNIQUE_ROLES = frozenset({"overlay-pod", "overlay-service", "lb-pool", "p2p"})


def resolve_overlap_policy(role: str, explicit: str | None = None) -> str:
    if explicit:
        s = explicit.strip().lower()
        if s not in OVERLAP_POLICIES:
            raise ipam_error(400, "invalid_overlap_policy", "overlap_policy må være site-local eller global-unique")
        return s
    return "global-unique" if role in GLOBAL_UNIQUE_ROLES else "site-local"


def slugify_prefix(value: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", (value or "").strip().lower()).strip("-")
    return (s or "prefix")[:128]


def allocate_prefix_slug(
    db: Session,
    *,
    site_id: int,
    desired: str,
    exclude_prefix_id: int | None = None,
    reserved: set[str] | None = None,
    allow_suffix: bool = True,
) -> str:
    base = slugify_prefix(desired)
    candidate = base
    n = 2
    while True:
        taken = reserved is not None and candidate in reserved
        if not taken:
            q = select(IpamIpv4Prefix.id).where(
                IpamIpv4Prefix.site_id == site_id,
                IpamIpv4Prefix.slug == candidate,
            )
            if exclude_prefix_id is not None:
                q = q.where(IpamIpv4Prefix.id != exclude_prefix_id)
            taken = db.execute(q).scalar_one_or_none() is not None
        if not taken:
            if reserved is not None:
                reserved.add(candidate)
            return candidate
        if not allow_suffix:
            raise ipam_error(409, "slug_taken", "slug finnes allerede på denne siten")
        suffix = f"-{n}"
        candidate = f"{base[: 128 - len(suffix)]}{suffix}"
        n += 1
        if n > 1000:
            raise ipam_error(400, "slug_exhausted", "kunne ikke lage unik slug")


def vrf_scope_of(vrf_id: int | None) -> int:
    return int(vrf_id) if vrf_id is not None else 0


def dump_subnet_services(raw: object) -> dict | None:
    if raw is None:
        return None
    if isinstance(raw, SubnetServices):
        return raw.model_dump()
    try:
        return parse_subnet_services(raw)
    except Exception as e:
        raise ipam_error(400, "invalid_subnet_services", str(e)) from e


def prefix_role(row: IpamIpv4Prefix) -> str:
    return getattr(row, "role", None) or "active"


def prefix_status(row: IpamIpv4Prefix) -> str:
    return getattr(row, "status", None) or "active"


def require_host_allocation(pfx: IpamIpv4Prefix) -> None:
    role = prefix_role(pfx)
    status = prefix_status(pfx)
    if role in NO_HOST_ALLOC_ROLES:
        raise ipam_error(
            409,
            "prefix_role_forbids_alloc",
            f"prefiks-rolle {role} tillater ikke host-allokering",
            role=role,
        )
    if status in NO_HOST_ALLOC_STATUSES:
        raise ipam_error(
            409,
            "prefix_status_forbids_alloc",
            f"prefiks-status {status} tillater ikke host-allokering",
            status=status,
        )


def require_vlan_allowed(role: str, vlan_id: int | None) -> None:
    if vlan_id is not None and role in NO_VLAN_ROLES:
        raise ipam_error(
            400,
            "prefix_role_forbids_vlan",
            f"prefiks-rolle {role} skal ikke ha VLAN",
            role=role,
        )


def new_ipv4_prefix_orm(
    db: Session,
    *,
    site_id: int,
    name: str,
    cidr: str,
    slug: str | None = None,
    role: str = "active",
    status: str = "active",
    description: str | None = None,
    subnet_services: dict | None = None,
    tenant_id: int | None = None,
    vlan_id: int | None = None,
    vrf_id: int | None = None,
    reserved_slugs: set[str] | None = None,
    overlap_policy: str | None = None,
    dual_stack_group_id: int | None = None,
) -> IpamIpv4Prefix:
    explicit = slug is not None
    require_vlan_allowed(role, vlan_id)
    return IpamIpv4Prefix(
        site_id=site_id,
        tenant_id=tenant_id,
        vlan_id=vlan_id,
        vrf_id=vrf_id,
        vrf_scope=vrf_scope_of(vrf_id),
        name=name.strip(),
        slug=allocate_prefix_slug(
            db,
            site_id=site_id,
            desired=slug or name or cidr,
            reserved=reserved_slugs,
            allow_suffix=not explicit,
        ),
        role=role,
        status=status,
        overlap_policy=resolve_overlap_policy(role, overlap_policy),
        dual_stack_group_id=dual_stack_group_id,
        description=description,
        cidr=cidr,
        subnet_services=subnet_services,
    )


def _ipv4_address_total(cidr: str) -> int:
    net = ipaddress.ip_network(cidr, strict=False)
    if net.version != 4:
        return 0
    return int(net.num_addresses)


def _ipv4_assignments_with_site(db: Session) -> list[tuple[ipaddress.IPv4Address, int]]:
    """IPv4-tildelinger: (adresse, site_id) fra device.site_id eller rack → rom."""
    q = (
        select(InterfaceIpAssignment.address, DeviceInstance.site_id, Room.site_id)
        .join(DeviceInterface, DeviceInterface.id == InterfaceIpAssignment.interface_id)
        .join(DeviceInstance, DeviceInstance.id == DeviceInterface.device_id)
        .outerjoin(RackPlacement, RackPlacement.device_id == DeviceInstance.id)
        .outerjoin(Rack, Rack.id == RackPlacement.rack_id)
        .outerjoin(Room, Room.id == Rack.room_id)
        .where(InterfaceIpAssignment.family == "ipv4")
    )
    out: list[tuple[ipaddress.IPv4Address, int]] = []
    for addr, dev_site, room_site in db.execute(q).all():
        sid = dev_site if dev_site is not None else room_site
        if sid is None:
            continue
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


def _immediate_parent_row(child: IpamIpv4Prefix, same_site_rows: list[IpamIpv4Prefix]) -> IpamIpv4Prefix | None:
    """Nærmeste «omsluttende» prefiks på samme site (strammeste supernett i databasen)."""
    try:
        child_net = ipaddress.ip_network(child.cidr, strict=False)
    except ValueError:
        return None
    if child_net.version != 4:
        return None
    best: IpamIpv4Prefix | None = None
    best_pl = -1
    for p in same_site_rows:
        if p.id == child.id:
            continue
        if vrf_scope_of(getattr(p, "vrf_id", None)) != vrf_scope_of(getattr(child, "vrf_id", None)):
            continue
        try:
            p_net = ipaddress.ip_network(p.cidr, strict=False)
        except ValueError:
            continue
        if p_net.version != 4:
            continue
        if not child_net.subnet_of(p_net) or child_net.prefixlen <= p_net.prefixlen:
            continue
        if p_net.prefixlen > best_pl:
            best_pl = p_net.prefixlen
            best = p
    return best


def _child_prefix_orms(
    parent: IpamIpv4Prefix,
    same_site_rows: list[IpamIpv4Prefix],
) -> list[IpamIpv4Prefix]:
    """Direkte underprefiks: strengere CIDR der nærmeste forelder i DB er `parent`."""
    out: list[IpamIpv4Prefix] = []
    for c in same_site_rows:
        if c.id == parent.id:
            continue
        ipar = _immediate_parent_row(c, same_site_rows)
        if ipar is not None and ipar.id == parent.id:
            out.append(c)
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
        raise ipam_error(404, "prefix_not_found", "prefiks ikke funnet")
    return _assignment_rows_in_prefix(db, row)


def explore_ipv4_prefix(db: Session, prefix_id: int) -> Ipv4PrefixExploreRead:
    row = get_ipv4_prefix(db, prefix_id)
    if row is None:
        raise ipam_error(404, "prefix_not_found", "prefiks ikke funnet")
    same_site = list(
        db.execute(select(IpamIpv4Prefix).where(IpamIpv4Prefix.site_id == row.site_id)).scalars().all(),
    )
    cache = _ipv4_assignments_with_site(db)
    inv_cache = _ipv4_inventory_used_with_site(db)
    children = _child_prefix_orms(row, same_site)
    child_reads = [
        ipv4_prefix_read(db, c, _cache=cache, _inventory_cache=inv_cache, _same_site=same_site) for c in children
    ]
    assigns = _assignment_rows_in_prefix(db, row)
    return Ipv4PrefixExploreRead(
        prefix=ipv4_prefix_read(db, row, _cache=cache, _inventory_cache=inv_cache, _same_site=same_site),
        child_prefixes=child_reads,
        assignments=assigns,
    )


def _ipv4_inventory_used_with_site(db: Session) -> list[tuple[ipaddress.IPv4Address, int]]:
    """Inventory-adresser med status reserved|assigned: (adresse, site_id)."""
    q = select(IpamIpv4Address.address, IpamIpv4Address.site_id).where(
        IpamIpv4Address.status.in_(tuple(_INVENTORY_USED_STATUSES)),
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
    dcim_cache: list[tuple[ipaddress.IPv4Address, int]],
    inventory_cache: list[tuple[ipaddress.IPv4Address, int]],
) -> int:
    try:
        net = ipaddress.ip_network(cidr, strict=False)
    except ValueError:
        return 0
    if net.version != 4:
        return 0
    used: set[str] = set()
    for ip, sid in dcim_cache:
        if sid == site_id and ip in net:
            used.add(str(ip))
    for ip, sid in inventory_cache:
        if sid == site_id and ip in net:
            used.add(str(ip))
    return len(used)


def _usable_hosts(cidr: str) -> int:
    total = _ipv4_address_total(cidr)
    try:
        net = ipaddress.ip_network(cidr, strict=False)
    except ValueError:
        return total
    if net.version == 4 and net.prefixlen <= 30:
        return max(total - 2, 0)
    return total


def ipv4_prefix_read(
    db: Session,
    row: IpamIpv4Prefix,
    *,
    _cache: list[tuple[ipaddress.IPv4Address, int]] | None = None,
    _inventory_cache: list[tuple[ipaddress.IPv4Address, int]] | None = None,
    _same_site: list[IpamIpv4Prefix] | None = None,
    created: bool | None = None,
) -> Ipv4PrefixRead:
    cache = _ipv4_assignments_with_site(db) if _cache is None else _cache
    inv_cache = _ipv4_inventory_used_with_site(db) if _inventory_cache is None else _inventory_cache
    used = _used_count_in_network(row.cidr, row.site_id, cache, inv_cache)
    slug = getattr(row, "slug", None) or slugify_prefix(row.name or row.cidr)
    same_site = _same_site
    if same_site is None:
        same_site = list(
            db.execute(select(IpamIpv4Prefix).where(IpamIpv4Prefix.site_id == row.site_id)).scalars().all(),
        )
    parent = _immediate_parent_row(row, same_site)
    usable = _usable_hosts(row.cidr)
    try:
        services = parse_subnet_services(getattr(row, "subnet_services", None))
    except Exception:
        services = getattr(row, "subnet_services", None)
    return Ipv4PrefixRead(
        id=row.id,
        site_id=row.site_id,
        tenant_id=row.tenant_id,
        vlan_id=getattr(row, "vlan_id", None),
        vrf_id=getattr(row, "vrf_id", None),
        name=row.name,
        slug=slug,
        role=prefix_role(row),
        status=prefix_status(row),
        cidr=row.cidr,
        description=row.description,
        created_at=row.created_at,
        updated_at=getattr(row, "updated_at", None),
        parent_id=parent.id if parent is not None else None,
        used_count=used,
        address_total=_ipv4_address_total(row.cidr),
        usable_hosts=usable,
        utilization=(used / usable) if usable else 0.0,
        created=created,
        subnet_services=services,
        overlap_policy=getattr(row, "overlap_policy", None) or "site-local",
        dual_stack_group_id=getattr(row, "dual_stack_group_id", None),
        etag=etag_svc.format_etag(row),
    )


def _normalize_ipv4_cidr(raw: str) -> str:
    try:
        net = ipaddress.ip_network(raw.strip(), strict=False)
    except ValueError as e:
        raise ipam_error(400, "invalid_cidr", f"ugyldig IPv4 CIDR: {e}") from e
    if net.version != 4:
        raise ipam_error(400, "ipv4_only", "kun IPv4-støtte i denne endepunktet")
    return f"{net.network_address}/{net.prefixlen}"


def _require_no_partial_overlap(
    db: Session,
    *,
    site_id: int,
    cidr: str,
    vrf_id: int | None,
    exclude_prefix_id: int | None = None,
) -> None:
    """Delvis overlap stoppes innenfor samme site + VRF-scope. Hierarki er tillatt."""
    try:
        new_net = ipaddress.ip_network(cidr, strict=False)
    except ValueError:
        return
    if new_net.version != 4:
        return

    scope = vrf_scope_of(vrf_id)
    q = select(IpamIpv4Prefix).where(IpamIpv4Prefix.site_id == site_id)
    if exclude_prefix_id is not None:
        q = q.where(IpamIpv4Prefix.id != exclude_prefix_id)
    rows = db.execute(q).scalars().all()
    for r in rows:
        if vrf_scope_of(getattr(r, "vrf_id", None)) != scope:
            continue
        try:
            other = ipaddress.ip_network(r.cidr, strict=False)
        except ValueError:
            continue
        if other.version != 4:
            continue
        if not new_net.overlaps(other):
            continue
        if new_net.subnet_of(other) or other.subnet_of(new_net):
            continue
        raise ipam_error(
            409,
            "prefix_partial_overlap",
            f"prefiks {cidr} overlapper delvis med eksisterende prefiks {r.cidr} (id={r.id}) i samme VRF",
            other_id=r.id,
            other_cidr=r.cidr,
        )


def require_no_global_overlap(
    db: Session,
    *,
    site_id: int,
    cidr: str,
    policy: str,
    exclude_prefix_id: int | None = None,
    version: int = 4,
) -> None:
    """global-unique: CIDR kan ikke overlappe et prefiks på en annen site."""
    try:
        new_net = ipaddress.ip_network(cidr, strict=False)
    except ValueError:
        return
    if new_net.version != version:
        return
    from app.models.ipam import IpamIpv6Prefix

    model = IpamIpv4Prefix if version == 4 else IpamIpv6Prefix
    q = select(model)
    if exclude_prefix_id is not None:
        q = q.where(model.id != exclude_prefix_id)
    for r in db.execute(q).scalars().all():
        if int(r.site_id) == site_id:
            continue
        other_policy = getattr(r, "overlap_policy", None) or "site-local"
        if policy != "global-unique" and other_policy != "global-unique":
            continue
        try:
            other = ipaddress.ip_network(r.cidr, strict=False)
        except ValueError:
            continue
        if other.version != version:
            continue
        if new_net.overlaps(other):
            raise ipam_error(
                409,
                "prefix_global_overlap",
                f"prefiks {cidr} overlapper {r.cidr} på site {r.site_id} (global-unique)",
                other_id=r.id,
                other_cidr=r.cidr,
                other_site_id=r.site_id,
            )


def list_ipv4_prefixes(
    db: Session,
    *,
    site_id: int | None,
    tenant_id: int | None = None,
    vlan_id: int | None = None,
    vrf_id: int | None = None,
    cidr: str | None = None,
    name: str | None = None,
    slug: str | None = None,
    q: str | None = None,
    address: str | None = None,
    role: str | None = None,
    status: str | None = None,
    limit: int | None = None,
    offset: int = 0,
) -> tuple[list[Ipv4PrefixRead], int]:
    stmt = select(IpamIpv4Prefix).order_by(IpamIpv4Prefix.site_id, IpamIpv4Prefix.cidr)
    if site_id is not None:
        stmt = stmt.where(IpamIpv4Prefix.site_id == site_id)
    if tenant_id is not None:
        stmt = stmt.where(IpamIpv4Prefix.tenant_id == tenant_id)
    if vlan_id is not None:
        stmt = stmt.where(IpamIpv4Prefix.vlan_id == vlan_id)
    if vrf_id is not None:
        stmt = stmt.where(IpamIpv4Prefix.vrf_id == vrf_id)
    if role is not None:
        stmt = stmt.where(IpamIpv4Prefix.role == role)
    if status is not None:
        stmt = stmt.where(IpamIpv4Prefix.status == status)
    if slug is not None:
        stmt = stmt.where(IpamIpv4Prefix.slug == slugify_prefix(slug))
    if name is not None:
        stmt = stmt.where(func.lower(IpamIpv4Prefix.name) == name.strip().lower())
    rows = list(db.execute(stmt).scalars().all())

    if cidr is not None:
        want = _normalize_ipv4_cidr(cidr)
        rows = [r for r in rows if r.cidr == want]

    if address is not None:
        try:
            ip = ipaddress.ip_address(address.strip())
        except ValueError as e:
            raise ipam_error(400, "invalid_address", f"ugyldig adresse: {e}") from e
        if not isinstance(ip, ipaddress.IPv4Address):
            raise ipam_error(400, "ipv4_only", "kun IPv4")
        filtered: list[IpamIpv4Prefix] = []
        for r in rows:
            try:
                net = ipaddress.ip_network(r.cidr, strict=False)
            except ValueError:
                continue
            if net.version == 4 and ip in net:
                filtered.append(r)
        rows = filtered

    if q is not None:
        needle = q.strip().lower()
        if needle:
            rows = [
                r
                for r in rows
                if needle in (r.name or "").lower()
                or needle in (getattr(r, "slug", "") or "").lower()
                or needle in (r.cidr or "").lower()
            ]

    rows.sort(key=_prefix_sort_key)
    total = len(rows)
    if offset:
        rows = rows[offset:]
    if limit is not None:
        rows = rows[:limit]
    cache = _ipv4_assignments_with_site(db)
    inv_cache = _ipv4_inventory_used_with_site(db)
    site_ids = {r.site_id for r in rows}
    all_site: list[IpamIpv4Prefix] = []
    if site_ids:
        all_site = list(
            db.execute(select(IpamIpv4Prefix).where(IpamIpv4Prefix.site_id.in_(site_ids))).scalars().all(),
        )
    by_site: dict[int, list[IpamIpv4Prefix]] = {}
    for r in all_site:
        by_site.setdefault(r.site_id, []).append(r)
    return (
        [
            ipv4_prefix_read(db, r, _cache=cache, _inventory_cache=inv_cache, _same_site=by_site.get(r.site_id, []))
            for r in rows
        ],
        total,
    )


def get_ipv4_prefix(db: Session, prefix_id: int) -> IpamIpv4Prefix | None:
    return db.get(IpamIpv4Prefix, prefix_id)


def _validate_prefix_refs(
    db: Session,
    *,
    site_id: int,
    tenant_id: int | None,
    vlan_id: int | None,
    vrf_id: int | None,
) -> None:
    if dcim_svc.get_site(db, site_id) is None:
        raise ipam_error(404, "site_not_found", "site ikke funnet")
    if tenant_id is not None and tenant_svc.get_tenant(db, tenant_id) is None:
        raise ipam_error(404, "tenant_not_found", "tenant ikke funnet")
    if vlan_id is not None:
        v = fac_svc.get_vlan(db, int(vlan_id))
        if v is None:
            raise ipam_error(404, "vlan_not_found", "vlan ikke funnet")
        if v.site_id != site_id:
            raise ipam_error(400, "vlan_site_mismatch", "vlan tilhører ikke samme site")
    if vrf_id is not None:
        vrf = fac_svc.get_vrf(db, int(vrf_id))
        if vrf is None:
            raise ipam_error(404, "vrf_not_found", "vrf ikke funnet")
        if vrf.site_id != site_id:
            raise ipam_error(400, "vrf_site_mismatch", "vrf tilhører ikke samme site")


def find_ipv4_prefix_by_site_vrf_cidr(
    db: Session,
    *,
    site_id: int,
    cidr: str,
    vrf_id: int | None,
) -> IpamIpv4Prefix | None:
    return db.execute(
        select(IpamIpv4Prefix).where(
            IpamIpv4Prefix.site_id == site_id,
            IpamIpv4Prefix.cidr == cidr,
            IpamIpv4Prefix.vrf_scope == vrf_scope_of(vrf_id),
        ),
    ).scalar_one_or_none()


def create_ipv4_prefix(db: Session, data: Ipv4PrefixCreate) -> Ipv4PrefixRead:
    _validate_prefix_refs(
        db,
        site_id=data.site_id,
        tenant_id=data.tenant_id,
        vlan_id=data.vlan_id,
        vrf_id=data.vrf_id,
    )
    cidr = _normalize_ipv4_cidr(data.cidr)
    policy = resolve_overlap_policy(data.role, data.overlap_policy)
    _require_no_partial_overlap(db, site_id=data.site_id, cidr=cidr, vrf_id=data.vrf_id)
    require_no_global_overlap(db, site_id=data.site_id, cidr=cidr, policy=policy)
    row = new_ipv4_prefix_orm(
        db,
        site_id=data.site_id,
        name=data.name,
        cidr=cidr,
        slug=data.slug,
        role=data.role,
        status=data.status,
        description=data.description,
        subnet_services=dump_subnet_services(data.subnet_services),
        tenant_id=data.tenant_id,
        vlan_id=data.vlan_id,
        vrf_id=data.vrf_id,
        overlap_policy=policy,
        dual_stack_group_id=data.dual_stack_group_id,
    )
    db.add(row)
    try:
        db.flush()
        audit_svc.record(
            db,
            action="create",
            resource_type="prefix",
            resource_id=row.id,
            site_id=data.site_id,
            cidr=cidr,
            role=data.role,
            family="ipv4",
        )
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ipam_error(
            409,
            "prefix_conflict",
            "prefiks med samme CIDR i denne VRF-en eller samme slug finnes allerede på siten",
        ) from None
    db.refresh(row)
    return ipv4_prefix_read(db, row, created=True)


def _apply_prefix_ensure_update(db: Session, row: IpamIpv4Prefix, data: Ipv4PrefixEnsure) -> IpamIpv4Prefix:
    if data.name is not None:
        row.name = data.name.strip()
    if data.slug is not None:
        row.slug = allocate_prefix_slug(
            db,
            site_id=row.site_id,
            desired=data.slug,
            exclude_prefix_id=row.id,
            allow_suffix=False,
        )
    if data.role is not None:
        require_vlan_allowed(data.role, row.vlan_id if data.vlan_id is None else data.vlan_id)
        row.role = data.role
    if data.status is not None:
        row.status = data.status
    if data.description is not None:
        row.description = data.description
    if data.subnet_services is not None:
        row.subnet_services = dump_subnet_services(data.subnet_services)
    if data.tenant_id is not None:
        row.tenant_id = data.tenant_id
    if data.vlan_id is not None:
        require_vlan_allowed(prefix_role(row), data.vlan_id)
        row.vlan_id = data.vlan_id
    if data.overlap_policy is not None:
        row.overlap_policy = resolve_overlap_policy(prefix_role(row), data.overlap_policy)
    if data.dual_stack_group_id is not None:
        row.dual_stack_group_id = data.dual_stack_group_id
    return row


def ensure_ipv4_prefix(db: Session, data: Ipv4PrefixEnsure, *, update: bool = False) -> Ipv4PrefixRead:
    cidr = _normalize_ipv4_cidr(data.cidr)
    existing = find_ipv4_prefix_by_site_vrf_cidr(db, site_id=data.site_id, cidr=cidr, vrf_id=data.vrf_id)
    if existing is not None:
        if update:
            _validate_prefix_refs(
                db,
                site_id=data.site_id,
                tenant_id=data.tenant_id,
                vlan_id=data.vlan_id,
                vrf_id=data.vrf_id,
            )
            _apply_prefix_ensure_update(db, existing, data)
            db.commit()
            db.refresh(existing)
        return ipv4_prefix_read(db, existing, created=False)
    name = (data.name or data.slug or cidr).strip()
    create = Ipv4PrefixCreate(
        site_id=data.site_id,
        name=name,
        cidr=cidr,
        slug=data.slug,
        role=data.role or "active",
        status=data.status or "active",
        description=data.description,
        subnet_services=data.subnet_services,
        tenant_id=data.tenant_id,
        vlan_id=data.vlan_id,
        vrf_id=data.vrf_id,
        overlap_policy=data.overlap_policy,
        dual_stack_group_id=data.dual_stack_group_id,
    )
    try:
        return create_ipv4_prefix(db, create)
    except HTTPException as e:
        if e.status_code != 409:
            raise
        existing = find_ipv4_prefix_by_site_vrf_cidr(db, site_id=data.site_id, cidr=cidr, vrf_id=data.vrf_id)
        if existing is not None:
            return ipv4_prefix_read(db, existing, created=False)
        raise


def update_ipv4_prefix(db: Session, row: IpamIpv4Prefix, data: Ipv4PrefixUpdate) -> Ipv4PrefixRead:
    patch = data.model_dump(exclude_unset=True)
    if not patch:
        raise ipam_error(400, "empty_patch", "ingen felter å oppdatere")
    if "name" in patch and patch["name"] is not None:
        row.name = str(patch["name"]).strip()
    if "slug" in patch and patch["slug"] is not None:
        row.slug = allocate_prefix_slug(
            db,
            site_id=row.site_id,
            desired=str(patch["slug"]),
            exclude_prefix_id=row.id,
            allow_suffix=False,
        )
    if "role" in patch and patch["role"] is not None:
        require_vlan_allowed(str(patch["role"]), row.vlan_id if "vlan_id" not in patch else patch["vlan_id"])
        row.role = str(patch["role"])
    if "status" in patch and patch["status"] is not None:
        row.status = str(patch["status"])
    if "overlap_policy" in patch and patch["overlap_policy"] is not None:
        row.overlap_policy = resolve_overlap_policy(prefix_role(row), str(patch["overlap_policy"]))
        require_no_global_overlap(
            db,
            site_id=row.site_id,
            cidr=row.cidr,
            policy=row.overlap_policy,
            exclude_prefix_id=row.id,
        )
    if "dual_stack_group_id" in patch:
        row.dual_stack_group_id = patch["dual_stack_group_id"]
    if "description" in patch:
        v = patch["description"]
        row.description = None if v is None else (str(v).strip() or None)
    if "cidr" in patch and patch["cidr"] is not None:
        same_site = list(
            db.execute(select(IpamIpv4Prefix).where(IpamIpv4Prefix.site_id == row.site_id)).scalars().all(),
        )
        children = _child_prefix_orms(row, same_site)
        addr_count = _prefix_address_count(db, row.id)
        if children or addr_count:
            raise ipam_error(
                409,
                "prefix_cidr_locked",
                "kan ikke endre CIDR mens prefikset har underprefiks eller adresser",
                child_count=len(children),
                address_count=addr_count,
            )
        new_cidr = _normalize_ipv4_cidr(patch["cidr"])
        next_vrf = patch["vrf_id"] if "vrf_id" in patch else row.vrf_id
        _require_no_partial_overlap(
            db,
            site_id=row.site_id,
            cidr=new_cidr,
            vrf_id=next_vrf,
            exclude_prefix_id=row.id,
        )
        row.cidr = new_cidr
    if "subnet_services" in patch:
        row.subnet_services = dump_subnet_services(patch["subnet_services"])
    if "tenant_id" in patch:
        tid = patch["tenant_id"]
        if tid is not None and tenant_svc.get_tenant(db, int(tid)) is None:
            raise ipam_error(404, "tenant_not_found", "tenant ikke funnet")
        row.tenant_id = tid
    if "vlan_id" in patch:
        vid = patch["vlan_id"]
        if vid is None:
            row.vlan_id = None
        else:
            v = fac_svc.get_vlan(db, int(vid))
            if v is None:
                raise ipam_error(404, "vlan_not_found", "vlan ikke funnet")
            if v.site_id != row.site_id:
                raise ipam_error(400, "vlan_site_mismatch", "vlan tilhører ikke samme site")
            require_vlan_allowed(prefix_role(row), int(vid))
            row.vlan_id = int(vid)
    if "vrf_id" in patch:
        vrf_id = patch["vrf_id"]
        if vrf_id is None:
            row.vrf_id = None
            row.vrf_scope = 0
        else:
            vrf = fac_svc.get_vrf(db, int(vrf_id))
            if vrf is None:
                raise ipam_error(404, "vrf_not_found", "vrf ikke funnet")
            if vrf.site_id != row.site_id:
                raise ipam_error(400, "vrf_site_mismatch", "vrf tilhører ikke samme site")
            row.vrf_id = int(vrf_id)
            row.vrf_scope = vrf_scope_of(int(vrf_id))
    row.updated_at = dt.datetime.now(dt.UTC)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ipam_error(
            409,
            "prefix_conflict",
            "prefiks med samme CIDR i denne VRF-en eller samme slug finnes allerede på siten",
        ) from None
    db.refresh(row)
    return ipv4_prefix_read(db, row)


def _prefix_address_count(db: Session, prefix_id: int) -> int:
    return int(
        db.execute(
            select(func.count()).select_from(IpamIpv4Address).where(IpamIpv4Address.ipv4_prefix_id == prefix_id),
        ).scalar_one(),
    )


def delete_ipv4_prefix(db: Session, row: IpamIpv4Prefix, *, cascade: bool = False) -> None:
    _delete_ipv4_prefix_tree(db, row, cascade=cascade)
    db.commit()


def _delete_ipv4_prefix_tree(db: Session, row: IpamIpv4Prefix, *, cascade: bool) -> None:
    same_site = list(
        db.execute(select(IpamIpv4Prefix).where(IpamIpv4Prefix.site_id == row.site_id)).scalars().all(),
    )
    children = _child_prefix_orms(row, same_site)
    addr_count = _prefix_address_count(db, row.id)
    if (children or addr_count) and not cascade:
        raise ipam_error(
            409,
            "prefix_has_children",
            f"prefiks har {len(children)} underprefiks og {addr_count} adresser — "
            "slett dem først eller bruk cascade=true",
            child_count=len(children),
            address_count=addr_count,
        )
    if cascade:
        for child in children:
            _delete_ipv4_prefix_tree(db, child, cascade=True)
        addrs = list(
            db.execute(select(IpamIpv4Address).where(IpamIpv4Address.ipv4_prefix_id == row.id)).scalars().all(),
        )
        for addr in addrs:
            if addr.interface_ip_assignment_id is not None:
                assign = db.get(InterfaceIpAssignment, addr.interface_ip_assignment_id)
                if assign is not None:
                    db.delete(assign)
            db.delete(addr)
    db.delete(row)
