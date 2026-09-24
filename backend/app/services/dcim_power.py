"""Strøm og kabling. Ingen oppdiktede måleverdier. Elektrisk kurs ≠ IPAM-samband."""

from __future__ import annotations

import re
from typing import Any

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.dcim import (
    Cable,
    CableTermination,
    FiberBundle,
    FiberBundleMember,
    FiberStrand,
    DeviceInstance,
    DeviceInterface,
    DeviceModelTemplate,
    DevicePort,
    PowerCircuit,
    PowerFeed,
    PowerPanel,
    PowerSource,
    Rack,
    Room,
    Site,
)
from app.schemas.dcim import (
    CableCreate,
    FIBER_CABLE_TYPES,
    FiberBundleCreate,
    FiberBundleMemberCreate,
    FiberBundleMemberRead,
    FiberBundleRead,
    FiberStrandCreate,
    FiberStrandRead,
    FiberStrandUpdate,
    CablePathHop,
    CablePathRead,
    CableRead,
    CableTerminationIn,
    CableTerminationRead,
    DevicePortCreate,
    DevicePortRead,
    DevicePortUpdate,
    PowerCircuitCreate,
    PowerCircuitRead,
    PowerFeedCreate,
    PowerFeedRead,
    PowerPanelCreate,
    PowerPanelRead,
    PowerSourceCreate,
    PowerSourceRead,
)
from app.services import dcim as dcim_svc

_KIND_FROM_TEMPLATE = {
    "power-ports": "power-port",
    "power-outlets": "power-outlet",
    "front-ports": "front-port",
    "rear-ports": "rear-port",
}


def _slugify(value: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", (value or "").strip().lower()).strip("-")
    return (s or "item")[:128]


def _unique_slug(
    db: Session,
    model: type,
    site_or_parent_col: Any,
    parent_id: int,
    desired: str,
    *,
    explicit: bool = False,
) -> str:
    base = _slugify(desired)
    if explicit:
        taken = db.execute(select(model.id).where(site_or_parent_col == parent_id, model.slug == base)).scalar_one_or_none()
        if taken is not None:
            raise HTTPException(status_code=409, detail="slug finnes allerede")
        return base
    candidate = base
    n = 2
    while True:
        q = select(model.id).where(site_or_parent_col == parent_id, model.slug == candidate)
        if db.execute(q).scalar_one_or_none() is None:
            return candidate
        candidate = f"{base}-{n}"[:128]
        n += 1


def _require_site(db: Session, site_id: int) -> Site:
    row = db.get(Site, site_id)
    if row is None:
        raise HTTPException(status_code=404, detail="site ikke funnet")
    return row


def _require_room(db: Session, room_id: int, *, site_id: int) -> Room:
    row = db.get(Room, room_id)
    if row is None:
        raise HTTPException(status_code=404, detail="rom ikke funnet")
    if row.site_id != site_id:
        raise HTTPException(status_code=400, detail="rom tilhører en annen site")
    return row


def _require_rack(db: Session, rack_id: int) -> Rack:
    row = db.get(Rack, rack_id)
    if row is None:
        raise HTTPException(status_code=404, detail="rack ikke funnet")
    return row


def source_to_read(row: PowerSource) -> PowerSourceRead:
    return PowerSourceRead.model_validate(row)


def panel_to_read(row: PowerPanel) -> PowerPanelRead:
    return PowerPanelRead.model_validate(row)


def _require_source(db: Session, source_id: int, *, site_id: int) -> PowerSource:
    row = db.get(PowerSource, source_id)
    if row is None:
        raise HTTPException(status_code=404, detail="strømkilde ikke funnet")
    if row.site_id != site_id:
        raise HTTPException(status_code=400, detail="strømkilden tilhører en annen site")
    return row


def list_sources(db: Session, *, site_id: int | None = None) -> list[PowerSource]:
    q = select(PowerSource).order_by(PowerSource.name)
    if site_id is not None:
        q = q.where(PowerSource.site_id == site_id)
    return list(db.execute(q).scalars().all())


def create_source(db: Session, data: PowerSourceCreate) -> PowerSource:
    _require_site(db, data.site_id)
    device_id = data.device_id
    if data.kind == "ups-device":
        if device_id is None:
            raise HTTPException(status_code=400, detail="ups-device krever device_id")
        device = dcim_svc.get_device(db, device_id)
        if device is None:
            raise HTTPException(status_code=404, detail="enhet ikke funnet")
        site = dcim_svc.device_effective_site_id(db, device.id)
        if site is None:
            device.site_id = data.site_id
            site = data.site_id
        elif int(site) != data.site_id:
            raise HTTPException(status_code=400, detail="enhetens site stemmer ikke med kildens site")
    elif device_id is not None:
        raise HTTPException(status_code=400, detail="device_id er bare lov når kind er ups-device")
    row = PowerSource(
        site_id=data.site_id,
        name=data.name.strip(),
        slug=_unique_slug(
            db, PowerSource, PowerSource.site_id, data.site_id, data.slug or data.name, explicit=data.slug is not None
        ),
        kind=data.kind,
        device_id=device_id,
        description=data.description,
    )
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="kilde-slug finnes allerede på siten")
    db.refresh(row)
    return row


def get_source(db: Session, source_id: int) -> PowerSource | None:
    return db.get(PowerSource, source_id)


def delete_source(db: Session, row: PowerSource) -> None:
    for panel in db.execute(select(PowerPanel).where(PowerPanel.source_id == row.id)).scalars().all():
        panel.source_id = None
    db.delete(row)
    db.commit()


def circuit_to_read(row: PowerCircuit) -> PowerCircuitRead:
    return PowerCircuitRead.model_validate(row)


def feed_to_read(db: Session, row: PowerFeed) -> PowerFeedRead:
    circuit = db.get(PowerCircuit, row.circuit_id)
    panel = db.get(PowerPanel, circuit.panel_id) if circuit is not None else None
    rack = db.get(Rack, row.rack_id) if row.rack_id is not None else None
    return PowerFeedRead.model_validate(row).model_copy(
        update={
            "panel_name": panel.name if panel is not None else None,
            "circuit_name": circuit.name if circuit is not None else None,
            "rack_name": rack.name if rack is not None else None,
        },
    )


def port_to_read(row: DevicePort) -> DevicePortRead:
    return DevicePortRead.model_validate(row)


