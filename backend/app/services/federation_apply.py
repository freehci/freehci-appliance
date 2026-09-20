"""Apply a TenantInventory snapshot using ensure-funksjoner (slug-nøkler)."""

from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.asn import is_private_asn
from app.models.dcim import Building, DeviceInstance, DeviceModel, DeviceType, Floor, Manufacturer, Rack, RackPlacement, Room, Site, Wing
from app.models.ipam import IpamBgpSession, IpamCircuit, IpamVlan, IpamVlanGroup, IpamVpnService, IpamVrf
from app.models.tenant import Tenant
from app.schemas.dcim import (
    BuildingCreate,
    DeviceInstanceCreate,
    DeviceModelCreate,
    DeviceTypeCreate,
    FloorCreate,
    ManufacturerCreate,
    RackCreate,
    RackPlacementCreate,
    RoomCreate,
    SiteCreate,
    SiteUpdate,
    WingCreate,
)
from app.schemas.ipam import (
    IpamAsAssignmentCreate,
    IpamAutonomousSystemCreate,
    IpamBgpSessionCreate,
    IpamCircuitCreate,
    IpamProviderCreate,
    IpamVlanCreate,
    IpamVlanGroupCreate,
    IpamVpnServiceCreate,
    IpamVrfCreate,
    Ipv4AddressEnsure,
    Ipv4PrefixEnsure,
    Ipv6AddressEnsure,
    Ipv6PrefixEnsure,
)
from app.services import dcim as dcim_svc
from app.services import ipam as ipam_svc
from app.services import ipam_address as addr_svc
from app.services import ipam_facilities as fac_svc
from app.services import ipam_ipv6 as ipv6_svc
from app.services import dcim_power as pwr_svc
from app.services import ipam_bgp as bgp_svc
from app.services import ipam_providers as prov_svc
from app.services import ipam_vpn as vpn_svc
from app.services import tenant as tenant_svc
from app.schemas.tenant import TenantCreate


def _site_by_slug(db: Session, slug: str) -> Site | None:
    return db.execute(select(Site).where(Site.slug == slug)).scalar_one_or_none()


def _building(db: Session, site_id: int, slug: str) -> Building | None:
    return db.execute(select(Building).where(Building.site_id == site_id, Building.slug == slug)).scalar_one_or_none()


def _wing(db: Session, building_id: int, slug: str) -> Wing | None:
    return db.execute(select(Wing).where(Wing.building_id == building_id, Wing.slug == slug)).scalar_one_or_none()


