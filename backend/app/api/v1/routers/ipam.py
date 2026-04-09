"""IPAM REST API (IPv4 prefiks per site)."""

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.ipam import (
    Ipv4AddressPatch,
    Ipv4AddressRead,
    Ipv4AddressRequest,
    Ipv4PrefixCreate,
    Ipv4PrefixExploreRead,
    Ipv4PrefixRead,
    Ipv4PrefixUpdate,
    SubnetScanCreate,
    SubnetScanDetailRead,
    SubnetScanRead,
    UserCreate,
    UserRead,
)
from app.services import ipam as ipam_svc
from app.services import ipam_address as addr_svc
from app.services import ipam_subnet_scan as scan_svc

router = APIRouter(prefix="/ipam", tags=["ipam"])


@router.get("/ipv4-prefixes", response_model=list[Ipv4PrefixRead])
def list_ipv4_prefixes(
    site_id: int | None = Query(None, description="Filtrer på DCIM site-id"),
    db: Session = Depends(get_db),
) -> list[Ipv4PrefixRead]:
    return ipam_svc.list_ipv4_prefixes(db, site_id=site_id)


@router.post("/ipv4-prefixes", response_model=Ipv4PrefixRead)
def create_ipv4_prefix(data: Ipv4PrefixCreate, db: Session = Depends(get_db)) -> Ipv4PrefixRead:
    return ipam_svc.create_ipv4_prefix(db, data)


@router.get("/ipv4-prefixes/{prefix_id}/explore", response_model=Ipv4PrefixExploreRead)
def explore_ipv4_prefix(prefix_id: int, db: Session = Depends(get_db)) -> Ipv4PrefixExploreRead:
    return ipam_svc.explore_ipv4_prefix(db, prefix_id)


@router.get("/ipv4-prefixes/{prefix_id}", response_model=Ipv4PrefixRead)
def get_ipv4_prefix(prefix_id: int, db: Session = Depends(get_db)) -> Ipv4PrefixRead:
    row = ipam_svc.get_ipv4_prefix(db, prefix_id)
    if row is None:
        raise HTTPException(status_code=404, detail="prefiks ikke funnet")
    return ipam_svc.ipv4_prefix_read(db, row)


@router.patch("/ipv4-prefixes/{prefix_id}", response_model=Ipv4PrefixRead)
def patch_ipv4_prefix(
    prefix_id: int,
    data: Ipv4PrefixUpdate,
    db: Session = Depends(get_db),
) -> Ipv4PrefixRead:
    row = ipam_svc.get_ipv4_prefix(db, prefix_id)
    if row is None:
        raise HTTPException(status_code=404, detail="prefiks ikke funnet")
    return ipam_svc.update_ipv4_prefix(db, row, data)


@router.delete("/ipv4-prefixes/{prefix_id}", status_code=204)
def delete_ipv4_prefix(prefix_id: int, db: Session = Depends(get_db)) -> None:
    row = ipam_svc.get_ipv4_prefix(db, prefix_id)
    if row is None:
        raise HTTPException(status_code=404, detail="prefiks ikke funnet")
    ipam_svc.delete_ipv4_prefix(db, row)


@router.post("/subnet-scans", response_model=SubnetScanRead)
def create_subnet_scan(
    data: SubnetScanCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
) -> SubnetScanRead:
    row = scan_svc.create_pending_scan(db, ipv4_prefix_id=data.ipv4_prefix_id)
    background_tasks.add_task(scan_svc.run_scan_background, row.id)
    return scan_svc.scan_to_read(row)


@router.get("/subnet-scans", response_model=list[SubnetScanRead])
def list_subnet_scans(
    site_id: int | None = Query(None),
    ipv4_prefix_id: int | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
) -> list[SubnetScanRead]:
    rows = scan_svc.list_scans(db, site_id=site_id, ipv4_prefix_id=ipv4_prefix_id, limit=limit)
    return [scan_svc.scan_to_read(r) for r in rows]


@router.get("/subnet-scans/{scan_id}", response_model=SubnetScanDetailRead)
def get_subnet_scan(scan_id: int, db: Session = Depends(get_db)) -> SubnetScanDetailRead:
    row = scan_svc.get_scan_with_hosts(db, scan_id)
    if row is None:
        raise HTTPException(status_code=404, detail="skann ikke funnet")
    return scan_svc.scan_to_detail_read(row)


@router.get("/users", response_model=list[UserRead])
def list_users(limit: int = Query(200, ge=1, le=500), db: Session = Depends(get_db)) -> list[UserRead]:
    return addr_svc.list_users(db, limit=limit)


@router.post("/users", response_model=UserRead)
def create_user(data: UserCreate, db: Session = Depends(get_db)) -> UserRead:
    return addr_svc.create_user(db, data)


@router.get("/ipv4-addresses", response_model=list[Ipv4AddressRead])
def list_ipv4_addresses(
    site_id: int | None = Query(None),
    ipv4_prefix_id: int | None = Query(None),
    status: str | None = Query(None),
    limit: int = Query(200, ge=1, le=500),
    db: Session = Depends(get_db),
) -> list[Ipv4AddressRead]:
    return addr_svc.list_ipv4_addresses(db, site_id=site_id, ipv4_prefix_id=ipv4_prefix_id, status=status, limit=limit)


@router.patch("/ipv4-addresses/{addr_id}", response_model=Ipv4AddressRead)
def patch_ipv4_address(addr_id: int, data: Ipv4AddressPatch, db: Session = Depends(get_db)) -> Ipv4AddressRead:
    row = addr_svc.get_ipv4_address(db, addr_id)
    if row is None:
        raise HTTPException(status_code=404, detail="IP-adresse ikke funnet")
    return addr_svc.patch_ipv4_address(db, row, data)


@router.post("/ipv4-addresses/request", response_model=Ipv4AddressRead)
def request_ipv4_address(data: Ipv4AddressRequest, db: Session = Depends(get_db)) -> Ipv4AddressRead:
    return addr_svc.request_ipv4_address(db, data)
