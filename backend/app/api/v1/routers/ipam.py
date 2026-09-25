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
    Ipv4RangeCreate,
    Ipv4RangeRead,
    Ipv4RangeUpdate,
    PrefixAddressGridRead,
    SubnetScanCreate,
    SubnetScanDetailRead,
    SubnetScanRead,
    UserCreate,
    UserRead,
    IpamCircuitClassify,
    IpamCircuitClassifyRead,
    IpamCircuitCreate,
    IpamCircuitGroupCreate,
    IpamCircuitGroupRead,
    IpamCircuitGroupUpdate,
    IpamCircuitRead,
    IpamCircuitStrandCreate,
    IpamCircuitStrandRead,
    IpamCircuitTerminationCreate,
    IpamCircuitTerminationRead,
    IpamCircuitUpdate,
    IpamContractCreate,
    IpamContractRead,
    IpamContractUpdate,
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
    IpamTunnelTransportCreate,
    IpamTunnelTransportRead,
    IpamTunnelUpdate,
    IpamWireGuardInterfaceCreate,
    IpamWireGuardInterfaceRead,
    IpamWireGuardInterfaceUpdate,
    IpamWireGuardPeerCreate,
    IpamWireGuardPeerRead,
    IpamWireGuardPeerUpdate,
    IpamVpnMemberCreate,
    IpamVpnMemberRead,
    IpamVpnServiceCreate,
    IpamVpnServiceRead,
    IpamVpnServiceUpdate,
    IpamOverlaySegmentCreate,
    IpamOverlaySegmentRead,
    IpamOverlayStretchCreate,
    IpamOverlayStretchRead,
    IpamVrfStretchCreate,
    IpamVrfStretchRead,
    IpamVlanStretchCreate,
    IpamVlanStretchRead,
    IpamVlanCreate,
    IpamVlanEnsure,
    IpamVlanGroupCreate,
    IpamVlanGroupRead,
    IpamVlanGroupUpdate,
    IpamVlanRead,
    IpamVlanUpdate,
    IpamAsAssignmentCreate,
    IpamAsAssignmentRead,
    IpamAutonomousSystemCreate,
    IpamAutonomousSystemRead,
    IpamAutonomousSystemUpdate,
    IpamBgpInstanceCreate,
    IpamBgpInstanceRead,
    IpamBgpSessionCreate,
    IpamBgpSessionRead,
    IpamBgpSessionUpdate,
    IpamRouteTargetCreate,
    IpamRouteTargetRead,
    IpamRouteTargetUpdate,
    IpamVrfCreate,
    IpamVrfEnsure,
    IpamVrfInstanceCreate,
    IpamVrfInstanceRead,
    IpamVrfInstanceUpdate,
    IpamVrfRead,
    IpamVrfRouteTargetCreate,
    IpamVrfRouteTargetRead,
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
from app.services import ipam_bgp as bgp_svc
from app.services import ipam_providers as prov_svc
from app.services import ipam_vpn as vpn_svc
from app.services import ipam_wireguard as wg_svc
from app.services import ipam_prefix_grid as grid_svc
from app.services import ipam_subnet_scan as scan_svc
from app.services import ipam_ipv6 as ipv6_svc
from app.services import ipam_ipv6_grid as ipv6_grid_svc
from app.services import ipam_ipv6_split as ipv6_split_svc
from app.services import ipam_audit as audit_svc
from app.services import ipam_etag as etag_svc
from app.services import ipam_sync as sync_svc
from app.services import ipam_webhooks as hook_svc
from app.services import ipam_range as range_svc
from app.services import ipam_vrf_instance as vrfi_svc
from app.services import ipam_route_target as rt_svc

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


@router.get("/ipv4-prefixes/{prefix_id}/ranges", response_model=list[Ipv4RangeRead])
def list_ipv4_ranges(prefix_id: int, db: Session = Depends(get_db)) -> list[Ipv4RangeRead]:
    row = ipam_svc.get_ipv4_prefix(db, prefix_id)
    if row is None:
        raise HTTPException(status_code=404, detail={"code": "prefix_not_found", "detail": "prefiks ikke funnet"})
    return [range_svc.range_to_read(x) for x in range_svc.list_ipv4_ranges(db, prefix_id)]


@router.post("/ipv4-prefixes/{prefix_id}/ranges", response_model=Ipv4RangeRead)
def create_ipv4_range(prefix_id: int, data: Ipv4RangeCreate, db: Session = Depends(get_db)) -> Ipv4RangeRead:
    row = ipam_svc.get_ipv4_prefix(db, prefix_id)
    if row is None:
        raise HTTPException(status_code=404, detail={"code": "prefix_not_found", "detail": "prefiks ikke funnet"})
    return range_svc.create_ipv4_range(db, row, data)


