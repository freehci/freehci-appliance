"""Ærlig cluster- og VM-inventar — uten observert helse eller kapasitet."""

from __future__ import annotations

import re

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.models.platform import (
    PlatformCluster,
    PlatformClusterMember,
    PlatformStoragePool,
    PlatformVirtualInterface,
    PlatformVirtualMachine,
)
from app.schemas.platform import (
    PlatformClusterCreate,
    PlatformClusterMemberCreate,
    PlatformClusterMemberRead,
    PlatformClusterRead,
    PlatformStoragePoolCreate,
    PlatformStoragePoolRead,
    PlatformVirtualInterfaceCreate,
    PlatformVirtualInterfaceRead,
    PlatformVirtualMachineCreate,
    PlatformVirtualMachineRead,
)
from app.services import dcim as dcim_svc


def _slugify(value: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", (value or "").strip().lower()).strip("-")
    return (s or "cluster")[:128]


def cluster_to_read(row: PlatformCluster) -> PlatformClusterRead:
    return PlatformClusterRead(
        id=row.id,
        name=row.name,
        slug=row.slug,
        kind=row.kind,
        site_id=row.site_id,
        description=row.description,
        created_at=row.created_at,
        members=[PlatformClusterMemberRead.model_validate(m) for m in row.members],
        vms=[PlatformVirtualMachineRead.model_validate(v) for v in row.vms],
        storage_pools=[PlatformStoragePoolRead.model_validate(p) for p in row.storage_pools],
    )


def _load(db: Session, cluster_id: int) -> PlatformCluster | None:
    return db.execute(
        select(PlatformCluster)
        .options(
            selectinload(PlatformCluster.members),
            selectinload(PlatformCluster.vms).selectinload(PlatformVirtualMachine.interfaces),
            selectinload(PlatformCluster.storage_pools),
        )
        .where(PlatformCluster.id == cluster_id)
    ).scalar_one_or_none()


def list_clusters(db: Session) -> list[PlatformCluster]:
    return list(
        db.execute(
            select(PlatformCluster)
            .options(
                selectinload(PlatformCluster.members),
                selectinload(PlatformCluster.vms).selectinload(PlatformVirtualMachine.interfaces),
                selectinload(PlatformCluster.storage_pools),
            )
            .order_by(PlatformCluster.name)
        ).scalars().all()
    )


def get_cluster(db: Session, cluster_id: int) -> PlatformCluster | None:
    return _load(db, cluster_id)


def get_cluster_by_slug(db: Session, slug: str) -> PlatformCluster | None:
    return db.execute(select(PlatformCluster).where(PlatformCluster.slug == slug)).scalar_one_or_none()


def create_cluster(db: Session, data: PlatformClusterCreate) -> PlatformCluster:
    slug = _slugify(data.slug or data.name)
    if db.execute(select(PlatformCluster.id).where(PlatformCluster.slug == slug)).scalar_one_or_none():
        raise HTTPException(status_code=409, detail="cluster-slug finnes allerede")
    if data.site_id is not None and dcim_svc.get_site(db, data.site_id) is None:
        raise HTTPException(status_code=404, detail="site ikke funnet")
    row = PlatformCluster(
        name=data.name.strip(),
        slug=slug,
        kind=data.kind,
        site_id=data.site_id,
        description=(data.description or "").strip() or None,
    )
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="cluster-slug finnes allerede")
    loaded = _load(db, row.id)
    assert loaded is not None
    return loaded


def delete_cluster(db: Session, row: PlatformCluster) -> None:
    db.delete(row)
    db.commit()


def add_member(db: Session, cluster: PlatformCluster, data: PlatformClusterMemberCreate) -> PlatformClusterMember:
    device = dcim_svc.get_device(db, data.device_id)
    if device is None:
        raise HTTPException(status_code=404, detail="enhet ikke funnet")
    exists = db.execute(
        select(PlatformClusterMember.id).where(
            PlatformClusterMember.cluster_id == cluster.id,
            PlatformClusterMember.device_id == device.id,
        )
    ).scalar_one_or_none()
    if exists:
        raise HTTPException(status_code=409, detail="enheten er allerede medlem")
    row = PlatformClusterMember(cluster_id=cluster.id, device_id=device.id, role=data.role)
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="enheten er allerede medlem")
    db.refresh(row)
    return row


def remove_member(db: Session, cluster: PlatformCluster, member_id: int) -> None:
    row = db.get(PlatformClusterMember, member_id)
    if row is None or row.cluster_id != cluster.id:
        raise HTTPException(status_code=404, detail="medlem ikke funnet")
    db.delete(row)
    db.commit()


def device_is_member(db: Session, cluster_id: int, device_id: int) -> bool:
    return (
        db.execute(
            select(PlatformClusterMember.id).where(
                PlatformClusterMember.cluster_id == cluster_id,
                PlatformClusterMember.device_id == device_id,
            )
        ).scalar_one_or_none()
        is not None
    )


