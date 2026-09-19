"""IPv6 GitOps-kontrakt: prefiks + adresse, speil av IPv4."""

from __future__ import annotations

import ipaddress

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.ipam import IpamIpv6Address, IpamIpv6Prefix
from app.schemas.ipam import (
    ADDRESS_STATUSES,
    IpRangeRead,
    Ipv6AddressEnsure,
    Ipv6AddressRead,
    Ipv6AddressRequest,
    Ipv6AvailableRangesRead,
    Ipv6PrefixAllocate,
    Ipv6PrefixCreate,
    Ipv6PrefixEnsure,
    Ipv6PrefixRead,
    Ipv4AvailablePrefixesRead,
)
from app.services import ipam as ipam_svc
from app.services import ipam_audit as audit_svc
from app.services import ipam_etag as etag_svc
from app.services.ipam_errors import ipam_error

_HELD_STATUSES = frozenset({"reserved", "assigned"})

_IN_USE = frozenset({"planned", "reserved", "assigned", "dhcp"})
_MODE_TO_STATUS = {"reserve": "reserved", "assign": "assigned"}


def _normalize_cidr(raw: str) -> str:
    try:
        net = ipaddress.ip_network(raw.strip(), strict=False)
    except ValueError as e:
        raise ipam_error(400, "invalid_cidr", f"ugyldig IPv6 CIDR: {e}") from e
    if net.version != 6:
        raise ipam_error(400, "ipv6_only", "kun IPv6-støtte i denne endepunktet")
    return str(net)


def _parent_of(child: IpamIpv6Prefix, rows: list[IpamIpv6Prefix]) -> IpamIpv6Prefix | None:
    try:
        child_net = ipaddress.ip_network(child.cidr, strict=False)
    except ValueError:
        return None
    best: IpamIpv6Prefix | None = None
    best_pl = -1
    for p in rows:
        if p.id == child.id or ipam_svc.vrf_scope_of(p.vrf_id) != ipam_svc.vrf_scope_of(child.vrf_id):
            continue
        try:
            p_net = ipaddress.ip_network(p.cidr, strict=False)
        except ValueError:
            continue
        if child_net.subnet_of(p_net) and p_net.prefixlen > best_pl and child_net.prefixlen > p_net.prefixlen:
            best = p
            best_pl = p_net.prefixlen
    return best


def ipv6_prefix_read(db: Session, row: IpamIpv6Prefix, *, created: bool | None = None) -> Ipv6PrefixRead:
    same = list(db.execute(select(IpamIpv6Prefix).where(IpamIpv6Prefix.site_id == row.site_id)).scalars().all())
    parent = _parent_of(row, same)
    net = ipaddress.ip_network(row.cidr, strict=False)
    addrs = db.execute(
        select(IpamIpv6Address.address).where(
            IpamIpv6Address.site_id == row.site_id,
            IpamIpv6Address.status.in_(("reserved", "assigned")),
        ),
    ).scalars().all()
    in_net = 0
    for raw in addrs:
        try:
            ip = ipaddress.ip_address(raw)
        except ValueError:
            continue
        if ip in net:
            in_net += 1
    return Ipv6PrefixRead(
        id=row.id,
        site_id=row.site_id,
        tenant_id=row.tenant_id,
        vlan_id=row.vlan_id,
        vrf_id=row.vrf_id,
        name=row.name,
        slug=row.slug,
        role=row.role,
        status=row.status,
        cidr=row.cidr,
        description=row.description,
        overlap_policy=row.overlap_policy,
        dual_stack_group_id=row.dual_stack_group_id,
        parent_id=parent.id if parent is not None else None,
        used_count=in_net,
        created=created,
        subnet_services=ipam_svc.dump_subnet_services(row.subnet_services) if row.subnet_services else None,
        created_at=row.created_at,
        updated_at=row.updated_at,
        etag=etag_svc.format_etag(row),
    )


def child_prefix_orms(parent: IpamIpv6Prefix, same_site: list[IpamIpv6Prefix]) -> list[IpamIpv6Prefix]:
    out: list[IpamIpv6Prefix] = []
    for c in same_site:
        if c.id == parent.id:
            continue
        ipar = _parent_of(c, same_site)
        if ipar is not None and ipar.id == parent.id:
            out.append(c)
    return out