@router.get("/ipv4-ranges/{range_id}", response_model=Ipv4RangeRead)
def get_ipv4_range(range_id: int, db: Session = Depends(get_db)) -> Ipv4RangeRead:
    row = range_svc.get_ipv4_range(db, range_id)
    if row is None:
        raise HTTPException(status_code=404, detail={"code": "range_not_found", "detail": "område ikke funnet"})
    return range_svc.range_to_read(row)


@router.patch("/ipv4-ranges/{range_id}", response_model=Ipv4RangeRead)
def patch_ipv4_range(range_id: int, data: Ipv4RangeUpdate, db: Session = Depends(get_db)) -> Ipv4RangeRead:
    row = range_svc.get_ipv4_range(db, range_id)
    if row is None:
        raise HTTPException(status_code=404, detail={"code": "range_not_found", "detail": "område ikke funnet"})
    return range_svc.update_ipv4_range(db, row, data)


@router.delete("/ipv4-ranges/{range_id}", status_code=204)
def delete_ipv4_range(range_id: int, db: Session = Depends(get_db)) -> None:
    row = range_svc.get_ipv4_range(db, range_id)
    if row is None:
        raise HTTPException(status_code=404, detail={"code": "range_not_found", "detail": "område ikke funnet"})
    range_svc.delete_ipv4_range(db, row)


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


@router.get("/vrfs/{vrf_id}/instances", response_model=list[IpamVrfInstanceRead])
def list_vrf_instances_for_vrf(vrf_id: int, db: Session = Depends(get_db)) -> list[IpamVrfInstanceRead]:
    row = fac_svc.get_vrf(db, vrf_id)
    if row is None:
        raise HTTPException(status_code=404, detail={"code": "vrf_not_found", "detail": "VRF ikke funnet"})
    return [vrfi_svc.instance_to_read(db, x) for x in vrfi_svc.list_instances(db, vrf_id=vrf_id)]


@router.post("/vrfs/{vrf_id}/instances", response_model=IpamVrfInstanceRead)
def create_vrf_instance(vrf_id: int, data: IpamVrfInstanceCreate, db: Session = Depends(get_db)) -> IpamVrfInstanceRead:
    row = fac_svc.get_vrf(db, vrf_id)
    if row is None:
        raise HTTPException(status_code=404, detail={"code": "vrf_not_found", "detail": "VRF ikke funnet"})
    return vrfi_svc.create_instance(db, row, data)


@router.get("/vrf-instances", response_model=list[IpamVrfInstanceRead])
def list_vrf_instances(
    vrf_id: int | None = Query(None),
    device_id: int | None = Query(None),
    site_id: int | None = Query(None),
    db: Session = Depends(get_db),
) -> list[IpamVrfInstanceRead]:
    return [
        vrfi_svc.instance_to_read(db, x)
        for x in vrfi_svc.list_instances(db, vrf_id=vrf_id, device_id=device_id, site_id=site_id)
    ]


@router.get("/vrf-instances/{instance_id}", response_model=IpamVrfInstanceRead)
def get_vrf_instance(instance_id: int, db: Session = Depends(get_db)) -> IpamVrfInstanceRead:
    row = vrfi_svc.get_instance(db, instance_id)
    if row is None:
        raise HTTPException(status_code=404, detail={"code": "vrf_instance_not_found", "detail": "VRF-instans ikke funnet"})
    return vrfi_svc.instance_to_read(db, row)


@router.patch("/vrf-instances/{instance_id}", response_model=IpamVrfInstanceRead)
def patch_vrf_instance(
    instance_id: int,
    data: IpamVrfInstanceUpdate,
    db: Session = Depends(get_db),
) -> IpamVrfInstanceRead:
    row = vrfi_svc.get_instance(db, instance_id)
    if row is None:
        raise HTTPException(status_code=404, detail={"code": "vrf_instance_not_found", "detail": "VRF-instans ikke funnet"})
    return vrfi_svc.update_instance(db, row, data)


@router.delete("/vrf-instances/{instance_id}", status_code=204)
def delete_vrf_instance(instance_id: int, db: Session = Depends(get_db)) -> None:
    row = vrfi_svc.get_instance(db, instance_id)
    if row is None:
        raise HTTPException(status_code=404, detail={"code": "vrf_instance_not_found", "detail": "VRF-instans ikke funnet"})
    vrfi_svc.delete_instance(db, row)


@router.get("/route-targets", response_model=list[IpamRouteTargetRead])
def list_route_targets(db: Session = Depends(get_db)) -> list[IpamRouteTargetRead]:
    return [rt_svc.rt_to_read(x) for x in rt_svc.list_route_targets(db)]


@router.post("/route-targets", response_model=IpamRouteTargetRead)
def create_route_target(data: IpamRouteTargetCreate, db: Session = Depends(get_db)) -> IpamRouteTargetRead:
    return rt_svc.create_route_target(db, data)


