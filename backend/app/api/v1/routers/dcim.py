"""DCIM REST API (fase 2 – kjerne)."""

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.config import get_settings
from app.core.media_storage import (
    resolve_device_model_image_path,
    resolve_manufacturer_logo_path,
    resolve_room_floorplan_path,
    resolve_site_banner_path,
)
from app.schemas.dcim import (
    ComponentClassCreate,
    ComponentChildTemplateCreate,
    ComponentChildTemplateRead,
    ComponentChildTemplateUpdate,
    ComponentClassEffectiveFieldRead,
    ComponentClassFieldCreate,
    ComponentClassFieldRead,
    ComponentClassFieldUpdate,
    ComponentClassParentCreate,
    ComponentClassParentRead,
    ComponentClassParentUpdate,
    ComponentClassRead,
    ComponentClassUpdate,
    ComponentCreate,
    ComponentExternalMappingProfileRead,
    ComponentExternalMappingPreviewRead,
    ComponentExternalMappingPreviewRequest,
    ComponentFieldImpactRead,
    ComponentIdentityCreate,
    ComponentIdentityRead,
    ComponentIdentityUpdate,
    ComponentMaterializeInterfacesRequest,
    ComponentRead,
    ComponentStandardCatalogSeedResponse,
    ComponentUpdate,
    DeviceInstanceCreate,
    DeviceInstanceComponentCreate,
    DeviceInstanceComponentRead,
    DeviceInstanceComponentUpdate,
    DeviceInstanceRead,
    DeviceInstanceUpdate,
    DeviceIpAssignmentCreate,
    DeviceIpAssignmentRead,
    DeviceIpAssignmentUpdate,
    DeviceInterfaceCreate,
    DeviceInterfaceRead,
    DeviceInterfaceUpdate,
    DeviceModelIdentityCreate,
    DeviceModelIdentityRead,
    DeviceModelIdentityUpdate,
    ExternalIdentityResolveMatch,
    ExternalIdentityResolveRequest,
    ExternalInventoryImportApplyRead,
    ExternalInventoryImportApplyRequest,
    ExternalInventoryImportPreviewRead,
    ExternalInventoryImportPreviewRequest,
    DeviceModelTemplateRead,
    DeviceModelTemplateQualityRead,
    NetBoxDtlApplyRead,
    NetBoxDtlApplyRequest,
    NetBoxDtlDownloadImportRequest,
    NetBoxDtlGithubImportRequest,
    NetBoxDtlImportRead,
    NetBoxDtlItemListRead,
    NetBoxDtlItemRead,
    NetBoxDtlPreviewRead,
    RedfishInventoryApplyRead,
    RedfishInventoryImportRequest,
    RedfishInventoryPreviewRead,
    RedfishSchemaBundleDownloadRequest,
    RedfishSchemaBundleRead,
    RedfishSchemaResourceRead,
    IpAssignmentCreate,
    IpAssignmentRead,
    IpAssignmentUpdate,
    DeviceModelCreate,
    DeviceModelComponentCreate,
    DeviceModelComponentRead,
    DeviceModelComponentUpdate,
    DeviceModelRead,
    DeviceModelUpdate,
    DeviceArtifactCreate,
    DeviceArtifactRead,
    DeviceArtifactBaselineAssignmentCreate,
    DeviceArtifactBaselineAssignmentRead,
    DeviceArtifactBaselineCreate,
    DeviceArtifactBaselineMemberCreate,
    DeviceArtifactBaselineRead,
    DeviceArtifactRecordCreate,
    DeviceArtifactRecordRead,
    DeviceArtifactUpdate,
    DeviceRoleCreate,
    DeviceRoleRead,
    DeviceRoleUpdate,
    DeviceTypeCreate,
    DeviceTypeRead,
    DeviceTypeUpdate,
    ManufacturerCreate,
    ManufacturerDetailRead,
    ManufacturerIdentityCreate,
    ManufacturerIdentityRead,
    ManufacturerIdentityUpdate,
    ManufacturerRead,
    ManufacturerUpdate,
    BuildingCreate,
    BuildingRead,
    BuildingUpdate,
    FloorCreate,
    FloorRead,
    FloorUpdate,
    RackCreate,
    RackPlacementCreate,
    RackPlacementRead,
    RackPlacementUpdate,
    RackRead,
    RackUpdate,
    RoomCreate,
    RoomRead,
    RoomUpdate,
    WingCreate,
    WingRead,
    WingUpdate,
    SiteCreate,
    SiteGeocodeRequest,
    SiteGeocodeResponse,
    SiteAccessGrantCreate,
    SiteAccessGrantRead,
    SiteAccessGrantUpdate,
    SiteRoleCreate,
    SiteRoleRead,
    SiteRoleUpdate,
    SiteRead,
    SiteUpdate,
    PowerSourceCreate,
    PowerSourceRead,
    PowerPanelCreate,
    PowerPanelRead,
    PowerCircuitCreate,
    PowerCircuitRead,
    PowerFeedCreate,
    PowerFeedRead,
    DevicePortCreate,
    DevicePortRead,
    DevicePortUpdate,
    CableCreate,
    CableRead,
    CablePathRead,
    FiberBundleCreate,
    FiberBundleMemberCreate,
    FiberBundleRead,
    FiberStrandCreate,
    FiberStrandRead,
    FiberStrandUpdate,
)
from app.services import dcim as dcim_svc
from app.services import dcim_power as power_svc
from app.services import geocoding as geocode_svc
from app.services import netbox_device_type_library as netbox_dtl_svc
from app.services import redfish_schema_bundle as redfish_schema_svc

router = APIRouter(prefix="/dcim", tags=["dcim"])

# --- Sites ---


@router.get("/sites", response_model=list[SiteRead])
def list_sites(db: Session = Depends(get_db)) -> list[SiteRead]:
    return dcim_svc.list_sites(db)


@router.post("/sites", response_model=SiteRead)
def create_site(data: SiteCreate, db: Session = Depends(get_db)) -> SiteRead:
    return dcim_svc.create_site(db, data)


@router.get("/sites/{site_id}", response_model=SiteRead)
def get_site(site_id: int, db: Session = Depends(get_db)) -> SiteRead:
    row = dcim_svc.get_site(db, site_id)
    if row is None:
        raise HTTPException(status_code=404, detail="site ikke funnet")
    return row


@router.patch("/sites/{site_id}", response_model=SiteRead)
def update_site(site_id: int, data: SiteUpdate, db: Session = Depends(get_db)) -> SiteRead:
    row = dcim_svc.get_site(db, site_id)
    if row is None:
        raise HTTPException(status_code=404, detail="site ikke funnet")
    return dcim_svc.update_site(db, row, data)


@router.post("/sites/{site_id}/geocode", response_model=SiteGeocodeResponse)
def geocode_site(site_id: int, body: SiteGeocodeRequest, db: Session = Depends(get_db)) -> SiteGeocodeResponse:
    site = dcim_svc.get_site(db, site_id)
    if site is None:
        raise HTTPException(status_code=404, detail="site ikke funnet")
    q = (body.query or "").strip()
    if not q:
        q = geocode_svc.build_site_query(
            {
                "address_line1": site.address_line1,
                "address_line2": site.address_line2,
                "postal_code": site.postal_code,
                "city": site.city,
                "county": site.county,
                "country": site.country,
            },
        )
    if not q.strip():
        raise HTTPException(status_code=400, detail="Mangler adresse: fyll inn adressefeltene eller send query")
    try:
        cand = geocode_svc.geocode_nominatim(q, limit=body.limit)
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=f"Geokoding feilet: {e!s}"[:500]) from e
    return SiteGeocodeResponse(
        query=q,
        candidates=[
            {"display_name": c.display_name, "latitude": c.latitude, "longitude": c.longitude} for c in cand
        ],
    )


@router.get("/site-roles", response_model=list[SiteRoleRead])
def list_site_roles(db: Session = Depends(get_db)) -> list[SiteRoleRead]:
    return dcim_svc.list_site_roles(db)


@router.post("/site-roles", response_model=SiteRoleRead)
def create_site_role(data: SiteRoleCreate, db: Session = Depends(get_db)) -> SiteRoleRead:
    return dcim_svc.create_site_role(db, data)


@router.patch("/site-roles/{role_id}", response_model=SiteRoleRead)
def update_site_role(role_id: int, data: SiteRoleUpdate, db: Session = Depends(get_db)) -> SiteRoleRead:
    row = dcim_svc.get_site_role(db, role_id)
    if row is None:
        raise HTTPException(status_code=404, detail="rolle ikke funnet")
    return dcim_svc.update_site_role(db, row, data)


@router.delete("/site-roles/{role_id}", status_code=204)
def delete_site_role(role_id: int, db: Session = Depends(get_db)) -> None:
    row = dcim_svc.get_site_role(db, role_id)
    if row is None:
        raise HTTPException(status_code=404, detail="rolle ikke funnet")
    dcim_svc.delete_site_role(db, row)


@router.get("/sites/{site_id}/access", response_model=list[SiteAccessGrantRead])
def list_site_access_grants(
    site_id: int,
    is_contact: bool | None = Query(None),
    db: Session = Depends(get_db),
) -> list[SiteAccessGrantRead]:
    if dcim_svc.get_site(db, site_id) is None:
        raise HTTPException(status_code=404, detail="site ikke funnet")
    return dcim_svc.list_site_access_grants(db, site_id=site_id, is_contact=is_contact)


@router.post("/sites/{site_id}/access", response_model=SiteAccessGrantRead)
def create_site_access_grant(
    site_id: int,
    data: SiteAccessGrantCreate,
    db: Session = Depends(get_db),
) -> SiteAccessGrantRead:
    return dcim_svc.create_site_access_grant(db, site_id=site_id, data=data)


@router.patch("/sites/{site_id}/access/{grant_id}", response_model=SiteAccessGrantRead)
def update_site_access_grant(
    site_id: int,
    grant_id: int,
    data: SiteAccessGrantUpdate,
    db: Session = Depends(get_db),
) -> SiteAccessGrantRead:
    row = dcim_svc.get_site_access_grant(db, grant_id)
    if row is None or row.site_id != site_id:
        raise HTTPException(status_code=404, detail="tilgang ikke funnet")
    return dcim_svc.update_site_access_grant(db, row, data)


@router.delete("/sites/{site_id}/access/{grant_id}", status_code=204)
def delete_site_access_grant(site_id: int, grant_id: int, db: Session = Depends(get_db)) -> None:
    row = dcim_svc.get_site_access_grant(db, grant_id)
    if row is None or row.site_id != site_id:
        raise HTTPException(status_code=404, detail="tilgang ikke funnet")
    dcim_svc.delete_site_access_grant(db, row)


@router.get("/sites/{site_id}/banner")
def get_site_banner(site_id: int, db: Session = Depends(get_db)) -> FileResponse:
    row = dcim_svc.get_site(db, site_id)
    if row is None or not row.banner_relpath or not row.banner_mime_type:
        raise HTTPException(status_code=404, detail="banner finnes ikke")
    path = resolve_site_banner_path(get_settings().upload_root_path, row.banner_relpath)
    if path is None:
        raise HTTPException(status_code=404, detail="banner finnes ikke")
    return FileResponse(path, media_type=row.banner_mime_type)


