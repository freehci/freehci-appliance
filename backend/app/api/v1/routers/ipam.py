"""IPAM REST API (IPv4 prefiks per site)."""

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.ipam import (
    Ipv4AddressBatchRead,
    Ipv4AddressBatchRequest,
    Ipv4AddressEnsure,
    Ipv4AddressPatch,
    Ipv4AddressRead,
    Ipv4AddressRequest,
    Ipv4PrefixCreate,
    Ipv4PrefixExploreRead,
    Ipv4PrefixRead,
    Ipv4PrefixUpdate,
    PrefixAddressGridRead,
    SubnetScanCreate,
    SubnetScanDetailRead,
    SubnetScanRead,
    UserCreate,
    UserRead,
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
from app.services import ipam as ipam_svc
from app.services import ipam_address as addr_svc
from app.services import ipam_facilities as fac_svc
from app.services import ipam_prefix_grid as grid_svc
from app.services import ipam_subnet_scan as scan_svc

router = APIRouter(prefix="/ipam", tags=["ipam"])


@router.get("/ipv4-prefixes", response_model=list[Ipv4PrefixRead])
def list_ipv4_prefixes(
    site_id: int | None = Query(None, description="Filtrer på DCIM site-id"),
    tenant_id: int | None = Query(None, description="Filtrer på tenant-id (colo/kunde)"),
    db: Session = Depends(get_db),
) -> list[Ipv4PrefixRead]:
    return ipam_svc.list_ipv4_prefixes(db, site_id=site_id, tenant_id=tenant_id)


@router.post("/ipv4-prefixes", response_model=Ipv4PrefixRead)
def create_ipv4_prefix(data: Ipv4PrefixCreate, db: Session = Depends(get_db)) -> Ipv4PrefixRead:
    return ipam_svc.create_ipv4_prefix(db, data)


@router.get("/ipv4-prefixes/{prefix_id}/explore", response_model=Ipv4PrefixExploreRead)
def explore_ipv4_prefix(prefix_id: int, db: Session = Depends(get_db)) -> Ipv4PrefixExploreRead:
    return ipam_svc.explore_ipv4_prefix(db, prefix_id)


@router.get("/ipv4-prefixes/{prefix_id}/address-grid", response_model=PrefixAddressGridRead)
def get_prefix_address_grid(prefix_id: int, db: Session = Depends(get_db)) -> PrefixAddressGridRead:
    return grid_svc.build_prefix_address_grid(db, prefix_id)


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


@router.post("/ipv4-addresses/ensure", response_model=Ipv4AddressRead)
def ensure_ipv4_address(data: Ipv4AddressEnsure, db: Session = Depends(get_db)) -> Ipv4AddressRead:
    row = grid_svc.ensure_ipv4_address_row(db, ipv4_prefix_id=data.ipv4_prefix_id, address=data.address)
    return addr_svc._ipv4_address_read(db, row)


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


@router.post("/ipv4-addresses/request-batch", response_model=Ipv4AddressBatchRead)
def request_ipv4_addresses_batch(data: Ipv4AddressBatchRequest, db: Session = Depends(get_db)) -> Ipv4AddressBatchRead:
    return addr_svc.request_ipv4_addresses_batch(db, data)


@router.post("/ipv4-addresses/{addr_id}/release", response_model=Ipv4AddressRead)
def release_ipv4_address(addr_id: int, db: Session = Depends(get_db)) -> Ipv4AddressRead:
    row = addr_svc.get_ipv4_address(db, addr_id)
    if row is None:
        raise HTTPException(status_code=404, detail="IP-adresse ikke funnet")
    return addr_svc.release_ipv4_address(db, row)


# --- VRF / VLAN / samband ---


@router.get("/vrfs", response_model=list[IpamVrfRead])
def list_ipam_vrfs(
    site_id: int | None = Query(None, description="Filtrer på DCIM site-id"),
    db: Session = Depends(get_db),
) -> list[IpamVrfRead]:
    return [fac_svc.vrf_to_read(r) for r in fac_svc.list_vrfs(db, site_id=site_id)]


@router.post("/vrfs", response_model=IpamVrfRead)
def create_ipam_vrf(data: IpamVrfCreate, db: Session = Depends(get_db)) -> IpamVrfRead:
    try:
        row = fac_svc.create_vrf(db, data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except IntegrityError as e:
        raise HTTPException(status_code=409, detail="VRF med samme navn finnes på denne siten") from e
    return fac_svc.vrf_to_read(row)


@router.delete("/vrfs/{vrf_id}", status_code=204)
def delete_ipam_vrf(vrf_id: int, db: Session = Depends(get_db)) -> None:
    row = fac_svc.get_vrf(db, vrf_id)
    if row is None:
        raise HTTPException(status_code=404, detail="VRF ikke funnet")
    fac_svc.delete_vrf(db, row)


@router.get("/vlans", response_model=list[IpamVlanRead])
def list_ipam_vlans(
    site_id: int | None = Query(None, description="Filtrer på DCIM site-id"),
    db: Session = Depends(get_db),
) -> list[IpamVlanRead]:
    return [fac_svc.vlan_to_read(r) for r in fac_svc.list_vlans(db, site_id=site_id)]


@router.post("/vlans", response_model=IpamVlanRead)
def create_ipam_vlan(data: IpamVlanCreate, db: Session = Depends(get_db)) -> IpamVlanRead:
    try:
        row = fac_svc.create_vlan(db, data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except IntegrityError as e:
        raise HTTPException(status_code=409, detail="VLAN-ID finnes allerede på denne siten") from e
    return fac_svc.vlan_to_read(row)


@router.delete("/vlans/{vlan_id}", status_code=204)
def delete_ipam_vlan(vlan_id: int, db: Session = Depends(get_db)) -> None:
    row = fac_svc.get_vlan(db, vlan_id)
    if row is None:
        raise HTTPException(status_code=404, detail="VLAN ikke funnet")
    fac_svc.delete_vlan(db, row)


@router.get("/circuits", response_model=list[IpamCircuitRead])
def list_ipam_circuits(
    tenant_id: int | None = Query(None, description="Filtrer på tenant-id"),
    db: Session = Depends(get_db),
) -> list[IpamCircuitRead]:
    return [fac_svc.circuit_to_read(r) for r in fac_svc.list_circuits(db, tenant_id=tenant_id)]


@router.post("/circuits", response_model=IpamCircuitRead)
def create_ipam_circuit(data: IpamCircuitCreate, db: Session = Depends(get_db)) -> IpamCircuitRead:
    try:
        row = fac_svc.create_circuit(db, data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except IntegrityError as e:
        raise HTTPException(status_code=409, detail="sambandsnummer finnes allerede for denne tenanten") from e
    return fac_svc.circuit_to_read(row)


@router.patch("/circuits/{circuit_id}", response_model=IpamCircuitRead)
def patch_ipam_circuit(
    circuit_id: int,
    data: IpamCircuitUpdate,
    db: Session = Depends(get_db),
) -> IpamCircuitRead:
    row = fac_svc.get_circuit(db, circuit_id)
    if row is None:
        raise HTTPException(status_code=404, detail="samband ikke funnet")
    return fac_svc.circuit_to_read(fac_svc.update_circuit(db, row, data))


@router.delete("/circuits/{circuit_id}", status_code=204)
def delete_ipam_circuit(circuit_id: int, db: Session = Depends(get_db)) -> None:
    row = fac_svc.get_circuit(db, circuit_id)
    if row is None:
        raise HTTPException(status_code=404, detail="samband ikke funnet")
    fac_svc.delete_circuit(db, row)


@router.get("/circuits/{circuit_id}/terminations", response_model=list[IpamCircuitTerminationRead])
def list_circuit_terminations(circuit_id: int, db: Session = Depends(get_db)) -> list[IpamCircuitTerminationRead]:
    row = fac_svc.get_circuit(db, circuit_id)
    if row is None:
        raise HTTPException(status_code=404, detail="samband ikke funnet")
    return [fac_svc.termination_to_read(t) for t in fac_svc.list_circuit_terminations(db, circuit_id)]


@router.post("/circuits/{circuit_id}/terminations", response_model=IpamCircuitTerminationRead)
def upsert_circuit_termination(
    circuit_id: int,
    data: IpamCircuitTerminationCreate,
    db: Session = Depends(get_db),
) -> IpamCircuitTerminationRead:
    row = fac_svc.get_circuit(db, circuit_id)
    if row is None:
        raise HTTPException(status_code=404, detail="samband ikke funnet")
    try:
        t = fac_svc.upsert_circuit_termination(db, row, data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except IntegrityError as e:
        raise HTTPException(status_code=409, detail="kunne ikke lagre terminering") from e
    return fac_svc.termination_to_read(t)
