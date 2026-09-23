"""Federation: instans-identitet, paring, snapshot, pull og promote."""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import secrets
import socket
import uuid
from typing import Any

import httpx
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.config import get_settings
from app.models.admin_account import AdminAccount
from app.models.catalog import ServiceInstance, ServiceTemplate
from app.models.dcim import Building, DeviceArtifact, DeviceArtifactRecord, DeviceInstance, DeviceModel, DeviceRole, DeviceType, Floor, Manufacturer, Rack, RackPlacement, Room, Site, Wing
from app.models.ipam import IpamIpv4Address
from app.models.platform import PlatformCloudSubscription, PlatformCluster, PlatformVirtualDisk, PlatformVirtualMachine
from app.models.federation import FederationLocal, FederationPairingToken, FederationPeer, FederationTenantRole
from app.models.tenant import Tenant
from app.schemas.federation import (
    FederationAcceptPeerIn,
    FederationConnectIn,
    FederationConsistencyRead,
    FederationHelloRead,
    FederationPairingCreated,
    FederationPeerRead,
    FederationPromoteRead,
    FederationPullRead,
    FederationSnapshotRead,
    FederationStatusRead,
    FederationTenantRoleRead,
)
from app.services import catalog as cat_svc
from app.services import dcim_power as pwr_svc
from app.services import ipam_sync
from app.services import platform as plat_svc
from app.services.auth_admin import create_api_token, ensure_default_admin
from app.services.federation_apply import apply_tenant_document
from app.services.federation_guard import apply_mode

PAIRING_PREFIX = "fhpair_"
_STRIP_KEYS = frozenset(
    {
        "id",
        "created_at",
        "updated_at",
        "etag",
        "vlan_id",
        "vrf_id",
        "ipv4_prefix_id",
        "ipv6_prefix_id",
        "tenant_id",
        "site_id",
        "dual_stack_group_id",
        "a_site_id",
        "z_site_id",
        "cluster_id",
        "vm_id",
        "device_id",
        "device_role_id",
        "storage_pool_id",
        "virtual_interface_id",
        "virtual_disk_id",
        "cloud_subscription_id",
        "template_version_id",
        "template_id",
        "deployment_id",
        "ipv4_address_id",
        "artifact_id",
    },
)


def _now() -> dt.datetime:
    return dt.datetime.now(dt.UTC)


