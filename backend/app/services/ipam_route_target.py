"""Route target som inventory. Ikke RD, og ikke påført import/eksport-policy."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.ipam import IpamRouteTarget, IpamVrf, IpamVrfRouteTarget
from app.schemas.ipam import (
    ROUTE_TARGET_DIRECTIONS,
    IpamRouteTargetCreate,
    IpamRouteTargetRead,
    IpamRouteTargetUpdate,
    IpamVrfRouteTargetCreate,
    IpamVrfRouteTargetRead,
)
from app.services.federation_guard import require_site_write
from app.services.ipam import slugify_prefix
from app.services.ipam_errors import ipam_error


def rt_to_read(row: IpamRouteTarget) -> IpamRouteTargetRead:
    return IpamRouteTargetRead.model_validate(row)


def binding_to_read(db: Session, row: IpamVrfRouteTarget) -> IpamVrfRouteTargetRead:
    vrf = db.get(IpamVrf, row.vrf_id)
    rt = db.get(IpamRouteTarget, row.route_target_id)
    return IpamVrfRouteTargetRead(
        id=row.id,
        vrf_id=row.vrf_id,
        vrf_name=vrf.name if vrf is not None else "",
        vrf_slug=vrf.slug if vrf is not None else "",
        route_target_id=row.route_target_id,
        route_target_slug=rt.slug if rt is not None else "",
        route_target_name=rt.name if rt is not None else "",
        value=rt.value if rt is not None else "",
        direction=row.direction,
    )


def get_route_target(db: Session, rt_id: int) -> IpamRouteTarget | None:
    return db.get(IpamRouteTarget, rt_id)


def get_route_target_by_slug(db: Session, slug: str) -> IpamRouteTarget | None:
    return db.execute(select(IpamRouteTarget).where(IpamRouteTarget.slug == slug.strip().lower())).scalar_one_or_none()


def list_route_targets(db: Session) -> list[IpamRouteTarget]:
    return list(db.execute(select(IpamRouteTarget).order_by(IpamRouteTarget.value, IpamRouteTarget.id)).scalars().all())


def _unique_slug(db: Session, desired: str, *, exclude_id: int | None = None) -> str:
    base = slugify_prefix(desired)
    candidate = base
    n = 2
    while True:
        q = select(IpamRouteTarget.id).where(IpamRouteTarget.slug == candidate)
        if exclude_id is not None:
            q = q.where(IpamRouteTarget.id != exclude_id)
        if db.execute(q).scalar_one_or_none() is None:
            return candidate
        suffix = f"-{n}"
        candidate = f"{base[: 128 - len(suffix)]}{suffix}"
        n += 1
        if n > 1000:
            raise ipam_error(400, "slug_exhausted", "kunne ikke lage unik slug")


def create_route_target(db: Session, data: IpamRouteTargetCreate) -> IpamRouteTargetRead:
    row = IpamRouteTarget(
        name=data.name,
        slug=_unique_slug(db, data.slug or data.name),
        value=data.value,
        description=data.description,
    )
    db.add(row)
    try:
        db.commit()
        db.refresh(row)
    except IntegrityError:
        db.rollback()
        raise ipam_error(409, "route_target_conflict", "route target med samme slug eller verdi finnes allerede") from None
    return rt_to_read(row)


def update_route_target(db: Session, row: IpamRouteTarget, data: IpamRouteTargetUpdate) -> IpamRouteTargetRead:
    if data.name is not None:
        row.name = data.name
    if data.slug is not None:
        row.slug = _unique_slug(db, data.slug, exclude_id=row.id)
    if data.value is not None:
        row.value = data.value
    if data.description is not None:
        row.description = data.description
    try:
        db.commit()
        db.refresh(row)
    except IntegrityError:
        db.rollback()
        raise ipam_error(409, "route_target_conflict", "route target med samme slug eller verdi finnes allerede") from None
    return rt_to_read(row)


def delete_route_target(db: Session, row: IpamRouteTarget) -> None:
    for bind in list(
        db.execute(select(IpamVrfRouteTarget).where(IpamVrfRouteTarget.route_target_id == row.id)).scalars().all()
    ):
        db.delete(bind)
    db.delete(row)
    db.commit()


def list_vrf_bindings(db: Session, *, vrf_id: int | None = None, site_id: int | None = None) -> list[IpamVrfRouteTarget]:
    q = select(IpamVrfRouteTarget).order_by(IpamVrfRouteTarget.id)
    if vrf_id is not None:
        q = q.where(IpamVrfRouteTarget.vrf_id == vrf_id)
    if site_id is not None:
        q = q.join(IpamVrf, IpamVrf.id == IpamVrfRouteTarget.vrf_id).where(IpamVrf.site_id == site_id)
    return list(db.execute(q).scalars().all())


def get_binding(db: Session, binding_id: int) -> IpamVrfRouteTarget | None:
    return db.get(IpamVrfRouteTarget, binding_id)


def bind_vrf_route_target(db: Session, vrf: IpamVrf, data: IpamVrfRouteTargetCreate) -> IpamVrfRouteTargetRead:
    require_site_write(db, vrf.site_id)
    rt = get_route_target(db, data.route_target_id)
    if rt is None:
        raise ipam_error(404, "route_target_not_found", "route target ikke funnet")
    direction = data.direction if data.direction in ROUTE_TARGET_DIRECTIONS else "import"
    existing = db.execute(
        select(IpamVrfRouteTarget.id).where(
            IpamVrfRouteTarget.vrf_id == vrf.id,
            IpamVrfRouteTarget.route_target_id == rt.id,
            IpamVrfRouteTarget.direction == direction,
        )
    ).scalar_one_or_none()
    if existing is not None:
        raise ipam_error(409, "vrf_route_target_exists", "denne VRF-en har allerede denne RT-en i denne retningen")
    row = IpamVrfRouteTarget(vrf_id=vrf.id, route_target_id=rt.id, direction=direction)
    db.add(row)
    try:
        db.commit()
        db.refresh(row)
    except IntegrityError:
        db.rollback()
        raise ipam_error(409, "vrf_route_target_exists", "denne VRF-en har allerede denne RT-en i denne retningen") from None
    return binding_to_read(db, row)


def unbind_vrf_route_target(db: Session, row: IpamVrfRouteTarget) -> None:
    vrf = db.get(IpamVrf, row.vrf_id)
    if vrf is not None:
        require_site_write(db, vrf.site_id)
    db.delete(row)
    db.commit()
