"""Federation API: paring, snapshot, pull og promote."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.federation import (
    FederationAcceptPeerIn,
    FederationAcceptPeerRead,
    FederationConnectIn,
    FederationConsistencyRead,
    FederationFreezeIn,
    FederationHandoffIn,
    FederationHelloRead,
    FederationPairingCreated,
    FederationPeerRead,
    FederationPromoteIn,
    FederationPromoteRead,
    FederationPullIn,
    FederationPullRead,
    FederationSnapshotRead,
    FederationStatusRead,
    FederationTenantRoleRead,
)
from app.services import federation as fed_svc

router = APIRouter(prefix="/federation", tags=["federation"])


@router.get("/hello", response_model=FederationHelloRead)
def federation_hello(db: Session = Depends(get_db)) -> FederationHelloRead:
    return fed_svc.hello(db)


@router.get("/status", response_model=FederationStatusRead)
def federation_status(db: Session = Depends(get_db)) -> FederationStatusRead:
    return fed_svc.status(db)


@router.post("/pairing-tokens", response_model=FederationPairingCreated)
def create_pairing_token(db: Session = Depends(get_db)) -> FederationPairingCreated:
    return fed_svc.create_pairing_token(db)


@router.post("/accept-peer", response_model=FederationAcceptPeerRead)
def accept_peer(data: FederationAcceptPeerIn, db: Session = Depends(get_db)) -> FederationAcceptPeerRead:
    body = fed_svc.accept_peer(db, data)
    return FederationAcceptPeerRead(**body)


@router.post("/connect", response_model=FederationPeerRead)
def connect_to_existing(data: FederationConnectIn, db: Session = Depends(get_db)) -> FederationPeerRead:
    return fed_svc.connect_to_existing(db, data)


@router.post("/peers/{peer_id}/ping", response_model=FederationPeerRead)
def ping_peer(peer_id: int, db: Session = Depends(get_db)) -> FederationPeerRead:
    return fed_svc.ping_peer(db, peer_id)


@router.get("/tenants/{tenant_slug}/snapshot", response_model=FederationSnapshotRead)
def tenant_snapshot(tenant_slug: str, db: Session = Depends(get_db)) -> FederationSnapshotRead:
    return fed_svc.tenant_snapshot(db, tenant_slug)


@router.get("/tenants/{tenant_slug}/consistency", response_model=FederationConsistencyRead)
def tenant_consistency(
    tenant_slug: str,
    peer_id: int | None = None,
    db: Session = Depends(get_db),
) -> FederationConsistencyRead:
    return fed_svc.consistency(db, tenant_slug, peer_id)


@router.post("/tenants/{tenant_slug}/freeze", response_model=FederationTenantRoleRead)
def freeze_tenant(
    tenant_slug: str,
    data: FederationFreezeIn,
    db: Session = Depends(get_db),
) -> FederationTenantRoleRead:
    tenant = fed_svc._tenant_by_slug(db, tenant_slug)
    role = fed_svc.set_frozen(db, tenant, data.frozen)
    local = fed_svc.local_instance(db)
    return FederationTenantRoleRead(
        tenant_id=tenant.id,
        tenant_slug=tenant.slug,
        tenant_name=tenant.name,
        primary_instance_uuid=role.primary_instance_uuid,
        is_primary_here=role.primary_instance_uuid == local.instance_uuid,
        frozen=role.frozen,
        last_pull_at=role.last_pull_at,
    )


@router.post("/tenants/{tenant_slug}/handoff", response_model=FederationTenantRoleRead)
def handoff_tenant(
    tenant_slug: str,
    data: FederationHandoffIn,
    db: Session = Depends(get_db),
) -> FederationTenantRoleRead:
    return fed_svc.handoff(db, tenant_slug, data.primary_instance_uuid)


@router.post("/pull", response_model=FederationPullRead)
def pull_tenant(data: FederationPullIn, db: Session = Depends(get_db)) -> FederationPullRead:
    return fed_svc.pull_tenant(db, data.tenant_slug, data.peer_id)


@router.post("/promote", response_model=FederationPromoteRead)
def promote_tenant(data: FederationPromoteIn, db: Session = Depends(get_db)) -> FederationPromoteRead:
    return fed_svc.promote(db, data.tenant_slug, data.peer_id)