def new_ipv6_prefix_orm(
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
) -> IpamIpv6Prefix:
    cidr_n = _normalize_cidr(cidr)
    slug_s = _unique_v6_slug(db, site_id=site_id, desired=slug or name or cidr_n, explicit=slug is not None)
    if reserved_slugs is not None:
        base = slug_s
        n = 2
        while slug_s in reserved_slugs:
            suffix = f"-{n}"
            slug_s = f"{base[: 128 - len(suffix)]}{suffix}"
            n += 1
        reserved_slugs.add(slug_s)
    return IpamIpv6Prefix(
        site_id=site_id,
        tenant_id=tenant_id,
        vlan_id=vlan_id,
        vrf_id=vrf_id,
        vrf_scope=ipam_svc.vrf_scope_of(vrf_id),
        name=name.strip(),
        slug=slug_s,
        role=role,
        status=status,
        overlap_policy=ipam_svc.resolve_overlap_policy(role, overlap_policy),
        dual_stack_group_id=dual_stack_group_id,
        description=description,
        cidr=cidr_n,
        subnet_services=ipam_svc.dump_subnet_services(subnet_services) if subnet_services else None,
    )


def available_ranges(db: Session, pfx: IpamIpv6Prefix) -> Ipv6AvailableRangesRead:
    from app.services.ipam_prefix_alloc import MAX_USED_ADDRESS_EXPORT, _invert_ranges, _merge_ints

    net = ipaddress.ip_network(pfx.cidr, strict=False)
    if net.prefixlen <= 126:
        usable_start = int(net.network_address) + 1
        usable_end = int(net.broadcast_address)
    else:
        usable_start = int(net.network_address)
        usable_end = int(net.broadcast_address)

    used_ips: set[ipaddress.IPv6Address] = set()
    inv_rows = list(
        db.execute(
            select(IpamIpv6Address)
            .where(
                IpamIpv6Address.site_id == pfx.site_id,
                IpamIpv6Address.status.in_(("reserved", "assigned")),
            )
            .order_by(IpamIpv6Address.address),
        )
        .scalars()
        .all(),
    )
    used_reads: list[Ipv6AddressRead] = []
    for row in inv_rows:
        try:
            ip = ipaddress.ip_address(row.address)
        except ValueError:
            continue
        if not isinstance(ip, ipaddress.IPv6Address) or ip not in net:
            continue
        used_ips.add(ip)
        if len(used_reads) < MAX_USED_ADDRESS_EXPORT:
            used_reads.append(_addr_read(row))

    gw = (pfx.subnet_services or {}).get("gateway") if isinstance(pfx.subnet_services, dict) else None
    if gw:
        try:
            gip = ipaddress.ip_address(str(gw))
        except ValueError:
            gip = None
        if isinstance(gip, ipaddress.IPv6Address) and gip in net:
            used_ips.add(gip)

    used_ints = [int(ip) for ip in used_ips if usable_start <= int(ip) <= usable_end]
    used_ranges = _merge_ints(used_ints)
    free_ranges = _invert_ranges(usable_start, usable_end, used_ranges)
    free_cidrs: list[str] = []
    for a, b in free_ranges:
        for block in ipaddress.summarize_address_range(ipaddress.IPv6Address(a), ipaddress.IPv6Address(b)):
            free_cidrs.append(str(block))

    return Ipv6AvailableRangesRead(
        prefix_id=pfx.id,
        cidr=pfx.cidr,
        role=pfx.role,
        used_count=len(used_ints),
        used_addresses=used_reads,
        used_ranges=[
            IpRangeRead(start=str(ipaddress.IPv6Address(a)), end=str(ipaddress.IPv6Address(b)), count=b - a + 1)
            for a, b in used_ranges
        ],
        free_ranges=[
            IpRangeRead(start=str(ipaddress.IPv6Address(a)), end=str(ipaddress.IPv6Address(b)), count=b - a + 1)
            for a, b in free_ranges
        ],
        free_cidrs=free_cidrs,
    )


