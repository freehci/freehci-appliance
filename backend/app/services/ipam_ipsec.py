"""IPsec-profiler og selektorer. Nøkler er referanser. Prefiks og vpn_type gjettes ikke."""

from __future__ import annotations

import ipaddress
import re

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.models.ipam import IpamIpsecProfile, IpamIpsecSelector, IpamIpsecTunnel, IpamTunnel, IpamVpnService
from app.schemas.ipam import (
    IPSEC_IKE_VERSIONS,
    IPSEC_MODES,
    IpamIpsecProfileCreate,
    IpamIpsecProfileRead,
    IpamIpsecSelectorCreate,
    IpamIpsecSelectorRead,
    IpamIpsecTunnelCreate,
    IpamIpsecTunnelRead,
)
from app.services.ipam_errors import ipam_error


def _slugify(value: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", (value or "").strip().lower()).strip("-")
    return (s or "ipsec")[:128]


def _unique_profile_slug(db: Session, desired: str, *, explicit: bool, exclude_id: int | None = None) -> str:
    base = _slugify(desired)
    if explicit:
        q = select(IpamIpsecProfile.id).where(IpamIpsecProfile.slug == base)
        if exclude_id is not None:
            q = q.where(IpamIpsecProfile.id != exclude_id)
        if db.execute(q).scalar_one_or_none() is not None:
            raise ipam_error(409, "ipsec_slug", "IPsec-slug finnes allerede")
        return base
    candidate = base
    n = 2
    while True:
        q = select(IpamIpsecProfile.id).where(IpamIpsecProfile.slug == candidate)
        if exclude_id is not None:
            q = q.where(IpamIpsecProfile.id != exclude_id)
        if db.execute(q).scalar_one_or_none() is None:
            return candidate
        candidate = f"{base}-{n}"[:128]
        n += 1


def _unique_selector_slug(db: Session, profile_id: int, desired: str, *, explicit: bool) -> str:
    base = _slugify(desired)
    if explicit:
        taken = db.execute(
            select(IpamIpsecSelector.id).where(
                IpamIpsecSelector.profile_id == profile_id,
                IpamIpsecSelector.slug == base,
            ),
        ).scalar_one_or_none()
        if taken is not None:
            raise ipam_error(409, "ipsec_selector_slug", "selektor-slug finnes allerede på profilen")
        return base
    candidate = base
    n = 2
    while True:
        q = select(IpamIpsecSelector.id).where(
            IpamIpsecSelector.profile_id == profile_id,
            IpamIpsecSelector.slug == candidate,
        )
        if db.execute(q).scalar_one_or_none() is None:
            return candidate
        candidate = f"{base}-{n}"[:128]
        n += 1


def _validate_ike(value: str | None) -> str | None:
    if value is None:
        return None
    if value not in IPSEC_IKE_VERSIONS:
        raise ipam_error(400, "ipsec_ike", "ukjent IKE-versjon")
    return value


def _validate_mode(value: str | None) -> str | None:
    if value is None:
        return None
    if value not in IPSEC_MODES:
        raise ipam_error(400, "ipsec_mode", "ukjent IPsec-modus")
    return value


def _validate_cidr(value: str | None) -> str | None:
    if value is None:
        return None
    try:
        ipaddress.ip_network(value, strict=False)
    except ValueError:
        raise ipam_error(400, "ipsec_cidr", "ugyldig CIDR")
    return value


def list_profiles(db: Session) -> list[IpamIpsecProfile]:
    return list(
        db.execute(
            select(IpamIpsecProfile)
            .options(selectinload(IpamIpsecProfile.selectors), selectinload(IpamIpsecProfile.tunnels))
            .order_by(IpamIpsecProfile.slug),
        ).scalars().unique().all(),
    )


def get_profile(db: Session, profile_id: int) -> IpamIpsecProfile | None:
    return db.execute(
        select(IpamIpsecProfile)
        .options(selectinload(IpamIpsecProfile.selectors), selectinload(IpamIpsecProfile.tunnels))
        .where(IpamIpsecProfile.id == profile_id),
    ).scalar_one_or_none()


def get_profile_by_slug(db: Session, slug: str) -> IpamIpsecProfile | None:
    return db.execute(select(IpamIpsecProfile).where(IpamIpsecProfile.slug == slug)).scalar_one_or_none()


def get_selector(db: Session, selector_id: int) -> IpamIpsecSelector | None:
    return db.get(IpamIpsecSelector, selector_id)


def get_selector_by_slug(db: Session, profile_id: int, slug: str) -> IpamIpsecSelector | None:
    return db.execute(
        select(IpamIpsecSelector).where(
            IpamIpsecSelector.profile_id == profile_id,
            IpamIpsecSelector.slug == slug,
        ),
    ).scalar_one_or_none()


def get_tunnel_bind(db: Session, bind_id: int) -> IpamIpsecTunnel | None:
    return db.get(IpamIpsecTunnel, bind_id)


def get_bind_for_tunnel(db: Session, tunnel_id: int) -> IpamIpsecTunnel | None:
    return db.execute(select(IpamIpsecTunnel).where(IpamIpsecTunnel.tunnel_id == tunnel_id)).scalar_one_or_none()


def create_profile(db: Session, data: IpamIpsecProfileCreate) -> IpamIpsecProfile:
    slug = _unique_profile_slug(db, data.slug or data.name, explicit=data.slug is not None)
    row = IpamIpsecProfile(
        name=data.name.strip(),
        slug=slug,
        ike_version=_validate_ike(data.ike_version),
        mode=_validate_mode(data.mode),
        psk_ref=data.psk_ref,
        local_id=data.local_id,
        remote_id=data.remote_id,
        notes=data.notes,
    )
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ipam_error(409, "ipsec_slug", "IPsec-slug finnes allerede")
    db.refresh(row)
    loaded = get_profile(db, row.id)
    return loaded if loaded is not None else row


def delete_profile(db: Session, row: IpamIpsecProfile) -> None:
    db.delete(row)
    db.commit()


def create_selector(db: Session, profile: IpamIpsecProfile, data: IpamIpsecSelectorCreate) -> IpamIpsecSelector:
    slug = _unique_selector_slug(db, profile.id, data.slug or data.name, explicit=data.slug is not None)
    row = IpamIpsecSelector(
        profile_id=profile.id,
        slug=slug,
        name=data.name.strip(),
        local_cidr=_validate_cidr(data.local_cidr),
        remote_cidr=_validate_cidr(data.remote_cidr),
        notes=data.notes,
    )
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ipam_error(409, "ipsec_selector_slug", "selektor-slug finnes allerede på profilen")
    db.refresh(row)
    return row


def delete_selector(db: Session, row: IpamIpsecSelector) -> None:
    db.delete(row)
    db.commit()


def bind_tunnel(db: Session, data: IpamIpsecTunnelCreate) -> IpamIpsecTunnel:
    tunnel = db.get(IpamTunnel, data.tunnel_id)
    if tunnel is None:
        raise ipam_error(404, "ipsec_tunnel", "tunnel ikke funnet")
    profile = get_profile(db, data.profile_id)
    if profile is None:
        raise ipam_error(404, "ipsec_profile", "IPsec-profil ikke funnet")
    if get_bind_for_tunnel(db, tunnel.id) is not None:
        raise ipam_error(409, "ipsec_tunnel_taken", "tunnelen har allerede en IPsec-profil")
    row = IpamIpsecTunnel(tunnel_id=tunnel.id, profile_id=profile.id)
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ipam_error(409, "ipsec_tunnel_taken", "tunnelen har allerede en IPsec-profil")
    db.refresh(row)
    return row


def unbind_tunnel(db: Session, row: IpamIpsecTunnel) -> None:
    db.delete(row)
    db.commit()


def selector_to_read(row: IpamIpsecSelector) -> IpamIpsecSelectorRead:
    return IpamIpsecSelectorRead.model_validate(row)


def tunnel_bind_to_read(db: Session, row: IpamIpsecTunnel) -> IpamIpsecTunnelRead:
    tunnel = db.get(IpamTunnel, row.tunnel_id)
    vpn = db.get(IpamVpnService, tunnel.vpn_service_id) if tunnel is not None else None
    return IpamIpsecTunnelRead(
        id=row.id,
        tunnel_id=row.tunnel_id,
        profile_id=row.profile_id,
        tunnel_slug=tunnel.slug if tunnel is not None else None,
        vpn_slug=vpn.slug if vpn is not None else None,
        created_at=row.created_at,
    )


def profile_to_read(db: Session, row: IpamIpsecProfile) -> IpamIpsecProfileRead:
    selectors = list(row.selectors) if row.selectors is not None else []
    binds = list(row.tunnels) if row.tunnels is not None else []
    return IpamIpsecProfileRead(
        id=row.id,
        name=row.name,
        slug=row.slug,
        ike_version=row.ike_version,
        mode=row.mode,
        psk_ref=row.psk_ref,
        local_id=row.local_id,
        remote_id=row.remote_id,
        notes=row.notes,
        created_at=row.created_at,
        selectors=[selector_to_read(s) for s in sorted(selectors, key=lambda x: x.slug)],
        tunnels=[tunnel_bind_to_read(db, b) for b in binds],
    )