@router.get("/route-targets/{rt_id}", response_model=IpamRouteTargetRead)
def get_route_target(rt_id: int, db: Session = Depends(get_db)) -> IpamRouteTargetRead:
    row = rt_svc.get_route_target(db, rt_id)
    if row is None:
        raise HTTPException(status_code=404, detail={"code": "route_target_not_found", "detail": "route target ikke funnet"})
    return rt_svc.rt_to_read(row)


@router.patch("/route-targets/{rt_id}", response_model=IpamRouteTargetRead)
def patch_route_target(rt_id: int, data: IpamRouteTargetUpdate, db: Session = Depends(get_db)) -> IpamRouteTargetRead:
    row = rt_svc.get_route_target(db, rt_id)
    if row is None:
        raise HTTPException(status_code=404, detail={"code": "route_target_not_found", "detail": "route target ikke funnet"})
    return rt_svc.update_route_target(db, row, data)


@router.delete("/route-targets/{rt_id}", status_code=204)
def delete_route_target(rt_id: int, db: Session = Depends(get_db)) -> None:
    row = rt_svc.get_route_target(db, rt_id)
    if row is None:
        raise HTTPException(status_code=404, detail={"code": "route_target_not_found", "detail": "route target ikke funnet"})
    rt_svc.delete_route_target(db, row)


@router.get("/vrfs/{vrf_id}/route-targets", response_model=list[IpamVrfRouteTargetRead])
def list_vrf_route_targets(vrf_id: int, db: Session = Depends(get_db)) -> list[IpamVrfRouteTargetRead]:
    row = fac_svc.get_vrf(db, vrf_id)
    if row is None:
        raise HTTPException(status_code=404, detail={"code": "vrf_not_found", "detail": "VRF ikke funnet"})
    return [rt_svc.binding_to_read(db, x) for x in rt_svc.list_vrf_bindings(db, vrf_id=vrf_id)]


@router.post("/vrfs/{vrf_id}/route-targets", response_model=IpamVrfRouteTargetRead)
def bind_vrf_route_target(
    vrf_id: int,
    data: IpamVrfRouteTargetCreate,
    db: Session = Depends(get_db),
) -> IpamVrfRouteTargetRead:
    row = fac_svc.get_vrf(db, vrf_id)
    if row is None:
        raise HTTPException(status_code=404, detail={"code": "vrf_not_found", "detail": "VRF ikke funnet"})
    return rt_svc.bind_vrf_route_target(db, row, data)


@router.get("/vrf-route-targets", response_model=list[IpamVrfRouteTargetRead])
def list_all_vrf_route_targets(
    site_id: int | None = Query(None),
    db: Session = Depends(get_db),
) -> list[IpamVrfRouteTargetRead]:
    return [rt_svc.binding_to_read(db, x) for x in rt_svc.list_vrf_bindings(db, site_id=site_id)]


@router.delete("/vrf-route-targets/{binding_id}", status_code=204)
def unbind_vrf_route_target(binding_id: int, db: Session = Depends(get_db)) -> None:
    row = rt_svc.get_binding(db, binding_id)
    if row is None:
        raise HTTPException(status_code=404, detail={"code": "vrf_route_target_not_found", "detail": "VRF-RT-kobling ikke funnet"})
    rt_svc.unbind_vrf_route_target(db, row)


@router.get("/autonomous-systems", response_model=list[IpamAutonomousSystemRead])
def list_autonomous_systems(
    tenant_id: int | None = Query(None),
    db: Session = Depends(get_db),
) -> list[IpamAutonomousSystemRead]:
    return [bgp_svc.as_to_read(r) for r in bgp_svc.list_autonomous_systems(db, tenant_id=tenant_id)]


@router.post("/autonomous-systems", response_model=IpamAutonomousSystemRead)
def create_autonomous_system(
    data: IpamAutonomousSystemCreate,
    db: Session = Depends(get_db),
) -> IpamAutonomousSystemRead:
    try:
        return bgp_svc.as_to_read(bgp_svc.create_autonomous_system(db, data))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.get("/autonomous-systems/{as_id}", response_model=IpamAutonomousSystemRead)
def get_autonomous_system(as_id: int, db: Session = Depends(get_db)) -> IpamAutonomousSystemRead:
    row = bgp_svc.get_autonomous_system(db, as_id)
    if row is None:
        raise HTTPException(status_code=404, detail="AS ikke funnet")
    return bgp_svc.as_to_read(row)


@router.patch("/autonomous-systems/{as_id}", response_model=IpamAutonomousSystemRead)
def patch_autonomous_system(
    as_id: int,
    data: IpamAutonomousSystemUpdate,
    db: Session = Depends(get_db),
) -> IpamAutonomousSystemRead:
    row = bgp_svc.get_autonomous_system(db, as_id)
    if row is None:
        raise HTTPException(status_code=404, detail="AS ikke funnet")
    try:
        return bgp_svc.as_to_read(bgp_svc.update_autonomous_system(db, row, data))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.delete("/autonomous-systems/{as_id}", status_code=204)
