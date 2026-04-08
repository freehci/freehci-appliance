"""DCIM REST API (fase 2 – kjerne)."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.dcim import (
    DeviceInstanceCreate,
    DeviceInstanceRead,
    DeviceInstanceUpdate,
    DeviceModelCreate,
    DeviceModelRead,
    DeviceModelUpdate,
    ManufacturerCreate,
    ManufacturerRead,
    RackCreate,
    RackPlacementCreate,
    RackPlacementRead,
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


@router.delete("/manufacturers/{mid}", status_code=204)
def delete_manufacturer(mid: int, db: Session = Depends(get_db)) -> None:
    row = dcim_svc.get_manufacturer(db, mid)
    if row is None:
        raise HTTPException(status_code=404, detail="manufacturer ikke funnet")
    dcim_svc.delete_manufacturer(db, row)


# --- Device models ---


@router.get("/device-models", response_model=list[DeviceModelRead])
def list_device_models(db: Session = Depends(get_db)) -> list[DeviceModelRead]:
    return dcim_svc.list_device_models(db)


@router.post("/device-models", response_model=DeviceModelRead)
def create_device_model(data: DeviceModelCreate, db: Session = Depends(get_db)) -> DeviceModelRead:
    return dcim_svc.create_device_model(db, data)


@router.get("/device-models/{mid}", response_model=DeviceModelRead)
def get_device_model(mid: int, db: Session = Depends(get_db)) -> DeviceModelRead:
    row = dcim_svc.get_device_model(db, mid)
    if row is None:
        raise HTTPException(status_code=404, detail="device_model ikke funnet")
    return row


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


@router.get("/devices/{did}", response_model=DeviceInstanceRead)
def get_device(did: int, db: Session = Depends(get_db)) -> DeviceInstanceRead:
    row = dcim_svc.get_device(db, did)
    if row is None:
        raise HTTPException(status_code=404, detail="device ikke funnet")
    return row


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


@router.delete("/placements/{pid}", status_code=204)
def delete_placement(pid: int, db: Session = Depends(get_db)) -> None:
    row = dcim_svc.get_placement(db, pid)
    if row is None:
        raise HTTPException(status_code=404, detail="plassering ikke funnet")
    dcim_svc.delete_placement(db, row)
