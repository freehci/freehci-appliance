"""DCIM forretningslogikk."""

from __future__ import annotations

import ipaddress
from collections import defaultdict

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from pathlib import Path

from fastapi import HTTPException

from app.core.config import get_settings
from app.core.media_storage import (
    delete_device_model_all_images,
    delete_device_model_image_slot,
    delete_manufacturer_logo_files,
    write_device_model_image_file,
    write_manufacturer_logo_file,
)
from app.models.dcim import (
    DeviceInstance,
    DeviceInterface,
    DeviceIpAssignment,
    DeviceModel,
    DeviceType,
    InterfaceIpAssignment,
    Manufacturer,
    Rack,
    RackPlacement,
    Room,
    Site,
)
from app.models.ipam import IpamIpv4Prefix

from app.schemas.dcim import (
    DeviceInstanceCreate,
    DeviceInstanceRead,
    DeviceInstanceUpdate,
    DeviceInterfaceCreate,
    DeviceInterfaceRead,
    DeviceInterfaceUpdate,
    IpAssignmentCreate,
    IpAssignmentRead,
    IpAssignmentUpdate,
    DeviceIpAssignmentCreate,
    DeviceIpAssignmentRead,
    DeviceIpAssignmentUpdate,
    DeviceModelCreate,
    DeviceModelUpdate,
    DeviceModelBrief,
    DeviceModelRead,
    DeviceTypeCreate,
    DeviceTypeUpdate,
    ManufacturerCreate,
    ManufacturerDetailRead,
    ManufacturerRead,
    ManufacturerUpdate,
    RackCreate,
    RackPlacementCreate,
    RackPlacementUpdate,
    RackUpdate,
    RoomCreate,
    RoomUpdate,
    SiteCreate,
    SiteUpdate,
)

_SITE_QUERY = object()


def device_effective_site_id(db: Session, device_id: int) -> int | None:
    q = (
        select(Room.site_id)
        .join(Rack, Rack.room_id == Room.id)
        .join(RackPlacement, RackPlacement.rack_id == Rack.id)
        .where(RackPlacement.device_id == device_id)
        .limit(1)
    )
    return db.execute(q).scalar_one_or_none()


def _device_site_ids_batch(db: Session, device_ids: list[int]) -> dict[int, int]:
    if not device_ids:
        return {}
    q = (
        select(RackPlacement.device_id, Room.site_id)
        .join(Rack, Rack.id == RackPlacement.rack_id)
        .join(Room, Room.id == Rack.room_id)
        .where(RackPlacement.device_id.in_(device_ids))
    )
    return {did: sid for did, sid in db.execute(q).all()}


def _validate_ipv4_prefix_for_assignment(
    db: Session,
    *,
    device_id: int,
    prefix_id: int | None,
    family: str,
    address: str,
) -> int | None:
    if prefix_id is None:
        return None
    if family != "ipv4":
        raise HTTPException(
            status_code=400,
            detail="IPv4-prefiks kan bare knyttes til IPv4-adresser",
        )
    pfx = db.get(IpamIpv4Prefix, prefix_id)
    if pfx is None:
        raise HTTPException(status_code=404, detail="IPAM-prefiks ikke funnet")
    site_id = device_effective_site_id(db, device_id)
    if site_id is None:
        raise HTTPException(
            status_code=400,
            detail="enhet uten rack-plassering kan ikke knyttes til site-prefiks — plasser enheten i rack først",
        )
    if pfx.site_id != site_id:
        raise HTTPException(
            status_code=400,
            detail="prefiks tilhører en annen site enn enhetens rack-plassering",
        )
    try:
        net = ipaddress.ip_network(pfx.cidr, strict=False)
        ip_a = ipaddress.ip_address(address)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"ugyldig adresse eller prefiks: {e}") from e
    if ip_a not in net:
        raise HTTPException(status_code=400, detail="IP-adressen ligger ikke innenfor valgt prefiks")
    return prefix_id


def _device_u_height(db: Session, device: DeviceInstance) -> int:
    if device.device_model_id is None:
        return 1
    m = db.get(DeviceModel, device.device_model_id)
    if m is None:
        return 1
    return m.u_height


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
    if u_h == 0:
        if u_position != 0:
            raise HTTPException(
                status_code=400,
                detail="Modell med U-høyde 0 må plasseres med u_position=0 (utenfor RU-rutenettet)",
            )
        return

    if u_position < 1:
        raise HTTPException(
            status_code=400,
            detail="u_position må være minst 1 for rack-montert utstyr (RU 1 = nederst)",
        )

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
        if oh == 0:
            continue
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
        height_mm=data.height_mm,
        width_mm=data.width_mm,
        depth_mm=data.depth_mm,
        brand=data.brand.strip() if data.brand else None,
        purchase_date=data.purchase_date,
        commissioned_date=data.commissioned_date,
        notes=data.notes.strip() if data.notes else None,
        attributes=data.attributes,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def get_rack(db: Session, rack_id: int) -> Rack | None:
    return db.get(Rack, rack_id)


