"""AS og BGP-sesjoner. Ikke RIB/IRR/RPKI. Observed status gjettes aldri."""

from __future__ import annotations

import re

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.asn import is_private_asn
from app.models.dcim import DeviceInstance, DeviceInterface, Site
from app.models.ipam import IpamAsAssignment, IpamAutonomousSystem, IpamBgpInstance, IpamBgpSession, IpamVrf
from app.models.tenant import Tenant
from app.schemas.ipam import (
    IpamAsAssignmentCreate,
    IpamAsAssignmentRead,
    IpamAutonomousSystemCreate,
    IpamAutonomousSystemRead,
    IpamAutonomousSystemUpdate,
    IpamBgpInstanceCreate,
    IpamBgpInstanceRead,
    IpamBgpSessionCreate,
    IpamBgpSessionRead,
    IpamBgpSessionUpdate,
)
from app.services import dcim as dcim_svc
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


def _require_vrf(db: Session, vrf_id: int, *, site_id: int | None = None) -> IpamVrf:
    row = db.get(IpamVrf, vrf_id)
    if row is None:
        raise ValueError("VRF ikke funnet")
    if site_id is not None and row.site_id != site_id:
        raise ipam_error(400, "vrf_site_mismatch", "VRF tilhører en annen site")
    return row


def _unique_as_slug(db: Session, desired: str, *, exclude_id: int | None = None) -> str:
    base = _slugify(desired)
    candidate = base
    n = 2
    while True:
        q = select(IpamAutonomousSystem.id).where(IpamAutonomousSystem.slug == candidate)
        if exclude_id is not None:
            q = q.where(IpamAutonomousSystem.id != exclude_id)
        if db.execute(q).scalar_one_or_none() is None:
            return candidate
        candidate = f"{base}-{n}"[:128]
        n += 1


def _unique_bgp_slug(db: Session, site_id: int, desired: str, *, exclude_id: int | None = None) -> str:
    base = _slugify(desired)
    candidate = base
    n = 2
    while True:
        q = select(IpamBgpSession.id).where(IpamBgpSession.site_id == site_id, IpamBgpSession.slug == candidate)
        if exclude_id is not None:
            q = q.where(IpamBgpSession.id != exclude_id)
        if db.execute(q).scalar_one_or_none() is None:
            return candidate
        candidate = f"{base}-{n}"[:128]
        n += 1


def list_autonomous_systems(db: Session, *, tenant_id: int | None = None) -> list[IpamAutonomousSystem]:
    q = select(IpamAutonomousSystem).order_by(IpamAutonomousSystem.asn)
    if tenant_id is not None:
        q = q.where(IpamAutonomousSystem.tenant_id == tenant_id)
    return list(db.execute(q).scalars().all())


def get_autonomous_system(db: Session, as_id: int) -> IpamAutonomousSystem | None:
    return db.get(IpamAutonomousSystem, as_id)


def get_as_by_asn(db: Session, asn: int, *, tenant_scope: int | None = None) -> IpamAutonomousSystem | None:
    q = select(IpamAutonomousSystem).where(IpamAutonomousSystem.asn == asn)
    if tenant_scope is not None:
        q = q.where(IpamAutonomousSystem.tenant_scope == tenant_scope)
    return db.execute(q).scalars().first()


def resolve_as_for_site(db: Session, asn: int, site: Site) -> IpamAutonomousSystem | None:
    """Offentlig ASN er globalt; privat ASN slås opp i site-tenant først, deretter uscopet."""
    if is_private_asn(asn) and site.tenant_id is not None:
        scoped = get_as_by_asn(db, asn, tenant_scope=site.tenant_id)
        if scoped is not None:
            return scoped
    return db.execute(
        select(IpamAutonomousSystem).where(
            IpamAutonomousSystem.asn == asn,
            IpamAutonomousSystem.tenant_scope == 0,
        ),
    ).scalar_one_or_none()


