"""DCIM forretningslogikk."""

from __future__ import annotations

import ipaddress
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path

from fastapi import HTTPException
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.core.config import get_settings
from app.core.media_storage import (
    delete_device_model_all_images,
    delete_device_model_image_slot,
    delete_manufacturer_logo_files,
    delete_room_floorplan_files,
    write_device_model_image_file,
    write_manufacturer_logo_file,
    write_room_floorplan_file,
)
from app.models.dcim import (
    Component,
    ComponentChildTemplate,
    ComponentClass,
    ComponentClassField,
    ComponentClassParent,
    DeviceInstance,
    DeviceInstanceComponent,
    DeviceInterface,
    DeviceIpAssignment,
    DeviceModel,
    DeviceModelComponent,
    DeviceType,
    InterfaceIpAssignment,
    Manufacturer,
    Rack,
    RackPlacement,
    Room,
    Site,
    SiteAccessGrant,
    SiteRole,
)
from app.models.iam import User
from app.models.ipam import IpamIpv4Prefix

from app.services import tenant as tenant_svc

LOGO_MAX_BYTES = 512 * 1024
DM_IMAGE_MAX_BYTES = 2 * 1024 * 1024
ALLOWED_LOGO_MIME = frozenset({"image/png", "image/jpeg", "image/webp", "image/svg+xml"})

from app.schemas.dcim import (
    ComponentClassCreate,
    ComponentChildTemplateCreate,
    ComponentChildTemplateRead,
    ComponentChildTemplateUpdate,
    ComponentMaterializeInterfacesRequest,
    ComponentClassEffectiveFieldRead,
    ComponentClassFieldCreate,
    ComponentClassFieldRead,
    ComponentClassFieldUpdate,
    ComponentClassParentCreate,
    ComponentClassParentRead,
    ComponentClassParentUpdate,
    ComponentClassRead,
    ComponentClassUpdate,
    ComponentExternalMappingProfileRead,
    ComponentExternalMappingPreviewRead,
    ComponentExternalMappingPreviewRequest,
    ComponentStandardCatalogSeedResponse,
    ComponentCreate,
    ComponentFieldImpactRead,
    ComponentRead,
    ComponentUpdate,
    DeviceInstanceCreate,
    DeviceInstanceComponentCreate,
    DeviceInstanceComponentRead,
    DeviceInstanceComponentUpdate,
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
    DeviceModelComponentCreate,
    DeviceModelComponentRead,
    DeviceModelComponentUpdate,
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
    SiteAccessGrantCreate,
    SiteAccessGrantRead,
    SiteAccessGrantUpdate,
    SiteRoleCreate,
    SiteRoleRead,
    SiteRoleUpdate,
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
    if data.tenant_id is not None:
        if tenant_svc.get_tenant(db, data.tenant_id) is None:
            raise HTTPException(status_code=404, detail="tenant ikke funnet")
        tid = data.tenant_id
    else:
        tid = tenant_svc.ensure_default_tenant(db)
    row = Site(
        tenant_id=tid,
        name=data.name.strip(),
        slug=data.slug,
        description=data.description,
        address_line1=data.address_line1,
        address_line2=data.address_line2,
        postal_code=data.postal_code,
        city=data.city,
        county=data.county,
        country=data.country,
        latitude=data.latitude,
        longitude=data.longitude,
        address_note=data.address_note,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def get_site(db: Session, site_id: int) -> Site | None:
    return db.get(Site, site_id)


def update_site(db: Session, site: Site, data: SiteUpdate) -> Site:
    if data.tenant_id is not None:
        if tenant_svc.get_tenant(db, data.tenant_id) is None:
            raise HTTPException(status_code=404, detail="tenant ikke funnet")
        site.tenant_id = data.tenant_id
    if data.name is not None:
        site.name = data.name.strip()
    if data.description is not None:
        site.description = data.description
    if data.address_line1 is not None:
        site.address_line1 = data.address_line1
    if data.address_line2 is not None:
        site.address_line2 = data.address_line2
    if data.postal_code is not None:
        site.postal_code = data.postal_code
    if data.city is not None:
        site.city = data.city
    if data.county is not None:
        site.county = data.county
    if data.country is not None:
        site.country = data.country
    if data.latitude is not None:
        site.latitude = data.latitude
    if data.longitude is not None:
        site.longitude = data.longitude
    if data.address_note is not None:
        site.address_note = data.address_note
    db.commit()
    db.refresh(site)
    return site


def delete_site(db: Session, site: Site) -> None:
    db.delete(site)
    db.commit()


# --- Site roles & access ---

_DEFAULT_SITE_ROLES: list[tuple[str, str, str | None]] = [
    ("utleier", "Utleier", None),
    ("vaktmester", "Vaktmester", None),
    ("vekter", "Vekter", None),
    ("tekniker", "Tekniker", None),
    ("renholder", "Renholder", None),
    ("drift", "Drift", None),
    ("leverandor", "Leverandør", None),
]


def _ensure_default_site_roles(db: Session) -> None:
    n = db.execute(select(SiteRole.id).limit(1)).first()
    if n is not None:
        return
    for slug, name, desc in _DEFAULT_SITE_ROLES:
        db.add(SiteRole(slug=slug, name=name, description=desc))
    db.commit()


def list_site_roles(db: Session) -> list[SiteRoleRead]:
    _ensure_default_site_roles(db)
    rows = list(db.execute(select(SiteRole).order_by(SiteRole.name)).scalars().all())
    return [SiteRoleRead.model_validate(r) for r in rows]


def create_site_role(db: Session, data: SiteRoleCreate) -> SiteRoleRead:
    row = SiteRole(name=data.name.strip(), slug=data.slug, description=data.description)
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="rolle finnes allerede") from None
    db.refresh(row)
    return SiteRoleRead.model_validate(row)


def get_site_role(db: Session, role_id: int) -> SiteRole | None:
    return db.get(SiteRole, role_id)


def update_site_role(db: Session, row: SiteRole, data: SiteRoleUpdate) -> SiteRoleRead:
    patch = data.model_dump(exclude_unset=True)
    if not patch:
        raise HTTPException(status_code=400, detail="ingen felter å oppdatere")
    if "name" in patch and patch["name"] is not None:
        row.name = str(patch["name"]).strip()
    if "description" in patch:
        row.description = patch["description"]
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="rolle finnes allerede") from None
    db.refresh(row)
    return SiteRoleRead.model_validate(row)


def delete_site_role(db: Session, row: SiteRole) -> None:
    db.delete(row)
    db.commit()


def list_site_access_grants(db: Session, *, site_id: int, is_contact: bool | None = None) -> list[SiteAccessGrantRead]:
    q = select(SiteAccessGrant).where(SiteAccessGrant.site_id == site_id).order_by(SiteAccessGrant.id)
    if is_contact is not None:
        q = q.where(SiteAccessGrant.is_contact == bool(is_contact))
    rows = list(db.execute(q).scalars().all())
    return [SiteAccessGrantRead.model_validate(r) for r in rows]


def create_site_access_grant(db: Session, *, site_id: int, data: SiteAccessGrantCreate) -> SiteAccessGrantRead:
    if get_site(db, site_id) is None:
        raise HTTPException(status_code=404, detail="site ikke funnet")
    if db.get(User, data.user_id) is None:
        raise HTTPException(status_code=404, detail="user ikke funnet")
    if db.get(SiteRole, data.role_id) is None:
        raise HTTPException(status_code=404, detail="rolle ikke funnet")
    row = SiteAccessGrant(
        site_id=site_id,
        user_id=int(data.user_id),
        role_id=int(data.role_id),
        is_contact=bool(data.is_contact),
        valid_from=data.valid_from,
        valid_to=data.valid_to,
        notes=data.notes,
    )
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="tilgang finnes allerede") from None
    db.refresh(row)
    return SiteAccessGrantRead.model_validate(row)


def get_site_access_grant(db: Session, grant_id: int) -> SiteAccessGrant | None:
    return db.get(SiteAccessGrant, grant_id)


def update_site_access_grant(db: Session, row: SiteAccessGrant, data: SiteAccessGrantUpdate) -> SiteAccessGrantRead:
    patch = data.model_dump(exclude_unset=True)
    if not patch:
        raise HTTPException(status_code=400, detail="ingen felter å oppdatere")
    if "role_id" in patch and patch["role_id"] is not None:
        if db.get(SiteRole, int(patch["role_id"])) is None:
            raise HTTPException(status_code=404, detail="rolle ikke funnet")
        row.role_id = int(patch["role_id"])
    if "is_contact" in patch and patch["is_contact"] is not None:
        row.is_contact = bool(patch["is_contact"])
    if "valid_from" in patch:
        row.valid_from = patch["valid_from"]
    if "valid_to" in patch:
        row.valid_to = patch["valid_to"]
    if "notes" in patch:
        row.notes = patch["notes"]
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="tilgang finnes allerede") from None
    db.refresh(row)
    return SiteAccessGrantRead.model_validate(row)