def _term_label(db: Session, object_type: str, object_id: int) -> str:
    if object_type == "power-feed":
        feed = db.get(PowerFeed, object_id)
        return f"feed:{feed.name}" if feed is not None else f"feed:{object_id}"
    if object_type == "device-port":
        port = db.get(DevicePort, object_id)
        if port is None:
            return f"port:{object_id}"
        dev = db.get(DeviceInstance, port.device_id)
        return f"{dev.name if dev else object_id}:{port.kind}:{port.name}"
    if object_type == "interface":
        iface = db.get(DeviceInterface, object_id)
        if iface is None:
            return f"iface:{object_id}"
        dev = db.get(DeviceInstance, iface.device_id)
        return f"{dev.name if dev else object_id}:iface:{iface.name}"
    return f"{object_type}:{object_id}"


def cable_to_read(db: Session, row: Cable) -> CableRead:
    terms = list(db.execute(select(CableTermination).where(CableTermination.cable_id == row.id)).scalars().all())
    return CableRead(
        id=row.id,
        site_id=row.site_id,
        name=row.name,
        slug=row.slug,
        cable_type=row.cable_type,
        status=row.status,
        color=row.color,
        length_m=row.length_m,
        description=row.description,
        created_at=row.created_at,
        terminations=[
            CableTerminationRead(
                id=t.id,
                cable_id=t.cable_id,
                end=t.end,
                object_type=t.object_type,
                object_id=t.object_id,
                label=_term_label(db, t.object_type, t.object_id),
            )
            for t in sorted(terms, key=lambda x: x.end)
        ],
    )


def list_panels(db: Session, *, site_id: int | None = None, room_id: int | None = None) -> list[PowerPanel]:
    q = select(PowerPanel).order_by(PowerPanel.name)
    if site_id is not None:
        q = q.where(PowerPanel.site_id == site_id)
    if room_id is not None:
        q = q.where(PowerPanel.room_id == room_id)
    return list(db.execute(q).scalars().all())


def create_panel(db: Session, data: PowerPanelCreate) -> PowerPanel:
    _require_site(db, data.site_id)
    if data.room_id is not None:
        _require_room(db, data.room_id, site_id=data.site_id)
    if data.source_id is not None:
        _require_source(db, data.source_id, site_id=data.site_id)
    row = PowerPanel(
        site_id=data.site_id,
        room_id=data.room_id,
        source_id=data.source_id,
        name=data.name.strip(),
        slug=_unique_slug(
            db, PowerPanel, PowerPanel.site_id, data.site_id, data.slug or data.name, explicit=data.slug is not None
        ),
        description=data.description,
    )
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="tavle-slug finnes allerede på siten")
    db.refresh(row)
    return row


def get_panel(db: Session, panel_id: int) -> PowerPanel | None:
    return db.get(PowerPanel, panel_id)


def delete_panel(db: Session, row: PowerPanel) -> None:
    db.delete(row)
    db.commit()


def list_circuits(db: Session, *, panel_id: int | None = None, site_id: int | None = None) -> list[PowerCircuit]:
    q = select(PowerCircuit).order_by(PowerCircuit.name)
    if panel_id is not None:
        q = q.where(PowerCircuit.panel_id == panel_id)
    if site_id is not None:
        q = q.join(PowerPanel, PowerPanel.id == PowerCircuit.panel_id).where(PowerPanel.site_id == site_id)
    return list(db.execute(q).scalars().all())


def create_circuit(db: Session, data: PowerCircuitCreate) -> PowerCircuit:
    if db.get(PowerPanel, data.panel_id) is None:
        raise HTTPException(status_code=404, detail="tavle ikke funnet")
    row = PowerCircuit(
        panel_id=data.panel_id,
        name=data.name.strip(),
        breaker_label=(data.breaker_label or "").strip() or None,
        rating_amps=data.rating_amps,
        voltage=data.voltage,
        description=data.description,
    )
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="kursnavn finnes allerede på tavlen")
    db.refresh(row)
    return row


def get_circuit(db: Session, circuit_id: int) -> PowerCircuit | None:
    return db.get(PowerCircuit, circuit_id)


def delete_circuit(db: Session, row: PowerCircuit) -> None:
    db.delete(row)
    db.commit()


def list_feeds(
    db: Session,
    *,
    site_id: int | None = None,
    circuit_id: int | None = None,
    rack_id: int | None = None,
    room_id: int | None = None,
) -> list[PowerFeed]:
    q = select(PowerFeed).order_by(PowerFeed.name)
    if circuit_id is not None:
        q = q.where(PowerFeed.circuit_id == circuit_id)
    if rack_id is not None:
        q = q.where(PowerFeed.rack_id == rack_id)
    if site_id is not None or room_id is not None:
        q = q.join(PowerCircuit, PowerCircuit.id == PowerFeed.circuit_id).join(PowerPanel, PowerPanel.id == PowerCircuit.panel_id)
        if site_id is not None:
            q = q.where(PowerPanel.site_id == site_id)
        if room_id is not None:
            q = q.where(PowerPanel.room_id == room_id)
    return list(db.execute(q).scalars().all())


def create_feed(db: Session, data: PowerFeedCreate) -> PowerFeed:
    circuit = db.get(PowerCircuit, data.circuit_id)
    if circuit is None:
        raise HTTPException(status_code=404, detail="kurs ikke funnet")
    if data.rack_id is not None:
        rack = _require_rack(db, data.rack_id)
        panel = db.get(PowerPanel, circuit.panel_id)
        room = db.get(Room, rack.room_id)
        if panel is None or room is None or room.site_id != panel.site_id:
            raise HTTPException(status_code=400, detail="rack tilhører en annen site enn tavlen")
    row = PowerFeed(
        circuit_id=data.circuit_id,
        name=data.name.strip(),
        slug=_unique_slug(
            db, PowerFeed, PowerFeed.circuit_id, data.circuit_id, data.slug or data.name, explicit=data.slug is not None
        ),
        rack_id=data.rack_id,
        status=data.status,
        supply=data.supply,
        phase=data.phase,
        description=data.description,
    )
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="feed-slug finnes allerede på kursen")
    db.refresh(row)
    return row


def get_feed(db: Session, feed_id: int) -> PowerFeed | None:
    return db.get(PowerFeed, feed_id)


def delete_feed(db: Session, row: PowerFeed) -> None:
    _delete_cables_for(db, "power-feed", row.id)
    db.delete(row)
    db.commit()