def update_rack(db: Session, rack: Rack, data: RackUpdate) -> Rack:
    payload = data.model_dump(exclude_unset=True)

    if "name" in payload and payload["name"] is not None:
        rack.name = str(payload["name"]).strip()
    if "u_height" in payload and payload["u_height"] is not None:
        new_u = int(payload["u_height"])
        if new_u < rack.u_height:
            # strammere rack: sjekk at ingen plassering stikker utenfor
            placements = db.execute(
                select(RackPlacement).where(RackPlacement.rack_id == rack.id),
            ).scalars().all()
            for p in placements:
                dev = db.get(DeviceInstance, p.device_id)
                if dev is None:
                    continue
                duh = _device_u_height(db, dev)
                if duh == 0:
                    continue
                _, top = _occupies_bottom_top(p.u_position, duh)
                if top > new_u:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Kan ikke redusere u_height: enhet id={dev.id} går til RU {top}",
                    )
        rack.u_height = new_u
    if "sort_order" in payload:
        so = payload["sort_order"]
        rack.sort_order = int(so) if so is not None else 0

    for dim in ("height_mm", "width_mm", "depth_mm"):
        if dim in payload:
            setattr(rack, dim, payload[dim])

    if "brand" in payload:
        b = payload["brand"]
        rack.brand = b.strip() if isinstance(b, str) and b.strip() else None

    if "purchase_date" in payload:
        rack.purchase_date = payload["purchase_date"]
    if "commissioned_date" in payload:
        rack.commissioned_date = payload["commissioned_date"]

    if "notes" in payload:
        n = payload["notes"]
        rack.notes = n.strip() if isinstance(n, str) and n.strip() else None

    if "attributes" in payload:
        rack.attributes = payload["attributes"]

    db.commit()
    db.refresh(rack)
    return rack


def delete_rack(db: Session, rack: Rack) -> None:
    db.delete(rack)
    db.commit()


# --- Manufacturers ---

LOGO_MAX_BYTES = 512 * 1024
DM_IMAGE_MAX_BYTES = 2 * 1024 * 1024
ALLOWED_LOGO_MIME = frozenset({"image/png", "image/jpeg", "image/webp", "image/svg+xml"})


def manufacturer_read(m: Manufacturer) -> ManufacturerRead:
    return ManufacturerRead(
        id=m.id,
        name=m.name,
        description=m.description,
        website_url=m.website_url,
        has_logo=m.logo_relpath is not None,
        iana_enterprise_number=m.iana_enterprise_number,
    )


def list_manufacturers(db: Session) -> list[ManufacturerRead]:
    rows = list(db.execute(select(Manufacturer).order_by(Manufacturer.name)).scalars().all())
    return [manufacturer_read(r) for r in rows]


