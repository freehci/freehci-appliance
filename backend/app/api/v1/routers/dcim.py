"""DCIM REST API (fase 2 – kjerne)."""

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.config import get_settings
from app.core.media_storage import resolve_device_model_image_path, resolve_manufacturer_logo_path
from app.schemas.dcim import (
    DeviceInstanceCreate,
    DeviceInstanceRead,
    DeviceInstanceUpdate,
    DeviceIpAssignmentCreate,
    DeviceIpAssignmentRead,
    DeviceIpAssignmentUpdate,
    DeviceInterfaceCreate,
    DeviceInterfaceRead,
    DeviceInterfaceUpdate,
    IpAssignmentCreate,
    IpAssignmentRead,
    IpAssignmentUpdate,
    DeviceModelCreate,
    DeviceModelRead,
    DeviceModelUpdate,
    DeviceTypeCreate,
    DeviceTypeRead,
    DeviceTypeUpdate,
    ManufacturerCreate,
    ManufacturerDetailRead,
    ManufacturerRead,
    ManufacturerUpdate,
    RackCreate,
    RackPlacementCreate,
    RackPlacementRead,
    RackPlacementUpdate,
    RackRead,
    RackUpdate,
    RoomCreate,
    RoomRead,
    RoomUpdate,
    SiteCreate,
    SiteRead,
    SiteUpdate,
)
from app.services import dcim as dcim_svc

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


@router.delete("/sites/{site_id}", status_code=204)
def delete_site(site_id: int, db: Session = Depends(get_db)) -> None:
    row = dcim_svc.get_site(db, site_id)
    if row is None:
        raise HTTPException(status_code=404, detail="site ikke funnet")
    dcim_svc.delete_site(db, row)


# --- Rooms ---


@router.get("/rooms", response_model=list[RoomRead])
def list_rooms(
    db: Session = Depends(get_db),
    site_id: int | None = Query(None),
) -> list[RoomRead]:
    return dcim_svc.list_rooms(db, site_id=site_id)


@router.post("/rooms", response_model=RoomRead)
def create_room(data: RoomCreate, db: Session = Depends(get_db)) -> RoomRead:
    return dcim_svc.create_room(db, data)


@router.get("/rooms/{room_id}", response_model=RoomRead)
def get_room(room_id: int, db: Session = Depends(get_db)) -> RoomRead:
    row = dcim_svc.get_room(db, room_id)
    if row is None:
        raise HTTPException(status_code=404, detail="room ikke funnet")
    return row


@router.patch("/rooms/{room_id}", response_model=RoomRead)
def update_room(room_id: int, data: RoomUpdate, db: Session = Depends(get_db)) -> RoomRead:
    row = dcim_svc.get_room(db, room_id)
    if row is None:
        raise HTTPException(status_code=404, detail="room ikke funnet")
    return dcim_svc.update_room(db, row, data)


@router.delete("/rooms/{room_id}", status_code=204)
def delete_room(room_id: int, db: Session = Depends(get_db)) -> None:
    row = dcim_svc.get_room(db, room_id)
    if row is None:
        raise HTTPException(status_code=404, detail="room ikke funnet")
    dcim_svc.delete_room(db, row)


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
