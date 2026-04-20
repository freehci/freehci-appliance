"""Tenants API."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.tenant import (
    TenantCreate,
    TenantDcimGrantCreate,
    TenantDcimGrantRead,
    TenantRead,
    TenantUpdate,
    TenantUserMembershipCreate,
    TenantUserMembershipRead,
)
from app.services import tenant as tenant_svc
from app.services import tenant_access as tenant_access_svc

router = APIRouter(prefix="/tenants", tags=["tenants"])


@router.get("", response_model=list[TenantRead])
def list_tenants(db: Session = Depends(get_db)) -> list[TenantRead]:
    return [TenantRead.model_validate(r) for r in tenant_svc.list_tenants(db)]


@router.post("", response_model=TenantRead)
def create_tenant(data: TenantCreate, db: Session = Depends(get_db)) -> TenantRead:
    try:
        row = tenant_svc.create_tenant(db, data)
    except IntegrityError as e:
        raise HTTPException(status_code=409, detail="tenant med samme slug finnes allerede") from e
    return TenantRead.model_validate(row)


@router.get("/{tenant_id}", response_model=TenantRead)
def get_tenant(tenant_id: int, db: Session = Depends(get_db)) -> TenantRead:
    row = tenant_svc.get_tenant(db, tenant_id)
    if row is None:
        raise HTTPException(status_code=404, detail="tenant ikke funnet")
    return TenantRead.model_validate(row)


@router.patch("/{tenant_id}", response_model=TenantRead)
def patch_tenant(
    tenant_id: int,
    data: TenantUpdate,
    db: Session = Depends(get_db),
) -> TenantRead:
    row = tenant_svc.get_tenant(db, tenant_id)
    if row is None:
        raise HTTPException(status_code=404, detail="tenant ikke funnet")
    return TenantRead.model_validate(tenant_svc.update_tenant(db, row, data))


@router.get("/{tenant_id}/members", response_model=list[TenantUserMembershipRead])
def list_tenant_members(tenant_id: int, db: Session = Depends(get_db)) -> list[TenantUserMembershipRead]:
    tenant_access_svc.ensure_tenant_exists(db, tenant_id)
    return [TenantUserMembershipRead.model_validate(r) for r in tenant_access_svc.list_tenant_members(db, tenant_id)]


@router.post("/{tenant_id}/members", response_model=TenantUserMembershipRead)
def add_tenant_member(
    tenant_id: int,
    data: TenantUserMembershipCreate,
    db: Session = Depends(get_db),
) -> TenantUserMembershipRead:
    tenant = tenant_access_svc.ensure_tenant_exists(db, tenant_id)
    row = tenant_access_svc.add_tenant_member(db, tenant, data)
    return TenantUserMembershipRead.model_validate(row)


@router.delete("/{tenant_id}/members/{user_id}", status_code=204, response_model=None)
def remove_tenant_member(tenant_id: int, user_id: int, db: Session = Depends(get_db)) -> None:
    tenant_access_svc.ensure_tenant_exists(db, tenant_id)
    tenant_access_svc.remove_tenant_member(db, tenant_id, user_id)


@router.get("/{tenant_id}/dcim-grants", response_model=list[TenantDcimGrantRead])
def list_tenant_dcim_grants(tenant_id: int, db: Session = Depends(get_db)) -> list[TenantDcimGrantRead]:
    tenant_access_svc.ensure_tenant_exists(db, tenant_id)
    return [TenantDcimGrantRead.model_validate(r) for r in tenant_access_svc.list_tenant_dcim_grants(db, tenant_id)]


@router.post("/{tenant_id}/dcim-grants", response_model=TenantDcimGrantRead)
def add_tenant_dcim_grant(
    tenant_id: int,
    data: TenantDcimGrantCreate,
    db: Session = Depends(get_db),
) -> TenantDcimGrantRead:
    tenant = tenant_access_svc.ensure_tenant_exists(db, tenant_id)
    row = tenant_access_svc.add_tenant_dcim_grant(db, tenant, data)
    return TenantDcimGrantRead.model_validate(row)


@router.delete("/{tenant_id}/dcim-grants/{grant_id}", status_code=204, response_model=None)
def remove_tenant_dcim_grant(tenant_id: int, grant_id: int, db: Session = Depends(get_db)) -> None:
    tenant_access_svc.ensure_tenant_exists(db, tenant_id)
    tenant_access_svc.remove_tenant_dcim_grant(db, tenant_id, grant_id)