def _aware(value: dt.datetime | None) -> dt.datetime | None:
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=dt.UTC)
    return value


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _strip_local_ids(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {k: _strip_local_ids(v) for k, v in obj.items() if k not in _STRIP_KEYS}
    if isinstance(obj, list):
        return [_strip_local_ids(x) for x in obj]
    return obj


def document_checksum(document: dict[str, Any]) -> str:
    canonical = json.dumps(
        _strip_local_ids(document),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        default=str,
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def local_instance(db: Session) -> FederationLocal:
    row = db.execute(select(FederationLocal).order_by(FederationLocal.id).limit(1)).scalar_one_or_none()
    if row is not None:
        return row
    settings = get_settings()
    configured = (getattr(settings, "federation_instance_uuid", None) or "").strip()
    try:
        inst = str(uuid.UUID(configured)) if configured else str(uuid.uuid4())
    except ValueError:
        inst = str(uuid.uuid4())
    name = (getattr(settings, "federation_instance_name", None) or "").strip() or socket.gethostname()[:128] or "appliance"
    row = FederationLocal(instance_uuid=inst, name=name[:128])
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def ensure_local_instance(db: Session) -> FederationLocal | None:
    try:
        return local_instance(db)
    except Exception:
        db.rollback()
        return None


def upsert_tenant_role(db: Session, tenant_id: int, primary_instance_uuid: str, *, frozen: bool | None = None) -> FederationTenantRole:
    role = db.execute(
        select(FederationTenantRole).where(FederationTenantRole.tenant_id == tenant_id),
    ).scalar_one_or_none()
    if role is None:
        role = FederationTenantRole(
            tenant_id=tenant_id,
            primary_instance_uuid=primary_instance_uuid,
            frozen=bool(frozen) if frozen is not None else False,
        )
        db.add(role)
    else:
        role.primary_instance_uuid = primary_instance_uuid
        if frozen is not None:
            role.frozen = frozen
        role.updated_at = _now()
    db.commit()
    db.refresh(role)
    return role


def assign_local_primary(db: Session, tenant_id: int) -> None:
    from app.services.federation_guard import is_apply_mode

    if is_apply_mode():
        return
    try:
        local = local_instance(db)
    except Exception:
        db.rollback()
        return
    existing = db.execute(
        select(FederationTenantRole).where(FederationTenantRole.tenant_id == tenant_id),
    ).scalar_one_or_none()
    if existing is not None:
        return
    upsert_tenant_role(db, tenant_id, local.instance_uuid, frozen=False)


def hello(db: Session) -> FederationHelloRead:
    local = local_instance(db)
    return FederationHelloRead(instance_uuid=local.instance_uuid, name=local.name)


def create_pairing_token(db: Session, *, ttl_minutes: int = 60) -> FederationPairingCreated:
    local = local_instance(db)
    raw = f"{PAIRING_PREFIX}{secrets.token_urlsafe(24)}"
    expires = _now() + dt.timedelta(minutes=ttl_minutes)
    db.add(
        FederationPairingToken(
            token_hash=_hash_token(raw),
            token_prefix=raw[:16],
            expires_at=expires,
        ),
    )
    db.commit()
    return FederationPairingCreated(
        token=raw,
        instance_uuid=local.instance_uuid,
        name=local.name,
        expires_at=expires,
    )


def _issue_peer_api_token(db: Session, peer_uuid: str) -> str:
    admin = db.execute(select(AdminAccount).order_by(AdminAccount.id)).scalars().first()
    if admin is None:
        ensure_default_admin(db)
        admin = db.execute(select(AdminAccount).order_by(AdminAccount.id)).scalars().first()
    if admin is None:
        raise HTTPException(status_code=500, detail="ingen admin-konto for federation-nøkkel")
    created = create_api_token(db, admin, f"federation:{peer_uuid[:8]}", scopes=["federation"])
    return created.token


def upsert_peer(
    db: Session,
    *,
    instance_uuid: str,
    name: str,
    base_url: str,
    outbound_token: str | None = None,
    status: str = "active",
) -> FederationPeer:
    row = db.execute(select(FederationPeer).where(FederationPeer.instance_uuid == instance_uuid)).scalar_one_or_none()
    if row is None:
        row = FederationPeer(
            instance_uuid=instance_uuid,
            name=name[:128],
            base_url=base_url.rstrip("/"),
            outbound_token=outbound_token,
            status=status,
            last_seen_at=_now(),
        )
        db.add(row)
    else:
        row.name = name[:128]
        row.base_url = base_url.rstrip("/")
        if outbound_token:
            row.outbound_token = outbound_token
        row.status = status
        row.last_seen_at = _now()
    db.commit()
    db.refresh(row)
    return row


def _seed_local_primary_roles(db: Session) -> None:
    local = local_instance(db)
    tenants = list(db.execute(select(Tenant)).scalars().all())
    for t in tenants:
        existing = db.execute(
            select(FederationTenantRole).where(FederationTenantRole.tenant_id == t.id),
        ).scalar_one_or_none()
        if existing is None:
            db.add(
                FederationTenantRole(
                    tenant_id=t.id,
                    primary_instance_uuid=local.instance_uuid,
                    frozen=False,
                ),
            )
    db.commit()


def accept_peer(db: Session, data: FederationAcceptPeerIn) -> dict[str, str]:
    digest = _hash_token(data.pairing_token.strip())
    row = db.execute(select(FederationPairingToken).where(FederationPairingToken.token_hash == digest)).scalar_one_or_none()
    if row is None:
        raise HTTPException(status_code=401, detail={"code": "pairing_invalid", "detail": "ugyldig paringsnøkkel"})
    if row.consumed_at is not None:
        raise HTTPException(status_code=409, detail={"code": "pairing_used", "detail": "paringsnøkkel er allerede brukt"})
    if _aware(row.expires_at) is not None and _aware(row.expires_at) < _now():  # type: ignore[operator]
        raise HTTPException(status_code=401, detail={"code": "pairing_expired", "detail": "paringsnøkkel er utløpt"})
    local = local_instance(db)
    if data.instance_uuid == local.instance_uuid:
        raise HTTPException(status_code=400, detail={"code": "self_peer", "detail": "kan ikke pare med seg selv"})
    row.consumed_at = _now()
    db.commit()
    upsert_peer(db, instance_uuid=data.instance_uuid, name=data.name, base_url=data.base_url)
    _seed_local_primary_roles(db)
    token = _issue_peer_api_token(db, data.instance_uuid)
    return {"instance_uuid": local.instance_uuid, "name": local.name, "token": token}


def connect_to_existing(db: Session, data: FederationConnectIn) -> FederationPeerRead:
    local = local_instance(db)
    url = data.base_url.rstrip("/") + "/api/v1/federation/accept-peer"
    advertised = (data.advertised_base_url or "").strip() or data.base_url
    try:
        with httpx.Client(timeout=20.0, follow_redirects=True) as client:
            resp = client.post(
                url,
                json={
                    "pairing_token": data.pairing_token.strip(),
                    "instance_uuid": local.instance_uuid,
                    "name": local.name,
                    "base_url": advertised.rstrip("/"),
                },
            )
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=502,
            detail={"code": "peer_unreachable", "detail": str(exc)},
        ) from exc
    if resp.status_code >= 400:
        detail: Any
        try:
            detail = resp.json()
        except Exception:
            detail = resp.text[:400]
        raise HTTPException(status_code=502, detail={"code": "peer_error", "detail": detail, "status": resp.status_code})
    body = resp.json()
    peer = upsert_peer(
        db,
        instance_uuid=body["instance_uuid"],
        name=body.get("name") or "peer",
        base_url=data.base_url,
        outbound_token=body.get("token"),
    )
    return _peer_read(peer)


def _peer_read(row: FederationPeer) -> FederationPeerRead:
    return FederationPeerRead(
        id=row.id,
        instance_uuid=row.instance_uuid,
        name=row.name,
        base_url=row.base_url,
        status=row.status,
        last_seen_at=row.last_seen_at,
    )


def list_peers(db: Session) -> list[FederationPeer]:
    return list(db.execute(select(FederationPeer).order_by(FederationPeer.id)).scalars().all())


def get_peer(db: Session, peer_id: int) -> FederationPeer | None:
    return db.get(FederationPeer, peer_id)


def resolve_peer(db: Session, peer_id: int | None) -> FederationPeer:
    if peer_id is not None:
        peer = get_peer(db, peer_id)
        if peer is None:
            raise HTTPException(status_code=404, detail={"code": "peer_not_found", "detail": "peer ikke funnet"})
        return peer
    peers = list_peers(db)
    if len(peers) != 1:
        raise HTTPException(status_code=400, detail={"code": "peer_required", "detail": "peer_id kreves når det finnes flere peers"})
    return peers[0]


def ping_peer(db: Session, peer_id: int) -> FederationPeerRead:
    peer = get_peer(db, peer_id)
    if peer is None:
        raise HTTPException(status_code=404, detail="peer ikke funnet")
    url = peer.base_url.rstrip("/") + "/api/v1/federation/hello"
    try:
        with httpx.Client(timeout=8.0, follow_redirects=True) as client:
            resp = client.get(url)
        body = resp.json()
        if resp.status_code >= 400:
            peer.status = "unreachable"
        elif body.get("instance_uuid") == peer.instance_uuid:
            peer.status = "active"
            peer.last_seen_at = _now()
        else:
            peer.status = "mismatch"
    except (httpx.RequestError, ValueError):
        peer.status = "unreachable"
    db.commit()
    db.refresh(peer)
    return _peer_read(peer)


def _tenant_by_slug(db: Session, slug: str) -> Tenant:
    row = db.execute(select(Tenant).where(Tenant.slug == slug.strip().lower())).scalar_one_or_none()
    if row is None:
        raise HTTPException(status_code=404, detail={"code": "tenant_not_found", "detail": "tenant ikke funnet"})
    return row


def set_frozen(db: Session, tenant: Tenant, frozen: bool) -> FederationTenantRole:
    local = local_instance(db)
    role = db.execute(
        select(FederationTenantRole).where(FederationTenantRole.tenant_id == tenant.id),
    ).scalar_one_or_none()
    if role is None:
        role = upsert_tenant_role(db, tenant.id, local.instance_uuid, frozen=frozen)
    else:
        role.frozen = frozen
        role.updated_at = _now()
        db.commit()
        db.refresh(role)
    return role


def _ipam_for_site(db: Session, site: Site) -> dict[str, Any]:
    raw = ipam_sync.export_site(db, site.id)
    addresses = []
    for a in raw.get("addresses") or []:
        addresses.append(
            {
                "address": a["address"],
                "status": a.get("status"),
                "role": a.get("role"),
                "note": a.get("note"),
                "prefix_cidr": a.get("prefix_cidr"),
                "site_slug": site.slug,
                "virtual_interface_slug": a.get("virtual_interface_slug"),
            },
        )
    v6_addrs = []
    for a in raw.get("ipv6_addresses") or []:
        v6_addrs.append(
            {
                "address": a["address"],
                "status": a.get("status"),
                "role": a.get("role"),
                "prefix_cidr": a.get("prefix_cidr"),
                "site_slug": site.slug,
            },
        )
    return {
        "site": {"slug": site.slug, "name": site.name},
        "vrfs": [{"name": v["name"], "slug": v["slug"]} for v in raw.get("vrfs") or []],
        "vlan_groups": [{"name": g["name"], "slug": g["slug"]} for g in raw.get("vlan_groups") or []],
        "vlans": [
            {
                "vid": v["vid"],
                "name": v["name"],
                "slug": v["slug"],
                "vlan_group_slug": v.get("vlan_group_slug"),
            }
            for v in raw.get("vlans") or []
        ],
        "prefixes": [
            {
                "cidr": p["cidr"],
                "slug": p.get("slug"),
                "name": p.get("name"),
                "role": p.get("role"),
                "status": p.get("status"),
                "site_slug": site.slug,
                "vlan_slug": p.get("vlan_slug"),
                "vrf_slug": p.get("vrf_slug"),
                "overlap_policy": p.get("overlap_policy"),
            }
            for p in raw.get("prefixes") or []
        ],
        "addresses": addresses,
        "ipv6_prefixes": [
            {"cidr": p["cidr"], "slug": p.get("slug"), "role": p.get("role"), "status": p.get("status")}
            for p in raw.get("ipv6_prefixes") or []
        ],
        "ipv6_addresses": v6_addrs,
        "providers": [{"name": p.get("name"), "slug": p.get("slug")} for p in raw.get("providers") or [] if p.get("slug")],
        "circuit_groups": [
            {
                "name": g.get("name"),
                "slug": g.get("slug"),
                "shared_risk": g.get("shared_risk"),
                "description": g.get("description"),
            }
            for g in raw.get("circuit_groups") or []
            if g.get("slug")
        ],
        "contracts": [
            {
                "name": c.get("name"),
                "slug": c.get("slug"),
                "provider_slug": c.get("provider_slug"),
                "account_slug": c.get("account_slug"),
                "reference": c.get("reference"),
                "starts_on": c.get("starts_on"),
                "ends_on": c.get("ends_on"),
                "description": c.get("description"),
            }
            for c in raw.get("contracts") or []
            if c.get("slug") and c.get("provider_slug")
        ],
        "circuits": [
            {
                "circuit_number": c["circuit_number"],
                "name": c.get("name"),
                "circuit_type": c.get("circuit_type"),
                "layer": c.get("layer"),
                "a_site_slug": c.get("a_site_slug"),
                "z_site_slug": c.get("z_site_slug"),
                "provider_slug": c.get("provider_slug"),
                "provider_name": c.get("provider_name"),
                "contract_slug": c.get("contract_slug"),
                "group_slug": c.get("group_slug"),
            }
            for c in raw.get("circuits") or []
            if c.get("circuit_number")
        ],
        "vpn_services": [
            {
                "name": v.get("name"),
                "slug": v.get("slug"),
                "vpn_type": v.get("vpn_type"),
                "source_circuit_number": v.get("source_circuit_number"),
            }
            for v in raw.get("vpn_services") or []
            if v.get("slug")
        ],
        "autonomous_systems": [
            {"asn": a.get("asn"), "name": a.get("name"), "slug": a.get("slug"), "is_private": a.get("is_private")}
            for a in raw.get("autonomous_systems") or []
            if a.get("asn")
        ],
        "as_assignments": [
            {"asn": x.get("asn"), "site_slug": x.get("site_slug"), "vrf_slug": x.get("vrf_slug")}
            for x in raw.get("as_assignments") or []
            if x.get("asn")
        ],
        "bgp_sessions": [
            {
                "name": s.get("name"),
                "slug": s.get("slug"),
                "local_asn": s.get("local_asn"),
                "remote_asn": s.get("remote_asn"),
                "peer_ip": s.get("peer_ip"),
                "site_slug": s.get("site_slug"),
                "vrf_slug": s.get("vrf_slug"),
                "address_families": s.get("address_families"),
                "desired_status": s.get("desired_status"),
            }
            for s in raw.get("bgp_sessions") or []
            if s.get("peer_ip") and s.get("local_asn")
        ],
        "route_targets": [
            {"name": r.get("name"), "slug": r.get("slug"), "value": r.get("value"), "description": r.get("description")}
            for r in raw.get("route_targets") or []
            if r.get("slug") and r.get("value")
        ],
        "vrf_route_targets": [
            {
                "vrf_slug": r.get("vrf_slug"),
                "route_target_slug": r.get("route_target_slug"),
                "direction": r.get("direction"),
            }
            for r in raw.get("vrf_route_targets") or []
            if r.get("vrf_slug") and r.get("route_target_slug") and r.get("direction")
        ],
        "vrf_instances": [
            {
                "vrf_slug": r.get("vrf_slug"),
                "site_slug": site.slug,
                "device_name": r.get("device_name"),
                "slug": r.get("slug"),
                "intent": r.get("intent"),
                "route_distinguisher": r.get("route_distinguisher"),
                "description": r.get("description"),
            }
            for r in raw.get("vrf_instances") or []
            if r.get("vrf_slug") and r.get("device_name")
        ],
        "ipv4_ranges": [
            {
                "prefix_cidr": r.get("prefix_cidr"),
                "site_slug": site.slug,
                "slug": r.get("slug"),
                "name": r.get("name"),
                "kind": r.get("kind"),
                "start_address": r.get("start_address"),
                "end_address": r.get("end_address"),
                "description": r.get("description"),
            }
            for r in raw.get("ipv4_ranges") or []
            if r.get("slug") and r.get("start_address") and r.get("end_address")
        ],
    }


def export_tenant_document(db: Session, tenant: Tenant) -> dict[str, Any]:
    sites = list(
        db.execute(
            select(Site)
            .where(Site.tenant_id == tenant.id)
            .options(
                selectinload(Site.rooms).selectinload(Room.racks),
                selectinload(Site.buildings).selectinload(Building.wings),
                selectinload(Site.buildings).selectinload(Building.floors),
            ),
        ).scalars().all(),
    )
    site_ids = [s.id for s in sites]
    buildings = [b for s in sites for b in s.buildings]
    wings = [w for b in buildings for w in b.wings]
    floors = [f for b in buildings for f in b.floors]
    rooms = [r for s in sites for r in s.rooms]
    racks = [k for r in rooms for k in r.racks]
    devices = []
    if site_ids:
        devices = list(
            db.execute(select(DeviceInstance).where(DeviceInstance.site_id.in_(site_ids))).scalars().all(),
        )
    rack_ids = [k.id for k in racks]
    placements = []
    if rack_ids:
        placements = list(
            db.execute(select(RackPlacement).where(RackPlacement.rack_id.in_(rack_ids))).scalars().all(),
        )
    model_ids = {d.device_model_id for d in devices if d.device_model_id}
    models = list(db.execute(select(DeviceModel).where(DeviceModel.id.in_(model_ids))).scalars().all()) if model_ids else []
    mfr_ids = {m.manufacturer_id for m in models if m.manufacturer_id}
    type_ids = {m.device_type_id for m in models if m.device_type_id}
    manufacturers = list(db.execute(select(Manufacturer).where(Manufacturer.id.in_(mfr_ids))).scalars().all()) if mfr_ids else []
    types = list(db.execute(select(DeviceType).where(DeviceType.id.in_(type_ids))).scalars().all()) if type_ids else []
    mfr_by_id = {m.id: m for m in manufacturers}
    type_by_id = {t.id: t for t in types}
    model_by_id = {m.id: m for m in models}
    site_by_id = {s.id: s for s in sites}
    building_by_id = {b.id: b for b in buildings}
    wing_by_id = {w.id: w for w in wings}
    floor_by_id = {f.id: f for f in floors}
    room_by_id = {r.id: r for r in rooms}
    rack_by_id = {k.id: k for k in racks}
    device_by_id = {d.id: d for d in devices}
    role_ids = {d.device_role_id for d in devices if getattr(d, "device_role_id", None)}
    roles = list(db.execute(select(DeviceRole).where(DeviceRole.id.in_(role_ids))).scalars().all()) if role_ids else []
    role_by_id = {r.id: r for r in roles}

    return {
        "apiVersion": "freehci.inventory/v1",
        "kind": "TenantInventory",
        "tenant": {"slug": tenant.slug, "name": tenant.name, "description": tenant.description},
        "sites": [
            {
                "slug": s.slug,
                "name": s.name,
                "description": s.description,
                "city": s.city,
                "country": s.country,
                "address_line1": s.address_line1,
                "postal_code": s.postal_code,
            }
            for s in sites
        ],
        "buildings": [
            {
                "site_slug": site_by_id[b.site_id].slug,
                "slug": b.slug,
                "name": b.name,
                "description": b.description,
            }
            for b in buildings
        ],
        "wings": [
            {
                "site_slug": site_by_id[building_by_id[w.building_id].site_id].slug,
                "building_slug": building_by_id[w.building_id].slug,
                "slug": w.slug,
                "name": w.name,
                "description": w.description,
            }
            for w in wings
        ],
        "floors": [
            {
                "site_slug": site_by_id[building_by_id[f.building_id].site_id].slug,
                "building_slug": building_by_id[f.building_id].slug,
                "wing_slug": wing_by_id[f.wing_id].slug if f.wing_id and f.wing_id in wing_by_id else None,
                "slug": f.slug,
                "name": f.name,
                "level": f.level,
                "description": f.description,
            }
            for f in floors
        ],
        "rooms": [
            {
                "site_slug": site_by_id[r.site_id].slug,
                "name": r.name,
                "description": r.description,
                "floor": floor_by_id[r.floor_id].name if r.floor_id and r.floor_id in floor_by_id else r.floor,
                "building_slug": building_by_id[r.building_id].slug if r.building_id and r.building_id in building_by_id else None,
                "wing_slug": wing_by_id[r.wing_id].slug if r.wing_id and r.wing_id in wing_by_id else None,
                "floor_slug": floor_by_id[r.floor_id].slug if r.floor_id and r.floor_id in floor_by_id else None,
            }
            for r in rooms
        ],
        "racks": [
            {
                "site_slug": site_by_id[room_by_id[k.room_id].site_id].slug,
                "room_name": room_by_id[k.room_id].name,
                "name": k.name,
                "u_height": k.u_height,
                "mounting": k.mounting,
                "elevation_mm": k.elevation_mm,
            }
            for k in racks
        ],
        "manufacturers": [{"name": m.name, "description": m.description, "website_url": m.website_url} for m in manufacturers],
        "device_types": [{"slug": t.slug, "name": t.name} for t in types],
        "device_models": [
            {
                "name": m.name,
                "u_height": m.u_height,
                "manufacturer_name": mfr_by_id[m.manufacturer_id].name if m.manufacturer_id and m.manufacturer_id in mfr_by_id else None,
                "device_type_slug": type_by_id[m.device_type_id].slug if m.device_type_id and m.device_type_id in type_by_id else None,
            }
            for m in models
        ],
        "devices": [
            {
                "name": d.name,
                "site_slug": site_by_id[d.site_id].slug if d.site_id and d.site_id in site_by_id else None,
                "serial_number": d.serial_number,
                "asset_tag": d.asset_tag,
                "model_name": model_by_id[d.device_model_id].name if d.device_model_id and d.device_model_id in model_by_id else None,
                "manufacturer_name": (
                    mfr_by_id[model_by_id[d.device_model_id].manufacturer_id].name
                    if d.device_model_id
                    and d.device_model_id in model_by_id
                    and model_by_id[d.device_model_id].manufacturer_id
                    and model_by_id[d.device_model_id].manufacturer_id in mfr_by_id
                    else None
                ),
                "device_role_slug": (
                    role_by_id[d.device_role_id].slug
                    if getattr(d, "device_role_id", None) and d.device_role_id in role_by_id
                    else None
                ),
            }
            for d in devices
        ],
        "placements": [
            {
                "site_slug": site_by_id[room_by_id[rack_by_id[p.rack_id].room_id].site_id].slug,
                "room_name": room_by_id[rack_by_id[p.rack_id].room_id].name,
                "rack_name": rack_by_id[p.rack_id].name,
                "device_name": device_by_id[p.device_id].name if p.device_id in device_by_id else None,
                "u_position": p.u_position,
                "mounting": p.mounting,
            }
            for p in placements
            if p.rack_id in rack_by_id and p.device_id in device_by_id
        ],
        "ipam": [_ipam_for_site(db, s) for s in sites],
        "device_roles": [
            {"slug": r.slug, "name": r.name, "kind": r.kind, "description": r.description} for r in roles
        ],
        **_export_device_artifacts(db, devices=devices, site_by_id=site_by_id, device_by_id=device_by_id),
        **_export_platform_catalog(db, sites=sites, devices=devices, site_by_id=site_by_id, device_by_id=device_by_id),
        **pwr_svc.export_for_sites(db, sites),
    }


def _export_device_artifacts(
    db: Session,
    *,
    devices: list[DeviceInstance],
    site_by_id: dict[int, Site],
    device_by_id: dict[int, DeviceInstance],
) -> dict[str, Any]:
    device_ids = {d.id for d in devices}
    records = (
        list(
            db.execute(select(DeviceArtifactRecord).where(DeviceArtifactRecord.device_id.in_(device_ids))).scalars().all()
        )
        if device_ids
        else []
    )
    inst_art = (
        list(
            db.execute(
                select(ServiceInstance.artifact_id).where(
                    ServiceInstance.device_id.in_(device_ids),
                    ServiceInstance.artifact_id.is_not(None),
                )
            ).scalars().all()
        )
        if device_ids
        else []
    )
    art_ids = {r.artifact_id for r in records} | {i for i in inst_art if i}
    artifacts = (
        list(db.execute(select(DeviceArtifact).where(DeviceArtifact.id.in_(art_ids))).scalars().all()) if art_ids else []
    )
    art_by_id = {a.id: a for a in artifacts}
    return {
        "device_artifacts": [
            {
                "slug": a.slug,
                "name": a.name,
                "kind": a.kind,
                "version": a.version,
                "description": a.description,
            }
            for a in artifacts
        ],
        "device_artifact_records": [
            {
                "device_name": device_by_id[r.device_id].name if r.device_id in device_by_id else None,
                "site_slug": (
                    site_by_id[device_by_id[r.device_id].site_id].slug
                    if r.device_id in device_by_id
                    and device_by_id[r.device_id].site_id
                    and device_by_id[r.device_id].site_id in site_by_id
                    else None
                ),
                "artifact_slug": art_by_id[r.artifact_id].slug if r.artifact_id in art_by_id else None,
                "intent": r.intent,
            }
            for r in records
            if r.device_id in device_by_id and r.artifact_id in art_by_id
        ],
    }


def _export_platform_catalog(
    db: Session,
    *,
    sites: list[Site],
    devices: list[DeviceInstance],
    site_by_id: dict[int, Site],
    device_by_id: dict[int, DeviceInstance],
) -> dict[str, Any]:
    site_ids = {s.id for s in sites}
    device_ids = {d.id for d in devices}
    clusters: list[PlatformCluster] = []
    for cluster in plat_svc.list_clusters(db):
        if cluster.site_id and int(cluster.site_id) in site_ids:
            clusters.append(cluster)
            continue
        if any(m.device_id in device_ids for m in cluster.members):
            clusters.append(cluster)
    cluster_ids = {c.id for c in clusters}
    cluster_by_id = {c.id: c for c in clusters}

    vm_by_id: dict[int, PlatformVirtualMachine] = {}
    pool_by_id: dict[int, Any] = {}
    vif_by_id: dict[int, Any] = {}
    disk_by_id: dict[int, PlatformVirtualDisk] = {}
    for cluster in clusters:
        for pool in cluster.storage_pools:
            pool_by_id[pool.id] = pool
        for vm in cluster.vms:
            vm_by_id[vm.id] = vm
            for iface in vm.interfaces:
                vif_by_id[iface.id] = iface
            for disk in vm.disks:
                disk_by_id[disk.id] = disk

    instances: list[ServiceInstance] = []
    for inst in cat_svc.list_instances(db):
        if inst.device_id and inst.device_id in device_ids:
            instances.append(inst)
            continue
        if inst.cluster_id and inst.cluster_id in cluster_ids:
            instances.append(inst)
            continue
        if inst.vm_id and inst.vm_id in vm_by_id:
            instances.append(inst)
            continue
        if inst.virtual_interface_id and inst.virtual_interface_id in vif_by_id:
            instances.append(inst)
            continue
        if inst.virtual_disk_id and inst.virtual_disk_id in disk_by_id:
            instances.append(inst)
            continue
        if inst.storage_pool_id and inst.storage_pool_id in pool_by_id:
            instances.append(inst)

    version_ids = {i.template_version_id for i in instances}
    templates: list[ServiceTemplate] = []
    seen_tpl: set[int] = set()
    for tpl in cat_svc.list_templates(db):
        if any(v.id in version_ids for v in tpl.versions) and tpl.id not in seen_tpl:
            templates.append(tpl)
            seen_tpl.add(tpl.id)

    cloud_ids = {i.cloud_subscription_id for i in instances if i.cloud_subscription_id}
    clouds = (
        list(db.execute(select(PlatformCloudSubscription).where(PlatformCloudSubscription.id.in_(cloud_ids))).scalars().all())
        if cloud_ids
        else []
    )
    cloud_by_id = {c.id: c for c in clouds}
    addr_ids = {i.ipv4_address_id for i in instances if i.ipv4_address_id}
    addr_by_id = (
        {a.id: a for a in db.execute(select(IpamIpv4Address).where(IpamIpv4Address.id.in_(addr_ids))).scalars().all()}
        if addr_ids
        else {}
    )

    def _device_ref(device_id: int | None) -> tuple[str | None, str | None]:
        if not device_id or device_id not in device_by_id:
            return None, None
        device = device_by_id[device_id]
        site_slug = site_by_id[device.site_id].slug if device.site_id and device.site_id in site_by_id else None
        return device.name, site_slug

    cluster_docs = []
    for cluster in clusters:
        members = []
        for member in cluster.members:
            name, site_slug = _device_ref(member.device_id)
            if not name:
                continue
            members.append({"device_name": name, "site_slug": site_slug, "role": member.role})
        vms = []
        for vm in cluster.vms:
            dname, dsite = _device_ref(vm.device_id)
            vms.append(
                {
                    "slug": vm.slug,
                    "name": vm.name,
                    "status": vm.status,
                    "device_name": dname,
                    "site_slug": dsite,
                    "interfaces": [{"slug": i.slug, "name": i.name, "status": i.status} for i in vm.interfaces],
                    "disks": [
                        {
                            "slug": d.slug,
                            "name": d.name,
                            "kind": d.kind,
                            "status": d.status,
                            "storage_pool_slug": pool_by_id[d.storage_pool_id].slug if d.storage_pool_id in pool_by_id else None,
                        }
                        for d in vm.disks
                    ],
                }
            )
        cluster_docs.append(
            {
                "slug": cluster.slug,
                "name": cluster.name,
                "kind": cluster.kind,
                "description": cluster.description,
                "site_slug": site_by_id[cluster.site_id].slug if cluster.site_id and cluster.site_id in site_by_id else None,
                "members": members,
                "storage_pools": [
                    {"slug": p.slug, "name": p.name, "kind": p.kind, "status": p.status} for p in cluster.storage_pools
                ],
                "vms": vms,
            }
        )

    instance_docs = []
    tpl_by_version: dict[int, tuple[ServiceTemplate, Any]] = {}
    for tpl in templates:
        for ver in tpl.versions:
            tpl_by_version[ver.id] = (tpl, ver)
    for inst in instances:
        pair = tpl_by_version.get(inst.template_version_id)
        dname, dsite = _device_ref(inst.device_id)
        cluster = cluster_by_id.get(inst.cluster_id) if inst.cluster_id else None
        vm = vm_by_id.get(inst.vm_id) if inst.vm_id else None
        iface = vif_by_id.get(inst.virtual_interface_id) if inst.virtual_interface_id else None
        disk = disk_by_id.get(inst.virtual_disk_id) if inst.virtual_disk_id else None
        pool = pool_by_id.get(inst.storage_pool_id) if inst.storage_pool_id else None
        cloud = cloud_by_id.get(inst.cloud_subscription_id) if inst.cloud_subscription_id else None
        addr = addr_by_id.get(inst.ipv4_address_id) if inst.ipv4_address_id else None
        art_row = db.get(DeviceArtifact, inst.artifact_id) if inst.artifact_id else None
        instance_docs.append(
            {
                "slug": inst.slug,
                "name": inst.name,
                "status": inst.status,
                "template_slug": pair[0].slug if pair else None,
                "template_version": pair[1].version if pair else None,
                "device_name": dname,
                "site_slug": dsite,
                "cluster_slug": cluster.slug if cluster else None,
                "vm_slug": vm.slug if vm else None,
                "storage_pool_slug": pool.slug if pool else None,
                "virtual_interface_slug": iface.slug if iface else None,
                "virtual_disk_slug": disk.slug if disk else None,
                "cloud_subscription_slug": cloud.slug if cloud else None,
                "artifact_slug": art_row.slug if art_row is not None else None,
                "ipv4_address": addr.address if addr else None,
            }
        )

    return {
        "clusters": cluster_docs,
        "cloud_subscriptions": [
            {
                "slug": c.slug,
                "name": c.name,
                "kind": c.kind,
                "status": c.status,
                "description": c.description,
            }
            for c in clouds
        ],
        "catalog_templates": [
            {
                "slug": t.slug,
                "name": t.name,
                "description": t.description,
                "versions": [{"version": v.version, "spec": v.spec if isinstance(v.spec, dict) else {}} for v in t.versions],
            }
            for t in templates
        ],
        "catalog_instances": instance_docs,
    }


def tenant_snapshot(db: Session, tenant_slug: str) -> FederationSnapshotRead:
    tenant = _tenant_by_slug(db, tenant_slug)
    document = export_tenant_document(db, tenant)
    return FederationSnapshotRead(
        apiVersion="freehci.inventory/v1",
        kind="TenantInventory",
        checksum=document_checksum(document),
        document=document,
    )


def status(db: Session) -> FederationStatusRead:
    local = local_instance(db)
    tenants = list(db.execute(select(Tenant).order_by(Tenant.name)).scalars().all())
    roles = {
        r.tenant_id: r
        for r in db.execute(select(FederationTenantRole)).scalars().all()
    }
    return FederationStatusRead(
        instance_uuid=local.instance_uuid,
        name=local.name,
        peers=[_peer_read(p) for p in list_peers(db)],
        tenants=[
            FederationTenantRoleRead(
                tenant_id=t.id,
                tenant_slug=t.slug,
                tenant_name=t.name,
                primary_instance_uuid=(roles[t.id].primary_instance_uuid if t.id in roles else local.instance_uuid),
                is_primary_here=(
                    (roles[t.id].primary_instance_uuid if t.id in roles else local.instance_uuid) == local.instance_uuid
                ),
                frozen=bool(roles[t.id].frozen) if t.id in roles else False,
                last_pull_at=roles[t.id].last_pull_at if t.id in roles else None,
            )
            for t in tenants
        ],
    )


def _peer_request(peer: FederationPeer, method: str, path: str, json_body: dict[str, Any] | None = None) -> Any:
    if not peer.outbound_token:
        raise HTTPException(status_code=409, detail={"code": "peer_token_missing", "detail": "peer mangler utgående nøkkel"})
    url = peer.base_url.rstrip("/") + "/api/v1/federation" + path
    try:
        with httpx.Client(timeout=30.0, follow_redirects=True) as client:
            resp = client.request(
                method,
                url,
                json=json_body,
                headers={"Authorization": f"Bearer {peer.outbound_token}"},
            )
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=502,
            detail={"code": "peer_unreachable", "detail": str(exc)},
        ) from exc
    if resp.status_code >= 400:
        try:
            detail = resp.json()
        except Exception:
            detail = resp.text[:400]
        raise HTTPException(
            status_code=502,
            detail={"code": "peer_error", "detail": detail, "status": resp.status_code},
        )
    if not resp.content:
        return {}
    return resp.json()


