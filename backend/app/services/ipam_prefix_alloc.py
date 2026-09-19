"""Neste ledige barn-prefiks og kompakte ledige ranges."""

from __future__ import annotations

import ipaddress

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.ipam import IpamIpv4Address, IpamIpv4Prefix
from app.schemas.ipam import (
    IpRangeRead,
    Ipv4AddressRead,
    Ipv4AvailablePrefixesRead,
    Ipv4AvailableRangesRead,
    Ipv4PrefixAllocate,
    Ipv4PrefixCreate,
    Ipv4PrefixRead,
)
from app.services import ipam as ipam_svc
from app.services import ipam_address as addr_svc
from app.services.ipam_errors import ipam_error

CHILD_ALLOC_ROLES = frozenset({"container", "active"})
MAX_USED_ADDRESS_EXPORT = 500


def require_child_allocation(pfx: IpamIpv4Prefix) -> None:
    role = ipam_svc.prefix_role(pfx)
    status = ipam_svc.prefix_status(pfx)
    if role not in CHILD_ALLOC_ROLES:
        raise ipam_error(
            409,
            "prefix_role_forbids_child_alloc",
            f"prefiks-rolle {role} tillater ikke allokering av barn-prefiks",
            role=role,
        )
    if status in {"reserved", "deprecated"}:
        raise ipam_error(
            409,
            "prefix_status_forbids_alloc",
            f"prefiks-status {status} tillater ikke allokering av barn-prefiks",
            status=status,
        )


def _parent_net(pfx: IpamIpv4Prefix) -> ipaddress.IPv4Network:
    try:
        net = ipaddress.ip_network(pfx.cidr, strict=False)
    except ValueError as e:
        raise ipam_error(400, "invalid_cidr", f"ugyldig IPv4 CIDR: {e}") from e
    if net.version != 4:
        raise ipam_error(400, "ipv4_only", "kun IPv4")
    return net  # type: ignore[return-value]


def _occupied_child_networks(db: Session, parent: IpamIpv4Prefix) -> list[ipaddress.IPv4Network]:
    parent_net = _parent_net(parent)
    scope = ipam_svc.vrf_scope_of(parent.vrf_id)
    rows = db.execute(select(IpamIpv4Prefix).where(IpamIpv4Prefix.site_id == parent.site_id)).scalars().all()
    out: list[ipaddress.IPv4Network] = []
    for r in rows:
        if r.id == parent.id:
            continue
        if ipam_svc.vrf_scope_of(getattr(r, "vrf_id", None)) != scope:
            continue
        try:
            other = ipaddress.ip_network(r.cidr, strict=False)
        except ValueError:
            continue
        if other.version != 4:
            continue
        if other.overlaps(parent_net) and other != parent_net:
            out.append(other)  # type: ignore[arg-type]
    return out


def _used_ips_in_prefix(db: Session, parent: IpamIpv4Prefix) -> set[ipaddress.IPv4Address]:
    parent_net = _parent_net(parent)
    used: set[ipaddress.IPv4Address] = set()
    for ip, sid in ipam_svc._ipv4_inventory_used_with_site(db):
        if sid == parent.site_id and ip in parent_net:
            used.add(ip)
    for ip, sid in ipam_svc._ipv4_assignments_with_site(db):
        if sid == parent.site_id and ip in parent_net:
            used.add(ip)
    return used


def _candidate_is_free(
    cand: ipaddress.IPv4Network,
    occupied: list[ipaddress.IPv4Network],
    used_ips: set[ipaddress.IPv4Address],
) -> bool:
    for other in occupied:
        if cand.overlaps(other):
            return False
    for ip in used_ips:
        if ip in cand:
            return False
    return True


def iter_available_child_cidrs(
    db: Session,
    parent: IpamIpv4Prefix,
    prefixlen: int,
    *,
    limit: int | None = None,
) -> tuple[list[str], bool]:
    parent_net = _parent_net(parent)
    if prefixlen <= parent_net.prefixlen or prefixlen > 32:
        raise ipam_error(
            400,
            "invalid_prefixlen",
            f"prefixlen må være mellom {parent_net.prefixlen + 1} og 32",
        )
    occupied = _occupied_child_networks(db, parent)
    used_ips = _used_ips_in_prefix(db, parent)
    found: list[str] = []
    truncated = False
    for cand in parent_net.subnets(new_prefix=prefixlen):
        if not _candidate_is_free(cand, occupied, used_ips):
            continue
        found.append(str(cand))
        if limit is not None and len(found) >= limit:
            truncated = True
            break
    return found, truncated


def list_available_child_prefixes(
    db: Session,
    parent: IpamIpv4Prefix,
    prefixlen: int,
    *,
    limit: int = 64,
) -> Ipv4AvailablePrefixesRead:
    require_child_allocation(parent)
    available, truncated = iter_available_child_cidrs(db, parent, prefixlen, limit=limit)
    return Ipv4AvailablePrefixesRead(
        parent_id=parent.id,
        cidr=parent.cidr,
        prefixlen=prefixlen,
        available=available,
        truncated=truncated,
    )


