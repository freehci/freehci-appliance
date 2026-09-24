"""Apply a TenantInventory snapshot using ensure-funksjoner (slug-nøkler)."""

from __future__ import annotations

import datetime as dt
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.asn import is_private_asn
from app.models.dcim import Building, Cable, DeviceInstance, DeviceInterface, DeviceModel, DeviceType, FiberStrand, Floor, Manufacturer, Rack, RackPlacement, Room, Site, Wing
from app.models.ipam import IpamBgpSession, IpamCircuit, IpamIpv4Address, IpamIpv4Prefix, IpamTunnel, IpamVlan, IpamVlanGroup, IpamVpnService, IpamVrf
from app.models.tenant import Tenant
from app.schemas.dcim import (
    BuildingCreate,
    DeviceInstanceCreate,
    DeviceInstanceUpdate,
    DeviceModelCreate,
    DeviceArtifactCreate,
    DeviceArtifactBaselineCreate,
    DeviceArtifactBaselineMemberCreate,
    DeviceArtifactBaselineAssignmentCreate,
    DeviceArtifactRecordCreate,
    DeviceRoleCreate,
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
    IpamBgpInstanceCreate,
    IpamBgpSessionCreate,
    IpamCircuitCreate,
    IpamCircuitGroupCreate,
    IpamCircuitStrandCreate,
    IpamCircuitTerminationCreate,
    IpamTunnelCreate,
    IpamTunnelTransportCreate,
    IpamVpnMemberCreate,
    IpamContractCreate,
    IpamProviderCreate,
    IpamOverlaySegmentCreate,
    IpamVlanCreate,
    IpamVlanStretchCreate,
    IpamVlanGroupCreate,
    IpamVpnServiceCreate,
    IpamVrfCreate,
    IPV4_RANGE_KINDS,
    ROUTE_TARGET_DIRECTIONS,
    VRF_INSTANCE_INTENTS,
    IpamRouteTargetCreate,
    IpamVrfRouteTargetCreate,
    Ipv4AddressEnsure,
    Ipv4PrefixEnsure,
    Ipv4RangeCreate,
    IpamVrfInstanceCreate,
    Ipv6AddressEnsure,
    Ipv6PrefixEnsure,
)
from app.schemas.platform import (
    PlatformCloudSubscriptionCreate,
    PlatformClusterCreate,
    PlatformClusterMemberCreate,
    PlatformStoragePoolCreate,
    PlatformVirtualDiskCreate,
    PlatformVirtualInterfaceCreate,
    PlatformVirtualMachineCreate,
)
from app.services import catalog as cat_svc
from app.services import dcim as dcim_svc
from app.services import ipam as ipam_svc
from app.services import platform as plat_svc
from app.services import ipam_address as addr_svc
from app.services import ipam_range as range_svc
from app.services import ipam_vrf_instance as vrfi_svc
from app.services import ipam_route_target as rt_svc
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

    for role in doc.get("device_roles") or []:
        slug = str(role.get("slug") or "").strip().lower()
        if not slug or dcim_svc.get_device_role_by_slug(db, slug) is not None:
            continue
        dcim_svc.create_device_role(
            db,
            DeviceRoleCreate(
                name=role.get("name") or slug,
                slug=slug,
                kind=role.get("kind") or "other",
                description=role.get("description"),
            ),
        )

    for art in doc.get("device_artifacts") or []:
        slug = str(art.get("slug") or "").strip().lower()
        if not slug or dcim_svc.get_device_artifact_by_slug(db, slug) is not None:
            continue
        version = str(art.get("version") or "").strip()
        if not version:
            continue
        dcim_svc.create_device_artifact(
            db,
            DeviceArtifactCreate(
                name=art.get("name") or slug,
                slug=slug,
                kind=art.get("kind") or "other",
                version=version,
                description=art.get("description"),
            ),
        )

    for b in doc.get("device_artifact_baselines") or []:
        slug = str(b.get("slug") or "").strip().lower()
        kind = str(b.get("kind") or "").strip().lower()
        if not slug or kind not in {"firmware", "bios"} or dcim_svc.get_artifact_baseline_by_slug(db, slug) is not None:
            continue
        try:
            baseline = dcim_svc.create_artifact_baseline(
                db,
                DeviceArtifactBaselineCreate(
                    name=b.get("name") or slug,
                    slug=slug,
                    kind=kind,
                    description=b.get("description"),
                ),
            )
        except Exception:
            continue
        for art_slug in b.get("artifact_slugs") or []:
            art = dcim_svc.get_device_artifact_by_slug(db, str(art_slug or "").strip().lower())
            if art is None:
                continue
            try:
                dcim_svc.add_artifact_baseline_member(
                    db,
                    baseline,
                    DeviceArtifactBaselineMemberCreate(artifact_id=art.id),
                )
            except Exception:
                continue

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
        role = dcim_svc.get_device_role_by_slug(db, str(d.get("device_role_slug") or "").strip().lower()) if d.get("device_role_slug") else None
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
                    device_role_id=role.id if role is not None else None,
                    serial_number=d.get("serial_number"),
                    asset_tag=d.get("asset_tag"),
                ),
            )
        elif role is not None and found.device_role_id != role.id:
            dcim_svc.update_device(db, found, DeviceInstanceUpdate(device_role_id=role.id))

    for rec in doc.get("device_artifact_records") or []:
        device = _device_by_site_name(db, rec.get("site_slug"), rec.get("device_name"))
        art = dcim_svc.get_device_artifact_by_slug(db, str(rec.get("artifact_slug") or "").strip().lower())
        if device is None or art is None:
            continue
        existing = [
            r
            for r in dcim_svc.list_device_artifact_records(db, device.id)
            if r.artifact_id == art.id
        ]
        if existing:
            continue
        intent = str(rec.get("intent") or "recorded").strip().lower() or "recorded"
        if intent not in ("recorded", "intended"):
            intent = "recorded"
        dcim_svc.record_device_artifact(
            db,
            device,
            DeviceArtifactRecordCreate(artifact_id=art.id, intent=intent),
        )

    for rec in doc.get("device_artifact_baseline_assignments") or []:
        device = _device_by_site_name(db, rec.get("site_slug"), rec.get("device_name"))
        baseline = dcim_svc.get_artifact_baseline_by_slug(db, str(rec.get("baseline_slug") or "").strip().lower())
        if device is None or baseline is None:
            continue
        existing = [
            r
            for r in dcim_svc.list_artifact_baseline_assignments(db, device_id=device.id)
            if r.baseline_id == baseline.id
        ]
        if existing:
            continue
        intent = str(rec.get("intent") or "recorded").strip().lower() or "recorded"
        if intent not in ("recorded", "intended"):
            intent = "recorded"
        try:
            dcim_svc.assign_artifact_baseline(
                db,
                device,
                DeviceArtifactBaselineAssignmentCreate(baseline_id=baseline.id, intent=intent),
            )
        except Exception:
            continue

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
    _apply_vlan_stretches(db, doc)

    site_by_slug = {s.slug: s for s in db.execute(select(Site)).scalars().all()}
    pwr_svc.apply_from_document(db, doc, site_by_slug=site_by_slug)
    _apply_circuit_strands(db, doc)
    _apply_platform(db, doc)
    _bind_vif_ipv4(db, doc)
    _apply_catalog(db, doc)


