"""API for nettverksskann (maler, jobber, oppdagelseskø)."""

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.network_scan import (
    NetworkScanDiscoveryApprove,
    NetworkScanDiscoveryRead,
    NetworkScanJobCreate,
    NetworkScanJobDetailRead,
    NetworkScanJobRead,
    NetworkScanPrefixBindingCreate,
    NetworkScanPrefixBindingRead,
    NetworkScanTemplateCreate,
    NetworkScanTemplateRead,
)
from app.services import network_scan as netscan_svc

router = APIRouter(prefix="/network-scans", tags=["network-scans"])


@router.get("/templates", response_model=list[NetworkScanTemplateRead])
def list_templates(db: Session = Depends(get_db)) -> list[NetworkScanTemplateRead]:
    return netscan_svc.list_templates(db)


@router.post("/templates", response_model=NetworkScanTemplateRead)
def create_template(
    data: NetworkScanTemplateCreate,
    db: Session = Depends(get_db),
) -> NetworkScanTemplateRead:
    return netscan_svc.create_custom_template(db, data)


@router.get("/prefix-bindings", response_model=list[NetworkScanPrefixBindingRead])
def list_prefix_bindings(
    ipv4_prefix_id: int | None = Query(None),
    db: Session = Depends(get_db),
) -> list[NetworkScanPrefixBindingRead]:
    return netscan_svc.list_prefix_bindings(db, ipv4_prefix_id=ipv4_prefix_id)


@router.post("/prefix-bindings", response_model=NetworkScanPrefixBindingRead)
def create_prefix_binding(
    data: NetworkScanPrefixBindingCreate,
    db: Session = Depends(get_db),
) -> NetworkScanPrefixBindingRead:
    return netscan_svc.create_prefix_binding(db, data)


@router.delete("/prefix-bindings/{binding_id}", status_code=204)
def delete_prefix_binding(binding_id: int, db: Session = Depends(get_db)) -> None:
    netscan_svc.delete_prefix_binding(db, binding_id)


@router.post("/jobs", response_model=NetworkScanJobRead)
def create_job(
    data: NetworkScanJobCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
) -> NetworkScanJobRead:
    row = netscan_svc.create_job(db, data)
    background_tasks.add_task(netscan_svc.execute_network_scan_job, row.id)
    return row


@router.get("/jobs", response_model=list[NetworkScanJobRead])
def list_jobs(
    ipv4_prefix_id: int | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
) -> list[NetworkScanJobRead]:
    return netscan_svc.list_jobs(db, ipv4_prefix_id=ipv4_prefix_id, limit=limit)


@router.get("/jobs/{job_id}", response_model=NetworkScanJobDetailRead)
def get_job(job_id: int, db: Session = Depends(get_db)) -> NetworkScanJobDetailRead:
    row = netscan_svc.get_job_detail(db, job_id)
    if row is None:
        raise HTTPException(status_code=404, detail="jobb ikke funnet")
    return row


@router.delete("/jobs/{job_id}", status_code=204)
def delete_job(job_id: int, db: Session = Depends(get_db)) -> None:
    netscan_svc.delete_job(db, job_id)


@router.get("/discoveries", response_model=list[NetworkScanDiscoveryRead])
def list_discoveries(
    status: str | None = Query(None, description="f.eks. pending, promoted, rejected, auto_promoted"),
    site_id: int | None = Query(None),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
) -> list[NetworkScanDiscoveryRead]:
    return netscan_svc.list_discoveries(db, status=status, site_id=site_id, limit=limit)


@router.patch("/discoveries/{discovery_id}", response_model=NetworkScanDiscoveryRead)
def approve_discovery(
    discovery_id: int,
    data: NetworkScanDiscoveryApprove,
    db: Session = Depends(get_db),
) -> NetworkScanDiscoveryRead:
    return netscan_svc.approve_discovery(db, discovery_id, data)


@router.post("/discoveries/{discovery_id}/reject", status_code=204)
def reject_discovery(discovery_id: int, db: Session = Depends(get_db)) -> None:
    netscan_svc.reject_discovery(db, discovery_id)
