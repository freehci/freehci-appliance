"""VRF-instans på enhet: registrert rutekontekst, ikke påført config."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.dcim import DeviceInstance
from app.models.ipam import IpamVrf, IpamVrfInstance
from app.schemas.ipam import (
    VRF_INSTANCE_INTENTS,
    IpamVrfInstanceCreate,
    IpamVrfInstanceRead,
    IpamVrfInstanceUpdate,
)
from app.services import dcim as dcim_svc
from app.services.federation_guard import require_site_write
from app.services.ipam import slugify_prefix
from app.services.ipam_errors import ipam_error


def instance_to_read(db: Session, row: IpamVrfInstance) -> IpamVrfInstanceRead:
    vrf = db.get(IpamVrf, row.vrf_id)
    device = db.get(DeviceInstance, row.device_id)
    vrf_rd = vrf.route_distinguisher if vrf is not None else None
    return IpamVrfInstanceRead(
        id=row.id,
        vrf_id=row.vrf_id,
        vrf_name=vrf.name if vrf is not None else "",
        vrf_slug=vrf.slug if vrf is not None else "",
        device_id=row.device_id,
        device_name=device.name if device is not None else "",
        slug=row.slug,
        intent=row.intent,
        route_distinguisher=row.route_distinguisher,
        effective_rd=row.route_distinguisher or vrf_rd,
        description=row.description,
        created_at=row.created_at,
    )


def get_instance(db: Session, instance_id: int) -> IpamVrfInstance | None:
    return db.get(IpamVrfInstance, instance_id)


def get_instance_by_slug(db: Session, vrf_id: int, slug: str) -> IpamVrfInstance | None:
    return db.execute(
        select(IpamVrfInstance).where(
            IpamVrfInstance.vrf_id == vrf_id,
            IpamVrfInstance.slug == slug.strip().lower(),
        )
    ).scalar_one_or_none()


def list_instances(
    db: Session,
    *,
    vrf_id: int | None = None,
    device_id: int | None = None,
    site_id: int | None = None,
) -> list[IpamVrfInstance]:
    q = select(IpamVrfInstance).order_by(IpamVrfInstance.id)
    if vrf_id is not None:
        q = q.where(IpamVrfInstance.vrf_id == vrf_id)
    if device_id is not None:
        q = q.where(IpamVrfInstance.device_id == device_id)
    if site_id is not None:
        q = q.join(IpamVrf, IpamVrf.id == IpamVrfInstance.vrf_id).where(IpamVrf.site_id == site_id)
    return list(db.execute(q).scalars().all())


def _unique_slug(db: Session, vrf_id: int, desired: str, *, exclude_id: int | None = None) -> str:
    base = slugify_prefix(desired)
    candidate = base
    n = 2
    while True:
        q = select(IpamVrfInstance.id).where(IpamVrfInstance.vrf_id == vrf_id, IpamVrfInstance.slug == candidate)
        if exclude_id is not None:
            q = q.where(IpamVrfInstance.id != exclude_id)
        if db.execute(q).scalar_one_or_none() is None:
            return candidate
        suffix = f"-{n}"
        candidate = f"{base[: 128 - len(suffix)]}{suffix}"
        n += 1
        if n > 1000:
            raise ipam_error(400, "slug_exhausted", "kunne ikke lage unik slug")


def _require_device_on_vrf_site(db: Session, vrf: IpamVrf, device_id: int) -> DeviceInstance:
    device = dcim_svc.get_device(db, device_id)
    if device is None:
        raise ipam_error(404, "device_not_found", "enhet ikke funnet")
    site = dcim_svc.device_effective_site_id(db, device.id)
    if site is None:
        raise ipam_error(400, "device_site_required", "enheten må tilhøre en site før VRF kan registreres")
    if int(site) != vrf.site_id:
        raise ipam_error(400, "site_mismatch", "enhetens site stemmer ikke med VRF-ens site")
    return device


def create_instance(db: Session, vrf: IpamVrf, data: IpamVrfInstanceCreate) -> IpamVrfInstanceRead:
    require_site_write(db, vrf.site_id)
    device = _require_device_on_vrf_site(db, vrf, data.device_id)
    intent = data.intent if data.intent in VRF_INSTANCE_INTENTS else "recorded"
    slug = _unique_slug(db, vrf.id, data.slug or device.name)
    existing = db.execute(
        select(IpamVrfInstance.id).where(
            IpamVrfInstance.vrf_id == vrf.id,
            IpamVrfInstance.device_id == device.id,
        )
    ).scalar_one_or_none()
    if existing is not None:
        raise ipam_error(409, "vrf_instance_exists", "VRF er allerede registrert på denne enheten")
    row = IpamVrfInstance(
        vrf_id=vrf.id,
        device_id=device.id,
        slug=slug,
        intent=intent,
        route_distinguisher=data.route_distinguisher,
        description=data.description,
    )
    db.add(row)
    try:
        db.commit()
        db.refresh(row)
    except IntegrityError:
        db.rollback()
        raise ipam_error(409, "vrf_instance_exists", "VRF er allerede registrert på denne enheten") from None
    return instance_to_read(db, row)


def update_instance(db: Session, row: IpamVrfInstance, data: IpamVrfInstanceUpdate) -> IpamVrfInstanceRead:
    vrf = db.get(IpamVrf, row.vrf_id)
    if vrf is None:
        raise ipam_error(404, "vrf_not_found", "VRF ikke funnet")
    require_site_write(db, vrf.site_id)
    if data.slug is not None:
        row.slug = _unique_slug(db, vrf.id, data.slug, exclude_id=row.id)
    if data.intent is not None:
        row.intent = data.intent if data.intent in VRF_INSTANCE_INTENTS else row.intent
    if data.route_distinguisher is not None or "route_distinguisher" in data.model_dump(exclude_unset=True):
        row.route_distinguisher = data.route_distinguisher
    if data.description is not None:
        row.description = data.description
    try:
        db.commit()
        db.refresh(row)
    except IntegrityError:
        db.rollback()
        raise ipam_error(409, "vrf_instance_conflict", "slug er allerede i bruk på denne VRF-en") from None
    return instance_to_read(db, row)


def delete_instance(db: Session, row: IpamVrfInstance) -> None:
    vrf = db.get(IpamVrf, row.vrf_id)
    if vrf is not None:
        require_site_write(db, vrf.site_id)
    db.delete(row)
    db.commit()
