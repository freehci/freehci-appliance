"""Adresseplan. Samme CIDR, VRF-navn eller site-navn er ikke medlemskap."""

from __future__ import annotations

import re

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.ipam import IpamAddressSpace, IpamIpv4Prefix, IpamIpv6Prefix
from app.schemas.ipam import IpamAddressSpaceCreate, IpamAddressSpaceRead
from app.services.ipam_errors import ipam_error


def _slugify(value: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", (value or "").strip().lower()).strip("-")
    return (s or "address-space")[:128]


def _unique_slug(db: Session, desired: str, *, explicit: bool, exclude_id: int | None = None) -> str:
    base = _slugify(desired)
    if explicit:
        q = select(IpamAddressSpace.id).where(IpamAddressSpace.slug == base)
        if exclude_id is not None:
            q = q.where(IpamAddressSpace.id != exclude_id)
        if db.execute(q).scalar_one_or_none() is not None:
            raise ipam_error(409, "address_space_slug", "adresseplan-slug finnes allerede")
        return base
    candidate = base
    n = 2
    while True:
        q = select(IpamAddressSpace.id).where(IpamAddressSpace.slug == candidate)
        if exclude_id is not None:
            q = q.where(IpamAddressSpace.id != exclude_id)
        if db.execute(q).scalar_one_or_none() is None:
            return candidate
        candidate = f"{base}-{n}"[:128]
        n += 1


def list_spaces(db: Session) -> list[IpamAddressSpace]:
    return list(db.execute(select(IpamAddressSpace).order_by(IpamAddressSpace.slug)).scalars().all())


def get_space(db: Session, space_id: int) -> IpamAddressSpace | None:
    return db.get(IpamAddressSpace, space_id)


def get_space_by_slug(db: Session, slug: str) -> IpamAddressSpace | None:
    return db.execute(select(IpamAddressSpace).where(IpamAddressSpace.slug == slug)).scalar_one_or_none()


def require_existing(db: Session, space_id: int | None) -> int | None:
    if space_id is None:
        return None
    if get_space(db, space_id) is None:
        raise ipam_error(400, "address_space", "adresseplan ikke funnet")
    return space_id


def resolve_ref(db: Session, *, space_id: int | None = None, space_slug: str | None = None) -> int | None:
    slug = (space_slug or "").strip()
    if slug:
        row = get_space_by_slug(db, slug)
        if row is None:
            raise ipam_error(400, "address_space", "adresseplan ikke funnet")
        return row.id
    return require_existing(db, space_id)


def labels(db: Session, space_id: int | None) -> tuple[str | None, str | None]:
    if space_id is None:
        return None, None
    row = get_space(db, space_id)
    if row is None:
        return None, None
    return row.slug, row.name


def create_space(db: Session, data: IpamAddressSpaceCreate) -> IpamAddressSpace:
    slug = _unique_slug(db, data.slug or data.name, explicit=data.slug is not None)
    row = IpamAddressSpace(name=data.name.strip(), slug=slug, notes=data.notes)
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ipam_error(409, "address_space_slug", "adresseplan-slug finnes allerede")
    db.refresh(row)
    return row


def delete_space(db: Session, row: IpamAddressSpace) -> None:
    db.execute(update(IpamIpv4Prefix).where(IpamIpv4Prefix.address_space_id == row.id).values(address_space_id=None))
    db.execute(update(IpamIpv6Prefix).where(IpamIpv6Prefix.address_space_id == row.id).values(address_space_id=None))
    db.delete(row)
    db.commit()


def space_to_read(row: IpamAddressSpace) -> IpamAddressSpaceRead:
    return IpamAddressSpaceRead.model_validate(row)