def get_vm(db: Session, vm_id: int) -> PlatformVirtualMachine | None:
    return db.get(PlatformVirtualMachine, vm_id)


def get_vm_by_slug(db: Session, slug: str) -> PlatformVirtualMachine | None:
    return db.execute(select(PlatformVirtualMachine).where(PlatformVirtualMachine.slug == slug)).scalar_one_or_none()


def vm_to_read(row: PlatformVirtualMachine) -> PlatformVirtualMachineRead:
    return PlatformVirtualMachineRead.model_validate(row)


def create_vm(db: Session, cluster: PlatformCluster, data: PlatformVirtualMachineCreate) -> PlatformVirtualMachine:
    slug = _slugify(data.slug or data.name)
    if get_vm_by_slug(db, slug) is not None:
        raise HTTPException(status_code=409, detail="vm-slug finnes allerede")
    if data.device_id is not None:
        if dcim_svc.get_device(db, data.device_id) is None:
            raise HTTPException(status_code=404, detail="enhet ikke funnet")
        if not device_is_member(db, cluster.id, data.device_id):
            raise HTTPException(status_code=400, detail="enheten er ikke medlem av clusteret")
    row = PlatformVirtualMachine(
        name=data.name.strip(),
        slug=slug,
        cluster_id=cluster.id,
        device_id=data.device_id,
        status=data.status,
    )
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="vm-slug finnes allerede")
    db.refresh(row)
    return row


def get_storage_pool_by_slug(db: Session, slug: str) -> PlatformStoragePool | None:
    return db.execute(select(PlatformStoragePool).where(PlatformStoragePool.slug == slug)).scalar_one_or_none()


def storage_to_read(row: PlatformStoragePool) -> PlatformStoragePoolRead:
    return PlatformStoragePoolRead.model_validate(row)


def create_storage_pool(
    db: Session,
    cluster: PlatformCluster,
    data: PlatformStoragePoolCreate,
) -> PlatformStoragePool:
    slug = _slugify(data.slug or data.name)
    if get_storage_pool_by_slug(db, slug) is not None:
        raise HTTPException(status_code=409, detail="lagringspool-slug finnes allerede")
    row = PlatformStoragePool(
        name=data.name.strip(),
        slug=slug,
        cluster_id=cluster.id,
        kind=data.kind,
        status=data.status,
    )
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="lagringspool-slug finnes allerede")
    db.refresh(row)
    return row


def get_vif_by_slug(db: Session, slug: str) -> PlatformVirtualInterface | None:
    return db.execute(select(PlatformVirtualInterface).where(PlatformVirtualInterface.slug == slug)).scalar_one_or_none()


def vif_to_read(row: PlatformVirtualInterface) -> PlatformVirtualInterfaceRead:
    return PlatformVirtualInterfaceRead.model_validate(row)


def create_vif(
    db: Session,
    cluster: PlatformCluster,
    vm: PlatformVirtualMachine,
    data: PlatformVirtualInterfaceCreate,
) -> PlatformVirtualInterface:
    if vm.cluster_id != cluster.id:
        raise HTTPException(status_code=404, detail="vm ikke funnet")
    slug = _slugify(data.slug or data.name)
    if get_vif_by_slug(db, slug) is not None:
        raise HTTPException(status_code=409, detail="vif-slug finnes allerede")
    row = PlatformVirtualInterface(
        name=data.name.strip(),
        slug=slug,
        vm_id=vm.id,
        status=data.status,
    )
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="vif-slug finnes allerede")
    db.refresh(row)
    return row


def delete_vif(db: Session, cluster: PlatformCluster, vm_id: int, iface_id: int) -> None:
    vm = db.get(PlatformVirtualMachine, vm_id)
    if vm is None or vm.cluster_id != cluster.id:
        raise HTTPException(status_code=404, detail="vm ikke funnet")
    row = db.get(PlatformVirtualInterface, iface_id)
    if row is None or row.vm_id != vm.id:
        raise HTTPException(status_code=404, detail="virtuelt grensesnitt ikke funnet")
    db.delete(row)
    db.commit()


def delete_storage_pool(db: Session, cluster: PlatformCluster, pool_id: int) -> None:
    row = db.get(PlatformStoragePool, pool_id)
    if row is None or row.cluster_id != cluster.id:
        raise HTTPException(status_code=404, detail="lagringspool ikke funnet")
    db.delete(row)
    db.commit()


def delete_vm(db: Session, cluster: PlatformCluster, vm_id: int) -> None:
    row = db.get(PlatformVirtualMachine, vm_id)
    if row is None or row.cluster_id != cluster.id:
        raise HTTPException(status_code=404, detail="vm ikke funnet")
    db.delete(row)
    db.commit()


def shared_site_id(db: Session, device_ids: list[int]) -> int | None:
    sites: set[int] = set()
    for did in device_ids:
        sid = dcim_svc.device_effective_site_id(db, did)
        if sid is not None:
            sites.add(int(sid))
    if len(sites) == 1:
        return next(iter(sites))
    return None