def list_ports(db: Session, *, device_id: int | None = None, kind: str | None = None) -> list[DevicePort]:
    q = select(DevicePort).order_by(DevicePort.kind, DevicePort.name)
    if device_id is not None:
        q = q.where(DevicePort.device_id == device_id)
    if kind is not None:
        q = q.where(DevicePort.kind == kind)
    return list(db.execute(q).scalars().all())


def create_port(db: Session, device_id: int, data: DevicePortCreate) -> DevicePort:
    if db.get(DeviceInstance, device_id) is None:
        raise HTTPException(status_code=404, detail="enhet ikke funnet")
    rear_id = data.rear_port_id
    power_id = data.power_port_id
    if rear_id is not None:
        rear = db.get(DevicePort, rear_id)
        if rear is None or rear.device_id != device_id or rear.kind != "rear-port":
            raise HTTPException(status_code=400, detail="rear_port må være en bakport på samme enhet")
    if power_id is not None:
        inlet = db.get(DevicePort, power_id)
        if inlet is None or inlet.device_id != device_id or inlet.kind != "power-port":
            raise HTTPException(status_code=400, detail="power_port må være en strøminngang på samme enhet")
    row = DevicePort(
        device_id=device_id,
        kind=data.kind,
        name=data.name.strip(),
        label=(data.label or "").strip() or None,
        connector=(data.connector or "").strip() or None,
        rear_port_id=rear_id,
        power_port_id=power_id,
    )
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="portnavn finnes allerede på enheten")
    db.refresh(row)
    return row


def get_port(db: Session, port_id: int) -> DevicePort | None:
    return db.get(DevicePort, port_id)


def update_port(db: Session, row: DevicePort, data: DevicePortUpdate) -> DevicePort:
    changed = False
    if "rear_port_id" in data.model_fields_set:
        rear_id = data.rear_port_id
        if rear_id is None:
            row.rear_port_id = None
        else:
            if row.kind != "front-port":
                raise HTTPException(
                    status_code=400,
                    detail={"code": "port_rear_kind", "detail": "bare front-port kan peke på bakport"},
                )
            if rear_id == row.id:
                raise HTTPException(
                    status_code=400,
                    detail={"code": "port_rear_same", "detail": "port kan ikke peke på seg selv"},
                )
            rear = db.get(DevicePort, rear_id)
            if rear is None or rear.device_id != row.device_id or rear.kind != "rear-port":
                raise HTTPException(
                    status_code=400,
                    detail={"code": "port_rear", "detail": "rear_port må være en bakport på samme enhet"},
                )
            row.rear_port_id = rear_id
        changed = True
    if "power_port_id" in data.model_fields_set:
        power_id = data.power_port_id
        if power_id is None:
            row.power_port_id = None
        else:
            if row.kind != "power-outlet":
                raise HTTPException(
                    status_code=400,
                    detail={"code": "port_power_kind", "detail": "bare power-outlet kan peke på strøminngang"},
                )
            if power_id == row.id:
                raise HTTPException(
                    status_code=400,
                    detail={"code": "port_power_same", "detail": "port kan ikke peke på seg selv"},
                )
            inlet = db.get(DevicePort, power_id)
            if inlet is None or inlet.device_id != row.device_id or inlet.kind != "power-port":
                raise HTTPException(
                    status_code=400,
                    detail={"code": "port_power", "detail": "power_port må være en strøminngang på samme enhet"},
                )
            row.power_port_id = power_id
        changed = True
    if changed:
        db.commit()
        db.refresh(row)
    return row


def delete_port(db: Session, row: DevicePort) -> None:
    _delete_cables_for(db, "device-port", row.id)
    db.delete(row)
    db.commit()


def copy_ports_from_templates(db: Session, device_id: int) -> list[DevicePort]:
    device = db.get(DeviceInstance, device_id)
    if device is None:
        raise HTTPException(status_code=404, detail="enhet ikke funnet")
    if device.device_model_id is None:
        raise HTTPException(status_code=400, detail="enheten har ingen modell")
    templates = list(
        db.execute(
            select(DeviceModelTemplate)
            .where(DeviceModelTemplate.device_model_id == device.device_model_id)
            .where(DeviceModelTemplate.component_type.in_(tuple(_KIND_FROM_TEMPLATE)))
            .order_by(DeviceModelTemplate.sort_order, DeviceModelTemplate.name),
        ).scalars().all(),
    )
    existing = {(p.kind, p.name) for p in list_ports(db, device_id=device_id)}
    created: list[DevicePort] = []
    by_name: dict[tuple[str, str], DevicePort] = {
        (p.kind, p.name): p for p in list_ports(db, device_id=device_id)
    }
    for tpl in templates:
        kind = _KIND_FROM_TEMPLATE[tpl.component_type]
        if kind in {"rear-port", "power-port"} and (kind, tpl.name) not in existing:
            created.append(
                create_port(
                    db,
                    device_id,
                    DevicePortCreate(
                        kind=kind,
                        name=tpl.name,
                        label=tpl.label,
                        connector=(tpl.normalized_json or {}).get("connector_type"),
                    ),
                ),
            )
            by_name[(kind, tpl.name)] = created[-1]
            existing.add((kind, tpl.name))
    for tpl in templates:
        kind = _KIND_FROM_TEMPLATE[tpl.component_type]
        if kind not in {"front-port", "power-outlet"} or (kind, tpl.name) in existing:
            continue
        norm = tpl.normalized_json or {}
        rear_id = None
        power_id = None
        if kind == "front-port" and norm.get("rear_port"):
            rear = by_name.get(("rear-port", str(norm["rear_port"])))
            rear_id = rear.id if rear is not None else None
        if kind == "power-outlet" and norm.get("power_port"):
            inlet = by_name.get(("power-port", str(norm["power_port"])))
            power_id = inlet.id if inlet is not None else None
        created.append(
            create_port(
                db,
                device_id,
                DevicePortCreate(
                    kind=kind,
                    name=tpl.name,
                    label=tpl.label,
                    connector=norm.get("connector_type"),
                    rear_port_id=rear_id,
                    power_port_id=power_id,
                ),
            ),
        )
        existing.add((kind, tpl.name))
    return created


def _resolve_term(db: Session, term: CableTerminationIn) -> None:
    if term.object_type == "power-feed":
        if db.get(PowerFeed, term.object_id) is None:
            raise HTTPException(status_code=404, detail="power feed ikke funnet")
        return
    if term.object_type == "device-port":
        if db.get(DevicePort, term.object_id) is None:
            raise HTTPException(status_code=404, detail="port ikke funnet")
        return
    if db.get(DeviceInterface, term.object_id) is None:
        raise HTTPException(status_code=404, detail="grensesnitt ikke funnet")


