"""IPv4-område/pool som inventory-vindu. Ikke DHCP-tjeneste, lease eller DNS."""

from __future__ import annotations

import ipaddress

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, object_session

from app.models.ipam import IpamIpv4Prefix, IpamIpv4Range
from app.schemas.ipam import IPV4_RANGE_KINDS, Ipv4RangeCreate, Ipv4RangeRead, Ipv4RangeUpdate
from app.services.federation_guard import require_site_write
from app.services.ipam import slugify_prefix
from app.services.ipam_errors import ipam_error


def inclusive_range_ips(cidr: str, start_s: str, end_s: str) -> set[str]:
    try:
        start = ipaddress.ip_address(str(start_s).strip())
        end = ipaddress.ip_address(str(end_s).strip())
        net = ipaddress.ip_network(cidr, strict=False)
    except ValueError:
        return set()
    if not isinstance(start, ipaddress.IPv4Address) or not isinstance(end, ipaddress.IPv4Address):
        return set()
    if int(start) > int(end):
        start, end = end, start
    last = min(int(end), int(start) + 65536)
    out: set[str] = set()
    for n in range(int(start), last + 1):
        ip = ipaddress.IPv4Address(n)
        if ip in net:
            out.add(str(ip))
    return out


def first_class_range_ips(pfx: IpamIpv4Prefix, kinds: set[str] | frozenset[str]) -> set[str]:
    db = object_session(pfx)
    if db is None or pfx.id is None:
        return set()
    rows = db.execute(
        select(IpamIpv4Range).where(
            IpamIpv4Range.ipv4_prefix_id == pfx.id,
            IpamIpv4Range.kind.in_(tuple(kinds)),
        )
    ).scalars().all()
    out: set[str] = set()
    for row in rows:
        out |= inclusive_range_ips(pfx.cidr, row.start_address, row.end_address)
    return out


def allocation_pool_ips(pfx: IpamIpv4Prefix) -> set[str] | None:
    db = object_session(pfx)
    if db is None or pfx.id is None:
        return None
    rows = db.execute(
        select(IpamIpv4Range).where(
            IpamIpv4Range.ipv4_prefix_id == pfx.id,
            IpamIpv4Range.kind == "allocation",
        )
    ).scalars().all()
    if not rows:
        return None
    out: set[str] = set()
    for row in rows:
        out |= inclusive_range_ips(pfx.cidr, row.start_address, row.end_address)
    return out


def range_to_read(row: IpamIpv4Range) -> Ipv4RangeRead:
    return Ipv4RangeRead.model_validate(row)


def get_ipv4_range(db: Session, range_id: int) -> IpamIpv4Range | None:
    return db.get(IpamIpv4Range, range_id)


def get_ipv4_range_by_slug(db: Session, prefix_id: int, slug: str) -> IpamIpv4Range | None:
    return db.execute(
        select(IpamIpv4Range).where(
            IpamIpv4Range.ipv4_prefix_id == prefix_id,
            IpamIpv4Range.slug == slug.strip().lower(),
        )
    ).scalar_one_or_none()


def list_ipv4_ranges(db: Session, prefix_id: int) -> list[IpamIpv4Range]:
    return list(
        db.execute(
            select(IpamIpv4Range)
            .where(IpamIpv4Range.ipv4_prefix_id == prefix_id)
            .order_by(IpamIpv4Range.start_address, IpamIpv4Range.id)
        ).scalars().all()
    )


def _parse_bound(raw: str, *, label: str) -> ipaddress.IPv4Address:
    try:
        ip = ipaddress.ip_address(raw.strip())
    except ValueError as e:
        raise ipam_error(400, "invalid_range_address", f"{label} er ikke en gyldig IPv4-adresse") from e
    if not isinstance(ip, ipaddress.IPv4Address):
        raise ipam_error(400, "invalid_range_address", f"{label} må være IPv4")
    return ip


def _validate_span(
    pfx: IpamIpv4Prefix,
    start_s: str,
    end_s: str,
) -> tuple[str, str]:
    start = _parse_bound(start_s, label="start_address")
    end = _parse_bound(end_s, label="end_address")
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
    return int(ipaddress.IPv4Address(a_start)) <= int(ipaddress.IPv4Address(b_end)) and int(
        ipaddress.IPv4Address(b_start)
    ) <= int(ipaddress.IPv4Address(a_end))


def _reject_overlap(
    db: Session,
    prefix_id: int,
    start: str,
    end: str,
    *,
    exclude_id: int | None = None,
) -> None:
    rows = list_ipv4_ranges(db, prefix_id)
    for row in rows:
        if exclude_id is not None and row.id == exclude_id:
            continue
        if _overlaps(start, end, row.start_address, row.end_address):
            raise ipam_error(409, "range_overlap", "området overlapper et eksisterende område på prefikset")


def _unique_slug(db: Session, prefix_id: int, desired: str, *, exclude_id: int | None = None) -> str:
    base = slugify_prefix(desired)
    candidate = base
    n = 2
    while True:
        q = select(IpamIpv4Range.id).where(IpamIpv4Range.ipv4_prefix_id == prefix_id, IpamIpv4Range.slug == candidate)
        if exclude_id is not None:
            q = q.where(IpamIpv4Range.id != exclude_id)
        if db.execute(q).scalar_one_or_none() is None:
            return candidate
        suffix = f"-{n}"
        candidate = f"{base[: 128 - len(suffix)]}{suffix}"
        n += 1
        if n > 1000:
            raise ipam_error(400, "slug_exhausted", "kunne ikke lage unik slug")


def create_ipv4_range(db: Session, pfx: IpamIpv4Prefix, data: Ipv4RangeCreate) -> Ipv4RangeRead:
    require_site_write(db, pfx.site_id)
    kind = data.kind if data.kind in IPV4_RANGE_KINDS else "allocation"
    start, end = _validate_span(pfx, data.start_address, data.end_address)
    _reject_overlap(db, pfx.id, start, end)
    slug = _unique_slug(db, pfx.id, data.slug or data.name)
    row = IpamIpv4Range(
        ipv4_prefix_id=pfx.id,
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


def update_ipv4_range(db: Session, row: IpamIpv4Range, data: Ipv4RangeUpdate) -> Ipv4RangeRead:
    pfx = db.get(IpamIpv4Prefix, row.ipv4_prefix_id)
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
        row.kind = data.kind if data.kind in IPV4_RANGE_KINDS else row.kind
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


def delete_ipv4_range(db: Session, row: IpamIpv4Range) -> None:
    pfx = db.get(IpamIpv4Prefix, row.ipv4_prefix_id)
    if pfx is not None:
        require_site_write(db, pfx.site_id)
    db.delete(row)
    db.commit()