@router.post("/sites/{site_id}/banner", response_model=SiteRead)
async def upload_site_banner(
    site_id: int,
    db: Session = Depends(get_db),
    file: UploadFile = File(...),
) -> SiteRead:
    row = dcim_svc.get_site(db, site_id)
    if row is None:
        raise HTTPException(status_code=404, detail="site ikke funnet")
    content = await file.read()
    mime = file.content_type or "application/octet-stream"
    dcim_svc.set_site_banner(db, row, content, mime)
    return row


@router.delete("/sites/{site_id}/banner", response_model=SiteRead)
def remove_site_banner(site_id: int, db: Session = Depends(get_db)) -> SiteRead:
    row = dcim_svc.get_site(db, site_id)
    if row is None:
        raise HTTPException(status_code=404, detail="site ikke funnet")
    dcim_svc.clear_site_banner(db, row)
    return row


@router.delete("/sites/{site_id}", status_code=204)
def delete_site(site_id: int, db: Session = Depends(get_db)) -> None:
    row = dcim_svc.get_site(db, site_id)
    if row is None:
        raise HTTPException(status_code=404, detail="site ikke funnet")
    dcim_svc.delete_site(db, row)


# --- Buildings / wings / floors ---


@router.get("/buildings", response_model=list[BuildingRead])
def list_buildings(
    db: Session = Depends(get_db),
    site_id: int | None = Query(None),
) -> list[BuildingRead]:
    return dcim_svc.list_buildings(db, site_id=site_id)


@router.post("/buildings", response_model=BuildingRead)
def create_building(data: BuildingCreate, db: Session = Depends(get_db)) -> BuildingRead:
    return dcim_svc.create_building(db, data)


@router.get("/buildings/{building_id}", response_model=BuildingRead)
def get_building(building_id: int, db: Session = Depends(get_db)) -> BuildingRead:
    row = dcim_svc.get_building(db, building_id)
    if row is None:
        raise HTTPException(status_code=404, detail="bygg ikke funnet")
    return row


@router.patch("/buildings/{building_id}", response_model=BuildingRead)
def update_building(building_id: int, data: BuildingUpdate, db: Session = Depends(get_db)) -> BuildingRead:
    row = dcim_svc.get_building(db, building_id)
    if row is None:
        raise HTTPException(status_code=404, detail="bygg ikke funnet")
    return dcim_svc.update_building(db, row, data)


@router.delete("/buildings/{building_id}", status_code=204)
def delete_building(building_id: int, db: Session = Depends(get_db)) -> None:
    row = dcim_svc.get_building(db, building_id)
    if row is None:
        raise HTTPException(status_code=404, detail="bygg ikke funnet")
    dcim_svc.delete_building(db, row)


@router.get("/wings", response_model=list[WingRead])
def list_wings(
    db: Session = Depends(get_db),
    building_id: int | None = Query(None),
) -> list[WingRead]:
    return dcim_svc.list_wings(db, building_id=building_id)


@router.post("/wings", response_model=WingRead)
def create_wing(data: WingCreate, db: Session = Depends(get_db)) -> WingRead:
    return dcim_svc.create_wing(db, data)


@router.get("/wings/{wing_id}", response_model=WingRead)
def get_wing(wing_id: int, db: Session = Depends(get_db)) -> WingRead:
    row = dcim_svc.get_wing(db, wing_id)
    if row is None:
        raise HTTPException(status_code=404, detail="fløy ikke funnet")
    return row


@router.patch("/wings/{wing_id}", response_model=WingRead)
def update_wing(wing_id: int, data: WingUpdate, db: Session = Depends(get_db)) -> WingRead:
    row = dcim_svc.get_wing(db, wing_id)
    if row is None:
        raise HTTPException(status_code=404, detail="fløy ikke funnet")
    return dcim_svc.update_wing(db, row, data)


@router.delete("/wings/{wing_id}", status_code=204)
def delete_wing(wing_id: int, db: Session = Depends(get_db)) -> None:
    row = dcim_svc.get_wing(db, wing_id)
    if row is None:
        raise HTTPException(status_code=404, detail="fløy ikke funnet")
    dcim_svc.delete_wing(db, row)


@router.get("/floors", response_model=list[FloorRead])
def list_floors(
    db: Session = Depends(get_db),
    building_id: int | None = Query(None),
    wing_id: int | None = Query(None),
) -> list[FloorRead]:
    return dcim_svc.list_floors(db, building_id=building_id, wing_id=wing_id)


@router.post("/floors", response_model=FloorRead)
def create_floor(data: FloorCreate, db: Session = Depends(get_db)) -> FloorRead:
    return dcim_svc.create_floor(db, data)


@router.get("/floors/{floor_id}", response_model=FloorRead)
def get_floor(floor_id: int, db: Session = Depends(get_db)) -> FloorRead:
    row = dcim_svc.get_floor(db, floor_id)
    if row is None:
        raise HTTPException(status_code=404, detail="etasje ikke funnet")
    return row


@router.patch("/floors/{floor_id}", response_model=FloorRead)
def update_floor(floor_id: int, data: FloorUpdate, db: Session = Depends(get_db)) -> FloorRead:
    row = dcim_svc.get_floor(db, floor_id)
    if row is None:
        raise HTTPException(status_code=404, detail="etasje ikke funnet")
    return dcim_svc.update_floor(db, row, data)


@router.delete("/floors/{floor_id}", status_code=204)
def delete_floor(floor_id: int, db: Session = Depends(get_db)) -> None:
    row = dcim_svc.get_floor(db, floor_id)
    if row is None:
        raise HTTPException(status_code=404, detail="etasje ikke funnet")
    dcim_svc.delete_floor(db, row)


# --- Rooms ---


@router.get("/rooms", response_model=list[RoomRead])
def list_rooms(
    db: Session = Depends(get_db),
    site_id: int | None = Query(None),
    building_id: int | None = Query(None),
    wing_id: int | None = Query(None),
    floor_id: int | None = Query(None),
) -> list[RoomRead]:
    return [
        dcim_svc.room_to_read(r)
        for r in dcim_svc.list_rooms(
            db,
            site_id=site_id,
            building_id=building_id,
            wing_id=wing_id,
            floor_id=floor_id,
        )
    ]


@router.post("/rooms", response_model=RoomRead)
def create_room(data: RoomCreate, db: Session = Depends(get_db)) -> RoomRead:
    return dcim_svc.room_to_read(dcim_svc.create_room(db, data))


@router.get("/rooms/{room_id}", response_model=RoomRead)
def get_room(room_id: int, db: Session = Depends(get_db)) -> RoomRead:
    row = dcim_svc.get_room(db, room_id)
    if row is None:
        raise HTTPException(status_code=404, detail="room ikke funnet")
    return dcim_svc.room_to_read(row)


@router.patch("/rooms/{room_id}", response_model=RoomRead)
def update_room(room_id: int, data: RoomUpdate, db: Session = Depends(get_db)) -> RoomRead:
    row = dcim_svc.get_room(db, room_id)
    if row is None:
        raise HTTPException(status_code=404, detail="room ikke funnet")
    return dcim_svc.room_to_read(dcim_svc.update_room(db, row, data))


@router.delete("/rooms/{room_id}", status_code=204)
def delete_room(room_id: int, db: Session = Depends(get_db)) -> None:
    row = dcim_svc.get_room(db, room_id)
    if row is None:
        raise HTTPException(status_code=404, detail="room ikke funnet")
    dcim_svc.delete_room(db, row)


@router.get("/rooms/{room_id}/floorplan")
def get_room_floorplan(room_id: int, db: Session = Depends(get_db)) -> FileResponse:
    row = dcim_svc.get_room(db, room_id)
    if row is None or not row.floorplan_relpath or not row.floorplan_mime_type:
        raise HTTPException(status_code=404, detail="plantegning finnes ikke")
    path = resolve_room_floorplan_path(get_settings().upload_root_path, row.floorplan_relpath)
    if path is None:
        raise HTTPException(status_code=404, detail="plantegning finnes ikke")
    return FileResponse(path, media_type=row.floorplan_mime_type)


@router.post("/rooms/{room_id}/floorplan", response_model=RoomRead)
async def upload_room_floorplan(
    room_id: int,
    db: Session = Depends(get_db),
    file: UploadFile = File(...),
) -> RoomRead:
    row = dcim_svc.get_room(db, room_id)
    if row is None:
        raise HTTPException(status_code=404, detail="room ikke funnet")
    content = await file.read()
    mime = file.content_type or "application/octet-stream"
    dcim_svc.set_room_floorplan(db, row, content, mime)
    return dcim_svc.room_to_read(row)


@router.delete("/rooms/{room_id}/floorplan", response_model=RoomRead)
def remove_room_floorplan(room_id: int, db: Session = Depends(get_db)) -> RoomRead:
    row = dcim_svc.get_room(db, room_id)
    if row is None:
        raise HTTPException(status_code=404, detail="room ikke funnet")
    dcim_svc.clear_room_floorplan(db, row)
    return dcim_svc.room_to_read(row)


# --- Racks ---


@router.get("/racks", response_model=list[RackRead])
def list_racks(
    db: Session = Depends(get_db),
    room_id: int | None = Query(None),
) -> list[RackRead]:
    return dcim_svc.list_racks(db, room_id=room_id)


@router.post("/racks", response_model=RackRead)
def create_rack(data: RackCreate, db: Session = Depends(get_db)) -> RackRead:
    return dcim_svc.create_rack(db, data)


@router.get("/racks/{rack_id}", response_model=RackRead)
def get_rack(rack_id: int, db: Session = Depends(get_db)) -> RackRead:
    row = dcim_svc.get_rack(db, rack_id)
    if row is None:
        raise HTTPException(status_code=404, detail="rack ikke funnet")
    return row


@router.patch("/racks/{rack_id}", response_model=RackRead)
def update_rack(rack_id: int, data: RackUpdate, db: Session = Depends(get_db)) -> RackRead:
    row = dcim_svc.get_rack(db, rack_id)
    if row is None:
        raise HTTPException(status_code=404, detail="rack ikke funnet")
    return dcim_svc.update_rack(db, row, data)


@router.delete("/racks/{rack_id}", status_code=204)
def delete_rack(rack_id: int, db: Session = Depends(get_db)) -> None:
    row = dcim_svc.get_rack(db, rack_id)
    if row is None:
        raise HTTPException(status_code=404, detail="rack ikke funnet")
    dcim_svc.delete_rack(db, row)


# --- Manufacturers ---


@router.get("/manufacturers", response_model=list[ManufacturerRead])
def list_manufacturers(db: Session = Depends(get_db)) -> list[ManufacturerRead]:
    return dcim_svc.list_manufacturers(db)


@router.post("/manufacturers", response_model=ManufacturerRead)
def create_manufacturer(data: ManufacturerCreate, db: Session = Depends(get_db)) -> ManufacturerRead:
    return dcim_svc.create_manufacturer(db, data)


