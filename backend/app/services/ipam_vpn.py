"""VPN-tjenester, tunneler og peers. Nøkler er referanser, ikke materiale."""

from __future__ import annotations

import re

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.dcim import DeviceInstance, DeviceInterface, Site
from app.models.ipam import (
    IpamCircuit,
    IpamTunnel,
    IpamTunnelEndpoint,
    IpamTunnelTransport,
    IpamVpnMember,
    IpamTunnelPeer,
    IpamTunnelProfile,
    IpamVpnService,
)
from app.models.tenant import Tenant
from app.schemas.ipam import (
    IpamTunnelCreate,
    IpamTunnelEndpointCreate,
    IpamTunnelEndpointRead,
    IpamTunnelPeerCreate,
    IpamTunnelPeerRead,
    IpamTunnelPeerUpdate,
    IpamTunnelProfileCreate,
    IpamTunnelProfileRead,
    IpamTunnelProfileUpdate,
    IpamTunnelRead,
    IpamTunnelTransportCreate,
    IpamTunnelTransportRead,
    IpamTunnelUpdate,
    IpamVpnMemberCreate,
    IpamVpnMemberRead,
    IpamVpnServiceCreate,
    IpamVpnServiceRead,
    IpamVpnServiceUpdate,
)
from app.services.ipam_errors import ipam_error


