"""Versjonert katalog og ærlig device_instance-deployment (uten OS-install)."""

from __future__ import annotations

import datetime as dt
import re

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.models.catalog import (
    ServiceDeployment,
    ServiceDeploymentStep,
    ServiceInstance,
    ServiceTemplate,
    ServiceTemplateVersion,
)
from app.models.dcim import DeviceInstance
from app.models.ipam import IpamIpv4Prefix
from app.schemas.catalog import (
    ServiceDeploymentCreate,
    ServiceDeploymentRead,
    ServiceDeploymentStepRead,
    ServiceInstanceRead,
    ServiceTemplateCreate,
    ServiceTemplateRead,
    ServiceTemplateSpec,
    ServiceTemplateVersionCreate,
    ServiceTemplateVersionRead,
)
from app.schemas.ipam import Ipv4AddressRequest
from app.services import dcim as dcim_svc
from app.services import ipam as ipam_svc
from app.services.ipam_address import request_ipv4_address


def _slugify(value: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", (value or "").strip().lower()).strip("-")
    return (s or "item")[:128]


def _spec_dict(spec: ServiceTemplateSpec) -> dict:
    return spec.model_dump()


def version_to_read(row: ServiceTemplateVersion) -> ServiceTemplateVersionRead:
    return ServiceTemplateVersionRead.model_validate(row)


def _instance_for_deployment(db: Session, deployment_id: int) -> ServiceInstance | None:
    return db.execute(
        select(ServiceInstance).where(ServiceInstance.deployment_id == deployment_id)
    ).scalar_one_or_none()


def template_to_read(row: ServiceTemplate) -> ServiceTemplateRead:
    versions = sorted(row.versions, key=lambda v: v.id)
    return ServiceTemplateRead(
        id=row.id,
        name=row.name,
        slug=row.slug,
        description=row.description,
        created_at=row.created_at,
        versions=[version_to_read(v) for v in versions],
    )


def instance_to_read(row: ServiceInstance) -> ServiceInstanceRead:
    return ServiceInstanceRead.model_validate(row)


def deployment_to_read(db: Session, row: ServiceDeployment) -> ServiceDeploymentRead:
    inst = _instance_for_deployment(db, row.id)
    return ServiceDeploymentRead(
        id=row.id,
        template_version_id=row.template_version_id,
        device_id=row.device_id,
        ipv4_prefix_id=row.ipv4_prefix_id,
        status=row.status,
        plan_json=row.plan_json,
        created_at=row.created_at,
        started_at=row.started_at,
        finished_at=row.finished_at,
        steps=[ServiceDeploymentStepRead.model_validate(s) for s in row.steps],
        instance=instance_to_read(inst) if inst is not None else None,
    )


def _load_template(db: Session, template_id: int) -> ServiceTemplate | None:
    return db.execute(
        select(ServiceTemplate)
        .options(selectinload(ServiceTemplate.versions))
        .where(ServiceTemplate.id == template_id)
    ).scalar_one_or_none()


def list_templates(db: Session) -> list[ServiceTemplate]:
    return list(
        db.execute(
            select(ServiceTemplate)
            .options(selectinload(ServiceTemplate.versions))
            .order_by(ServiceTemplate.name)
        ).scalars().all()
    )


def get_template(db: Session, template_id: int) -> ServiceTemplate | None:
    return _load_template(db, template_id)


def create_template(db: Session, data: ServiceTemplateCreate) -> ServiceTemplate:
    slug = _slugify(data.slug or data.name)
    if db.execute(select(ServiceTemplate.id).where(ServiceTemplate.slug == slug)).scalar_one_or_none():
        raise HTTPException(status_code=409, detail="mal-slug finnes allerede")
    row = ServiceTemplate(
        name=data.name.strip(),
        slug=slug,
        description=(data.description or "").strip() or None,
    )
    db.add(row)
    db.flush()
    ver = ServiceTemplateVersion(template_id=row.id, version="1.0.0", spec=_spec_dict(data.spec))
    db.add(ver)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="mal-slug finnes allerede")
    loaded = _load_template(db, row.id)
    assert loaded is not None
    return loaded


