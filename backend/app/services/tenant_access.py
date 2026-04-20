"""Tenant-medlemskap og DCIM-grants."""

from __future__ import annotations

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.iam import User
from app.models.tenant import Tenant
from app.models.tenant_access import TenantDcimGrant, TenantUserMembership
from app.schemas.tenant import TenantDcimGrantCreate, TenantUserMembershipCreate
from app.services import dcim as dcim_svc


def list_tenant_members(db: Session, tenant_id: int) -> list[TenantUserMembership]:
    return list(
        db.execute(
            select(TenantUserMembership)
            .where(TenantUserMembership.tenant_id == tenant_id)
            .order_by(TenantUserMembership.created_at),
        ).scalars().all(),
    )


def add_tenant_member(db: Session, tenant: Tenant, data: TenantUserMembershipCreate) -> TenantUserMembership:
    if db.get(User, data.user_id) is None:
        raise HTTPException(status_code=404, detail="bruker ikke funnet")
    row = TenantUserMembership(
        tenant_id=tenant.id,
        user_id=data.user_id,
        role=data.role.strip(),
    )
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="brukeren er allerede medlem av denne tenanten",
        ) from None
    db.refresh(row)
    return row


def remove_tenant_member(db: Session, tenant_id: int, user_id: int) -> None:
    row = db.execute(
        select(TenantUserMembership).where(
            TenantUserMembership.tenant_id == tenant_id,
            TenantUserMembership.user_id == user_id,
        ),
    ).scalar_one_or_none()
    if row is None:
        raise HTTPException(status_code=404, detail="medlemskap ikke funnet")
    db.delete(row)
    db.commit()


def _validate_grant_scope(db: Session, scope_type: str, scope_id: int) -> None:
    if scope_type == "site":
        if dcim_svc.get_site(db, scope_id) is None:
            raise HTTPException(status_code=404, detail="site ikke funnet")
    elif scope_type == "room":
        if dcim_svc.get_room(db, scope_id) is None:
            raise HTTPException(status_code=404, detail="rom ikke funnet")
    elif scope_type == "rack":
        if dcim_svc.get_rack(db, scope_id) is None:
            raise HTTPException(status_code=404, detail="rack ikke funnet")
    else:
        raise HTTPException(status_code=400, detail="ugyldig scope_type")


def list_tenant_dcim_grants(db: Session, tenant_id: int) -> list[TenantDcimGrant]:
    return list(
        db.execute(
            select(TenantDcimGrant)
            .where(TenantDcimGrant.tenant_id == tenant_id)
            .order_by(TenantDcimGrant.scope_type, TenantDcimGrant.scope_id),
        ).scalars().all(),
    )


def add_tenant_dcim_grant(db: Session, tenant: Tenant, data: TenantDcimGrantCreate) -> TenantDcimGrant:
    _validate_grant_scope(db, data.scope_type, data.scope_id)
    row = TenantDcimGrant(
        tenant_id=tenant.id,
        scope_type=data.scope_type,
        scope_id=data.scope_id,
        access=data.access,
    )
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="grant for samme omfang finnes allerede for denne tenanten",
        ) from None
    db.refresh(row)
    return row


def remove_tenant_dcim_grant(db: Session, tenant_id: int, grant_id: int) -> None:
    row = db.execute(
        select(TenantDcimGrant).where(
            TenantDcimGrant.tenant_id == tenant_id,
            TenantDcimGrant.id == grant_id,
        ),
    ).scalar_one_or_none()
    if row is None:
        raise HTTPException(status_code=404, detail="grant ikke funnet")
    db.delete(row)
    db.commit()


def ensure_tenant_exists(db: Session, tenant_id: int) -> Tenant:
    t = db.get(Tenant, tenant_id)
    if t is None:
        raise HTTPException(status_code=404, detail="tenant ikke funnet")
    return t
