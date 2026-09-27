"""L2-domene. Samme VID, navn eller A–B-strekning er ikke medlemskap."""

from __future__ import annotations

import re

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.ipam import IpamL2Domain, IpamVlan
from app.schemas.ipam import IpamL2DomainCreate, IpamL2DomainRead
from app.services.ipam_errors import ipam_error


def _slugify(value: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", (value or "").strip().lower()).strip("-")
    return (s or "l2-domain")[:128]


def _unique_slug(db: Session, desired: str, *, explicit: bool, exclude_id: int | None = None) -> str:
    base = _slugify(desired)
    if explicit:
        q = select(IpamL2Domain.id).where(IpamL2Domain.slug == base)
        if exclude_id is not None:
            q = q.where(IpamL2Domain.id != exclude_id)
        if db.execute(q).scalar_one_or_none() is not None:
            raise ipam_error(409, "l2_domain_slug", "L2-domene-slug finnes allerede")
        return base
    candidate = base
    n = 2
    while True:
        q = select(IpamL2Domain.id).where(IpamL2Domain.slug == candidate)
        if exclude_id is not None:
            q = q.where(IpamL2Domain.id != exclude_id)
        if db.execute(q).scalar_one_or_none() is None:
            return candidate
        candidate = f"{base}-{n}"[:128]
        n += 1


def list_domains(db: Session) -> list[IpamL2Domain]:
    return list(db.execute(select(IpamL2Domain).order_by(IpamL2Domain.slug)).scalars().all())


def get_domain(db: Session, domain_id: int) -> IpamL2Domain | None:
    return db.get(IpamL2Domain, domain_id)


def get_domain_by_slug(db: Session, slug: str) -> IpamL2Domain | None:
    return db.execute(select(IpamL2Domain).where(IpamL2Domain.slug == slug)).scalar_one_or_none()


def require_existing(db: Session, domain_id: int | None) -> int | None:
    if domain_id is None:
        return None
    if get_domain(db, domain_id) is None:
        raise ipam_error(400, "l2_domain", "L2-domene ikke funnet")
    return domain_id


def resolve_ref(db: Session, *, domain_id: int | None = None, domain_slug: str | None = None) -> int | None:
    slug = (domain_slug or "").strip()
    if slug:
        row = get_domain_by_slug(db, slug)
        if row is None:
            raise ipam_error(400, "l2_domain", "L2-domene ikke funnet")
        return row.id
    return require_existing(db, domain_id)


def labels(db: Session, domain_id: int | None) -> tuple[str | None, str | None]:
    if domain_id is None:
        return None, None
    row = get_domain(db, domain_id)
    if row is None:
        return None, None
    return row.slug, row.name


def create_domain(db: Session, data: IpamL2DomainCreate) -> IpamL2Domain:
    slug = _unique_slug(db, data.slug or data.name, explicit=data.slug is not None)
    row = IpamL2Domain(name=data.name.strip(), slug=slug, notes=data.notes)
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ipam_error(409, "l2_domain_slug", "L2-domene-slug finnes allerede")
    db.refresh(row)
    return row


def delete_domain(db: Session, row: IpamL2Domain) -> None:
    db.execute(update(IpamVlan).where(IpamVlan.l2_domain_id == row.id).values(l2_domain_id=None))
    db.delete(row)
    db.commit()


def domain_to_read(row: IpamL2Domain) -> IpamL2DomainRead:
    return IpamL2DomainRead.model_validate(row)
