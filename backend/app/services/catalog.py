"""Versjonert katalog og ærlig device_instance-deployment (uten OS-install)."""

from __future__ import annotations

import datetime as dt
import re

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.models.platform import PlatformStoragePool
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
    CLOUD_KINDS,
    CLUSTER_KINDS,
    DISK_KINDS,
    STORAGE_KINDS,
    PlatformCloudSubscriptionCreate,
    PlatformClusterCreate,
    PlatformClusterMemberCreate,
    PlatformStoragePoolCreate,
    PlatformVirtualDiskCreate,
    PlatformVirtualInterfaceCreate,
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
        storage_pool_id=row.storage_pool_id,
        virtual_interface_id=row.virtual_interface_id,
        virtual_disk_id=row.virtual_disk_id,
        cloud_subscription_id=row.cloud_subscription_id,
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


def build_storage_plan(
    db: Session,
    version: ServiceTemplateVersion,
    cluster_id: int | None,
    name: str | None,
    storage_kind: str | None,
) -> dict:
    template = db.get(ServiceTemplate, version.template_id)
    blockers: list[str] = []
    pool_name = (name or "").strip()
    if not pool_name:
        blockers.append("storage_name_required")
    kind = (storage_kind or "other").strip().lower() or "other"
    if kind not in STORAGE_KINDS:
        blockers.append("unknown_storage_kind")
        kind = "other"
    cluster = plat_svc.get_cluster(db, cluster_id) if cluster_id else None
    if cluster is None:
        blockers.append("cluster_required" if not cluster_id else "cluster_not_found")
    slug = _slugify(pool_name) if pool_name else None
    if slug and plat_svc.get_storage_pool_by_slug(db, slug) is not None:
        blockers.append("storage_slug_taken")
    return {
        "kind": "storage_pool",
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
        "storage": {"name": pool_name or None, "slug": slug, "kind": kind},
        "requested_name": pool_name or None,
        "storage_kind": kind,
        "cluster_id": cluster.id if cluster is not None else cluster_id,
        "reserve_ipv4": False,
        "prefix": None,
        "blockers": list(dict.fromkeys(blockers)),
        "can_run": len(blockers) == 0,
        "notes": [
            "Registrerer en lagringspool på et eksisterende cluster.",
            "Måler ikke kapasitet og oppretter ikke datastore i hypervisoren.",
        ],
    }


def build_vif_plan(
    db: Session,
    version: ServiceTemplateVersion,
    vm_id: int | None,
    name: str | None,
    prefix_id: int | None = None,
) -> dict:
    template = db.get(ServiceTemplate, version.template_id)
    spec = version.spec if isinstance(version.spec, dict) else {}
    reserve = bool(spec.get("reserve_ipv4"))
    blockers: list[str] = []
    iface_name = (name or "").strip()
    if not iface_name:
        blockers.append("vif_name_required")
    vm = plat_svc.get_vm(db, vm_id) if vm_id else None
    if vm is None:
        blockers.append("vm_required" if not vm_id else "vm_not_found")
    cluster = plat_svc.get_cluster(db, vm.cluster_id) if vm is not None else None
    slug = _slugify(iface_name) if iface_name else None
    if slug and plat_svc.get_vif_by_slug(db, slug) is not None:
        blockers.append("vif_slug_taken")
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
                if cluster is not None and cluster.site_id is not None and int(cluster.site_id) != int(pfx.site_id):
                    blockers.append("prefix_site_mismatch")
                if read.usable_hosts <= read.used_count:
                    blockers.append("prefix_exhausted")
    notes = [
        "Registrerer et virtuelt grensesnitt på en eksisterende VM.",
        "Oppretter ikke NIC i hypervisoren og finner ikke opp MAC.",
    ]
    if reserve:
        notes.append("Reserverer IPv4 på grensesnittet uten å finne opp MAC.")
    return {
        "kind": "virtual_interface",
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
        "vm": (
            {"id": vm.id, "name": vm.name, "slug": vm.slug}
            if vm is not None
            else None
        ),
        "vif": {"name": iface_name or None, "slug": slug},
        "requested_name": iface_name or None,
        "vm_id": vm.id if vm is not None else vm_id,
        "cluster_id": cluster.id if cluster is not None else None,
        "reserve_ipv4": reserve,
        "prefix": prefix_info,
        "blockers": list(dict.fromkeys(blockers)),
        "can_run": len(blockers) == 0,
        "notes": notes,
    }