def delete_site_access_grant(db: Session, row: SiteAccessGrant) -> None:
    db.delete(row)
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
    fl = data.floor
    floor = None if fl is None else (str(fl).strip() or None)
    row = Room(
        site_id=data.site_id,
        name=data.name.strip(),
        description=data.description,
        floor=floor,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def get_room(db: Session, room_id: int) -> Room | None:
    return db.get(Room, room_id)


def update_room(db: Session, room: Room, data: RoomUpdate) -> Room:
    patch = data.model_dump(exclude_unset=True)
    if not patch:
        raise HTTPException(status_code=400, detail="ingen felter å oppdatere")
    if "site_id" in patch:
        sid = patch["site_id"]
        if sid is None:
            raise HTTPException(status_code=400, detail="site_id kan ikke fjernes")
        if get_site(db, sid) is None:
            raise HTTPException(status_code=404, detail="site ikke funnet")
        room.site_id = sid
    if "name" in patch and patch["name"] is not None:
        room.name = str(patch["name"]).strip()
    if "description" in patch:
        v = patch["description"]
        room.description = None if v is None else (str(v).strip() or None)
    if "floor" in patch:
        v = patch["floor"]
        room.floor = None if v is None else (str(v).strip() or None)
    db.commit()
    db.refresh(room)
    return room


def set_room_floorplan(db: Session, room: Room, content: bytes, mime: str) -> None:
    if len(content) > DM_IMAGE_MAX_BYTES:
        raise HTTPException(status_code=413, detail="plantegning for stor (maks 2 MiB)")
    if mime not in ALLOWED_LOGO_MIME:
        raise HTTPException(
            status_code=400,
            detail="plantegning må være PNG, JPEG, WebP eller SVG",
        )
    root: Path = get_settings().upload_root_path
    relpath = write_room_floorplan_file(root, room.id, content, mime)
    room.floorplan_relpath = relpath
    room.floorplan_mime_type = mime
    db.commit()
    db.refresh(room)


def clear_room_floorplan(db: Session, room: Room) -> None:
    root: Path = get_settings().upload_root_path
    delete_room_floorplan_files(root, room.id)
    room.floorplan_relpath = None
    room.floorplan_mime_type = None
    db.commit()
    db.refresh(room)


def delete_room(db: Session, room: Room) -> None:
    root: Path = get_settings().upload_root_path
    delete_room_floorplan_files(root, room.id)
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
        raise HTTPException(status_code=404, detail="room ikke funnet")
    if data.tenant_id is not None and tenant_svc.get_tenant(db, data.tenant_id) is None:
        raise HTTPException(status_code=404, detail="tenant ikke funnet")
    row = Rack(
        room_id=data.room_id,
        tenant_id=data.tenant_id,
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

    if "tenant_id" in payload:
        tid = payload["tenant_id"]
        if tid is not None and tenant_svc.get_tenant(db, int(tid)) is None:
            raise HTTPException(status_code=404, detail="tenant ikke funnet")
        rack.tenant_id = tid

    db.commit()
    db.refresh(rack)
    return rack


def delete_rack(db: Session, rack: Rack) -> None:
    db.delete(rack)
    db.commit()


# --- Manufacturers ---


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
    row = DeviceType(
        name=data.name.strip(),
        slug=data.slug,
        description=data.description,
        fa_icon=data.fa_icon,
    )
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
    if "fa_icon" in patch:
        row.fa_icon = patch["fa_icon"]
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


# --- Custom hardware components ---


def _dict_or_empty(v: object) -> dict:
    return dict(v) if isinstance(v, dict) else {}


def component_class_read(row: ComponentClass) -> ComponentClassRead:
    return ComponentClassRead.model_validate(row)


def component_field_read(row: ComponentClassField) -> ComponentClassFieldRead:
    return ComponentClassFieldRead(
        id=row.id,
        class_id=row.class_id,
        key=row.key,
        label=row.label,
        data_type=row.data_type,
        unit=row.unit,
        required=row.required,
        sort_order=row.sort_order,
        min_number=row.min_number,
        max_number=row.max_number,
        choices_json=list(row.choices_json) if isinstance(row.choices_json, list) else None,
        default_value=row.default_value,
        description=row.description,
        active=row.active,
    )


def component_effective_field_read(
    row: ComponentClassField,
    *,
    inherited_from: ComponentClass | None,
) -> ComponentClassEffectiveFieldRead:
    return ComponentClassEffectiveFieldRead(
        id=row.id,
        class_id=row.class_id,
        key=row.key,
        label=row.label,
        data_type=row.data_type,
        unit=row.unit,
        required=row.required,
        sort_order=row.sort_order,
        min_number=row.min_number,
        max_number=row.max_number,
        choices_json=list(row.choices_json) if isinstance(row.choices_json, list) else None,
        default_value=row.default_value,
        description=row.description,
        active=row.active,
        inherited_from_class_id=inherited_from.id if inherited_from is not None else None,
        inherited_from_class_name=inherited_from.name if inherited_from is not None else None,
        inherited=inherited_from is not None,
    )


def component_class_parent_read(row: ComponentClassParent) -> ComponentClassParentRead:
    return ComponentClassParentRead.model_validate(row)


def component_read(row: Component) -> ComponentRead:
    return ComponentRead(
        id=row.id,
        class_id=row.class_id,
        manufacturer_id=row.manufacturer_id,
        name=row.name,
        part_number=row.part_number,
        description=row.description,
        specs_json=_dict_or_empty(row.specs_json),
        active=row.active,
    )


def component_child_template_read(row: ComponentChildTemplate) -> ComponentChildTemplateRead:
    return ComponentChildTemplateRead(
        id=row.id,
        parent_component_id=row.parent_component_id,
        child_class_id=row.child_class_id,
        child_component_id=row.child_component_id,
        quantity=row.quantity,
        name_pattern=row.name_pattern,
        slot_label=row.slot_label,
        overrides_json=_dict_or_empty(row.overrides_json),
        materialize_as=row.materialize_as,
        sort_order=row.sort_order,
    )


def device_model_component_read(row: DeviceModelComponent) -> DeviceModelComponentRead:
    return DeviceModelComponentRead(
        id=row.id,
        device_model_id=row.device_model_id,
        component_id=row.component_id,
        quantity=row.quantity,
        slot_label=row.slot_label,
        notes=row.notes,
        overrides_json=_dict_or_empty(row.overrides_json),
        sort_order=row.sort_order,
    )


def device_instance_component_read(row: DeviceInstanceComponent) -> DeviceInstanceComponentRead:
    return DeviceInstanceComponentRead(
        id=row.id,
        device_id=row.device_id,
        component_id=row.component_id,
        quantity=row.quantity,
        slot_label=row.slot_label,
        serial_number=row.serial_number,
        asset_tag=row.asset_tag,
        installed_at=row.installed_at,
        notes=row.notes,
        overrides_json=_dict_or_empty(row.overrides_json),
        sort_order=row.sort_order,
    )


def _component_fields(db: Session, class_id: int) -> list[ComponentClassField]:
    return list(
        db.execute(
            select(ComponentClassField)
            .where(ComponentClassField.class_id == class_id, ComponentClassField.active.is_(True))
            .order_by(ComponentClassField.sort_order, ComponentClassField.id)
        )
        .scalars()
        .all()
    )


def _component_class_parent_ids(db: Session, class_id: int) -> list[int]:
    return list(
        db.execute(
            select(ComponentClassParent.parent_class_id)
            .where(ComponentClassParent.child_class_id == class_id)
            .order_by(ComponentClassParent.sort_order, ComponentClassParent.id)
        )
        .scalars()
        .all()
    )


def _component_class_descendant_ids(db: Session, class_id: int) -> set[int]:
    out: set[int] = set()
    stack = [class_id]
    while stack:
        cur = stack.pop()
        child_ids = list(
            db.execute(
                select(ComponentClassParent.child_class_id).where(ComponentClassParent.parent_class_id == cur)
            )
            .scalars()
            .all()
        )
        for child_id in child_ids:
            if child_id not in out:
                out.add(child_id)
                stack.append(child_id)
    return out


def _component_effective_fields(
    db: Session,
    class_id: int,
    *,
    validate_unique: bool = True,
) -> list[tuple[ComponentClassField, ComponentClass | None]]:
    if get_component_class(db, class_id) is None:
        raise HTTPException(status_code=404, detail="komponentklasse ikke funnet")
    visited: set[int] = set()
    visiting: set[int] = set()
    rows: list[tuple[ComponentClassField, ComponentClass | None]] = []

    def walk(cid: int, inherited_from: ComponentClass | None) -> None:
        if cid in visiting:
            raise HTTPException(status_code=409, detail="komponentklasse-arv inneholder en syklus")
        if cid in visited:
            return
        visiting.add(cid)
        parent_ids = _component_class_parent_ids(db, cid)
        for parent_id in parent_ids:
            parent = get_component_class(db, parent_id)
            if parent is None:
                continue
            walk(parent_id, parent)
        visiting.remove(cid)
        visited.add(cid)
        source = inherited_from if cid != class_id else None
        rows.extend((field, source) for field in _component_fields(db, cid))

    walk(class_id, None)
    if validate_unique:
        by_key: dict[str, list[str]] = defaultdict(list)
        for field, source in rows:
            by_key[field.key].append(source.name if source is not None else "egen klasse")
        duplicate = {key: origins for key, origins in by_key.items() if len(origins) > 1}
        if duplicate:
            detail = "; ".join(f"{key}: {', '.join(origins)}" for key, origins in sorted(duplicate.items()))
            raise HTTPException(status_code=409, detail=f"dupliserte arvede komponentfelt: {detail}")
    return rows


def _normalize_choice_list(v: object) -> list[str] | None:
    if v is None:
        return None
    if not isinstance(v, list):
        raise HTTPException(status_code=422, detail="choices_json må være en liste")
    out = [str(x).strip() for x in v if str(x).strip()]
    return out or None


def _validate_component_field_shape(
    data_type: str,
    min_number: float | None,
    max_number: float | None,
    choices_json: object,
) -> list[str] | None:
    if data_type not in {"text", "number", "integer", "boolean", "choice", "date"}:
        raise HTTPException(status_code=422, detail="ugyldig data_type")
    if min_number is not None and max_number is not None and min_number > max_number:
        raise HTTPException(status_code=422, detail="min_number kan ikke være større enn max_number")
    choices = _normalize_choice_list(choices_json)
    if data_type == "choice" and not choices:
        raise HTTPException(status_code=422, detail="choice-felt må ha choices_json")
    if data_type != "choice" and choices:
        raise HTTPException(status_code=422, detail="choices_json kan bare brukes for choice-felt")
    return choices


def _validate_value(field: ComponentClassField, value: object, *, missing_ok: bool) -> None:
    if value is None or value == "":
        if field.required and not missing_ok:
            raise HTTPException(status_code=422, detail=f"mangler required komponentfelt: {field.key}")
        return
    dt = field.data_type
    if dt == "text":
        if not isinstance(value, str):
            raise HTTPException(status_code=422, detail=f"{field.key} må være tekst")
        return
    if dt == "boolean":
        if not isinstance(value, bool):
            raise HTTPException(status_code=422, detail=f"{field.key} må være boolean")
        return
    if dt in ("number", "integer"):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise HTTPException(status_code=422, detail=f"{field.key} må være tall")
        if dt == "integer" and int(value) != value:
            raise HTTPException(status_code=422, detail=f"{field.key} må være heltall")
        fv = float(value)
        if field.min_number is not None and fv < field.min_number:
            raise HTTPException(status_code=422, detail=f"{field.key} er lavere enn minimum")
        if field.max_number is not None and fv > field.max_number:
            raise HTTPException(status_code=422, detail=f"{field.key} er høyere enn maksimum")
        return
    if dt == "choice":
        choices = [str(x) for x in (field.choices_json or [])]
        if str(value) not in choices:
            raise HTTPException(status_code=422, detail=f"{field.key} må være en gyldig verdi")
        return
    if dt == "date":
        if isinstance(value, (date, datetime)):
            return
        if isinstance(value, str):
            try:
                date.fromisoformat(value[:10])
                return
            except ValueError:
                pass
        raise HTTPException(status_code=422, detail=f"{field.key} må være ISO-dato")


def _validate_specs_for_class(db: Session, class_id: int, data: dict | None, *, partial: bool = False) -> dict:
    specs = dict(data or {})
    fields = [field for field, _source in _component_effective_fields(db, class_id)]
    allowed = {f.key: f for f in fields}
    unknown = sorted(k for k in specs if k not in allowed)
    if unknown:
        raise HTTPException(status_code=422, detail=f"ukjente komponentfelt: {', '.join(unknown)}")
    for f in fields:
        _validate_value(f, specs.get(f.key), missing_ok=partial)
    return specs


def _component_class_id_for_component(db: Session, component_id: int) -> int:
    component = db.get(Component, component_id)
    if component is None:
        raise HTTPException(status_code=404, detail="komponent ikke funnet")
    return component.class_id


def list_component_classes(db: Session) -> list[ComponentClassRead]:
    rows = list(db.execute(select(ComponentClass).order_by(ComponentClass.name)).scalars().all())
    return [component_class_read(r) for r in rows]


def get_component_class(db: Session, class_id: int) -> ComponentClass | None:
    return db.get(ComponentClass, class_id)


STANDARD_COMPONENT_CATALOG: list[dict] = [
    {
        "slug": "physical-device",
        "name": "Physical Device",
        "description": "FreeHCI canonical physical hardware mixin, inspired by Redfish physical resources and SMBIOS chassis/slot data.",
        "icon": "box",
        "fields": [
            ("height_mm", "Height", "integer", "mm", False, 0, None, None, "Physical height in millimeters."),
            ("width_mm", "Width", "integer", "mm", False, 0, None, None, "Physical width in millimeters."),
            ("depth_mm", "Depth", "integer", "mm", False, 0, None, None, "Physical depth in millimeters."),
            ("weight_kg", "Weight", "number", "kg", False, 0, None, None, "Physical weight in kilograms."),
            ("serial_number", "Serial number", "text", None, False, None, None, None, "Manufacturer serial number."),
            ("firmware_version", "Firmware version", "text", None, False, None, None, None, "Firmware or bundle version."),
        ],
    },
    {
        "slug": "network-capable",
        "name": "Network Capable",
        "description": "FreeHCI canonical network capability mixin, mapping cleanly from Redfish NetworkPort and NetworkDeviceFunction.",
        "icon": "network-wired",
        "fields": [
            ("speed_mbps", "Speed", "integer", "Mbps", False, 0, None, None, "Negotiated or nominal network speed."),
            ("supported_speeds", "Supported speeds", "text", None, False, None, None, None, "Comma-separated supported speeds when a list is needed."),
            ("media_type", "Media type", "choice", None, False, None, None, ["copper", "fiber", "backplane", "dac", "virtual", "unknown"], "Physical or logical media type."),
            ("mac_address", "MAC address", "text", None, False, None, None, None, "MAC address when the function or port exposes one."),
        ],
    },
    {
        "slug": "network-adapter",
        "name": "Network Adapter",
        "description": "Physical NIC/CNA adapter. Redfish analogue: NetworkAdapter.",
        "icon": "ethernet",
        "parents": ["physical-device", "network-capable"],
        "fields": [
            ("port_count", "Port count", "integer", None, False, 0, None, None, "Number of physical ports."),
            ("sriov_supported", "SR-IOV supported", "boolean", None, False, None, None, None, "Whether the adapter supports SR-IOV."),
            ("pcie_generation", "PCIe generation", "text", None, False, None, None, None, "PCIe generation or bus standard."),
        ],
    },
    {
        "slug": "network-port",
        "name": "Network Port",
        "description": "Physical network port. Redfish analogue: NetworkPort.",
        "icon": "plug",
        "parents": ["network-capable"],
        "fields": [
            ("port_type", "Port type", "choice", None, False, None, None, ["ethernet", "fibre_channel", "infiniband", "management", "unknown"], "Protocol family for the physical port."),
            ("connector_type", "Connector type", "choice", None, False, None, None, ["rj45", "sfp", "sfp+", "sfp28", "qsfp", "qsfp28", "backplane", "unknown"], "Connector or transceiver form."),
            ("lane_count", "Lane count", "integer", None, False, 0, None, None, "Number of physical lanes."),
        ],
    },
    {
        "slug": "network-device-function",
        "name": "Network Device Function",
        "description": "Logical network function. Redfish analogue: NetworkDeviceFunction.",
        "icon": "diagram-project",
        "parents": ["network-capable"],
        "fields": [
            ("function_type", "Function type", "choice", None, False, None, None, ["ethernet", "fibre_channel", "iscsi", "fcoe", "management", "virtual"], "Logical function type."),
            ("device_enabled", "Device enabled", "boolean", None, False, None, None, None, "Whether the logical function is enabled."),
        ],
    },
    {
        "slug": "memory-module",
        "name": "Memory Module",
        "description": "DIMM or memory device. Redfish Memory and SMBIOS Memory Device analogue.",
        "icon": "memory",
        "parents": ["physical-device"],
        "fields": [
            ("capacity_gb", "Capacity", "integer", "GB", False, 0, None, None, "Installed capacity."),
            ("memory_type", "Memory type", "choice", None, False, None, None, ["ddr3", "ddr4", "ddr5", "lpddr4", "lpddr5", "hbm", "unknown"], "Memory technology."),
            ("speed_mt_s", "Speed", "integer", "MT/s", False, 0, None, None, "Configured or rated transfer speed."),
            ("ecc", "ECC", "boolean", None, False, None, None, None, "Whether ECC is supported/enabled."),
            ("slot", "Slot", "text", None, False, None, None, None, "Physical memory slot or locator."),
        ],
    },
    {
        "slug": "processor",
        "name": "Processor",
        "description": "CPU package/socket. Redfish Processor and SMBIOS Processor analogue.",
        "icon": "microchip",
        "parents": ["physical-device"],
        "fields": [
            ("socket", "Socket", "text", None, False, None, None, None, "CPU socket or SMBIOS socket designation."),
            ("core_count", "Core count", "integer", None, False, 0, None, None, "Number of physical cores."),
            ("thread_count", "Thread count", "integer", None, False, 0, None, None, "Number of hardware threads."),
            ("base_frequency_mhz", "Base frequency", "integer", "MHz", False, 0, None, None, "Base frequency."),
            ("max_frequency_mhz", "Max frequency", "integer", "MHz", False, 0, None, None, "Maximum frequency."),
        ],
    },
    {
        "slug": "drive",
        "name": "Drive",
        "description": "Storage drive. Redfish Drive analogue.",
        "icon": "hard-drive",
        "parents": ["physical-device"],
        "fields": [
            ("capacity_gb", "Capacity", "integer", "GB", False, 0, None, None, "Drive capacity."),
            ("drive_type", "Drive type", "choice", None, False, None, None, ["hdd", "ssd", "nvme", "emmc", "unknown"], "Drive media/interface family."),
            ("protocol", "Protocol", "choice", None, False, None, None, ["sata", "sas", "nvme", "usb", "unknown"], "Drive protocol."),
            ("form_factor", "Form factor", "text", None, False, None, None, None, "Drive form factor."),
        ],
    },
    {
        "slug": "pcie-device",
        "name": "PCIe Device",
        "description": "PCIe add-in or onboard device. Redfish PCIeDevice and SMBIOS System Slot analogue.",
        "icon": "grip",
        "parents": ["physical-device"],
        "fields": [
            ("vendor_id", "Vendor ID", "text", None, False, None, None, None, "PCI vendor ID."),
            ("device_id", "Device ID", "text", None, False, None, None, None, "PCI device ID."),
            ("slot", "Slot", "text", None, False, None, None, None, "PCIe slot or bus location."),
            ("pcie_generation", "PCIe generation", "text", None, False, None, None, None, "PCIe generation."),
        ],
    },
    {
        "slug": "power-supply",
        "name": "Power Supply",
        "description": "Power supply unit. Redfish PowerSupply analogue.",
        "icon": "plug-circle-bolt",
        "parents": ["physical-device"],
        "fields": [
            ("capacity_w", "Capacity", "integer", "W", False, 0, None, None, "Rated power capacity."),
            ("input_voltage_v", "Input voltage", "number", "V", False, 0, None, None, "Input voltage."),
            ("redundant", "Redundant", "boolean", None, False, None, None, None, "Whether the PSU is part of a redundant set."),
        ],
    },
    {
        "slug": "chassis",
        "name": "Chassis",
        "description": "System chassis/enclosure. Redfish Chassis and SMBIOS Chassis analogue.",
        "icon": "server",
        "parents": ["physical-device"],
        "fields": [
            ("chassis_type", "Chassis type", "text", None, False, None, None, None, "Chassis type or enclosure class."),
            ("asset_tag", "Asset tag", "text", None, False, None, None, None, "Asset tag from firmware or inventory."),
        ],
    },
    {
        "slug": "baseboard",
        "name": "Baseboard",
        "description": "Mainboard/baseboard. SMBIOS Baseboard analogue.",
        "icon": "table-cells-large",
        "parents": ["physical-device"],
        "fields": [
            ("board_type", "Board type", "text", None, False, None, None, None, "Baseboard type."),
            ("location", "Location", "text", None, False, None, None, None, "Physical location in chassis."),
        ],
    },
    {
        "slug": "system-slot",
        "name": "System Slot",
        "description": "Physical slot. SMBIOS System Slot analogue.",
        "icon": "border-all",
        "parents": ["physical-device"],
        "fields": [
            ("slot_type", "Slot type", "text", None, False, None, None, None, "Slot type."),
            ("slot_width", "Slot width", "text", None, False, None, None, None, "Electrical/mechanical width."),
            ("occupied", "Occupied", "boolean", None, False, None, None, None, "Whether the slot is occupied."),
        ],
    },
]


EXTERNAL_COMPONENT_MAPPING_PROFILES: list[dict] = [
    {
        "source": "redfish",
        "display_name": "DMTF Redfish",
        "description": "Primary mapping reference for modern out-of-band hardware inventory. FreeHCI keeps its own normal model and maps Redfish resources into canonical classes.",
        "resources": [
            {
                "source_type": "NetworkAdapter",
                "target_class_slug": "network-adapter",
                "relation": "component",
                "notes": "Physical NIC/CNA adapter. Ports and functions should be modeled as child templates/functions.",
                "fields": [
                    {"source_path": "Id", "target_field_key": "slot", "notes": "Use as locator when no dedicated slot is present."},
                    {"source_path": "Manufacturer", "target_field_key": "manufacturer"},
                    {"source_path": "Model", "target_field_key": "model"},
                    {"source_path": "SerialNumber", "target_field_key": "serial_number"},
                    {"source_path": "FirmwareVersion", "target_field_key": "firmware_version"},
                ],
            },
            {
                "source_type": "NetworkPort",
                "target_class_slug": "network-port",
                "relation": "child_template",
                "notes": "Physical port under a NetworkAdapter.",
                "fields": [
                    {"source_path": "CurrentLinkSpeedMbps", "target_field_key": "speed_mbps"},
                    {"source_path": "SupportedLinkCapabilities[].LinkSpeedMbps", "target_field_key": "supported_speeds", "transform": "join_csv"},
                    {"source_path": "PhysicalPortNumber", "target_field_key": "slot"},
                    {"source_path": "ActiveLinkTechnology", "target_field_key": "media_type", "transform": "normalize_media_type"},
                ],
            },
            {
                "source_type": "NetworkDeviceFunction",
                "target_class_slug": "network-device-function",
                "relation": "child_template",
                "notes": "Logical function for SR-IOV, CNA, FC, iSCSI and management functions.",
                "fields": [
                    {"source_path": "NetDevFuncType", "target_field_key": "function_type", "transform": "normalize_function_type"},
                    {"source_path": "DeviceEnabled", "target_field_key": "device_enabled"},
                    {"source_path": "Ethernet.MACAddress", "target_field_key": "mac_address"},
                ],
            },
            {
                "source_type": "Memory",
                "target_class_slug": "memory-module",
                "relation": "component",
                "fields": [
                    {"source_path": "CapacityMiB", "target_field_key": "capacity_gb", "transform": "mib_to_gb"},
                    {"source_path": "MemoryDeviceType", "target_field_key": "memory_type", "transform": "normalize_memory_type"},
                    {"source_path": "OperatingSpeedMhz", "target_field_key": "speed_mt_s"},
                    {"source_path": "Location.PartLocation.ServiceLabel", "target_field_key": "slot"},
                ],
            },
            {
                "source_type": "Processor",
                "target_class_slug": "processor",
                "relation": "component",
                "fields": [
                    {"source_path": "Socket", "target_field_key": "socket"},
                    {"source_path": "TotalCores", "target_field_key": "core_count"},
                    {"source_path": "TotalThreads", "target_field_key": "thread_count"},
                    {"source_path": "MaxSpeedMHz", "target_field_key": "max_frequency_mhz"},
                ],
            },
            {
                "source_type": "Drive",
                "target_class_slug": "drive",
                "relation": "component",
                "fields": [
                    {"source_path": "CapacityBytes", "target_field_key": "capacity_gb", "transform": "bytes_to_gb"},
                    {"source_path": "MediaType", "target_field_key": "drive_type", "transform": "normalize_drive_type"},
                    {"source_path": "Protocol", "target_field_key": "protocol", "transform": "lowercase"},
                    {"source_path": "PhysicalLocation.PartLocation.ServiceLabel", "target_field_key": "slot"},
                ],
            },
            {
                "source_type": "PCIeDevice",
                "target_class_slug": "pcie-device",
                "relation": "component",
                "fields": [
                    {"source_path": "PCIeInterface.PCIeType", "target_field_key": "pcie_generation"},
                    {"source_path": "Manufacturer", "target_field_key": "manufacturer"},
                    {"source_path": "Model", "target_field_key": "model"},
                    {"source_path": "SerialNumber", "target_field_key": "serial_number"},
                ],
            },
            {
                "source_type": "PowerSupply",
                "target_class_slug": "power-supply",
                "relation": "component",
                "fields": [
                    {"source_path": "PowerCapacityWatts", "target_field_key": "capacity_w"},
                    {"source_path": "LineInputVoltage", "target_field_key": "input_voltage_v"},
                    {"source_path": "SerialNumber", "target_field_key": "serial_number"},
                    {"source_path": "FirmwareVersion", "target_field_key": "firmware_version"},
                ],
            },
        ],
    },
    {
        "source": "smbios",
        "display_name": "SMBIOS / DMI",
        "description": "Low-level firmware inventory for sockets, slots, chassis, BIOS and installed memory/CPU details.",
        "resources": [
            {
                "source_type": "Type 3 Chassis",
                "target_class_slug": "chassis",
                "relation": "component",
                "fields": [
                    {"source_path": "Type", "target_field_key": "chassis_type"},
                    {"source_path": "Serial Number", "target_field_key": "serial_number"},
                    {"source_path": "Asset Tag", "target_field_key": "asset_tag"},
                ],
            },
            {
                "source_type": "Type 4 Processor Information",
                "target_class_slug": "processor",
                "relation": "component",
                "fields": [
                    {"source_path": "Socket Designation", "target_field_key": "socket"},
                    {"source_path": "Core Count", "target_field_key": "core_count"},
                    {"source_path": "Thread Count", "target_field_key": "thread_count"},
                    {"source_path": "Max Speed", "target_field_key": "max_frequency_mhz", "transform": "mhz_text_to_int"},
                ],
            },
            {
                "source_type": "Type 9 System Slots",
                "target_class_slug": "system-slot",
                "relation": "component",
                "fields": [
                    {"source_path": "Designation", "target_field_key": "slot"},
                    {"source_path": "Type", "target_field_key": "slot_type"},
                    {"source_path": "Current Usage", "target_field_key": "occupied", "transform": "usage_to_bool"},
                    {"source_path": "Slot Length", "target_field_key": "slot_width"},
                ],
            },
            {
                "source_type": "Type 17 Memory Device",
                "target_class_slug": "memory-module",
                "relation": "component",
                "fields": [
                    {"source_path": "Locator", "target_field_key": "slot"},
                    {"source_path": "Size", "target_field_key": "capacity_gb", "transform": "size_text_to_gb"},
                    {"source_path": "Type", "target_field_key": "memory_type", "transform": "normalize_memory_type"},
                    {"source_path": "Speed", "target_field_key": "speed_mt_s", "transform": "mt_s_text_to_int"},
                    {"source_path": "Serial Number", "target_field_key": "serial_number"},
                ],
            },
        ],
    },
    {
        "source": "lshw",
        "display_name": "lshw",
        "description": "Linux hardware tree mapping. Useful as an OS-side fallback where Redfish/SMBIOS is incomplete or unavailable.",
        "resources": [
            {"source_type": "network", "target_class_slug": "network-adapter", "relation": "component", "fields": [
                {"source_path": "logicalname", "target_field_key": "slot"},
                {"source_path": "serial", "target_field_key": "mac_address"},
                {"source_path": "capacity", "target_field_key": "speed_mbps", "transform": "bits_per_second_to_mbps"},
            ]},
            {"source_type": "memory/bank", "target_class_slug": "memory-module", "relation": "component", "fields": [
                {"source_path": "slot", "target_field_key": "slot"},
                {"source_path": "size", "target_field_key": "capacity_gb", "transform": "bytes_to_gb"},
                {"source_path": "clock", "target_field_key": "speed_mt_s", "transform": "hz_to_mt_s"},
            ]},
            {"source_type": "processor", "target_class_slug": "processor", "relation": "component", "fields": [
                {"source_path": "slot", "target_field_key": "socket"},
                {"source_path": "configuration.cores", "target_field_key": "core_count"},
                {"source_path": "capacity", "target_field_key": "max_frequency_mhz", "transform": "hz_to_mhz"},
            ]},
        ],
    },
    {
        "source": "netbox",
        "display_name": "NetBox",
        "description": "Mapping from NetBox inventory objects to FreeHCI canonical components. Intended for import/sync, not internal storage.",
        "resources": [
            {"source_type": "dcim.Interface", "target_class_slug": "network-port", "relation": "child_template", "fields": [
                {"source_path": "name", "target_field_key": "slot"},
                {"source_path": "type", "target_field_key": "connector_type", "transform": "normalize_connector_type"},
                {"source_path": "speed", "target_field_key": "speed_mbps"},
            ]},
            {"source_type": "dcim.InventoryItem", "target_class_slug": "physical-device", "relation": "component", "fields": [
                {"source_path": "serial", "target_field_key": "serial_number"},
                {"source_path": "asset_tag", "target_field_key": "asset_tag"},
            ]},
        ],
    },
    {
        "source": "openbmc",
        "display_name": "OpenBMC",
        "description": "Mapping from OpenBMC inventory D-Bus objects to FreeHCI canonical classes.",
        "resources": [
            {"source_type": "xyz.openbmc_project.Inventory.Item.Dimm", "target_class_slug": "memory-module", "relation": "component", "fields": [
                {"source_path": "MemorySizeInKB", "target_field_key": "capacity_gb", "transform": "kb_to_gb"},
                {"source_path": "MemoryType", "target_field_key": "memory_type", "transform": "normalize_memory_type"},
                {"source_path": "PartNumber", "target_field_key": "part_number"},
                {"source_path": "SerialNumber", "target_field_key": "serial_number"},
            ]},
            {"source_type": "xyz.openbmc_project.Inventory.Item.Cpu", "target_class_slug": "processor", "relation": "component", "fields": [
                {"source_path": "CoreCount", "target_field_key": "core_count"},
                {"source_path": "Socket", "target_field_key": "socket"},
                {"source_path": "SerialNumber", "target_field_key": "serial_number"},
            ]},
        ],
    },
]


def list_component_external_mapping_profiles(
    source: str | None = None,
) -> list[ComponentExternalMappingProfileRead]:
    profiles = EXTERNAL_COMPONENT_MAPPING_PROFILES
    if source is not None:
        wanted = source.strip().lower()
        profiles = [p for p in profiles if str(p["source"]).lower() == wanted]
    return [ComponentExternalMappingProfileRead.model_validate(p) for p in profiles]


def get_component_external_mapping_profile(source: str) -> ComponentExternalMappingProfileRead | None:
    rows = list_component_external_mapping_profiles(source)
    return rows[0] if rows else None


def _mapping_resource(source: str, resource_type: str) -> dict | None:
    wanted_source = source.strip().lower()
    wanted_type = resource_type.strip().lower()
    for profile in EXTERNAL_COMPONENT_MAPPING_PROFILES:
        if str(profile["source"]).lower() != wanted_source:
            continue
        for resource in profile.get("resources", []):
            if str(resource["source_type"]).lower() == wanted_type:
                return resource
    return None


def _extract_mapping_path(payload: object, path: str) -> object:
    parts = path.split(".") if path else []

    def walk(value: object, idx: int) -> object:
        if idx >= len(parts):
            return value
        part = parts[idx]
        if part.endswith("[]"):
            key = part[:-2]
            if not isinstance(value, dict) or key not in value or not isinstance(value[key], list):
                return None
            out = [walk(item, idx + 1) for item in value[key]]
            return [x for x in out if x is not None]
        if isinstance(value, list):
            out = [walk(item, idx) for item in value]
            return [x for x in out if x is not None]
        if not isinstance(value, dict) or part not in value:
            return None
        return walk(value[part], idx + 1)

    return walk(payload, 0)


def _first_number(value: object) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        cleaned = ""
        seen_digit = False
        for ch in value:
            if ch.isdigit() or (ch == "." and seen_digit):
                cleaned += ch
                if ch.isdigit():
                    seen_digit = True
            elif seen_digit:
                break
        if cleaned:
            try:
                return float(cleaned)
            except ValueError:
                return None
    return None


def _normalize_choice(value: object, mapping: dict[str, str], default: str = "unknown") -> str:
    raw = str(value).strip().lower().replace(" ", "_").replace("-", "_")
    return mapping.get(raw, raw if raw in set(mapping.values()) else default)


def _apply_mapping_transform(value: object, transform: str | None) -> object:
    if value is None or transform is None:
        return value
    if transform == "join_csv":
        if isinstance(value, list):
            return ",".join(str(x) for x in value)
        return str(value)
    if transform == "lowercase":
        return str(value).strip().lower()
    if transform == "bytes_to_gb":
        n = _first_number(value)
        return int(round(n / 1_000_000_000)) if n is not None else value
    if transform == "mib_to_gb":
        n = _first_number(value)
        return int(round(n / 1024)) if n is not None else value
    if transform == "kb_to_gb":
        n = _first_number(value)
        return int(round(n / (1024 * 1024))) if n is not None else value
    if transform == "bits_per_second_to_mbps":
        n = _first_number(value)
        return int(round(n / 1_000_000)) if n is not None else value
    if transform == "hz_to_mhz":
        n = _first_number(value)
        return int(round(n / 1_000_000)) if n is not None else value
    if transform == "hz_to_mt_s":
        n = _first_number(value)
        return int(round(n / 1_000_000)) if n is not None else value
    if transform == "mhz_text_to_int":
        n = _first_number(value)
        return int(n) if n is not None else value
    if transform == "mt_s_text_to_int":
        n = _first_number(value)
        return int(n) if n is not None else value
    if transform == "size_text_to_gb":
        n = _first_number(value)
        if n is None:
            return value
        raw = str(value).lower()
        if "mb" in raw:
            return int(round(n / 1024))
        if "kb" in raw:
            return int(round(n / (1024 * 1024)))
        return int(round(n))
    if transform == "usage_to_bool":
        raw = str(value).strip().lower()
        return raw in {"in use", "used", "occupied", "true", "yes"}
    if transform == "normalize_media_type":
        return _normalize_choice(
            value,
            {
                "ethernet": "copper",
                "base_t": "copper",
                "baset": "copper",
                "twisted_pair": "copper",
                "fiber": "fiber",
                "fibre": "fiber",
                "optical": "fiber",
                "backplane": "backplane",
                "dac": "dac",
                "virtual": "virtual",
            },
        )
    if transform == "normalize_memory_type":
        return _normalize_choice(
            value,
            {"ddr3": "ddr3", "ddr4": "ddr4", "ddr5": "ddr5", "lpddr4": "lpddr4", "lpddr5": "lpddr5", "hbm": "hbm"},
        )
    if transform == "normalize_drive_type":
        return _normalize_choice(value, {"hdd": "hdd", "ssd": "ssd", "nvme": "nvme", "solid_state": "ssd"})
    if transform == "normalize_function_type":
        return _normalize_choice(
            value,
            {
                "ethernet": "ethernet",
                "fibrechannel": "fibre_channel",
                "fibre_channel": "fibre_channel",
                "fc": "fibre_channel",
                "iscsi": "iscsi",
                "fcoe": "fcoe",
                "management": "management",
                "virtual": "virtual",
            },
        )
    if transform == "normalize_connector_type":
        return _normalize_choice(
            value,
            {
                "1000base_t": "rj45",
                "10gbase_t": "rj45",
                "rj45": "rj45",
                "sfp": "sfp",
                "sfp+": "sfp+",
                "sfp28": "sfp28",
                "qsfp": "qsfp",
                "qsfp28": "qsfp28",
                "backplane": "backplane",
            },
        )
    return value


def preview_component_external_mapping(data: ComponentExternalMappingPreviewRequest) -> ComponentExternalMappingPreviewRead:
    resource = _mapping_resource(data.source, data.resource_type)
    if resource is None:
        raise HTTPException(status_code=404, detail="mapping-resource ikke funnet")
    mapped: dict[str, object] = {}
    missing: list[str] = []
    notes: list[str] = []
    if resource.get("notes"):
        notes.append(str(resource["notes"]))
    for field in resource.get("fields", []):
        path = str(field["source_path"])
        value = _extract_mapping_path(data.payload, path)
        if value is None or value == []:
            missing.append(path)
            continue
        mapped[str(field["target_field_key"])] = _apply_mapping_transform(value, field.get("transform"))
        if field.get("notes"):
            notes.append(str(field["notes"]))
    return ComponentExternalMappingPreviewRead(
        source=data.source,
        source_type=str(resource["source_type"]),
        target_class_slug=str(resource["target_class_slug"]),
        relation=str(resource.get("relation") or "component"),
        mapped_values=mapped,
        missing_paths=missing,
        notes=notes,
    )


def _component_class_by_slug(db: Session, slug: str) -> ComponentClass | None:
    return db.execute(select(ComponentClass).where(ComponentClass.slug == slug)).scalar_one_or_none()


def _component_field_by_key(db: Session, class_id: int, key: str) -> ComponentClassField | None:
    return db.execute(
        select(ComponentClassField).where(ComponentClassField.class_id == class_id, ComponentClassField.key == key)
    ).scalar_one_or_none()


def seed_standard_component_catalog(db: Session) -> ComponentStandardCatalogSeedResponse:
    classes_created = 0
    fields_created = 0
    parents_created = 0
    by_slug: dict[str, ComponentClass] = {}

    for class_def in STANDARD_COMPONENT_CATALOG:
        slug = str(class_def["slug"])
        row = _component_class_by_slug(db, slug)
        if row is None:
            row = ComponentClass(
                name=str(class_def["name"]),
                slug=slug,
                description=str(class_def.get("description") or ""),
                icon=class_def.get("icon"),
                active=True,
            )
            db.add(row)
            db.flush()
            classes_created += 1
        by_slug[slug] = row

    for class_def in STANDARD_COMPONENT_CATALOG:
        row = by_slug[str(class_def["slug"])]
        for idx, field_def in enumerate(class_def.get("fields", []), start=1):
            key, label, data_type, unit, required, min_number, max_number, choices, description = field_def
            if _component_field_by_key(db, row.id, key) is not None:
                continue
            normalized_choices = _validate_component_field_shape(data_type, min_number, max_number, choices)
            db.add(
                ComponentClassField(
                    class_id=row.id,
                    key=key,
                    label=label,
                    data_type=data_type,
                    unit=unit,
                    required=required,
                    sort_order=idx,
                    min_number=min_number,
                    max_number=max_number,
                    choices_json=normalized_choices,
                    default_value=None,
                    description=description,
                    active=True,
                )
            )
            fields_created += 1

    for class_def in STANDARD_COMPONENT_CATALOG:
        child = by_slug[str(class_def["slug"])]
        for idx, parent_slug in enumerate(class_def.get("parents", []), start=1):
            parent = by_slug.get(parent_slug)
            if parent is None:
                continue
            exists = db.execute(
                select(ComponentClassParent.id).where(
                    ComponentClassParent.child_class_id == child.id,
                    ComponentClassParent.parent_class_id == parent.id,
                )
            ).scalar_one_or_none()
            if exists is not None:
                continue
            if _component_parent_would_cycle(db, child.id, parent.id):
                raise HTTPException(status_code=409, detail=f"standardkatalog ville laget arv-syklus for {child.slug}")
            db.add(ComponentClassParent(child_class_id=child.id, parent_class_id=parent.id, sort_order=idx))
            db.flush()
            _component_effective_fields(db, child.id)
            parents_created += 1

    db.commit()
    return ComponentStandardCatalogSeedResponse(
        classes_created=classes_created,
        fields_created=fields_created,
        parents_created=parents_created,
        class_slugs=[str(c["slug"]) for c in STANDARD_COMPONENT_CATALOG],
    )


def create_component_class(db: Session, data: ComponentClassCreate) -> ComponentClassRead:
    row = ComponentClass(
        name=data.name.strip(),
        slug=data.slug,
        description=data.description,
        icon=data.icon,
        active=data.active,
    )
    db.add(row)
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=409, detail="komponentklasse finnes allerede") from e
    db.refresh(row)
    return component_class_read(row)


def update_component_class(db: Session, row: ComponentClass, data: ComponentClassUpdate) -> ComponentClassRead:
    patch = data.model_dump(exclude_unset=True)
    if not patch:
        raise HTTPException(status_code=400, detail="ingen felter å oppdatere")
    for k, v in patch.items():
        if k == "name" and v is not None:
            v = str(v).strip()
        setattr(row, k, v)
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=409, detail="komponentklasse finnes allerede") from e
    db.refresh(row)
    return component_class_read(row)