def create_manufacturer(db: Session, data: ManufacturerCreate) -> ManufacturerRead:
    desc = data.description.strip() if data.description else None
    web = data.website_url.strip() if data.website_url else None
    row = Manufacturer(
        name=data.name.strip(),
        description=desc or None,
        website_url=web or None,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return manufacturer_read(row)


def update_manufacturer(db: Session, m: Manufacturer, data: ManufacturerUpdate) -> ManufacturerRead:
    patch = data.model_dump(exclude_unset=True)
    if not patch:
        raise HTTPException(status_code=400, detail="ingen felter å oppdatere")
    if "name" in patch:
        nm = patch["name"]
        if not nm or not str(nm).strip():
            raise HTTPException(status_code=400, detail="navn kan ikke være tomt")
        m.name = str(nm).strip()
    if "description" in patch:
        v = patch["description"]
        m.description = None if v is None else (str(v).strip() or None)
    if "website_url" in patch:
        v = patch["website_url"]
        m.website_url = None if v is None else (str(v).strip() or None)
    if "iana_enterprise_number" in patch:
        pen = patch["iana_enterprise_number"]
        if pen is not None:
            db.execute(
                update(Manufacturer)
                .where(
                    Manufacturer.iana_enterprise_number == pen,
                    Manufacturer.id != m.id,
                )
                .values(iana_enterprise_number=None),
            )
        m.iana_enterprise_number = pen
    db.commit()
    db.refresh(m)
    return manufacturer_read(m)


def get_manufacturer(db: Session, mid: int) -> Manufacturer | None:
    return db.get(Manufacturer, mid)


def get_manufacturer_detail(db: Session, mid: int) -> ManufacturerDetailRead | None:
    m = get_manufacturer(db, mid)
    if m is None:
        return None
    q = select(DeviceModel).where(DeviceModel.manufacturer_id == mid).order_by(DeviceModel.name)
    models = list(db.execute(q).scalars().all())
    return ManufacturerDetailRead(
        id=m.id,
        name=m.name,
        description=m.description,
        website_url=m.website_url,
        has_logo=m.logo_relpath is not None,
        iana_enterprise_number=m.iana_enterprise_number,
        device_models=[DeviceModelBrief.model_validate(x) for x in models],
    )


def set_manufacturer_logo(db: Session, m: Manufacturer, content: bytes, mime: str) -> None:
    if len(content) > LOGO_MAX_BYTES:
        raise HTTPException(status_code=413, detail="logo for stor (maks 512 KiB)")
    if mime not in ALLOWED_LOGO_MIME:
        raise HTTPException(
            status_code=400,
            detail="logo må være PNG, JPEG, WebP eller SVG",
        )
    root: Path = get_settings().upload_root_path
    relpath = write_manufacturer_logo_file(root, m.id, content, mime)
    m.logo_relpath = relpath
    m.logo_mime_type = mime
    db.commit()
    db.refresh(m)


def clear_manufacturer_logo(db: Session, m: Manufacturer) -> None:
    root: Path = get_settings().upload_root_path
    delete_manufacturer_logo_files(root, m.id)
    m.logo_relpath = None
    m.logo_mime_type = None
    db.commit()
    db.refresh(m)


def delete_manufacturer(db: Session, m: Manufacturer) -> None:
    root: Path = get_settings().upload_root_path
    delete_manufacturer_logo_files(root, m.id)
    db.delete(m)
    db.commit()


# --- Device types ---


def list_device_types(db: Session) -> list[DeviceType]:
    return list(db.execute(select(DeviceType).order_by(DeviceType.name)).scalars().all())


def get_device_type(db: Session, tid: int) -> DeviceType | None:
    return db.get(DeviceType, tid)


def create_device_type(db: Session, data: DeviceTypeCreate) -> DeviceType:
    row = DeviceType(name=data.name.strip(), slug=data.slug, description=data.description)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def update_device_type(db: Session, row: DeviceType, data: DeviceTypeUpdate) -> DeviceType:
    patch = data.model_dump(exclude_unset=True)
    if not patch:
        raise HTTPException(status_code=400, detail="ingen felter å oppdatere")
    if "name" in patch:
        nm = patch["name"]
        if not nm or not str(nm).strip():
            raise HTTPException(status_code=400, detail="navn kan ikke være tomt")
        row.name = str(nm).strip()
    if "description" in patch:
        v = patch["description"]
        row.description = None if v is None else (str(v).strip() or None)
    db.commit()
    db.refresh(row)
    return row


def delete_device_type(db: Session, row: DeviceType) -> None:
    db.delete(row)
    db.commit()


# --- Device models ---


def device_model_read(dm: DeviceModel) -> DeviceModelRead:
    return DeviceModelRead(
        id=dm.id,
        manufacturer_id=dm.manufacturer_id,
        device_type_id=dm.device_type_id,
        name=dm.name,
        u_height=dm.u_height,
        form_factor=dm.form_factor,
        image_front_url=dm.image_front_url,
        image_back_url=dm.image_back_url,
        image_product_url=dm.image_product_url,
        has_image_front_file=dm.image_front_relpath is not None,
        has_image_back_file=dm.image_back_relpath is not None,
        has_image_product_file=dm.image_product_relpath is not None,
        snmp_sys_object_id_prefix=dm.snmp_sys_object_id_prefix,
    )


def list_device_models(db: Session) -> list[DeviceModelRead]:
    rows = list(db.execute(select(DeviceModel).order_by(DeviceModel.name)).scalars().all())
    return [device_model_read(r) for r in rows]


def create_device_model(db: Session, data: DeviceModelCreate) -> DeviceModelRead:
    if data.manufacturer_id is not None and get_manufacturer(db, data.manufacturer_id) is None:
        raise HTTPException(status_code=404, detail="manufacturer ikke funnet")
    if data.device_type_id is not None and get_device_type(db, data.device_type_id) is None:
        raise HTTPException(status_code=404, detail="device_type ikke funnet")
    snmp_pfx = data.snmp_sys_object_id_prefix
    snmp_pfx = None if snmp_pfx is None else str(snmp_pfx).strip() or None
    row = DeviceModel(
        manufacturer_id=data.manufacturer_id,
        device_type_id=data.device_type_id,
        name=data.name.strip(),
        u_height=data.u_height,
        form_factor=data.form_factor,
        image_front_url=data.image_front_url,
        image_back_url=data.image_back_url,
        image_product_url=data.image_product_url,
        snmp_sys_object_id_prefix=snmp_pfx,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return device_model_read(row)


def get_device_model(db: Session, mid: int) -> DeviceModel | None:
    return db.get(DeviceModel, mid)


def set_device_model_image(db: Session, row: DeviceModel, slot: str, content: bytes, mime: str) -> None:
    if slot not in ("front", "back", "product"):
        raise HTTPException(status_code=400, detail="slot må være front, back eller product")
    if len(content) > DM_IMAGE_MAX_BYTES:
        raise HTTPException(status_code=413, detail="bilde for stort (maks 2 MiB)")
    if mime not in ALLOWED_LOGO_MIME:
        raise HTTPException(
            status_code=400,
            detail="bilde må være PNG, JPEG, WebP eller SVG",
        )
    root: Path = get_settings().upload_root_path
    relpath = write_device_model_image_file(root, row.id, slot, content, mime)
    if slot == "front":
        row.image_front_relpath = relpath
        row.image_front_mime_type = mime
    elif slot == "back":
        row.image_back_relpath = relpath
        row.image_back_mime_type = mime
    else:
        row.image_product_relpath = relpath
        row.image_product_mime_type = mime
    db.commit()
    db.refresh(row)


def clear_device_model_image(db: Session, row: DeviceModel, slot: str) -> None:
    if slot not in ("front", "back", "product"):
        raise HTTPException(status_code=400, detail="slot må være front, back eller product")
    root: Path = get_settings().upload_root_path
    delete_device_model_image_slot(root, row.id, slot)
    if slot == "front":
        row.image_front_relpath = None
        row.image_front_mime_type = None
    elif slot == "back":
        row.image_back_relpath = None
        row.image_back_mime_type = None
    else:
        row.image_product_relpath = None
        row.image_product_mime_type = None
    db.commit()
    db.refresh(row)


def update_device_model(db: Session, row: DeviceModel, data: DeviceModelUpdate) -> DeviceModelRead:
    patch = data.model_dump(exclude_unset=True)
    if not patch:
        raise HTTPException(status_code=400, detail="ingen felter å oppdatere")
    if "manufacturer_id" in patch:
        mid = patch["manufacturer_id"]
        if mid is not None and get_manufacturer(db, mid) is None:
            raise HTTPException(status_code=404, detail="manufacturer ikke funnet")
        row.manufacturer_id = mid
    if "device_type_id" in patch:
        tid = patch["device_type_id"]
        if tid is not None and get_device_type(db, tid) is None:
            raise HTTPException(status_code=404, detail="device_type ikke funnet")
        row.device_type_id = tid
    if "name" in patch:
        nm = patch["name"]
        if not nm or not str(nm).strip():
            raise HTTPException(status_code=400, detail="navn kan ikke være tomt")
        row.name = str(nm).strip()
    if "u_height" in patch:
        row.u_height = patch["u_height"]
    if "form_factor" in patch:
        v = patch["form_factor"]
        row.form_factor = None if v is None else (str(v).strip() or None)
    if "image_front_url" in patch:
        v = patch["image_front_url"]
        row.image_front_url = None if v is None else (str(v).strip() or None)
    if "image_back_url" in patch:
        v = patch["image_back_url"]
        row.image_back_url = None if v is None else (str(v).strip() or None)
    if "image_product_url" in patch:
        v = patch["image_product_url"]
        row.image_product_url = None if v is None else (str(v).strip() or None)
    if "snmp_sys_object_id_prefix" in patch:
        v = patch["snmp_sys_object_id_prefix"]
        row.snmp_sys_object_id_prefix = None if v is None else (str(v).strip() or None)
    db.commit()
    db.refresh(row)
    return device_model_read(row)


def list_device_models_matching_snmp_oid(db: Session, numeric_oid: str) -> list[DeviceModelRead]:
    """Returnerer modeller der snmp_sys_object_id_prefix er prefiks av den numeriske OID-en (lengst prefiks først)."""
    needle = numeric_oid.strip()
    if not needle:
        return []
    rows = list(db.execute(select(DeviceModel).order_by(DeviceModel.name)).scalars().all())
    hits: list[tuple[int, DeviceModel]] = []
    for dm in rows:
        pfx = dm.snmp_sys_object_id_prefix
        if not pfx:
            continue
        p = str(pfx).strip()
        if not p:
            continue
        if needle.startswith(p) or needle == p:
            hits.append((len(p), dm))
    hits.sort(key=lambda x: (-x[0], x[1].name))
    return [device_model_read(dm) for _, dm in hits]


def delete_device_model(db: Session, row: DeviceModel) -> None:
    root: Path = get_settings().upload_root_path
    delete_device_model_all_images(root, row.id)
    db.delete(row)
    db.commit()


# --- Device instances ---


def _effective_device_type_id(db: Session, dev: DeviceInstance) -> int | None:
    if dev.device_type_id is not None:
        return dev.device_type_id
    if dev.device_model_id is None:
        return None
    m = db.get(DeviceModel, dev.device_model_id)
    return None if m is None else m.device_type_id


def device_instance_read(
    db: Session,
    dev: DeviceInstance,
    *,
    effective_site_id: int | None | object = _SITE_QUERY,
) -> DeviceInstanceRead:
    raw = dev.attributes
    attrs: dict = dict(raw) if isinstance(raw, dict) else {}
    if effective_site_id is _SITE_QUERY:
        es: int | None = device_effective_site_id(db, dev.id)
    else:
        es = effective_site_id  # type: ignore[assignment]
    return DeviceInstanceRead(
        id=dev.id,
        device_model_id=dev.device_model_id,
        device_type_id=dev.device_type_id,
        effective_device_type_id=_effective_device_type_id(db, dev),
        effective_site_id=es,
        name=dev.name,
        serial_number=dev.serial_number,
        asset_tag=dev.asset_tag,
        attributes=attrs,
    )


def list_devices(db: Session) -> list[DeviceInstanceRead]:
    rows = list(db.execute(select(DeviceInstance).order_by(DeviceInstance.name)).scalars().all())
    site_by_dev = _device_site_ids_batch(db, [r.id for r in rows])
    return [device_instance_read(db, r, effective_site_id=site_by_dev.get(r.id)) for r in rows]


def create_device(db: Session, data: DeviceInstanceCreate) -> DeviceInstanceRead:
    if data.device_model_id is not None and get_device_model(db, data.device_model_id) is None:
        raise HTTPException(status_code=404, detail="device_model ikke funnet")
    if data.device_type_id is not None and get_device_type(db, data.device_type_id) is None:
        raise HTTPException(status_code=404, detail="device_type ikke funnet")
    attrs = data.attributes
    row = DeviceInstance(
        device_model_id=data.device_model_id,
        device_type_id=data.device_type_id,
        name=data.name.strip(),
        serial_number=data.serial_number,
        asset_tag=data.asset_tag,
        attributes=dict(attrs) if attrs is not None else None,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return device_instance_read(db, row)


def get_device(db: Session, did: int) -> DeviceInstance | None:
    return db.get(DeviceInstance, did)


def update_device(db: Session, row: DeviceInstance, data: DeviceInstanceUpdate) -> DeviceInstanceRead:
    patch = data.model_dump(exclude_unset=True)
    if not patch:
        raise HTTPException(status_code=400, detail="ingen felter å oppdatere")
    if "device_model_id" in patch:
        mid = patch["device_model_id"]
        if mid is not None and get_device_model(db, mid) is None:
            raise HTTPException(status_code=404, detail="device_model ikke funnet")
        row.device_model_id = mid
    if "device_type_id" in patch:
        tid = patch["device_type_id"]
        if tid is not None and get_device_type(db, tid) is None:
            raise HTTPException(status_code=404, detail="device_type ikke funnet")
        row.device_type_id = tid
    if "name" in patch and patch["name"] is not None:
        row.name = str(patch["name"]).strip()
    if "serial_number" in patch:
        row.serial_number = patch["serial_number"]
    if "asset_tag" in patch:
        row.asset_tag = patch["asset_tag"]
    if "attributes" in patch:
        a = patch["attributes"]
        row.attributes = None if a is None else dict(a)
    db.commit()
    db.refresh(row)
    return device_instance_read(db, row)


def delete_device(db: Session, row: DeviceInstance) -> None:
    db.delete(row)
    db.commit()


def _require_device(db: Session, did: int) -> DeviceInstance:
    dev = get_device(db, did)
    if dev is None:
        raise HTTPException(status_code=404, detail="device ikke funnet")
    return dev


def _iface_commit(db: Session) -> None:
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="grensesnitt med samme navn finnes allerede på denne enheten",
        ) from None


def _iface_tree_sort_rows(rows: list[DeviceInterface]) -> list[DeviceInterface]:
    """Rot først, deretter barn sortert på sort_order, name (rekursivt)."""
    by_parent: dict[int | None, list[DeviceInterface]] = defaultdict(list)
    row_ids = {r.id for r in rows}
    for r in rows:
        pid = r.parent_interface_id
        if pid is not None and pid not in row_ids:
            pid = None
        by_parent[pid].append(r)
    for lst in by_parent.values():
        lst.sort(key=lambda x: (x.sort_order, x.name))
    out: list[DeviceInterface] = []

    def walk(parent_id: int | None) -> None:
        for r in by_parent.get(parent_id, []):
            out.append(r)
            walk(r.id)

    walk(None)
    if len(out) != len(rows):
        seen = {r.id for r in out}
        rest = [r for r in rows if r.id not in seen]
        rest.sort(key=lambda x: (x.sort_order, x.name))
        out.extend(rest)
    return out


def _validate_iface_parent(
    db: Session,
    device_id: int,
    parent_interface_id: int | None,
    *,
    exclude_interface_id: int | None,
) -> None:
    if parent_interface_id is None:
        return
    if exclude_interface_id is not None and parent_interface_id == exclude_interface_id:
        raise HTTPException(status_code=400, detail="grensesnitt kan ikke være sin egen forelder")
    parent = db.get(DeviceInterface, parent_interface_id)
    if parent is None or parent.device_id != device_id:
        raise HTTPException(status_code=400, detail="foreldregrensesnitt finnes ikke på denne enheten")


def _iface_parent_would_cycle(db: Session, interface_id: int, new_parent_id: int | None) -> bool:
    if new_parent_id is None:
        return False
    cur: int | None = new_parent_id
    seen: set[int] = set()
    while cur is not None:
        if cur == interface_id:
            return True
        if cur in seen:
            return True
        seen.add(cur)
        row = db.get(DeviceInterface, cur)
        if row is None:
            break
        cur = row.parent_interface_id
    return False


def _iface_descendant_ids_post_order(db: Session, root_id: int) -> list[int]:
    q = (
        select(DeviceInterface.id)
        .where(DeviceInterface.parent_interface_id == root_id)
        .order_by(DeviceInterface.sort_order, DeviceInterface.name)
    )
    child_ids = list(db.execute(q).scalars().all())
    out: list[int] = []
    for cid in child_ids:
        out.extend(_iface_descendant_ids_post_order(db, cid))
        out.append(cid)
    return out


def _normalize_ip(addr: str) -> tuple[str, str]:
    try:
        p = ipaddress.ip_address(addr.strip())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"ugyldig IP-adresse: {e}") from e
    if isinstance(p, ipaddress.IPv4Address):
        return "ipv4", str(p)
    return "ipv6", p.compressed


def device_interface_read(row: DeviceInterface) -> DeviceInterfaceRead:
    ips = sorted(
        row.ip_assignments,
        key=lambda x: (0 if x.is_primary else 1, x.family, x.address),
    )
    return DeviceInterfaceRead(
        id=row.id,
        device_id=row.device_id,
        parent_interface_id=row.parent_interface_id,
        name=row.name,
        description=row.description,
        mac_address=row.mac_address,
        speed_mbps=row.speed_mbps,
        mtu=row.mtu,
        vlan_id=row.vlan_id,
        enabled=row.enabled,
        sort_order=row.sort_order,
        ip_assignments=[IpAssignmentRead.model_validate(x) for x in ips],
    )


def list_device_interfaces(db: Session, device_id: int) -> list[DeviceInterfaceRead]:
    _require_device(db, device_id)
    q = (
        select(DeviceInterface)
        .where(DeviceInterface.device_id == device_id)
        .options(selectinload(DeviceInterface.ip_assignments))
        .order_by(DeviceInterface.sort_order, DeviceInterface.name)
    )
    rows = list(db.execute(q).scalars().all())
    rows = _iface_tree_sort_rows(rows)
    return [device_interface_read(r) for r in rows]


def get_device_interface(db: Session, device_id: int, interface_id: int) -> DeviceInterface | None:
    row = db.get(DeviceInterface, interface_id)
    if row is None or row.device_id != device_id:
        return None
    return row


def create_device_interface(db: Session, device_id: int, data: DeviceInterfaceCreate) -> DeviceInterfaceRead:
    _require_device(db, device_id)
    _validate_iface_parent(db, device_id, data.parent_interface_id, exclude_interface_id=None)
    mac = data.mac_address
    mac = None if mac is None or str(mac).strip() == "" else str(mac).strip()
    row = DeviceInterface(
        device_id=device_id,
        parent_interface_id=data.parent_interface_id,
        name=data.name.strip(),
        description=data.description,
        mac_address=mac,
        speed_mbps=data.speed_mbps,
        mtu=data.mtu,
        vlan_id=data.vlan_id,
        enabled=data.enabled,
        sort_order=data.sort_order,
    )
    db.add(row)
    _iface_commit(db)
    db.refresh(row)
    return device_interface_read(row)


def update_device_interface(
    db: Session,
    device_id: int,
    row: DeviceInterface,
    data: DeviceInterfaceUpdate,
) -> DeviceInterfaceRead:
    patch = data.model_dump(exclude_unset=True)
    if not patch:
        raise HTTPException(status_code=400, detail="ingen felter å oppdatere")
    if "name" in patch:
        nm = patch["name"]
        if not nm or not str(nm).strip():
            raise HTTPException(status_code=400, detail="navn kan ikke være tomt")
        row.name = str(nm).strip()
    if "description" in patch:
        v = patch["description"]
        row.description = None if v is None else (str(v).strip() or None)
    if "mac_address" in patch:
        v = patch["mac_address"]
        row.mac_address = None if v is None or str(v).strip() == "" else str(v).strip()
    if "speed_mbps" in patch:
        row.speed_mbps = patch["speed_mbps"]
    if "mtu" in patch:
        row.mtu = patch["mtu"]
    if "vlan_id" in patch:
        row.vlan_id = patch["vlan_id"]
    if "enabled" in patch and patch["enabled"] is not None:
        row.enabled = bool(patch["enabled"])
    if "sort_order" in patch and patch["sort_order"] is not None:
        row.sort_order = int(patch["sort_order"])
    if "parent_interface_id" in patch:
        new_pid = patch["parent_interface_id"]
        if new_pid is None:
            row.parent_interface_id = None
        else:
            _validate_iface_parent(db, device_id, int(new_pid), exclude_interface_id=row.id)
            if _iface_parent_would_cycle(db, row.id, int(new_pid)):
                raise HTTPException(status_code=400, detail="ugyldig forelder (sirkel)")
            row.parent_interface_id = int(new_pid)
    _iface_commit(db)
    db.refresh(row)
    return device_interface_read(row)


def delete_device_interface(db: Session, row: DeviceInterface) -> None:
    for cid in _iface_descendant_ids_post_order(db, row.id):
        child = db.get(DeviceInterface, cid)
        if child is not None:
            db.delete(child)
    db.delete(row)
    db.commit()


def _clear_primary_same_family(db: Session, interface_id: int, family: str) -> None:
    q = select(InterfaceIpAssignment).where(
        InterfaceIpAssignment.interface_id == interface_id,
        InterfaceIpAssignment.family == family,
        InterfaceIpAssignment.is_primary.is_(True),
    )
    for r in db.execute(q).scalars().all():
        r.is_primary = False


def create_iface_ip_assignment(
    db: Session,
    device_id: int,
    interface_id: int,
    data: IpAssignmentCreate,
) -> IpAssignmentRead:
    if get_device_interface(db, device_id, interface_id) is None:
        raise HTTPException(status_code=404, detail="grensesnitt ikke funnet")
    family, addr = _normalize_ip(data.address)
    dup = db.execute(
        select(InterfaceIpAssignment).where(
            InterfaceIpAssignment.interface_id == interface_id,
            InterfaceIpAssignment.address == addr,
        )
    ).scalar_one_or_none()
    if dup is not None:
        raise HTTPException(status_code=409, detail="IP-adressen finnes allerede på dette grensesnittet")
    pfx_id = _validate_ipv4_prefix_for_assignment(
        db,
        device_id=device_id,
        prefix_id=data.ipv4_prefix_id,
        family=family,
        address=addr,
    )
    if data.is_primary:
        _clear_primary_same_family(db, interface_id, family)
    row = InterfaceIpAssignment(
        interface_id=interface_id,
        ipv4_prefix_id=pfx_id,
        family=family,
        address=addr,
        is_primary=data.is_primary,
    )
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="IP-adressen finnes allerede på dette grensesnittet",
        ) from None
    db.refresh(row)
    return IpAssignmentRead.model_validate(row)