def add_version(db: Session, template: ServiceTemplate, data: ServiceTemplateVersionCreate) -> ServiceTemplateVersion:
    version = data.version.strip()
    exists = db.execute(
        select(ServiceTemplateVersion.id).where(
            ServiceTemplateVersion.template_id == template.id,
            ServiceTemplateVersion.version == version,
        )
    ).scalar_one_or_none()
    if exists:
        raise HTTPException(status_code=409, detail="versjonen finnes allerede for denne malen")
    row = ServiceTemplateVersion(template_id=template.id, version=version, spec=_spec_dict(data.spec))
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="versjonen finnes allerede for denne malen")
    db.refresh(row)
    return row


def get_version(db: Session, version_id: int) -> ServiceTemplateVersion | None:
    return db.get(ServiceTemplateVersion, version_id)


def _exc_detail(exc: HTTPException) -> str:
    d = exc.detail
    if isinstance(d, dict):
        return str(d.get("detail") or d.get("code") or d)
    return str(d)


def build_plan(
    db: Session,
    version: ServiceTemplateVersion,
    device: DeviceInstance,
    prefix_id: int | None,
) -> dict:
    template = db.get(ServiceTemplate, version.template_id)
    spec = version.spec if isinstance(version.spec, dict) else {}
    reserve = bool(spec.get("reserve_ipv4"))
    site_id = dcim_svc.device_effective_site_id(db, device.id)
    blockers: list[str] = []
    prefix_info: dict | None = None

    if reserve:
        if prefix_id is None:
            blockers.append("prefix_required")
        else:
            pfx = db.get(IpamIpv4Prefix, prefix_id)
            if pfx is None:
                blockers.append("prefix_not_found")
            else:
                read = ipam_svc.ipv4_prefix_read(db, pfx)
                prefix_info = {
                    "id": pfx.id,
                    "cidr": pfx.cidr,
                    "name": pfx.name,
                    "site_id": pfx.site_id,
                    "used_count": read.used_count,
                    "usable_hosts": read.usable_hosts,
                }
                if site_id is not None and int(site_id) != int(pfx.site_id):
                    blockers.append("prefix_site_mismatch")
                if read.usable_hosts <= read.used_count:
                    blockers.append("prefix_exhausted")
    elif prefix_id is not None:
        pfx = db.get(IpamIpv4Prefix, prefix_id)
        if pfx is None:
            blockers.append("prefix_not_found")
        else:
            read = ipam_svc.ipv4_prefix_read(db, pfx)
            prefix_info = {
                "id": pfx.id,
                "cidr": pfx.cidr,
                "name": pfx.name,
                "site_id": pfx.site_id,
                "used_count": read.used_count,
                "usable_hosts": read.usable_hosts,
            }

    return {
        "kind": spec.get("kind") or "device_instance",
        "template": {
            "id": template.id if template else version.template_id,
            "name": template.name if template else None,
            "version": version.version,
        },
        "device": {"id": device.id, "name": device.name, "site_id": site_id},
        "reserve_ipv4": reserve,
        "prefix": prefix_info,
        "blockers": blockers,
        "can_run": len(blockers) == 0,
        "notes": [
            "Registrerer en tjenesteinstans på en eksisterende enhet.",
            "Installerer ikke OS, hypervisor eller cluster.",
        ],
    }


def list_deployments(db: Session) -> list[ServiceDeployment]:
    return list(
        db.execute(
            select(ServiceDeployment)
            .options(selectinload(ServiceDeployment.steps))
            .order_by(ServiceDeployment.id.desc())
        ).scalars().all()
    )


def get_deployment(db: Session, deployment_id: int) -> ServiceDeployment | None:
    return db.execute(
        select(ServiceDeployment)
        .options(selectinload(ServiceDeployment.steps))
        .where(ServiceDeployment.id == deployment_id)
    ).scalar_one_or_none()


def create_deployment(db: Session, data: ServiceDeploymentCreate) -> ServiceDeployment:
    version = get_version(db, data.template_version_id)
    if version is None:
        raise HTTPException(status_code=404, detail="malversjon ikke funnet")
    device = dcim_svc.get_device(db, data.device_id)
    if device is None:
        raise HTTPException(status_code=404, detail="enhet ikke funnet")
    plan = build_plan(db, version, device, data.ipv4_prefix_id)
    if data.name and data.name.strip():
        plan["requested_name"] = data.name.strip()
    row = ServiceDeployment(
        template_version_id=version.id,
        device_id=device.id,
        ipv4_prefix_id=data.ipv4_prefix_id,
        status="planned",
        plan_json=plan,
    )
    db.add(row)
    db.commit()
    loaded = get_deployment(db, row.id)
    assert loaded is not None
    return loaded


