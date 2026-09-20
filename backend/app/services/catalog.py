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
from app.schemas.platform import (
    CLUSTER_KINDS,
    PlatformClusterCreate,
    PlatformClusterMemberCreate,
    PlatformVirtualMachineCreate,
)
from app.services import dcim as dcim_svc
from app.services import ipam as ipam_svc
from app.services import platform as plat_svc
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
        cluster_id=row.cluster_id,
        vm_id=row.vm_id,
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


def build_cluster_plan(
    db: Session,
    version: ServiceTemplateVersion,
    device_ids: list[int],
    name: str | None,
    cluster_kind: str | None,
) -> dict:
    template = db.get(ServiceTemplate, version.template_id)
    blockers: list[str] = []
    kind = (cluster_kind or "other").strip().lower() or "other"
    if kind not in CLUSTER_KINDS:
        blockers.append("unknown_cluster_kind")
        kind = "other"
    cluster_name = (name or "").strip()
    if not cluster_name:
        blockers.append("cluster_name_required")
    ids: list[int] = []
    seen: set[int] = set()
    for raw in device_ids:
        try:
            did = int(raw)
        except (TypeError, ValueError):
            blockers.append("device_not_found")
            continue
        if did in seen:
            continue
        seen.add(did)
        ids.append(did)
    if not ids:
        blockers.append("devices_required")
    devices: list[dict] = []
    for did in ids:
        device = dcim_svc.get_device(db, did)
        if device is None:
            blockers.append("device_not_found")
            continue
        devices.append(
            {
                "id": device.id,
                "name": device.name,
                "site_id": dcim_svc.device_effective_site_id(db, device.id),
            }
        )
    slug = _slugify(cluster_name) if cluster_name else None
    if slug and plat_svc.get_cluster_by_slug(db, slug) is not None:
        blockers.append("cluster_slug_taken")
    return {
        "kind": "cluster",
        "template": {
            "id": template.id if template else version.template_id,
            "name": template.name if template else None,
            "version": version.version,
        },
        "cluster": {"name": cluster_name or None, "kind": kind, "slug": slug},
        "devices": devices,
        "device_ids": ids,
        "requested_name": cluster_name or None,
        "cluster_kind": kind,
        "reserve_ipv4": False,
        "prefix": None,
        "blockers": list(dict.fromkeys(blockers)),
        "can_run": len(blockers) == 0,
        "notes": [
            "Registrerer et cluster og medlemskap på eksisterende enheter.",
            "Installerer ikke OS, hypervisor eller cluster-programvare.",
        ],
    }