def delete_component_class(db: Session, row: ComponentClass) -> None:
    used = db.execute(select(Component.id).where(Component.class_id == row.id).limit(1)).scalar_one_or_none()
    if used is not None:
        raise HTTPException(status_code=409, detail="komponentklasse er i bruk")
    db.delete(row)
    db.commit()


def list_component_class_parents(db: Session, class_id: int) -> list[ComponentClassParentRead]:
    if get_component_class(db, class_id) is None:
        raise HTTPException(status_code=404, detail="komponentklasse ikke funnet")
    rows = list(
        db.execute(
            select(ComponentClassParent)
            .where(ComponentClassParent.child_class_id == class_id)
            .order_by(ComponentClassParent.sort_order, ComponentClassParent.id)
        )
        .scalars()
        .all()
    )
    return [component_class_parent_read(r) for r in rows]


def _component_parent_would_cycle(db: Session, child_class_id: int, parent_class_id: int) -> bool:
    if child_class_id == parent_class_id:
        return True
    return child_class_id in _component_class_descendant_ids(db, parent_class_id)


def create_component_class_parent(
    db: Session,
    class_id: int,
    data: ComponentClassParentCreate,
) -> ComponentClassParentRead:
    if get_component_class(db, class_id) is None or get_component_class(db, data.parent_class_id) is None:
        raise HTTPException(status_code=404, detail="komponentklasse ikke funnet")
    if _component_parent_would_cycle(db, class_id, data.parent_class_id):
        raise HTTPException(status_code=409, detail="komponentklasse-arv kan ikke lage syklus")
    row = ComponentClassParent(
        child_class_id=class_id,
        parent_class_id=data.parent_class_id,
        sort_order=data.sort_order,
    )
    db.add(row)
    try:
        db.flush()
        _component_effective_fields(db, class_id)
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=409, detail="forelder er allerede lagt til") from e
    except HTTPException:
        db.rollback()
        raise
    db.refresh(row)
    return component_class_parent_read(row)


