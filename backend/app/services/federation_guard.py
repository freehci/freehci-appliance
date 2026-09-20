"""Skrivesteng per tenant. Apply/pull går utenom via apply_mode()."""

from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar
from typing import Iterator

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.dcim import Site
from app.models.federation import FederationPeer, FederationTenantRole

_APPLY: ContextVar[bool] = ContextVar("federation_apply", default=False)


@contextmanager
def apply_mode() -> Iterator[None]:
    token = _APPLY.set(True)
    try:
        yield
    finally:
        _APPLY.reset(token)


def is_apply_mode() -> bool:
    return bool(_APPLY.get())


def has_peers(db: Session) -> bool:
    n = db.execute(select(func.count()).select_from(FederationPeer)).scalar_one()
    return int(n) > 0


def require_tenant_write(db: Session, tenant_id: int | None) -> None:
    if is_apply_mode() or tenant_id is None:
        return
    if not has_peers(db):
        return
    from app.services import federation as fed_svc

    local = fed_svc.local_instance(db)
    role = db.execute(
        select(FederationTenantRole).where(FederationTenantRole.tenant_id == tenant_id),
    ).scalar_one_or_none()
    if role is None:
        fed_svc.upsert_tenant_role(db, tenant_id, local.instance_uuid, frozen=False)
        return
    if role.frozen:
        raise HTTPException(
            status_code=409,
            detail={"code": "tenant_frozen", "detail": "tenant er fryst under primærbytte"},
        )
    if role.primary_instance_uuid != local.instance_uuid:
        peer = db.execute(
            select(FederationPeer).where(FederationPeer.instance_uuid == role.primary_instance_uuid),
        ).scalar_one_or_none()
        raise HTTPException(
            status_code=409,
            detail={
                "code": "tenant_not_primary",
                "detail": "denne instansen er ikke primær for tenanten",
                "primary_url": peer.base_url if peer else None,
                "primary_instance_uuid": role.primary_instance_uuid,
            },
        )


def require_site_write(db: Session, site_id: int | None) -> None:
    if site_id is None:
        return
    site = db.get(Site, site_id)
    if site is None:
        return
    require_tenant_write(db, site.tenant_id)
