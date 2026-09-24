"""IPAM: VRF, VLAN og samband (circuits)."""

from __future__ import annotations

import re

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.dcim import Cable, DeviceInstance, DeviceInterface, FiberStrand, Site
from app.models.ipam import (
    IpamCircuit,
    IpamCircuitGroup,
    IpamCircuitStrand,
    IpamCircuitTermination,
    IpamTunnelTransport,
    IpamVlan,
    IpamVlanGroup,
    IpamVrf,
)
from app.models.tenant import Tenant
from app.schemas.ipam import (
    CLASSIFY_CIRCUIT_TYPES,
    IpamCircuitClassify,
    IpamCircuitCreate,
    IpamCircuitGroupCreate,
    IpamCircuitGroupRead,
    IpamCircuitGroupUpdate,
    IpamCircuitRead,
    IpamCircuitStrandCreate,
    IpamCircuitStrandRead,
    IpamCircuitTerminationCreate,
    IpamCircuitTerminationRead,
    IpamCircuitUpdate,
    IpamVlanCreate,
    IpamVlanEnsure,
    IpamVlanGroupCreate,
    IpamVlanGroupRead,
    IpamVlanGroupUpdate,
    IpamVlanRead,
    IpamVlanUpdate,
    IpamVrfCreate,
    IpamVrfEnsure,
    IpamVrfRead,
    IpamVrfUpdate,
)

DEFAULT_VLAN_GROUP_SLUG = "default"
DEFAULT_VLAN_GROUP_NAME = "Default"
from app.services.ipam_errors import ipam_error