def get_iface_ip_assignment(
    db: Session,
    device_id: int,
    interface_id: int,
    assignment_id: int,
) -> InterfaceIpAssignment | None:
    if get_device_interface(db, device_id, interface_id) is None:
        return None
    row = db.get(InterfaceIpAssignment, assignment_id)
    if row is None or row.interface_id != interface_id:
        return None
    return row


def update_iface_ip_assignment(
    db: Session,
    device_id: int,
    interface_id: int,
    row: InterfaceIpAssignment,
    data: IpAssignmentUpdate,
) -> IpAssignmentRead:
    patch = data.model_dump(exclude_unset=True)
    if not patch:
        raise HTTPException(status_code=400, detail="ingen felter å oppdatere")
    if "ipv4_prefix_id" in patch:
        v = patch["ipv4_prefix_id"]
        if v is None:
            row.ipv4_prefix_id = None
        else:
            row.ipv4_prefix_id = _validate_ipv4_prefix_for_assignment(
                db,
                device_id=device_id,
                prefix_id=int(v),
                family=row.family,
                address=row.address,
            )
    if patch.get("is_primary") is True:
        _clear_primary_same_family(db, interface_id, row.family)
        row.is_primary = True
    elif patch.get("is_primary") is False:
        row.is_primary = False
    db.commit()
    db.refresh(row)
    return IpAssignmentRead.model_validate(row)