def build_disk_plan(
    db: Session,
    version: ServiceTemplateVersion,
    vm_id: int | None,
    name: str | None,
    disk_kind: str | None,
    storage_pool_id: int | None,
) -> dict:
    template = db.get(ServiceTemplate, version.template_id)
    blockers: list[str] = []
    disk_name = (name or "").strip()
    if not disk_name:
        blockers.append("disk_name_required")
    kind = (disk_kind or "other").strip().lower() or "other"
    if kind not in DISK_KINDS:
        blockers.append("unknown_disk_kind")
        kind = "other"
    vm = plat_svc.get_vm(db, vm_id) if vm_id else None
    if vm is None:
        blockers.append("vm_required" if not vm_id else "vm_not_found")
    cluster = plat_svc.get_cluster(db, vm.cluster_id) if vm is not None else None
    pool_info: dict | None = None
    if storage_pool_id is not None:
        pool = db.get(PlatformStoragePool, storage_pool_id) if cluster is not None else None
        if pool is None or (cluster is not None and pool.cluster_id != cluster.id):
            blockers.append("storage_pool_not_on_cluster")
        elif pool is not None:
            pool_info = {"id": pool.id, "name": pool.name, "kind": pool.kind}
    slug = _slugify(disk_name) if disk_name else None
    if slug and plat_svc.get_disk_by_slug(db, slug) is not None:
        blockers.append("disk_slug_taken")
    return {
        "kind": "virtual_disk",
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
        "vm": (
            {"id": vm.id, "name": vm.name, "slug": vm.slug}
            if vm is not None
            else None
        ),
        "disk": {"name": disk_name or None, "slug": slug, "kind": kind},
        "storage": pool_info,
        "requested_name": disk_name or None,
        "disk_kind": kind,
        "storage_pool_id": pool_info["id"] if pool_info else storage_pool_id,
        "vm_id": vm.id if vm is not None else vm_id,
        "cluster_id": cluster.id if cluster is not None else None,
        "reserve_ipv4": False,
        "prefix": None,
        "blockers": list(dict.fromkeys(blockers)),
        "can_run": len(blockers) == 0,
        "notes": [
            "Registrerer en disk eller et volum på en eksisterende VM.",
            "Måler ikke kapasitet og oppretter ikke LUN i hypervisoren.",
        ],
    }