def get_component_class_parent(db: Session, parent_link_id: int) -> ComponentClassParent | None:
    return db.get(ComponentClassParent, parent_link_id)


def update_component_class_parent(
    db: Session,
    row: ComponentClassParent,
    data: ComponentClassParentUpdate,
) -> ComponentClassParentRead:
    patch = data.model_dump(exclude_unset=True)
    if not patch:
        raise HTTPException(status_code=400, detail="ingen felter å oppdatere")
    for k, v in patch.items():
        setattr(row, k, v)
    db.commit()
    db.refresh(row)
    return component_class_parent_read(row)


def delete_component_class_parent(db: Session, row: ComponentClassParent) -> None:
    child_id = row.child_class_id
    db.delete(row)
    db.flush()
    _component_effective_fields(db, child_id)
    db.commit()


def list_component_effective_fields(db: Session, class_id: int) -> list[ComponentClassEffectiveFieldRead]:
    return [
        component_effective_field_read(field, inherited_from=source)
        for field, source in _component_effective_fields(db, class_id)
    ]


def list_component_fields(db: Session, class_id: int) -> list[ComponentClassFieldRead]:
    if get_component_class(db, class_id) is None:
        raise HTTPException(status_code=404, detail="komponentklasse ikke funnet")
    rows = list(
        db.execute(
            select(ComponentClassField)
            .where(ComponentClassField.class_id == class_id)
            .order_by(ComponentClassField.sort_order, ComponentClassField.id)
        )
        .scalars()
        .all()
    )
    return [component_field_read(r) for r in rows]