def delete_iface_ip_assignment(db: Session, row: InterfaceIpAssignment) -> None:
    db.delete(row)
    db.commit()


def _clear_primary_same_family_device(db: Session, device_id: int, family: str) -> None:
    q = select(DeviceIpAssignment).where(
        DeviceIpAssignment.device_id == device_id,
        DeviceIpAssignment.family == family,
        DeviceIpAssignment.is_primary.is_(True),
    )
    for r in db.execute(q).scalars().all():
        r.is_primary = False


def list_device_ip_assignments(db: Session, device_id: int) -> list[DeviceIpAssignmentRead]:
    _require_device(db, device_id)
    q = (
        select(DeviceIpAssignment)
        .where(DeviceIpAssignment.device_id == device_id)
        .order_by(DeviceIpAssignment.family, DeviceIpAssignment.address)
    )
    rows = list(db.execute(q).scalars().all())
    return [DeviceIpAssignmentRead.model_validate(x) for x in rows]


def create_device_ip_assignment(
    db: Session,
    device_id: int,
    data: DeviceIpAssignmentCreate,
) -> DeviceIpAssignmentRead:
    _require_device(db, device_id)
    family, addr = _normalize_ip(data.address)
    dup = db.execute(
        select(DeviceIpAssignment).where(
            DeviceIpAssignment.device_id == device_id,
            DeviceIpAssignment.address == addr,
        )
    ).scalar_one_or_none()
    if dup is not None:
        raise HTTPException(status_code=409, detail="IP-adressen finnes allerede på denne enheten")
    pfx_id = _validate_ipv4_prefix_for_assignment(
        db,
        device_id=device_id,
        prefix_id=data.ipv4_prefix_id,
        family=family,
        address=addr,
    )
    if data.is_primary:
        _clear_primary_same_family_device(db, device_id, family)
    row = DeviceIpAssignment(
        device_id=device_id,
        ipv4_prefix_id=pfx_id,
        family=family,
        address=addr,
        is_primary=data.is_primary,
    )
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="IP-adressen finnes allerede på denne enheten",
        ) from None
    db.refresh(row)
    return DeviceIpAssignmentRead.model_validate(row)