def delete_autonomous_system(as_id: int, db: Session = Depends(get_db)) -> None:
    row = bgp_svc.get_autonomous_system(db, as_id)
    if row is None:
        raise HTTPException(status_code=404, detail="AS ikke funnet")
    bgp_svc.delete_autonomous_system(db, row)


@router.get("/as-assignments", response_model=list[IpamAsAssignmentRead])
def list_as_assignments(
    site_id: int | None = Query(None),
    as_id: int | None = Query(None),
    db: Session = Depends(get_db),
) -> list[IpamAsAssignmentRead]:
    return [bgp_svc.assignment_to_read(db, r) for r in bgp_svc.list_as_assignments(db, site_id=site_id, as_id=as_id)]


@router.post("/as-assignments", response_model=IpamAsAssignmentRead)
def create_as_assignment(data: IpamAsAssignmentCreate, db: Session = Depends(get_db)) -> IpamAsAssignmentRead:
    try:
        return bgp_svc.assignment_to_read(db, bgp_svc.create_as_assignment(db, data))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.delete("/as-assignments/{assignment_id}", status_code=204)
def delete_as_assignment(assignment_id: int, db: Session = Depends(get_db)) -> None:
    row = bgp_svc.get_as_assignment(db, assignment_id)
    if row is None:
        raise HTTPException(status_code=404, detail="AS-tilordning ikke funnet")
    bgp_svc.delete_as_assignment(db, row)


@router.get("/bgp-instances", response_model=list[IpamBgpInstanceRead])
def list_bgp_instances(
    site_id: int | None = Query(None),
    device_id: int | None = Query(None),
    db: Session = Depends(get_db),
) -> list[IpamBgpInstanceRead]:
    return [
        bgp_svc.instance_to_read(db, r)
        for r in bgp_svc.list_bgp_instances(db, site_id=site_id, device_id=device_id)
    ]


@router.post("/bgp-instances", response_model=IpamBgpInstanceRead)
def create_bgp_instance(data: IpamBgpInstanceCreate, db: Session = Depends(get_db)) -> IpamBgpInstanceRead:
    try:
        return bgp_svc.instance_to_read(db, bgp_svc.create_bgp_instance(db, data))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.get("/bgp-instances/{iid}", response_model=IpamBgpInstanceRead)
def get_bgp_instance(iid: int, db: Session = Depends(get_db)) -> IpamBgpInstanceRead:
    row = bgp_svc.get_bgp_instance(db, iid)
    if row is None:
        raise HTTPException(status_code=404, detail="BGP-instans ikke funnet")
    return bgp_svc.instance_to_read(db, row)


@router.delete("/bgp-instances/{iid}", status_code=204)
def delete_bgp_instance(iid: int, db: Session = Depends(get_db)) -> None:
    row = bgp_svc.get_bgp_instance(db, iid)
    if row is None:
        raise HTTPException(status_code=404, detail="BGP-instans ikke funnet")
    bgp_svc.delete_bgp_instance(db, row)


@router.get("/bgp-sessions", response_model=list[IpamBgpSessionRead])
def list_bgp_sessions(
    site_id: int | None = Query(None),
    db: Session = Depends(get_db),
) -> list[IpamBgpSessionRead]:
    return [bgp_svc.bgp_to_read(r) for r in bgp_svc.list_bgp_sessions(db, site_id=site_id)]


@router.post("/bgp-sessions", response_model=IpamBgpSessionRead)
def create_bgp_session(data: IpamBgpSessionCreate, db: Session = Depends(get_db)) -> IpamBgpSessionRead:
    try:
        return bgp_svc.bgp_to_read(bgp_svc.create_bgp_session(db, data))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.patch("/bgp-sessions/{session_id}", response_model=IpamBgpSessionRead)
def patch_bgp_session(
    session_id: int,
    data: IpamBgpSessionUpdate,
    db: Session = Depends(get_db),
) -> IpamBgpSessionRead:
    row = bgp_svc.get_bgp_session(db, session_id)
    if row is None:
        raise HTTPException(status_code=404, detail="BGP-sesjon ikke funnet")
    try:
        return bgp_svc.bgp_to_read(bgp_svc.update_bgp_session(db, row, data))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.delete("/bgp-sessions/{session_id}", status_code=204)
def delete_bgp_session(session_id: int, db: Session = Depends(get_db)) -> None:
    row = bgp_svc.get_bgp_session(db, session_id)
    if row is None:
        raise HTTPException(status_code=404, detail="BGP-sesjon ikke funnet")
    bgp_svc.delete_bgp_session(db, row)


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


@router.get("/overlay-segments", response_model=list[IpamOverlaySegmentRead])
def list_overlay_segments(
    site_id: int | None = Query(None, description="Filtrer på DCIM site-id"),
    db: Session = Depends(get_db),
) -> list[IpamOverlaySegmentRead]:
    return [fac_svc.overlay_segment_to_read(db, r) for r in fac_svc.list_overlay_segments(db, site_id=site_id)]


