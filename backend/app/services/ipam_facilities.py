"""IPAM: VRF, VLAN og samband (circuits)."""

from __future__ import annotations

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
    IpamVlanRead,
    IpamVrfCreate,
    IpamVrfRead,
)


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


# --- Circuits ---


def list_circuits(db: Session, *, tenant_id: int | None = None) -> list[IpamCircuit]:
    q = select(IpamCircuit).order_by(IpamCircuit.tenant_id, IpamCircuit.circuit_number)
    if tenant_id is not None:
        q = q.where(IpamCircuit.tenant_id == tenant_id)
    return list(db.execute(q).scalars().all())


def create_circuit(db: Session, data: IpamCircuitCreate) -> IpamCircuit:
    _require_tenant(db, data.tenant_id)
    row = IpamCircuit(
        tenant_id=data.tenant_id,
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

    existing = db.execute(
        select(IpamCircuitTermination).where(
            IpamCircuitTermination.circuit_id == circuit.id,
            IpamCircuitTermination.endpoint == data.endpoint,
        ),
    ).scalar_one_or_none()

    if existing is not None:
        existing.interface_id = data.interface_id
        existing.label = data.label.strip() if data.label else None
        db.commit()
        db.refresh(existing)
        return existing

    row = IpamCircuitTermination(
        circuit_id=circuit.id,
        endpoint=data.endpoint,
        interface_id=data.interface_id,
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


def vrf_to_read(row: IpamVrf) -> IpamVrfRead:
    return IpamVrfRead.model_validate(row)


def vlan_to_read(row: IpamVlan) -> IpamVlanRead:
    return IpamVlanRead.model_validate(row)


def circuit_to_read(row: IpamCircuit) -> IpamCircuitRead:
    return IpamCircuitRead.model_validate(row)


def termination_to_read(row: IpamCircuitTermination) -> IpamCircuitTerminationRead:
    return IpamCircuitTerminationRead.model_validate(row)