def _add_step(db: Session, deployment: ServiceDeployment, name: str, status: str, detail: str | None) -> None:
    db.add(
        ServiceDeploymentStep(
            deployment_id=deployment.id,
            name=name,
            status=status,
            detail=detail,
        )
    )


def run_deployment(db: Session, row: ServiceDeployment) -> ServiceDeployment:
    if row.status != "planned":
        raise HTTPException(status_code=409, detail="deployment er allerede kjørt")
    version = get_version(db, row.template_version_id)
    if version is None:
        raise HTTPException(status_code=404, detail="malversjon ikke funnet")
    device = dcim_svc.get_device(db, row.device_id)
    if device is None:
        raise HTTPException(status_code=404, detail="enhet ikke funnet")

    plan = build_plan(db, version, device, row.ipv4_prefix_id)
    row.plan_json = plan
    if not plan["can_run"]:
        db.commit()
        raise HTTPException(status_code=400, detail={"code": "cannot_run", "blockers": plan["blockers"]})

    now = dt.datetime.now(dt.timezone.utc)
    row.status = "running"
    row.started_at = now
    db.commit()

    _add_step(db, row, "validate_device", "ok", f"enhet {device.name} #{device.id}")
    db.commit()

    address_id: int | None = None
    spec = version.spec if isinstance(version.spec, dict) else {}
    if spec.get("reserve_ipv4"):
        if row.ipv4_prefix_id is None:
            row.status = "failed"
            row.finished_at = dt.datetime.now(dt.timezone.utc)
            _add_step(db, row, "reserve_ipv4", "failed", "prefix_required")
            db.commit()
            loaded = get_deployment(db, row.id)
            assert loaded is not None
            return loaded
        try:
            addr = request_ipv4_address(
                db,
                Ipv4AddressRequest(
                    ipv4_prefix_id=row.ipv4_prefix_id,
                    mode="reserve",
                    device_id=device.id,
                    note=f"service catalog deployment {row.id}",
                ),
            )
            address_id = addr.id
            _add_step(db, row, "reserve_ipv4", "ok", addr.address)
            db.commit()
        except HTTPException as exc:
            row.status = "failed"
            row.finished_at = dt.datetime.now(dt.timezone.utc)
            _add_step(db, row, "reserve_ipv4", "failed", _exc_detail(exc))
            db.commit()
            loaded = get_deployment(db, row.id)
            assert loaded is not None
            return loaded
    else:
        _add_step(db, row, "reserve_ipv4", "skipped", "malen ber ikke om IPv4-reservasjon")
        db.commit()

    template = db.get(ServiceTemplate, version.template_id)
    requested = (row.plan_json or {}).get("requested_name") if isinstance(row.plan_json, dict) else None
    name = str(requested).strip() if requested else f"{template.name if template else 'service'} on {device.name}"
    slug = _slugify(f"{template.slug if template else 'svc'}-{device.id}-{row.id}")
    inst = ServiceInstance(
        name=name[:255],
        slug=slug,
        template_version_id=version.id,
        deployment_id=row.id,
        device_id=device.id,
        ipv4_address_id=address_id,
        status="active",
    )
    db.add(inst)
    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        row = get_deployment(db, row.id)
        assert row is not None
        row.status = "failed"
        row.finished_at = dt.datetime.now(dt.timezone.utc)
        _add_step(db, row, "record_instance", "failed", "instans-slug finnes allerede")
        db.commit()
        loaded = get_deployment(db, row.id)
        assert loaded is not None
        return loaded

    _add_step(db, row, "record_instance", "ok", f"instans #{inst.id}")
    row.status = "succeeded"
    row.finished_at = dt.datetime.now(dt.timezone.utc)
    db.commit()
    loaded = get_deployment(db, row.id)
    assert loaded is not None
    return loaded


def list_instances(db: Session) -> list[ServiceInstance]:
    return list(db.execute(select(ServiceInstance).order_by(ServiceInstance.id.desc())).scalars().all())
