"""Tenant-forretningslogikk."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.tenant import Tenant
from app.schemas.tenant import TenantCreate, TenantUpdate


def ensure_default_tenant(db: Session) -> int:
    row = db.execute(select(Tenant).where(Tenant.slug == "default").limit(1)).scalar_one_or_none()
    if row is not None:
        return row.id
    t = Tenant(name="Default", slug="default", description="Auto-opprettet standard-tenant")
    db.add(t)
    db.commit()
    db.refresh(t)
    return t.id


def list_tenants(db: Session) -> list[Tenant]:
    return list(db.execute(select(Tenant).order_by(Tenant.name)).scalars().all())


def get_tenant(db: Session, tenant_id: int) -> Tenant | None:
    return db.get(Tenant, tenant_id)


def create_tenant(db: Session, data: TenantCreate) -> Tenant:
    row = Tenant(name=data.name.strip(), slug=data.slug, description=data.description)
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise
    db.refresh(row)
    return row


def update_tenant(db: Session, row: Tenant, data: TenantUpdate) -> Tenant:
    if data.name is not None:
        row.name = data.name.strip()
    if data.description is not None:
        row.description = data.description
    db.commit()
    db.refresh(row)
    return row
