"""IPv6-område/pool som inventory-vindu. Ikke DHCP-tjeneste, lease eller ledig-CIDR."""

from __future__ import annotations

import ipaddress

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, object_session

from app.models.ipam import IpamIpv6Prefix, IpamIpv6Range
from app.schemas.ipam import IPV6_RANGE_KINDS, Ipv6RangeCreate, Ipv6RangeRead, Ipv6RangeUpdate
from app.services.federation_guard import require_site_write
from app.services.ipam import slugify_prefix
from app.services.ipam_errors import ipam_error


def _as_v6(raw: str, *, label: str) -> ipaddress.IPv6Address:
    try:
        ip = ipaddress.ip_address(raw.strip())
    except ValueError as e:
        raise ipam_error(400, "invalid_range_address", f"{label} er ikke en gyldig IPv6-adresse") from e
    if not isinstance(ip, ipaddress.IPv6Address):
        raise ipam_error(400, "invalid_range_address", f"{label} må være IPv6")
    return ip


def address_in_span(addr: str, start_s: str, end_s: str) -> bool:
    try:
        ip = ipaddress.ip_address(str(addr).strip())
        start = ipaddress.ip_address(str(start_s).strip())
        end = ipaddress.ip_address(str(end_s).strip())
    except ValueError:
        return False
    if not isinstance(ip, ipaddress.IPv6Address):
        return False
    if not isinstance(start, ipaddress.IPv6Address) or not isinstance(end, ipaddress.IPv6Address):
        return False
    lo, hi = (start, end) if int(start) <= int(end) else (end, start)
    return int(lo) <= int(ip) <= int(hi)


def range_to_read(row: IpamIpv6Range) -> Ipv6RangeRead:
    return Ipv6RangeRead.model_validate(row)


def get_ipv6_range(db: Session, range_id: int) -> IpamIpv6Range | None:
    return db.get(IpamIpv6Range, range_id)


def get_ipv6_range_by_slug(db: Session, prefix_id: int, slug: str) -> IpamIpv6Range | None:
    return db.execute(
        select(IpamIpv6Range).where(
            IpamIpv6Range.ipv6_prefix_id == prefix_id,
            IpamIpv6Range.slug == slug.strip().lower(),
        )
    ).scalar_one_or_none()


def list_ipv6_ranges(db: Session, prefix_id: int) -> list[IpamIpv6Range]:
    return list(
        db.execute(
            select(IpamIpv6Range)
            .where(IpamIpv6Range.ipv6_prefix_id == prefix_id)
            .order_by(IpamIpv6Range.start_address, IpamIpv6Range.id)
        ).scalars().all()
    )


def address_in_kinds(pfx: IpamIpv6Prefix, addr: str, kinds: set[str] | frozenset[str]) -> bool:
    db = object_session(pfx)
    if db is None or pfx.id is None:
        return False
    rows = db.execute(
        select(IpamIpv6Range).where(
            IpamIpv6Range.ipv6_prefix_id == pfx.id,
            IpamIpv6Range.kind.in_(tuple(kinds)),
        )
    ).scalars().all()
    return any(address_in_span(addr, row.start_address, row.end_address) for row in rows)


def allocation_windows(pfx: IpamIpv6Prefix) -> list[IpamIpv6Range]:
    db = object_session(pfx)
    if db is None or pfx.id is None:
        return []
    return list(
        db.execute(
            select(IpamIpv6Range).where(
                IpamIpv6Range.ipv6_prefix_id == pfx.id,
                IpamIpv6Range.kind == "allocation",
            )
        ).scalars().all()
    )


def _validate_span(pfx: IpamIpv6Prefix, start_s: str, end_s: str) -> tuple[str, str]:
    start = _as_v6(start_s, label="start_address")
    end = _as_v6(end_s, label="end_address")
    try:
        net = ipaddress.ip_network(pfx.cidr, strict=False)
    except ValueError as e:
        raise ipam_error(400, "invalid_prefix_cidr", "ugyldig prefiks CIDR") from e
    if start not in net or end not in net:
        raise ipam_error(400, "address_outside_prefix", "start og slutt må ligge i prefikset")
    if int(start) > int(end):
        raise ipam_error(400, "invalid_range", "start_address må være mindre eller lik end_address")
    return str(start), str(end)