def _term_taken(db: Session, object_type: str, object_id: int) -> bool:
    return (
        db.execute(
            select(CableTermination.id).where(
                CableTermination.object_type == object_type,
                CableTermination.object_id == object_id,
            ),
        ).scalar_one_or_none()
        is not None
    )


def list_cables(db: Session, *, site_id: int | None = None, device_id: int | None = None) -> list[Cable]:
    if device_id is not None:
        port_ids = [p.id for p in list_ports(db, device_id=device_id)]
        iface_ids = [
            i.id
            for i in db.execute(select(DeviceInterface.id).where(DeviceInterface.device_id == device_id)).scalars().all()
        ]
        term_q = select(CableTermination.cable_id)
        clauses = []
        if port_ids:
            clauses.append(
                (CableTermination.object_type == "device-port") & CableTermination.object_id.in_(port_ids),
            )
        if iface_ids:
            clauses.append(
                (CableTermination.object_type == "interface") & CableTermination.object_id.in_(iface_ids),
            )
        if not clauses:
            return []
        from sqlalchemy import or_

        cable_ids = list(db.execute(term_q.where(or_(*clauses))).scalars().all())
        if not cable_ids:
            return []
        q = select(Cable).where(Cable.id.in_(cable_ids)).order_by(Cable.name)
        if site_id is not None:
            q = q.where(Cable.site_id == site_id)
        return list(db.execute(q).scalars().all())
    q = select(Cable).order_by(Cable.name)
    if site_id is not None:
        q = q.where(Cable.site_id == site_id)
    return list(db.execute(q).scalars().all())


def create_cable(db: Session, data: CableCreate) -> Cable:
    _require_site(db, data.site_id)
    if data.a.object_type == data.z.object_type and data.a.object_id == data.z.object_id:
        raise HTTPException(status_code=400, detail="kabelen kan ikke terminere mot samme objekt to ganger")
    _resolve_term(db, data.a)
    _resolve_term(db, data.z)
    if _term_taken(db, data.a.object_type, data.a.object_id) or _term_taken(db, data.z.object_type, data.z.object_id):
        raise HTTPException(status_code=409, detail="enden er allerede kablet")
    row = Cable(
        site_id=data.site_id,
        name=data.name.strip(),
        slug=_unique_slug(
            db, Cable, Cable.site_id, data.site_id, data.slug or data.name, explicit=data.slug is not None
        ),
        cable_type=data.cable_type,
        status=data.status,
        color=(data.color or "").strip() or None,
        length_m=data.length_m,
        description=data.description,
    )
    db.add(row)
    db.flush()
    db.add(CableTermination(cable_id=row.id, end="a", object_type=data.a.object_type, object_id=data.a.object_id))
    db.add(CableTermination(cable_id=row.id, end="z", object_type=data.z.object_type, object_id=data.z.object_id))
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="kabel-slug eller terminering finnes allerede")
    db.refresh(row)
    return row


def get_cable(db: Session, cable_id: int) -> Cable | None:
    return db.get(Cable, cable_id)


def delete_cable(db: Session, row: Cable) -> None:
    for b in list(db.execute(select(FiberBundle).where(FiberBundle.cable_id == row.id)).scalars().all()):
        for m in list(db.execute(select(FiberBundleMember).where(FiberBundleMember.bundle_id == b.id)).scalars().all()):
            db.delete(m)
        db.delete(b)
    for s in list(db.execute(select(FiberStrand).where(FiberStrand.cable_id == row.id)).scalars().all()):
        db.delete(s)
    db.delete(row)
    db.commit()


def list_fiber_strands(db: Session, cable_id: int) -> list[FiberStrand]:
    return list(
        db.execute(select(FiberStrand).where(FiberStrand.cable_id == cable_id).order_by(FiberStrand.position)).scalars().all()
    )


def get_fiber_strand(db: Session, strand_id: int) -> FiberStrand | None:
    return db.get(FiberStrand, strand_id)


def get_fiber_strand_by_position(db: Session, cable_id: int, position: int) -> FiberStrand | None:
    return db.execute(
        select(FiberStrand).where(FiberStrand.cable_id == cable_id, FiberStrand.position == position),
    ).scalar_one_or_none()


def create_fiber_strand(db: Session, cable: Cable, data: FiberStrandCreate) -> FiberStrand:
    if cable.cable_type not in FIBER_CABLE_TYPES:
        raise HTTPException(status_code=400, detail="kabelen er ikke fiber")
    if get_fiber_strand_by_position(db, cable.id, data.position) is not None:
        raise HTTPException(status_code=409, detail="fiberposisjon finnes allerede")
    row = FiberStrand(
        cable_id=cable.id,
        position=data.position,
        label=data.label.strip() if data.label else None,
        status=data.status,
    )
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="fiberposisjon finnes allerede")
    db.refresh(row)
    return row


def update_fiber_strand(db: Session, row: FiberStrand, data: FiberStrandUpdate) -> FiberStrand:
    if data.label is not None:
        row.label = data.label.strip() if data.label else None
    if data.status is not None:
        row.status = data.status
    db.commit()
    db.refresh(row)
    return row


def delete_fiber_strand(db: Session, row: FiberStrand) -> None:
    from app.models.ipam import IpamCircuitStrand

    for m in list(db.execute(select(FiberBundleMember).where(FiberBundleMember.strand_id == row.id)).scalars().all()):
        db.delete(m)
    for b in list(db.execute(select(IpamCircuitStrand).where(IpamCircuitStrand.strand_id == row.id)).scalars().all()):
        db.delete(b)
    db.delete(row)
    db.commit()


def fiber_strand_to_read(row: FiberStrand) -> FiberStrandRead:
    return FiberStrandRead.model_validate(row)


def list_fiber_bundles(db: Session, cable_id: int) -> list[FiberBundle]:
    return list(
        db.execute(select(FiberBundle).where(FiberBundle.cable_id == cable_id).order_by(FiberBundle.slug)).scalars().all()
    )


def get_fiber_bundle(db: Session, bundle_id: int) -> FiberBundle | None:
    return db.get(FiberBundle, bundle_id)