def create_component_field(db: Session, class_id: int, data: ComponentClassFieldCreate) -> ComponentClassFieldRead:
    if get_component_class(db, class_id) is None:
        raise HTTPException(status_code=404, detail="komponentklasse ikke funnet")
    choices = _validate_component_field_shape(data.data_type, data.min_number, data.max_number, data.choices_json)
    row = ComponentClassField(
        class_id=class_id,
        key=data.key,
        label=data.label.strip(),
        data_type=data.data_type,
        unit=data.unit,
        required=data.required,
        sort_order=data.sort_order,
        min_number=data.min_number,
        max_number=data.max_number,
        choices_json=choices,
        default_value=data.default_value,
        description=data.description,
        active=data.active,
    )
    db.add(row)
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=409, detail="felt-key finnes allerede for komponentklassen") from e
    db.refresh(row)
    return component_field_read(row)


def get_component_field(db: Session, field_id: int) -> ComponentClassField | None:
    return db.get(ComponentClassField, field_id)


def component_field_impact(db: Session, field: ComponentClassField, data: ComponentClassFieldUpdate) -> ComponentFieldImpactRead:
    patch = data.model_dump(exclude_unset=True)
    if not patch:
        return ComponentFieldImpactRead(breaking=False)
    candidate = ComponentClassField(
        class_id=field.class_id,
        key=field.key,
        label=patch.get("label", field.label),
        data_type=patch.get("data_type", field.data_type),
        unit=patch.get("unit", field.unit),
        required=patch.get("required", field.required),
        sort_order=patch.get("sort_order", field.sort_order),
        min_number=patch.get("min_number", field.min_number),
        max_number=patch.get("max_number", field.max_number),
        choices_json=patch.get("choices_json", field.choices_json),
        default_value=patch.get("default_value", field.default_value),
        description=patch.get("description", field.description),
        active=patch.get("active", field.active),
    )
    _validate_component_field_shape(candidate.data_type, candidate.min_number, candidate.max_number, candidate.choices_json)
    messages: list[str] = []
    affected_class_ids = {field.class_id, *_component_class_descendant_ids(db, field.class_id)}
    components = list(db.execute(select(Component).where(Component.class_id.in_(affected_class_ids))).scalars().all())
    model_links = list(
        db.execute(
            select(DeviceModelComponent)
            .join(Component, Component.id == DeviceModelComponent.component_id)
            .where(Component.class_id.in_(affected_class_ids))
        )
        .scalars()
        .all()
    )
    instance_links = list(
        db.execute(
            select(DeviceInstanceComponent)
            .join(Component, Component.id == DeviceInstanceComponent.component_id)
            .where(Component.class_id.in_(affected_class_ids))
        )
        .scalars()
        .all()
    )
    for row in components:
        try:
            _validate_value(candidate, _dict_or_empty(row.specs_json).get(field.key), missing_ok=False)
        except HTTPException as e:
            messages.append(f"Komponent #{row.id}: {e.detail}")
    for row in model_links:
        try:
            _validate_value(candidate, _dict_or_empty(row.overrides_json).get(field.key), missing_ok=True)
        except HTTPException as e:
            messages.append(f"DeviceModel-komponent #{row.id}: {e.detail}")
    for row in instance_links:
        try:
            _validate_value(candidate, _dict_or_empty(row.overrides_json).get(field.key), missing_ok=True)
        except HTTPException as e:
            messages.append(f"Device-komponent #{row.id}: {e.detail}")
    return ComponentFieldImpactRead(
        breaking=bool(messages),
        affected_components=len(components),
        affected_model_links=len(model_links),
        affected_instance_links=len(instance_links),
        messages=messages[:50],
    )