@router.get("/manufacturers/{mid}/logo")
def get_manufacturer_logo(mid: int, db: Session = Depends(get_db)) -> FileResponse:
    row = dcim_svc.get_manufacturer(db, mid)
    if row is None or not row.logo_relpath or not row.logo_mime_type:
        raise HTTPException(status_code=404, detail="logo finnes ikke")
    path = resolve_manufacturer_logo_path(get_settings().upload_root_path, row.logo_relpath)
    if path is None:
        raise HTTPException(status_code=404, detail="logo finnes ikke")
    return FileResponse(path, media_type=row.logo_mime_type)


@router.post("/manufacturers/{mid}/logo", response_model=ManufacturerRead)
async def upload_manufacturer_logo(
    mid: int,
    db: Session = Depends(get_db),
    file: UploadFile = File(...),
) -> ManufacturerRead:
    row = dcim_svc.get_manufacturer(db, mid)
    if row is None:
        raise HTTPException(status_code=404, detail="manufacturer ikke funnet")
    content = await file.read()
    mime = file.content_type or "application/octet-stream"
    dcim_svc.set_manufacturer_logo(db, row, content, mime)
    return dcim_svc.manufacturer_read(row)


@router.delete("/manufacturers/{mid}/logo", response_model=ManufacturerRead)
def remove_manufacturer_logo(mid: int, db: Session = Depends(get_db)) -> ManufacturerRead:
    row = dcim_svc.get_manufacturer(db, mid)
    if row is None:
        raise HTTPException(status_code=404, detail="manufacturer ikke funnet")
    dcim_svc.clear_manufacturer_logo(db, row)
    return dcim_svc.manufacturer_read(row)


@router.get("/manufacturers/{mid}", response_model=ManufacturerDetailRead)
def get_manufacturer_detail(mid: int, db: Session = Depends(get_db)) -> ManufacturerDetailRead:
    detail = dcim_svc.get_manufacturer_detail(db, mid)
    if detail is None:
        raise HTTPException(status_code=404, detail="manufacturer ikke funnet")
    return detail


@router.patch("/manufacturers/{mid}", response_model=ManufacturerRead)
def patch_manufacturer(mid: int, data: ManufacturerUpdate, db: Session = Depends(get_db)) -> ManufacturerRead:
    row = dcim_svc.get_manufacturer(db, mid)
    if row is None:
        raise HTTPException(status_code=404, detail="manufacturer ikke funnet")
    return dcim_svc.update_manufacturer(db, row, data)


@router.delete("/manufacturers/{mid}", status_code=204)
def delete_manufacturer(mid: int, db: Session = Depends(get_db)) -> None:
    row = dcim_svc.get_manufacturer(db, mid)
    if row is None:
        raise HTTPException(status_code=404, detail="manufacturer ikke funnet")
    dcim_svc.delete_manufacturer(db, row)


@router.get("/manufacturer-identities", response_model=list[ManufacturerIdentityRead])
def list_manufacturer_identities(
    manufacturer_id: int | None = Query(None),
    identity_type: str | None = Query(None),
    namespace: str | None = Query(None),
    q: str | None = Query(None),
    db: Session = Depends(get_db),
) -> list[ManufacturerIdentityRead]:
    return dcim_svc.list_manufacturer_identities(
        db,
        manufacturer_id=manufacturer_id,
        identity_type=identity_type,
        namespace=namespace,
        q=q,
    )


@router.get("/manufacturers/{mid}/identities", response_model=list[ManufacturerIdentityRead])
def list_manufacturer_identities_for_manufacturer(mid: int, db: Session = Depends(get_db)) -> list[ManufacturerIdentityRead]:
    if dcim_svc.get_manufacturer(db, mid) is None:
        raise HTTPException(status_code=404, detail="manufacturer ikke funnet")
    return dcim_svc.list_manufacturer_identities(db, manufacturer_id=mid)


@router.post("/manufacturers/{mid}/identities", response_model=ManufacturerIdentityRead)
def create_manufacturer_identity(
    mid: int,
    data: ManufacturerIdentityCreate,
    db: Session = Depends(get_db),
) -> ManufacturerIdentityRead:
    return dcim_svc.create_manufacturer_identity(db, mid, data)


@router.patch("/manufacturer-identities/{identity_id}", response_model=ManufacturerIdentityRead)
def patch_manufacturer_identity(
    identity_id: int,
    data: ManufacturerIdentityUpdate,
    db: Session = Depends(get_db),
) -> ManufacturerIdentityRead:
    row = dcim_svc.get_manufacturer_identity(db, identity_id)
    if row is None:
        raise HTTPException(status_code=404, detail="manufacturer-identitet ikke funnet")
    return dcim_svc.update_manufacturer_identity(db, row, data)


@router.delete("/manufacturer-identities/{identity_id}", status_code=204)
def delete_manufacturer_identity(identity_id: int, db: Session = Depends(get_db)) -> None:
    row = dcim_svc.get_manufacturer_identity(db, identity_id)
    if row is None:
        raise HTTPException(status_code=404, detail="manufacturer-identitet ikke funnet")
    dcim_svc.delete_manufacturer_identity(db, row)


# --- Device types ---


@router.get("/device-types", response_model=list[DeviceTypeRead])
def list_device_types(db: Session = Depends(get_db)) -> list[DeviceTypeRead]:
    return dcim_svc.list_device_types(db)


@router.post("/device-types", response_model=DeviceTypeRead)
def create_device_type(data: DeviceTypeCreate, db: Session = Depends(get_db)) -> DeviceTypeRead:
    return dcim_svc.create_device_type(db, data)


@router.get("/device-types/{tid}", response_model=DeviceTypeRead)
def get_device_type(tid: int, db: Session = Depends(get_db)) -> DeviceTypeRead:
    row = dcim_svc.get_device_type(db, tid)
    if row is None:
        raise HTTPException(status_code=404, detail="device_type ikke funnet")
    return row


@router.patch("/device-types/{tid}", response_model=DeviceTypeRead)
def patch_device_type(tid: int, data: DeviceTypeUpdate, db: Session = Depends(get_db)) -> DeviceTypeRead:
    row = dcim_svc.get_device_type(db, tid)
    if row is None:
        raise HTTPException(status_code=404, detail="device_type ikke funnet")
    return dcim_svc.update_device_type(db, row, data)


@router.delete("/device-types/{tid}", status_code=204)
def delete_device_type(tid: int, db: Session = Depends(get_db)) -> None:
    row = dcim_svc.get_device_type(db, tid)
    if row is None:
        raise HTTPException(status_code=404, detail="device_type ikke funnet")
    dcim_svc.delete_device_type(db, row)


# --- Device roles ---


@router.get("/device-roles", response_model=list[DeviceRoleRead])
def list_device_roles(db: Session = Depends(get_db)) -> list[DeviceRoleRead]:
    return dcim_svc.list_device_roles(db)


@router.post("/device-roles", response_model=DeviceRoleRead)
def create_device_role(data: DeviceRoleCreate, db: Session = Depends(get_db)) -> DeviceRoleRead:
    return dcim_svc.create_device_role(db, data)


@router.get("/device-roles/{rid}", response_model=DeviceRoleRead)
def get_device_role(rid: int, db: Session = Depends(get_db)) -> DeviceRoleRead:
    row = dcim_svc.get_device_role(db, rid)
    if row is None:
        raise HTTPException(status_code=404, detail="device_role ikke funnet")
    return row


@router.patch("/device-roles/{rid}", response_model=DeviceRoleRead)
def patch_device_role(rid: int, data: DeviceRoleUpdate, db: Session = Depends(get_db)) -> DeviceRoleRead:
    row = dcim_svc.get_device_role(db, rid)
    if row is None:
        raise HTTPException(status_code=404, detail="device_role ikke funnet")
    return dcim_svc.update_device_role(db, row, data)


@router.delete("/device-roles/{rid}", status_code=204)
def delete_device_role(rid: int, db: Session = Depends(get_db)) -> None:
    row = dcim_svc.get_device_role(db, rid)
    if row is None:
        raise HTTPException(status_code=404, detail="device_role ikke funnet")
    dcim_svc.delete_device_role(db, row)


# --- Artifacts (firmware/BIOS/OS-image, recorded only) ---


@router.get("/device-artifacts", response_model=list[DeviceArtifactRead])
def list_device_artifacts(db: Session = Depends(get_db)) -> list[DeviceArtifactRead]:
    return [dcim_svc.artifact_to_read(x) for x in dcim_svc.list_device_artifacts(db)]


@router.post("/device-artifacts", response_model=DeviceArtifactRead)
def create_device_artifact(data: DeviceArtifactCreate, db: Session = Depends(get_db)) -> DeviceArtifactRead:
    return dcim_svc.artifact_to_read(dcim_svc.create_device_artifact(db, data))


@router.get("/device-artifacts/{aid}", response_model=DeviceArtifactRead)
def get_device_artifact(aid: int, db: Session = Depends(get_db)) -> DeviceArtifactRead:
    row = dcim_svc.get_device_artifact(db, aid)
    if row is None:
        raise HTTPException(status_code=404, detail="artefakt ikke funnet")
    return dcim_svc.artifact_to_read(row)


@router.patch("/device-artifacts/{aid}", response_model=DeviceArtifactRead)
def patch_device_artifact(aid: int, data: DeviceArtifactUpdate, db: Session = Depends(get_db)) -> DeviceArtifactRead:
    row = dcim_svc.get_device_artifact(db, aid)
    if row is None:
        raise HTTPException(status_code=404, detail="artefakt ikke funnet")
    return dcim_svc.artifact_to_read(dcim_svc.update_device_artifact(db, row, data))


@router.delete("/device-artifacts/{aid}", status_code=204)
def delete_device_artifact(aid: int, db: Session = Depends(get_db)) -> None:
    row = dcim_svc.get_device_artifact(db, aid)
    if row is None:
        raise HTTPException(status_code=404, detail="artefakt ikke funnet")
    dcim_svc.delete_device_artifact(db, row)


@router.get("/devices/{did}/artifacts", response_model=list[DeviceArtifactRecordRead])
def list_device_artifact_records(did: int, db: Session = Depends(get_db)) -> list[DeviceArtifactRecordRead]:
    device = dcim_svc.get_device(db, did)
    if device is None:
        raise HTTPException(status_code=404, detail="enhet ikke funnet")
    return [dcim_svc.record_to_read(db, r) for r in dcim_svc.list_device_artifact_records(db, did)]


@router.post("/devices/{did}/artifacts", response_model=DeviceArtifactRecordRead)
def record_device_artifact(
    did: int,
    data: DeviceArtifactRecordCreate,
    db: Session = Depends(get_db),
) -> DeviceArtifactRecordRead:
    device = dcim_svc.get_device(db, did)
    if device is None:
        raise HTTPException(status_code=404, detail="enhet ikke funnet")
    return dcim_svc.record_to_read(db, dcim_svc.record_device_artifact(db, device, data))


@router.delete("/devices/{did}/artifacts/{rid}", status_code=204)
def delete_device_artifact_record(did: int, rid: int, db: Session = Depends(get_db)) -> None:
    row = dcim_svc.get_device_artifact_record(db, rid)
    if row is None or row.device_id != did:
        raise HTTPException(status_code=404, detail="artefakt-registrering ikke funnet")
    dcim_svc.delete_device_artifact_record(db, row)