def build_cloud_plan(
    db: Session,
    version: ServiceTemplateVersion,
    name: str | None,
    cloud_kind: str | None,
) -> dict:
    template = db.get(ServiceTemplate, version.template_id)
    blockers: list[str] = []
    cloud_name = (name or "").strip()
    if not cloud_name:
        blockers.append("cloud_name_required")
    kind = (cloud_kind or "other").strip().lower() or "other"
    if kind not in CLOUD_KINDS:
        blockers.append("unknown_cloud_kind")
        kind = "other"
    slug = _slugify(cloud_name) if cloud_name else None
    if slug and plat_svc.get_cloud_by_slug(db, slug) is not None:
        blockers.append("cloud_slug_taken")
    return {
        "kind": "cloud_subscription",
        "template": {
            "id": template.id if template else version.template_id,
            "name": template.name if template else None,
            "version": version.version,
        },
        "cloud": {"name": cloud_name or None, "slug": slug, "kind": kind},
        "requested_name": cloud_name or None,
        "cloud_kind": kind,
        "reserve_ipv4": False,
        "prefix": None,
        "blockers": list(dict.fromkeys(blockers)),
        "can_run": len(blockers) == 0,
        "notes": [
            "Registrerer et skyabonnement eller prosjekt.",
            "Oppretter ikke ressurser hos leverandøren og finner ikke opp kostnad eller kvote.",
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
    if spec.get("kind") == "cloud_subscription":
        plan = build_cloud_plan(db, version, data.name, data.cloud_kind)
        row = ServiceDeployment(
            template_version_id=version.id,
            device_id=None,
            ipv4_prefix_id=None,
            status="planned",
            plan_json=plan,
        )
        db.add(row)
        db.commit()
        loaded = get_deployment(db, row.id)
        assert loaded is not None
        return loaded
    if spec.get("kind") == "virtual_disk":
        plan = build_disk_plan(
            db, version, data.vm_id, data.name, data.disk_kind, data.storage_pool_id
        )
        row = ServiceDeployment(
            template_version_id=version.id,
            device_id=None,
            cluster_id=plan.get("cluster_id"),
            vm_id=data.vm_id,
            storage_pool_id=data.storage_pool_id,
            ipv4_prefix_id=None,
            status="planned",
            plan_json=plan,
        )
        db.add(row)
        db.commit()
        loaded = get_deployment(db, row.id)
        assert loaded is not None
        return loaded
    if spec.get("kind") == "virtual_interface":
        plan = build_vif_plan(db, version, data.vm_id, data.name, data.ipv4_prefix_id)
        row = ServiceDeployment(
            template_version_id=version.id,
            device_id=None,
            cluster_id=plan.get("cluster_id"),
            vm_id=data.vm_id,
            ipv4_prefix_id=data.ipv4_prefix_id,
            status="planned",
            plan_json=plan,
        )
        db.add(row)
        db.commit()
        loaded = get_deployment(db, row.id)
        assert loaded is not None
        return loaded
    if spec.get("kind") == "storage_pool":
        plan = build_storage_plan(db, version, data.cluster_id, data.name, data.storage_kind)
        row = ServiceDeployment(
            template_version_id=version.id,
            device_id=None,
            cluster_id=data.cluster_id,
            ipv4_prefix_id=None,
            status="planned",
            plan_json=plan,
        )
        db.add(row)
        db.commit()
        loaded = get_deployment(db, row.id)
        assert loaded is not None
        return loaded
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


def _run_storage(db: Session, row: ServiceDeployment, version: ServiceTemplateVersion) -> ServiceDeployment:
    prev = row.plan_json if isinstance(row.plan_json, dict) else {}
    plan = build_storage_plan(
        db,
        version,
        row.cluster_id or prev.get("cluster_id"),
        prev.get("requested_name"),
        prev.get("storage_kind"),
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
        pool = plat_svc.create_storage_pool(
            db,
            cluster,
            PlatformStoragePoolCreate(
                name=plan["storage"]["name"],
                slug=plan["storage"]["slug"],
                kind=plan["storage"]["kind"],
                status="active",
            ),
        )
        row.storage_pool_id = pool.id
        _add_step(db, row, "record_storage", "ok", f"{pool.name} #{pool.id}")
        db.commit()
    except HTTPException as exc:
        row.status = "failed"
        row.finished_at = dt.datetime.now(dt.timezone.utc)
        _add_step(db, row, "record_storage", "failed", _exc_detail(exc))
        db.commit()
        loaded = get_deployment(db, row.id)
        assert loaded is not None
        return loaded

    template = db.get(ServiceTemplate, version.template_id)
    name = plan["storage"]["name"]
    slug = _slugify(f"{template.slug if template else 'svc'}-storage-{row.id}")
    inst = ServiceInstance(
        name=name[:255],
        slug=slug,
        template_version_id=version.id,
        deployment_id=row.id,
        device_id=None,
        cluster_id=row.cluster_id,
        storage_pool_id=row.storage_pool_id,
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


def _run_vif(db: Session, row: ServiceDeployment, version: ServiceTemplateVersion) -> ServiceDeployment:
    prev = row.plan_json if isinstance(row.plan_json, dict) else {}
    plan = build_vif_plan(
        db,
        version,
        row.vm_id or prev.get("vm_id"),
        prev.get("requested_name"),
        row.ipv4_prefix_id,
    )
    row.plan_json = plan
    if not plan["can_run"]:
        db.commit()
        raise HTTPException(status_code=400, detail={"code": "cannot_run", "blockers": plan["blockers"]})

    row.status = "running"
    row.started_at = dt.datetime.now(dt.timezone.utc)
    db.commit()

    vm = plat_svc.get_vm(db, row.vm_id)
    assert vm is not None
    cluster = plat_svc.get_cluster(db, vm.cluster_id)
    assert cluster is not None
    _add_step(db, row, "validate_vm", "ok", vm.name)
    db.commit()

    try:
        iface = plat_svc.create_vif(
            db,
            cluster,
            vm,
            PlatformVirtualInterfaceCreate(
                name=plan["vif"]["name"],
                slug=plan["vif"]["slug"],
                status="active",
            ),
        )
        row.virtual_interface_id = iface.id
        row.cluster_id = cluster.id
        _add_step(db, row, "record_vif", "ok", f"{iface.name} #{iface.id}")
        db.commit()
    except HTTPException as exc:
        row.status = "failed"
        row.finished_at = dt.datetime.now(dt.timezone.utc)
        _add_step(db, row, "record_vif", "failed", _exc_detail(exc))
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
        iface = plat_svc.get_vif(db, row.virtual_interface_id) if row.virtual_interface_id else None
        if iface is None:
            row.status = "failed"
            row.finished_at = dt.datetime.now(dt.timezone.utc)
            _add_step(db, row, "reserve_ipv4", "failed", "virtuelt grensesnitt ikke funnet")
            db.commit()
            loaded = get_deployment(db, row.id)
            assert loaded is not None
            return loaded
        try:
            from app.schemas.platform import PlatformVifIpv4Assign

            addr = plat_svc.assign_vif_ipv4(
                db,
                cluster,
                vm,
                iface,
                PlatformVifIpv4Assign(ipv4_prefix_id=row.ipv4_prefix_id),
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
    name = plan["vif"]["name"]
    slug = _slugify(f"{template.slug if template else 'svc'}-vif-{row.id}")
    inst = ServiceInstance(
        name=name[:255],
        slug=slug,
        template_version_id=version.id,
        deployment_id=row.id,
        device_id=None,
        cluster_id=row.cluster_id,
        vm_id=row.vm_id,
        virtual_interface_id=row.virtual_interface_id,
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


def _run_disk(db: Session, row: ServiceDeployment, version: ServiceTemplateVersion) -> ServiceDeployment:
    prev = row.plan_json if isinstance(row.plan_json, dict) else {}
    plan = build_disk_plan(
        db,
        version,
        row.vm_id or prev.get("vm_id"),
        prev.get("requested_name"),
        prev.get("disk_kind"),
        row.storage_pool_id or prev.get("storage_pool_id"),
    )
    row.plan_json = plan
    if not plan["can_run"]:
        db.commit()
        raise HTTPException(status_code=400, detail={"code": "cannot_run", "blockers": plan["blockers"]})

    row.status = "running"
    row.started_at = dt.datetime.now(dt.timezone.utc)
    db.commit()

    vm = plat_svc.get_vm(db, row.vm_id)
    assert vm is not None
    cluster = plat_svc.get_cluster(db, vm.cluster_id)
    assert cluster is not None
    _add_step(db, row, "validate_vm", "ok", vm.name)
    db.commit()

    try:
        disk = plat_svc.create_disk(
            db,
            cluster,
            vm,
            PlatformVirtualDiskCreate(
                name=plan["disk"]["name"],
                slug=plan["disk"]["slug"],
                storage_pool_id=plan.get("storage_pool_id"),
                kind=plan["disk"]["kind"],
                status="active",
            ),
        )
        row.virtual_disk_id = disk.id
        row.cluster_id = cluster.id
        _add_step(db, row, "record_disk", "ok", f"{disk.name} #{disk.id}")
        db.commit()
    except HTTPException as exc:
        row.status = "failed"
        row.finished_at = dt.datetime.now(dt.timezone.utc)
        _add_step(db, row, "record_disk", "failed", _exc_detail(exc))
        db.commit()
        loaded = get_deployment(db, row.id)
        assert loaded is not None
        return loaded

    template = db.get(ServiceTemplate, version.template_id)
    name = plan["disk"]["name"]
    slug = _slugify(f"{template.slug if template else 'svc'}-disk-{row.id}")
    inst = ServiceInstance(
        name=name[:255],
        slug=slug,
        template_version_id=version.id,
        deployment_id=row.id,
        device_id=None,
        cluster_id=row.cluster_id,
        vm_id=row.vm_id,
        storage_pool_id=row.storage_pool_id,
        virtual_disk_id=row.virtual_disk_id,
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


def _run_cloud(db: Session, row: ServiceDeployment, version: ServiceTemplateVersion) -> ServiceDeployment:
    prev = row.plan_json if isinstance(row.plan_json, dict) else {}
    plan = build_cloud_plan(db, version, prev.get("requested_name"), prev.get("cloud_kind"))
    row.plan_json = plan
    if not plan["can_run"]:
        db.commit()
        raise HTTPException(status_code=400, detail={"code": "cannot_run", "blockers": plan["blockers"]})

    row.status = "running"
    row.started_at = dt.datetime.now(dt.timezone.utc)
    db.commit()

    try:
        cloud = plat_svc.create_cloud_subscription(
            db,
            PlatformCloudSubscriptionCreate(
                name=plan["cloud"]["name"],
                slug=plan["cloud"]["slug"],
                kind=plan["cloud"]["kind"],
                status="active",
            ),
        )
        row.cloud_subscription_id = cloud.id
        _add_step(db, row, "record_cloud", "ok", f"{cloud.name} #{cloud.id}")
        db.commit()
    except HTTPException as exc:
        row.status = "failed"
        row.finished_at = dt.datetime.now(dt.timezone.utc)
        _add_step(db, row, "record_cloud", "failed", _exc_detail(exc))
        db.commit()
        loaded = get_deployment(db, row.id)
        assert loaded is not None
        return loaded

    template = db.get(ServiceTemplate, version.template_id)
    name = plan["cloud"]["name"]
    slug = _slugify(f"{template.slug if template else 'svc'}-cloud-{row.id}")
    inst = ServiceInstance(
        name=name[:255],
        slug=slug,
        template_version_id=version.id,
        deployment_id=row.id,
        device_id=None,
        cloud_subscription_id=row.cloud_subscription_id,
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


def run_deployment(db: Session, row: ServiceDeployment) -> ServiceDeployment:
    if row.status != "planned":
        raise HTTPException(status_code=409, detail="deployment er allerede kjørt")
    version = get_version(db, row.template_version_id)
    if version is None:
        raise HTTPException(status_code=404, detail="malversjon ikke funnet")
    spec = version.spec if isinstance(version.spec, dict) else {}
    if spec.get("kind") == "cloud_subscription":
        return _run_cloud(db, row, version)
    if spec.get("kind") == "virtual_disk":
        return _run_disk(db, row, version)
    if spec.get("kind") == "virtual_interface":
        return _run_vif(db, row, version)
    if spec.get("kind") == "storage_pool":
        return _run_storage(db, row, version)
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


def get_template_by_slug(db: Session, slug: str) -> ServiceTemplate | None:
    return db.execute(
        select(ServiceTemplate)
        .options(selectinload(ServiceTemplate.versions))
        .where(ServiceTemplate.slug == slug)
    ).scalar_one_or_none()


def get_instance_by_slug(db: Session, slug: str) -> ServiceInstance | None:
    return db.execute(select(ServiceInstance).where(ServiceInstance.slug == slug)).scalar_one_or_none()


def ensure_template(
    db: Session,
    *,
    slug: str,
    name: str,
    description: str | None,
    versions: list[dict],
) -> ServiceTemplate:
    """Idempotent katalogmal etter slug. Oppretter manglende versjoner, uten å kjøre deploy."""
    slug_n = _slugify(slug or name)
    row = get_template_by_slug(db, slug_n)
    if row is None:
        row = ServiceTemplate(
            name=(name or slug_n).strip()[:255],
            slug=slug_n,
            description=(description or "").strip() or None,
        )
        db.add(row)
        db.flush()
    for item in versions:
        ver = str(item.get("version") or "").strip()
        if not ver:
            continue
        exists = db.execute(
            select(ServiceTemplateVersion.id).where(
                ServiceTemplateVersion.template_id == row.id,
                ServiceTemplateVersion.version == ver,
            )
        ).scalar_one_or_none()
        if exists:
            continue
        spec = ServiceTemplateSpec.model_validate(item.get("spec") or {})
        db.add(ServiceTemplateVersion(template_id=row.id, version=ver, spec=_spec_dict(spec)))
    db.commit()
    loaded = _load_template(db, row.id)
    assert loaded is not None
    return loaded


def import_instance(
    db: Session,
    *,
    slug: str,
    name: str,
    status: str,
    template_version: ServiceTemplateVersion,
    device_id: int | None = None,
    cluster_id: int | None = None,
    vm_id: int | None = None,
    storage_pool_id: int | None = None,
    virtual_interface_id: int | None = None,
    virtual_disk_id: int | None = None,
    cloud_subscription_id: int | None = None,
    ipv4_address_id: int | None = None,
) -> ServiceInstance:
    """Registrer en tjenesteinstans uten å kjøre deployment-steg."""
    slug_n = _slugify(slug or name)
    existing = get_instance_by_slug(db, slug_n)
    if existing is not None:
        return existing
    dep = ServiceDeployment(
        template_version_id=template_version.id,
        device_id=device_id,
        cluster_id=cluster_id,
        vm_id=vm_id,
        storage_pool_id=storage_pool_id,
        virtual_interface_id=virtual_interface_id,
        virtual_disk_id=virtual_disk_id,
        cloud_subscription_id=cloud_subscription_id,
        status="imported",
        plan_json={"source": "federation"},
    )
    db.add(dep)
    db.flush()
    inst = ServiceInstance(
        name=(name or slug_n).strip()[:255],
        slug=slug_n,
        template_version_id=template_version.id,
        deployment_id=dep.id,
        device_id=device_id,
        cluster_id=cluster_id,
        vm_id=vm_id,
        storage_pool_id=storage_pool_id,
        virtual_interface_id=virtual_interface_id,
        virtual_disk_id=virtual_disk_id,
        cloud_subscription_id=cloud_subscription_id,
        ipv4_address_id=ipv4_address_id,
        status=(status or "active").strip() or "active",
    )
    db.add(inst)
    db.commit()
    db.refresh(inst)
    return inst
