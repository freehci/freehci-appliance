"""Apply a TenantInventory snapshot using ensure-funksjoner (slug-nøkler)."""

from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.dcim import DeviceInstance, DeviceModel, DeviceType, Manufacturer, Rack, RackPlacement, Room, Site
from app.models.ipam import IpamVlan, IpamVrf
from app.models.tenant import Tenant
from app.schemas.dcim import DeviceInstanceCreate, DeviceModelCreate, DeviceTypeCreate, ManufacturerCreate, RackCreate, RackPlacementCreate, RoomCreate, SiteCreate, SiteUpdate
from app.schemas.ipam import IpamVlanCreate, IpamVrfCreate, Ipv4AddressEnsure, Ipv4PrefixEnsure, Ipv6AddressEnsure, Ipv6PrefixEnsure
from app.services import dcim as dcim_svc
from app.services import ipam as ipam_svc
from app.services import ipam_address as addr_svc
from app.services import ipam_facilities as fac_svc
from app.services import ipam_ipv6 as ipv6_svc
from app.services import tenant as tenant_svc
from app.schemas.tenant import TenantCreate


def _site_by_slug(db: Session, slug: str) -> Site | None:
    return db.execute(select(Site).where(Site.slug == slug)).scalar_one_or_none()


def _room(db: Session, site_id: int, name: str) -> Room | None:
    return db.execute(select(Room).where(Room.site_id == site_id, Room.name == name)).scalar_one_or_none()


def _rack(db: Session, room_id: int, name: str) -> Rack | None:
    return db.execute(select(Rack).where(Rack.room_id == room_id, Rack.name == name)).scalar_one_or_none()


def apply_tenant_document(db: Session, doc: dict[str, Any]) -> None:
    t = doc.get("tenant") or {}
    slug = str(t.get("slug") or "").strip().lower()
    if not slug:
        raise ValueError("tenant.slug mangler")
    tenant = db.execute(select(Tenant).where(Tenant.slug == slug)).scalar_one_or_none()
    if tenant is None:
        tenant = tenant_svc.create_tenant(
            db,
            TenantCreate(name=str(t.get("name") or slug), slug=slug, description=t.get("description")),
        )

    for s in doc.get("sites") or []:
        existing = _site_by_slug(db, s["slug"])
        if existing is None:
            dcim_svc.create_site(
                db,
                SiteCreate(
                    tenant_id=tenant.id,
                    name=s["name"],
                    slug=s["slug"],
                    description=s.get("description"),
                    city=s.get("city"),
                    country=s.get("country"),
                    address_line1=s.get("address_line1"),
                    postal_code=s.get("postal_code"),
                ),
            )
        else:
            dcim_svc.update_site(
                db,
                existing,
                SiteUpdate(
                    name=s.get("name"),
                    description=s.get("description"),
                    city=s.get("city"),
                    country=s.get("country"),
                ),
            )

    for r in doc.get("rooms") or []:
        site = _site_by_slug(db, r["site_slug"])
        if site is None:
            continue
        if _room(db, site.id, r["name"]) is None:
            dcim_svc.create_room(db, RoomCreate(site_id=site.id, name=r["name"], description=r.get("description"), floor=r.get("floor")))

    for k in doc.get("racks") or []:
        site = _site_by_slug(db, k["site_slug"])
        if site is None:
            continue
        room = _room(db, site.id, k["room_name"])
        if room is None:
            continue
        if _rack(db, room.id, k["name"]) is None:
            dcim_svc.create_rack(
                db,
                RackCreate(
                    room_id=room.id,
                    name=k["name"],
                    u_height=int(k.get("u_height") or 42),
                    mounting=k.get("mounting") or "floor",
                    elevation_mm=k.get("elevation_mm"),
                ),
            )

    for m in doc.get("manufacturers") or []:
        found = db.execute(select(Manufacturer).where(Manufacturer.name == m["name"])).scalar_one_or_none()
        if found is None:
            dcim_svc.create_manufacturer(db, ManufacturerCreate(name=m["name"], description=m.get("description"), website_url=m.get("website_url")))

    for dt in doc.get("device_types") or []:
        found = db.execute(select(DeviceType).where(DeviceType.slug == dt["slug"])).scalar_one_or_none()
        if found is None:
            dcim_svc.create_device_type(db, DeviceTypeCreate(name=dt.get("name") or dt["slug"], slug=dt["slug"]))

    for dm in doc.get("device_models") or []:
        mfr = db.execute(select(Manufacturer).where(Manufacturer.name == dm["manufacturer_name"])).scalar_one_or_none()
        dt = None
        if dm.get("device_type_slug"):
            dt = db.execute(select(DeviceType).where(DeviceType.slug == dm["device_type_slug"])).scalar_one_or_none()
        existing = None
        if mfr is not None:
            existing = db.execute(
                select(DeviceModel).where(DeviceModel.manufacturer_id == mfr.id, DeviceModel.name == dm["name"]),
            ).scalar_one_or_none()
        if existing is None:
            dcim_svc.create_device_model(
                db,
                DeviceModelCreate(
                    name=dm["name"],
                    manufacturer_id=mfr.id if mfr else None,
                    device_type_id=dt.id if dt else None,
                    u_height=int(dm.get("u_height") or 1),
                ),
            )

    for d in doc.get("devices") or []:
        site = _site_by_slug(db, d["site_slug"]) if d.get("site_slug") else None
        found = None
        if site is not None:
            found = db.execute(
                select(DeviceInstance).where(DeviceInstance.site_id == site.id, DeviceInstance.name == d["name"]),
            ).scalar_one_or_none()
        if found is None:
            model = None
            if d.get("model_name") and d.get("manufacturer_name"):
                mfr = db.execute(select(Manufacturer).where(Manufacturer.name == d["manufacturer_name"])).scalar_one_or_none()
                if mfr is not None:
                    model = db.execute(
                        select(DeviceModel).where(DeviceModel.manufacturer_id == mfr.id, DeviceModel.name == d["model_name"]),
                    ).scalar_one_or_none()
            dcim_svc.create_device(
                db,
                DeviceInstanceCreate(
                    name=d["name"],
                    site_id=site.id if site else None,
                    device_model_id=model.id if model else None,
                    serial_number=d.get("serial_number"),
                    asset_tag=d.get("asset_tag"),
                ),
            )

    for p in doc.get("placements") or []:
        site = _site_by_slug(db, p["site_slug"])
        if site is None:
            continue
        room = _room(db, site.id, p["room_name"])
        if room is None:
            continue
        rack = _rack(db, room.id, p["rack_name"])
        device = db.execute(
            select(DeviceInstance).where(DeviceInstance.site_id == site.id, DeviceInstance.name == p["device_name"]),
        ).scalar_one_or_none()
        if rack is None or device is None:
            continue
        existing = db.execute(select(RackPlacement).where(RackPlacement.device_id == device.id)).scalar_one_or_none()
        if existing is None:
            dcim_svc.create_placement(
                db,
                RackPlacementCreate(
                    rack_id=rack.id,
                    device_id=device.id,
                    u_position=int(p.get("u_position") or 1),
                    mounting=p.get("mounting") or "front",
                ),
            )

    for ipam in doc.get("ipam") or []:
        _apply_site_ipam(db, ipam)


