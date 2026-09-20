"""IPAM REST API (IPv4 prefiks per site)."""

from fastapi import APIRouter, BackgroundTasks, Depends, Header, HTTPException, Query, Response
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.ipam import (
    Ipv4AddressBatchRead,
    Ipv4AddressBatchRequest,
    Ipv4AddressBind,
    Ipv4AddressEnsure,
    Ipv4AddressPatch,
    Ipv4AddressRead,
    Ipv4AddressRequest,
    Ipv4AvailablePrefixesRead,
    Ipv4AvailableRangesRead,
    Ipv4PrefixAllocate,
    Ipv4PrefixCreate,
    Ipv4PrefixEnsure,
    Ipv4PrefixExploreRead,
    Ipv4PrefixRead,
    Ipv4PrefixSplitEqualRequest,
    Ipv4PrefixSplitEqualResponse,
    Ipv4PrefixSplitRequest,
    Ipv4PrefixSplitResponse,
    Ipv4PrefixUpdate,
    PrefixAddressGridRead,
    SubnetScanCreate,
    SubnetScanDetailRead,
    SubnetScanRead,
    UserCreate,
    UserRead,
    IpamCircuitClassify,
    IpamCircuitClassifyRead,
    IpamCircuitCreate,
    IpamCircuitRead,
    IpamCircuitTerminationCreate,
    IpamCircuitTerminationRead,
    IpamCircuitUpdate,
    IpamProviderAccountCreate,
    IpamProviderAccountRead,
    IpamProviderAccountUpdate,
    IpamProviderCreate,
    IpamProviderRead,
    IpamProviderUpdate,
    IpamTunnelCreate,
    IpamTunnelEndpointCreate,
    IpamTunnelEndpointRead,
    IpamTunnelPeerCreate,
    IpamTunnelPeerRead,
    IpamTunnelPeerUpdate,
    IpamTunnelProfileCreate,
    IpamTunnelProfileRead,
    IpamTunnelProfileUpdate,
    IpamTunnelRead,
    IpamTunnelUpdate,
    IpamVpnServiceCreate,
    IpamVpnServiceRead,
    IpamVpnServiceUpdate,
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
    IpamAuditEventRead,
    IpamBulkEnsure,
    IpamBulkEnsureRead,
    IpamWebhookCreate,
    IpamWebhookDeliveryRead,
    IpamWebhookRead,
    PrefixDriftRead,
    SiteDriftRead,
    Ipv6AddressEnsure,
    Ipv6AddressRead,
    Ipv6AddressRequest,
    Ipv6AvailableRangesRead,
    Ipv6PrefixAddressGridRead,
    Ipv6PrefixAllocate,
    Ipv6PrefixCreate,
    Ipv6PrefixEnsure,
    Ipv6PrefixRead,
    Ipv6PrefixSplitEqualRequest,
    Ipv6PrefixSplitEqualResponse,
    Ipv6PrefixSplitRequest,
    Ipv6PrefixSplitResponse,
)
from app.services import ipam as ipam_svc
from app.services import ipam_address as addr_svc
from app.services import ipam_idempotency as idem_svc
from app.services import ipam_prefix_alloc as alloc_svc
from app.services import ipam_prefix_split as split_svc
from app.services import ipam_facilities as fac_svc
from app.services import ipam_providers as prov_svc
from app.services import ipam_vpn as vpn_svc
from app.services import ipam_prefix_grid as grid_svc
from app.services import ipam_subnet_scan as scan_svc
from app.services import ipam_ipv6 as ipv6_svc
from app.services import ipam_ipv6_grid as ipv6_grid_svc
from app.services import ipam_ipv6_split as ipv6_split_svc
from app.services import ipam_audit as audit_svc
from app.services import ipam_etag as etag_svc
from app.services import ipam_sync as sync_svc
from app.services import ipam_webhooks as hook_svc

router = APIRouter(prefix="/ipam", tags=["ipam"])