def get_device_ip_assignment(db: Session, device_id: int, assignment_id: int) -> DeviceIpAssignment | None:
    row = db.get(DeviceIpAssignment, assignment_id)
    if row is None or row.device_id != device_id:
        return None
    return row


def update_device_ip_assignment(
    db: Session,
    device_id: int,
    row: DeviceIpAssignment,
    data: DeviceIpAssignmentUpdate,
) -> DeviceIpAssignmentRead:
    patch = data.model_dump(exclude_unset=True)
    if not patch:
        raise HTTPException(status_code=400, detail="ingen felter å oppdatere")
    if "ipv4_prefix_id" in patch:
        v = patch["ipv4_prefix_id"]
        if v is None:
            row.ipv4_prefix_id = None
        else:
            row.ipv4_prefix_id = _validate_ipv4_prefix_for_assignment(
                db,
                device_id=device_id,
                prefix_id=int(v),
                family=row.family,
                address=row.address,
            )
    if patch.get("is_primary") is True:
        _clear_primary_same_family_device(db, device_id, row.family)
        row.is_primary = True
    elif patch.get("is_primary") is False:
        row.is_primary = False
    db.commit()
    db.refresh(row)
    return DeviceIpAssignmentRead.model_validate(row)


def delete_device_ip_assignment(db: Session, row: DeviceIpAssignment) -> None:
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