def allocate_child_prefix(db: Session, parent: IpamIpv4Prefix, data: Ipv4PrefixAllocate) -> Ipv4PrefixRead:
    require_child_allocation(parent)
    if data.slug:
        existing = db.execute(
            select(IpamIpv4Prefix).where(
                IpamIpv4Prefix.site_id == parent.site_id,
                IpamIpv4Prefix.slug == ipam_svc.slugify_prefix(data.slug),
            ),
        ).scalar_one_or_none()
        if existing is not None:
            same_site = list(
                db.execute(select(IpamIpv4Prefix).where(IpamIpv4Prefix.site_id == parent.site_id)).scalars().all(),
            )
            immediate = ipam_svc._immediate_parent_row(existing, same_site)
            if immediate is None or immediate.id != parent.id:
                raise ipam_error(409, "slug_taken", "slug finnes allerede på denne siten")
            return ipam_svc.ipv4_prefix_read(db, existing, created=False)

    cidrs, _ = iter_available_child_cidrs(db, parent, data.prefixlen, limit=1)
    if not cidrs:
        raise ipam_error(409, "no_free_prefix", f"ingen ledig /{data.prefixlen} i {parent.cidr}")

    create = Ipv4PrefixCreate(
        site_id=parent.site_id,
        name=data.name,
        cidr=cidrs[0],
        slug=data.slug,
        role=data.role,
        status=data.status,
        description=data.description,
        subnet_services=data.subnet_services,
        tenant_id=data.tenant_id if data.tenant_id is not None else parent.tenant_id,
        vlan_id=data.vlan_id,
        vrf_id=parent.vrf_id,
    )
    return ipam_svc.create_ipv4_prefix(db, create)


def _merge_ints(values: list[int]) -> list[tuple[int, int]]:
    if not values:
        return []
    values = sorted(set(values))
    ranges: list[tuple[int, int]] = []
    start = prev = values[0]
    for n in values[1:]:
        if n == prev + 1:
            prev = n
            continue
        ranges.append((start, prev))
        start = prev = n
    ranges.append((start, prev))
    return ranges


def _invert_ranges(usable_start: int, usable_end: int, used: list[tuple[int, int]]) -> list[tuple[int, int]]:
    if usable_start > usable_end:
        return []
    free: list[tuple[int, int]] = []
    cursor = usable_start
    for a, b in used:
        if b < cursor:
            continue
        lo = max(a, usable_start)
        hi = min(b, usable_end)
        if lo > cursor:
            free.append((cursor, lo - 1))
        cursor = max(cursor, hi + 1)
        if cursor > usable_end:
            break
    if cursor <= usable_end:
        free.append((cursor, usable_end))
    return free


def _range_read(start: int, end: int) -> IpRangeRead:
    return IpRangeRead(start=str(ipaddress.IPv4Address(start)), end=str(ipaddress.IPv4Address(end)), count=end - start + 1)


def available_ranges(db: Session, pfx: IpamIpv4Prefix) -> Ipv4AvailableRangesRead:
    net = _parent_net(pfx)
    if net.prefixlen <= 30:
        usable_start = int(net.network_address) + 1
        usable_end = int(net.broadcast_address) - 1
    else:
        usable_start = int(net.network_address)
        usable_end = int(net.broadcast_address)

    used_ips = _used_ips_in_prefix(db, pfx)
    for raw in addr_svc.infra_reserved_ips(pfx):
        try:
            ip = ipaddress.ip_address(raw)
        except ValueError:
            continue
        if isinstance(ip, ipaddress.IPv4Address) and ip in net:
            used_ips.add(ip)

    used_ints = [int(ip) for ip in used_ips if usable_start <= int(ip) <= usable_end]
    used_ranges = _merge_ints(used_ints)
    free_ranges = _invert_ranges(usable_start, usable_end, used_ranges)

    free_cidrs: list[str] = []
    for a, b in free_ranges:
        for block in ipaddress.summarize_address_range(ipaddress.IPv4Address(a), ipaddress.IPv4Address(b)):
            free_cidrs.append(str(block))

    inv_rows = list(
        db.execute(
            select(IpamIpv4Address)
            .where(
                IpamIpv4Address.site_id == pfx.site_id,
                IpamIpv4Address.status.in_(("reserved", "assigned")),
            )
            .order_by(IpamIpv4Address.address),
        )
        .scalars()
        .all(),
    )
    used_reads: list[Ipv4AddressRead] = []
    for row in inv_rows:
        try:
            ip = ipaddress.ip_address(row.address)
        except ValueError:
            continue
        if isinstance(ip, ipaddress.IPv4Address) and ip in net:
            used_reads.append(addr_svc._ipv4_address_read(db, row))
        if len(used_reads) >= MAX_USED_ADDRESS_EXPORT:
            break

    return Ipv4AvailableRangesRead(
        prefix_id=pfx.id,
        cidr=pfx.cidr,
        role=ipam_svc.prefix_role(pfx),
        used_count=len(used_ints),
        used_addresses=used_reads,
        used_ranges=[_range_read(a, b) for a, b in used_ranges],
        free_ranges=[_range_read(a, b) for a, b in free_ranges],
        free_cidrs=free_cidrs,
    )
