"""GRE-profiler. GRE er innkapsling, ikke kryptering. Endepunkt og vpn_type gjettes ikke."""

from __future__ import annotations

import ipaddress
import re

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.models.ipam import IpamGreProfile, IpamGreTunnel, IpamTunnel, IpamVpnService
from app.schemas.ipam import IpamGreProfileCreate, IpamGreProfileRead, IpamGreTunnelCreate, IpamGreTunnelRead
from app.services.ipam_errors import ipam_error


def _slugify(value: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", (value or "").strip().lower()).strip("-")
    return (s or "gre")[:128]


def _unique_profile_slug(db: Session, desired: str, *, explicit: bool, exclude_id: int | None = None) -> str:
    base = _slugify(desired)
    if explicit:
        q = select(IpamGreProfile.id).where(IpamGreProfile.slug == base)
        if exclude_id is not None:
            q = q.where(IpamGreProfile.id != exclude_id)
        if db.execute(q).scalar_one_or_none() is not None:
            raise ipam_error(409, "gre_slug", "GRE-slug finnes allerede")
        return base
    candidate = base
    n = 2
    while True:
        q = select(IpamGreProfile.id).where(IpamGreProfile.slug == candidate)
        if exclude_id is not None:
            q = q.where(IpamGreProfile.id != exclude_id)
        if db.execute(q).scalar_one_or_none() is None:
            return candidate
        candidate = f"{base}-{n}"[:128]
        n += 1


def _validate_ip(value: str | None) -> str | None:
    if value is None:
        return None
    try:
        ipaddress.ip_address(value)
    except ValueError:
        raise ipam_error(400, "gre_address", "ugyldig IP-adresse")
    return value


def _validate_key_id(value: int | None) -> int | None:
    if value is None:
        return None
    if value < 0 or value > 0xFFFFFFFF:
        raise ipam_error(400, "gre_key", "GRE-nøkkel må være 0–4294967295")
    return value


def _validate_ttl(value: int | None) -> int | None:
    if value is None:
        return None
    if value < 1 or value > 255:
        raise ipam_error(400, "gre_ttl", "TTL må være 1–255")
    return value


def list_profiles(db: Session) -> list[IpamGreProfile]:
    return list(
        db.execute(
            select(IpamGreProfile)
            .options(selectinload(IpamGreProfile.tunnels))
            .order_by(IpamGreProfile.slug),
        ).scalars().unique().all(),
    )


def get_profile(db: Session, profile_id: int) -> IpamGreProfile | None:
    return db.execute(
        select(IpamGreProfile)
        .options(selectinload(IpamGreProfile.tunnels))
        .where(IpamGreProfile.id == profile_id),
    ).scalar_one_or_none()


def get_profile_by_slug(db: Session, slug: str) -> IpamGreProfile | None:
    return db.execute(select(IpamGreProfile).where(IpamGreProfile.slug == slug)).scalar_one_or_none()


def get_tunnel_bind(db: Session, bind_id: int) -> IpamGreTunnel | None:
    return db.get(IpamGreTunnel, bind_id)


def get_bind_for_tunnel(db: Session, tunnel_id: int) -> IpamGreTunnel | None:
    return db.execute(select(IpamGreTunnel).where(IpamGreTunnel.tunnel_id == tunnel_id)).scalar_one_or_none()


def create_profile(db: Session, data: IpamGreProfileCreate) -> IpamGreProfile:
    slug = _unique_profile_slug(db, data.slug or data.name, explicit=data.slug is not None)
    row = IpamGreProfile(
        name=data.name.strip(),
        slug=slug,
        local_address=_validate_ip(data.local_address),
        remote_address=_validate_ip(data.remote_address),
        key_id=_validate_key_id(data.key_id),
        ttl=_validate_ttl(data.ttl),
        checksum=data.checksum,
        sequence=data.sequence,
        notes=data.notes,
    )
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ipam_error(409, "gre_slug", "GRE-slug finnes allerede")
    db.refresh(row)
    loaded = get_profile(db, row.id)
    return loaded if loaded is not None else row


def delete_profile(db: Session, row: IpamGreProfile) -> None:
    db.delete(row)
    db.commit()


def bind_tunnel(db: Session, data: IpamGreTunnelCreate) -> IpamGreTunnel:
    tunnel = db.get(IpamTunnel, data.tunnel_id)
    if tunnel is None:
        raise ipam_error(404, "gre_tunnel", "tunnel ikke funnet")
    profile = get_profile(db, data.profile_id)
    if profile is None:
        raise ipam_error(404, "gre_profile", "GRE-profil ikke funnet")
    if get_bind_for_tunnel(db, tunnel.id) is not None:
        raise ipam_error(409, "gre_tunnel_taken", "tunnelen har allerede en GRE-profil")
    row = IpamGreTunnel(tunnel_id=tunnel.id, profile_id=profile.id)
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ipam_error(409, "gre_tunnel_taken", "tunnelen har allerede en GRE-profil")
    db.refresh(row)
    return row


def unbind_tunnel(db: Session, row: IpamGreTunnel) -> None:
    db.delete(row)
    db.commit()


def tunnel_bind_to_read(db: Session, row: IpamGreTunnel) -> IpamGreTunnelRead:
    tunnel = db.get(IpamTunnel, row.tunnel_id)
    vpn = db.get(IpamVpnService, tunnel.vpn_service_id) if tunnel is not None else None
    return IpamGreTunnelRead(
        id=row.id,
        tunnel_id=row.tunnel_id,
        profile_id=row.profile_id,
        tunnel_slug=tunnel.slug if tunnel is not None else None,
        vpn_slug=vpn.slug if vpn is not None else None,
        created_at=row.created_at,
    )


def profile_to_read(db: Session, row: IpamGreProfile) -> IpamGreProfileRead:
    binds = list(row.tunnels) if row.tunnels is not None else []
    return IpamGreProfileRead(
        id=row.id,
        name=row.name,
        slug=row.slug,
        local_address=row.local_address,
        remote_address=row.remote_address,
        key_id=row.key_id,
        ttl=row.ttl,
        checksum=row.checksum,
        sequence=row.sequence,
        notes=row.notes,
        created_at=row.created_at,
        tunnels=[tunnel_bind_to_read(db, b) for b in binds],
    )