def create_autonomous_system(db: Session, data: IpamAutonomousSystemCreate) -> IpamAutonomousSystem:
    if data.tenant_id is not None:
        _require_tenant(db, data.tenant_id)
    private = is_private_asn(data.asn)
    scope = int(data.tenant_id) if data.tenant_id is not None and private else 0
    if not private:
        existing = db.execute(select(IpamAutonomousSystem).where(IpamAutonomousSystem.asn == data.asn)).scalar_one_or_none()
        if existing is not None:
            raise ipam_error(409, "asn_exists", f"offentlig ASN {data.asn} finnes allerede")
    row = IpamAutonomousSystem(
        asn=data.asn,
        name=data.name.strip(),
        slug=_unique_as_slug(db, data.slug or f"as{data.asn}"),
        is_private=private,
        tenant_id=data.tenant_id,
        tenant_scope=scope,
        description=data.description,
    )
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ipam_error(409, "asn_exists", f"ASN {data.asn} finnes allerede i dette scopet")
    db.refresh(row)
    return row


def update_autonomous_system(
    db: Session,
    row: IpamAutonomousSystem,
    data: IpamAutonomousSystemUpdate,
) -> IpamAutonomousSystem:
    if data.tenant_id is not None:
        _require_tenant(db, data.tenant_id)
        row.tenant_id = data.tenant_id
        if row.is_private:
            row.tenant_scope = int(data.tenant_id)
    if data.name is not None:
        row.name = data.name.strip()
    if data.slug is not None:
        row.slug = _unique_as_slug(db, data.slug, exclude_id=row.id)
    if data.description is not None:
        row.description = data.description
    db.commit()
    db.refresh(row)
    return row


def delete_autonomous_system(db: Session, row: IpamAutonomousSystem) -> None:
    used = db.execute(select(IpamBgpSession.id).where(IpamBgpSession.local_as_id == row.id).limit(1)).scalar_one_or_none()
    if used is not None:
        raise ipam_error(409, "as_in_use", "AS brukes av en BGP-sesjon")
    inst = db.execute(select(IpamBgpInstance.id).where(IpamBgpInstance.local_as_id == row.id).limit(1)).scalar_one_or_none()
    if inst is not None:
        raise ipam_error(409, "as_in_use", "AS brukes av en BGP-instans")
    db.delete(row)
    db.commit()


def list_as_assignments(
    db: Session,
    *,
    site_id: int | None = None,
    as_id: int | None = None,
) -> list[IpamAsAssignment]:
    q = select(IpamAsAssignment).order_by(IpamAsAssignment.id)
    if site_id is not None:
        q = q.where(IpamAsAssignment.site_id == site_id)
    if as_id is not None:
        q = q.where(IpamAsAssignment.autonomous_system_id == as_id)
    return list(db.execute(q).scalars().all())


def get_as_assignment(db: Session, assignment_id: int) -> IpamAsAssignment | None:
    return db.get(IpamAsAssignment, assignment_id)


def create_as_assignment(db: Session, data: IpamAsAssignmentCreate) -> IpamAsAssignment:
    as_row = db.get(IpamAutonomousSystem, data.autonomous_system_id)
    if as_row is None:
        raise ValueError("AS ikke funnet")
    _require_site(db, data.site_id)
    vrf_scope = 0
    if data.vrf_id is not None:
        _require_vrf(db, data.vrf_id, site_id=data.site_id)
        vrf_scope = data.vrf_id
    row = IpamAsAssignment(
        autonomous_system_id=as_row.id,
        site_id=data.site_id,
        vrf_id=data.vrf_id,
        vrf_scope=vrf_scope,
    )
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ipam_error(409, "as_assignment_exists", "AS er allerede tilordnet dette rutingsdomenet")
    db.refresh(row)
    return row


def delete_as_assignment(db: Session, row: IpamAsAssignment) -> None:
    db.delete(row)
    db.commit()


def list_bgp_instances(
    db: Session,
    *,
    site_id: int | None = None,
    device_id: int | None = None,
) -> list[IpamBgpInstance]:
    q = select(IpamBgpInstance).order_by(IpamBgpInstance.slug)
    if site_id is not None:
        q = q.where(IpamBgpInstance.site_id == site_id)
    if device_id is not None:
        q = q.where(IpamBgpInstance.device_id == device_id)
    return list(db.execute(q).scalars().all())