def pull_tenant(db: Session, tenant_slug: str, peer_id: int | None = None) -> FederationPullRead:
    peer = resolve_peer(db, peer_id)
    snap = _peer_request(peer, "GET", f"/tenants/{tenant_slug}/snapshot")
    document = snap.get("document") or snap
    with apply_mode():
        apply_tenant_document(db, document)
    tenant = _tenant_by_slug(db, tenant_slug)
    role = upsert_tenant_role(db, tenant.id, peer.instance_uuid, frozen=False)
    role.last_pull_at = _now()
    db.commit()
    checksum = snap.get("checksum") or document_checksum(document)
    return FederationPullRead(
        tenant_slug=tenant.slug,
        checksum=checksum,
        applied=True,
        primary_instance_uuid=peer.instance_uuid,
    )


def apply_document_locally(db: Session, document: dict[str, Any], *, primary_instance_uuid: str | None = None) -> str:
    with apply_mode():
        apply_tenant_document(db, document)
    slug = str((document.get("tenant") or {}).get("slug") or "")
    tenant = _tenant_by_slug(db, slug)
    if primary_instance_uuid:
        upsert_tenant_role(db, tenant.id, primary_instance_uuid, frozen=False)
    return document_checksum(export_tenant_document(db, tenant))


def consistency(db: Session, tenant_slug: str, peer_id: int | None = None) -> FederationConsistencyRead:
    tenant = _tenant_by_slug(db, tenant_slug)
    local = local_instance(db)
    document = export_tenant_document(db, tenant)
    local_sum = document_checksum(document)
    role = db.execute(
        select(FederationTenantRole).where(FederationTenantRole.tenant_id == tenant.id),
    ).scalar_one_or_none()
    frozen = bool(role.frozen) if role else False
    is_primary = (role.primary_instance_uuid if role else local.instance_uuid) == local.instance_uuid
    if peer_id is None:
        return FederationConsistencyRead(
            tenant_slug=tenant.slug,
            checksum=local_sum,
            peer_checksum=None,
            match=None,
            frozen=frozen,
            is_primary_here=is_primary,
        )
    peer = resolve_peer(db, peer_id)
    remote = _peer_request(peer, "GET", f"/tenants/{tenant.slug}/consistency")
    peer_sum = remote.get("checksum")
    return FederationConsistencyRead(
        tenant_slug=tenant.slug,
        checksum=local_sum,
        peer_checksum=peer_sum,
        match=bool(peer_sum == local_sum) if peer_sum else None,
        frozen=frozen,
        is_primary_here=is_primary,
    )


