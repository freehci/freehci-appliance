"""IPAM: VRF, VLAN og samband (circuits)."""

from __future__ import annotations

import re

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.dcim import DeviceInterface, Site
from app.models.ipam import IpamCircuit, IpamCircuitTermination, IpamVlan, IpamVrf
from app.models.tenant import Tenant
from app.schemas.ipam import (
    IpamCircuitCreate,
    IpamCircuitRead,
    IpamCircuitTerminationCreate,
    IpamCircuitTerminationRead,
    IpamCircuitUpdate,
    IpamVlanCreate,
    IpamVlanEnsure,
    IpamVlanRead,
    IpamVlanUpdate,
    IpamVrfCreate,
    IpamVrfEnsure,
    IpamVrfRead,
    IpamVrfUpdate,
)
from app.services.ipam_errors import ipam_error


def _slugify(value: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", (value or "").strip().lower()).strip("-")
    return (s or "item")[:128]


def _unique_slug(db: Session, *, site_id: int, desired: str, kind: str, exclude_id: int | None = None) -> str:
    model = IpamVrf if kind == "vrf" else IpamVlan
    base = _slugify(desired)
    candidate = base
    n = 2
    while True:
        q = select(model.id).where(model.site_id == site_id, model.slug == candidate)
        if exclude_id is not None:
            q = q.where(model.id != exclude_id)
        if db.execute(q).scalar_one_or_none() is None:
            return candidate
        suffix = f"-{n}"
        candidate = f"{base[: 128 - len(suffix)]}{suffix}"
        n += 1
        if n > 1000:
            raise ipam_error(400, "slug_exhausted", "kunne ikke lage unik slug")


def _require_site(db: Session, site_id: int) -> Site:
    s = db.get(Site, site_id)
    if s is None:
        raise ValueError("site ikke funnet")
    return s


def _require_tenant(db: Session, tenant_id: int) -> Tenant:
    t = db.get(Tenant, tenant_id)
    if t is None:
        raise ValueError("tenant ikke funnet")
    return t


# --- VRF ---


def list_vrfs(db: Session, *, site_id: int | None = None) -> list[IpamVrf]:
    q = select(IpamVrf).order_by(IpamVrf.site_id, IpamVrf.name)
    if site_id is not None:
        q = q.where(IpamVrf.site_id == site_id)
    return list(db.execute(q).scalars().all())


def create_vrf(db: Session, data: IpamVrfCreate) -> IpamVrf:
    _require_site(db, data.site_id)
    row = IpamVrf(
        site_id=data.site_id,
        name=data.name.strip(),
        slug=_unique_slug(db, site_id=data.site_id, desired=data.slug or data.name, kind="vrf"),
        route_distinguisher=data.route_distinguisher.strip() if data.route_distinguisher else None,
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


def get_vrf(db: Session, vrf_id: int) -> IpamVrf | None:
    return db.get(IpamVrf, vrf_id)


def delete_vrf(db: Session, row: IpamVrf) -> None:
    db.delete(row)
    db.commit()


def update_vrf(db: Session, row: IpamVrf, data: IpamVrfUpdate) -> IpamVrf:
    patch = data.model_dump(exclude_unset=True)
    if not patch:
        raise ipam_error(400, "empty_patch", "ingen felter å oppdatere")
    if "name" in patch and patch["name"] is not None:
        row.name = str(patch["name"]).strip()
    if "slug" in patch and patch["slug"] is not None:
        row.slug = _unique_slug(db, site_id=row.site_id, desired=str(patch["slug"]), kind="vrf", exclude_id=row.id)
    if "route_distinguisher" in patch:
        v = patch["route_distinguisher"]
        row.route_distinguisher = v.strip() if isinstance(v, str) and v.strip() else None
    if "description" in patch:
        row.description = patch["description"]
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ipam_error(409, "vrf_conflict", "VRF med samme navn eller slug finnes på denne siten") from None
    db.refresh(row)
    return row


def ensure_vrf(db: Session, data: IpamVrfEnsure, *, update: bool = False) -> tuple[IpamVrf, bool]:
    existing = db.execute(
        select(IpamVrf).where(IpamVrf.site_id == data.site_id, IpamVrf.name == data.name.strip()),
    ).scalar_one_or_none()
    if existing is None and data.slug:
        existing = db.execute(
            select(IpamVrf).where(IpamVrf.site_id == data.site_id, IpamVrf.slug == _slugify(data.slug)),
        ).scalar_one_or_none()
    if existing is not None:
        if update:
            existing = update_vrf(
                db,
                existing,
                IpamVrfUpdate(
                    name=data.name,
                    slug=data.slug,
                    route_distinguisher=data.route_distinguisher,
                    description=data.description,
                ),
            )
        return existing, False
    return create_vrf(db, data), True


# --- VLAN ---


def list_vlans(db: Session, *, site_id: int | None = None) -> list[IpamVlan]:
    q = select(IpamVlan).order_by(IpamVlan.site_id, IpamVlan.vid)
    if site_id is not None:
        q = q.where(IpamVlan.site_id == site_id)
    return list(db.execute(q).scalars().all())


def create_vlan(db: Session, data: IpamVlanCreate) -> IpamVlan:
    _require_site(db, data.site_id)
    if data.vrf_id is not None:
        vrf = get_vrf(db, data.vrf_id)
        if vrf is None or vrf.site_id != data.site_id:
            raise ValueError("vrf ikke funnet eller tilhører ikke samme site")

    if data.tenant_id is not None:
        _require_tenant(db, data.tenant_id)

    row = IpamVlan(
        site_id=data.site_id,
        tenant_id=data.tenant_id,
        vid=data.vid,
        name=data.name.strip(),
        slug=_unique_slug(db, site_id=data.site_id, desired=data.slug or data.name or f"vlan-{data.vid}", kind="vlan"),
        description=data.description,
        vrf_id=data.vrf_id,
    )
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise
    db.refresh(row)
    return row


def get_vlan(db: Session, vlan_id: int) -> IpamVlan | None:
    return db.get(IpamVlan, vlan_id)


def delete_vlan(db: Session, row: IpamVlan) -> None:
    db.delete(row)
    db.commit()


def update_vlan(db: Session, row: IpamVlan, data: IpamVlanUpdate) -> IpamVlan:
    patch = data.model_dump(exclude_unset=True)
    if not patch:
        raise ipam_error(400, "empty_patch", "ingen felter å oppdatere")
    if "name" in patch and patch["name"] is not None:
        row.name = str(patch["name"]).strip()
    if "slug" in patch and patch["slug"] is not None:
        row.slug = _unique_slug(db, site_id=row.site_id, desired=str(patch["slug"]), kind="vlan", exclude_id=row.id)
    if "description" in patch:
        row.description = patch["description"]
    if "tenant_id" in patch:
        tid = patch["tenant_id"]
        if tid is not None:
            _require_tenant(db, int(tid))
        row.tenant_id = tid
    if "vrf_id" in patch:
        vrf_id = patch["vrf_id"]
        if vrf_id is None:
            row.vrf_id = None
        else:
            vrf = get_vrf(db, int(vrf_id))
            if vrf is None or vrf.site_id != row.site_id:
                raise ValueError("vrf ikke funnet eller tilhører ikke samme site")
            row.vrf_id = int(vrf_id)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ipam_error(409, "vlan_conflict", "VLAN-ID eller slug finnes allerede på denne siten") from None
    db.refresh(row)
    return row


def ensure_vlan(db: Session, data: IpamVlanEnsure, *, update: bool = False) -> tuple[IpamVlan, bool]:
    existing = db.execute(
        select(IpamVlan).where(IpamVlan.site_id == data.site_id, IpamVlan.vid == data.vid),
    ).scalar_one_or_none()
    if existing is not None:
        if update:
            existing = update_vlan(
                db,
                existing,
                IpamVlanUpdate(
                    name=data.name,
                    slug=data.slug,
                    vrf_id=data.vrf_id,
                    description=data.description,
                    tenant_id=data.tenant_id,
                ),
            )
        return existing, False
    return create_vlan(db, data), True


# --- Circuits ---


def list_circuits(
    db: Session,
    *,
    tenant_id: int | None = None,
    site_id: int | None = None,
) -> list[IpamCircuit]:
    q = select(IpamCircuit).order_by(IpamCircuit.circuit_number)
    if tenant_id is not None:
        q = q.where(IpamCircuit.tenant_id == tenant_id)
    if site_id is not None:
        q = q.where((IpamCircuit.a_site_id == site_id) | (IpamCircuit.z_site_id == site_id))
    return list(db.execute(q).scalars().all())


def create_circuit(db: Session, data: IpamCircuitCreate) -> IpamCircuit:
    if data.tenant_id is not None:
        _require_tenant(db, data.tenant_id)
    if data.a_site_id is not None:
        _require_site(db, data.a_site_id)
    if data.z_site_id is not None:
        _require_site(db, data.z_site_id)
    row = IpamCircuit(
        tenant_id=data.tenant_id,
        tenant_scope=int(data.tenant_id) if data.tenant_id is not None else 0,
        a_site_id=data.a_site_id,
        z_site_id=data.z_site_id,
        circuit_number=data.circuit_number.strip(),
        name=data.name.strip(),
        description=data.description,
        circuit_type=data.circuit_type,
        is_leased=data.is_leased,
        provider_name=data.provider_name.strip() if data.provider_name else None,
        established_on=data.established_on,
        contract_end_on=data.contract_end_on,
    )
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise
    db.refresh(row)
    return row


def get_circuit(db: Session, circuit_id: int) -> IpamCircuit | None:
    return db.get(IpamCircuit, circuit_id)


def update_circuit(db: Session, row: IpamCircuit, data: IpamCircuitUpdate) -> IpamCircuit:
    if data.name is not None:
        row.name = data.name.strip()
    if data.description is not None:
        row.description = data.description
    if data.circuit_type is not None:
        row.circuit_type = data.circuit_type
    if data.is_leased is not None:
        row.is_leased = data.is_leased
    if data.provider_name is not None:
        row.provider_name = data.provider_name.strip() if data.provider_name else None
    if data.established_on is not None:
        row.established_on = data.established_on
    if data.contract_end_on is not None:
        row.contract_end_on = data.contract_end_on
    if data.tenant_id is not None:
        _require_tenant(db, data.tenant_id)
        row.tenant_id = data.tenant_id
        row.tenant_scope = int(data.tenant_id)
    if data.a_site_id is not None:
        _require_site(db, data.a_site_id)
        row.a_site_id = data.a_site_id
    if data.z_site_id is not None:
        _require_site(db, data.z_site_id)
        row.z_site_id = data.z_site_id
    db.commit()
    db.refresh(row)
    return row


def delete_circuit(db: Session, row: IpamCircuit) -> None:
    db.delete(row)
    db.commit()


def list_circuit_terminations(db: Session, circuit_id: int) -> list[IpamCircuitTermination]:
    q = (
        select(IpamCircuitTermination)
        .where(IpamCircuitTermination.circuit_id == circuit_id)
        .order_by(IpamCircuitTermination.endpoint)
    )
    return list(db.execute(q).scalars().all())


def upsert_circuit_termination(
    db: Session,
    circuit: IpamCircuit,
    data: IpamCircuitTerminationCreate,
) -> IpamCircuitTermination:
    if data.interface_id is not None:
        iface = db.get(DeviceInterface, data.interface_id)
        if iface is None:
            raise ValueError("grensesnitt ikke funnet")
    if data.site_id is not None:
        _require_site(db, data.site_id)

    existing = db.execute(
        select(IpamCircuitTermination).where(
            IpamCircuitTermination.circuit_id == circuit.id,
            IpamCircuitTermination.endpoint == data.endpoint,
        ),
    ).scalar_one_or_none()

    if existing is not None:
        existing.interface_id = data.interface_id
        existing.site_id = data.site_id
        existing.label = data.label.strip() if data.label else None
        db.commit()
        db.refresh(existing)
        return existing

    row = IpamCircuitTermination(
        circuit_id=circuit.id,
        endpoint=data.endpoint,
        interface_id=data.interface_id,
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


def vrf_to_read(row: IpamVrf, *, created: bool | None = None) -> IpamVrfRead:
    return IpamVrfRead.model_validate(row).model_copy(update={"created": created})


def vlan_to_read(row: IpamVlan, *, created: bool | None = None) -> IpamVlanRead:
    return IpamVlanRead.model_validate(row).model_copy(update={"created": created})


def circuit_to_read(row: IpamCircuit) -> IpamCircuitRead:
    return IpamCircuitRead.model_validate(row)


def termination_to_read(row: IpamCircuitTermination) -> IpamCircuitTerminationRead:
    return IpamCircuitTerminationRead.model_validate(row)
