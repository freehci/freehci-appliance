"""Cluster-inventar under Plattform."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
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
from app.services import platform as plat_svc

router = APIRouter(prefix="/clusters", tags=["platform"])


@router.get("", response_model=list[PlatformClusterRead])
def list_clusters(db: Session = Depends(get_db)) -> list[PlatformClusterRead]:
    return [plat_svc.cluster_to_read(r) for r in plat_svc.list_clusters(db)]


@router.post("", response_model=PlatformClusterRead)
def create_cluster(data: PlatformClusterCreate, db: Session = Depends(get_db)) -> PlatformClusterRead:
    return plat_svc.cluster_to_read(plat_svc.create_cluster(db, data))


@router.get("/{cluster_id}", response_model=PlatformClusterRead)
def get_cluster(cluster_id: int, db: Session = Depends(get_db)) -> PlatformClusterRead:
    row = plat_svc.get_cluster(db, cluster_id)
    if row is None:
        raise HTTPException(status_code=404, detail="cluster ikke funnet")
    return plat_svc.cluster_to_read(row)


@router.delete("/{cluster_id}", status_code=204)
def delete_cluster(cluster_id: int, db: Session = Depends(get_db)) -> None:
    row = plat_svc.get_cluster(db, cluster_id)
    if row is None:
        raise HTTPException(status_code=404, detail="cluster ikke funnet")
    plat_svc.delete_cluster(db, row)


@router.post("/{cluster_id}/members", response_model=PlatformClusterMemberRead)
def add_member(
    cluster_id: int,
    data: PlatformClusterMemberCreate,
    db: Session = Depends(get_db),
) -> PlatformClusterMemberRead:
    row = plat_svc.get_cluster(db, cluster_id)
    if row is None:
        raise HTTPException(status_code=404, detail="cluster ikke funnet")
    return PlatformClusterMemberRead.model_validate(plat_svc.add_member(db, row, data))


@router.delete("/{cluster_id}/members/{member_id}", status_code=204)
def remove_member(cluster_id: int, member_id: int, db: Session = Depends(get_db)) -> None:
    row = plat_svc.get_cluster(db, cluster_id)
    if row is None:
        raise HTTPException(status_code=404, detail="cluster ikke funnet")
    plat_svc.remove_member(db, row, member_id)


@router.post("/{cluster_id}/vms", response_model=PlatformVirtualMachineRead)
def create_vm(
    cluster_id: int,
    data: PlatformVirtualMachineCreate,
    db: Session = Depends(get_db),
) -> PlatformVirtualMachineRead:
    row = plat_svc.get_cluster(db, cluster_id)
    if row is None:
        raise HTTPException(status_code=404, detail="cluster ikke funnet")
    return plat_svc.vm_to_read(plat_svc.create_vm(db, row, data))


@router.delete("/{cluster_id}/vms/{vm_id}", status_code=204)
def delete_vm(cluster_id: int, vm_id: int, db: Session = Depends(get_db)) -> None:
    row = plat_svc.get_cluster(db, cluster_id)
    if row is None:
        raise HTTPException(status_code=404, detail="cluster ikke funnet")
    plat_svc.delete_vm(db, row, vm_id)


@router.post("/{cluster_id}/storage-pools", response_model=PlatformStoragePoolRead)
def create_storage_pool(
    cluster_id: int,
    data: PlatformStoragePoolCreate,
    db: Session = Depends(get_db),
) -> PlatformStoragePoolRead:
    row = plat_svc.get_cluster(db, cluster_id)
    if row is None:
        raise HTTPException(status_code=404, detail="cluster ikke funnet")
    return plat_svc.storage_to_read(plat_svc.create_storage_pool(db, row, data))


@router.delete("/{cluster_id}/storage-pools/{pool_id}", status_code=204)
def delete_storage_pool(cluster_id: int, pool_id: int, db: Session = Depends(get_db)) -> None:
    row = plat_svc.get_cluster(db, cluster_id)
    if row is None:
        raise HTTPException(status_code=404, detail="cluster ikke funnet")
    plat_svc.delete_storage_pool(db, row, pool_id)


@router.post("/{cluster_id}/vms/{vm_id}/interfaces", response_model=PlatformVirtualInterfaceRead)
def create_vif(
    cluster_id: int,
    vm_id: int,
    data: PlatformVirtualInterfaceCreate,
    db: Session = Depends(get_db),
) -> PlatformVirtualInterfaceRead:
    cluster = plat_svc.get_cluster(db, cluster_id)
    if cluster is None:
        raise HTTPException(status_code=404, detail="cluster ikke funnet")
    vm = plat_svc.get_vm(db, vm_id)
    if vm is None:
        raise HTTPException(status_code=404, detail="vm ikke funnet")
    return plat_svc.vif_to_read(plat_svc.create_vif(db, cluster, vm, data))


@router.delete("/{cluster_id}/vms/{vm_id}/interfaces/{iface_id}", status_code=204)
def delete_vif(cluster_id: int, vm_id: int, iface_id: int, db: Session = Depends(get_db)) -> None:
    cluster = plat_svc.get_cluster(db, cluster_id)
    if cluster is None:
        raise HTTPException(status_code=404, detail="cluster ikke funnet")
    plat_svc.delete_vif(db, cluster, vm_id, iface_id)