@router.get("/device-artifact-baselines", response_model=list[DeviceArtifactBaselineRead])
def list_artifact_baselines(db: Session = Depends(get_db)) -> list[DeviceArtifactBaselineRead]:
    return [dcim_svc.artifact_baseline_to_read(db, x) for x in dcim_svc.list_artifact_baselines(db)]


@router.post("/device-artifact-baselines", response_model=DeviceArtifactBaselineRead)
def create_artifact_baseline(
    data: DeviceArtifactBaselineCreate,
    db: Session = Depends(get_db),
) -> DeviceArtifactBaselineRead:
    return dcim_svc.artifact_baseline_to_read(db, dcim_svc.create_artifact_baseline(db, data))


@router.get("/device-artifact-baselines/{bid}", response_model=DeviceArtifactBaselineRead)
def get_artifact_baseline(bid: int, db: Session = Depends(get_db)) -> DeviceArtifactBaselineRead:
    row = dcim_svc.get_artifact_baseline(db, bid)
    if row is None:
        raise HTTPException(status_code=404, detail="baseline ikke funnet")
    return dcim_svc.artifact_baseline_to_read(db, row)


@router.post("/device-artifact-baselines/{bid}/members", response_model=DeviceArtifactBaselineRead)
def add_artifact_baseline_member(
    bid: int,
    data: DeviceArtifactBaselineMemberCreate,
    db: Session = Depends(get_db),
) -> DeviceArtifactBaselineRead:
    row = dcim_svc.get_artifact_baseline(db, bid)
    if row is None:
        raise HTTPException(status_code=404, detail="baseline ikke funnet")
    dcim_svc.add_artifact_baseline_member(db, row, data)
    return dcim_svc.artifact_baseline_to_read(db, row)


@router.delete("/device-artifact-baselines/{bid}", status_code=204)
def delete_artifact_baseline(bid: int, db: Session = Depends(get_db)) -> None:
    row = dcim_svc.get_artifact_baseline(db, bid)
    if row is None:
        raise HTTPException(status_code=404, detail="baseline ikke funnet")
    dcim_svc.delete_artifact_baseline(db, row)


@router.delete("/device-artifact-baseline-members/{mid}", status_code=204)
def delete_artifact_baseline_member(mid: int, db: Session = Depends(get_db)) -> None:
    row = dcim_svc.get_artifact_baseline_member(db, mid)
    if row is None:
        raise HTTPException(status_code=404, detail="baseline-medlem ikke funnet")
    dcim_svc.delete_artifact_baseline_member(db, row)


@router.get("/devices/{did}/artifact-baselines", response_model=list[DeviceArtifactBaselineAssignmentRead])
def list_device_artifact_baseline_assignments(
    did: int,
    db: Session = Depends(get_db),
) -> list[DeviceArtifactBaselineAssignmentRead]:
    device = dcim_svc.get_device(db, did)
    if device is None:
        raise HTTPException(status_code=404, detail="enhet ikke funnet")
    return [
        dcim_svc.artifact_baseline_assignment_to_read(db, r)
        for r in dcim_svc.list_artifact_baseline_assignments(db, device_id=did)
    ]


@router.post("/devices/{did}/artifact-baselines", response_model=DeviceArtifactBaselineAssignmentRead)
def assign_device_artifact_baseline(
    did: int,
    data: DeviceArtifactBaselineAssignmentCreate,
    db: Session = Depends(get_db),
) -> DeviceArtifactBaselineAssignmentRead:
    device = dcim_svc.get_device(db, did)
    if device is None:
        raise HTTPException(status_code=404, detail="enhet ikke funnet")
    return dcim_svc.artifact_baseline_assignment_to_read(
        db,
        dcim_svc.assign_artifact_baseline(db, device, data),
    )


@router.delete("/devices/{did}/artifact-baselines/{aid}", status_code=204)
def delete_device_artifact_baseline_assignment(
    did: int,
    aid: int,
    db: Session = Depends(get_db),
) -> None:
    row = dcim_svc.get_artifact_baseline_assignment(db, aid)
    if row is None or row.device_id != did:
        raise HTTPException(status_code=404, detail="baseline-tilordning ikke funnet")
    dcim_svc.delete_artifact_baseline_assignment(db, row)


# --- Component classes / library ---


@router.get("/component-classes", response_model=list[ComponentClassRead])
def list_component_classes(db: Session = Depends(get_db)) -> list[ComponentClassRead]:
    return dcim_svc.list_component_classes(db)


@router.post("/component-classes", response_model=ComponentClassRead)
def create_component_class(data: ComponentClassCreate, db: Session = Depends(get_db)) -> ComponentClassRead:
    return dcim_svc.create_component_class(db, data)


@router.post("/component-classes/seed-standard", response_model=ComponentStandardCatalogSeedResponse)
def seed_standard_component_catalog(db: Session = Depends(get_db)) -> ComponentStandardCatalogSeedResponse:
    return dcim_svc.seed_standard_component_catalog(db)


@router.get("/component-mappings", response_model=list[ComponentExternalMappingProfileRead])
def list_component_external_mappings(source: str | None = Query(None)) -> list[ComponentExternalMappingProfileRead]:
    return dcim_svc.list_component_external_mapping_profiles(source)


@router.post("/component-mappings/preview", response_model=ComponentExternalMappingPreviewRead)
def preview_component_external_mapping(
    data: ComponentExternalMappingPreviewRequest,
    db: Session = Depends(get_db),
) -> ComponentExternalMappingPreviewRead:
    return dcim_svc.preview_component_external_mapping(db, data)


@router.post("/identity-resolver/resolve", response_model=list[ExternalIdentityResolveMatch])
def resolve_external_identities(
    data: ExternalIdentityResolveRequest,
    db: Session = Depends(get_db),
) -> list[ExternalIdentityResolveMatch]:
    return dcim_svc.resolve_external_identities(db, data)


@router.post("/component-imports/preview", response_model=ExternalInventoryImportPreviewRead)
def preview_component_import(
    data: ExternalInventoryImportPreviewRequest,
    db: Session = Depends(get_db),
) -> ExternalInventoryImportPreviewRead:
    return dcim_svc.preview_external_inventory_import(db, data)


@router.post("/component-imports/apply", response_model=ExternalInventoryImportApplyRead)
def apply_component_import(
    data: ExternalInventoryImportApplyRequest,
    db: Session = Depends(get_db),
) -> ExternalInventoryImportApplyRead:
    return dcim_svc.apply_external_inventory_import(db, data)