def get_fiber_bundle_by_slug(db: Session, cable_id: int, slug: str) -> FiberBundle | None:
    return db.execute(
        select(FiberBundle).where(FiberBundle.cable_id == cable_id, FiberBundle.slug == slug),
    ).scalar_one_or_none()


def get_fiber_bundle_member(db: Session, member_id: int) -> FiberBundleMember | None:
    return db.get(FiberBundleMember, member_id)


def get_bundle_member_for_strand(db: Session, strand_id: int) -> FiberBundleMember | None:
    return db.execute(
        select(FiberBundleMember).where(FiberBundleMember.strand_id == strand_id),
    ).scalar_one_or_none()


def create_fiber_bundle(db: Session, cable: Cable, data: FiberBundleCreate) -> FiberBundle:
    if cable.cable_type not in FIBER_CABLE_TYPES:
        raise HTTPException(status_code=400, detail="kabelen er ikke fiber")
    slug = _unique_slug(
        db,
        FiberBundle,
        FiberBundle.cable_id,
        cable.id,
        data.slug or data.name,
        explicit=data.slug is not None,
    )
    row = FiberBundle(
        cable_id=cable.id,
        name=data.name.strip(),
        slug=slug,
        description=data.description.strip() if data.description else None,
    )
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="fiberbunt finnes allerede")
    db.refresh(row)
    return row


def add_fiber_bundle_member(db: Session, bundle: FiberBundle, data: FiberBundleMemberCreate) -> FiberBundleMember:
    strand = get_fiber_strand(db, data.strand_id)
    if strand is None:
        raise HTTPException(status_code=404, detail="fiber ikke funnet")
    if strand.cable_id != bundle.cable_id:
        raise HTTPException(status_code=400, detail="strengen tilhører en annen kabel")
    if get_bundle_member_for_strand(db, strand.id) is not None:
        raise HTTPException(status_code=409, detail="fiber_bundle_member_taken")
    row = FiberBundleMember(bundle_id=bundle.id, strand_id=strand.id)
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="fiber_bundle_member_taken")
    db.refresh(row)
    return row


def delete_fiber_bundle(db: Session, row: FiberBundle) -> None:
    for m in list(db.execute(select(FiberBundleMember).where(FiberBundleMember.bundle_id == row.id)).scalars().all()):
        db.delete(m)
    db.delete(row)
    db.commit()


def delete_fiber_bundle_member(db: Session, row: FiberBundleMember) -> None:
    db.delete(row)
    db.commit()


def fiber_bundle_to_read(db: Session, row: FiberBundle) -> FiberBundleRead:
    members = list(
        db.execute(
            select(FiberBundleMember).where(FiberBundleMember.bundle_id == row.id),
        ).scalars().all()
    )
    items: list[FiberBundleMemberRead] = []
    for m in members:
        strand = db.get(FiberStrand, m.strand_id)
        if strand is None:
            continue
        items.append(
            FiberBundleMemberRead(
                id=m.id,
                strand_id=m.strand_id,
                position=strand.position,
                label=strand.label,
            )
        )
    items.sort(key=lambda x: x.position)
    return FiberBundleRead(
        id=row.id,
        cable_id=row.cable_id,
        name=row.name,
        slug=row.slug,
        description=row.description,
        members=items,
        created_at=row.created_at,
    )


def _delete_cables_for(db: Session, object_type: str, object_id: int) -> None:
    terms = list(
        db.execute(
            select(CableTermination).where(
                CableTermination.object_type == object_type,
                CableTermination.object_id == object_id,
            ),
        ).scalars().all(),
    )
    for t in terms:
        cable = db.get(Cable, t.cable_id)
        if cable is not None:
            db.delete(cable)


def _find_term(db: Session, object_type: str, object_id: int) -> CableTermination | None:
    return db.execute(
        select(CableTermination).where(
            CableTermination.object_type == object_type,
            CableTermination.object_id == object_id,
        ),
    ).scalar_one_or_none()


def _other_end(db: Session, term: CableTermination) -> CableTermination | None:
    other = "z" if term.end == "a" else "a"
    return db.execute(
        select(CableTermination).where(CableTermination.cable_id == term.cable_id, CableTermination.end == other),
    ).scalar_one_or_none()


def _internal_peer(db: Session, object_type: str, object_id: int) -> tuple[str, int] | None:
    if object_type != "device-port":
        return None
    port = db.get(DevicePort, object_id)
    if port is None:
        return None
    if port.kind == "front-port" and port.rear_port_id is not None:
        return "device-port", port.rear_port_id
    if port.kind == "rear-port":
        fronts = list(
            db.execute(
                select(DevicePort).where(DevicePort.rear_port_id == port.id, DevicePort.kind == "front-port"),
            ).scalars().all(),
        )
        if len(fronts) == 1:
            return "device-port", fronts[0].id
    if port.kind == "power-outlet" and port.power_port_id is not None:
        return "device-port", port.power_port_id
    return None


def trace_path(db: Session, object_type: str, object_id: int) -> CablePathRead:
    hops: list[CablePathHop] = []
    seen: set[tuple[str, int]] = set()
    current: tuple[str, int] | None = (object_type, object_id)
    via: str | None = None
    came_via_cable_id: int | None = None
    while current is not None and current not in seen:
        seen.add(current)
        hops.append(
            CablePathHop(
                object_type=current[0],
                object_id=current[1],
                label=_term_label(db, current[0], current[1]),
                via=via,
            ),
        )
        if came_via_cable_id is not None:
            peer = _internal_peer(db, current[0], current[1])
            if peer is not None and peer not in seen:
                via = "internal"
                came_via_cable_id = None
                current = peer
                continue
        term = _find_term(db, current[0], current[1])
        if term is not None and term.cable_id != came_via_cable_id:
            other = _other_end(db, term)
            if other is None:
                break
            cable = db.get(Cable, term.cable_id)
            via = cable.name if cable is not None else f"cable:{term.cable_id}"
            came_via_cable_id = term.cable_id
            current = (other.object_type, other.object_id)
            continue
        peer = _internal_peer(db, current[0], current[1])
        if peer is None or peer in seen:
            break
        via = "internal"
        came_via_cable_id = None
        current = peer
    return CablePathRead(hops=hops)


