"""Dual-stack-grupper. Samme navn eller CIDR er ikke en paring."""

from __future__ import annotations

import re

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.ipam import IpamDualStackGroup, IpamIpv4Prefix, IpamIpv6Prefix
from app.schemas.ipam import IpamDualStackGroupCreate, IpamDualStackGroupRead
from app.services.ipam_errors import ipam_error


def _slugify(value: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", (value or "").strip().lower()).strip("-")
    return (s or "dual-stack")[:128]


def _unique_slug(db: Session, desired: str, *, explicit: bool, exclude_id: int | None = None) -> str:
    base = _slugify(desired)
    if explicit:
        q = select(IpamDualStackGroup.id).where(IpamDualStackGroup.slug == base)
        if exclude_id is not None:
            q = q.where(IpamDualStackGroup.id != exclude_id)
        if db.execute(q).scalar_one_or_none() is not None:
            raise ipam_error(409, "dual_stack_slug", "dual-stack-slug finnes allerede")
        return base
    candidate = base
    n = 2
    while True:
        q = select(IpamDualStackGroup.id).where(IpamDualStackGroup.slug == candidate)
        if exclude_id is not None:
            q = q.where(IpamDualStackGroup.id != exclude_id)
        if db.execute(q).scalar_one_or_none() is None:
            return candidate
        candidate = f"{base}-{n}"[:128]
        n += 1


def list_groups(db: Session) -> list[IpamDualStackGroup]:
    return list(db.execute(select(IpamDualStackGroup).order_by(IpamDualStackGroup.slug)).scalars().all())


def get_group(db: Session, group_id: int) -> IpamDualStackGroup | None:
    return db.get(IpamDualStackGroup, group_id)


def get_group_by_slug(db: Session, slug: str) -> IpamDualStackGroup | None:
    return db.execute(select(IpamDualStackGroup).where(IpamDualStackGroup.slug == slug)).scalar_one_or_none()


def require_existing(db: Session, group_id: int | None) -> int | None:
    if group_id is None:
        return None
    if get_group(db, group_id) is None:
        raise ipam_error(400, "dual_stack_group", "dual-stack-gruppe ikke funnet")
    return group_id


def resolve_ref(db: Session, *, group_id: int | None = None, group_slug: str | None = None) -> int | None:
    slug = (group_slug or "").strip()
    if slug:
        row = get_group_by_slug(db, slug)
        if row is None:
            raise ipam_error(400, "dual_stack_group", "dual-stack-gruppe ikke funnet")
        return row.id
    return require_existing(db, group_id)


def labels(db: Session, group_id: int | None) -> tuple[str | None, str | None]:
    if group_id is None:
        return None, None
    row = get_group(db, group_id)
    if row is None:
        return None, None
    return row.slug, row.name


def create_group(db: Session, data: IpamDualStackGroupCreate) -> IpamDualStackGroup:
    slug = _unique_slug(db, data.slug or data.name, explicit=data.slug is not None)
    row = IpamDualStackGroup(name=data.name.strip(), slug=slug, notes=data.notes)
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ipam_error(409, "dual_stack_slug", "dual-stack-slug finnes allerede")
    db.refresh(row)
    return row


def delete_group(db: Session, row: IpamDualStackGroup) -> None:
    db.execute(update(IpamIpv4Prefix).where(IpamIpv4Prefix.dual_stack_group_id == row.id).values(dual_stack_group_id=None))
    db.execute(update(IpamIpv6Prefix).where(IpamIpv6Prefix.dual_stack_group_id == row.id).values(dual_stack_group_id=None))
    db.delete(row)
    db.commit()


def group_to_read(row: IpamDualStackGroup) -> IpamDualStackGroupRead:
    return IpamDualStackGroupRead.model_validate(row)