def build_vm_plan(
    db: Session,
    version: ServiceTemplateVersion,
    cluster_id: int | None,
    name: str | None,
    device_id: int | None,
    prefix_id: int | None,
) -> dict:
    template = db.get(ServiceTemplate, version.template_id)
    spec = version.spec if isinstance(version.spec, dict) else {}
    reserve = bool(spec.get("reserve_ipv4"))
    blockers: list[str] = []
    vm_name = (name or "").strip()
    if not vm_name:
        blockers.append("vm_name_required")
    cluster = plat_svc.get_cluster(db, cluster_id) if cluster_id else None
    if cluster is None:
        blockers.append("cluster_required" if not cluster_id else "cluster_not_found")
    device_info: dict | None = None
    if device_id is not None:
        device = dcim_svc.get_device(db, device_id)
        if device is None:
            blockers.append("device_not_found")
        elif cluster is not None and not plat_svc.device_is_member(db, cluster.id, device.id):
            blockers.append("device_not_member")
        elif device is not None:
            device_info = {
                "id": device.id,
                "name": device.name,
                "site_id": dcim_svc.device_effective_site_id(db, device.id),
            }
    slug = _slugify(vm_name) if vm_name else None
    if slug and plat_svc.get_vm_by_slug(db, slug) is not None:
        blockers.append("vm_slug_taken")
    prefix_info: dict | None = None
    site_id = device_info["site_id"] if device_info else (cluster.site_id if cluster else None)
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
    return {
        "kind": "virtual_machine",
        "template": {
            "id": template.id if template else version.template_id,
            "name": template.name if template else None,
            "version": version.version,
        },
        "cluster": (
            {"id": cluster.id, "name": cluster.name, "kind": cluster.kind, "slug": cluster.slug}
            if cluster is not None
            else None
        ),
        "vm": {"name": vm_name or None, "slug": slug},
        "device": device_info,
        "requested_name": vm_name or None,
        "cluster_id": cluster.id if cluster is not None else cluster_id,
        "reserve_ipv4": reserve,
        "prefix": prefix_info,
        "blockers": list(dict.fromkeys(blockers)),
        "can_run": len(blockers) == 0,
        "notes": [
            "Registrerer en VM på et eksisterende cluster.",
            "Oppretter eller starter ikke en virtuell maskin.",
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


def _device_ids_from(data: ServiceDeploymentCreate) -> list[int]:
    ids: list[int] = []
    seen: set[int] = set()
    raw = list(data.device_ids or [])
    if data.device_id is not None:
        raw = [data.device_id, *raw]
    for did in raw:
        if did in seen:
            continue
        seen.add(did)
        ids.append(did)
    return ids


def create_deployment(db: Session, data: ServiceDeploymentCreate) -> ServiceDeployment:
    version = get_version(db, data.template_version_id)
    if version is None:
        raise HTTPException(status_code=404, detail="malversjon ikke funnet")
    spec = version.spec if isinstance(version.spec, dict) else {}
    ids = _device_ids_from(data)
    if spec.get("kind") == "virtual_machine":
        plan = build_vm_plan(db, version, data.cluster_id, data.name, data.device_id, data.ipv4_prefix_id)
        row = ServiceDeployment(
            template_version_id=version.id,
            device_id=data.device_id,
            cluster_id=data.cluster_id,
            ipv4_prefix_id=data.ipv4_prefix_id,
            status="planned",
            plan_json=plan,
        )
        db.add(row)
        db.commit()
        loaded = get_deployment(db, row.id)
        assert loaded is not None
        return loaded
    if spec.get("kind") == "cluster":
        plan = build_cluster_plan(db, version, ids, data.name, data.cluster_kind)
        if not ids:
            raise HTTPException(status_code=400, detail="minst én enhet kreves")
        primary = dcim_svc.get_device(db, ids[0])
        if primary is None:
            raise HTTPException(status_code=404, detail="enhet ikke funnet")
        row = ServiceDeployment(
            template_version_id=version.id,
            device_id=primary.id,
            ipv4_prefix_id=None,
            status="planned",
            plan_json=plan,
        )
        db.add(row)
        db.commit()
        loaded = get_deployment(db, row.id)
        assert loaded is not None
        return loaded
    if not ids:
        raise HTTPException(status_code=400, detail="enhet kreves")
    device = dcim_svc.get_device(db, ids[0])
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


def _run_cluster(db: Session, row: ServiceDeployment, version: ServiceTemplateVersion) -> ServiceDeployment:
    prev = row.plan_json if isinstance(row.plan_json, dict) else {}
    ids = [int(x) for x in (prev.get("device_ids") or [row.device_id])]
    plan = build_cluster_plan(db, version, ids, prev.get("requested_name"), prev.get("cluster_kind"))
    row.plan_json = plan
    if not plan["can_run"]:
        db.commit()
        raise HTTPException(status_code=400, detail={"code": "cannot_run", "blockers": plan["blockers"]})

    row.status = "running"
    row.started_at = dt.datetime.now(dt.timezone.utc)
    db.commit()

    names = ", ".join(d["name"] for d in plan["devices"])
    _add_step(db, row, "validate_devices", "ok", names)
    db.commit()

    cluster_info = plan["cluster"]
    try:
        cluster = plat_svc.create_cluster(
            db,
            PlatformClusterCreate(
                name=cluster_info["name"],
                slug=cluster_info["slug"],
                kind=cluster_info["kind"],
                site_id=plat_svc.shared_site_id(db, ids),
            ),
        )
        for did in ids:
            plat_svc.add_member(db, cluster, PlatformClusterMemberCreate(device_id=did, role="node"))
        cluster = plat_svc.get_cluster(db, cluster.id)
        assert cluster is not None
        row.cluster_id = cluster.id
        _add_step(db, row, "record_cluster", "ok", f"{cluster.name} #{cluster.id}")
        db.commit()
    except HTTPException as exc:
        row.status = "failed"
        row.finished_at = dt.datetime.now(dt.timezone.utc)
        _add_step(db, row, "record_cluster", "failed", _exc_detail(exc))
        db.commit()
        loaded = get_deployment(db, row.id)
        assert loaded is not None
        return loaded

    template = db.get(ServiceTemplate, version.template_id)
    name = cluster_info["name"]
    slug = _slugify(f"{template.slug if template else 'svc'}-cluster-{row.id}")
    inst = ServiceInstance(
        name=name[:255],
        slug=slug,
        template_version_id=version.id,
        deployment_id=row.id,
        device_id=row.device_id,
        cluster_id=row.cluster_id,
        ipv4_address_id=None,
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


def _run_vm(db: Session, row: ServiceDeployment, version: ServiceTemplateVersion) -> ServiceDeployment:
    prev = row.plan_json if isinstance(row.plan_json, dict) else {}
    plan = build_vm_plan(
        db,
        version,
        row.cluster_id or prev.get("cluster_id"),
        prev.get("requested_name"),
        row.device_id,
        row.ipv4_prefix_id,
    )
    row.plan_json = plan
    if not plan["can_run"]:
        db.commit()
        raise HTTPException(status_code=400, detail={"code": "cannot_run", "blockers": plan["blockers"]})

    row.status = "running"
    row.started_at = dt.datetime.now(dt.timezone.utc)
    db.commit()

    cluster = plat_svc.get_cluster(db, row.cluster_id)
    assert cluster is not None
    _add_step(db, row, "validate_cluster", "ok", cluster.name)
    db.commit()

    try:
        vm = plat_svc.create_vm(
            db,
            cluster,
            PlatformVirtualMachineCreate(
                name=plan["vm"]["name"],
                slug=plan["vm"]["slug"],
                device_id=row.device_id,
                status="active",
            ),
        )
        row.vm_id = vm.id
        _add_step(db, row, "record_vm", "ok", f"{vm.name} #{vm.id}")
        db.commit()
    except HTTPException as exc:
        row.status = "failed"
        row.finished_at = dt.datetime.now(dt.timezone.utc)
        _add_step(db, row, "record_vm", "failed", _exc_detail(exc))
        db.commit()
        loaded = get_deployment(db, row.id)
        assert loaded is not None
        return loaded

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
                    device_id=row.device_id,
                    note=f"service catalog vm deployment {row.id}",
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
    name = plan["vm"]["name"]
    slug = _slugify(f"{template.slug if template else 'svc'}-vm-{row.id}")
    inst = ServiceInstance(
        name=name[:255],
        slug=slug,
        template_version_id=version.id,
        deployment_id=row.id,
        device_id=row.device_id,
        cluster_id=row.cluster_id,
        vm_id=row.vm_id,
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


def run_deployment(db: Session, row: ServiceDeployment) -> ServiceDeployment:
    if row.status != "planned":
        raise HTTPException(status_code=409, detail="deployment er allerede kjørt")
    version = get_version(db, row.template_version_id)
    if version is None:
        raise HTTPException(status_code=404, detail="malversjon ikke funnet")
    spec = version.spec if isinstance(version.spec, dict) else {}
    if spec.get("kind") == "virtual_machine":
        return _run_vm(db, row, version)
    if spec.get("kind") == "cluster":
        return _run_cluster(db, row, version)
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