def export_for_sites(db: Session, sites: list[Site]) -> dict[str, Any]:
    site_ids = [s.id for s in sites]
    site_by_id = {s.id: s for s in sites}
    if not site_ids:
        return {
            "power_sources": [],
            "power_panels": [],
            "power_circuits": [],
            "power_feeds": [],
            "device_ports": [],
            "cables": [],
            "fiber_strands": [],
            "fiber_bundles": [],
        }
    sources = list(db.execute(select(PowerSource).where(PowerSource.site_id.in_(site_ids))).scalars().all())
    source_by_id = {s.id: s for s in sources}
    panels = list(db.execute(select(PowerPanel).where(PowerPanel.site_id.in_(site_ids))).scalars().all())
    panel_by_id = {p.id: p for p in panels}
    circuits = (
        list(db.execute(select(PowerCircuit).where(PowerCircuit.panel_id.in_(panel_by_id))).scalars().all())
        if panel_by_id
        else []
    )
    circuit_by_id = {c.id: c for c in circuits}
    feeds = (
        list(db.execute(select(PowerFeed).where(PowerFeed.circuit_id.in_(circuit_by_id))).scalars().all())
        if circuit_by_id
        else []
    )
    rooms = list(db.execute(select(Room).where(Room.site_id.in_(site_ids))).scalars().all())
    room_by_id = {r.id: r for r in rooms}
    racks = list(db.execute(select(Rack).where(Rack.room_id.in_(room_by_id))).scalars().all()) if room_by_id else []
    rack_by_id = {k.id: k for k in racks}
    devices = list(db.execute(select(DeviceInstance).where(DeviceInstance.site_id.in_(site_ids))).scalars().all())
    device_by_id = {d.id: d for d in devices}
    ports = (
        list(db.execute(select(DevicePort).where(DevicePort.device_id.in_(device_by_id))).scalars().all())
        if device_by_id
        else []
    )
    port_by_id = {p.id: p for p in ports}
    cables = list(db.execute(select(Cable).where(Cable.site_id.in_(site_ids))).scalars().all())
    cable_by_id = {c.id: c for c in cables}
    strands = (
        list(db.execute(select(FiberStrand).where(FiberStrand.cable_id.in_(cable_by_id))).scalars().all())
        if cable_by_id
        else []
    )
    strand_by_id = {s.id: s for s in strands}
    bundles = (
        list(db.execute(select(FiberBundle).where(FiberBundle.cable_id.in_(cable_by_id))).scalars().all())
        if cable_by_id
        else []
    )
    bundle_by_id = {b.id: b for b in bundles}
    bundle_members = (
        list(db.execute(select(FiberBundleMember).where(FiberBundleMember.bundle_id.in_(bundle_by_id))).scalars().all())
        if bundle_by_id
        else []
    )
    members_by_bundle: dict[int, list[FiberBundleMember]] = {}
    for m in bundle_members:
        members_by_bundle.setdefault(m.bundle_id, []).append(m)
    terms = (
        list(db.execute(select(CableTermination).where(CableTermination.cable_id.in_({c.id for c in cables}))).scalars().all())
        if cables
        else []
    )
    terms_by_cable: dict[int, list[CableTermination]] = {}
    for t in terms:
        terms_by_cable.setdefault(t.cable_id, []).append(t)

    def _term_export(t: CableTermination) -> dict[str, Any]:
        out: dict[str, Any] = {"object_type": t.object_type, "end": t.end}
        if t.object_type == "power-feed":
            feed = db.get(PowerFeed, t.object_id)
            out["feed_slug"] = feed.slug if feed is not None else None
            circ = db.get(PowerCircuit, feed.circuit_id) if feed is not None else None
            panel = panel_by_id.get(circ.panel_id) if circ is not None else None
            out["panel_slug"] = panel.slug if panel is not None else None
            out["circuit_name"] = circ.name if circ is not None else None
        elif t.object_type == "device-port":
            port = port_by_id.get(t.object_id)
            dev = device_by_id.get(port.device_id) if port is not None else None
            out["device_name"] = dev.name if dev is not None else None
            out["port_kind"] = port.kind if port is not None else None
            out["port_name"] = port.name if port is not None else None
        elif t.object_type == "interface":
            iface = db.get(DeviceInterface, t.object_id)
            dev = device_by_id.get(iface.device_id) if iface is not None else None
            out["device_name"] = dev.name if dev is not None else None
            out["interface_name"] = iface.name if iface is not None else None
        return out

    return {
        "power_sources": [
            {
                "site_slug": site_by_id[s.site_id].slug,
                "name": s.name,
                "slug": s.slug,
                "kind": s.kind,
                "device_name": device_by_id[s.device_id].name if s.device_id and s.device_id in device_by_id else None,
            }
            for s in sources
        ],
        "power_panels": [
            {
                "site_slug": site_by_id[p.site_id].slug,
                "room_name": room_by_id[p.room_id].name if p.room_id and p.room_id in room_by_id else None,
                "source_slug": source_by_id[p.source_id].slug if p.source_id and p.source_id in source_by_id else None,
                "name": p.name,
                "slug": p.slug,
            }
            for p in panels
        ],
        "power_circuits": [
            {
                "panel_slug": panel_by_id[c.panel_id].slug if c.panel_id in panel_by_id else None,
                "site_slug": site_by_id[panel_by_id[c.panel_id].site_id].slug if c.panel_id in panel_by_id else None,
                "name": c.name,
                "breaker_label": c.breaker_label,
                "rating_amps": c.rating_amps,
                "voltage": c.voltage,
            }
            for c in circuits
        ],
        "power_feeds": [
            {
                "panel_slug": panel_by_id[circuit_by_id[f.circuit_id].panel_id].slug
                if f.circuit_id in circuit_by_id and circuit_by_id[f.circuit_id].panel_id in panel_by_id
                else None,
                "circuit_name": circuit_by_id[f.circuit_id].name if f.circuit_id in circuit_by_id else None,
                "name": f.name,
                "slug": f.slug,
                "rack_name": rack_by_id[f.rack_id].name if f.rack_id and f.rack_id in rack_by_id else None,
                "room_name": room_by_id[rack_by_id[f.rack_id].room_id].name
                if f.rack_id and f.rack_id in rack_by_id and rack_by_id[f.rack_id].room_id in room_by_id
                else None,
                "status": f.status,
                "supply": f.supply,
                "phase": f.phase,
            }
            for f in feeds
        ],
        "device_ports": [
            {
                "device_name": device_by_id[p.device_id].name if p.device_id in device_by_id else None,
                "kind": p.kind,
                "name": p.name,
                "label": p.label,
                "connector": p.connector,
                "rear_port_name": port_by_id[p.rear_port_id].name if p.rear_port_id and p.rear_port_id in port_by_id else None,
                "power_port_name": port_by_id[p.power_port_id].name if p.power_port_id and p.power_port_id in port_by_id else None,
            }
            for p in ports
        ],
        "cables": [
            {
                "site_slug": site_by_id[c.site_id].slug,
                "name": c.name,
                "slug": c.slug,
                "cable_type": c.cable_type,
                "status": c.status,
                "terminations": [_term_export(t) for t in terms_by_cable.get(c.id, [])],
            }
            for c in cables
        ],
        "fiber_strands": [
            {
                "site_slug": site_by_id[cable_by_id[s.cable_id].site_id].slug,
                "cable_slug": cable_by_id[s.cable_id].slug,
                "position": s.position,
                "label": s.label,
                "status": s.status,
            }
            for s in strands
            if s.cable_id in cable_by_id
        ],
        "fiber_bundles": [
            {
                "site_slug": site_by_id[cable_by_id[b.cable_id].site_id].slug,
                "cable_slug": cable_by_id[b.cable_id].slug,
                "slug": b.slug,
                "name": b.name,
                "description": b.description,
                "strand_positions": sorted(
                    strand_by_id[m.strand_id].position
                    for m in members_by_bundle.get(b.id, [])
                    if m.strand_id in strand_by_id
                ),
            }
            for b in bundles
            if b.cable_id in cable_by_id
        ],
    }