@router.post("/overlay-segments", response_model=IpamOverlaySegmentRead)
def create_overlay_segment(data: IpamOverlaySegmentCreate, db: Session = Depends(get_db)) -> IpamOverlaySegmentRead:
    try:
        return fac_svc.overlay_segment_to_read(db, fac_svc.create_overlay_segment(db, data))
    except ValueError as e:
        raise HTTPException(status_code=404, detail={"code": "overlay_ref_missing", "detail": str(e)}) from e


@router.get("/overlay-segments/{segment_id}", response_model=IpamOverlaySegmentRead)
def get_overlay_segment(segment_id: int, db: Session = Depends(get_db)) -> IpamOverlaySegmentRead:
    row = fac_svc.get_overlay_segment(db, segment_id)
    if row is None:
        raise HTTPException(status_code=404, detail={"code": "overlay_not_found", "detail": "overlay-segment ikke funnet"})
    return fac_svc.overlay_segment_to_read(db, row)


@router.delete("/overlay-segments/{segment_id}", status_code=204)
def delete_overlay_segment(segment_id: int, db: Session = Depends(get_db)) -> None:
    row = fac_svc.get_overlay_segment(db, segment_id)
    if row is None:
        raise HTTPException(status_code=404, detail={"code": "overlay_not_found", "detail": "overlay-segment ikke funnet"})
    fac_svc.delete_overlay_segment(db, row)


@router.get("/overlay-stretches", response_model=list[IpamOverlayStretchRead])
def list_overlay_stretches(
    site_id: int | None = Query(None, description="Filtrer på DCIM site-id"),
    db: Session = Depends(get_db),
) -> list[IpamOverlayStretchRead]:
    return [fac_svc.overlay_stretch_to_read(db, r) for r in fac_svc.list_overlay_stretches(db, site_id=site_id)]


@router.post("/overlay-stretches", response_model=IpamOverlayStretchRead)
def create_overlay_stretch(data: IpamOverlayStretchCreate, db: Session = Depends(get_db)) -> IpamOverlayStretchRead:
    return fac_svc.overlay_stretch_to_read(db, fac_svc.create_overlay_stretch(db, data))


@router.get("/overlay-stretches/{stretch_id}", response_model=IpamOverlayStretchRead)
def get_overlay_stretch(stretch_id: int, db: Session = Depends(get_db)) -> IpamOverlayStretchRead:
    row = fac_svc.get_overlay_stretch(db, stretch_id)
    if row is None:
        raise HTTPException(status_code=404, detail={"code": "overlay_stretch_not_found", "detail": "overlay-strekning ikke funnet"})
    return fac_svc.overlay_stretch_to_read(db, row)


@router.delete("/overlay-stretches/{stretch_id}", status_code=204)
def delete_overlay_stretch(stretch_id: int, db: Session = Depends(get_db)) -> None:
    row = fac_svc.get_overlay_stretch(db, stretch_id)
    if row is None:
        raise HTTPException(status_code=404, detail={"code": "overlay_stretch_not_found", "detail": "overlay-strekning ikke funnet"})
    fac_svc.delete_overlay_stretch(db, row)


@router.get("/vrf-stretches", response_model=list[IpamVrfStretchRead])
def list_vrf_stretches(
    site_id: int | None = Query(None, description="Filtrer på DCIM site-id"),
    db: Session = Depends(get_db),
) -> list[IpamVrfStretchRead]:
    return [fac_svc.vrf_stretch_to_read(db, r) for r in fac_svc.list_vrf_stretches(db, site_id=site_id)]


@router.post("/vrf-stretches", response_model=IpamVrfStretchRead)
def create_vrf_stretch(data: IpamVrfStretchCreate, db: Session = Depends(get_db)) -> IpamVrfStretchRead:
    return fac_svc.vrf_stretch_to_read(db, fac_svc.create_vrf_stretch(db, data))


@router.get("/vrf-stretches/{stretch_id}", response_model=IpamVrfStretchRead)
def get_vrf_stretch(stretch_id: int, db: Session = Depends(get_db)) -> IpamVrfStretchRead:
    row = fac_svc.get_vrf_stretch(db, stretch_id)
    if row is None:
        raise HTTPException(status_code=404, detail={"code": "vrf_stretch_not_found", "detail": "VRF-strekning ikke funnet"})
    return fac_svc.vrf_stretch_to_read(db, row)


@router.delete("/vrf-stretches/{stretch_id}", status_code=204)
def delete_vrf_stretch(stretch_id: int, db: Session = Depends(get_db)) -> None:
    row = fac_svc.get_vrf_stretch(db, stretch_id)
    if row is None:
        raise HTTPException(status_code=404, detail={"code": "vrf_stretch_not_found", "detail": "VRF-strekning ikke funnet"})
    fac_svc.delete_vrf_stretch(db, row)


