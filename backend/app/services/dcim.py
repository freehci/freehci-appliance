"""DCIM forretningslogikk."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.dcim import (
    DeviceInstance,
    DeviceModel,
    Manufacturer,
    Rack,
    RackPlacement,
    Room,
    Site,
)
from app.schemas.dcim import (
    DeviceInstanceCreate,
    DeviceInstanceUpdate,
    DeviceModelCreate,
    DeviceModelUpdate,
    ManufacturerCreate,
    RackCreate,
    RackPlacementCreate,
    RackUpdate,
    RoomCreate,
    RoomUpdate,
    SiteCreate,
    SiteUpdate,
)


def _device_u_height(db: Session, device: DeviceInstance) -> int:
    if device.device_model_id is None:
        return 1
    m = db.get(DeviceModel, device.device_model_id)
    return 1 if m is None else m.u_height


def _occupies_bottom_top(u_bottom: int, u_h: int) -> tuple[int, int]:
    return u_bottom, u_bottom + u_h - 1


def _ranges_overlap(a1: int, a2: int, b1: int, b2: int) -> bool:
    return not (a2 < b1 or b2 < a1)


def assert_placement_fits_rack(
    db: Session,
    *,
    rack: Rack,
    u_position: int,
    device: DeviceInstance,
    exclude_placement_id: int | None = None,
) -> None:
    from fastapi import HTTPException

    u_h = _device_u_height(db, device)
    bottom, top = _occupies_bottom_top(u_position, u_h)
    if bottom < 1 or top > rack.u_height:
        raise HTTPException(
            status_code=400,
            detail=f"Enheten krever RU {u_position}–{top}, men racket har u_height={rack.u_height}",
        )

    q = select(RackPlacement).where(RackPlacement.rack_id == rack.id)
    if exclude_placement_id is not None:
        q = q.where(RackPlacement.id != exclude_placement_id)
    existing = db.execute(q).scalars().all()
    for p in existing:
        other = db.get(DeviceInstance, p.device_id)
        if other is None:
            continue
        oh = _device_u_height(db, other)
        ob, ot = _occupies_bottom_top(p.u_position, oh)
        if _ranges_overlap(bottom, top, ob, ot):
            raise HTTPException(
                status_code=400,
                detail=f"RU-kollisjon med enhet id={p.device_id} (RU {ob}–{ot})",
            )


# --- Sites ---

def list_sites(db: Session) -> list[Site]:
    return list(db.execute(select(Site).order_by(Site.name)).scalars().all())


def create_site(db: Session, data: SiteCreate) -> Site:
    row = Site(name=data.name.strip(), slug=data.slug, description=data.description)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def get_site(db: Session, site_id: int) -> Site | None:
    return db.get(Site, site_id)


def update_site(db: Session, site: Site, data: SiteUpdate) -> Site:
    if data.name is not None:
        site.name = data.name.strip()
    if data.description is not None:
        site.description = data.description
    db.commit()
    db.refresh(site)
    return site


def delete_site(db: Session, site: Site) -> None:
    db.delete(site)
    db.commit()


# --- Rooms ---

def list_rooms(db: Session, *, site_id: int | None = None) -> list[Room]:
    q = select(Room).order_by(Room.name)
    if site_id is not None:
        q = q.where(Room.site_id == site_id)
    return list(db.execute(q).scalars().all())


def create_room(db: Session, data: RoomCreate) -> Room:
    if get_site(db, data.site_id) is None:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="site ikke funnet")
    row = Room(site_id=data.site_id, name=data.name.strip(), description=data.description)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def get_room(db: Session, room_id: int) -> Room | None:
    return db.get(Room, room_id)


def update_room(db: Session, room: Room, data: RoomUpdate) -> Room:
    if data.name is not None:
        room.name = data.name.strip()
    if data.description is not None:
        room.description = data.description
    db.commit()
    db.refresh(room)
    return room


def delete_room(db: Session, room: Room) -> None:
    db.delete(room)
    db.commit()


# --- Racks ---

def list_racks(db: Session, *, room_id: int | None = None) -> list[Rack]:
    q = select(Rack).order_by(Rack.sort_order, Rack.name)
    if room_id is not None:
        q = q.where(Rack.room_id == room_id)
    return list(db.execute(q).scalars().all())


def create_rack(db: Session, data: RackCreate) -> Rack:
    if get_room(db, data.room_id) is None:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="room ikke funnet")
    row = Rack(
        room_id=data.room_id,
        name=data.name.strip(),
        u_height=data.u_height,
        sort_order=data.sort_order,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def get_rack(db: Session, rack_id: int) -> Rack | None:
    return db.get(Rack, rack_id)


def update_rack(db: Session, rack: Rack, data: RackUpdate) -> Rack:
    from fastapi import HTTPException

    if data.name is not None:
        rack.name = data.name.strip()
    if data.u_height is not None:
        if data.u_height < rack.u_height:
            # strammere rack: sjekk at ingen plassering stikker utenfor
            placements = db.execute(
                select(RackPlacement).where(RackPlacement.rack_id == rack.id),
            ).scalars().all()
            for p in placements:
                dev = db.get(DeviceInstance, p.device_id)
                if dev is None:
                    continue
                _, top = _occupies_bottom_top(p.u_position, _device_u_height(db, dev))
                if top > data.u_height:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Kan ikke redusere u_height: enhet id={dev.id} går til RU {top}",
                    )
        rack.u_height = data.u_height
    if data.sort_order is not None:
        rack.sort_order = data.sort_order
    db.commit()
    db.refresh(rack)
    return rack


def delete_rack(db: Session, rack: Rack) -> None:
    db.delete(rack)
    db.commit()


# --- Manufacturers ---

def list_manufacturers(db: Session) -> list[Manufacturer]:
    return list(db.execute(select(Manufacturer).order_by(Manufacturer.name)).scalars().all())


def create_manufacturer(db: Session, data: ManufacturerCreate) -> Manufacturer:
    row = Manufacturer(name=data.name.strip())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def get_manufacturer(db: Session, mid: int) -> Manufacturer | None:
    return db.get(Manufacturer, mid)


def delete_manufacturer(db: Session, m: Manufacturer) -> None:
    db.delete(m)
    db.commit()


# --- Device models ---

def list_device_models(db: Session) -> list[DeviceModel]:
    return list(db.execute(select(DeviceModel).order_by(DeviceModel.name)).scalars().all())


def create_device_model(db: Session, data: DeviceModelCreate) -> DeviceModel:
    from fastapi import HTTPException

    if data.manufacturer_id is not None and get_manufacturer(db, data.manufacturer_id) is None:
        raise HTTPException(status_code=404, detail="manufacturer ikke funnet")
    row = DeviceModel(
        manufacturer_id=data.manufacturer_id,
        name=data.name.strip(),
        u_height=data.u_height,
        form_factor=data.form_factor,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def get_device_model(db: Session, mid: int) -> DeviceModel | None:
    return db.get(DeviceModel, mid)


def update_device_model(db: Session, row: DeviceModel, data: DeviceModelUpdate) -> DeviceModel:
    from fastapi import HTTPException

    if data.manufacturer_id is not None and get_manufacturer(db, data.manufacturer_id) is None:
        raise HTTPException(status_code=404, detail="manufacturer ikke funnet")
    if data.manufacturer_id is not None:
        row.manufacturer_id = data.manufacturer_id
    if data.name is not None:
        row.name = data.name.strip()
    if data.u_height is not None:
        row.u_height = data.u_height
    if data.form_factor is not None:
        row.form_factor = data.form_factor
    db.commit()
    db.refresh(row)
    return row


def delete_device_model(db: Session, row: DeviceModel) -> None:
    db.delete(row)
    db.commit()


# --- Device instances ---

def list_devices(db: Session) -> list[DeviceInstance]:
    return list(db.execute(select(DeviceInstance).order_by(DeviceInstance.name)).scalars().all())


def create_device(db: Session, data: DeviceInstanceCreate) -> DeviceInstance:
    from fastapi import HTTPException

    if data.device_model_id is not None and get_device_model(db, data.device_model_id) is None:
        raise HTTPException(status_code=404, detail="device_model ikke funnet")
    row = DeviceInstance(
        device_model_id=data.device_model_id,
        name=data.name.strip(),
        serial_number=data.serial_number,
        asset_tag=data.asset_tag,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def get_device(db: Session, did: int) -> DeviceInstance | None:
    return db.get(DeviceInstance, did)


def update_device(db: Session, row: DeviceInstance, data: DeviceInstanceUpdate) -> DeviceInstance:
    from fastapi import HTTPException

    if data.device_model_id is not None and get_device_model(db, data.device_model_id) is None:
        raise HTTPException(status_code=404, detail="device_model ikke funnet")
    if data.device_model_id is not None:
        row.device_model_id = data.device_model_id
    if data.name is not None:
        row.name = data.name.strip()
    if data.serial_number is not None:
        row.serial_number = data.serial_number
    if data.asset_tag is not None:
        row.asset_tag = data.asset_tag
    db.commit()
    db.refresh(row)
    return row


def delete_device(db: Session, row: DeviceInstance) -> None:
    db.delete(row)
    db.commit()


# --- Placements ---

def list_placements(db: Session, *, rack_id: int | None = None) -> list[RackPlacement]:
    q = select(RackPlacement).order_by(RackPlacement.u_position)
    if rack_id is not None:
        q = q.where(RackPlacement.rack_id == rack_id)
    return list(db.execute(q).scalars().all())


def create_placement(db: Session, data: RackPlacementCreate) -> RackPlacement:
    from fastapi import HTTPException

    rack = get_rack(db, data.rack_id)
    if rack is None:
        raise HTTPException(status_code=404, detail="rack ikke funnet")
    device = get_device(db, data.device_id)
    if device is None:
        raise HTTPException(status_code=404, detail="device ikke funnet")
    existing = db.scalars(
        select(RackPlacement).where(RackPlacement.device_id == data.device_id),
    ).first()
    if existing is not None:
        raise HTTPException(status_code=400, detail="enheten har allerede en plassering; slett først")
    assert_placement_fits_rack(db, rack=rack, u_position=data.u_position, device=device)
    row = RackPlacement(
        rack_id=data.rack_id,
        device_id=data.device_id,
        u_position=data.u_position,
        mounting=data.mounting,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def get_placement(db: Session, pid: int) -> RackPlacement | None:
    return db.get(RackPlacement, pid)


def delete_placement(db: Session, row: RackPlacement) -> None:
    db.delete(row)
    db.commit()