def _apply_vlan_stretches(db: Session, doc: dict[str, Any]) -> None:
    rows: list[dict[str, Any]] = list(doc.get("vlan_stretches") or [])
    for ipam in doc.get("ipam") or []:
        rows.extend(ipam.get("vlan_stretches") or [])
    seen: set[str] = set()
    for raw in rows:
        slug = (raw.get("slug") or "").strip().lower()
        a_site = (raw.get("a_site_slug") or "").strip()
        z_site = (raw.get("z_site_slug") or "").strip()
        a_vlan = (raw.get("a_vlan_slug") or "").strip().lower()
        z_vlan = (raw.get("z_vlan_slug") or "").strip().lower()
        if not slug or not a_site or not z_site or not a_vlan or not z_vlan or slug in seen:
            continue
        seen.add(slug)
        if fac_svc.get_vlan_stretch_by_slug(db, slug) is not None:
            continue
        site_a = _site_by_slug(db, a_site)
        site_z = _site_by_slug(db, z_site)
        if site_a is None or site_z is None:
            continue
        vlan_a = db.execute(
            select(IpamVlan).where(IpamVlan.site_id == site_a.id, IpamVlan.slug == a_vlan),
        ).scalar_one_or_none()
        vlan_z = db.execute(
            select(IpamVlan).where(IpamVlan.site_id == site_z.id, IpamVlan.slug == z_vlan),
        ).scalar_one_or_none()
        if vlan_a is None or vlan_z is None:
            continue
        try:
            fac_svc.create_vlan_stretch(
                db,
                IpamVlanStretchCreate(
                    vlan_a_id=vlan_a.id,
                    vlan_b_id=vlan_z.id,
                    name=raw.get("name") or slug,
                    slug=slug,
                    description=raw.get("description"),
                ),
            )
        except Exception:
            continue