@router.get("/vlan-stretches", response_model=list[IpamVlanStretchRead])
def list_vlan_stretches(
    site_id: int | None = Query(None, description="Filtrer på DCIM site-id"),
    db: Session = Depends(get_db),
) -> list[IpamVlanStretchRead]:
    return [fac_svc.vlan_stretch_to_read(db, r) for r in fac_svc.list_vlan_stretches(db, site_id=site_id)]


@router.post("/vlan-stretches", response_model=IpamVlanStretchRead)
def create_vlan_stretch(data: IpamVlanStretchCreate, db: Session = Depends(get_db)) -> IpamVlanStretchRead:
    return fac_svc.vlan_stretch_to_read(db, fac_svc.create_vlan_stretch(db, data))


@router.get("/vlan-stretches/{stretch_id}", response_model=IpamVlanStretchRead)
def get_vlan_stretch(stretch_id: int, db: Session = Depends(get_db)) -> IpamVlanStretchRead:
    row = fac_svc.get_vlan_stretch(db, stretch_id)
    if row is None:
        raise HTTPException(status_code=404, detail={"code": "vlan_stretch_not_found", "detail": "VLAN-strekning ikke funnet"})
    return fac_svc.vlan_stretch_to_read(db, row)


@router.delete("/vlan-stretches/{stretch_id}", status_code=204)
def delete_vlan_stretch(stretch_id: int, db: Session = Depends(get_db)) -> None:
    row = fac_svc.get_vlan_stretch(db, stretch_id)
    if row is None:
        raise HTTPException(status_code=404, detail={"code": "vlan_stretch_not_found", "detail": "VLAN-strekning ikke funnet"})
    fac_svc.delete_vlan_stretch(db, row)