def _slugify(value: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", (value or "").strip().lower()).strip("-")
    return (s or "item")[:128]


def resolve_circuit_ownership(*, ownership: str | None, is_leased: bool | None) -> str | None:
    if ownership:
        return ownership
    if is_leased is True:
        return "leased"
    return None


def _unique_slug(db: Session, *, site_id: int, desired: str, kind: str, exclude_id: int | None = None) -> str:
    model = IpamVrf if kind == "vrf" else IpamVlanGroup if kind == "vlan_group" else IpamVlan
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
    from app.services.federation_guard import require_site_write

    require_site_write(db, site_id)
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
    from app.models.ipam import IpamVrfInstance, IpamVrfRouteTarget
    from app.services.federation_guard import require_site_write

    require_site_write(db, row.site_id)
    for bind in list(
        db.execute(select(IpamVrfRouteTarget).where(IpamVrfRouteTarget.vrf_id == row.id)).scalars().all()
    ):
        db.delete(bind)
    for inst in list(
        db.execute(select(IpamVrfInstance).where(IpamVrfInstance.vrf_id == row.id)).scalars().all()
    ):
        db.delete(inst)
    db.delete(row)
    db.commit()


def update_vrf(db: Session, row: IpamVrf, data: IpamVrfUpdate) -> IpamVrf:
    from app.services.federation_guard import require_site_write

    require_site_write(db, row.site_id)
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


# --- VLAN-grupper ---


def list_vlan_groups(db: Session, *, site_id: int | None = None) -> list[IpamVlanGroup]:
    q = select(IpamVlanGroup).order_by(IpamVlanGroup.site_id, IpamVlanGroup.name)
    if site_id is not None:
        q = q.where(IpamVlanGroup.site_id == site_id)
    return list(db.execute(q).scalars().all())


def get_vlan_group(db: Session, group_id: int) -> IpamVlanGroup | None:
    return db.get(IpamVlanGroup, group_id)


def get_or_create_default_vlan_group(db: Session, site_id: int) -> IpamVlanGroup:
    existing = db.execute(
        select(IpamVlanGroup).where(IpamVlanGroup.site_id == site_id, IpamVlanGroup.slug == DEFAULT_VLAN_GROUP_SLUG),
    ).scalar_one_or_none()
    if existing is not None:
        return existing
    row = IpamVlanGroup(
        site_id=site_id,
        name=DEFAULT_VLAN_GROUP_NAME,
        slug=DEFAULT_VLAN_GROUP_SLUG,
        description=None,
    )
    try:
        with db.begin_nested():
            db.add(row)
            db.flush()
    except IntegrityError:
        existing = db.execute(
            select(IpamVlanGroup).where(IpamVlanGroup.site_id == site_id, IpamVlanGroup.slug == DEFAULT_VLAN_GROUP_SLUG),
        ).scalar_one_or_none()
        if existing is None:
            raise
        return existing
    return row


def _resolve_vlan_group(db: Session, *, site_id: int, vlan_group_id: int | None) -> IpamVlanGroup:
    if vlan_group_id is None:
        return get_or_create_default_vlan_group(db, site_id)
    group = get_vlan_group(db, vlan_group_id)
    if group is None or group.site_id != site_id:
        raise ValueError("vlan-gruppe ikke funnet eller tilhører ikke samme site")
    return group


def create_vlan_group(db: Session, data: IpamVlanGroupCreate) -> IpamVlanGroup:
    _require_site(db, data.site_id)
    row = IpamVlanGroup(
        site_id=data.site_id,
        name=data.name.strip(),
        slug=_unique_slug(db, site_id=data.site_id, desired=data.slug or data.name, kind="vlan_group"),
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


def update_vlan_group(db: Session, row: IpamVlanGroup, data: IpamVlanGroupUpdate) -> IpamVlanGroup:
    from app.services.federation_guard import require_site_write

    require_site_write(db, row.site_id)
    patch = data.model_dump(exclude_unset=True)
    if not patch:
        raise ipam_error(400, "empty_patch", "ingen felter å oppdatere")
    if "name" in patch and patch["name"] is not None:
        row.name = str(patch["name"]).strip()
    if "slug" in patch and patch["slug"] is not None:
        row.slug = _unique_slug(
            db, site_id=row.site_id, desired=str(patch["slug"]), kind="vlan_group", exclude_id=row.id
        )
    if "description" in patch:
        row.description = patch["description"]
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ipam_error(409, "vlan_group_conflict", "VLAN-gruppe med samme navn eller slug finnes på denne siten") from None
    db.refresh(row)
    return row


def delete_vlan_group(db: Session, row: IpamVlanGroup) -> None:
    from app.services.federation_guard import require_site_write

    require_site_write(db, row.site_id)
    used = db.execute(select(IpamVlan.id).where(IpamVlan.vlan_group_id == row.id).limit(1)).scalar_one_or_none()
    if used is not None:
        raise ipam_error(409, "vlan_group_in_use", "VLAN-gruppen har VLAN — flytt eller slett dem først")
    db.delete(row)
    db.commit()


# --- VLAN ---


def list_vlans(
    db: Session,
    *,
    site_id: int | None = None,
    vlan_group_id: int | None = None,
) -> list[IpamVlan]:
    q = select(IpamVlan).order_by(IpamVlan.site_id, IpamVlan.vid, IpamVlan.id)
    if site_id is not None:
        q = q.where(IpamVlan.site_id == site_id)
    if vlan_group_id is not None:
        q = q.where(IpamVlan.vlan_group_id == vlan_group_id)
    return list(db.execute(q).scalars().all())


def create_vlan(db: Session, data: IpamVlanCreate) -> IpamVlan:
    _require_site(db, data.site_id)
    group = _resolve_vlan_group(db, site_id=data.site_id, vlan_group_id=data.vlan_group_id)
    if data.vrf_id is not None:
        vrf = get_vrf(db, data.vrf_id)
        if vrf is None or vrf.site_id != data.site_id:
            raise ValueError("vrf ikke funnet eller tilhører ikke samme site")

    if data.tenant_id is not None:
        _require_tenant(db, data.tenant_id)

    row = IpamVlan(
        site_id=data.site_id,
        vlan_group_id=group.id,
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
    from app.services.federation_guard import require_site_write

    require_site_write(db, row.site_id)
    db.delete(row)
    db.commit()


def update_vlan(db: Session, row: IpamVlan, data: IpamVlanUpdate) -> IpamVlan:
    from app.services.federation_guard import require_site_write

    require_site_write(db, row.site_id)
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
    if "vlan_group_id" in patch:
        group = _resolve_vlan_group(db, site_id=row.site_id, vlan_group_id=patch["vlan_group_id"])
        row.vlan_group_id = group.id
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
        raise ipam_error(409, "vlan_conflict", "VLAN-ID finnes allerede i gruppen, eller slug er opptatt på siten") from None
    db.refresh(row)
    return row


def ensure_vlan(db: Session, data: IpamVlanEnsure, *, update: bool = False) -> tuple[IpamVlan, bool]:
    group = _resolve_vlan_group(db, site_id=data.site_id, vlan_group_id=data.vlan_group_id)
    existing = db.execute(
        select(IpamVlan).where(IpamVlan.vlan_group_id == group.id, IpamVlan.vid == data.vid),
    ).scalar_one_or_none()
    if existing is not None:
        if update:
            existing = update_vlan(
                db,
                existing,
                IpamVlanUpdate(
                    name=data.name,
                    slug=data.slug,
                    vlan_group_id=group.id,
                    vrf_id=data.vrf_id,
                    description=data.description,
                    tenant_id=data.tenant_id,
                ),
            )
        return existing, False
    return create_vlan(db, data.model_copy(update={"vlan_group_id": group.id})), True


# --- Circuits ---


def circuit_needs_classification(row: IpamCircuit) -> bool:
    return row.layer is None and row.circuit_type in CLASSIFY_CIRCUIT_TYPES


def list_circuits(
    db: Session,
    *,
    tenant_id: int | None = None,
    site_id: int | None = None,
    layer: str | None = None,
    group_id: int | None = None,
    needs_classification: bool | None = None,
) -> list[IpamCircuit]:
    q = select(IpamCircuit).order_by(IpamCircuit.circuit_number)
    if tenant_id is not None:
        q = q.where(IpamCircuit.tenant_id == tenant_id)
    if site_id is not None:
        q = q.where((IpamCircuit.a_site_id == site_id) | (IpamCircuit.z_site_id == site_id))
    if layer is not None:
        q = q.where(IpamCircuit.layer == layer)
    if group_id is not None:
        q = q.where(IpamCircuit.group_id == group_id)
    rows = list(db.execute(q).scalars().all())
    if needs_classification is True:
        return [r for r in rows if circuit_needs_classification(r)]
    if needs_classification is False:
        return [r for r in rows if not circuit_needs_classification(r)]
    return rows


def _unique_group_slug(db: Session, tenant_scope: int, desired: str, *, exclude_id: int | None = None) -> str:
    base = _slugify(desired)
    candidate = base
    n = 2
    while True:
        q = select(IpamCircuitGroup.id).where(
            IpamCircuitGroup.tenant_scope == tenant_scope,
            IpamCircuitGroup.slug == candidate,
        )
        if exclude_id is not None:
            q = q.where(IpamCircuitGroup.id != exclude_id)
        if db.execute(q).scalar_one_or_none() is None:
            return candidate
        candidate = f"{base}-{n}"[:128]
        n += 1


def list_circuit_groups(db: Session, *, tenant_id: int | None = None) -> list[IpamCircuitGroup]:
    q = select(IpamCircuitGroup).order_by(IpamCircuitGroup.name)
    if tenant_id is not None:
        q = q.where(IpamCircuitGroup.tenant_id == tenant_id)
    return list(db.execute(q).scalars().all())


def get_circuit_group(db: Session, group_id: int) -> IpamCircuitGroup | None:
    return db.get(IpamCircuitGroup, group_id)


def get_circuit_group_by_slug(db: Session, slug: str, *, tenant_scope: int = 0) -> IpamCircuitGroup | None:
    return db.execute(
        select(IpamCircuitGroup).where(
            IpamCircuitGroup.tenant_scope == tenant_scope,
            IpamCircuitGroup.slug == slug,
        ),
    ).scalar_one_or_none()


def create_circuit_group(db: Session, data: IpamCircuitGroupCreate) -> IpamCircuitGroup:
    if data.tenant_id is not None:
        _require_tenant(db, data.tenant_id)
    tenant_scope = int(data.tenant_id) if data.tenant_id is not None else 0
    slug = _slugify(data.slug) if data.slug else _unique_group_slug(db, tenant_scope, data.name)
    row = IpamCircuitGroup(
        tenant_id=data.tenant_id,
        tenant_scope=tenant_scope,
        name=data.name.strip(),
        slug=slug,
        shared_risk=data.shared_risk.strip() if data.shared_risk else None,
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


def update_circuit_group(db: Session, row: IpamCircuitGroup, data: IpamCircuitGroupUpdate) -> IpamCircuitGroup:
    if data.tenant_id is not None:
        _require_tenant(db, data.tenant_id)
        row.tenant_id = data.tenant_id
        row.tenant_scope = int(data.tenant_id)
    if data.name is not None:
        row.name = data.name.strip()
    if data.slug is not None:
        row.slug = _slugify(data.slug)
    if data.shared_risk is not None:
        row.shared_risk = data.shared_risk.strip() if data.shared_risk else None
    if data.description is not None:
        row.description = data.description
    db.commit()
    db.refresh(row)
    return row


def delete_circuit_group(db: Session, row: IpamCircuitGroup) -> None:
    for circ in db.execute(select(IpamCircuit).where(IpamCircuit.group_id == row.id)).scalars().all():
        circ.group_id = None
    db.delete(row)
    db.commit()


def require_circuit_group_ref(
    db: Session,
    *,
    group_id: int | None,
    tenant_id: int | None,
) -> IpamCircuitGroup | None:
    if group_id is None:
        return None
    row = db.get(IpamCircuitGroup, group_id)
    if row is None:
        raise ipam_error(404, "circuit_group_not_found", "redundansgruppe ikke funnet")
    if row.tenant_id is not None and tenant_id is not None and row.tenant_id != tenant_id:
        raise ipam_error(400, "circuit_group_tenant_mismatch", "gruppen tilhører en annen tenant")
    return row


def circuit_group_to_read(row: IpamCircuitGroup) -> IpamCircuitGroupRead:
    return IpamCircuitGroupRead.model_validate(row)


def require_circuit_rates(*, capacity_mbps: int | None, cir_mbps: int | None) -> None:
    if capacity_mbps is not None and cir_mbps is not None and cir_mbps > capacity_mbps:
        raise ipam_error(
            400,
            "circuit_cir_exceeds_capacity",
            "CIR kan ikke være høyere enn kapasitet",
            capacity_mbps=capacity_mbps,
            cir_mbps=cir_mbps,
        )


def require_provider_circuit_id(
    db: Session,
    *,
    provider_id: int | None,
    provider_circuit_id: str | None,
    exclude_id: int | None = None,
) -> str | None:
    cid = provider_circuit_id.strip() if provider_circuit_id else None
    if not cid:
        return None
    if provider_id is None:
        return cid
    q = select(IpamCircuit.id).where(
        IpamCircuit.provider_id == provider_id,
        IpamCircuit.provider_circuit_id == cid,
    )
    if exclude_id is not None:
        q = q.where(IpamCircuit.id != exclude_id)
    if db.execute(q).scalar_one_or_none() is not None:
        raise ipam_error(409, "provider_circuit_id_conflict", "leverandørens circuit-ID finnes allerede")
    return cid


def create_circuit(db: Session, data: IpamCircuitCreate) -> IpamCircuit:
    from app.services.ipam_providers import require_contract_ref, require_provider_refs

    if data.tenant_id is not None:
        _require_tenant(db, data.tenant_id)
    if data.a_site_id is not None:
        _require_site(db, data.a_site_id)
    if data.z_site_id is not None:
        _require_site(db, data.z_site_id)
    provider_id = data.provider_id
    contract = require_contract_ref(db, contract_id=data.contract_id, provider_id=provider_id)
    if contract is not None and provider_id is None:
        provider_id = contract.provider_id
    require_provider_refs(db, provider_id=provider_id, provider_account_id=data.provider_account_id)
    tenant_id = data.tenant_id
    group = require_circuit_group_ref(db, group_id=data.group_id, tenant_id=tenant_id)
    if group is not None and tenant_id is None and group.tenant_id is not None:
        tenant_id = group.tenant_id
    require_circuit_rates(capacity_mbps=data.capacity_mbps, cir_mbps=data.cir_mbps)
    provider_circuit_id = require_provider_circuit_id(
        db,
        provider_id=provider_id,
        provider_circuit_id=data.provider_circuit_id,
    )
    row = IpamCircuit(
        tenant_id=tenant_id,
        tenant_scope=int(tenant_id) if tenant_id is not None else 0,
        a_site_id=data.a_site_id,
        z_site_id=data.z_site_id,
        circuit_number=data.circuit_number.strip(),
        name=data.name.strip(),
        description=data.description,
        circuit_type=data.circuit_type,
        layer=data.layer,
        service_type=data.service_type,
        medium=data.medium,
        operational_status=data.operational_status,
        ownership=resolve_circuit_ownership(ownership=data.ownership, is_leased=data.is_leased),
        is_leased=resolve_circuit_ownership(ownership=data.ownership, is_leased=data.is_leased) == "leased",
        provider_name=data.provider_name.strip() if data.provider_name else None,
        provider_id=provider_id,
        provider_account_id=data.provider_account_id,
        contract_id=data.contract_id,
        group_id=data.group_id,
        provider_circuit_id=provider_circuit_id,
        capacity_mbps=data.capacity_mbps,
        cir_mbps=data.cir_mbps,
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
    from app.services.ipam_providers import require_contract_ref, require_provider_refs

    if data.name is not None:
        row.name = data.name.strip()
    if data.description is not None:
        row.description = data.description
    if data.circuit_type is not None:
        row.circuit_type = data.circuit_type
    if data.layer is not None:
        row.layer = data.layer
    if data.service_type is not None:
        row.service_type = data.service_type
    if data.medium is not None:
        row.medium = data.medium
    if data.operational_status is not None:
        row.operational_status = data.operational_status
    if data.ownership is not None or data.is_leased is True:
        row.ownership = resolve_circuit_ownership(ownership=data.ownership, is_leased=data.is_leased)
        row.is_leased = row.ownership == "leased"
    if data.provider_name is not None:
        row.provider_name = data.provider_name.strip() if data.provider_name else None
    provider_id = data.provider_id if data.provider_id is not None else row.provider_id
    contract_id = data.contract_id if data.contract_id is not None else row.contract_id
    if data.contract_id is not None or data.provider_id is not None:
        contract = require_contract_ref(db, contract_id=contract_id, provider_id=provider_id)
        if contract is not None and provider_id is None:
            provider_id = contract.provider_id
    if data.provider_id is not None or data.provider_account_id is not None or data.contract_id is not None:
        require_provider_refs(
            db,
            provider_id=provider_id,
            provider_account_id=data.provider_account_id
            if data.provider_account_id is not None
            else row.provider_account_id,
        )
    if data.provider_id is not None or (data.contract_id is not None and row.provider_id is None):
        row.provider_id = provider_id
    if data.provider_account_id is not None:
        row.provider_account_id = data.provider_account_id
    if data.contract_id is not None:
        row.contract_id = data.contract_id
    if data.group_id is not None:
        tenant_for_group = data.tenant_id if data.tenant_id is not None else row.tenant_id
        require_circuit_group_ref(db, group_id=data.group_id, tenant_id=tenant_for_group)
        row.group_id = data.group_id
    if data.capacity_mbps is not None or data.cir_mbps is not None:
        require_circuit_rates(
            capacity_mbps=data.capacity_mbps if data.capacity_mbps is not None else row.capacity_mbps,
            cir_mbps=data.cir_mbps if data.cir_mbps is not None else row.cir_mbps,
        )
    if data.capacity_mbps is not None:
        row.capacity_mbps = data.capacity_mbps
    if data.cir_mbps is not None:
        row.cir_mbps = data.cir_mbps
    if data.provider_circuit_id is not None:
        row.provider_circuit_id = require_provider_circuit_id(
            db,
            provider_id=provider_id,
            provider_circuit_id=data.provider_circuit_id,
            exclude_id=row.id,
        )
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


def classify_circuit(db: Session, row: IpamCircuit, data: IpamCircuitClassify):
    from app.services import ipam_vpn as vpn_svc

    # circuit_type skrives aldri her — bare layer.
    row.layer = data.layer
    db.commit()
    db.refresh(row)
    vpn = None
    if data.layer == "overlay" and data.create_vpn:
        vpn = vpn_svc.ensure_vpn_from_circuit(db, row)
    return row, vpn


def delete_circuit(db: Session, row: IpamCircuit) -> None:
    for b in list(db.execute(select(IpamCircuitStrand).where(IpamCircuitStrand.circuit_id == row.id)).scalars().all()):
        db.delete(b)
    for b in list(db.execute(select(IpamTunnelTransport).where(IpamTunnelTransport.circuit_id == row.id)).scalars().all()):
        db.delete(b)
    db.delete(row)
    db.commit()


def list_circuit_strands(db: Session, circuit_id: int) -> list[IpamCircuitStrand]:
    return list(
        db.execute(select(IpamCircuitStrand).where(IpamCircuitStrand.circuit_id == circuit_id).order_by(IpamCircuitStrand.id)).scalars().all()
    )


def get_circuit_strand(db: Session, bind_id: int) -> IpamCircuitStrand | None:
    return db.get(IpamCircuitStrand, bind_id)


def get_circuit_strand_by_strand(db: Session, strand_id: int) -> IpamCircuitStrand | None:
    return db.execute(select(IpamCircuitStrand).where(IpamCircuitStrand.strand_id == strand_id)).scalar_one_or_none()


def create_circuit_strand(db: Session, circuit: IpamCircuit, data: IpamCircuitStrandCreate) -> IpamCircuitStrand:
    strand = db.get(FiberStrand, data.strand_id)
    if strand is None:
        raise ipam_error(404, "fiber_strand_not_found", "fiberstreng ikke funnet")
    if get_circuit_strand_by_strand(db, strand.id) is not None:
        raise ipam_error(409, "circuit_strand_taken", "fiberstrengen er allerede knyttet til et samband")
    row = IpamCircuitStrand(circuit_id=circuit.id, strand_id=strand.id)
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ipam_error(409, "circuit_strand_taken", "fiberstrengen er allerede knyttet til et samband")
    db.refresh(row)
    return row


def delete_circuit_strand(db: Session, row: IpamCircuitStrand) -> None:
    db.delete(row)
    db.commit()


def circuit_strand_to_read(db: Session, row: IpamCircuitStrand) -> IpamCircuitStrandRead:
    strand = db.get(FiberStrand, row.strand_id)
    cable = db.get(Cable, strand.cable_id) if strand is not None else None
    return IpamCircuitStrandRead(
        id=row.id,
        circuit_id=row.circuit_id,
        strand_id=row.strand_id,
        cable_id=cable.id if cable is not None else (strand.cable_id if strand is not None else 0),
        cable_slug=cable.slug if cable is not None else "",
        position=strand.position if strand is not None else 0,
        label=strand.label if strand is not None else None,
        status=strand.status if strand is not None else "unused",
        created_at=row.created_at,
    )


def list_circuit_terminations(db: Session, circuit_id: int) -> list[IpamCircuitTermination]:
    q = (
        select(IpamCircuitTermination)
        .where(IpamCircuitTermination.circuit_id == circuit_id)
        .order_by(IpamCircuitTermination.endpoint)
    )
    return list(db.execute(q).scalars().all())


def _resolve_term_device_iface(
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


def upsert_circuit_termination(
    db: Session,
    circuit: IpamCircuit,
    data: IpamCircuitTerminationCreate,
) -> IpamCircuitTermination:
    device_id, interface_id = _resolve_term_device_iface(
        db,
        device_id=data.device_id,
        interface_id=data.interface_id,
    )
    if data.kind in {"unknown", "provider-network"} and (device_id is not None or interface_id is not None):
        raise ipam_error(400, "circuit_term_kind", "ukjent ende eller leverandørnett kan ikke peke på lokal enhet")
    if data.site_id is not None:
        _require_site(db, data.site_id)

    existing = db.execute(
        select(IpamCircuitTermination).where(
            IpamCircuitTermination.circuit_id == circuit.id,
            IpamCircuitTermination.endpoint == data.endpoint,
        ),
    ).scalar_one_or_none()

    if existing is not None:
        existing.kind = data.kind
        existing.device_id = device_id
        existing.interface_id = interface_id
        existing.site_id = data.site_id
        existing.label = data.label.strip() if data.label else None
        db.commit()
        db.refresh(existing)
        return existing

    row = IpamCircuitTermination(
        circuit_id=circuit.id,
        endpoint=data.endpoint,
        kind=data.kind,
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


def vrf_to_read(row: IpamVrf, *, created: bool | None = None) -> IpamVrfRead:
    return IpamVrfRead.model_validate(row).model_copy(update={"created": created})


def vlan_group_to_read(row: IpamVlanGroup) -> IpamVlanGroupRead:
    return IpamVlanGroupRead.model_validate(row)


def vlan_to_read(row: IpamVlan, *, created: bool | None = None) -> IpamVlanRead:
    return IpamVlanRead.model_validate(row).model_copy(update={"created": created})


def circuit_to_read(row: IpamCircuit) -> IpamCircuitRead:
    return IpamCircuitRead.model_validate(row).model_copy(
        update={"needs_classification": circuit_needs_classification(row)},
    )


def termination_to_read(db: Session, row: IpamCircuitTermination) -> IpamCircuitTerminationRead:
    device_name = None
    interface_name = None
    device_id = row.device_id
    if row.interface_id is not None:
        iface = db.get(DeviceInterface, row.interface_id)
        if iface is not None:
            interface_name = iface.name
            if device_id is None:
                device_id = iface.device_id
    if device_id is not None:
        device = db.get(DeviceInstance, device_id)
        if device is not None:
            device_name = device.name
    return IpamCircuitTerminationRead.model_validate(row).model_copy(
        update={"device_id": device_id, "device_name": device_name, "interface_name": interface_name},
    )