def update_component_field(
    db: Session,
    field: ComponentClassField,
    data: ComponentClassFieldUpdate,
    *,
    force: bool = False,
) -> ComponentClassFieldRead:
    impact = component_field_impact(db, field, data)
    if impact.breaking and not force:
        raise HTTPException(status_code=409, detail={"message": "feltendring brekker eksisterende data", "impact": impact.model_dump()})
    patch = data.model_dump(exclude_unset=True)
    if not patch:
        raise HTTPException(status_code=400, detail="ingen felter å oppdatere")
    if "choices_json" in patch:
        patch["choices_json"] = _normalize_choice_list(patch["choices_json"])
    data_type = patch.get("data_type", field.data_type)
    min_number = patch.get("min_number", field.min_number)
    max_number = patch.get("max_number", field.max_number)
    choices = patch.get("choices_json", field.choices_json)
    _validate_component_field_shape(data_type, min_number, max_number, choices)
    for k, v in patch.items():
        setattr(field, k, v)
    db.commit()
    db.refresh(field)
    return component_field_read(field)


def delete_component_field(db: Session, field: ComponentClassField, *, force: bool = False) -> None:
    impact = component_field_impact(db, field, ComponentClassFieldUpdate(active=False))
    if impact.breaking and not force:
        raise HTTPException(status_code=409, detail={"message": "feltet er i bruk", "impact": impact.model_dump()})
    db.delete(field)
    db.commit()