def _overlaps(a_start: str, a_end: str, b_start: str, b_end: str) -> bool:
    return int(ipaddress.IPv6Address(a_start)) <= int(ipaddress.IPv6Address(b_end)) and int(
        ipaddress.IPv6Address(b_start)
    ) <= int(ipaddress.IPv6Address(a_end))


def _reject_overlap(
    db: Session,
    prefix_id: int,
    start: str,
    end: str,
    *,
    exclude_id: int | None = None,
) -> None:
    for row in list_ipv6_ranges(db, prefix_id):
        if exclude_id is not None and row.id == exclude_id:
            continue
        if _overlaps(start, end, row.start_address, row.end_address):
            raise ipam_error(409, "range_overlap", "området overlapper et eksisterende område på prefikset")


def _unique_slug(db: Session, prefix_id: int, desired: str, *, exclude_id: int | None = None) -> str:
    base = slugify_prefix(desired)
    candidate = base
    n = 2
    while True:
        q = select(IpamIpv6Range.id).where(IpamIpv6Range.ipv6_prefix_id == prefix_id, IpamIpv6Range.slug == candidate)
        if exclude_id is not None:
            q = q.where(IpamIpv6Range.id != exclude_id)
        if db.execute(q).scalar_one_or_none() is None:
            return candidate
        suffix = f"-{n}"
        candidate = f"{base[: 128 - len(suffix)]}{suffix}"
        n += 1
        if n > 1000:
            raise ipam_error(400, "slug_exhausted", "kunne ikke lage unik slug")


def create_ipv6_range(db: Session, pfx: IpamIpv6Prefix, data: Ipv6RangeCreate) -> Ipv6RangeRead:
    require_site_write(db, pfx.site_id)
    kind = data.kind if data.kind in IPV6_RANGE_KINDS else "allocation"
    start, end = _validate_span(pfx, data.start_address, data.end_address)
    _reject_overlap(db, pfx.id, start, end)
    slug = _unique_slug(db, pfx.id, data.slug or data.name)
    row = IpamIpv6Range(
        ipv6_prefix_id=pfx.id,
        name=data.name,
        slug=slug,
        kind=kind,
        start_address=start,
        end_address=end,
        description=data.description,
    )
    db.add(row)
    try:
        db.commit()
        db.refresh(row)
    except IntegrityError:
        db.rollback()
        raise ipam_error(409, "range_conflict", "område med samme slug eller spenn finnes allerede") from None
    return range_to_read(row)


def update_ipv6_range(db: Session, row: IpamIpv6Range, data: Ipv6RangeUpdate) -> Ipv6RangeRead:
    pfx = db.get(IpamIpv6Prefix, row.ipv6_prefix_id)
    if pfx is None:
        raise ipam_error(404, "prefix_not_found", "prefiks ikke funnet")
    require_site_write(db, pfx.site_id)
    start = data.start_address if data.start_address is not None else row.start_address
    end = data.end_address if data.end_address is not None else row.end_address
    start, end = _validate_span(pfx, start, end)
    _reject_overlap(db, pfx.id, start, end, exclude_id=row.id)
    if data.name is not None:
        row.name = data.name
    if data.kind is not None:
        row.kind = data.kind if data.kind in IPV6_RANGE_KINDS else row.kind
    if data.description is not None:
        row.description = data.description
    if data.slug is not None:
        row.slug = _unique_slug(db, pfx.id, data.slug, exclude_id=row.id)
    row.start_address = start
    row.end_address = end
    try:
        db.commit()
        db.refresh(row)
    except IntegrityError:
        db.rollback()
        raise ipam_error(409, "range_conflict", "område med samme slug eller spenn finnes allerede") from None
    return range_to_read(row)


def delete_ipv6_range(db: Session, row: IpamIpv6Range) -> None:
    pfx = db.get(IpamIpv6Prefix, row.ipv6_prefix_id)
    if pfx is not None:
        require_site_write(db, pfx.site_id)
    db.delete(row)
    db.commit()