@router.post("/redfish/schema-bundles/upload", response_model=RedfishSchemaBundleRead)
async def upload_redfish_schema_bundle(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> RedfishSchemaBundleRead:
    return await redfish_schema_svc.import_schema_bundle_upload(db, get_settings(), file)


@router.post("/redfish/schema-bundles/download", response_model=RedfishSchemaBundleRead)
async def download_redfish_schema_bundle(
    data: RedfishSchemaBundleDownloadRequest,
    db: Session = Depends(get_db),
) -> RedfishSchemaBundleRead:
    return await redfish_schema_svc.import_schema_bundle_download(db, get_settings(), data.url, data.name)


@router.get("/redfish/schema-bundles", response_model=list[RedfishSchemaBundleRead])
def list_redfish_schema_bundles(db: Session = Depends(get_db)) -> list[RedfishSchemaBundleRead]:
    return redfish_schema_svc.list_schema_bundles(db)


@router.get("/redfish/schema-bundles/{bundle_id}/resources", response_model=list[RedfishSchemaResourceRead])
def list_redfish_schema_resources(
    bundle_id: int,
    db: Session = Depends(get_db),
) -> list[RedfishSchemaResourceRead]:
    return redfish_schema_svc.list_schema_resources(db, bundle_id)


@router.post("/redfish/inventory/preview", response_model=RedfishInventoryPreviewRead)
def preview_redfish_inventory(
    data: RedfishInventoryImportRequest,
    db: Session = Depends(get_db),
) -> RedfishInventoryPreviewRead:
    result = redfish_schema_svc.preview_redfish_inventory(db, get_settings(), data, apply=False)
    return result  # type: ignore[return-value]


@router.post("/redfish/inventory/apply", response_model=RedfishInventoryApplyRead)
def apply_redfish_inventory(
    data: RedfishInventoryImportRequest,
    db: Session = Depends(get_db),
) -> RedfishInventoryApplyRead:
    result = redfish_schema_svc.preview_redfish_inventory(db, get_settings(), data, apply=True)
    return result  # type: ignore[return-value]


@router.post("/netbox-dtl/imports/github", response_model=NetBoxDtlImportRead)
async def import_netbox_dtl_github(
    data: NetBoxDtlGithubImportRequest,
    db: Session = Depends(get_db),
) -> NetBoxDtlImportRead:
    return await netbox_dtl_svc.import_github(db, get_settings(), data.branch)


@router.post("/netbox-dtl/imports/upload", response_model=NetBoxDtlImportRead)
async def upload_netbox_dtl(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> NetBoxDtlImportRead:
    return await netbox_dtl_svc.import_upload(db, get_settings(), file)


@router.post("/netbox-dtl/imports/download", response_model=NetBoxDtlImportRead)
async def download_netbox_dtl(
    data: NetBoxDtlDownloadImportRequest,
    db: Session = Depends(get_db),
) -> NetBoxDtlImportRead:
    return await netbox_dtl_svc.import_download(db, get_settings(), data.url, name=data.name)


@router.get("/netbox-dtl/imports", response_model=list[NetBoxDtlImportRead])
def list_netbox_dtl_imports(db: Session = Depends(get_db)) -> list[NetBoxDtlImportRead]:
    return netbox_dtl_svc.list_imports(db)


@router.get("/netbox-dtl/items", response_model=list[NetBoxDtlItemRead])
def list_netbox_dtl_items(
    import_id: int | None = Query(None),
    q: str | None = Query(None),
    manufacturer: str | None = Query(None),
    limit: int = Query(200, ge=1, le=1000),
    db: Session = Depends(get_db),
) -> list[NetBoxDtlItemRead]:
    return netbox_dtl_svc.list_items(db, import_id=import_id, q=q, manufacturer=manufacturer, limit=limit)


@router.get("/netbox-dtl/items/search", response_model=NetBoxDtlItemListRead)
def search_netbox_dtl_items(
    import_id: int | None = Query(None),
    q: str | None = Query(None),
    manufacturer: str | None = Query(None),
    limit: int = Query(200, ge=1, le=10000),
    db: Session = Depends(get_db),
) -> NetBoxDtlItemListRead:
    return netbox_dtl_svc.search_items(db, import_id=import_id, q=q, manufacturer=manufacturer, limit=limit)


@router.post("/netbox-dtl/preview", response_model=NetBoxDtlPreviewRead)
def preview_netbox_dtl_import(
    data: NetBoxDtlApplyRequest,
    db: Session = Depends(get_db),
) -> NetBoxDtlPreviewRead:
    return netbox_dtl_svc.preview_apply(db, data)


@router.post("/netbox-dtl/apply", response_model=NetBoxDtlApplyRead)
def apply_netbox_dtl_import(
    data: NetBoxDtlApplyRequest,
    db: Session = Depends(get_db),
) -> NetBoxDtlApplyRead:
    return netbox_dtl_svc.apply_import(db, get_settings(), data)


@router.get("/component-mappings/{source}", response_model=ComponentExternalMappingProfileRead)
def get_component_external_mapping(source: str) -> ComponentExternalMappingProfileRead:
    row = dcim_svc.get_component_external_mapping_profile(source)
    if row is None:
        raise HTTPException(status_code=404, detail="mapping-kilde ikke funnet")
    return row


@router.get("/component-classes/{class_id}", response_model=ComponentClassRead)
def get_component_class(class_id: int, db: Session = Depends(get_db)) -> ComponentClassRead:
    row = dcim_svc.get_component_class(db, class_id)
    if row is None:
        raise HTTPException(status_code=404, detail="komponentklasse ikke funnet")
    return dcim_svc.component_class_read(row)


@router.patch("/component-classes/{class_id}", response_model=ComponentClassRead)
def patch_component_class(
    class_id: int,
    data: ComponentClassUpdate,
    db: Session = Depends(get_db),
) -> ComponentClassRead:
    row = dcim_svc.get_component_class(db, class_id)
    if row is None:
        raise HTTPException(status_code=404, detail="komponentklasse ikke funnet")
    return dcim_svc.update_component_class(db, row, data)


@router.delete("/component-classes/{class_id}", status_code=204)
def delete_component_class(class_id: int, db: Session = Depends(get_db)) -> None:
    row = dcim_svc.get_component_class(db, class_id)
    if row is None:
        raise HTTPException(status_code=404, detail="komponentklasse ikke funnet")
    dcim_svc.delete_component_class(db, row)


@router.get("/component-classes/{class_id}/parents", response_model=list[ComponentClassParentRead])
def list_component_class_parents(class_id: int, db: Session = Depends(get_db)) -> list[ComponentClassParentRead]:
    return dcim_svc.list_component_class_parents(db, class_id)


@router.post("/component-classes/{class_id}/parents", response_model=ComponentClassParentRead)
def create_component_class_parent(
    class_id: int,
    data: ComponentClassParentCreate,
    db: Session = Depends(get_db),
) -> ComponentClassParentRead:
    return dcim_svc.create_component_class_parent(db, class_id, data)


@router.patch("/component-class-parents/{parent_link_id}", response_model=ComponentClassParentRead)
def patch_component_class_parent(
    parent_link_id: int,
    data: ComponentClassParentUpdate,
    db: Session = Depends(get_db),
) -> ComponentClassParentRead:
    row = dcim_svc.get_component_class_parent(db, parent_link_id)
    if row is None:
        raise HTTPException(status_code=404, detail="klasseforelder ikke funnet")
    return dcim_svc.update_component_class_parent(db, row, data)


@router.delete("/component-class-parents/{parent_link_id}", status_code=204)
def delete_component_class_parent(parent_link_id: int, db: Session = Depends(get_db)) -> None:
    row = dcim_svc.get_component_class_parent(db, parent_link_id)
    if row is None:
        raise HTTPException(status_code=404, detail="klasseforelder ikke funnet")
    dcim_svc.delete_component_class_parent(db, row)


@router.get("/component-classes/{class_id}/fields", response_model=list[ComponentClassFieldRead])
def list_component_fields(class_id: int, db: Session = Depends(get_db)) -> list[ComponentClassFieldRead]:
    return dcim_svc.list_component_fields(db, class_id)


@router.get("/component-classes/{class_id}/effective-fields", response_model=list[ComponentClassEffectiveFieldRead])
def list_component_effective_fields(
    class_id: int,
    db: Session = Depends(get_db),
) -> list[ComponentClassEffectiveFieldRead]:
    return dcim_svc.list_component_effective_fields(db, class_id)


@router.post("/component-classes/{class_id}/fields", response_model=ComponentClassFieldRead)
def create_component_field(
    class_id: int,
    data: ComponentClassFieldCreate,
    db: Session = Depends(get_db),
) -> ComponentClassFieldRead:
    return dcim_svc.create_component_field(db, class_id, data)


@router.post("/component-class-fields/{field_id}/impact", response_model=ComponentFieldImpactRead)
def component_field_impact(
    field_id: int,
    data: ComponentClassFieldUpdate,
    db: Session = Depends(get_db),
) -> ComponentFieldImpactRead:
    row = dcim_svc.get_component_field(db, field_id)
    if row is None:
        raise HTTPException(status_code=404, detail="komponentfelt ikke funnet")
    return dcim_svc.component_field_impact(db, row, data)


@router.patch("/component-class-fields/{field_id}", response_model=ComponentClassFieldRead)
def patch_component_field(
    field_id: int,
    data: ComponentClassFieldUpdate,
    force: bool = Query(False),
    db: Session = Depends(get_db),
) -> ComponentClassFieldRead:
    row = dcim_svc.get_component_field(db, field_id)
    if row is None:
        raise HTTPException(status_code=404, detail="komponentfelt ikke funnet")
    return dcim_svc.update_component_field(db, row, data, force=force)


@router.delete("/component-class-fields/{field_id}", status_code=204)
def delete_component_field(field_id: int, force: bool = Query(False), db: Session = Depends(get_db)) -> None:
    row = dcim_svc.get_component_field(db, field_id)
    if row is None:
        raise HTTPException(status_code=404, detail="komponentfelt ikke funnet")
    dcim_svc.delete_component_field(db, row, force=force)


@router.get("/components", response_model=list[ComponentRead])
def list_components(
    class_id: int | None = Query(None),
    manufacturer_id: int | None = Query(None),
    db: Session = Depends(get_db),
) -> list[ComponentRead]:
    return dcim_svc.list_components(db, class_id=class_id, manufacturer_id=manufacturer_id)


@router.post("/components", response_model=ComponentRead)
def create_component(data: ComponentCreate, db: Session = Depends(get_db)) -> ComponentRead:
    return dcim_svc.create_component(db, data)


@router.get("/components/{component_id}", response_model=ComponentRead)
def get_component(component_id: int, db: Session = Depends(get_db)) -> ComponentRead:
    row = dcim_svc.get_component(db, component_id)
    if row is None:
        raise HTTPException(status_code=404, detail="komponent ikke funnet")
    return dcim_svc.component_read(row)


@router.patch("/components/{component_id}", response_model=ComponentRead)
def patch_component(component_id: int, data: ComponentUpdate, db: Session = Depends(get_db)) -> ComponentRead:
    row = dcim_svc.get_component(db, component_id)
    if row is None:
        raise HTTPException(status_code=404, detail="komponent ikke funnet")
    return dcim_svc.update_component(db, row, data)


@router.delete("/components/{component_id}", status_code=204)
def delete_component(component_id: int, db: Session = Depends(get_db)) -> None:
    row = dcim_svc.get_component(db, component_id)
    if row is None:
        raise HTTPException(status_code=404, detail="komponent ikke funnet")
    dcim_svc.delete_component(db, row)


@router.get("/component-identities", response_model=list[ComponentIdentityRead])
def list_component_identities(
    component_id: int | None = Query(None),
    identity_type: str | None = Query(None),
    namespace: str | None = Query(None),
    q: str | None = Query(None),
    db: Session = Depends(get_db),
) -> list[ComponentIdentityRead]:
    return dcim_svc.list_component_identities(db, component_id=component_id, identity_type=identity_type, namespace=namespace, q=q)


@router.get("/components/{component_id}/identities", response_model=list[ComponentIdentityRead])
def list_component_identities_for_component(component_id: int, db: Session = Depends(get_db)) -> list[ComponentIdentityRead]:
    if dcim_svc.get_component(db, component_id) is None:
        raise HTTPException(status_code=404, detail="komponent ikke funnet")
    return dcim_svc.list_component_identities(db, component_id=component_id)


@router.post("/components/{component_id}/identities", response_model=ComponentIdentityRead)
def create_component_identity(
    component_id: int,
    data: ComponentIdentityCreate,
    db: Session = Depends(get_db),
) -> ComponentIdentityRead:
    return dcim_svc.create_component_identity(db, component_id, data)


@router.patch("/component-identities/{identity_id}", response_model=ComponentIdentityRead)
def patch_component_identity(
    identity_id: int,
    data: ComponentIdentityUpdate,
    db: Session = Depends(get_db),
) -> ComponentIdentityRead:
    row = dcim_svc.get_component_identity(db, identity_id)
    if row is None:
        raise HTTPException(status_code=404, detail="komponentidentitet ikke funnet")
    return dcim_svc.update_component_identity(db, row, data)


@router.delete("/component-identities/{identity_id}", status_code=204)
def delete_component_identity(identity_id: int, db: Session = Depends(get_db)) -> None:
    row = dcim_svc.get_component_identity(db, identity_id)
    if row is None:
        raise HTTPException(status_code=404, detail="komponentidentitet ikke funnet")
    dcim_svc.delete_component_identity(db, row)


@router.get("/components/{component_id}/children", response_model=list[ComponentChildTemplateRead])
def list_component_child_templates(
    component_id: int,
    db: Session = Depends(get_db),
) -> list[ComponentChildTemplateRead]:
    return dcim_svc.list_component_child_templates(db, component_id)


@router.post("/components/{component_id}/children", response_model=ComponentChildTemplateRead)
def create_component_child_template(
    component_id: int,
    data: ComponentChildTemplateCreate,
    db: Session = Depends(get_db),
) -> ComponentChildTemplateRead:
    return dcim_svc.create_component_child_template(db, component_id, data)


@router.patch("/component-child-templates/{template_id}", response_model=ComponentChildTemplateRead)
def patch_component_child_template(
    template_id: int,
    data: ComponentChildTemplateUpdate,
    db: Session = Depends(get_db),
) -> ComponentChildTemplateRead:
    row = dcim_svc.get_component_child_template(db, template_id)
    if row is None:
        raise HTTPException(status_code=404, detail="child-template ikke funnet")
    return dcim_svc.update_component_child_template(db, row, data)


@router.delete("/component-child-templates/{template_id}", status_code=204)
def delete_component_child_template(template_id: int, db: Session = Depends(get_db)) -> None:
    row = dcim_svc.get_component_child_template(db, template_id)
    if row is None:
        raise HTTPException(status_code=404, detail="child-template ikke funnet")
    dcim_svc.delete_component_child_template(db, row)


# --- Device models ---


@router.get("/device-models", response_model=list[DeviceModelRead])
def list_device_models(db: Session = Depends(get_db)) -> list[DeviceModelRead]:
    return dcim_svc.list_device_models(db)


@router.get("/device-models/match-snmp", response_model=list[DeviceModelRead])
def match_device_models_snmp(
    numeric_oid: str = Query(..., min_length=1, max_length=512),
    db: Session = Depends(get_db),
) -> list[DeviceModelRead]:
    """Foreslå modeller ut fra numerisk sysObjectID (prefiksmatch mot snmp_sys_object_id_prefix)."""
    return dcim_svc.list_device_models_matching_snmp_oid(db, numeric_oid)


@router.get("/device-model-identities", response_model=list[DeviceModelIdentityRead])
def list_device_model_identities(
    device_model_id: int | None = Query(None),
    identity_type: str | None = Query(None),
    namespace: str | None = Query(None),
    q: str | None = Query(None),
    db: Session = Depends(get_db),
) -> list[DeviceModelIdentityRead]:
    return dcim_svc.list_device_model_identities(
        db,
        device_model_id=device_model_id,
        identity_type=identity_type,
        namespace=namespace,
        q=q,
    )


@router.get("/device-models/{mid}/identities", response_model=list[DeviceModelIdentityRead])
def list_device_model_identities_for_model(mid: int, db: Session = Depends(get_db)) -> list[DeviceModelIdentityRead]:
    if dcim_svc.get_device_model(db, mid) is None:
        raise HTTPException(status_code=404, detail="device_model ikke funnet")
    return dcim_svc.list_device_model_identities(db, device_model_id=mid)


@router.post("/device-models/{mid}/identities", response_model=DeviceModelIdentityRead)
def create_device_model_identity(
    mid: int,
    data: DeviceModelIdentityCreate,
    db: Session = Depends(get_db),
) -> DeviceModelIdentityRead:
    return dcim_svc.create_device_model_identity(db, mid, data)


@router.patch("/device-model-identities/{identity_id}", response_model=DeviceModelIdentityRead)
def patch_device_model_identity(
    identity_id: int,
    data: DeviceModelIdentityUpdate,
    db: Session = Depends(get_db),
) -> DeviceModelIdentityRead:
    row = dcim_svc.get_device_model_identity(db, identity_id)
    if row is None:
        raise HTTPException(status_code=404, detail="device-model-identitet ikke funnet")
    return dcim_svc.update_device_model_identity(db, row, data)


@router.delete("/device-model-identities/{identity_id}", status_code=204)
def delete_device_model_identity(identity_id: int, db: Session = Depends(get_db)) -> None:
    row = dcim_svc.get_device_model_identity(db, identity_id)
    if row is None:
        raise HTTPException(status_code=404, detail="device-model-identitet ikke funnet")
    dcim_svc.delete_device_model_identity(db, row)


@router.post("/device-models", response_model=DeviceModelRead)
def create_device_model(data: DeviceModelCreate, db: Session = Depends(get_db)) -> DeviceModelRead:
    return dcim_svc.create_device_model(db, data)


@router.get("/device-models/{mid}/image-front")
def get_device_model_image_front(mid: int, db: Session = Depends(get_db)) -> FileResponse:
    row = dcim_svc.get_device_model(db, mid)
    if row is None or not row.image_front_relpath or not row.image_front_mime_type:
        raise HTTPException(status_code=404, detail="front-bilde finnes ikke")
    path = resolve_device_model_image_path(get_settings().upload_root_path, row.image_front_relpath)
    if path is None:
        raise HTTPException(status_code=404, detail="front-bilde finnes ikke")
    return FileResponse(path, media_type=row.image_front_mime_type)


@router.get("/device-models/{mid}/image-back")
def get_device_model_image_back(mid: int, db: Session = Depends(get_db)) -> FileResponse:
    row = dcim_svc.get_device_model(db, mid)
    if row is None or not row.image_back_relpath or not row.image_back_mime_type:
        raise HTTPException(status_code=404, detail="back-bilde finnes ikke")
    path = resolve_device_model_image_path(get_settings().upload_root_path, row.image_back_relpath)
    if path is None:
        raise HTTPException(status_code=404, detail="back-bilde finnes ikke")
    return FileResponse(path, media_type=row.image_back_mime_type)


@router.get("/device-models/{mid}/image-product")
def get_device_model_image_product(mid: int, db: Session = Depends(get_db)) -> FileResponse:
    row = dcim_svc.get_device_model(db, mid)
    if row is None or not row.image_product_relpath or not row.image_product_mime_type:
        raise HTTPException(status_code=404, detail="produkt-bilde finnes ikke")
    path = resolve_device_model_image_path(get_settings().upload_root_path, row.image_product_relpath)
    if path is None:
        raise HTTPException(status_code=404, detail="produkt-bilde finnes ikke")
    return FileResponse(path, media_type=row.image_product_mime_type)


@router.post("/device-models/{mid}/image-front", response_model=DeviceModelRead)
async def upload_device_model_image_front(
    mid: int,
    db: Session = Depends(get_db),
    file: UploadFile = File(...),
) -> DeviceModelRead:
    row = dcim_svc.get_device_model(db, mid)
    if row is None:
        raise HTTPException(status_code=404, detail="device_model ikke funnet")
    content = await file.read()
    mime = file.content_type or "application/octet-stream"
    dcim_svc.set_device_model_image(db, row, "front", content, mime)
    return dcim_svc.device_model_read(row)


@router.post("/device-models/{mid}/image-back", response_model=DeviceModelRead)
async def upload_device_model_image_back(
    mid: int,
    db: Session = Depends(get_db),
    file: UploadFile = File(...),
) -> DeviceModelRead:
    row = dcim_svc.get_device_model(db, mid)
    if row is None:
        raise HTTPException(status_code=404, detail="device_model ikke funnet")
    content = await file.read()
    mime = file.content_type or "application/octet-stream"
    dcim_svc.set_device_model_image(db, row, "back", content, mime)
    return dcim_svc.device_model_read(row)


@router.post("/device-models/{mid}/image-product", response_model=DeviceModelRead)
async def upload_device_model_image_product(
    mid: int,
    db: Session = Depends(get_db),
    file: UploadFile = File(...),
) -> DeviceModelRead:
    row = dcim_svc.get_device_model(db, mid)
    if row is None:
        raise HTTPException(status_code=404, detail="device_model ikke funnet")
    content = await file.read()
    mime = file.content_type or "application/octet-stream"
    dcim_svc.set_device_model_image(db, row, "product", content, mime)
    return dcim_svc.device_model_read(row)


@router.delete("/device-models/{mid}/image-front", response_model=DeviceModelRead)
def remove_device_model_image_front(mid: int, db: Session = Depends(get_db)) -> DeviceModelRead:
    row = dcim_svc.get_device_model(db, mid)
    if row is None:
        raise HTTPException(status_code=404, detail="device_model ikke funnet")
    dcim_svc.clear_device_model_image(db, row, "front")
    return dcim_svc.device_model_read(row)


@router.delete("/device-models/{mid}/image-back", response_model=DeviceModelRead)
def remove_device_model_image_back(mid: int, db: Session = Depends(get_db)) -> DeviceModelRead:
    row = dcim_svc.get_device_model(db, mid)
    if row is None:
        raise HTTPException(status_code=404, detail="device_model ikke funnet")
    dcim_svc.clear_device_model_image(db, row, "back")
    return dcim_svc.device_model_read(row)


@router.delete("/device-models/{mid}/image-product", response_model=DeviceModelRead)
def remove_device_model_image_product(mid: int, db: Session = Depends(get_db)) -> DeviceModelRead:
    row = dcim_svc.get_device_model(db, mid)
    if row is None:
        raise HTTPException(status_code=404, detail="device_model ikke funnet")
    dcim_svc.clear_device_model_image(db, row, "product")
    return dcim_svc.device_model_read(row)


@router.get("/device-models/{mid}/components", response_model=list[DeviceModelComponentRead])
def list_device_model_components(mid: int, db: Session = Depends(get_db)) -> list[DeviceModelComponentRead]:
    return dcim_svc.list_device_model_components(db, mid)


@router.get("/device-models/{mid}/templates", response_model=list[DeviceModelTemplateRead])
def list_device_model_templates(mid: int, db: Session = Depends(get_db)) -> list[DeviceModelTemplateRead]:
    row = dcim_svc.get_device_model(db, mid)
    if row is None:
        raise HTTPException(status_code=404, detail="device_model ikke funnet")
    return netbox_dtl_svc.list_device_model_templates(db, mid)


@router.post("/device-models/{mid}/templates/renormalize", response_model=list[DeviceModelTemplateRead])
def renormalize_device_model_templates(mid: int, db: Session = Depends(get_db)) -> list[DeviceModelTemplateRead]:
    row = dcim_svc.get_device_model(db, mid)
    if row is None:
        raise HTTPException(status_code=404, detail="device_model ikke funnet")
    return netbox_dtl_svc.renormalize_device_model_templates(db, mid)


@router.get("/device-models/{mid}/template-quality", response_model=DeviceModelTemplateQualityRead)
def get_device_model_template_quality(mid: int, db: Session = Depends(get_db)) -> DeviceModelTemplateQualityRead:
    row = dcim_svc.get_device_model(db, mid)
    if row is None:
        raise HTTPException(status_code=404, detail="device_model ikke funnet")
    return DeviceModelTemplateQualityRead.model_validate(netbox_dtl_svc.device_model_template_quality(db, mid))


@router.post("/device-models/{mid}/components", response_model=DeviceModelComponentRead)
def create_device_model_component(
    mid: int,
    data: DeviceModelComponentCreate,
    db: Session = Depends(get_db),
) -> DeviceModelComponentRead:
    return dcim_svc.create_device_model_component(db, mid, data)


@router.patch("/device-models/{mid}/components/{link_id}", response_model=DeviceModelComponentRead)
def patch_device_model_component(
    mid: int,
    link_id: int,
    data: DeviceModelComponentUpdate,
    db: Session = Depends(get_db),
) -> DeviceModelComponentRead:
    row = dcim_svc.get_device_model_component(db, link_id)
    if row is None or row.device_model_id != mid:
        raise HTTPException(status_code=404, detail="modellkomponent ikke funnet")
    return dcim_svc.update_device_model_component(db, row, data)


@router.delete("/device-models/{mid}/components/{link_id}", status_code=204)
def delete_device_model_component(mid: int, link_id: int, db: Session = Depends(get_db)) -> None:
    row = dcim_svc.get_device_model_component(db, link_id)
    if row is None or row.device_model_id != mid:
        raise HTTPException(status_code=404, detail="modellkomponent ikke funnet")
    dcim_svc.delete_device_model_component(db, row)


@router.get("/device-models/{mid}", response_model=DeviceModelRead)
def get_device_model(mid: int, db: Session = Depends(get_db)) -> DeviceModelRead:
    row = dcim_svc.get_device_model(db, mid)
    if row is None:
        raise HTTPException(status_code=404, detail="device_model ikke funnet")
    return dcim_svc.device_model_read(row)


@router.patch("/device-models/{mid}", response_model=DeviceModelRead)
def update_device_model(
    mid: int,
    data: DeviceModelUpdate,
    db: Session = Depends(get_db),
) -> DeviceModelRead:
    row = dcim_svc.get_device_model(db, mid)
    if row is None:
        raise HTTPException(status_code=404, detail="device_model ikke funnet")
    return dcim_svc.update_device_model(db, row, data)


@router.delete("/device-models/{mid}", status_code=204)
def delete_device_model(mid: int, db: Session = Depends(get_db)) -> None:
    row = dcim_svc.get_device_model(db, mid)
    if row is None:
        raise HTTPException(status_code=404, detail="device_model ikke funnet")
    dcim_svc.delete_device_model(db, row)


# --- Device instances ---


@router.get("/devices", response_model=list[DeviceInstanceRead])
def list_devices(db: Session = Depends(get_db)) -> list[DeviceInstanceRead]:
    return dcim_svc.list_devices(db)


@router.post("/devices", response_model=DeviceInstanceRead)
def create_device(data: DeviceInstanceCreate, db: Session = Depends(get_db)) -> DeviceInstanceRead:
    return dcim_svc.create_device(db, data)


@router.get("/devices/{did}/components", response_model=list[DeviceInstanceComponentRead])
def list_device_instance_components(did: int, db: Session = Depends(get_db)) -> list[DeviceInstanceComponentRead]:
    return dcim_svc.list_device_instance_components(db, did)


@router.post("/devices/{did}/components", response_model=DeviceInstanceComponentRead)
def create_device_instance_component(
    did: int,
    data: DeviceInstanceComponentCreate,
    db: Session = Depends(get_db),
) -> DeviceInstanceComponentRead:
    return dcim_svc.create_device_instance_component(db, did, data)


@router.post("/devices/{did}/components/copy-from-model", response_model=list[DeviceInstanceComponentRead])
def copy_device_components_from_model(did: int, db: Session = Depends(get_db)) -> list[DeviceInstanceComponentRead]:
    return dcim_svc.copy_model_components_to_device(db, did)


@router.post("/devices/{did}/components/materialize-interfaces", response_model=list[DeviceInterfaceRead])
def materialize_component_interfaces(
    did: int,
    data: ComponentMaterializeInterfacesRequest,
    db: Session = Depends(get_db),
) -> list[DeviceInterfaceRead]:
    return dcim_svc.materialize_component_interfaces(db, did, data)


@router.patch("/devices/{did}/components/{link_id}", response_model=DeviceInstanceComponentRead)
def patch_device_instance_component(
    did: int,
    link_id: int,
    data: DeviceInstanceComponentUpdate,
    db: Session = Depends(get_db),
) -> DeviceInstanceComponentRead:
    row = dcim_svc.get_device_instance_component(db, link_id)
    if row is None or row.device_id != did:
        raise HTTPException(status_code=404, detail="device-komponent ikke funnet")
    return dcim_svc.update_device_instance_component(db, row, data)


@router.delete("/devices/{did}/components/{link_id}", status_code=204)
def delete_device_instance_component(did: int, link_id: int, db: Session = Depends(get_db)) -> None:
    row = dcim_svc.get_device_instance_component(db, link_id)
    if row is None or row.device_id != did:
        raise HTTPException(status_code=404, detail="device-komponent ikke funnet")
    dcim_svc.delete_device_instance_component(db, row)


@router.get("/devices/{did}/interfaces", response_model=list[DeviceInterfaceRead])
def list_device_interfaces(did: int, db: Session = Depends(get_db)) -> list[DeviceInterfaceRead]:
    return dcim_svc.list_device_interfaces(db, did)


@router.post("/devices/{did}/interfaces", response_model=DeviceInterfaceRead)
def create_device_interface(
    did: int,
    data: DeviceInterfaceCreate,
    db: Session = Depends(get_db),
) -> DeviceInterfaceRead:
    return dcim_svc.create_device_interface(db, did, data)


@router.post(
    "/devices/{did}/interfaces/{iid}/ip-assignments",
    response_model=IpAssignmentRead,
)
def create_iface_ip_assignment(
    did: int,
    iid: int,
    data: IpAssignmentCreate,
    db: Session = Depends(get_db),
) -> IpAssignmentRead:
    return dcim_svc.create_iface_ip_assignment(db, did, iid, data)


@router.patch(
    "/devices/{did}/interfaces/{iid}/ip-assignments/{aid}",
    response_model=IpAssignmentRead,
)
def patch_iface_ip_assignment(
    did: int,
    iid: int,
    aid: int,
    data: IpAssignmentUpdate,
    db: Session = Depends(get_db),
) -> IpAssignmentRead:
    row = dcim_svc.get_iface_ip_assignment(db, did, iid, aid)
    if row is None:
        raise HTTPException(status_code=404, detail="IP-tildeling ikke funnet")
    return dcim_svc.update_iface_ip_assignment(db, did, iid, row, data)


@router.delete("/devices/{did}/interfaces/{iid}/ip-assignments/{aid}", status_code=204)
def delete_iface_ip_assignment(did: int, iid: int, aid: int, db: Session = Depends(get_db)) -> None:
    row = dcim_svc.get_iface_ip_assignment(db, did, iid, aid)
    if row is None:
        raise HTTPException(status_code=404, detail="IP-tildeling ikke funnet")
    dcim_svc.delete_iface_ip_assignment(db, row)


@router.get("/devices/{did}/interfaces/{iid}", response_model=DeviceInterfaceRead)
def get_device_interface(did: int, iid: int, db: Session = Depends(get_db)) -> DeviceInterfaceRead:
    row = dcim_svc.get_device_interface(db, did, iid)
    if row is None:
        raise HTTPException(status_code=404, detail="grensesnitt ikke funnet")
    return dcim_svc.device_interface_read(row)


@router.patch("/devices/{did}/interfaces/{iid}", response_model=DeviceInterfaceRead)
def patch_device_interface(
    did: int,
    iid: int,
    data: DeviceInterfaceUpdate,
    db: Session = Depends(get_db),
) -> DeviceInterfaceRead:
    row = dcim_svc.get_device_interface(db, did, iid)
    if row is None:
        raise HTTPException(status_code=404, detail="grensesnitt ikke funnet")
    return dcim_svc.update_device_interface(db, did, row, data)


@router.delete("/devices/{did}/interfaces/{iid}", status_code=204)
def delete_device_interface(did: int, iid: int, db: Session = Depends(get_db)) -> None:
    row = dcim_svc.get_device_interface(db, did, iid)
    if row is None:
        raise HTTPException(status_code=404, detail="grensesnitt ikke funnet")
    dcim_svc.delete_device_interface(db, row)


@router.get("/devices/{did}", response_model=DeviceInstanceRead)
def get_device(did: int, db: Session = Depends(get_db)) -> DeviceInstanceRead:
    row = dcim_svc.get_device(db, did)
    if row is None:
        raise HTTPException(status_code=404, detail="device ikke funnet")
    return dcim_svc.device_instance_read(db, row)


@router.get("/devices/{did}/device-ip-assignments", response_model=list[DeviceIpAssignmentRead])
def list_device_ip_assignments(did: int, db: Session = Depends(get_db)) -> list[DeviceIpAssignmentRead]:
    return dcim_svc.list_device_ip_assignments(db, did)


@router.post("/devices/{did}/device-ip-assignments", response_model=DeviceIpAssignmentRead)
def create_device_ip_assignment(
    did: int,
    data: DeviceIpAssignmentCreate,
    db: Session = Depends(get_db),
) -> DeviceIpAssignmentRead:
    return dcim_svc.create_device_ip_assignment(db, did, data)


@router.patch(
    "/devices/{did}/device-ip-assignments/{aid}",
    response_model=DeviceIpAssignmentRead,
)
def patch_device_ip_assignment(
    did: int,
    aid: int,
    data: DeviceIpAssignmentUpdate,
    db: Session = Depends(get_db),
) -> DeviceIpAssignmentRead:
    row = dcim_svc.get_device_ip_assignment(db, did, aid)
    if row is None:
        raise HTTPException(status_code=404, detail="IP-tildeling ikke funnet")
    return dcim_svc.update_device_ip_assignment(db, did, row, data)


@router.delete("/devices/{did}/device-ip-assignments/{aid}", status_code=204)
def delete_device_ip_assignment(did: int, aid: int, db: Session = Depends(get_db)) -> None:
    row = dcim_svc.get_device_ip_assignment(db, did, aid)
    if row is None:
        raise HTTPException(status_code=404, detail="IP-tildeling ikke funnet")
    dcim_svc.delete_device_ip_assignment(db, row)


@router.patch("/devices/{did}", response_model=DeviceInstanceRead)
def update_device(did: int, data: DeviceInstanceUpdate, db: Session = Depends(get_db)) -> DeviceInstanceRead:
    row = dcim_svc.get_device(db, did)
    if row is None:
        raise HTTPException(status_code=404, detail="device ikke funnet")
    return dcim_svc.update_device(db, row, data)


@router.delete("/devices/{did}", status_code=204)
def delete_device(did: int, db: Session = Depends(get_db)) -> None:
    row = dcim_svc.get_device(db, did)
    if row is None:
        raise HTTPException(status_code=404, detail="device ikke funnet")
    dcim_svc.delete_device(db, row)


# --- Placements ---


@router.get("/placements", response_model=list[RackPlacementRead])
def list_placements(
    db: Session = Depends(get_db),
    rack_id: int | None = Query(None),
) -> list[RackPlacementRead]:
    return dcim_svc.list_placements(db, rack_id=rack_id)


@router.post("/placements", response_model=RackPlacementRead)
def create_placement(
    data: RackPlacementCreate,
    db: Session = Depends(get_db),
) -> RackPlacementRead:
    return dcim_svc.create_placement(db, data)


@router.patch("/placements/{pid}", response_model=RackPlacementRead)
def update_placement(
    pid: int,
    data: RackPlacementUpdate,
    db: Session = Depends(get_db),
) -> RackPlacementRead:
    row = dcim_svc.get_placement(db, pid)
    if row is None:
        raise HTTPException(status_code=404, detail="plassering ikke funnet")
    return dcim_svc.update_placement(db, row, data)


@router.delete("/placements/{pid}", status_code=204)
def delete_placement(pid: int, db: Session = Depends(get_db)) -> None:
    row = dcim_svc.get_placement(db, pid)
    if row is None:
        raise HTTPException(status_code=404, detail="plassering ikke funnet")
    dcim_svc.delete_placement(db, row)


@router.get("/power-sources", response_model=list[PowerSourceRead])
def list_power_sources(
    site_id: int | None = Query(None),
    db: Session = Depends(get_db),
) -> list[PowerSourceRead]:
    return [power_svc.source_to_read(r) for r in power_svc.list_sources(db, site_id=site_id)]


@router.post("/power-sources", response_model=PowerSourceRead)
def create_power_source(data: PowerSourceCreate, db: Session = Depends(get_db)) -> PowerSourceRead:
    return power_svc.source_to_read(power_svc.create_source(db, data))


@router.get("/power-sources/{source_id}", response_model=PowerSourceRead)
def get_power_source(source_id: int, db: Session = Depends(get_db)) -> PowerSourceRead:
    row = power_svc.get_source(db, source_id)
    if row is None:
        raise HTTPException(status_code=404, detail="strømkilde ikke funnet")
    return power_svc.source_to_read(row)


@router.delete("/power-sources/{source_id}", status_code=204)
def delete_power_source(source_id: int, db: Session = Depends(get_db)) -> None:
    row = power_svc.get_source(db, source_id)
    if row is None:
        raise HTTPException(status_code=404, detail="strømkilde ikke funnet")
    power_svc.delete_source(db, row)


@router.get("/power-panels", response_model=list[PowerPanelRead])
def list_power_panels(
    site_id: int | None = Query(None),
    room_id: int | None = Query(None),
    db: Session = Depends(get_db),
) -> list[PowerPanelRead]:
    return [power_svc.panel_to_read(r) for r in power_svc.list_panels(db, site_id=site_id, room_id=room_id)]


@router.post("/power-panels", response_model=PowerPanelRead)
def create_power_panel(data: PowerPanelCreate, db: Session = Depends(get_db)) -> PowerPanelRead:
    return power_svc.panel_to_read(power_svc.create_panel(db, data))


@router.delete("/power-panels/{panel_id}", status_code=204)
def delete_power_panel(panel_id: int, db: Session = Depends(get_db)) -> None:
    row = power_svc.get_panel(db, panel_id)
    if row is None:
        raise HTTPException(status_code=404, detail="tavle ikke funnet")
    power_svc.delete_panel(db, row)


@router.get("/power-circuits", response_model=list[PowerCircuitRead])
def list_power_circuits(
    panel_id: int | None = Query(None),
    site_id: int | None = Query(None),
    db: Session = Depends(get_db),
) -> list[PowerCircuitRead]:
    return [power_svc.circuit_to_read(r) for r in power_svc.list_circuits(db, panel_id=panel_id, site_id=site_id)]


@router.post("/power-circuits", response_model=PowerCircuitRead)
def create_power_circuit(data: PowerCircuitCreate, db: Session = Depends(get_db)) -> PowerCircuitRead:
    return power_svc.circuit_to_read(power_svc.create_circuit(db, data))


@router.delete("/power-circuits/{circuit_id}", status_code=204)
def delete_power_circuit(circuit_id: int, db: Session = Depends(get_db)) -> None:
    row = power_svc.get_circuit(db, circuit_id)
    if row is None:
        raise HTTPException(status_code=404, detail="kurs ikke funnet")
    power_svc.delete_circuit(db, row)


@router.get("/power-feeds", response_model=list[PowerFeedRead])
def list_power_feeds(
    site_id: int | None = Query(None),
    circuit_id: int | None = Query(None),
    rack_id: int | None = Query(None),
    room_id: int | None = Query(None),
    db: Session = Depends(get_db),
) -> list[PowerFeedRead]:
    return [
        power_svc.feed_to_read(db, r)
        for r in power_svc.list_feeds(db, site_id=site_id, circuit_id=circuit_id, rack_id=rack_id, room_id=room_id)
    ]


@router.post("/power-feeds", response_model=PowerFeedRead)
def create_power_feed(data: PowerFeedCreate, db: Session = Depends(get_db)) -> PowerFeedRead:
    return power_svc.feed_to_read(db, power_svc.create_feed(db, data))


@router.delete("/power-feeds/{feed_id}", status_code=204)
def delete_power_feed(feed_id: int, db: Session = Depends(get_db)) -> None:
    row = power_svc.get_feed(db, feed_id)
    if row is None:
        raise HTTPException(status_code=404, detail="feed ikke funnet")
    power_svc.delete_feed(db, row)


@router.get("/devices/{did}/ports", response_model=list[DevicePortRead])
def list_device_ports(did: int, db: Session = Depends(get_db)) -> list[DevicePortRead]:
    if dcim_svc.get_device(db, did) is None:
        raise HTTPException(status_code=404, detail="enhet ikke funnet")
    return [power_svc.port_to_read(r) for r in power_svc.list_ports(db, device_id=did)]


@router.post("/devices/{did}/ports", response_model=DevicePortRead)
def create_device_port(did: int, data: DevicePortCreate, db: Session = Depends(get_db)) -> DevicePortRead:
    return power_svc.port_to_read(power_svc.create_port(db, did, data))


@router.post("/devices/{did}/ports/from-templates", response_model=list[DevicePortRead])
def copy_device_ports_from_templates(did: int, db: Session = Depends(get_db)) -> list[DevicePortRead]:
    return [power_svc.port_to_read(r) for r in power_svc.copy_ports_from_templates(db, did)]


@router.patch("/device-ports/{port_id}", response_model=DevicePortRead)
def patch_device_port(port_id: int, data: DevicePortUpdate, db: Session = Depends(get_db)) -> DevicePortRead:
    row = power_svc.get_port(db, port_id)
    if row is None:
        raise HTTPException(status_code=404, detail="port ikke funnet")
    return power_svc.port_to_read(power_svc.update_port(db, row, data))


@router.delete("/device-ports/{port_id}", status_code=204)
def delete_device_port(port_id: int, db: Session = Depends(get_db)) -> None:
    row = power_svc.get_port(db, port_id)
    if row is None:
        raise HTTPException(status_code=404, detail="port ikke funnet")
    power_svc.delete_port(db, row)


@router.get("/device-ports/{port_id}/path", response_model=CablePathRead)
def device_port_path(port_id: int, db: Session = Depends(get_db)) -> CablePathRead:
    if power_svc.get_port(db, port_id) is None:
        raise HTTPException(status_code=404, detail="port ikke funnet")
    return power_svc.trace_path(db, "device-port", port_id)


@router.get("/cables", response_model=list[CableRead])
def list_cables(
    site_id: int | None = Query(None),
    device_id: int | None = Query(None),
    db: Session = Depends(get_db),
) -> list[CableRead]:
    return [power_svc.cable_to_read(db, r) for r in power_svc.list_cables(db, site_id=site_id, device_id=device_id)]


@router.post("/cables", response_model=CableRead)
def create_cable(data: CableCreate, db: Session = Depends(get_db)) -> CableRead:
    return power_svc.cable_to_read(db, power_svc.create_cable(db, data))


@router.get("/cables/{cable_id}", response_model=CableRead)
def get_cable(cable_id: int, db: Session = Depends(get_db)) -> CableRead:
    row = power_svc.get_cable(db, cable_id)
    if row is None:
        raise HTTPException(status_code=404, detail="kabel ikke funnet")
    return power_svc.cable_to_read(db, row)


@router.get("/cables/{cable_id}/path", response_model=CablePathRead)
def cable_path(cable_id: int, db: Session = Depends(get_db)) -> CablePathRead:
    row = power_svc.get_cable(db, cable_id)
    if row is None:
        raise HTTPException(status_code=404, detail="kabel ikke funnet")
    read = power_svc.cable_to_read(db, row)
    start = next((t for t in read.terminations if t.end == "a"), None)
    if start is None:
        return CablePathRead(hops=[])
    return power_svc.trace_path(db, start.object_type, start.object_id)


@router.delete("/cables/{cable_id}", status_code=204)
def delete_cable(cable_id: int, db: Session = Depends(get_db)) -> None:
    row = power_svc.get_cable(db, cable_id)
    if row is None:
        raise HTTPException(status_code=404, detail="kabel ikke funnet")
    power_svc.delete_cable(db, row)


@router.get("/cables/{cable_id}/strands", response_model=list[FiberStrandRead])
def list_fiber_strands(cable_id: int, db: Session = Depends(get_db)) -> list[FiberStrandRead]:
    row = power_svc.get_cable(db, cable_id)
    if row is None:
        raise HTTPException(status_code=404, detail="kabel ikke funnet")
    return [power_svc.fiber_strand_to_read(s) for s in power_svc.list_fiber_strands(db, cable_id)]


@router.post("/cables/{cable_id}/strands", response_model=FiberStrandRead)
def create_fiber_strand(
    cable_id: int,
    data: FiberStrandCreate,
    db: Session = Depends(get_db),
) -> FiberStrandRead:
    row = power_svc.get_cable(db, cable_id)
    if row is None:
        raise HTTPException(status_code=404, detail="kabel ikke funnet")
    return power_svc.fiber_strand_to_read(power_svc.create_fiber_strand(db, row, data))


@router.get("/fiber-strands/{strand_id}", response_model=FiberStrandRead)
def get_fiber_strand(strand_id: int, db: Session = Depends(get_db)) -> FiberStrandRead:
    row = power_svc.get_fiber_strand(db, strand_id)
    if row is None:
        raise HTTPException(status_code=404, detail="fiber ikke funnet")
    return power_svc.fiber_strand_to_read(row)


@router.patch("/fiber-strands/{strand_id}", response_model=FiberStrandRead)
def patch_fiber_strand(
    strand_id: int,
    data: FiberStrandUpdate,
    db: Session = Depends(get_db),
) -> FiberStrandRead:
    row = power_svc.get_fiber_strand(db, strand_id)
    if row is None:
        raise HTTPException(status_code=404, detail="fiber ikke funnet")
    return power_svc.fiber_strand_to_read(power_svc.update_fiber_strand(db, row, data))


@router.delete("/fiber-strands/{strand_id}", status_code=204)
def delete_fiber_strand(strand_id: int, db: Session = Depends(get_db)) -> None:
    row = power_svc.get_fiber_strand(db, strand_id)
    if row is None:
        raise HTTPException(status_code=404, detail="fiber ikke funnet")
    power_svc.delete_fiber_strand(db, row)


@router.get("/cables/{cable_id}/bundles", response_model=list[FiberBundleRead])
def list_fiber_bundles(cable_id: int, db: Session = Depends(get_db)) -> list[FiberBundleRead]:
    row = power_svc.get_cable(db, cable_id)
    if row is None:
        raise HTTPException(status_code=404, detail="kabel ikke funnet")
    return [power_svc.fiber_bundle_to_read(db, b) for b in power_svc.list_fiber_bundles(db, cable_id)]


@router.post("/cables/{cable_id}/bundles", response_model=FiberBundleRead)
def create_fiber_bundle(
    cable_id: int,
    data: FiberBundleCreate,
    db: Session = Depends(get_db),
) -> FiberBundleRead:
    row = power_svc.get_cable(db, cable_id)
    if row is None:
        raise HTTPException(status_code=404, detail="kabel ikke funnet")
    return power_svc.fiber_bundle_to_read(db, power_svc.create_fiber_bundle(db, row, data))


@router.get("/fiber-bundles/{bundle_id}", response_model=FiberBundleRead)
def get_fiber_bundle(bundle_id: int, db: Session = Depends(get_db)) -> FiberBundleRead:
    row = power_svc.get_fiber_bundle(db, bundle_id)
    if row is None:
        raise HTTPException(status_code=404, detail="fiberbunt ikke funnet")
    return power_svc.fiber_bundle_to_read(db, row)


@router.post("/fiber-bundles/{bundle_id}/members", response_model=FiberBundleRead)
def add_fiber_bundle_member(
    bundle_id: int,
    data: FiberBundleMemberCreate,
    db: Session = Depends(get_db),
) -> FiberBundleRead:
    row = power_svc.get_fiber_bundle(db, bundle_id)
    if row is None:
        raise HTTPException(status_code=404, detail="fiberbunt ikke funnet")
    power_svc.add_fiber_bundle_member(db, row, data)
    return power_svc.fiber_bundle_to_read(db, row)


@router.delete("/fiber-bundles/{bundle_id}", status_code=204)
def delete_fiber_bundle(bundle_id: int, db: Session = Depends(get_db)) -> None:
    row = power_svc.get_fiber_bundle(db, bundle_id)
    if row is None:
        raise HTTPException(status_code=404, detail="fiberbunt ikke funnet")
    power_svc.delete_fiber_bundle(db, row)


@router.delete("/fiber-bundle-members/{member_id}", status_code=204)
def delete_fiber_bundle_member(member_id: int, db: Session = Depends(get_db)) -> None:
    row = power_svc.get_fiber_bundle_member(db, member_id)
    if row is None:
        raise HTTPException(status_code=404, detail="fiberbunt-medlem ikke funnet")
    power_svc.delete_fiber_bundle_member(db, row)