def get_bgp_instance(db: Session, instance_id: int) -> IpamBgpInstance | None:
    return db.get(IpamBgpInstance, instance_id)


def get_bgp_instance_by_slug(db: Session, site_id: int, slug: str) -> IpamBgpInstance | None:
    return db.execute(
        select(IpamBgpInstance).where(IpamBgpInstance.site_id == site_id, IpamBgpInstance.slug == slug.strip().lower()),
    ).scalar_one_or_none()


def _unique_instance_slug(db: Session, site_id: int, desired: str, *, exclude_id: int | None = None) -> str:
    base = _slugify(desired)
    candidate = base
    n = 2
    while True:
        q = select(IpamBgpInstance.id).where(IpamBgpInstance.site_id == site_id, IpamBgpInstance.slug == candidate)
        if exclude_id is not None:
            q = q.where(IpamBgpInstance.id != exclude_id)
        if db.execute(q).scalar_one_or_none() is None:
            return candidate
        candidate = f"{base}-{n}"[:128]
        n += 1
        if n > 1000:
            raise ipam_error(400, "slug_exhausted", "kunne ikke lage unik slug")


def create_bgp_instance(db: Session, data: IpamBgpInstanceCreate) -> IpamBgpInstance:
    device = dcim_svc.get_device(db, data.device_id)
    if device is None:
        raise ValueError("enhet ikke funnet")
    site_id = dcim_svc.device_effective_site_id(db, device.id)
    if site_id is None:
        raise ipam_error(400, "device_site_required", "enheten må tilhøre en site før BGP-instans kan registreres")
    local = db.get(IpamAutonomousSystem, data.local_as_id)
    if local is None:
        raise ValueError("lokalt AS ikke funnet")
    vrf_scope = 0
    if data.vrf_id is not None:
        _require_vrf(db, data.vrf_id, site_id=int(site_id))
        vrf_scope = data.vrf_id
    existing = db.execute(
        select(IpamBgpInstance.id).where(
            IpamBgpInstance.device_id == device.id,
            IpamBgpInstance.local_as_id == local.id,
            IpamBgpInstance.vrf_scope == vrf_scope,
        ),
    ).scalar_one_or_none()
    if existing is not None:
        raise ipam_error(409, "bgp_instance_exists", "BGP-instans finnes allerede på denne enheten for AS/VRF")
    if data.slug:
        slug = data.slug.strip().lower()
        if get_bgp_instance_by_slug(db, int(site_id), slug) is not None:
            raise ipam_error(409, "bgp_instance_slug", "instans-slug finnes allerede")
    else:
        slug = _unique_instance_slug(db, int(site_id), data.name or f"bgp-{device.name}-as{local.asn}")
    name = (data.name or "").strip() or f"AS{local.asn} {device.name}"
    row = IpamBgpInstance(
        site_id=int(site_id),
        device_id=device.id,
        local_as_id=local.id,
        vrf_id=data.vrf_id,
        vrf_scope=vrf_scope,
        name=name,
        slug=slug,
        intent=data.intent,
        router_id=data.router_id,
        description=data.description,
    )
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ipam_error(409, "bgp_instance_exists", "BGP-instans finnes allerede på denne enheten for AS/VRF")
    db.refresh(row)
    return row


def delete_bgp_instance(db: Session, row: IpamBgpInstance) -> None:
    for s in list(
        db.execute(select(IpamBgpSession).where(IpamBgpSession.bgp_instance_id == row.id)).scalars().all()
    ):
        s.bgp_instance_id = None
    db.delete(row)
    db.commit()


def instance_to_read(db: Session, row: IpamBgpInstance) -> IpamBgpInstanceRead:
    device = db.get(DeviceInstance, row.device_id)
    local = db.get(IpamAutonomousSystem, row.local_as_id)
    vrf = db.get(IpamVrf, row.vrf_id) if row.vrf_id is not None else None
    return IpamBgpInstanceRead(
        id=row.id,
        site_id=row.site_id,
        device_id=row.device_id,
        device_name=device.name if device is not None else None,
        local_as_id=row.local_as_id,
        local_asn=local.asn if local is not None else None,
        vrf_id=row.vrf_id,
        vrf_name=vrf.name if vrf is not None else None,
        name=row.name,
        slug=row.slug,
        intent=row.intent,
        router_id=row.router_id,
        description=row.description,
        created_at=row.created_at,
    )