def list_components(
    db: Session,
    *,
    class_id: int | None = None,
    manufacturer_id: int | None = None,
) -> list[ComponentRead]:
    stmt = select(Component).order_by(Component.name)
    if class_id is not None:
        stmt = stmt.where(Component.class_id == class_id)
    if manufacturer_id is not None:
        stmt = stmt.where(Component.manufacturer_id == manufacturer_id)
    return [component_read(r) for r in db.execute(stmt).scalars().all()]


def get_component(db: Session, component_id: int) -> Component | None:
    return db.get(Component, component_id)


def create_component(db: Session, data: ComponentCreate) -> ComponentRead:
    if get_component_class(db, data.class_id) is None:
        raise HTTPException(status_code=404, detail="komponentklasse ikke funnet")
    if data.manufacturer_id is not None and get_manufacturer(db, data.manufacturer_id) is None:
        raise HTTPException(status_code=404, detail="manufacturer ikke funnet")
    specs = _validate_specs_for_class(db, data.class_id, data.specs_json)
    row = Component(
        class_id=data.class_id,
        manufacturer_id=data.manufacturer_id,
        name=data.name.strip(),
        part_number=data.part_number,
        description=data.description,
        specs_json=specs,
        active=data.active,
    )
    db.add(row)
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=409, detail="komponent finnes allerede") from e
    db.refresh(row)
    return component_read(row)


def update_component(db: Session, row: Component, data: ComponentUpdate) -> ComponentRead:
    patch = data.model_dump(exclude_unset=True)
    if not patch:
        raise HTTPException(status_code=400, detail="ingen felter å oppdatere")
    class_id = patch.get("class_id", row.class_id)
    if class_id != row.class_id and get_component_class(db, class_id) is None:
        raise HTTPException(status_code=404, detail="komponentklasse ikke funnet")
    if "manufacturer_id" in patch and patch["manufacturer_id"] is not None and get_manufacturer(db, patch["manufacturer_id"]) is None:
        raise HTTPException(status_code=404, detail="manufacturer ikke funnet")
    if "specs_json" in patch or class_id != row.class_id:
        patch["specs_json"] = _validate_specs_for_class(db, class_id, patch.get("specs_json", row.specs_json))
    for k, v in patch.items():
        if k == "name" and v is not None:
            v = str(v).strip()
        setattr(row, k, v)
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=409, detail="komponent finnes allerede") from e
    db.refresh(row)
    return component_read(row)


def delete_component(db: Session, row: Component) -> None:
    used_model = db.execute(select(DeviceModelComponent.id).where(DeviceModelComponent.component_id == row.id).limit(1)).scalar_one_or_none()
    used_dev = db.execute(select(DeviceInstanceComponent.id).where(DeviceInstanceComponent.component_id == row.id).limit(1)).scalar_one_or_none()
    if used_model is not None or used_dev is not None:
        raise HTTPException(status_code=409, detail="komponent er i bruk")
    db.delete(row)
    db.commit()


def list_component_child_templates(db: Session, component_id: int) -> list[ComponentChildTemplateRead]:
    if get_component(db, component_id) is None:
        raise HTTPException(status_code=404, detail="komponent ikke funnet")
    rows = list(
        db.execute(
            select(ComponentChildTemplate)
            .where(ComponentChildTemplate.parent_component_id == component_id)
            .order_by(ComponentChildTemplate.sort_order, ComponentChildTemplate.id)
        )
        .scalars()
        .all()
    )
    return [component_child_template_read(r) for r in rows]


def _validate_child_template(
    db: Session,
    *,
    parent_component_id: int,
    child_class_id: int,
    child_component_id: int | None,
    overrides_json: dict | None,
    materialize_as: str | None,
) -> dict:
    parent = get_component(db, parent_component_id)
    if parent is None:
        raise HTTPException(status_code=404, detail="parent-komponent ikke funnet")
    if get_component_class(db, child_class_id) is None:
        raise HTTPException(status_code=404, detail="child-komponentklasse ikke funnet")
    if child_component_id is not None:
        child_component = get_component(db, child_component_id)
        if child_component is None:
            raise HTTPException(status_code=404, detail="child-komponent ikke funnet")
        if child_component.class_id != child_class_id:
            raise HTTPException(status_code=400, detail="child_component må tilhøre child_class")
        if child_component_id == parent_component_id:
            raise HTTPException(status_code=400, detail="komponent kan ikke inneholde seg selv")
    if materialize_as is not None and materialize_as not in {"interface"}:
        raise HTTPException(status_code=422, detail="materialize_as må være interface eller null")
    return _validate_specs_for_class(db, child_class_id, overrides_json, partial=True)