def _floor(db: Session, building_id: int, slug: str) -> Floor | None:
    return db.execute(select(Floor).where(Floor.building_id == building_id, Floor.slug == slug)).scalar_one_or_none()


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

    for b in doc.get("buildings") or []:
        site = _site_by_slug(db, b["site_slug"])
        if site is None:
            continue
        slug = str(b.get("slug") or "").strip().lower()
        if not slug or _building(db, site.id, slug) is not None:
            continue
        dcim_svc.create_building(
            db,
            BuildingCreate(site_id=site.id, name=b.get("name") or slug, slug=slug, description=b.get("description")),
        )

    for w in doc.get("wings") or []:
        site = _site_by_slug(db, w["site_slug"])
        if site is None:
            continue
        bld = _building(db, site.id, str(w.get("building_slug") or "").strip().lower())
        if bld is None:
            continue
        slug = str(w.get("slug") or "").strip().lower()
        if not slug or _wing(db, bld.id, slug) is not None:
            continue
        dcim_svc.create_wing(
            db,
            WingCreate(building_id=bld.id, name=w.get("name") or slug, slug=slug, description=w.get("description")),
        )

    for f in doc.get("floors") or []:
        site = _site_by_slug(db, f["site_slug"])
        if site is None:
            continue
        bld = _building(db, site.id, str(f.get("building_slug") or "").strip().lower())
        if bld is None:
            continue
        slug = str(f.get("slug") or "").strip().lower()
        if not slug or _floor(db, bld.id, slug) is not None:
            continue
        wing_id = None
        wing_slug = str(f.get("wing_slug") or "").strip().lower()
        if wing_slug:
            wing = _wing(db, bld.id, wing_slug)
            if wing is not None:
                wing_id = wing.id
        dcim_svc.create_floor(
            db,
            FloorCreate(
                building_id=bld.id,
                wing_id=wing_id,
                name=f.get("name") or slug,
                slug=slug,
                level=int(f.get("level") or 0),
                description=f.get("description"),
            ),
        )

    for r in doc.get("rooms") or []:
        site = _site_by_slug(db, r["site_slug"])
        if site is None:
            continue
        if _room(db, site.id, r["name"]) is not None:
            continue
        building_id = None
        wing_id = None
        floor_id = None
        bslug = str(r.get("building_slug") or "").strip().lower()
        if bslug:
            bld = _building(db, site.id, bslug)
            if bld is not None:
                building_id = bld.id
                wslug = str(r.get("wing_slug") or "").strip().lower()
                if wslug:
                    wing = _wing(db, bld.id, wslug)
                    if wing is not None:
                        wing_id = wing.id
                fslug = str(r.get("floor_slug") or "").strip().lower()
                if fslug:
                    fl = _floor(db, bld.id, fslug)
                    if fl is not None:
                        floor_id = fl.id
        dcim_svc.create_room(
            db,
            RoomCreate(
                site_id=site.id,
                name=r["name"],
                description=r.get("description"),
                floor=r.get("floor"),
                building_id=building_id,
                wing_id=wing_id,
                floor_id=floor_id,
            ),
        )

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

    site_by_slug = {s.slug: s for s in db.execute(select(Site)).scalars().all()}
    pwr_svc.apply_from_document(db, doc, site_by_slug=site_by_slug)


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
    for g in ipam.get("vlan_groups") or []:
        found = db.execute(
            select(IpamVlanGroup).where(IpamVlanGroup.site_id == site.id, IpamVlanGroup.slug == g["slug"]),
        ).scalar_one_or_none()
        if found is None:
            fac_svc.create_vlan_group(
                db,
                IpamVlanGroupCreate(site_id=site.id, name=g.get("name") or g["slug"], slug=g["slug"]),
            )
    for v in ipam.get("vlans") or []:
        found = db.execute(select(IpamVlan).where(IpamVlan.site_id == site.id, IpamVlan.slug == v["slug"])).scalar_one_or_none()
        if found is None:
            group_slug = (v.get("vlan_group_slug") or "").strip().lower()
            group_id = None
            if group_slug:
                group = db.execute(
                    select(IpamVlanGroup).where(IpamVlanGroup.site_id == site.id, IpamVlanGroup.slug == group_slug),
                ).scalar_one_or_none()
                group_id = group.id if group is not None else None
            fac_svc.create_vlan(
                db,
                IpamVlanCreate(
                    site_id=site.id,
                    vid=int(v["vid"]),
                    name=v.get("name") or v["slug"],
                    slug=v["slug"],
                    vlan_group_id=group_id,
                ),
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
    for p in ipam.get("providers") or []:
        if not p.get("slug"):
            continue
        found = prov_svc.get_provider_by_slug(db, p["slug"])
        if found is None:
            prov_svc.create_provider(db, IpamProviderCreate(name=p.get("name") or p["slug"], slug=p["slug"]))
    for c in ipam.get("circuits") or []:
        number = (c.get("circuit_number") or "").strip()
        if not number:
            continue
        found = db.execute(select(IpamCircuit).where(IpamCircuit.circuit_number == number)).scalar_one_or_none()
        if found is not None:
            continue
        provider = prov_svc.get_provider_by_slug(db, c["provider_slug"]) if c.get("provider_slug") else None
        a_site = _site_by_slug(db, c["a_site_slug"]) if c.get("a_site_slug") else None
        z_site = _site_by_slug(db, c["z_site_slug"]) if c.get("z_site_slug") else None
        fac_svc.create_circuit(
            db,
            IpamCircuitCreate(
                circuit_number=number,
                name=c.get("name") or number,
                circuit_type=c.get("circuit_type") or "other",
                layer=c.get("layer"),
                provider_id=provider.id if provider is not None else None,
                provider_name=c.get("provider_name"),
                a_site_id=a_site.id if a_site is not None else None,
                z_site_id=z_site.id if z_site is not None else None,
            ),
        )
    for v in ipam.get("vpn_services") or []:
        slug = (v.get("slug") or "").strip()
        if not slug:
            continue
        found = db.execute(select(IpamVpnService).where(IpamVpnService.slug == slug)).scalar_one_or_none()
        if found is not None:
            continue
        source_id = None
        src_num = (v.get("source_circuit_number") or "").strip()
        if src_num:
            src = db.execute(select(IpamCircuit).where(IpamCircuit.circuit_number == src_num)).scalar_one_or_none()
            source_id = src.id if src is not None else None
        vpn_svc.create_vpn_service(
            db,
            IpamVpnServiceCreate(
                name=v.get("name") or slug,
                slug=slug,
                vpn_type=v.get("vpn_type") or "other",
                source_circuit_id=source_id,
            ),
        )
    for a in ipam.get("autonomous_systems") or []:
        asn = a.get("asn")
        if asn is None:
            continue
        found = bgp_svc.resolve_as_for_site(db, int(asn), site)
        if found is None:
            bgp_svc.create_autonomous_system(
                db,
                IpamAutonomousSystemCreate(
                    asn=int(asn),
                    name=a.get("name") or f"AS{asn}",
                    slug=a.get("slug"),
                    tenant_id=site.tenant_id if is_private_asn(int(asn)) else None,
                ),
            )
    for x in ipam.get("as_assignments") or []:
        asn = x.get("asn")
        if asn is None:
            continue
        as_row = bgp_svc.resolve_as_for_site(db, int(asn), site)
        if as_row is None:
            continue
        vrf_id = None
        vrf_slug = (x.get("vrf_slug") or "").strip()
        if vrf_slug:
            vrf = db.execute(select(IpamVrf).where(IpamVrf.site_id == site.id, IpamVrf.slug == vrf_slug)).scalar_one_or_none()
            vrf_id = vrf.id if vrf is not None else None
        existing = [
            r
            for r in bgp_svc.list_as_assignments(db, site_id=site.id, as_id=as_row.id)
            if (r.vrf_id or None) == vrf_id
        ]
        if not existing:
            bgp_svc.create_as_assignment(
                db,
                IpamAsAssignmentCreate(autonomous_system_id=as_row.id, site_id=site.id, vrf_id=vrf_id),
            )
    for s in ipam.get("bgp_sessions") or []:
        slug = (s.get("slug") or "").strip()
        local_asn = s.get("local_asn")
        peer_ip = (s.get("peer_ip") or "").strip()
        if local_asn is None or not peer_ip or s.get("remote_asn") is None:
            continue
        found = None
        if slug:
            found = db.execute(
                select(IpamBgpSession).where(IpamBgpSession.site_id == site.id, IpamBgpSession.slug == slug),
            ).scalar_one_or_none()
        if found is not None:
            continue
        local = bgp_svc.resolve_as_for_site(db, int(local_asn), site)
        if local is None:
            continue
        vrf_id = None
        vrf_slug = (s.get("vrf_slug") or "").strip()
        if vrf_slug:
            vrf = db.execute(select(IpamVrf).where(IpamVrf.site_id == site.id, IpamVrf.slug == vrf_slug)).scalar_one_or_none()
            vrf_id = vrf.id if vrf is not None else None
        bgp_svc.create_bgp_session(
            db,
            IpamBgpSessionCreate(
                site_id=site.id,
                local_as_id=local.id,
                remote_asn=int(s["remote_asn"]) if s.get("remote_asn") is not None else None,
                peer_ip=peer_ip,
                vrf_id=vrf_id,
                name=s.get("name"),
                slug=slug or None,
                address_families=s.get("address_families") or ["ipv4-unicast"],
                desired_status=s.get("desired_status") or "planned",
            ),
        )