def get_ipv6_prefix(db: Session, prefix_id: int) -> IpamIpv6Prefix | None:
    return db.get(IpamIpv6Prefix, prefix_id)


def get_ipv6_address(db: Session, addr_id: int) -> IpamIpv6Address | None:
    return db.get(IpamIpv6Address, addr_id)


def list_ipv6_prefixes(
    db: Session,
    *,
    site_id: int | None = None,
    slug: str | None = None,
    limit: int | None = None,
    offset: int = 0,
) -> tuple[list[Ipv6PrefixRead], int]:
    q = select(IpamIpv6Prefix).order_by(IpamIpv6Prefix.site_id, IpamIpv6Prefix.cidr)
    if site_id is not None:
        q = q.where(IpamIpv6Prefix.site_id == site_id)
    if slug is not None:
        q = q.where(IpamIpv6Prefix.slug == ipam_svc.slugify_prefix(slug))
    rows = list(db.execute(q).scalars().all())
    total = len(rows)
    if offset:
        rows = rows[offset:]
    if limit is not None:
        rows = rows[:limit]
    return [ipv6_prefix_read(db, r) for r in rows], total


def find_by_site_vrf_cidr(db: Session, *, site_id: int, cidr: str, vrf_id: int | None) -> IpamIpv6Prefix | None:
    return db.execute(
        select(IpamIpv6Prefix).where(
            IpamIpv6Prefix.site_id == site_id,
            IpamIpv6Prefix.cidr == cidr,
            IpamIpv6Prefix.vrf_scope == ipam_svc.vrf_scope_of(vrf_id),
        ),
    ).scalar_one_or_none()


def create_ipv6_prefix(db: Session, data: Ipv6PrefixCreate) -> Ipv6PrefixRead:
    ipam_svc._validate_prefix_refs(
        db, site_id=data.site_id, tenant_id=data.tenant_id, vlan_id=data.vlan_id, vrf_id=data.vrf_id,
    )
    cidr = _normalize_cidr(data.cidr)
    policy = ipam_svc.resolve_overlap_policy(data.role, data.overlap_policy)
    ipam_svc.require_vlan_allowed(data.role, data.vlan_id)
    net = ipaddress.ip_network(cidr, strict=False)
    rows = db.execute(select(IpamIpv6Prefix).where(IpamIpv6Prefix.site_id == data.site_id)).scalars().all()
    scope = ipam_svc.vrf_scope_of(data.vrf_id)
    for r in rows:
        if ipam_svc.vrf_scope_of(r.vrf_id) != scope:
            continue
        other = ipaddress.ip_network(r.cidr, strict=False)
        if net.overlaps(other) and not (net.subnet_of(other) or other.subnet_of(net)):
            raise ipam_error(409, "prefix_partial_overlap", f"overlapper {r.cidr}", other_id=r.id)
    ipam_svc.require_no_global_overlap(db, site_id=data.site_id, cidr=cidr, policy=policy, version=6)
    row = IpamIpv6Prefix(
        site_id=data.site_id,
        tenant_id=data.tenant_id,
        vlan_id=data.vlan_id,
        vrf_id=data.vrf_id,
        vrf_scope=ipam_svc.vrf_scope_of(data.vrf_id),
        name=data.name.strip(),
        slug=_unique_v6_slug(db, site_id=data.site_id, desired=data.slug or data.name or cidr, explicit=data.slug is not None),
        role=data.role,
        status=data.status,
        overlap_policy=policy,
        dual_stack_group_id=data.dual_stack_group_id,
        description=data.description,
        cidr=cidr,
        subnet_services=ipam_svc.dump_subnet_services(data.subnet_services),
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
            family="ipv6",
        )
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ipam_error(409, "prefix_conflict", "IPv6-prefiks med samme CIDR eller slug finnes allerede") from None
    db.refresh(row)
    from app.services import ipam_webhooks as hook_svc

    hook_svc.fire("prefix.created", {"id": row.id, "site_id": row.site_id, "cidr": row.cidr, "family": "ipv6"})
    return ipv6_prefix_read(db, row, created=True)