def _apply_circuit_strands(db: Session, doc: dict[str, Any]) -> None:
    for ipam in doc.get("ipam") or []:
        for b in ipam.get("circuit_strands") or []:
            number = (b.get("circuit_number") or "").strip()
            cable_slug = (b.get("cable_slug") or "").strip()
            site = _site_by_slug(db, (b.get("site_slug") or "").strip())
            position = b.get("position")
            if not number or not cable_slug or site is None or position is None:
                continue
            circuit = db.execute(select(IpamCircuit).where(IpamCircuit.circuit_number == number)).scalar_one_or_none()
            cable = db.execute(select(Cable).where(Cable.site_id == site.id, Cable.slug == cable_slug)).scalar_one_or_none()
            if circuit is None or cable is None:
                continue
            strand = db.execute(
                select(FiberStrand).where(FiberStrand.cable_id == cable.id, FiberStrand.position == int(position)),
            ).scalar_one_or_none()
            if strand is None or fac_svc.get_circuit_strand_by_strand(db, strand.id) is not None:
                continue
            try:
                fac_svc.create_circuit_strand(db, circuit, IpamCircuitStrandCreate(strand_id=strand.id))
            except Exception:
                continue


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
    for rt in ipam.get("route_targets") or []:
        slug = str(rt.get("slug") or "").strip().lower()
        value = str(rt.get("value") or "").strip()
        if not slug or not value:
            continue
        if rt_svc.get_route_target_by_slug(db, slug) is not None:
            continue
        try:
            rt_svc.create_route_target(
                db,
                IpamRouteTargetCreate(name=rt.get("name") or slug, slug=slug, value=value, description=rt.get("description")),
            )
        except Exception:
            continue
    for bind in ipam.get("vrf_route_targets") or []:
        vrf_slug = str(bind.get("vrf_slug") or "").strip().lower()
        rt_slug = str(bind.get("route_target_slug") or "").strip().lower()
        direction = str(bind.get("direction") or "").strip().lower()
        if not vrf_slug or not rt_slug or direction not in ROUTE_TARGET_DIRECTIONS:
            continue
        vrf = db.execute(
            select(IpamVrf).where(IpamVrf.site_id == site.id, IpamVrf.slug == vrf_slug),
        ).scalar_one_or_none()
        rt_row = rt_svc.get_route_target_by_slug(db, rt_slug)
        if vrf is None or rt_row is None:
            continue
        existing = [
            x
            for x in rt_svc.list_vrf_bindings(db, vrf_id=vrf.id)
            if x.route_target_id == rt_row.id and x.direction == direction
        ]
        if existing:
            continue
        rt_svc.bind_vrf_route_target(
            db,
            vrf,
            IpamVrfRouteTargetCreate(route_target_id=rt_row.id, direction=direction),
        )
    for inst in ipam.get("vrf_instances") or []:
        vrf_slug = str(inst.get("vrf_slug") or "").strip().lower()
        device_name = str(inst.get("device_name") or "").strip()
        slug = str(inst.get("slug") or "").strip().lower()
        if not vrf_slug or not device_name:
            continue
        vrf = db.execute(
            select(IpamVrf).where(IpamVrf.site_id == site.id, IpamVrf.slug == vrf_slug),
        ).scalar_one_or_none()
        device = _device_by_site_name(db, site.slug, device_name)
        if vrf is None or device is None:
            continue
        if vrfi_svc.get_instance_by_slug(db, vrf.id, slug or device.name) is not None:
            continue
        existing = [
            x
            for x in vrfi_svc.list_instances(db, vrf_id=vrf.id, device_id=device.id)
        ]
        if existing:
            continue
        intent = str(inst.get("intent") or "recorded").strip().lower() or "recorded"
        if intent not in VRF_INSTANCE_INTENTS:
            intent = "recorded"
        vrfi_svc.create_instance(
            db,
            vrf,
            IpamVrfInstanceCreate(
                device_id=device.id,
                slug=slug or None,
                intent=intent,
                route_distinguisher=inst.get("route_distinguisher"),
                description=inst.get("description"),
            ),
        )
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
    for o in ipam.get("overlay_segments") or []:
        slug = (o.get("slug") or "").strip().lower()
        vni = o.get("vni")
        if not slug or vni is None:
            continue
        if fac_svc.get_overlay_segment_by_slug(db, site.id, slug) is not None:
            continue
        vlan_id = None
        vlan_slug = (o.get("vlan_slug") or "").strip().lower()
        if vlan_slug:
            vlan = db.execute(
                select(IpamVlan).where(IpamVlan.site_id == site.id, IpamVlan.slug == vlan_slug),
            ).scalar_one_or_none()
            vlan_id = vlan.id if vlan is not None else None
        vrf_id = None
        vrf_slug = (o.get("vrf_slug") or "").strip()
        if vrf_slug:
            vrf = db.execute(
                select(IpamVrf).where(IpamVrf.site_id == site.id, IpamVrf.slug == vrf_slug),
            ).scalar_one_or_none()
            vrf_id = vrf.id if vrf is not None else None
        kind = (o.get("kind") or "vxlan").strip().lower() or "vxlan"
        try:
            fac_svc.create_overlay_segment(
                db,
                IpamOverlaySegmentCreate(
                    site_id=site.id,
                    vni=int(vni),
                    name=o.get("name") or slug,
                    slug=slug,
                    kind=kind,
                    vlan_id=vlan_id,
                    vrf_id=vrf_id,
                    description=o.get("description"),
                ),
            )
        except Exception:
            continue
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
    for r in ipam.get("ipv4_ranges") or []:
        slug = str(r.get("slug") or "").strip().lower()
        start = str(r.get("start_address") or "").strip()
        end = str(r.get("end_address") or "").strip()
        cidr = str(r.get("prefix_cidr") or "").strip()
        if not slug or not start or not end or not cidr:
            continue
        pfx = db.execute(
            select(IpamIpv4Prefix).where(IpamIpv4Prefix.site_id == site.id, IpamIpv4Prefix.cidr == cidr),
        ).scalar_one_or_none()
        if pfx is None:
            continue
        if range_svc.get_ipv4_range_by_slug(db, pfx.id, slug) is not None:
            continue
        kind = str(r.get("kind") or "other").strip().lower() or "other"
        if kind not in IPV4_RANGE_KINDS:
            kind = "other"
        range_svc.create_ipv4_range(
            db,
            pfx,
            Ipv4RangeCreate(
                name=r.get("name") or slug,
                slug=slug,
                kind=kind,
                start_address=start,
                end_address=end,
                description=r.get("description"),
            ),
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
    for g in ipam.get("circuit_groups") or []:
        slug = (g.get("slug") or "").strip()
        if not slug:
            continue
        found = fac_svc.get_circuit_group_by_slug(db, slug)
        if found is not None:
            continue
        fac_svc.create_circuit_group(
            db,
            IpamCircuitGroupCreate(
                name=g.get("name") or slug,
                slug=slug,
                shared_risk=g.get("shared_risk"),
                description=g.get("description"),
            ),
        )
    for c in ipam.get("contracts") or []:
        slug = (c.get("slug") or "").strip()
        provider = prov_svc.get_provider_by_slug(db, c["provider_slug"]) if c.get("provider_slug") else None
        if not slug or provider is None:
            continue
        found = prov_svc.get_contract_by_slug(db, provider.id, slug)
        if found is not None:
            continue
        starts = None
        ends = None
        if c.get("starts_on"):
            starts = dt.date.fromisoformat(str(c["starts_on"])[:10])
        if c.get("ends_on"):
            ends = dt.date.fromisoformat(str(c["ends_on"])[:10])
        prov_svc.create_contract(
            db,
            IpamContractCreate(
                provider_id=provider.id,
                name=c.get("name") or slug,
                slug=slug,
                reference=c.get("reference"),
                starts_on=starts,
                ends_on=ends,
                description=c.get("description"),
            ),
        )
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
        contract = None
        if provider is not None and c.get("contract_slug"):
            contract = prov_svc.get_contract_by_slug(db, provider.id, c["contract_slug"])
        group = fac_svc.get_circuit_group_by_slug(db, c["group_slug"]) if c.get("group_slug") else None
        fac_svc.create_circuit(
            db,
            IpamCircuitCreate(
                circuit_number=number,
                name=c.get("name") or number,
                circuit_type=c.get("circuit_type") or "other",
                layer=c.get("layer"),
                provider_id=provider.id if provider is not None else None,
                provider_name=c.get("provider_name"),
                contract_id=contract.id if contract is not None else None,
                group_id=group.id if group is not None else None,
                provider_circuit_id=c.get("provider_circuit_id"),
                capacity_mbps=c.get("capacity_mbps"),
                cir_mbps=c.get("cir_mbps"),
                service_type=c.get("service_type"),
                medium=c.get("medium"),
                operational_status=c.get("operational_status"),
                ownership=c.get("ownership"),
                is_leased=c.get("is_leased") if c.get("ownership") is None else None,
                a_site_id=a_site.id if a_site is not None else None,
                z_site_id=z_site.id if z_site is not None else None,
            ),
        )
    for t in ipam.get("circuit_terminations") or []:
        number = (t.get("circuit_number") or "").strip()
        endpoint = (t.get("endpoint") or "").strip().lower()
        if not number or endpoint not in {"a", "z"}:
            continue
        circuit = db.execute(select(IpamCircuit).where(IpamCircuit.circuit_number == number)).scalar_one_or_none()
        if circuit is None:
            continue
        site = _site_by_slug(db, (t.get("site_slug") or "").strip())
        device = None
        iface = None
        device_name = (t.get("device_name") or "").strip()
        iface_name = (t.get("interface_name") or "").strip()
        if device_name:
            q = select(DeviceInstance).where(DeviceInstance.name == device_name)
            if site is not None:
                q = q.where(DeviceInstance.site_id == site.id)
            device = db.execute(q).scalars().first()
        if device is not None and iface_name:
            iface = db.execute(
                select(DeviceInterface).where(
                    DeviceInterface.device_id == device.id,
                    DeviceInterface.name == iface_name,
                ),
            ).scalar_one_or_none()
        try:
            fac_svc.upsert_circuit_termination(
                db,
                circuit,
                IpamCircuitTerminationCreate(
                    endpoint=endpoint,
                    kind=t.get("kind"),
                    site_id=site.id if site is not None else None,
                    device_id=device.id if device is not None else None,
                    interface_id=iface.id if iface is not None else None,
                    label=t.get("label"),
                ),
            )
        except Exception:
            continue
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
    for m in ipam.get("vpn_members") or []:
        vpn_slug = (m.get("vpn_slug") or "").strip()
        site = _site_by_slug(db, (m.get("site_slug") or "").strip())
        client_slug = (m.get("slug") or "").strip()
        client_name = (m.get("name") or "").strip()
        if not vpn_slug:
            continue
        vpn = db.execute(select(IpamVpnService).where(IpamVpnService.slug == vpn_slug)).scalar_one_or_none()
        if vpn is None:
            continue
        try:
            if site is not None:
                if vpn_svc.get_vpn_member_by_site(db, vpn.id, site.id) is not None:
                    continue
                vpn_svc.create_vpn_member(db, vpn, IpamVpnMemberCreate(site_id=site.id, role=m.get("role")))
            elif client_slug or client_name:
                slug = client_slug or None
                if slug and vpn_svc.get_vpn_member_by_slug(db, vpn.id, slug) is not None:
                    continue
                vpn_svc.create_vpn_member(
                    db,
                    vpn,
                    IpamVpnMemberCreate(name=client_name or slug, slug=slug, role=m.get("role")),
                )
        except Exception:
            continue
    for t in ipam.get("tunnels") or []:
        vpn_slug = (t.get("vpn_slug") or "").strip()
        slug = (t.get("slug") or "").strip()
        if not vpn_slug or not slug:
            continue
        vpn = db.execute(select(IpamVpnService).where(IpamVpnService.slug == vpn_slug)).scalar_one_or_none()
        if vpn is None:
            continue
        found = db.execute(select(IpamTunnel).where(IpamTunnel.vpn_service_id == vpn.id, IpamTunnel.slug == slug)).scalar_one_or_none()
        if found is not None:
            continue
        try:
            vpn_svc.create_tunnel(
                db,
                vpn,
                IpamTunnelCreate(name=t.get("name") or slug, slug=slug, status=t.get("status") or "planned"),
            )
        except Exception:
            continue
    for b in ipam.get("tunnel_transports") or []:
        vpn_slug = (b.get("vpn_slug") or "").strip()
        tunnel_slug = (b.get("tunnel_slug") or "").strip()
        number = (b.get("circuit_number") or "").strip()
        if not vpn_slug or not tunnel_slug or not number:
            continue
        vpn = db.execute(select(IpamVpnService).where(IpamVpnService.slug == vpn_slug)).scalar_one_or_none()
        circuit = db.execute(select(IpamCircuit).where(IpamCircuit.circuit_number == number)).scalar_one_or_none()
        if vpn is None or circuit is None:
            continue
        tunnel = db.execute(
            select(IpamTunnel).where(IpamTunnel.vpn_service_id == vpn.id, IpamTunnel.slug == tunnel_slug),
        ).scalar_one_or_none()
        if tunnel is None or vpn_svc.get_tunnel_transport_by_circuit(db, tunnel.id, circuit.id) is not None:
            continue
        try:
            vpn_svc.create_tunnel_transport(db, tunnel, IpamTunnelTransportCreate(circuit_id=circuit.id))
        except Exception:
            continue
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
    for i in ipam.get("bgp_instances") or []:
        slug = (i.get("slug") or "").strip().lower()
        device_name = (i.get("device_name") or "").strip()
        local_asn = i.get("local_asn")
        if not slug or not device_name or local_asn is None:
            continue
        if bgp_svc.get_bgp_instance_by_slug(db, site.id, slug) is not None:
            continue
        device = _device_by_site_name(db, site.slug, device_name)
        local = bgp_svc.resolve_as_for_site(db, int(local_asn), site)
        if device is None or local is None:
            continue
        vrf_id = None
        vrf_slug = (i.get("vrf_slug") or "").strip()
        if vrf_slug:
            vrf = db.execute(select(IpamVrf).where(IpamVrf.site_id == site.id, IpamVrf.slug == vrf_slug)).scalar_one_or_none()
            vrf_id = vrf.id if vrf is not None else None
        intent = (i.get("intent") or "recorded").strip().lower()
        if intent not in ("recorded", "intended"):
            intent = "recorded"
        try:
            bgp_svc.create_bgp_instance(
                db,
                IpamBgpInstanceCreate(
                    device_id=device.id,
                    local_as_id=local.id,
                    vrf_id=vrf_id,
                    name=i.get("name") or slug,
                    slug=slug,
                    intent=intent,
                    router_id=i.get("router_id"),
                    description=i.get("description"),
                ),
            )
        except Exception:
            continue
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
        instance_id = None
        instance_slug = (s.get("instance_slug") or "").strip().lower()
        if instance_slug:
            inst = bgp_svc.get_bgp_instance_by_slug(db, site.id, instance_slug)
            instance_id = inst.id if inst is not None else None
        bgp_svc.create_bgp_session(
            db,
            IpamBgpSessionCreate(
                site_id=site.id,
                bgp_instance_id=instance_id,
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


def _device_by_site_name(db: Session, site_slug: str | None, name: str | None) -> DeviceInstance | None:
    if not name:
        return None
    site = _site_by_slug(db, site_slug) if site_slug else None
    if site is None:
        return None
    return db.execute(
        select(DeviceInstance).where(DeviceInstance.site_id == site.id, DeviceInstance.name == name),
    ).scalar_one_or_none()


def _ipv4_on_site(db: Session, site_id: int, address: str) -> IpamIpv4Address | None:
    return db.execute(
        select(IpamIpv4Address)
        .join(IpamIpv4Prefix, IpamIpv4Address.ipv4_prefix_id == IpamIpv4Prefix.id)
        .where(IpamIpv4Prefix.site_id == site_id, IpamIpv4Address.address == address),
    ).scalar_one_or_none()


def _apply_platform(db: Session, doc: dict[str, Any]) -> None:
    for cloud in doc.get("cloud_subscriptions") or []:
        slug = str(cloud.get("slug") or "").strip()
        if not slug or plat_svc.get_cloud_by_slug(db, slug) is not None:
            continue
        plat_svc.create_cloud_subscription(
            db,
            PlatformCloudSubscriptionCreate(
                name=cloud.get("name") or slug,
                slug=slug,
                kind=cloud.get("kind") or "other",
                status=cloud.get("status") or "planned",
                description=cloud.get("description"),
            ),
        )
    for c in doc.get("clusters") or []:
        slug = str(c.get("slug") or "").strip()
        if not slug:
            continue
        site = _site_by_slug(db, c["site_slug"]) if c.get("site_slug") else None
        cluster = plat_svc.get_cluster_by_slug(db, slug)
        if cluster is None:
            cluster = plat_svc.create_cluster(
                db,
                PlatformClusterCreate(
                    name=c.get("name") or slug,
                    slug=slug,
                    kind=c.get("kind") or "other",
                    site_id=site.id if site is not None else None,
                    description=c.get("description"),
                ),
            )
        for member in c.get("members") or []:
            device = _device_by_site_name(db, member.get("site_slug"), member.get("device_name"))
            if device is None or plat_svc.device_is_member(db, cluster.id, device.id):
                continue
            plat_svc.add_member(
                db,
                cluster,
                PlatformClusterMemberCreate(device_id=device.id, role=member.get("role") or "node"),
            )
        for pool in c.get("storage_pools") or []:
            pslug = str(pool.get("slug") or "").strip()
            if not pslug or plat_svc.get_storage_pool_by_slug(db, pslug) is not None:
                continue
            plat_svc.create_storage_pool(
                db,
                cluster,
                PlatformStoragePoolCreate(
                    name=pool.get("name") or pslug,
                    slug=pslug,
                    kind=pool.get("kind") or "other",
                    status=pool.get("status") or "planned",
                ),
            )
        for vm in c.get("vms") or []:
            vslug = str(vm.get("slug") or "").strip()
            if not vslug:
                continue
            existing_vm = plat_svc.get_vm_by_slug(db, vslug)
            if existing_vm is None:
                device = _device_by_site_name(db, vm.get("site_slug"), vm.get("device_name"))
                existing_vm = plat_svc.create_vm(
                    db,
                    cluster,
                    PlatformVirtualMachineCreate(
                        name=vm.get("name") or vslug,
                        slug=vslug,
                        device_id=device.id if device is not None else None,
                        status=vm.get("status") or "planned",
                    ),
                )
            for iface in vm.get("interfaces") or []:
                islug = str(iface.get("slug") or "").strip()
                if not islug or plat_svc.get_vif_by_slug(db, islug) is not None:
                    continue
                plat_svc.create_vif(
                    db,
                    cluster,
                    existing_vm,
                    PlatformVirtualInterfaceCreate(
                        name=iface.get("name") or islug,
                        slug=islug,
                        status=iface.get("status") or "planned",
                    ),
                )
            for disk in vm.get("disks") or []:
                dslug = str(disk.get("slug") or "").strip()
                if not dslug or plat_svc.get_disk_by_slug(db, dslug) is not None:
                    continue
                pool = plat_svc.get_storage_pool_by_slug(db, disk["storage_pool_slug"]) if disk.get("storage_pool_slug") else None
                plat_svc.create_disk(
                    db,
                    cluster,
                    existing_vm,
                    PlatformVirtualDiskCreate(
                        name=disk.get("name") or dslug,
                        slug=dslug,
                        kind=disk.get("kind") or "other",
                        status=disk.get("status") or "planned",
                        storage_pool_id=pool.id if pool is not None else None,
                    ),
                )


def _bind_vif_ipv4(db: Session, doc: dict[str, Any]) -> None:
    changed = False
    for ipam in doc.get("ipam") or []:
        site_slug = (ipam.get("site") or {}).get("slug")
        site = _site_by_slug(db, site_slug) if site_slug else None
        if site is None:
            continue
        for a in ipam.get("addresses") or []:
            vif_slug = str(a.get("virtual_interface_slug") or "").strip()
            address = str(a.get("address") or "").strip()
            if not vif_slug or not address:
                continue
            vif = plat_svc.get_vif_by_slug(db, vif_slug)
            row = _ipv4_on_site(db, site.id, address)
            if vif is None or row is None:
                continue
            if row.virtual_interface_id != vif.id:
                row.virtual_interface_id = vif.id
                changed = True
    if changed:
        db.commit()


def _apply_catalog(db: Session, doc: dict[str, Any]) -> None:
    for tpl in doc.get("catalog_templates") or []:
        slug = str(tpl.get("slug") or "").strip()
        if not slug:
            continue
        cat_svc.ensure_template(
            db,
            slug=slug,
            name=tpl.get("name") or slug,
            description=tpl.get("description"),
            versions=list(tpl.get("versions") or []),
        )
    for inst in doc.get("catalog_instances") or []:
        slug = str(inst.get("slug") or "").strip()
        if not slug or cat_svc.get_instance_by_slug(db, slug) is not None:
            continue
        tpl = cat_svc.get_template_by_slug(db, str(inst.get("template_slug") or "").strip())
        if tpl is None:
            continue
        wanted = str(inst.get("template_version") or "").strip()
        version = next((v for v in tpl.versions if v.version == wanted), None) if wanted else None
        if version is None and tpl.versions:
            version = sorted(tpl.versions, key=lambda v: v.id)[0]
        if version is None:
            continue
        device = _device_by_site_name(db, inst.get("site_slug"), inst.get("device_name"))
        cluster = plat_svc.get_cluster_by_slug(db, inst["cluster_slug"]) if inst.get("cluster_slug") else None
        vm = plat_svc.get_vm_by_slug(db, inst["vm_slug"]) if inst.get("vm_slug") else None
        pool = plat_svc.get_storage_pool_by_slug(db, inst["storage_pool_slug"]) if inst.get("storage_pool_slug") else None
        iface = plat_svc.get_vif_by_slug(db, inst["virtual_interface_slug"]) if inst.get("virtual_interface_slug") else None
        disk = plat_svc.get_disk_by_slug(db, inst["virtual_disk_slug"]) if inst.get("virtual_disk_slug") else None
        cloud = plat_svc.get_cloud_by_slug(db, inst["cloud_subscription_slug"]) if inst.get("cloud_subscription_slug") else None
        artifact = (
            dcim_svc.get_device_artifact_by_slug(db, str(inst.get("artifact_slug") or "").strip().lower())
            if inst.get("artifact_slug")
            else None
        )
        addr = None
        if inst.get("ipv4_address") and inst.get("site_slug"):
            site = _site_by_slug(db, inst["site_slug"])
            if site is not None:
                addr = _ipv4_on_site(db, site.id, str(inst["ipv4_address"]))
        cat_svc.import_instance(
            db,
            slug=slug,
            name=inst.get("name") or slug,
            status=inst.get("status") or "active",
            template_version=version,
            device_id=device.id if device is not None else None,
            cluster_id=cluster.id if cluster is not None else None,
            vm_id=vm.id if vm is not None else None,
            storage_pool_id=pool.id if pool is not None else None,
            virtual_interface_id=iface.id if iface is not None else None,
            virtual_disk_id=disk.id if disk is not None else None,
            cloud_subscription_id=cloud.id if cloud is not None else None,
            artifact_id=artifact.id if artifact is not None else None,
            ipv4_address_id=addr.id if addr is not None else None,
        )