def _apply_site_ipam(db: Session, ipam: dict[str, Any]) -> None:
    site_slug = (ipam.get("site") or {}).get("slug")
    if not site_slug:
        return
    site = _site_by_slug(db, site_slug)
    if site is None:
        return
    for v in ipam.get("vrfs") or []:
        found = db.execute(select(IpamVrf).where(IpamVrf.site_id == site.id, IpamVrf.slug == v["slug"])).scalar_one_or_none()
        if found is None:
            fac_svc.create_vrf(db, IpamVrfCreate(site_id=site.id, name=v.get("name") or v["slug"], slug=v["slug"]))
    for v in ipam.get("vlans") or []:
        found = db.execute(select(IpamVlan).where(IpamVlan.site_id == site.id, IpamVlan.slug == v["slug"])).scalar_one_or_none()
        if found is None:
            fac_svc.create_vlan(
                db,
                IpamVlanCreate(site_id=site.id, vid=int(v["vid"]), name=v.get("name") or v["slug"], slug=v["slug"]),
            )
    for p in ipam.get("prefixes") or []:
        ipam_svc.ensure_ipv4_prefix(
            db,
            Ipv4PrefixEnsure(
                site_slug=site_slug,
                cidr=p["cidr"],
                name=p.get("name"),
                slug=p.get("slug"),
                role=p.get("role"),
                status=p.get("status"),
                vlan_slug=p.get("vlan_slug"),
                vrf_slug=p.get("vrf_slug"),
                overlap_policy=p.get("overlap_policy"),
            ),
            update=True,
        )
    for a in ipam.get("addresses") or []:
        addr_svc.ensure_ipv4_address(
            db,
            Ipv4AddressEnsure(
                site_slug=site_slug,
                prefix_cidr=a.get("prefix_cidr"),
                address=a["address"],
                mode="reserve" if a.get("status") != "assigned" else "assign",
                role=a.get("role"),
                note=a.get("note"),
            ),
            update=True,
        )
    for p in ipam.get("ipv6_prefixes") or []:
        ipv6_svc.ensure_ipv6_prefix(
            db,
            Ipv6PrefixEnsure(site_slug=site_slug, cidr=p["cidr"], slug=p.get("slug"), role=p.get("role"), status=p.get("status")),
            update=True,
        )
    for a in ipam.get("ipv6_addresses") or []:
        ipv6_svc.ensure_ipv6_address(
            db,
            Ipv6AddressEnsure(site_slug=site_slug, prefix_cidr=a.get("prefix_cidr"), address=a["address"], mode="reserve", role=a.get("role")),
            update=True,
        )