def _bind_session_to_instance(
    db: Session,
    data: IpamBgpSessionCreate,
) -> tuple[int, int, int | None, int | None, int | None]:
    inst = get_bgp_instance(db, data.bgp_instance_id) if data.bgp_instance_id is not None else None
    if data.bgp_instance_id is not None and inst is None:
        raise ValueError("BGP-instans ikke funnet")
    if inst is None:
        assert data.site_id is not None and data.local_as_id is not None
        return data.site_id, data.local_as_id, data.vrf_id, data.local_device_id, None
    if data.site_id is not None and data.site_id != inst.site_id:
        raise ipam_error(400, "bgp_instance_site", "sesjonens site stemmer ikke med BGP-instansen")
    if data.local_as_id is not None and data.local_as_id != inst.local_as_id:
        raise ipam_error(400, "bgp_instance_as", "sesjonens lokale AS stemmer ikke med BGP-instansen")
    if data.local_device_id is not None and data.local_device_id != inst.device_id:
        raise ipam_error(400, "bgp_instance_device", "sesjonens enhet stemmer ikke med BGP-instansen")
    provided = data.model_dump(exclude_unset=True)
    if "vrf_id" in provided and data.vrf_id != inst.vrf_id:
        raise ipam_error(400, "bgp_instance_vrf", "sesjonens VRF stemmer ikke med BGP-instansen")
    return inst.site_id, inst.local_as_id, inst.vrf_id, inst.device_id, inst.id


def list_bgp_sessions(db: Session, *, site_id: int | None = None) -> list[IpamBgpSession]:
    q = select(IpamBgpSession).order_by(IpamBgpSession.name)
    if site_id is not None:
        q = q.where(IpamBgpSession.site_id == site_id)
    return list(db.execute(q).scalars().all())


def get_bgp_session(db: Session, session_id: int) -> IpamBgpSession | None:
    return db.get(IpamBgpSession, session_id)


def _resolve_remote_asn(db: Session, data: IpamBgpSessionCreate) -> tuple[int | None, int]:
    if data.remote_as_id is not None:
        remote = db.get(IpamAutonomousSystem, data.remote_as_id)
        if remote is None:
            raise ValueError("fjern-AS ikke funnet")
        return remote.id, remote.asn
    if data.remote_asn is None:
        raise ipam_error(400, "remote_asn_required", "oppgi remote_as_id eller remote_asn")
    return None, data.remote_asn


def create_bgp_session(db: Session, data: IpamBgpSessionCreate) -> IpamBgpSession:
    site_id, local_as_id, vrf_id, local_device_id, instance_id = _bind_session_to_instance(db, data)
    _require_site(db, site_id)
    local = db.get(IpamAutonomousSystem, local_as_id)
    if local is None:
        raise ValueError("lokalt AS ikke funnet")
    vrf_scope = 0
    if vrf_id is not None:
        _require_vrf(db, vrf_id, site_id=site_id)
        vrf_scope = vrf_id
    if local_device_id is not None and db.get(DeviceInstance, local_device_id) is None:
        raise ValueError("enhet ikke funnet")
    if data.local_interface_id is not None:
        iface = db.get(DeviceInterface, data.local_interface_id)
        if iface is None:
            raise ValueError("grensesnitt ikke funnet")
        if local_device_id is not None and iface.device_id != local_device_id:
            raise ipam_error(400, "device_interface_mismatch", "grensesnittet tilhører en annen enhet")
    remote_as_id, remote_asn = _resolve_remote_asn(db, data)
    name = (data.name or "").strip() or f"AS{local.asn}-AS{remote_asn}"
    row = IpamBgpSession(
        site_id=site_id,
        bgp_instance_id=instance_id,
        local_as_id=local.id,
        remote_as_id=remote_as_id,
        remote_asn=remote_asn,
        peer_ip=data.peer_ip,
        vrf_id=vrf_id,
        vrf_scope=vrf_scope,
        name=name,
        slug=_unique_bgp_slug(db, site_id, data.slug or name),
        address_families=data.address_families,
        desired_status=data.desired_status,
        observed_status=data.observed_status,
        local_device_id=local_device_id,
        local_interface_id=data.local_interface_id,
        description=data.description,
    )
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ipam_error(409, "bgp_session_exists", "BGP-sesjon mot denne peer-IP-en finnes allerede")
    db.refresh(row)
    return row