def apply_from_document(db: Session, doc: dict[str, Any], *, site_by_slug: dict[str, Site]) -> None:
    from app.models.dcim import Room as RoomModel

    for s in doc.get("power_sources") or []:
        slug = (s.get("slug") or "").strip()
        site = site_by_slug.get((s.get("site_slug") or "").strip())
        kind = (s.get("kind") or "").strip()
        if not slug or site is None or not kind:
            continue
        found = db.execute(
            select(PowerSource).where(PowerSource.site_id == site.id, PowerSource.slug == slug),
        ).scalar_one_or_none()
        if found is not None:
            continue
        device_id = None
        device_name = (s.get("device_name") or "").strip()
        if kind == "ups-device" and device_name:
            device = db.execute(
                select(DeviceInstance).where(DeviceInstance.site_id == site.id, DeviceInstance.name == device_name),
            ).scalar_one_or_none()
            device_id = device.id if device is not None else None
        if kind == "ups-device" and device_id is None:
            continue
        create_source(
            db,
            PowerSourceCreate(
                site_id=site.id,
                name=s.get("name") or slug,
                slug=slug,
                kind=kind,
                device_id=device_id,
            ),
        )

    for p in doc.get("power_panels") or []:
        slug = (p.get("slug") or "").strip()
        site = site_by_slug.get((p.get("site_slug") or "").strip())
        if not slug or site is None:
            continue
        found = db.execute(
            select(PowerPanel).where(PowerPanel.site_id == site.id, PowerPanel.slug == slug),
        ).scalar_one_or_none()
        if found is not None:
            continue
        room_id = None
        room_name = (p.get("room_name") or "").strip()
        if room_name:
            room = db.execute(
                select(RoomModel).where(RoomModel.site_id == site.id, RoomModel.name == room_name),
            ).scalar_one_or_none()
            room_id = room.id if room is not None else None
        source_id = None
        source_slug = (p.get("source_slug") or "").strip()
        if source_slug:
            src = db.execute(
                select(PowerSource).where(PowerSource.site_id == site.id, PowerSource.slug == source_slug),
            ).scalar_one_or_none()
            source_id = src.id if src is not None else None
        create_panel(
            db,
            PowerPanelCreate(
                site_id=site.id,
                room_id=room_id,
                source_id=source_id,
                name=p.get("name") or slug,
                slug=slug,
            ),
        )

    for c in doc.get("power_circuits") or []:
        site = site_by_slug.get((c.get("site_slug") or "").strip())
        panel_slug = (c.get("panel_slug") or "").strip()
        name = (c.get("name") or "").strip()
        if site is None or not panel_slug or not name:
            continue
        panel = db.execute(
            select(PowerPanel).where(PowerPanel.site_id == site.id, PowerPanel.slug == panel_slug),
        ).scalar_one_or_none()
        if panel is None:
            continue
        found = db.execute(
            select(PowerCircuit).where(PowerCircuit.panel_id == panel.id, PowerCircuit.name == name),
        ).scalar_one_or_none()
        if found is None:
            create_circuit(
                db,
                PowerCircuitCreate(
                    panel_id=panel.id,
                    name=name,
                    breaker_label=c.get("breaker_label"),
                    rating_amps=c.get("rating_amps"),
                    voltage=c.get("voltage"),
                ),
            )

    for f in doc.get("power_feeds") or []:
        slug = (f.get("slug") or "").strip()
        panel_slug = (f.get("panel_slug") or "").strip()
        circuit_name = (f.get("circuit_name") or "").strip()
        if not slug or not panel_slug or not circuit_name:
            continue
        panel = db.execute(select(PowerPanel).where(PowerPanel.slug == panel_slug)).scalars().first()
        if panel is None:
            continue
        circuit = db.execute(
            select(PowerCircuit).where(PowerCircuit.panel_id == panel.id, PowerCircuit.name == circuit_name),
        ).scalar_one_or_none()
        if circuit is None:
            continue
        found = db.execute(
            select(PowerFeed).where(PowerFeed.circuit_id == circuit.id, PowerFeed.slug == slug),
        ).scalar_one_or_none()
        if found is not None:
            continue
        rack_id = None
        rack_name = (f.get("rack_name") or "").strip()
        room_name = (f.get("room_name") or "").strip()
        if rack_name and room_name:
            room = db.execute(
                select(Room).where(Room.site_id == panel.site_id, Room.name == room_name),
            ).scalar_one_or_none()
            if room is not None:
                rack = db.execute(select(Rack).where(Rack.room_id == room.id, Rack.name == rack_name)).scalar_one_or_none()
                rack_id = rack.id if rack is not None else None
        create_feed(
            db,
            PowerFeedCreate(
                circuit_id=circuit.id,
                name=f.get("name") or slug,
                slug=slug,
                rack_id=rack_id,
                status=f.get("status") or "planned",
                supply=f.get("supply"),
                phase=f.get("phase"),
            ),
        )

    port_rows = list(doc.get("device_ports") or [])
    port_rows.sort(key=lambda p: 0 if (p.get("kind") or "") in {"rear-port", "power-port"} else 1)
    for p in port_rows:
        device_name = (p.get("device_name") or "").strip()
        kind = (p.get("kind") or "").strip()
        name = (p.get("name") or "").strip()
        if not device_name or not kind or not name:
            continue
        device = db.execute(select(DeviceInstance).where(DeviceInstance.name == device_name)).scalars().first()
        if device is None:
            continue
        found = db.execute(
            select(DevicePort).where(DevicePort.device_id == device.id, DevicePort.kind == kind, DevicePort.name == name),
        ).scalar_one_or_none()
        if found is not None:
            continue
        rear_id = None
        power_id = None
        if p.get("rear_port_name"):
            rear = db.execute(
                select(DevicePort).where(
                    DevicePort.device_id == device.id,
                    DevicePort.kind == "rear-port",
                    DevicePort.name == p["rear_port_name"],
                ),
            ).scalar_one_or_none()
            rear_id = rear.id if rear is not None else None
        if p.get("power_port_name"):
            inlet = db.execute(
                select(DevicePort).where(
                    DevicePort.device_id == device.id,
                    DevicePort.kind == "power-port",
                    DevicePort.name == p["power_port_name"],
                ),
            ).scalar_one_or_none()
            power_id = inlet.id if inlet is not None else None
        create_port(
            db,
            device.id,
            DevicePortCreate(
                kind=kind,
                name=name,
                label=p.get("label"),
                connector=p.get("connector"),
                rear_port_id=rear_id,
                power_port_id=power_id,
            ),
        )

    for c in doc.get("cables") or []:
        slug = (c.get("slug") or "").strip()
        site = site_by_slug.get((c.get("site_slug") or "").strip())
        if not slug or site is None:
            continue
        found = db.execute(select(Cable).where(Cable.site_id == site.id, Cable.slug == slug)).scalar_one_or_none()
        if found is not None:
            continue
        ends = {t.get("end"): t for t in (c.get("terminations") or []) if t.get("end") in {"a", "z"}}
        if "a" not in ends or "z" not in ends:
            continue
        try:
            a = _term_from_export(db, ends["a"])
            z = _term_from_export(db, ends["z"])
        except HTTPException:
            continue
        if a is None or z is None:
            continue
        create_cable(
            db,
            CableCreate(
                site_id=site.id,
                name=c.get("name") or slug,
                slug=slug,
                cable_type=c.get("cable_type") or "other",
                status=c.get("status") or "connected",
                a=a,
                z=z,
            ),
        )

    for s in doc.get("fiber_strands") or []:
        slug = (s.get("cable_slug") or "").strip()
        site = site_by_slug.get((s.get("site_slug") or "").strip())
        position = s.get("position")
        if not slug or site is None or position is None:
            continue
        cable = db.execute(select(Cable).where(Cable.site_id == site.id, Cable.slug == slug)).scalar_one_or_none()
        if cable is None or get_fiber_strand_by_position(db, cable.id, int(position)) is not None:
            continue
        try:
            create_fiber_strand(
                db,
                cable,
                FiberStrandCreate(
                    position=int(position),
                    label=s.get("label"),
                    status=s.get("status") or "unused",
                ),
            )
        except (HTTPException, ValueError, TypeError):
            continue

    for b in doc.get("fiber_bundles") or []:
        slug = (b.get("slug") or "").strip()
        cable_slug = (b.get("cable_slug") or "").strip()
        site = site_by_slug.get((b.get("site_slug") or "").strip())
        if not slug or not cable_slug or site is None:
            continue
        cable = db.execute(select(Cable).where(Cable.site_id == site.id, Cable.slug == cable_slug)).scalar_one_or_none()
        if cable is None or get_fiber_bundle_by_slug(db, cable.id, slug) is not None:
            continue
        try:
            bundle = create_fiber_bundle(
                db,
                cable,
                FiberBundleCreate(name=b.get("name") or slug, slug=slug, description=b.get("description")),
            )
        except (HTTPException, ValueError, TypeError):
            continue
        for pos in b.get("strand_positions") or []:
            try:
                position = int(pos)
            except (TypeError, ValueError):
                continue
            strand = get_fiber_strand_by_position(db, cable.id, position)
            if strand is None:
                continue
            try:
                add_fiber_bundle_member(db, bundle, FiberBundleMemberCreate(strand_id=strand.id))
            except (HTTPException, ValueError, TypeError):
                continue


