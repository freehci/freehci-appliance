"""Cluster-inventar under Plattform."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.platform import (
    PlatformClusterCreate,
    PlatformClusterMemberCreate,
    PlatformClusterMemberRead,
    PlatformClusterRead,
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