def update_bgp_session(db: Session, row: IpamBgpSession, data: IpamBgpSessionUpdate) -> IpamBgpSession:
    if data.name is not None:
        row.name = data.name.strip() or row.name
    if data.slug is not None:
        row.slug = _unique_bgp_slug(db, row.site_id, data.slug, exclude_id=row.id)
    if data.peer_ip is not None:
        row.peer_ip = data.peer_ip
    if data.vrf_id is not None:
        _require_vrf(db, data.vrf_id, site_id=row.site_id)
        row.vrf_id = data.vrf_id
        row.vrf_scope = data.vrf_id
    if data.address_families is not None:
        row.address_families = data.address_families
    if data.desired_status is not None:
        row.desired_status = data.desired_status
    if data.observed_status is not None:
        row.observed_status = data.observed_status
    if data.remote_as_id is not None:
        remote = db.get(IpamAutonomousSystem, data.remote_as_id)
        if remote is None:
            raise ValueError("fjern-AS ikke funnet")
        row.remote_as_id = remote.id
        row.remote_asn = remote.asn
    elif data.remote_asn is not None:
        row.remote_asn = data.remote_asn
    if data.bgp_instance_id is not None:
        inst = get_bgp_instance(db, data.bgp_instance_id)
        if inst is None:
            raise ValueError("BGP-instans ikke funnet")
        if inst.site_id != row.site_id:
            raise ipam_error(400, "bgp_instance_site", "sesjonens site stemmer ikke med BGP-instansen")
        if inst.local_as_id != row.local_as_id:
            raise ipam_error(400, "bgp_instance_as", "sesjonens lokale AS stemmer ikke med BGP-instansen")
        if row.local_device_id is not None and row.local_device_id != inst.device_id:
            raise ipam_error(400, "bgp_instance_device", "sesjonens enhet stemmer ikke med BGP-instansen")
        if row.vrf_id != inst.vrf_id:
            raise ipam_error(400, "bgp_instance_vrf", "sesjonens VRF stemmer ikke med BGP-instansen")
        row.bgp_instance_id = inst.id
        row.local_device_id = inst.device_id
        row.vrf_id = inst.vrf_id
        row.vrf_scope = inst.vrf_scope
    if data.local_device_id is not None:
        if db.get(DeviceInstance, data.local_device_id) is None:
            raise ValueError("enhet ikke funnet")
        row.local_device_id = data.local_device_id
    if data.local_interface_id is not None:
        iface = db.get(DeviceInterface, data.local_interface_id)
        if iface is None:
            raise ValueError("grensesnitt ikke funnet")
        row.local_interface_id = iface.id
        row.local_device_id = iface.device_id
    if data.description is not None:
        row.description = data.description
    db.commit()
    db.refresh(row)
    return row


def delete_bgp_session(db: Session, row: IpamBgpSession) -> None:
    db.delete(row)
    db.commit()


def as_to_read(row: IpamAutonomousSystem) -> IpamAutonomousSystemRead:
    return IpamAutonomousSystemRead.model_validate(row)


def assignment_to_read(db: Session, row: IpamAsAssignment) -> IpamAsAssignmentRead:
    as_row = db.get(IpamAutonomousSystem, row.autonomous_system_id)
    site = db.get(Site, row.site_id)
    vrf = db.get(IpamVrf, row.vrf_id) if row.vrf_id is not None else None
    return IpamAsAssignmentRead.model_validate(row).model_copy(
        update={
            "asn": as_row.asn if as_row is not None else None,
            "as_name": as_row.name if as_row is not None else None,
            "site_name": site.name if site is not None else None,
            "vrf_name": vrf.name if vrf is not None else None,
        },
    )


def bgp_to_read(row: IpamBgpSession) -> IpamBgpSessionRead:
    return IpamBgpSessionRead.model_validate(row)