@router.get("/ipv4-prefixes", response_model=list[Ipv4PrefixRead])
def list_ipv4_prefixes(
    response: Response,
    site_id: int | None = Query(None, description="Filtrer på DCIM site-id"),
    tenant_id: int | None = Query(None, description="Filtrer på tenant-id (colo/kunde)"),
    vlan_id: int | None = Query(None, description="Filtrer på VLAN-id"),
    vrf_id: int | None = Query(None, description="Filtrer på VRF-id"),
    cidr: str | None = Query(None, description="Eksakt IPv4 CIDR (normaliseres)"),
    name: str | None = Query(None, description="Eksakt prefiksnavn (case-insensitive)"),
    slug: str | None = Query(None, description="Eksakt slug"),
    q: str | None = Query(None, description="Søk i name, slug og cidr"),
    address: str | None = Query(None, description="Prefiks som inneholder denne IPv4-adressen"),
    role: str | None = Query(None),
    status: str | None = Query(None),
    limit: int | None = Query(None, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
) -> list[Ipv4PrefixRead]:
    items, total = ipam_svc.list_ipv4_prefixes(
        db,
        site_id=site_id,
        tenant_id=tenant_id,
        vlan_id=vlan_id,
        vrf_id=vrf_id,
        cidr=cidr,
        name=name,
        slug=slug,
        q=q,
        address=address,
        role=role,
        status=status,
        limit=limit,
        offset=offset,
    )
    etag_svc.attach_page(response, total=total, offset=offset, count=len(items))
    return items


@router.post("/ipv4-prefixes", response_model=Ipv4PrefixRead)
def create_ipv4_prefix(data: Ipv4PrefixCreate, db: Session = Depends(get_db)) -> Ipv4PrefixRead:
    return ipam_svc.create_ipv4_prefix(db, data)


@router.post("/ipv4-prefixes/ensure", response_model=Ipv4PrefixRead)
def ensure_ipv4_prefix(
    data: Ipv4PrefixEnsure,
    update: bool = Query(False, description="Oppdater eksisterende prefiks til desired state"),
    db: Session = Depends(get_db),
) -> Ipv4PrefixRead:
    return ipam_svc.ensure_ipv4_prefix(db, data, update=update)


@router.get("/ipv4-prefixes/{prefix_id}/explore", response_model=Ipv4PrefixExploreRead)
def explore_ipv4_prefix(prefix_id: int, db: Session = Depends(get_db)) -> Ipv4PrefixExploreRead:
    return ipam_svc.explore_ipv4_prefix(db, prefix_id)


@router.get("/ipv4-prefixes/{prefix_id}/address-grid", response_model=PrefixAddressGridRead)
def get_prefix_address_grid(prefix_id: int, db: Session = Depends(get_db)) -> PrefixAddressGridRead:
    return grid_svc.build_prefix_address_grid(db, prefix_id)


@router.get("/ipv4-prefixes/{prefix_id}/available-prefixes", response_model=Ipv4AvailablePrefixesRead)
def list_available_child_prefixes(
    prefix_id: int,
    prefixlen: int = Query(..., ge=1, le=32),
    limit: int = Query(64, ge=1, le=256),
    db: Session = Depends(get_db),
) -> Ipv4AvailablePrefixesRead:
    row = ipam_svc.get_ipv4_prefix(db, prefix_id)
    if row is None:
        raise HTTPException(status_code=404, detail={"code": "prefix_not_found", "detail": "prefiks ikke funnet"})
    return alloc_svc.list_available_child_prefixes(db, row, prefixlen, limit=limit)


@router.post("/ipv4-prefixes/{prefix_id}/allocate", response_model=Ipv4PrefixRead)
def allocate_child_prefix(
    prefix_id: int,
    data: Ipv4PrefixAllocate,
    db: Session = Depends(get_db),
    idempotency_key: str | None = Header(None, alias="Idempotency-Key"),
) -> Ipv4PrefixRead:
    row = ipam_svc.get_ipv4_prefix(db, prefix_id)
    if row is None:
        raise HTTPException(status_code=404, detail={"code": "prefix_not_found", "detail": "prefiks ikke funnet"})
    return idem_svc.run_idempotent(
        db,
        idempotency_key,
        scope="prefix-allocate",
        payload={"prefix_id": prefix_id, **data.model_dump(mode="json")},
        fn=lambda: alloc_svc.allocate_child_prefix(db, row, data),
    )


@router.get("/ipv4-prefixes/{prefix_id}/available-ranges", response_model=Ipv4AvailableRangesRead)
def get_available_ranges(prefix_id: int, db: Session = Depends(get_db)) -> Ipv4AvailableRangesRead:
    row = ipam_svc.get_ipv4_prefix(db, prefix_id)
    if row is None:
        raise HTTPException(status_code=404, detail={"code": "prefix_not_found", "detail": "prefiks ikke funnet"})
    return alloc_svc.available_ranges(db, row)


@router.get("/ipv4-prefixes/{prefix_id}/drift", response_model=PrefixDriftRead)
def get_ipv4_prefix_drift(prefix_id: int, db: Session = Depends(get_db)) -> PrefixDriftRead:
    return sync_svc.prefix_drift(db, prefix_id)


@router.get("/ipv4-prefixes/{prefix_id}", response_model=Ipv4PrefixRead)
def get_ipv4_prefix(prefix_id: int, response: Response, db: Session = Depends(get_db)) -> Ipv4PrefixRead:
    row = ipam_svc.get_ipv4_prefix(db, prefix_id)
    if row is None:
        raise HTTPException(status_code=404, detail={"code": "prefix_not_found", "detail": "prefiks ikke funnet"})
    etag_svc.attach_etag(response, row)
    return ipam_svc.ipv4_prefix_read(db, row)


@router.patch("/ipv4-prefixes/{prefix_id}", response_model=Ipv4PrefixRead)
def patch_ipv4_prefix(
    prefix_id: int,
    data: Ipv4PrefixUpdate,
    response: Response,
    db: Session = Depends(get_db),
    if_match: str | None = Header(None, alias="If-Match"),
) -> Ipv4PrefixRead:
    row = ipam_svc.get_ipv4_prefix(db, prefix_id)
    if row is None:
        raise HTTPException(status_code=404, detail={"code": "prefix_not_found", "detail": "prefiks ikke funnet"})
    etag_svc.require_if_match(row, if_match)
    body = ipam_svc.update_ipv4_prefix(db, row, data)
    etag_svc.attach_etag(response, row)
    return body


@router.delete("/ipv4-prefixes/{prefix_id}", status_code=204)
def delete_ipv4_prefix(
    prefix_id: int,
    cascade: bool = Query(False, description="Slett underprefiks og inventory-adresser"),
    db: Session = Depends(get_db),
    if_match: str | None = Header(None, alias="If-Match"),
) -> None:
    row = ipam_svc.get_ipv4_prefix(db, prefix_id)
    if row is None:
        raise HTTPException(status_code=404, detail={"code": "prefix_not_found", "detail": "prefiks ikke funnet"})
    etag_svc.require_if_match(row, if_match)
    ipam_svc.delete_ipv4_prefix(db, row, cascade=cascade)


@router.post("/ipv4-prefixes/{prefix_id}/split", response_model=Ipv4PrefixSplitResponse)
def split_ipv4_prefix(
    prefix_id: int,
    data: Ipv4PrefixSplitRequest,
    db: Session = Depends(get_db),
) -> Ipv4PrefixSplitResponse:
    return split_svc.ipv4_prefix_split(db, prefix_id, data)


@router.post("/ipv4-prefixes/{prefix_id}/split-equal", response_model=Ipv4PrefixSplitEqualResponse)
def split_ipv4_prefix_equal(
    prefix_id: int,
    data: Ipv4PrefixSplitEqualRequest,
    db: Session = Depends(get_db),
) -> Ipv4PrefixSplitEqualResponse:
    return split_svc.ipv4_prefix_split_equal(db, prefix_id, data)


@router.post("/subnet-scans", response_model=SubnetScanRead)
def create_subnet_scan(
    data: SubnetScanCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
) -> SubnetScanRead:
    row = scan_svc.create_pending_scan(
        db,
        ipv4_prefix_id=data.ipv4_prefix_id,
        ipv6_prefix_id=data.ipv6_prefix_id,
    )
    background_tasks.add_task(scan_svc.run_scan_background, row.id)
    return scan_svc.scan_to_read(row)


@router.get("/subnet-scans", response_model=list[SubnetScanRead])
def list_subnet_scans(
    site_id: int | None = Query(None),
    ipv4_prefix_id: int | None = Query(None),
    ipv6_prefix_id: int | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
) -> list[SubnetScanRead]:
    rows = scan_svc.list_scans(
        db,
        site_id=site_id,
        ipv4_prefix_id=ipv4_prefix_id,
        ipv6_prefix_id=ipv6_prefix_id,
        limit=limit,
    )
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
def ensure_ipv4_address(
    data: Ipv4AddressEnsure,
    update: bool = Query(False, description="Oppdater eksisterende adresse til desired state"),
    db: Session = Depends(get_db),
) -> Ipv4AddressRead:
    return addr_svc.ensure_ipv4_address(db, data, update=update)


@router.get("/ipv4-addresses", response_model=list[Ipv4AddressRead])
def list_ipv4_addresses(
    response: Response,
    site_id: int | None = Query(None),
    ipv4_prefix_id: int | None = Query(None),
    status: str | None = Query(None),
    address: str | None = Query(None, description="Eksakt IPv4-adresse"),
    q: str | None = Query(None, description="Søk i address, note, hostname, fqdn, dns_name"),
    device_id: int | None = Query(None),
    role: str | None = Query(None),
    limit: int = Query(200, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
) -> list[Ipv4AddressRead]:
    items, total = addr_svc.list_ipv4_addresses(
        db,
        site_id=site_id,
        ipv4_prefix_id=ipv4_prefix_id,
        status=status,
        limit=limit,
        offset=offset,
        address=address,
        q=q,
        device_id=device_id,
        role=role,
    )
    etag_svc.attach_page(response, total=total, offset=offset, count=len(items))
    return items


@router.get("/ipv4-addresses/{addr_id}", response_model=Ipv4AddressRead)
def get_ipv4_address(addr_id: int, response: Response, db: Session = Depends(get_db)) -> Ipv4AddressRead:
    row = addr_svc.get_ipv4_address(db, addr_id)
    if row is None:
        raise HTTPException(status_code=404, detail={"code": "address_not_found", "detail": "IP-adresse ikke funnet"})
    etag_svc.attach_etag(response, row)
    return addr_svc.get_ipv4_address_read(db, addr_id)


@router.patch("/ipv4-addresses/{addr_id}", response_model=Ipv4AddressRead)
def patch_ipv4_address(
    addr_id: int,
    data: Ipv4AddressPatch,
    response: Response,
    db: Session = Depends(get_db),
    if_match: str | None = Header(None, alias="If-Match"),
) -> Ipv4AddressRead:
    row = addr_svc.get_ipv4_address(db, addr_id)
    if row is None:
        raise HTTPException(status_code=404, detail={"code": "address_not_found", "detail": "IP-adresse ikke funnet"})
    etag_svc.require_if_match(row, if_match)
    body = addr_svc.patch_ipv4_address(db, row, data)
    etag_svc.attach_etag(response, row)
    return body


@router.delete("/ipv4-addresses/{addr_id}", status_code=204)
def delete_ipv4_address(
    addr_id: int,
    force: bool = Query(False, description="Hard-slett reserved/assigned uten release"),
    db: Session = Depends(get_db),
    if_match: str | None = Header(None, alias="If-Match"),
) -> None:
    row = addr_svc.get_ipv4_address(db, addr_id)
    if row is None:
        raise HTTPException(status_code=404, detail={"code": "address_not_found", "detail": "IP-adresse ikke funnet"})
    etag_svc.require_if_match(row, if_match)
    addr_svc.delete_ipv4_address(db, row, force=force)


@router.post("/ipv4-addresses/request", response_model=Ipv4AddressRead)
def request_ipv4_address(
    data: Ipv4AddressRequest,
    db: Session = Depends(get_db),
    idempotency_key: str | None = Header(None, alias="Idempotency-Key"),
) -> Ipv4AddressRead:
    return idem_svc.run_idempotent(
        db,
        idempotency_key,
        scope="address-request",
        payload=data.model_dump(mode="json"),
        fn=lambda: addr_svc.request_ipv4_address(db, data),
    )


@router.post("/ipv4-addresses/request-batch", response_model=Ipv4AddressBatchRead)
def request_ipv4_addresses_batch(
    data: Ipv4AddressBatchRequest,
    db: Session = Depends(get_db),
    idempotency_key: str | None = Header(None, alias="Idempotency-Key"),
) -> Ipv4AddressBatchRead:
    return idem_svc.run_idempotent(
        db,
        idempotency_key,
        scope="address-request-batch",
        payload=data.model_dump(mode="json"),
        fn=lambda: addr_svc.request_ipv4_addresses_batch(db, data),
    )


@router.post("/ipv4-addresses/{addr_id}/bind", response_model=Ipv4AddressRead)
def bind_ipv4_address(
    addr_id: int,
    data: Ipv4AddressBind,
    response: Response,
    db: Session = Depends(get_db),
    if_match: str | None = Header(None, alias="If-Match"),
) -> Ipv4AddressRead:
    row = addr_svc.get_ipv4_address(db, addr_id)
    if row is None:
        raise HTTPException(status_code=404, detail={"code": "address_not_found", "detail": "IP-adresse ikke funnet"})
    etag_svc.require_if_match(row, if_match)
    body = addr_svc.bind_ipv4_address(db, row, data.device_id, data.interface_id)
    etag_svc.attach_etag(response, row)
    return body


@router.post("/ipv4-addresses/{addr_id}/release", response_model=Ipv4AddressRead)
def release_ipv4_address(
    addr_id: int,
    response: Response,
    db: Session = Depends(get_db),
    if_match: str | None = Header(None, alias="If-Match"),
) -> Ipv4AddressRead:
    row = addr_svc.get_ipv4_address(db, addr_id)
    if row is None:
        raise HTTPException(status_code=404, detail={"code": "address_not_found", "detail": "IP-adresse ikke funnet"})
    etag_svc.require_if_match(row, if_match)
    body = addr_svc.release_ipv4_address(db, row)
    etag_svc.attach_etag(response, row)
    return body


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
        raise HTTPException(status_code=404, detail={"code": "vrf_ref_missing", "detail": str(e)}) from e
    except IntegrityError as e:
        raise HTTPException(
            status_code=409,
            detail={"code": "vrf_conflict", "detail": "VRF med samme navn eller slug finnes på denne siten"},
        ) from e
    return fac_svc.vrf_to_read(row, created=True)


@router.post("/vrfs/ensure", response_model=IpamVrfRead)
def ensure_ipam_vrf(
    data: IpamVrfEnsure,
    update: bool = Query(False),
    db: Session = Depends(get_db),
) -> IpamVrfRead:
    try:
        row, created = fac_svc.ensure_vrf(db, data, update=update)
    except ValueError as e:
        raise HTTPException(status_code=404, detail={"code": "vrf_ref_missing", "detail": str(e)}) from e
    except IntegrityError as e:
        raise HTTPException(
            status_code=409,
            detail={"code": "vrf_conflict", "detail": "VRF med samme navn eller slug finnes på denne siten"},
        ) from e
    return fac_svc.vrf_to_read(row, created=created)


@router.get("/vrfs/{vrf_id}", response_model=IpamVrfRead)
def get_ipam_vrf(vrf_id: int, db: Session = Depends(get_db)) -> IpamVrfRead:
    row = fac_svc.get_vrf(db, vrf_id)
    if row is None:
        raise HTTPException(status_code=404, detail={"code": "vrf_not_found", "detail": "VRF ikke funnet"})
    return fac_svc.vrf_to_read(row)


@router.patch("/vrfs/{vrf_id}", response_model=IpamVrfRead)
def patch_ipam_vrf(vrf_id: int, data: IpamVrfUpdate, db: Session = Depends(get_db)) -> IpamVrfRead:
    row = fac_svc.get_vrf(db, vrf_id)
    if row is None:
        raise HTTPException(status_code=404, detail={"code": "vrf_not_found", "detail": "VRF ikke funnet"})
    return fac_svc.vrf_to_read(fac_svc.update_vrf(db, row, data))


@router.delete("/vrfs/{vrf_id}", status_code=204)
def delete_ipam_vrf(vrf_id: int, db: Session = Depends(get_db)) -> None:
    row = fac_svc.get_vrf(db, vrf_id)
    if row is None:
        raise HTTPException(status_code=404, detail={"code": "vrf_not_found", "detail": "VRF ikke funnet"})
    fac_svc.delete_vrf(db, row)


@router.get("/vlan-groups", response_model=list[IpamVlanGroupRead])
def list_ipam_vlan_groups(
    site_id: int | None = Query(None, description="Filtrer på DCIM site-id"),
    db: Session = Depends(get_db),
) -> list[IpamVlanGroupRead]:
    return [fac_svc.vlan_group_to_read(r) for r in fac_svc.list_vlan_groups(db, site_id=site_id)]


@router.post("/vlan-groups", response_model=IpamVlanGroupRead)
def create_ipam_vlan_group(data: IpamVlanGroupCreate, db: Session = Depends(get_db)) -> IpamVlanGroupRead:
    try:
        row = fac_svc.create_vlan_group(db, data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail={"code": "vlan_group_ref_missing", "detail": str(e)}) from e
    except IntegrityError as e:
        raise HTTPException(
            status_code=409,
            detail={"code": "vlan_group_conflict", "detail": "VLAN-gruppe med samme navn eller slug finnes på denne siten"},
        ) from e
    return fac_svc.vlan_group_to_read(row)


@router.get("/vlan-groups/{group_id}", response_model=IpamVlanGroupRead)
def get_ipam_vlan_group(group_id: int, db: Session = Depends(get_db)) -> IpamVlanGroupRead:
    row = fac_svc.get_vlan_group(db, group_id)
    if row is None:
        raise HTTPException(status_code=404, detail={"code": "vlan_group_not_found", "detail": "VLAN-gruppe ikke funnet"})
    return fac_svc.vlan_group_to_read(row)


@router.patch("/vlan-groups/{group_id}", response_model=IpamVlanGroupRead)
def patch_ipam_vlan_group(
    group_id: int, data: IpamVlanGroupUpdate, db: Session = Depends(get_db)
) -> IpamVlanGroupRead:
    row = fac_svc.get_vlan_group(db, group_id)
    if row is None:
        raise HTTPException(status_code=404, detail={"code": "vlan_group_not_found", "detail": "VLAN-gruppe ikke funnet"})
    return fac_svc.vlan_group_to_read(fac_svc.update_vlan_group(db, row, data))


@router.delete("/vlan-groups/{group_id}", status_code=204)
def delete_ipam_vlan_group(group_id: int, db: Session = Depends(get_db)) -> None:
    row = fac_svc.get_vlan_group(db, group_id)
    if row is None:
        raise HTTPException(status_code=404, detail={"code": "vlan_group_not_found", "detail": "VLAN-gruppe ikke funnet"})
    fac_svc.delete_vlan_group(db, row)


@router.get("/vlans", response_model=list[IpamVlanRead])
def list_ipam_vlans(
    site_id: int | None = Query(None, description="Filtrer på DCIM site-id"),
    vlan_group_id: int | None = Query(None, description="Filtrer på VLAN-gruppe"),
    db: Session = Depends(get_db),
) -> list[IpamVlanRead]:
    return [fac_svc.vlan_to_read(r) for r in fac_svc.list_vlans(db, site_id=site_id, vlan_group_id=vlan_group_id)]


@router.post("/vlans", response_model=IpamVlanRead)
def create_ipam_vlan(data: IpamVlanCreate, db: Session = Depends(get_db)) -> IpamVlanRead:
    try:
        row = fac_svc.create_vlan(db, data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail={"code": "vlan_ref_missing", "detail": str(e)}) from e
    except IntegrityError as e:
        raise HTTPException(
            status_code=409,
            detail={"code": "vlan_conflict", "detail": "VLAN-ID finnes allerede i gruppen, eller slug er opptatt på siten"},
        ) from e
    return fac_svc.vlan_to_read(row, created=True)


@router.post("/vlans/ensure", response_model=IpamVlanRead)
def ensure_ipam_vlan(
    data: IpamVlanEnsure,
    update: bool = Query(False),
    db: Session = Depends(get_db),
) -> IpamVlanRead:
    try:
        row, created = fac_svc.ensure_vlan(db, data, update=update)
    except ValueError as e:
        raise HTTPException(status_code=404, detail={"code": "vlan_ref_missing", "detail": str(e)}) from e
    except IntegrityError as e:
        raise HTTPException(
            status_code=409,
            detail={"code": "vlan_conflict", "detail": "VLAN-ID finnes allerede i gruppen, eller slug er opptatt på siten"},
        ) from e
    return fac_svc.vlan_to_read(row, created=created)


@router.get("/vlans/{vlan_id}", response_model=IpamVlanRead)
def get_ipam_vlan(vlan_id: int, db: Session = Depends(get_db)) -> IpamVlanRead:
    row = fac_svc.get_vlan(db, vlan_id)
    if row is None:
        raise HTTPException(status_code=404, detail={"code": "vlan_not_found", "detail": "VLAN ikke funnet"})
    return fac_svc.vlan_to_read(row)


@router.patch("/vlans/{vlan_id}", response_model=IpamVlanRead)
def patch_ipam_vlan(vlan_id: int, data: IpamVlanUpdate, db: Session = Depends(get_db)) -> IpamVlanRead:
    row = fac_svc.get_vlan(db, vlan_id)
    if row is None:
        raise HTTPException(status_code=404, detail={"code": "vlan_not_found", "detail": "VLAN ikke funnet"})
    try:
        return fac_svc.vlan_to_read(fac_svc.update_vlan(db, row, data))
    except ValueError as e:
        raise HTTPException(status_code=404, detail={"code": "vlan_ref_missing", "detail": str(e)}) from e


@router.delete("/vlans/{vlan_id}", status_code=204)
def delete_ipam_vlan(vlan_id: int, db: Session = Depends(get_db)) -> None:
    row = fac_svc.get_vlan(db, vlan_id)
    if row is None:
        raise HTTPException(status_code=404, detail={"code": "vlan_not_found", "detail": "VLAN ikke funnet"})
    fac_svc.delete_vlan(db, row)


@router.get("/circuits", response_model=list[IpamCircuitRead])
def list_ipam_circuits(
    tenant_id: int | None = Query(None, description="Filtrer på tenant-id"),
    site_id: int | None = Query(None, description="Filtrer på A- eller Z-site"),
    layer: str | None = Query(None, description="transport eller overlay"),
    needs_classification: bool | None = Query(None),
    db: Session = Depends(get_db),
) -> list[IpamCircuitRead]:
    return [
        fac_svc.circuit_to_read(r)
        for r in fac_svc.list_circuits(
            db,
            tenant_id=tenant_id,
            site_id=site_id,
            layer=layer,
            needs_classification=needs_classification,
        )
    ]


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
    return [fac_svc.termination_to_read(db, t) for t in fac_svc.list_circuit_terminations(db, circuit_id)]


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
    return fac_svc.termination_to_read(db, t)


@router.post("/circuits/{circuit_id}/classify", response_model=IpamCircuitClassifyRead)
def classify_ipam_circuit(
    circuit_id: int,
    data: IpamCircuitClassify,
    db: Session = Depends(get_db),
) -> IpamCircuitClassifyRead:
    row = fac_svc.get_circuit(db, circuit_id)
    if row is None:
        raise HTTPException(status_code=404, detail="samband ikke funnet")
    stored_type = row.circuit_type
    circuit, vpn = fac_svc.classify_circuit(db, row, data)
    if circuit.circuit_type != stored_type:
        raise HTTPException(status_code=500, detail="klassifisering endret circuit_type — avbrutt")
    return IpamCircuitClassifyRead(
        circuit=fac_svc.circuit_to_read(circuit),
        vpn_service_id=vpn.id if vpn is not None else None,
    )


@router.get("/providers", response_model=list[IpamProviderRead])
def list_ipam_providers(db: Session = Depends(get_db)) -> list[IpamProviderRead]:
    return [prov_svc.provider_to_read(r) for r in prov_svc.list_providers(db)]


@router.post("/providers", response_model=IpamProviderRead)
def create_ipam_provider(data: IpamProviderCreate, db: Session = Depends(get_db)) -> IpamProviderRead:
    try:
        return prov_svc.provider_to_read(prov_svc.create_provider(db, data))
    except IntegrityError as e:
        raise HTTPException(status_code=409, detail="leverandørslug finnes allerede") from e


@router.get("/providers/{provider_id}", response_model=IpamProviderRead)
def get_ipam_provider(provider_id: int, db: Session = Depends(get_db)) -> IpamProviderRead:
    row = prov_svc.get_provider(db, provider_id)
    if row is None:
        raise HTTPException(status_code=404, detail="leverandør ikke funnet")
    return prov_svc.provider_to_read(row)


@router.patch("/providers/{provider_id}", response_model=IpamProviderRead)
def patch_ipam_provider(
    provider_id: int,
    data: IpamProviderUpdate,
    db: Session = Depends(get_db),
) -> IpamProviderRead:
    row = prov_svc.get_provider(db, provider_id)
    if row is None:
        raise HTTPException(status_code=404, detail="leverandør ikke funnet")
    return prov_svc.provider_to_read(prov_svc.update_provider(db, row, data))


@router.delete("/providers/{provider_id}", status_code=204)
def delete_ipam_provider(provider_id: int, db: Session = Depends(get_db)) -> None:
    row = prov_svc.get_provider(db, provider_id)
    if row is None:
        raise HTTPException(status_code=404, detail="leverandør ikke funnet")
    prov_svc.delete_provider(db, row)


@router.get("/providers/{provider_id}/accounts", response_model=list[IpamProviderAccountRead])
def list_provider_accounts(provider_id: int, db: Session = Depends(get_db)) -> list[IpamProviderAccountRead]:
    row = prov_svc.get_provider(db, provider_id)
    if row is None:
        raise HTTPException(status_code=404, detail="leverandør ikke funnet")
    return [prov_svc.account_to_read(a) for a in prov_svc.list_accounts(db, provider_id)]


@router.post("/providers/{provider_id}/accounts", response_model=IpamProviderAccountRead)
def create_provider_account(
    provider_id: int,
    data: IpamProviderAccountCreate,
    db: Session = Depends(get_db),
) -> IpamProviderAccountRead:
    row = prov_svc.get_provider(db, provider_id)
    if row is None:
        raise HTTPException(status_code=404, detail="leverandør ikke funnet")
    try:
        return prov_svc.account_to_read(prov_svc.create_account(db, row, data))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except IntegrityError as e:
        raise HTTPException(status_code=409, detail="konto-slug finnes allerede") from e


@router.patch("/provider-accounts/{account_id}", response_model=IpamProviderAccountRead)
def patch_provider_account(
    account_id: int,
    data: IpamProviderAccountUpdate,
    db: Session = Depends(get_db),
) -> IpamProviderAccountRead:
    row = prov_svc.get_account(db, account_id)
    if row is None:
        raise HTTPException(status_code=404, detail="leverandørkonto ikke funnet")
    try:
        return prov_svc.account_to_read(prov_svc.update_account(db, row, data))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.delete("/provider-accounts/{account_id}", status_code=204)
def delete_provider_account(account_id: int, db: Session = Depends(get_db)) -> None:
    row = prov_svc.get_account(db, account_id)
    if row is None:
        raise HTTPException(status_code=404, detail="leverandørkonto ikke funnet")
    prov_svc.delete_account(db, row)


@router.get("/vpn-services", response_model=list[IpamVpnServiceRead])
def list_vpn_services(
    tenant_id: int | None = Query(None),
    db: Session = Depends(get_db),
) -> list[IpamVpnServiceRead]:
    return [vpn_svc.vpn_to_read(r) for r in vpn_svc.list_vpn_services(db, tenant_id=tenant_id)]


@router.post("/vpn-services", response_model=IpamVpnServiceRead)
def create_vpn_service(data: IpamVpnServiceCreate, db: Session = Depends(get_db)) -> IpamVpnServiceRead:
    try:
        return vpn_svc.vpn_to_read(vpn_svc.create_vpn_service(db, data))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except IntegrityError as e:
        raise HTTPException(status_code=409, detail="VPN-slug finnes allerede") from e


@router.get("/vpn-services/{vpn_id}", response_model=IpamVpnServiceRead)
def get_vpn_service(vpn_id: int, db: Session = Depends(get_db)) -> IpamVpnServiceRead:
    row = vpn_svc.get_vpn_service(db, vpn_id)
    if row is None:
        raise HTTPException(status_code=404, detail="VPN-tjeneste ikke funnet")
    return vpn_svc.vpn_to_read(row)


@router.patch("/vpn-services/{vpn_id}", response_model=IpamVpnServiceRead)
def patch_vpn_service(
    vpn_id: int,
    data: IpamVpnServiceUpdate,
    db: Session = Depends(get_db),
) -> IpamVpnServiceRead:
    row = vpn_svc.get_vpn_service(db, vpn_id)
    if row is None:
        raise HTTPException(status_code=404, detail="VPN-tjeneste ikke funnet")
    try:
        return vpn_svc.vpn_to_read(vpn_svc.update_vpn_service(db, row, data))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.delete("/vpn-services/{vpn_id}", status_code=204)
def delete_vpn_service(vpn_id: int, db: Session = Depends(get_db)) -> None:
    row = vpn_svc.get_vpn_service(db, vpn_id)
    if row is None:
        raise HTTPException(status_code=404, detail="VPN-tjeneste ikke funnet")
    vpn_svc.delete_vpn_service(db, row)


@router.get("/vpn-services/{vpn_id}/tunnels", response_model=list[IpamTunnelRead])
def list_vpn_tunnels(vpn_id: int, db: Session = Depends(get_db)) -> list[IpamTunnelRead]:
    row = vpn_svc.get_vpn_service(db, vpn_id)
    if row is None:
        raise HTTPException(status_code=404, detail="VPN-tjeneste ikke funnet")
    return [vpn_svc.tunnel_to_read(t) for t in vpn_svc.list_tunnels(db, vpn_id)]


@router.post("/vpn-services/{vpn_id}/tunnels", response_model=IpamTunnelRead)
def create_vpn_tunnel(vpn_id: int, data: IpamTunnelCreate, db: Session = Depends(get_db)) -> IpamTunnelRead:
    row = vpn_svc.get_vpn_service(db, vpn_id)
    if row is None:
        raise HTTPException(status_code=404, detail="VPN-tjeneste ikke funnet")
    try:
        return vpn_svc.tunnel_to_read(vpn_svc.create_tunnel(db, row, data))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except IntegrityError as e:
        raise HTTPException(status_code=409, detail="tunnelslug finnes allerede") from e


@router.patch("/tunnels/{tunnel_id}", response_model=IpamTunnelRead)
def patch_vpn_tunnel(tunnel_id: int, data: IpamTunnelUpdate, db: Session = Depends(get_db)) -> IpamTunnelRead:
    row = vpn_svc.get_tunnel(db, tunnel_id)
    if row is None:
        raise HTTPException(status_code=404, detail="tunnel ikke funnet")
    try:
        return vpn_svc.tunnel_to_read(vpn_svc.update_tunnel(db, row, data))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.delete("/tunnels/{tunnel_id}", status_code=204)
def delete_vpn_tunnel(tunnel_id: int, db: Session = Depends(get_db)) -> None:
    row = vpn_svc.get_tunnel(db, tunnel_id)
    if row is None:
        raise HTTPException(status_code=404, detail="tunnel ikke funnet")
    vpn_svc.delete_tunnel(db, row)


@router.get("/tunnels/{tunnel_id}/endpoints", response_model=list[IpamTunnelEndpointRead])
def list_tunnel_endpoints(tunnel_id: int, db: Session = Depends(get_db)) -> list[IpamTunnelEndpointRead]:
    row = vpn_svc.get_tunnel(db, tunnel_id)
    if row is None:
        raise HTTPException(status_code=404, detail="tunnel ikke funnet")
    return [vpn_svc.endpoint_to_read(db, e) for e in vpn_svc.list_endpoints(db, tunnel_id)]


@router.post("/tunnels/{tunnel_id}/endpoints", response_model=IpamTunnelEndpointRead)
def upsert_tunnel_endpoint(
    tunnel_id: int,
    data: IpamTunnelEndpointCreate,
    db: Session = Depends(get_db),
) -> IpamTunnelEndpointRead:
    row = vpn_svc.get_tunnel(db, tunnel_id)
    if row is None:
        raise HTTPException(status_code=404, detail="tunnel ikke funnet")
    try:
        return vpn_svc.endpoint_to_read(db, vpn_svc.upsert_endpoint(db, row, data))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.get("/tunnels/{tunnel_id}/peers", response_model=list[IpamTunnelPeerRead])
def list_tunnel_peers(tunnel_id: int, db: Session = Depends(get_db)) -> list[IpamTunnelPeerRead]:
    row = vpn_svc.get_tunnel(db, tunnel_id)
    if row is None:
        raise HTTPException(status_code=404, detail="tunnel ikke funnet")
    return [vpn_svc.peer_to_read(p) for p in vpn_svc.list_peers(db, tunnel_id)]


@router.post("/tunnels/{tunnel_id}/peers", response_model=IpamTunnelPeerRead)
def create_tunnel_peer(tunnel_id: int, data: IpamTunnelPeerCreate, db: Session = Depends(get_db)) -> IpamTunnelPeerRead:
    row = vpn_svc.get_tunnel(db, tunnel_id)
    if row is None:
        raise HTTPException(status_code=404, detail="tunnel ikke funnet")
    try:
        return vpn_svc.peer_to_read(vpn_svc.create_peer(db, row, data))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.patch("/tunnel-peers/{peer_id}", response_model=IpamTunnelPeerRead)
def patch_tunnel_peer(peer_id: int, data: IpamTunnelPeerUpdate, db: Session = Depends(get_db)) -> IpamTunnelPeerRead:
    row = vpn_svc.get_peer(db, peer_id)
    if row is None:
        raise HTTPException(status_code=404, detail="peer ikke funnet")
    try:
        return vpn_svc.peer_to_read(vpn_svc.update_peer(db, row, data))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.delete("/tunnel-peers/{peer_id}", status_code=204)
def delete_tunnel_peer(peer_id: int, db: Session = Depends(get_db)) -> None:
    row = vpn_svc.get_peer(db, peer_id)
    if row is None:
        raise HTTPException(status_code=404, detail="peer ikke funnet")
    vpn_svc.delete_peer(db, row)


@router.get("/tunnel-profiles", response_model=list[IpamTunnelProfileRead])
def list_tunnel_profiles(db: Session = Depends(get_db)) -> list[IpamTunnelProfileRead]:
    return [vpn_svc.profile_to_read(r) for r in vpn_svc.list_profiles(db)]


@router.post("/tunnel-profiles", response_model=IpamTunnelProfileRead)
def create_tunnel_profile(data: IpamTunnelProfileCreate, db: Session = Depends(get_db)) -> IpamTunnelProfileRead:
    try:
        return vpn_svc.profile_to_read(vpn_svc.create_profile(db, data))
    except IntegrityError as e:
        raise HTTPException(status_code=409, detail="profilslug finnes allerede") from e


@router.patch("/tunnel-profiles/{profile_id}", response_model=IpamTunnelProfileRead)
def patch_tunnel_profile(
    profile_id: int,
    data: IpamTunnelProfileUpdate,
    db: Session = Depends(get_db),
) -> IpamTunnelProfileRead:
    row = vpn_svc.get_profile(db, profile_id)
    if row is None:
        raise HTTPException(status_code=404, detail="tunnelprofil ikke funnet")
    return vpn_svc.profile_to_read(vpn_svc.update_profile(db, row, data))


@router.delete("/tunnel-profiles/{profile_id}", status_code=204)
def delete_tunnel_profile(profile_id: int, db: Session = Depends(get_db)) -> None:
    row = vpn_svc.get_profile(db, profile_id)
    if row is None:
        raise HTTPException(status_code=404, detail="tunnelprofil ikke funnet")
    vpn_svc.delete_profile(db, row)


@router.get("/ipv6-prefixes", response_model=list[Ipv6PrefixRead])
def list_ipv6_prefixes(
    response: Response,
    site_id: int | None = Query(None),
    slug: str | None = Query(None),
    limit: int | None = Query(None, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
) -> list[Ipv6PrefixRead]:
    items, total = ipv6_svc.list_ipv6_prefixes(db, site_id=site_id, slug=slug, limit=limit, offset=offset)
    etag_svc.attach_page(response, total=total, offset=offset, count=len(items))
    return items


@router.post("/ipv6-prefixes", response_model=Ipv6PrefixRead)
def create_ipv6_prefix(data: Ipv6PrefixCreate, db: Session = Depends(get_db)) -> Ipv6PrefixRead:
    return ipv6_svc.create_ipv6_prefix(db, data)


@router.post("/ipv6-prefixes/ensure", response_model=Ipv6PrefixRead)
def ensure_ipv6_prefix(
    data: Ipv6PrefixEnsure,
    update: bool = Query(False),
    db: Session = Depends(get_db),
) -> Ipv6PrefixRead:
    return ipv6_svc.ensure_ipv6_prefix(db, data, update=update)


@router.get("/ipv6-prefixes/{prefix_id}", response_model=Ipv6PrefixRead)
def get_ipv6_prefix(prefix_id: int, response: Response, db: Session = Depends(get_db)) -> Ipv6PrefixRead:
    row = ipv6_svc.get_ipv6_prefix(db, prefix_id)
    if row is None:
        raise HTTPException(status_code=404, detail={"code": "prefix_not_found", "detail": "prefiks ikke funnet"})
    etag_svc.attach_etag(response, row)
    return ipv6_svc.ipv6_prefix_read(db, row)


@router.get("/ipv6-prefixes/{prefix_id}/available-prefixes", response_model=Ipv4AvailablePrefixesRead)
def list_available_ipv6_children(
    prefix_id: int,
    prefixlen: int = Query(..., ge=1, le=128),
    limit: int = Query(64, ge=1, le=256),
    db: Session = Depends(get_db),
) -> Ipv4AvailablePrefixesRead:
    row = ipv6_svc.get_ipv6_prefix(db, prefix_id)
    if row is None:
        raise HTTPException(status_code=404, detail={"code": "prefix_not_found", "detail": "prefiks ikke funnet"})
    return ipv6_svc.list_available_child_ipv6(db, row, prefixlen, limit=limit)


@router.post("/ipv6-prefixes/{prefix_id}/allocate", response_model=Ipv6PrefixRead)
def allocate_ipv6_child(prefix_id: int, data: Ipv6PrefixAllocate, db: Session = Depends(get_db)) -> Ipv6PrefixRead:
    row = ipv6_svc.get_ipv6_prefix(db, prefix_id)
    if row is None:
        raise HTTPException(status_code=404, detail={"code": "prefix_not_found", "detail": "prefiks ikke funnet"})
    return ipv6_svc.allocate_child_ipv6(db, row, data)


@router.delete("/ipv6-prefixes/{prefix_id}", status_code=204)
def delete_ipv6_prefix(
    prefix_id: int,
    cascade: bool = Query(False, description="Slett underprefiks og inventory-adresser"),
    db: Session = Depends(get_db),
    if_match: str | None = Header(None, alias="If-Match"),
) -> None:
    row = ipv6_svc.get_ipv6_prefix(db, prefix_id)
    if row is None:
        raise HTTPException(status_code=404, detail={"code": "prefix_not_found", "detail": "prefiks ikke funnet"})
    etag_svc.require_if_match(row, if_match)
    ipv6_svc.delete_ipv6_prefix(db, row, cascade=cascade)


@router.get("/ipv6-prefixes/{prefix_id}/address-grid", response_model=Ipv6PrefixAddressGridRead)
def get_ipv6_address_grid(prefix_id: int, db: Session = Depends(get_db)) -> Ipv6PrefixAddressGridRead:
    return ipv6_grid_svc.build_ipv6_address_grid(db, prefix_id)


@router.get("/ipv6-prefixes/{prefix_id}/available-ranges", response_model=Ipv6AvailableRangesRead)
def get_ipv6_available_ranges(prefix_id: int, db: Session = Depends(get_db)) -> Ipv6AvailableRangesRead:
    row = ipv6_svc.get_ipv6_prefix(db, prefix_id)
    if row is None:
        raise HTTPException(status_code=404, detail={"code": "prefix_not_found", "detail": "prefiks ikke funnet"})
    return ipv6_svc.available_ranges(db, row)


@router.post("/ipv6-prefixes/{prefix_id}/split", response_model=Ipv6PrefixSplitResponse)
def split_ipv6_prefix(
    prefix_id: int,
    data: Ipv6PrefixSplitRequest,
    db: Session = Depends(get_db),
) -> Ipv6PrefixSplitResponse:
    return ipv6_split_svc.ipv6_prefix_split(db, prefix_id, data)


@router.post("/ipv6-prefixes/{prefix_id}/split-equal", response_model=Ipv6PrefixSplitEqualResponse)
def split_ipv6_prefix_equal(
    prefix_id: int,
    data: Ipv6PrefixSplitEqualRequest,
    db: Session = Depends(get_db),
) -> Ipv6PrefixSplitEqualResponse:
    return ipv6_split_svc.ipv6_prefix_split_equal(db, prefix_id, data)


@router.post("/ipv6-addresses/ensure", response_model=Ipv6AddressRead)
def ensure_ipv6_address(
    data: Ipv6AddressEnsure,
    update: bool = Query(False),
    db: Session = Depends(get_db),
) -> Ipv6AddressRead:
    return ipv6_svc.ensure_ipv6_address(db, data, update=update)


@router.post("/ipv6-addresses/request", response_model=Ipv6AddressRead)
def request_ipv6_address(data: Ipv6AddressRequest, db: Session = Depends(get_db)) -> Ipv6AddressRead:
    return ipv6_svc.request_ipv6_address(db, data)


@router.get("/ipv6-addresses", response_model=list[Ipv6AddressRead])
def list_ipv6_addresses(
    response: Response,
    site_id: int | None = Query(None),
    ipv6_prefix_id: int | None = Query(None),
    address: str | None = Query(None),
    limit: int = Query(200, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
) -> list[Ipv6AddressRead]:
    items, total = ipv6_svc.list_ipv6_addresses(
        db, site_id=site_id, ipv6_prefix_id=ipv6_prefix_id, address=address, limit=limit, offset=offset,
    )
    etag_svc.attach_page(response, total=total, offset=offset, count=len(items))
    return items


@router.post("/ipv6-addresses/{addr_id}/release", response_model=Ipv6AddressRead)
def release_ipv6_address(
    addr_id: int,
    response: Response,
    db: Session = Depends(get_db),
    if_match: str | None = Header(None, alias="If-Match"),
) -> Ipv6AddressRead:
    row = ipv6_svc.get_ipv6_address(db, addr_id)
    if row is None:
        raise HTTPException(status_code=404, detail={"code": "address_not_found", "detail": "IP-adresse ikke funnet"})
    etag_svc.require_if_match(row, if_match)
    body = ipv6_svc.release_ipv6_address(db, row)
    etag_svc.attach_etag(response, row)
    return body


@router.delete("/ipv6-addresses/{addr_id}", status_code=204)
def delete_ipv6_address(
    addr_id: int,
    force: bool = Query(False, description="Hard-slett reserved/assigned uten release"),
    db: Session = Depends(get_db),
    if_match: str | None = Header(None, alias="If-Match"),
) -> None:
    row = ipv6_svc.get_ipv6_address(db, addr_id)
    if row is None:
        raise HTTPException(status_code=404, detail={"code": "address_not_found", "detail": "IP-adresse ikke funnet"})
    etag_svc.require_if_match(row, if_match)
    ipv6_svc.delete_ipv6_address(db, row, force=force)


@router.get("/audit", response_model=list[IpamAuditEventRead])
def list_ipam_audit(
    site_id: int | None = Query(None),
    resource_type: str | None = Query(None),
    action: str | None = Query(None),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
) -> list[IpamAuditEventRead]:
    return [
        IpamAuditEventRead.model_validate(r)
        for r in audit_svc.list_events(db, site_id=site_id, resource_type=resource_type, action=action, limit=limit)
    ]


@router.get("/drift", response_model=SiteDriftRead)
def get_site_drift(site_id: int = Query(..., ge=1), db: Session = Depends(get_db)) -> SiteDriftRead:
    return sync_svc.site_drift(db, site_id)


@router.post("/bulk-ensure", response_model=IpamBulkEnsureRead)
def bulk_ensure_ipam(data: IpamBulkEnsure, db: Session = Depends(get_db)) -> IpamBulkEnsureRead:
    return sync_svc.bulk_ensure(db, data)


@router.get("/export")
def export_site_ipam(
    site_id: int = Query(..., ge=1),
    format: str = Query("json", description="json | yaml"),
    db: Session = Depends(get_db),
):
    if format.strip().lower() == "yaml":
        text = sync_svc.export_site_yaml(db, site_id)
        return Response(content=text, media_type="application/yaml")
    return sync_svc.export_site(db, site_id)


@router.get("/webhooks", response_model=list[IpamWebhookRead])
def list_ipam_webhooks(db: Session = Depends(get_db)) -> list[IpamWebhookRead]:
    return [hook_svc.webhook_to_read(r) for r in hook_svc.list_webhooks(db)]


@router.post("/webhooks", response_model=IpamWebhookRead)
def create_ipam_webhook(data: IpamWebhookCreate, db: Session = Depends(get_db)) -> IpamWebhookRead:
    return hook_svc.webhook_to_read(hook_svc.create_webhook(db, data))


@router.get("/webhooks/{webhook_id}/deliveries", response_model=list[IpamWebhookDeliveryRead])
def list_ipam_webhook_deliveries(
    webhook_id: int,
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
) -> list[IpamWebhookDeliveryRead]:
    row = hook_svc.get_webhook(db, webhook_id)
    if row is None:
        raise HTTPException(status_code=404, detail={"code": "webhook_not_found", "detail": "webhook ikke funnet"})
    return [hook_svc.delivery_to_read(d) for d in hook_svc.list_deliveries(db, webhook_id, limit=limit)]


@router.delete("/webhooks/{webhook_id}", status_code=204)
def delete_ipam_webhook(webhook_id: int, db: Session = Depends(get_db)) -> None:
    row = hook_svc.get_webhook(db, webhook_id)
    if row is None:
        raise HTTPException(status_code=404, detail={"code": "webhook_not_found", "detail": "webhook ikke funnet"})
    hook_svc.delete_webhook(db, row)