def update_placement(db: Session, row: RackPlacement, data: RackPlacementUpdate) -> RackPlacement:
    from fastapi import HTTPException

    if data.rack_id is None and data.u_position is None and data.mounting is None:
        raise HTTPException(status_code=400, detail="ingen felter å oppdatere")

    target_rack_id = data.rack_id if data.rack_id is not None else row.rack_id
    rack = get_rack(db, target_rack_id)
    if rack is None:
        raise HTTPException(status_code=404, detail="rack ikke funnet")

    device = get_device(db, row.device_id)
    if device is None:
        raise HTTPException(status_code=404, detail="device ikke funnet")

    new_u = data.u_position if data.u_position is not None else row.u_position
    new_mounting = data.mounting if data.mounting is not None else row.mounting

    assert_placement_fits_rack(
        db,
        rack=rack,
        u_position=new_u,
        device=device,
        exclude_placement_id=row.id,
    )

    row.rack_id = target_rack_id
    row.u_position = new_u
    row.mounting = new_mounting
    db.commit()
    db.refresh(row)
    return row


def get_placement(db: Session, pid: int) -> RackPlacement | None:
    return db.get(RackPlacement, pid)


def delete_placement(db: Session, row: RackPlacement) -> None:
    db.delete(row)
    db.commit()
