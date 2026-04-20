"""Tenants API."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.tenant import TenantCreate, TenantRead, TenantUpdate
from app.services import tenant as tenant_svc

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