@router.get("/circuits", response_model=list[IpamCircuitRead])
def list_ipam_circuits(
    tenant_id: int | None = Query(None, description="Filtrer på tenant-id"),
    site_id: int | None = Query(None, description="Filtrer på A- eller Z-site"),
    layer: str | None = Query(None, description="transport eller overlay"),
    group_id: int | None = Query(None, description="Filtrer på redundansgruppe"),
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
            group_id=group_id,
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


@router.get("/circuit-groups", response_model=list[IpamCircuitGroupRead])
def list_ipam_circuit_groups(
    tenant_id: int | None = Query(None),
    db: Session = Depends(get_db),
) -> list[IpamCircuitGroupRead]:
    return [fac_svc.circuit_group_to_read(r) for r in fac_svc.list_circuit_groups(db, tenant_id=tenant_id)]


@router.post("/circuit-groups", response_model=IpamCircuitGroupRead)
def create_ipam_circuit_group(data: IpamCircuitGroupCreate, db: Session = Depends(get_db)) -> IpamCircuitGroupRead:
    try:
        return fac_svc.circuit_group_to_read(fac_svc.create_circuit_group(db, data))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except IntegrityError as e:
        raise HTTPException(status_code=409, detail="gruppeslug finnes allerede") from e


@router.get("/circuit-groups/{group_id}", response_model=IpamCircuitGroupRead)
def get_ipam_circuit_group(group_id: int, db: Session = Depends(get_db)) -> IpamCircuitGroupRead:
    row = fac_svc.get_circuit_group(db, group_id)
    if row is None:
        raise HTTPException(status_code=404, detail="redundansgruppe ikke funnet")
    return fac_svc.circuit_group_to_read(row)


@router.patch("/circuit-groups/{group_id}", response_model=IpamCircuitGroupRead)
def patch_ipam_circuit_group(
    group_id: int,
    data: IpamCircuitGroupUpdate,
    db: Session = Depends(get_db),
) -> IpamCircuitGroupRead:
    row = fac_svc.get_circuit_group(db, group_id)
    if row is None:
        raise HTTPException(status_code=404, detail="redundansgruppe ikke funnet")
    try:
        return fac_svc.circuit_group_to_read(fac_svc.update_circuit_group(db, row, data))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.delete("/circuit-groups/{group_id}", status_code=204)
def delete_ipam_circuit_group(group_id: int, db: Session = Depends(get_db)) -> None:
    row = fac_svc.get_circuit_group(db, group_id)
    if row is None:
        raise HTTPException(status_code=404, detail="redundansgruppe ikke funnet")
    fac_svc.delete_circuit_group(db, row)


@router.get("/circuits/{circuit_id}/strands", response_model=list[IpamCircuitStrandRead])
def list_ipam_circuit_strands(circuit_id: int, db: Session = Depends(get_db)) -> list[IpamCircuitStrandRead]:
    row = fac_svc.get_circuit(db, circuit_id)
    if row is None:
        raise HTTPException(status_code=404, detail="samband ikke funnet")
    return [fac_svc.circuit_strand_to_read(db, b) for b in fac_svc.list_circuit_strands(db, circuit_id)]


@router.post("/circuits/{circuit_id}/strands", response_model=IpamCircuitStrandRead)
def create_ipam_circuit_strand(
    circuit_id: int,
    data: IpamCircuitStrandCreate,
    db: Session = Depends(get_db),
) -> IpamCircuitStrandRead:
    row = fac_svc.get_circuit(db, circuit_id)
    if row is None:
        raise HTTPException(status_code=404, detail="samband ikke funnet")
    return fac_svc.circuit_strand_to_read(db, fac_svc.create_circuit_strand(db, row, data))


@router.delete("/circuit-strands/{bind_id}", status_code=204)
def delete_ipam_circuit_strand(bind_id: int, db: Session = Depends(get_db)) -> None:
    row = fac_svc.get_circuit_strand(db, bind_id)
    if row is None:
        raise HTTPException(status_code=404, detail="fiberkobling ikke funnet")
    fac_svc.delete_circuit_strand(db, row)


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


@router.get("/contracts", response_model=list[IpamContractRead])
def list_ipam_contracts(
    provider_id: int | None = Query(None),
    tenant_id: int | None = Query(None),
    db: Session = Depends(get_db),
) -> list[IpamContractRead]:
    return [
        prov_svc.contract_to_read(r)
        for r in prov_svc.list_contracts(db, provider_id=provider_id, tenant_id=tenant_id)
    ]


@router.post("/contracts", response_model=IpamContractRead)
def create_ipam_contract(data: IpamContractCreate, db: Session = Depends(get_db)) -> IpamContractRead:
    try:
        return prov_svc.contract_to_read(prov_svc.create_contract(db, data))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except IntegrityError as e:
        raise HTTPException(status_code=409, detail="kontraktslug finnes allerede") from e


@router.get("/contracts/{contract_id}", response_model=IpamContractRead)
def get_ipam_contract(contract_id: int, db: Session = Depends(get_db)) -> IpamContractRead:
    row = prov_svc.get_contract(db, contract_id)
    if row is None:
        raise HTTPException(status_code=404, detail="kontrakt ikke funnet")
    return prov_svc.contract_to_read(row)


@router.patch("/contracts/{contract_id}", response_model=IpamContractRead)
def patch_ipam_contract(
    contract_id: int,
    data: IpamContractUpdate,
    db: Session = Depends(get_db),
) -> IpamContractRead:
    row = prov_svc.get_contract(db, contract_id)
    if row is None:
        raise HTTPException(status_code=404, detail="kontrakt ikke funnet")
    try:
        return prov_svc.contract_to_read(prov_svc.update_contract(db, row, data))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.delete("/contracts/{contract_id}", status_code=204)
def delete_ipam_contract(contract_id: int, db: Session = Depends(get_db)) -> None:
    row = prov_svc.get_contract(db, contract_id)
    if row is None:
        raise HTTPException(status_code=404, detail="kontrakt ikke funnet")
    prov_svc.delete_contract(db, row)


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


@router.get("/vpn-services/{vpn_id}/members", response_model=list[IpamVpnMemberRead])
def list_vpn_members(vpn_id: int, db: Session = Depends(get_db)) -> list[IpamVpnMemberRead]:
    row = vpn_svc.get_vpn_service(db, vpn_id)
    if row is None:
        raise HTTPException(status_code=404, detail="VPN-tjeneste ikke funnet")
    return [vpn_svc.vpn_member_to_read(db, m) for m in vpn_svc.list_vpn_members(db, vpn_id)]


@router.post("/vpn-services/{vpn_id}/members", response_model=IpamVpnMemberRead)
def create_vpn_member(
    vpn_id: int,
    data: IpamVpnMemberCreate,
    db: Session = Depends(get_db),
) -> IpamVpnMemberRead:
    row = vpn_svc.get_vpn_service(db, vpn_id)
    if row is None:
        raise HTTPException(status_code=404, detail="VPN-tjeneste ikke funnet")
    return vpn_svc.vpn_member_to_read(db, vpn_svc.create_vpn_member(db, row, data))


@router.delete("/vpn-members/{member_id}", status_code=204)
def delete_vpn_member(member_id: int, db: Session = Depends(get_db)) -> None:
    row = vpn_svc.get_vpn_member(db, member_id)
    if row is None:
        raise HTTPException(status_code=404, detail="VPN-medlem ikke funnet")
    vpn_svc.delete_vpn_member(db, row)


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


@router.get("/tunnels/{tunnel_id}/transports", response_model=list[IpamTunnelTransportRead])
def list_tunnel_transports(tunnel_id: int, db: Session = Depends(get_db)) -> list[IpamTunnelTransportRead]:
    row = vpn_svc.get_tunnel(db, tunnel_id)
    if row is None:
        raise HTTPException(status_code=404, detail="tunnel ikke funnet")
    return [vpn_svc.tunnel_transport_to_read(db, b) for b in vpn_svc.list_tunnel_transports(db, tunnel_id)]


@router.post("/tunnels/{tunnel_id}/transports", response_model=IpamTunnelTransportRead)
def create_tunnel_transport(
    tunnel_id: int,
    data: IpamTunnelTransportCreate,
    db: Session = Depends(get_db),
) -> IpamTunnelTransportRead:
    row = vpn_svc.get_tunnel(db, tunnel_id)
    if row is None:
        raise HTTPException(status_code=404, detail="tunnel ikke funnet")
    return vpn_svc.tunnel_transport_to_read(db, vpn_svc.create_tunnel_transport(db, row, data))


@router.delete("/tunnel-transports/{bind_id}", status_code=204)
def delete_tunnel_transport(bind_id: int, db: Session = Depends(get_db)) -> None:
    row = vpn_svc.get_tunnel_transport(db, bind_id)
    if row is None:
        raise HTTPException(status_code=404, detail="underlagskobling ikke funnet")
    vpn_svc.delete_tunnel_transport(db, row)


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


@router.get("/wireguard-interfaces", response_model=list[IpamWireGuardInterfaceRead])
def list_wireguard_interfaces(
    device_id: int | None = Query(None, ge=1),
    db: Session = Depends(get_db),
) -> list[IpamWireGuardInterfaceRead]:
    return [wg_svc.iface_to_read(db, r) for r in wg_svc.list_interfaces(db, device_id=device_id)]


@router.post("/wireguard-interfaces", response_model=IpamWireGuardInterfaceRead)
def create_wireguard_interface(
    data: IpamWireGuardInterfaceCreate,
    db: Session = Depends(get_db),
) -> IpamWireGuardInterfaceRead:
    return wg_svc.iface_to_read(db, wg_svc.create_interface(db, data))


@router.get("/wireguard-interfaces/{iface_id}", response_model=IpamWireGuardInterfaceRead)
def get_wireguard_interface(iface_id: int, db: Session = Depends(get_db)) -> IpamWireGuardInterfaceRead:
    row = wg_svc.get_interface(db, iface_id)
    if row is None:
        raise HTTPException(status_code=404, detail="WireGuard-grensesnitt ikke funnet")
    return wg_svc.iface_to_read(db, row)


@router.patch("/wireguard-interfaces/{iface_id}", response_model=IpamWireGuardInterfaceRead)
def patch_wireguard_interface(
    iface_id: int,
    data: IpamWireGuardInterfaceUpdate,
    db: Session = Depends(get_db),
) -> IpamWireGuardInterfaceRead:
    row = wg_svc.get_interface(db, iface_id)
    if row is None:
        raise HTTPException(status_code=404, detail="WireGuard-grensesnitt ikke funnet")
    return wg_svc.iface_to_read(db, wg_svc.update_interface(db, row, data))


@router.delete("/wireguard-interfaces/{iface_id}", status_code=204)
def delete_wireguard_interface(iface_id: int, db: Session = Depends(get_db)) -> None:
    row = wg_svc.get_interface(db, iface_id)
    if row is None:
        raise HTTPException(status_code=404, detail="WireGuard-grensesnitt ikke funnet")
    wg_svc.delete_interface(db, row)


@router.get("/wireguard-interfaces/{iface_id}/peers", response_model=list[IpamWireGuardPeerRead])
def list_wireguard_peers(iface_id: int, db: Session = Depends(get_db)) -> list[IpamWireGuardPeerRead]:
    row = wg_svc.get_interface(db, iface_id)
    if row is None:
        raise HTTPException(status_code=404, detail="WireGuard-grensesnitt ikke funnet")
    return [wg_svc.peer_to_read(p) for p in sorted(row.peers, key=lambda x: x.slug)]


@router.post("/wireguard-interfaces/{iface_id}/peers", response_model=IpamWireGuardPeerRead)
def create_wireguard_peer(
    iface_id: int,
    data: IpamWireGuardPeerCreate,
    db: Session = Depends(get_db),
) -> IpamWireGuardPeerRead:
    row = wg_svc.get_interface(db, iface_id)
    if row is None:
        raise HTTPException(status_code=404, detail="WireGuard-grensesnitt ikke funnet")
    return wg_svc.peer_to_read(wg_svc.create_peer(db, row, data))


@router.patch("/wireguard-peers/{peer_id}", response_model=IpamWireGuardPeerRead)
def patch_wireguard_peer(
    peer_id: int,
    data: IpamWireGuardPeerUpdate,
    db: Session = Depends(get_db),
) -> IpamWireGuardPeerRead:
    row = wg_svc.get_peer(db, peer_id)
    if row is None:
        raise HTTPException(status_code=404, detail="WireGuard-peer ikke funnet")
    return wg_svc.peer_to_read(wg_svc.update_peer(db, row, data))


@router.delete("/wireguard-peers/{peer_id}", status_code=204)
def delete_wireguard_peer(peer_id: int, db: Session = Depends(get_db)) -> None:
    row = wg_svc.get_peer(db, peer_id)
    if row is None:
        raise HTTPException(status_code=404, detail="WireGuard-peer ikke funnet")
    wg_svc.delete_peer(db, row)


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
