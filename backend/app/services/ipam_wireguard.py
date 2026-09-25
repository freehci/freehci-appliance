"""WireGuard-grensesnitt og peers. Nøkler er referanser. AllowedIPs er ikke BGP."""

from __future__ import annotations

import re

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.models.dcim import DeviceInstance, DeviceInterface
from app.models.ipam import IpamTunnel, IpamVpnService, IpamWireGuardInterface, IpamWireGuardPeer
from app.schemas.ipam import (
    IpamWireGuardInterfaceCreate,
    IpamWireGuardInterfaceRead,
    IpamWireGuardInterfaceUpdate,
    IpamWireGuardPeerCreate,
    IpamWireGuardPeerRead,
    IpamWireGuardPeerUpdate,
)
from app.services.ipam_errors import ipam_error


def _slugify(value: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", (value or "").strip().lower()).strip("-")
    return (s or "wg")[:128]


def _unique_iface_slug(db: Session, device_id: int, desired: str, *, explicit: bool, exclude_id: int | None = None) -> str:
    base = _slugify(desired)
    if explicit:
        q = select(IpamWireGuardInterface.id).where(
            IpamWireGuardInterface.device_id == device_id,
            IpamWireGuardInterface.slug == base,
        )
        if exclude_id is not None:
            q = q.where(IpamWireGuardInterface.id != exclude_id)
        if db.execute(q).scalar_one_or_none() is not None:
            raise ipam_error(409, "wg_slug", "WireGuard-slug finnes allerede på enheten")
        return base
    candidate = base
    n = 2
    while True:
        q = select(IpamWireGuardInterface.id).where(
            IpamWireGuardInterface.device_id == device_id,
            IpamWireGuardInterface.slug == candidate,
        )
        if exclude_id is not None:
            q = q.where(IpamWireGuardInterface.id != exclude_id)
        if db.execute(q).scalar_one_or_none() is None:
            return candidate
        candidate = f"{base}-{n}"[:128]
        n += 1


def _unique_peer_slug(
    db: Session,
    wg_interface_id: int,
    desired: str,
    *,
    explicit: bool,
    exclude_id: int | None = None,
) -> str:
    base = _slugify(desired)
    if explicit:
        q = select(IpamWireGuardPeer.id).where(
            IpamWireGuardPeer.wg_interface_id == wg_interface_id,
            IpamWireGuardPeer.slug == base,
        )
        if exclude_id is not None:
            q = q.where(IpamWireGuardPeer.id != exclude_id)
        if db.execute(q).scalar_one_or_none() is not None:
            raise ipam_error(409, "wg_peer_slug", "peer-slug finnes allerede på grensesnittet")
        return base
    candidate = base
    n = 2
    while True:
        q = select(IpamWireGuardPeer.id).where(
            IpamWireGuardPeer.wg_interface_id == wg_interface_id,
            IpamWireGuardPeer.slug == candidate,
        )
        if exclude_id is not None:
            q = q.where(IpamWireGuardPeer.id != exclude_id)
        if db.execute(q).scalar_one_or_none() is None:
            return candidate
        candidate = f"{base}-{n}"[:128]
        n += 1


def _require_device(db: Session, device_id: int) -> DeviceInstance:
    row = db.get(DeviceInstance, device_id)
    if row is None:
        raise ipam_error(404, "wg_device", "enhet ikke funnet")
    return row


def _validate_dcim_interface(db: Session, device_id: int, interface_id: int | None) -> int | None:
    if interface_id is None:
        return None
    iface = db.get(DeviceInterface, interface_id)
    if iface is None:
        raise ipam_error(404, "wg_dcim_iface", "grensesnitt ikke funnet")
    if iface.device_id != device_id:
        raise ipam_error(400, "wg_iface_device", "grensesnittet tilhører en annen enhet")
    return iface.id


def _validate_tunnel(db: Session, tunnel_id: int | None) -> int | None:
    if tunnel_id is None:
        return None
    row = db.get(IpamTunnel, tunnel_id)
    if row is None:
        raise ipam_error(404, "wg_tunnel", "tunnel ikke funnet")
    return row.id


def list_interfaces(db: Session, *, device_id: int | None = None) -> list[IpamWireGuardInterface]:
    q = select(IpamWireGuardInterface).options(selectinload(IpamWireGuardInterface.peers)).order_by(
        IpamWireGuardInterface.slug,
    )
    if device_id is not None:
        _require_device(db, device_id)
        q = q.where(IpamWireGuardInterface.device_id == device_id)
    return list(db.execute(q).scalars().unique().all())


def get_interface(db: Session, iface_id: int) -> IpamWireGuardInterface | None:
    return db.execute(
        select(IpamWireGuardInterface)
        .options(selectinload(IpamWireGuardInterface.peers))
        .where(IpamWireGuardInterface.id == iface_id),
    ).scalar_one_or_none()


def get_interface_by_slug(db: Session, device_id: int, slug: str) -> IpamWireGuardInterface | None:
    return db.execute(
        select(IpamWireGuardInterface).where(
            IpamWireGuardInterface.device_id == device_id,
            IpamWireGuardInterface.slug == slug,
        ),
    ).scalar_one_or_none()


def get_peer(db: Session, peer_id: int) -> IpamWireGuardPeer | None:
    return db.get(IpamWireGuardPeer, peer_id)


def get_peer_by_slug(db: Session, wg_interface_id: int, slug: str) -> IpamWireGuardPeer | None:
    return db.execute(
        select(IpamWireGuardPeer).where(
            IpamWireGuardPeer.wg_interface_id == wg_interface_id,
            IpamWireGuardPeer.slug == slug,
        ),
    ).scalar_one_or_none()


def create_interface(db: Session, data: IpamWireGuardInterfaceCreate) -> IpamWireGuardInterface:
    device = _require_device(db, data.device_id)
    interface_id = _validate_dcim_interface(db, device.id, data.interface_id)
    tunnel_id = _validate_tunnel(db, data.tunnel_id)
    slug = _unique_iface_slug(db, device.id, data.slug or data.name, explicit=data.slug is not None)
    row = IpamWireGuardInterface(
        device_id=device.id,
        slug=slug,
        name=data.name.strip(),
        interface_id=interface_id,
        listen_port=data.listen_port,
        address=data.address,
        private_key_ref=data.private_key_ref,
        tunnel_id=tunnel_id,
        notes=data.notes,
    )
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ipam_error(409, "wg_slug", "WireGuard-slug finnes allerede på enheten")
    db.refresh(row)
    loaded = get_interface(db, row.id)
    return loaded if loaded is not None else row


def update_interface(db: Session, row: IpamWireGuardInterface, data: IpamWireGuardInterfaceUpdate) -> IpamWireGuardInterface:
    if data.name is not None:
        row.name = data.name.strip()
    if data.slug is not None:
        row.slug = _unique_iface_slug(db, row.device_id, data.slug, explicit=True, exclude_id=row.id)
    if "interface_id" in data.model_fields_set:
        row.interface_id = _validate_dcim_interface(db, row.device_id, data.interface_id)
    if "listen_port" in data.model_fields_set:
        row.listen_port = data.listen_port
    if "address" in data.model_fields_set:
        row.address = data.address
    if "private_key_ref" in data.model_fields_set:
        row.private_key_ref = data.private_key_ref
    if "tunnel_id" in data.model_fields_set:
        row.tunnel_id = _validate_tunnel(db, data.tunnel_id)
    if data.notes is not None:
        row.notes = data.notes
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ipam_error(409, "wg_slug", "WireGuard-slug finnes allerede på enheten")
    db.refresh(row)
    loaded = get_interface(db, row.id)
    return loaded if loaded is not None else row


def delete_interface(db: Session, row: IpamWireGuardInterface) -> None:
    db.delete(row)
    db.commit()


def create_peer(db: Session, iface: IpamWireGuardInterface, data: IpamWireGuardPeerCreate) -> IpamWireGuardPeer:
    slug = _unique_peer_slug(db, iface.id, data.slug or data.name, explicit=data.slug is not None)
    row = IpamWireGuardPeer(
        wg_interface_id=iface.id,
        slug=slug,
        name=data.name.strip(),
        public_key_ref=data.public_key_ref,
        psk_ref=data.psk_ref,
        endpoint_host=data.endpoint_host.strip() if data.endpoint_host else None,
        endpoint_port=data.endpoint_port,
        allowed_ips=data.allowed_ips,
        persistent_keepalive=data.persistent_keepalive,
        notes=data.notes,
    )
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ipam_error(409, "wg_peer_slug", "peer-slug finnes allerede på grensesnittet")
    db.refresh(row)
    return row


def update_peer(db: Session, row: IpamWireGuardPeer, data: IpamWireGuardPeerUpdate) -> IpamWireGuardPeer:
    if data.name is not None:
        row.name = data.name.strip()
    if data.slug is not None:
        row.slug = _unique_peer_slug(db, row.wg_interface_id, data.slug, explicit=True, exclude_id=row.id)
    if "public_key_ref" in data.model_fields_set:
        row.public_key_ref = data.public_key_ref
    if "psk_ref" in data.model_fields_set:
        row.psk_ref = data.psk_ref
    if "endpoint_host" in data.model_fields_set:
        row.endpoint_host = data.endpoint_host.strip() if data.endpoint_host else None
    if "endpoint_port" in data.model_fields_set:
        row.endpoint_port = data.endpoint_port
    if "allowed_ips" in data.model_fields_set:
        row.allowed_ips = data.allowed_ips
    if "persistent_keepalive" in data.model_fields_set:
        row.persistent_keepalive = data.persistent_keepalive
    if data.notes is not None:
        row.notes = data.notes
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ipam_error(409, "wg_peer_slug", "peer-slug finnes allerede på grensesnittet")
    db.refresh(row)
    return row


def delete_peer(db: Session, row: IpamWireGuardPeer) -> None:
    db.delete(row)
    db.commit()


def peer_to_read(row: IpamWireGuardPeer) -> IpamWireGuardPeerRead:
    return IpamWireGuardPeerRead.model_validate(row)


def iface_to_read(db: Session, row: IpamWireGuardInterface) -> IpamWireGuardInterfaceRead:
    device = db.get(DeviceInstance, row.device_id)
    iface = db.get(DeviceInterface, row.interface_id) if row.interface_id else None
    tunnel = db.get(IpamTunnel, row.tunnel_id) if row.tunnel_id else None
    vpn = db.get(IpamVpnService, tunnel.vpn_service_id) if tunnel is not None else None
    peers = list(row.peers) if row.peers is not None else []
    return IpamWireGuardInterfaceRead(
        id=row.id,
        device_id=row.device_id,
        device_name=device.name if device is not None else None,
        site_id=device.site_id if device is not None else None,
        name=row.name,
        slug=row.slug,
        interface_id=row.interface_id,
        interface_name=iface.name if iface is not None else None,
        listen_port=row.listen_port,
        address=row.address,
        private_key_ref=row.private_key_ref,
        tunnel_id=row.tunnel_id,
        tunnel_slug=tunnel.slug if tunnel is not None else None,
        vpn_slug=vpn.slug if vpn is not None else None,
        notes=row.notes,
        created_at=row.created_at,
        peers=[peer_to_read(p) for p in sorted(peers, key=lambda x: x.slug)],
    )