def _term_from_export(db: Session, raw: dict[str, Any]) -> CableTerminationIn | None:
    object_type = (raw.get("object_type") or "").strip()
    if object_type == "power-feed":
        panel = db.execute(select(PowerPanel).where(PowerPanel.slug == (raw.get("panel_slug") or ""))).scalars().first()
        if panel is None:
            return None
        circuit = db.execute(
            select(PowerCircuit).where(PowerCircuit.panel_id == panel.id, PowerCircuit.name == (raw.get("circuit_name") or "")),
        ).scalar_one_or_none()
        if circuit is None:
            return None
        feed = db.execute(
            select(PowerFeed).where(PowerFeed.circuit_id == circuit.id, PowerFeed.slug == (raw.get("feed_slug") or "")),
        ).scalar_one_or_none()
        return CableTerminationIn(object_type="power-feed", object_id=feed.id) if feed is not None else None
    if object_type == "device-port":
        device = db.execute(select(DeviceInstance).where(DeviceInstance.name == (raw.get("device_name") or ""))).scalars().first()
        if device is None:
            return None
        port = db.execute(
            select(DevicePort).where(
                DevicePort.device_id == device.id,
                DevicePort.kind == (raw.get("port_kind") or ""),
                DevicePort.name == (raw.get("port_name") or ""),
            ),
        ).scalar_one_or_none()
        return CableTerminationIn(object_type="device-port", object_id=port.id) if port is not None else None
    if object_type == "interface":
        device = db.execute(select(DeviceInstance).where(DeviceInstance.name == (raw.get("device_name") or ""))).scalars().first()
        if device is None:
            return None
        iface = db.execute(
            select(DeviceInterface).where(
                DeviceInterface.device_id == device.id,
                DeviceInterface.name == (raw.get("interface_name") or ""),
            ),
        ).scalar_one_or_none()
        return CableTerminationIn(object_type="interface", object_id=iface.id) if iface is not None else None
    return None