def _slugify(value: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", (value or "").strip().lower()).strip("-")
    return (s or "item")[:128]


def _require_tenant(db: Session, tenant_id: int) -> Tenant:
    row = db.get(Tenant, tenant_id)
    if row is None:
        raise ValueError("tenant ikke funnet")
    return row


def _require_site(db: Session, site_id: int) -> Site:
    row = db.get(Site, site_id)
    if row is None:
        raise ValueError("site ikke funnet")
    return row


def _resolve_device_iface(
    db: Session,
    *,
    device_id: int | None,
    interface_id: int | None,
) -> tuple[int | None, int | None]:
    if interface_id is None:
        if device_id is not None and db.get(DeviceInstance, device_id) is None:
            raise ValueError("enhet ikke funnet")
        return device_id, None
    iface = db.get(DeviceInterface, interface_id)
    if iface is None:
        raise ValueError("grensesnitt ikke funnet")
    if device_id is not None and iface.device_id != device_id:
        raise ipam_error(400, "device_interface_mismatch", "grensesnittet tilhører en annen enhet")
    return iface.device_id, iface.id


def _unique_vpn_slug(db: Session, tenant_scope: int, desired: str, *, exclude_id: int | None = None) -> str:
    base = _slugify(desired)
    candidate = base
    n = 2
    while True:
        q = select(IpamVpnService.id).where(IpamVpnService.tenant_scope == tenant_scope, IpamVpnService.slug == candidate)
        if exclude_id is not None:
            q = q.where(IpamVpnService.id != exclude_id)
        if db.execute(q).scalar_one_or_none() is None:
            return candidate
        candidate = f"{base}-{n}"[:128]
        n += 1


def _unique_tunnel_slug(db: Session, vpn_id: int, desired: str, *, exclude_id: int | None = None) -> str:
    base = _slugify(desired)
    candidate = base
    n = 2
    while True:
        q = select(IpamTunnel.id).where(IpamTunnel.vpn_service_id == vpn_id, IpamTunnel.slug == candidate)
        if exclude_id is not None:
            q = q.where(IpamTunnel.id != exclude_id)
        if db.execute(q).scalar_one_or_none() is None:
            return candidate
        candidate = f"{base}-{n}"[:128]
        n += 1


def _unique_profile_slug(db: Session, desired: str, *, exclude_id: int | None = None) -> str:
    base = _slugify(desired)
    candidate = base
    n = 2
    while True:
        q = select(IpamTunnelProfile.id).where(IpamTunnelProfile.slug == candidate)
        if exclude_id is not None:
            q = q.where(IpamTunnelProfile.id != exclude_id)
        if db.execute(q).scalar_one_or_none() is None:
            return candidate
        candidate = f"{base}-{n}"[:128]
        n += 1


def list_vpn_services(db: Session, *, tenant_id: int | None = None) -> list[IpamVpnService]:
    q = select(IpamVpnService).order_by(IpamVpnService.name)
    if tenant_id is not None:
        q = q.where(IpamVpnService.tenant_id == tenant_id)
    return list(db.execute(q).scalars().all())


def get_vpn_service(db: Session, vpn_id: int) -> IpamVpnService | None:
    return db.get(IpamVpnService, vpn_id)


def get_vpn_by_source_circuit(db: Session, circuit_id: int) -> IpamVpnService | None:
    return db.execute(
        select(IpamVpnService).where(IpamVpnService.source_circuit_id == circuit_id),
    ).scalar_one_or_none()


def create_vpn_service(db: Session, data: IpamVpnServiceCreate) -> IpamVpnService:
    if data.tenant_id is not None:
        _require_tenant(db, data.tenant_id)
    if data.source_circuit_id is not None:
        circuit = db.get(IpamCircuit, data.source_circuit_id)
        if circuit is None:
            raise ValueError("samband ikke funnet")
        existing = get_vpn_by_source_circuit(db, circuit.id)
        if existing is not None:
            raise ipam_error(409, "vpn_source_exists", "sambandet har allerede en VPN-tjeneste")
    scope = int(data.tenant_id) if data.tenant_id is not None else 0
    row = IpamVpnService(
        tenant_id=data.tenant_id,
        tenant_scope=scope,
        name=data.name.strip(),
        slug=_unique_vpn_slug(db, scope, data.slug or data.name),
        vpn_type=data.vpn_type,
        source_circuit_id=data.source_circuit_id,
        description=data.description,
    )
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise
    db.refresh(row)
    return row


def update_vpn_service(db: Session, row: IpamVpnService, data: IpamVpnServiceUpdate) -> IpamVpnService:
    if data.tenant_id is not None:
        _require_tenant(db, data.tenant_id)
        row.tenant_id = data.tenant_id
        row.tenant_scope = int(data.tenant_id)
    if data.name is not None:
        row.name = data.name.strip()
    if data.slug is not None:
        row.slug = _unique_vpn_slug(db, row.tenant_scope, data.slug, exclude_id=row.id)
    if data.vpn_type is not None:
        row.vpn_type = data.vpn_type
    if data.source_circuit_id is not None:
        circuit = db.get(IpamCircuit, data.source_circuit_id)
        if circuit is None:
            raise ValueError("samband ikke funnet")
        existing = get_vpn_by_source_circuit(db, circuit.id)
        if existing is not None and existing.id != row.id:
            raise ipam_error(409, "vpn_source_exists", "sambandet har allerede en VPN-tjeneste")
        row.source_circuit_id = data.source_circuit_id
    if data.description is not None:
        row.description = data.description
    db.commit()
    db.refresh(row)
    return row


def delete_vpn_service(db: Session, row: IpamVpnService) -> None:
    for m in list(db.execute(select(IpamVpnMember).where(IpamVpnMember.vpn_service_id == row.id)).scalars().all()):
        db.delete(m)
    db.delete(row)
    db.commit()


def list_vpn_members(db: Session, vpn_id: int) -> list[IpamVpnMember]:
    return list(
        db.execute(select(IpamVpnMember).where(IpamVpnMember.vpn_service_id == vpn_id).order_by(IpamVpnMember.id)).scalars().all()
    )


def get_vpn_member(db: Session, member_id: int) -> IpamVpnMember | None:
    return db.get(IpamVpnMember, member_id)


def get_vpn_member_by_site(db: Session, vpn_id: int, site_id: int) -> IpamVpnMember | None:
    return db.execute(
        select(IpamVpnMember).where(IpamVpnMember.vpn_service_id == vpn_id, IpamVpnMember.site_id == site_id),
    ).scalar_one_or_none()


def get_vpn_member_by_slug(db: Session, vpn_id: int, slug: str) -> IpamVpnMember | None:
    return db.execute(
        select(IpamVpnMember).where(IpamVpnMember.vpn_service_id == vpn_id, IpamVpnMember.slug == slug),
    ).scalar_one_or_none()


def _unique_member_slug(db: Session, vpn_id: int, desired: str, *, explicit: bool = False) -> str:
    base = _slugify(desired)
    if explicit:
        if get_vpn_member_by_slug(db, vpn_id, base) is not None:
            raise ipam_error(409, "vpn_member_taken", "klienten er allerede medlem av denne VPN-tjenesten")
        return base
    candidate = base
    n = 2
    while get_vpn_member_by_slug(db, vpn_id, candidate) is not None:
        candidate = f"{base}-{n}"[:128]
        n += 1
    return candidate


def create_vpn_member(db: Session, vpn: IpamVpnService, data: IpamVpnMemberCreate) -> IpamVpnMember:
    has_site = data.site_id is not None
    has_client = bool((data.name or "").strip() or (data.slug or "").strip())
    if has_site == has_client:
        raise ipam_error(400, "vpn_member_target", "oppgi site eller klient, ikke begge")
    if has_site:
        site = db.get(Site, data.site_id)
        if site is None:
            raise ipam_error(404, "site_not_found", "site ikke funnet")
        if get_vpn_member_by_site(db, vpn.id, site.id) is not None:
            raise ipam_error(409, "vpn_member_taken", "siten er allerede medlem av denne VPN-tjenesten")
        row = IpamVpnMember(vpn_service_id=vpn.id, site_id=site.id, name=None, slug=None, role=data.role)
    else:
        name = (data.name or data.slug or "").strip()
        slug = _unique_member_slug(db, vpn.id, data.slug or name, explicit=True)
        row = IpamVpnMember(vpn_service_id=vpn.id, site_id=None, name=name, slug=slug, role=data.role)
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ipam_error(409, "vpn_member_taken", "medlemmet finnes allerede i denne VPN-tjenesten")
    db.refresh(row)
    return row


def delete_vpn_member(db: Session, row: IpamVpnMember) -> None:
    db.delete(row)
    db.commit()


def vpn_member_to_read(db: Session, row: IpamVpnMember) -> IpamVpnMemberRead:
    site = db.get(Site, row.site_id) if row.site_id is not None else None
    return IpamVpnMemberRead(
        id=row.id,
        vpn_service_id=row.vpn_service_id,
        site_id=row.site_id,
        site_name=site.name if site is not None else None,
        site_slug=site.slug if site is not None else None,
        name=row.name,
        slug=row.slug,
        role=row.role,
        created_at=row.created_at,
    )


def vpn_type_from_circuit(circuit: IpamCircuit) -> str:
    if circuit.circuit_type == "wireguard":
        return "wireguard"
    return "other"


def ensure_vpn_from_circuit(db: Session, circuit: IpamCircuit) -> IpamVpnService:
    existing = get_vpn_by_source_circuit(db, circuit.id)
    if existing is not None:
        return existing
    return create_vpn_service(
        db,
        IpamVpnServiceCreate(
            name=circuit.name,
            slug=circuit.circuit_number,
            vpn_type=vpn_type_from_circuit(circuit),
            tenant_id=circuit.tenant_id,
            source_circuit_id=circuit.id,
            description=circuit.description,
        ),
    )


def list_tunnels(db: Session, vpn_id: int) -> list[IpamTunnel]:
    q = select(IpamTunnel).where(IpamTunnel.vpn_service_id == vpn_id).order_by(IpamTunnel.name)
    return list(db.execute(q).scalars().all())


def get_tunnel(db: Session, tunnel_id: int) -> IpamTunnel | None:
    return db.get(IpamTunnel, tunnel_id)


def create_tunnel(db: Session, vpn: IpamVpnService, data: IpamTunnelCreate) -> IpamTunnel:
    if data.profile_id is not None and db.get(IpamTunnelProfile, data.profile_id) is None:
        raise ValueError("tunnelprofil ikke funnet")
    row = IpamTunnel(
        vpn_service_id=vpn.id,
        profile_id=data.profile_id,
        name=data.name.strip(),
        slug=_unique_tunnel_slug(db, vpn.id, data.slug or data.name),
        status=data.status,
        description=data.description,
    )
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise
    db.refresh(row)
    return row


def update_tunnel(db: Session, row: IpamTunnel, data: IpamTunnelUpdate) -> IpamTunnel:
    if data.name is not None:
        row.name = data.name.strip()
    if data.slug is not None:
        row.slug = _unique_tunnel_slug(db, row.vpn_service_id, data.slug, exclude_id=row.id)
    if data.status is not None:
        row.status = data.status
    if data.profile_id is not None:
        if db.get(IpamTunnelProfile, data.profile_id) is None:
            raise ValueError("tunnelprofil ikke funnet")
        row.profile_id = data.profile_id
    if data.description is not None:
        row.description = data.description
    db.commit()
    db.refresh(row)
    return row


def delete_tunnel(db: Session, row: IpamTunnel) -> None:
    for b in list(db.execute(select(IpamTunnelTransport).where(IpamTunnelTransport.tunnel_id == row.id)).scalars().all()):
        db.delete(b)
    db.delete(row)
    db.commit()


def list_tunnel_transports(db: Session, tunnel_id: int) -> list[IpamTunnelTransport]:
    return list(
        db.execute(select(IpamTunnelTransport).where(IpamTunnelTransport.tunnel_id == tunnel_id).order_by(IpamTunnelTransport.id)).scalars().all()
    )


def get_tunnel_transport(db: Session, bind_id: int) -> IpamTunnelTransport | None:
    return db.get(IpamTunnelTransport, bind_id)


def get_tunnel_transport_by_circuit(db: Session, tunnel_id: int, circuit_id: int) -> IpamTunnelTransport | None:
    return db.execute(
        select(IpamTunnelTransport).where(
            IpamTunnelTransport.tunnel_id == tunnel_id,
            IpamTunnelTransport.circuit_id == circuit_id,
        ),
    ).scalar_one_or_none()


def create_tunnel_transport(db: Session, tunnel: IpamTunnel, data: IpamTunnelTransportCreate) -> IpamTunnelTransport:
    circuit = db.get(IpamCircuit, data.circuit_id)
    if circuit is None:
        raise ipam_error(404, "circuit_not_found", "samband ikke funnet")
    if get_tunnel_transport_by_circuit(db, tunnel.id, circuit.id) is not None:
        raise ipam_error(409, "tunnel_transport_taken", "sambandet er allerede knyttet til denne tunnelen")
    row = IpamTunnelTransport(tunnel_id=tunnel.id, circuit_id=circuit.id)
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ipam_error(409, "tunnel_transport_taken", "sambandet er allerede knyttet til denne tunnelen")
    db.refresh(row)
    return row


def delete_tunnel_transport(db: Session, row: IpamTunnelTransport) -> None:
    db.delete(row)
    db.commit()


def tunnel_transport_to_read(db: Session, row: IpamTunnelTransport) -> IpamTunnelTransportRead:
    circuit = db.get(IpamCircuit, row.circuit_id)
    return IpamTunnelTransportRead(
        id=row.id,
        tunnel_id=row.tunnel_id,
        circuit_id=row.circuit_id,
        circuit_number=circuit.circuit_number if circuit is not None else "",
        circuit_name=circuit.name if circuit is not None else "",
        created_at=row.created_at,
    )


def list_endpoints(db: Session, tunnel_id: int) -> list[IpamTunnelEndpoint]:
    q = select(IpamTunnelEndpoint).where(IpamTunnelEndpoint.tunnel_id == tunnel_id).order_by(IpamTunnelEndpoint.endpoint)
    return list(db.execute(q).scalars().all())


def upsert_endpoint(db: Session, tunnel: IpamTunnel, data: IpamTunnelEndpointCreate) -> IpamTunnelEndpoint:
    device_id, interface_id = _resolve_device_iface(db, device_id=data.device_id, interface_id=data.interface_id)
    if data.site_id is not None:
        _require_site(db, data.site_id)
    existing = db.execute(
        select(IpamTunnelEndpoint).where(
            IpamTunnelEndpoint.tunnel_id == tunnel.id,
            IpamTunnelEndpoint.endpoint == data.endpoint,
        ),
    ).scalar_one_or_none()
    if existing is not None:
        existing.device_id = device_id
        existing.interface_id = interface_id
        existing.site_id = data.site_id
        existing.label = data.label.strip() if data.label else None
        db.commit()
        db.refresh(existing)
        return existing
    row = IpamTunnelEndpoint(
        tunnel_id=tunnel.id,
        endpoint=data.endpoint,
        device_id=device_id,
        interface_id=interface_id,
        site_id=data.site_id,
        label=data.label.strip() if data.label else None,
    )
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise
    db.refresh(row)
    return row


def list_peers(db: Session, tunnel_id: int) -> list[IpamTunnelPeer]:
    q = select(IpamTunnelPeer).where(IpamTunnelPeer.tunnel_id == tunnel_id).order_by(IpamTunnelPeer.name)
    return list(db.execute(q).scalars().all())


def get_peer(db: Session, peer_id: int) -> IpamTunnelPeer | None:
    return db.get(IpamTunnelPeer, peer_id)


def create_peer(db: Session, tunnel: IpamTunnel, data: IpamTunnelPeerCreate) -> IpamTunnelPeer:
    device_id, interface_id = _resolve_device_iface(db, device_id=data.device_id, interface_id=data.interface_id)
    row = IpamTunnelPeer(
        tunnel_id=tunnel.id,
        name=data.name.strip(),
        public_key_ref=data.public_key_ref,
        allowed_ips=data.allowed_ips,
        endpoint_host=data.endpoint_host.strip() if data.endpoint_host else None,
        endpoint_port=data.endpoint_port,
        persistent_keepalive=data.persistent_keepalive,
        device_id=device_id,
        interface_id=interface_id,
        notes=data.notes,
    )
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise
    db.refresh(row)
    return row


def update_peer(db: Session, row: IpamTunnelPeer, data: IpamTunnelPeerUpdate) -> IpamTunnelPeer:
    if data.name is not None:
        row.name = data.name.strip()
    if data.public_key_ref is not None:
        row.public_key_ref = data.public_key_ref
    if data.allowed_ips is not None:
        row.allowed_ips = data.allowed_ips
    if data.endpoint_host is not None:
        row.endpoint_host = data.endpoint_host.strip() if data.endpoint_host else None
    if data.endpoint_port is not None:
        row.endpoint_port = data.endpoint_port
    if data.persistent_keepalive is not None:
        row.persistent_keepalive = data.persistent_keepalive
    if data.device_id is not None or data.interface_id is not None:
        device_id, interface_id = _resolve_device_iface(db, device_id=data.device_id, interface_id=data.interface_id)
        row.device_id = device_id
        row.interface_id = interface_id
    if data.notes is not None:
        row.notes = data.notes
    db.commit()
    db.refresh(row)
    return row


def delete_peer(db: Session, row: IpamTunnelPeer) -> None:
    db.delete(row)
    db.commit()


def list_profiles(db: Session) -> list[IpamTunnelProfile]:
    return list(db.execute(select(IpamTunnelProfile).order_by(IpamTunnelProfile.name)).scalars().all())


def get_profile(db: Session, profile_id: int) -> IpamTunnelProfile | None:
    return db.get(IpamTunnelProfile, profile_id)


def create_profile(db: Session, data: IpamTunnelProfileCreate) -> IpamTunnelProfile:
    row = IpamTunnelProfile(
        name=data.name.strip(),
        slug=_unique_profile_slug(db, data.slug or data.name),
        vpn_type=data.vpn_type,
        settings=data.settings,
        description=data.description,
    )
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise
    db.refresh(row)
    return row


def update_profile(db: Session, row: IpamTunnelProfile, data: IpamTunnelProfileUpdate) -> IpamTunnelProfile:
    if data.name is not None:
        row.name = data.name.strip()
    if data.slug is not None:
        row.slug = _unique_profile_slug(db, data.slug, exclude_id=row.id)
    if data.vpn_type is not None:
        row.vpn_type = data.vpn_type
    if data.settings is not None:
        row.settings = data.settings
    if data.description is not None:
        row.description = data.description
    db.commit()
    db.refresh(row)
    return row


def delete_profile(db: Session, row: IpamTunnelProfile) -> None:
    db.delete(row)
    db.commit()


def _names_for(db: Session, device_id: int | None, interface_id: int | None) -> tuple[str | None, str | None]:
    device_name = None
    interface_name = None
    if interface_id is not None:
        iface = db.get(DeviceInterface, interface_id)
        if iface is not None:
            interface_name = iface.name
            if device_id is None:
                device_id = iface.device_id
    if device_id is not None:
        device = db.get(DeviceInstance, device_id)
        if device is not None:
            device_name = device.name
    return device_name, interface_name


def vpn_to_read(row: IpamVpnService) -> IpamVpnServiceRead:
    return IpamVpnServiceRead.model_validate(row)


def tunnel_to_read(row: IpamTunnel) -> IpamTunnelRead:
    return IpamTunnelRead.model_validate(row)


def endpoint_to_read(db: Session, row: IpamTunnelEndpoint) -> IpamTunnelEndpointRead:
    device_name, interface_name = _names_for(db, row.device_id, row.interface_id)
    return IpamTunnelEndpointRead.model_validate(row).model_copy(
        update={"device_name": device_name, "interface_name": interface_name},
    )


def peer_to_read(row: IpamTunnelPeer) -> IpamTunnelPeerRead:
    return IpamTunnelPeerRead.model_validate(row)


def profile_to_read(row: IpamTunnelProfile) -> IpamTunnelProfileRead:
    return IpamTunnelProfileRead.model_validate(row)
