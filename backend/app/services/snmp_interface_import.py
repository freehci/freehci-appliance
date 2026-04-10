"""Importer SNMP IF-inventar til DCIM-grensesnitt (match på navn)."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.schemas.dcim import DeviceInterfaceCreate, DeviceInterfaceRead, DeviceInterfaceUpdate
from app.schemas.snmp import SnmpInterfaceRow, SnmpInventoryApplyRead
from app.services import dcim as dcim_svc
from app.services.snmp_inventory import collect_interface_inventory


def _build_update(existing: DeviceInterfaceRead, row: SnmpInterfaceRow) -> DeviceInterfaceUpdate | None:
    patch: dict = {}
    if row.description != existing.description:
        patch["description"] = row.description
    if row.mac_address is not None and row.mac_address != existing.mac_address:
        patch["mac_address"] = row.mac_address
    if row.speed_mbps is not None and row.speed_mbps != existing.speed_mbps:
        patch["speed_mbps"] = row.speed_mbps
    if row.mtu is not None and row.mtu != existing.mtu:
        patch["mtu"] = row.mtu
    if row.enabled != existing.enabled:
        patch["enabled"] = row.enabled
    if row.if_index != existing.sort_order:
        patch["sort_order"] = row.if_index
    if not patch:
        return None
    return DeviceInterfaceUpdate(**patch)


async def apply_interface_inventory(
    db: Session,
    *,
    device_id: int,
    host: str,
    port: int,
    community: str,
    timeout_sec: float,
    retries: int,
    max_varbinds: int,
) -> SnmpInventoryApplyRead:
    if dcim_svc.get_device(db, device_id) is None:
        return SnmpInventoryApplyRead(
            ok=False,
            error="enhet ikke funnet",
            device_id=device_id,
        )

    inv = await collect_interface_inventory(
        host=host.strip(),
        port=port,
        community=community,
        timeout_sec=timeout_sec,
        retries=retries,
        max_varbinds=max_varbinds,
    )
    if not inv.ok:
        return SnmpInventoryApplyRead(
            ok=False,
            error=inv.error or "SNMP-feil",
            device_id=device_id,
            host=host,
            poll=inv,
        )

    existing = dcim_svc.list_device_interfaces(db, device_id)
    by_name = {e.name: e for e in existing}

    created = updated = skipped = 0
    for row in inv.interfaces:
        name = row.name.strip()
        if not name:
            skipped += 1
            continue
        cur = by_name.get(name)
        if cur is None:
            dcim_svc.create_device_interface(
                db,
                device_id,
                DeviceInterfaceCreate(
                    name=name,
                    description=row.description,
                    mac_address=row.mac_address,
                    speed_mbps=row.speed_mbps,
                    mtu=row.mtu,
                    enabled=row.enabled,
                    sort_order=row.if_index,
                ),
            )
            created += 1
        else:
            upd = _build_update(cur, row)
            if upd is None:
                skipped += 1
            else:
                row_obj = dcim_svc.get_device_interface(db, device_id, cur.id)
                if row_obj is None:
                    skipped += 1
                else:
                    dcim_svc.update_device_interface(db, device_id, row_obj, upd)
                    updated += 1

    return SnmpInventoryApplyRead(
        ok=True,
        device_id=device_id,
        host=host.strip(),
        created=created,
        updated=updated,
        skipped=skipped,
        poll=inv,
    )