def create_component_child_template(
    db: Session,
    component_id: int,
    data: ComponentChildTemplateCreate,
) -> ComponentChildTemplateRead:
    overrides = _validate_child_template(
        db,
        parent_component_id=component_id,
        child_class_id=data.child_class_id,
        child_component_id=data.child_component_id,
        overrides_json=data.overrides_json,
        materialize_as=data.materialize_as,
    )
    row = ComponentChildTemplate(
        parent_component_id=component_id,
        child_class_id=data.child_class_id,
        child_component_id=data.child_component_id,
        quantity=data.quantity,
        name_pattern=data.name_pattern,
        slot_label=data.slot_label,
        overrides_json=overrides,
        materialize_as=data.materialize_as,
        sort_order=data.sort_order,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return component_child_template_read(row)


def get_component_child_template(db: Session, template_id: int) -> ComponentChildTemplate | None:
    return db.get(ComponentChildTemplate, template_id)


def update_component_child_template(
    db: Session,
    row: ComponentChildTemplate,
    data: ComponentChildTemplateUpdate,
) -> ComponentChildTemplateRead:
    patch = data.model_dump(exclude_unset=True)
    if not patch:
        raise HTTPException(status_code=400, detail="ingen felter å oppdatere")
    child_class_id = patch.get("child_class_id", row.child_class_id)
    child_component_id = patch.get("child_component_id", row.child_component_id)
    materialize_as = patch.get("materialize_as", row.materialize_as)
    if "overrides_json" in patch or child_class_id != row.child_class_id:
        patch["overrides_json"] = _validate_child_template(
            db,
            parent_component_id=row.parent_component_id,
            child_class_id=child_class_id,
            child_component_id=child_component_id,
            overrides_json=patch.get("overrides_json", row.overrides_json),
            materialize_as=materialize_as,
        )
    else:
        _validate_child_template(
            db,
            parent_component_id=row.parent_component_id,
            child_class_id=child_class_id,
            child_component_id=child_component_id,
            overrides_json=row.overrides_json,
            materialize_as=materialize_as,
        )
    for k, v in patch.items():
        setattr(row, k, v)
    db.commit()
    db.refresh(row)
    return component_child_template_read(row)


def delete_component_child_template(db: Session, row: ComponentChildTemplate) -> None:
    db.delete(row)
    db.commit()


def _template_instance_name(template: ComponentChildTemplate, idx: int) -> str:
    base = template.name_pattern or template.slot_label or "port{n}"
    return base.replace("{n}", str(idx)).replace("{i}", str(idx))


def _speed_from_specs(specs: dict) -> int | None:
    for key in ("speed_mbps", "network_speed_mbps"):
        value = specs.get(key)
        if isinstance(value, bool):
            continue
        if isinstance(value, (int, float)):
            return int(value)
        if isinstance(value, str):
            digits = "".join(ch for ch in value if ch.isdigit())
            if digits:
                return int(digits)
    return None


def materialize_component_interfaces(
    db: Session,
    device_id: int,
    data: ComponentMaterializeInterfacesRequest,
) -> list[DeviceInterfaceRead]:
    dev = _require_device(db, device_id)
    link = get_device_instance_component(db, data.component_link_id)
    if link is None or link.device_id != device_id:
        raise HTTPException(status_code=404, detail="device-komponent ikke funnet")
    templates = list(
        db.execute(
            select(ComponentChildTemplate)
            .where(
                ComponentChildTemplate.parent_component_id == link.component_id,
                ComponentChildTemplate.materialize_as == "interface",
            )
            .order_by(ComponentChildTemplate.sort_order, ComponentChildTemplate.id)
        )
        .scalars()
        .all()
    )
    if not templates:
        raise HTTPException(status_code=400, detail="komponenten har ingen interface-templates")
    existing_names = {
        name
        for name in db.execute(select(DeviceInterface.name).where(DeviceInterface.device_id == device_id)).scalars().all()
    }
    created: list[DeviceInterface] = []
    sort_base = db.execute(select(DeviceInterface.id).where(DeviceInterface.device_id == device_id)).scalars().all()
    sort_order = len(list(sort_base))
    for template in templates:
        child_component_specs = {}
        if template.child_component_id is not None:
            child_component = get_component(db, template.child_component_id)
            child_component_specs = _dict_or_empty(child_component.specs_json) if child_component is not None else {}
        specs = {**child_component_specs, **_dict_or_empty(template.overrides_json)}
        for idx in range(1, template.quantity + 1):
            name = _template_instance_name(template, idx)
            if name in existing_names:
                if data.overwrite_existing:
                    continue
                raise HTTPException(status_code=409, detail=f"interface finnes allerede: {name}")
            sort_order += 1
            iface = DeviceInterface(
                device_id=dev.id,
                name=name,
                description=template.slot_label,
                speed_mbps=_speed_from_specs(specs),
                enabled=True,
                sort_order=sort_order,
            )
            db.add(iface)
            created.append(iface)
            existing_names.add(name)
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=409, detail="kunne ikke opprette interfaces") from e
    for row in created:
        db.refresh(row)
    return [device_interface_read(row) for row in created]


def list_device_model_components(db: Session, model_id: int) -> list[DeviceModelComponentRead]:
    if get_device_model(db, model_id) is None:
        raise HTTPException(status_code=404, detail="device_model ikke funnet")
    rows = list(
        db.execute(
            select(DeviceModelComponent)
            .where(DeviceModelComponent.device_model_id == model_id)
            .order_by(DeviceModelComponent.sort_order, DeviceModelComponent.id)
        )
        .scalars()
        .all()
    )
    return [device_model_component_read(r) for r in rows]


def create_device_model_component(db: Session, model_id: int, data: DeviceModelComponentCreate) -> DeviceModelComponentRead:
    if get_device_model(db, model_id) is None:
        raise HTTPException(status_code=404, detail="device_model ikke funnet")
    class_id = _component_class_id_for_component(db, data.component_id)
    overrides = _validate_specs_for_class(db, class_id, data.overrides_json, partial=True)
    row = DeviceModelComponent(
        device_model_id=model_id,
        component_id=data.component_id,
        quantity=data.quantity,
        slot_label=data.slot_label,
        notes=data.notes,
        overrides_json=overrides,
        sort_order=data.sort_order,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return device_model_component_read(row)


def get_device_model_component(db: Session, link_id: int) -> DeviceModelComponent | None:
    return db.get(DeviceModelComponent, link_id)


def update_device_model_component(db: Session, row: DeviceModelComponent, data: DeviceModelComponentUpdate) -> DeviceModelComponentRead:
    patch = data.model_dump(exclude_unset=True)
    if not patch:
        raise HTTPException(status_code=400, detail="ingen felter å oppdatere")
    component_id = patch.get("component_id", row.component_id)
    class_id = _component_class_id_for_component(db, component_id)
    if "overrides_json" in patch or component_id != row.component_id:
        patch["overrides_json"] = _validate_specs_for_class(db, class_id, patch.get("overrides_json", row.overrides_json), partial=True)
    for k, v in patch.items():
        setattr(row, k, v)
    db.commit()
    db.refresh(row)
    return device_model_component_read(row)


def delete_device_model_component(db: Session, row: DeviceModelComponent) -> None:
    db.delete(row)
    db.commit()


def list_device_instance_components(db: Session, device_id: int) -> list[DeviceInstanceComponentRead]:
    _require_device(db, device_id)
    rows = list(
        db.execute(
            select(DeviceInstanceComponent)
            .where(DeviceInstanceComponent.device_id == device_id)
            .order_by(DeviceInstanceComponent.sort_order, DeviceInstanceComponent.id)
        )
        .scalars()
        .all()
    )
    return [device_instance_component_read(r) for r in rows]


def create_device_instance_component(db: Session, device_id: int, data: DeviceInstanceComponentCreate) -> DeviceInstanceComponentRead:
    _require_device(db, device_id)
    class_id = _component_class_id_for_component(db, data.component_id)
    overrides = _validate_specs_for_class(db, class_id, data.overrides_json, partial=True)
    row = DeviceInstanceComponent(
        device_id=device_id,
        component_id=data.component_id,
        quantity=data.quantity,
        slot_label=data.slot_label,
        serial_number=data.serial_number,
        asset_tag=data.asset_tag,
        installed_at=data.installed_at,
        notes=data.notes,
        overrides_json=overrides,
        sort_order=data.sort_order,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return device_instance_component_read(row)


def copy_model_components_to_device(db: Session, device_id: int) -> list[DeviceInstanceComponentRead]:
    dev = _require_device(db, device_id)
    if dev.device_model_id is None:
        raise HTTPException(status_code=400, detail="device har ingen device_model")
    existing = db.execute(select(DeviceInstanceComponent.id).where(DeviceInstanceComponent.device_id == device_id).limit(1)).scalar_one_or_none()
    if existing is not None:
        raise HTTPException(status_code=409, detail="device har allerede komponenter")
    model_rows = list(
        db.execute(
            select(DeviceModelComponent)
            .where(DeviceModelComponent.device_model_id == dev.device_model_id)
            .order_by(DeviceModelComponent.sort_order, DeviceModelComponent.id)
        )
        .scalars()
        .all()
    )
    for m in model_rows:
        db.add(
            DeviceInstanceComponent(
                device_id=device_id,
                component_id=m.component_id,
                quantity=m.quantity,
                slot_label=m.slot_label,
                notes=m.notes,
                overrides_json=_dict_or_empty(m.overrides_json),
                sort_order=m.sort_order,
            )
        )
    db.commit()
    return list_device_instance_components(db, device_id)


def get_device_instance_component(db: Session, link_id: int) -> DeviceInstanceComponent | None:
    return db.get(DeviceInstanceComponent, link_id)


def update_device_instance_component(
    db: Session,
    row: DeviceInstanceComponent,
    data: DeviceInstanceComponentUpdate,
) -> DeviceInstanceComponentRead:
    patch = data.model_dump(exclude_unset=True)
    if not patch:
        raise HTTPException(status_code=400, detail="ingen felter å oppdatere")
    component_id = patch.get("component_id", row.component_id)
    class_id = _component_class_id_for_component(db, component_id)
    if "overrides_json" in patch or component_id != row.component_id:
        patch["overrides_json"] = _validate_specs_for_class(db, class_id, patch.get("overrides_json", row.overrides_json), partial=True)
    for k, v in patch.items():
        setattr(row, k, v)
    db.commit()
    db.refresh(row)
    return device_instance_component_read(row)


def delete_device_instance_component(db: Session, row: DeviceInstanceComponent) -> None:
    db.delete(row)
    db.commit()


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