def promote_if_match(
    db: Session,
    tenant: Tenant,
    *,
    remote_checksum: str,
    remote_frozen: bool,
) -> FederationPromoteRead:
    local = local_instance(db)
    if not remote_frozen:
        raise HTTPException(
            status_code=409,
            detail={"code": "peer_not_frozen", "detail": "peer må være fryst før promote"},
        )
    set_frozen(db, tenant, True)
    local_sum = document_checksum(export_tenant_document(db, tenant))
    if local_sum != remote_checksum:
        return FederationPromoteRead(
            tenant_slug=tenant.slug,
            primary_instance_uuid=(
                db.execute(select(FederationTenantRole).where(FederationTenantRole.tenant_id == tenant.id)).scalar_one().primary_instance_uuid
                if db.execute(select(FederationTenantRole).where(FederationTenantRole.tenant_id == tenant.id)).scalar_one_or_none()
                else local.instance_uuid
            ),
            checksum=local_sum,
            match=False,
        )
    upsert_tenant_role(db, tenant.id, local.instance_uuid, frozen=False)
    return FederationPromoteRead(
        tenant_slug=tenant.slug,
        primary_instance_uuid=local.instance_uuid,
        checksum=local_sum,
        match=True,
    )


def promote(db: Session, tenant_slug: str, peer_id: int | None = None) -> FederationPromoteRead:
    tenant = _tenant_by_slug(db, tenant_slug)
    peer = resolve_peer(db, peer_id)
    local = local_instance(db)
    role = db.execute(
        select(FederationTenantRole).where(FederationTenantRole.tenant_id == tenant.id),
    ).scalar_one_or_none()
    if role is not None and role.primary_instance_uuid == local.instance_uuid:
        raise HTTPException(status_code=409, detail={"code": "already_primary", "detail": "denne instansen er allerede primær"})
    set_frozen(db, tenant, True)
    try:
        _peer_request(peer, "POST", f"/tenants/{tenant.slug}/freeze", {"frozen": True})
    except HTTPException:
        set_frozen(db, tenant, False)
        raise
    snap = _peer_request(peer, "GET", f"/tenants/{tenant.slug}/snapshot")
    document = snap.get("document") or snap
    with apply_mode():
        apply_tenant_document(db, document)
    remote = _peer_request(peer, "GET", f"/tenants/{tenant.slug}/consistency")
    result = promote_if_match(
        db,
        tenant,
        remote_checksum=str(remote.get("checksum") or ""),
        remote_frozen=bool(remote.get("frozen")),
    )
    if not result.match:
        return result
    _peer_request(
        peer,
        "POST",
        f"/tenants/{tenant.slug}/handoff",
        {"primary_instance_uuid": local.instance_uuid},
    )
    set_frozen(db, tenant, False)
    return result


def handoff(db: Session, tenant_slug: str, primary_instance_uuid: str) -> FederationTenantRoleRead:
    tenant = _tenant_by_slug(db, tenant_slug)
    local = local_instance(db)
    known = primary_instance_uuid == local.instance_uuid or db.execute(
        select(FederationPeer).where(FederationPeer.instance_uuid == primary_instance_uuid),
    ).scalar_one_or_none() is not None
    if not known:
        raise HTTPException(status_code=400, detail={"code": "unknown_instance", "detail": "ukjent instans-uuid"})
    role = upsert_tenant_role(db, tenant.id, primary_instance_uuid, frozen=False)
    return FederationTenantRoleRead(
        tenant_id=tenant.id,
        tenant_slug=tenant.slug,
        tenant_name=tenant.name,
        primary_instance_uuid=role.primary_instance_uuid,
        is_primary_here=role.primary_instance_uuid == local.instance_uuid,
        frozen=role.frozen,
        last_pull_at=role.last_pull_at,
    )