def _unique_v6_slug(db: Session, *, site_id: int, desired: str, explicit: bool) -> str:
    base = ipam_svc.slugify_prefix(desired)
    candidate = base
    n = 2
    while True:
        taken = db.execute(
            select(IpamIpv6Prefix.id).where(IpamIpv6Prefix.site_id == site_id, IpamIpv6Prefix.slug == candidate),
        ).scalar_one_or_none()
        if taken is None:
            return candidate
        if explicit:
            raise ipam_error(409, "slug_taken", "slug finnes allerede på denne siten")
        suffix = f"-{n}"
        candidate = f"{base[: 128 - len(suffix)]}{suffix}"
        n += 1
        if n > 1000:
            raise ipam_error(400, "slug_exhausted", "kunne ikke lage unik slug")


def ensure_ipv6_prefix(db: Session, data: Ipv6PrefixEnsure, *, update: bool = False) -> Ipv6PrefixRead:
    cidr = _normalize_cidr(data.cidr)
    existing = find_by_site_vrf_cidr(db, site_id=data.site_id, cidr=cidr, vrf_id=data.vrf_id)
    if existing is not None:
        if update:
            if data.name:
                existing.name = data.name.strip()
            if data.role:
                existing.role = data.role
            if data.status:
                existing.status = data.status
            if data.overlap_policy:
                existing.overlap_policy = data.overlap_policy
            if data.dual_stack_group_id is not None:
                existing.dual_stack_group_id = data.dual_stack_group_id
            db.commit()
            db.refresh(existing)
        return ipv6_prefix_read(db, existing, created=False)
    create = Ipv6PrefixCreate(
        site_id=data.site_id,
        name=(data.name or data.slug or cidr).strip(),
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
    return create_ipv6_prefix(db, create)


def allocate_child_ipv6(db: Session, parent: IpamIpv6Prefix, data: Ipv6PrefixAllocate) -> Ipv6PrefixRead:
    from app.services.ipam_prefix_alloc import require_child_allocation

    require_child_allocation(parent)
    parent_net = ipaddress.ip_network(parent.cidr, strict=False)
    if data.prefixlen <= parent_net.prefixlen or data.prefixlen > 128:
        raise ipam_error(400, "invalid_prefixlen", "ugyldig prefixlen")
    occupied = []
    for r in db.execute(select(IpamIpv6Prefix).where(IpamIpv6Prefix.site_id == parent.site_id)).scalars().all():
        if r.id == parent.id or ipam_svc.vrf_scope_of(r.vrf_id) != ipam_svc.vrf_scope_of(parent.vrf_id):
            continue
        other = ipaddress.ip_network(r.cidr, strict=False)
        if other.overlaps(parent_net) and other != parent_net:
            occupied.append(other)
    for cand in parent_net.subnets(new_prefix=data.prefixlen):
        if any(cand.overlaps(o) for o in occupied):
            continue
        create = Ipv6PrefixCreate(
            site_id=parent.site_id,
            name=data.name,
            cidr=str(cand),
            slug=data.slug,
            role=data.role,
            status=data.status,
            description=data.description,
            vlan_id=data.vlan_id,
            tenant_id=data.tenant_id if data.tenant_id is not None else parent.tenant_id,
            vrf_id=parent.vrf_id,
            overlap_policy=parent.overlap_policy,
            dual_stack_group_id=parent.dual_stack_group_id,
        )
        return create_ipv6_prefix(db, create)
    raise ipam_error(409, "no_free_prefix", f"ingen ledig /{data.prefixlen} i {parent.cidr}")


def list_available_child_ipv6(db: Session, parent: IpamIpv6Prefix, prefixlen: int, *, limit: int = 64) -> Ipv4AvailablePrefixesRead:
    from app.services.ipam_prefix_alloc import require_child_allocation

    require_child_allocation(parent)
    parent_net = ipaddress.ip_network(parent.cidr, strict=False)
    if prefixlen <= parent_net.prefixlen or prefixlen > 128:
        raise ipam_error(400, "invalid_prefixlen", "ugyldig prefixlen")
    occupied = []
    for r in db.execute(select(IpamIpv6Prefix).where(IpamIpv6Prefix.site_id == parent.site_id)).scalars().all():
        if r.id == parent.id:
            continue
        other = ipaddress.ip_network(r.cidr, strict=False)
        if other.overlaps(parent_net) and other != parent_net:
            occupied.append(other)
    found: list[str] = []
    truncated = False
    for cand in parent_net.subnets(new_prefix=prefixlen):
        if any(cand.overlaps(o) for o in occupied):
            continue
        found.append(str(cand))
        if len(found) >= limit:
            truncated = True
            break
    return Ipv4AvailablePrefixesRead(
        parent_id=parent.id, cidr=parent.cidr, prefixlen=prefixlen, available=found, truncated=truncated,
    )


def _addr_read(row: IpamIpv6Address, *, created: bool | None = None) -> Ipv6AddressRead:
    status = row.status if row.status in ADDRESS_STATUSES else "discovered"
    return Ipv6AddressRead.model_validate(row).model_copy(
        update={"created": created, "status": status, "etag": etag_svc.format_etag(row)},
    )


def ensure_ipv6_address(db: Session, data: Ipv6AddressEnsure, *, update: bool = False) -> Ipv6AddressRead:
    pfx = db.get(IpamIpv6Prefix, data.ipv6_prefix_id)
    if pfx is None:
        raise ipam_error(404, "prefix_not_found", "prefiks ikke funnet")
    ipam_svc.require_host_allocation(pfx)
    try:
        ip = ipaddress.ip_address(data.address.strip())
    except ValueError as e:
        raise ipam_error(400, "invalid_address", str(e)) from e
    if not isinstance(ip, ipaddress.IPv6Address):
        raise ipam_error(400, "ipv6_only", "kun IPv6")
    net = ipaddress.ip_network(pfx.cidr, strict=False)
    if ip not in net:
        raise ipam_error(400, "address_outside_prefix", "adressen ligger ikke i prefiksnettet")
    ip_s = str(ip)
    status = data.status
    if data.mode:
        status = _MODE_TO_STATUS[data.mode]
    row = db.execute(
        select(IpamIpv6Address).where(IpamIpv6Address.site_id == pfx.site_id, IpamIpv6Address.address == ip_s),
    ).scalar_one_or_none()
    if row is not None and not update:
        return _addr_read(row, created=False)
    created = row is None
    if row is None:
        row = IpamIpv6Address(
            site_id=pfx.site_id,
            ipv6_prefix_id=pfx.id,
            address=ip_s,
            status=status or "discovered",
            role=data.role or "host",
            hostname=data.hostname,
            fqdn=data.fqdn,
            dns_name=data.dns_name,
            note=data.note,
            owner_type=data.owner_type,
            owner_ref=data.owner_ref,
        )
        db.add(row)
    elif update:
        if status:
            row.status = status
        if data.role:
            row.role = data.role
        if data.note is not None:
            row.note = data.note
    audit_svc.record(db, action="ensure", resource_type="address", site_id=pfx.site_id, address=ip_s, family="ipv6")
    db.commit()
    db.refresh(row)
    from app.services import ipam_webhooks as hook_svc

    hook_svc.fire(
        "address.ensured",
        {"id": row.id, "site_id": row.site_id, "address": row.address, "family": "ipv6", "created": created},
    )
    return _addr_read(row, created=created)


def request_ipv6_address(db: Session, data: Ipv6AddressRequest) -> Ipv6AddressRead:
    pfx = db.get(IpamIpv6Prefix, data.ipv6_prefix_id)
    if pfx is None:
        raise ipam_error(404, "prefix_not_found", "prefiks ikke funnet")
    ipam_svc.require_host_allocation(pfx)
    net = ipaddress.ip_network(pfx.cidr, strict=False)
    used = {
        str(ipaddress.ip_address(a))
        for a in db.execute(
            select(IpamIpv6Address.address).where(
                IpamIpv6Address.site_id == pfx.site_id,
                IpamIpv6Address.status.in_(tuple(_IN_USE)),
            ),
        ).scalars().all()
    }
    gw = (pfx.subnet_services or {}).get("gateway") if isinstance(pfx.subnet_services, dict) else None
    if gw:
        used.add(str(ipaddress.ip_address(str(gw))))
    used.add(str(net.network_address))
    chosen: ipaddress.IPv6Address | None = None
    if data.preferred_address:
        try:
            pref = ipaddress.ip_address(data.preferred_address.strip())
        except ValueError as e:
            raise ipam_error(400, "invalid_address", str(e)) from e
        if pref not in net or str(pref) in used:
            raise ipam_error(409, "address_taken", "foretrukket adresse er opptatt")
        chosen = pref  # type: ignore[assignment]
    else:
        start = int(net.network_address) + 1
        end = min(int(net.broadcast_address), start + 65536)
        for n in range(start, end):
            cand = ipaddress.IPv6Address(n)
            if str(cand) not in used:
                chosen = cand
                break
    if chosen is None:
        raise ipam_error(409, "no_free_address", "ingen ledig IPv6-adresse i søkevinduet")
    return ensure_ipv6_address(
        db,
        Ipv6AddressEnsure(
            ipv6_prefix_id=pfx.id,
            address=str(chosen),
            mode=data.mode,
            role=data.role,
            note=data.note,
        ),
        update=True,
    )


def list_ipv6_addresses(
    db: Session,
    *,
    site_id: int | None = None,
    ipv6_prefix_id: int | None = None,
    address: str | None = None,
    limit: int = 200,
    offset: int = 0,
) -> tuple[list[Ipv6AddressRead], int]:
    q = select(IpamIpv6Address).order_by(IpamIpv6Address.address)
    if site_id is not None:
        q = q.where(IpamIpv6Address.site_id == site_id)
    if ipv6_prefix_id is not None:
        q = q.where(IpamIpv6Address.ipv6_prefix_id == ipv6_prefix_id)
    if address is not None:
        q = q.where(IpamIpv6Address.address == str(ipaddress.ip_address(address.strip())))
    rows = list(db.execute(q).scalars().all())
    total = len(rows)
    if offset:
        rows = rows[offset:]
    rows = rows[:limit]
    return [_addr_read(r) for r in rows], total


def release_ipv6_address(db: Session, row: IpamIpv6Address) -> Ipv6AddressRead:
    row.status = "discovered"
    row.device_id = None
    row.interface_id = None
    db.commit()
    db.refresh(row)
    from app.services import ipam_webhooks as hook_svc

    hook_svc.fire("address.released", {"id": row.id, "site_id": row.site_id, "address": row.address, "family": "ipv6"})
    return _addr_read(row)


def delete_ipv6_prefix(db: Session, row: IpamIpv6Prefix, *, cascade: bool = False) -> None:
    _delete_ipv6_prefix_tree(db, row, cascade=cascade)
    db.commit()


def _delete_ipv6_prefix_tree(db: Session, row: IpamIpv6Prefix, *, cascade: bool) -> None:
    same = list(db.execute(select(IpamIpv6Prefix).where(IpamIpv6Prefix.site_id == row.site_id)).scalars().all())
    children = child_prefix_orms(row, same)
    addrs = list(
        db.execute(select(IpamIpv6Address).where(IpamIpv6Address.ipv6_prefix_id == row.id)).scalars().all(),
    )
    if (children or addrs) and not cascade:
        raise ipam_error(
            409,
            "prefix_has_children",
            f"prefiks har {len(children)} underprefiks og {len(addrs)} adresser — slett dem først eller bruk cascade=true",
            child_count=len(children),
            address_count=len(addrs),
        )
    if cascade:
        for child in children:
            _delete_ipv6_prefix_tree(db, child, cascade=True)
        leftover = list(
            db.execute(select(IpamIpv6Address).where(IpamIpv6Address.ipv6_prefix_id == row.id)).scalars().all(),
        )
        for addr in leftover:
            db.delete(addr)
    db.delete(row)


def delete_ipv6_address(db: Session, row: IpamIpv6Address, *, force: bool = False) -> None:
    if not force and (row.status or "") in _HELD_STATUSES:
        raise ipam_error(
            409,
            "address_must_release",
            "release adressen først (beholder raden) eller DELETE med ?force=true",
            address_status=row.status,
        )
    db.delete(row)
    db.commit()
