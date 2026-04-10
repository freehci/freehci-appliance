"""Tester for SNMP IF-inventar (parser + DCIM-import med mock SNMP)."""

from __future__ import annotations

import asyncio
import uuid

import pytest
from fastapi.testclient import TestClient

from app.core.db import SessionLocal
from app.main import create_app
from app.models.dcim import DeviceInstance
from app.schemas.snmp import SnmpInterfaceRow, SnmpInventoryRead, SnmpVarBindRead
from app.services import snmp_interface_import as iface_imp
from app.services.snmp_inventory import _parse_if_table_varbinds, _parse_ifx_table_varbinds, build_interface_rows


def test_parse_if_and_ifx_merge() -> None:
    if_vbs = [
        SnmpVarBindRead(oid="1.3.6.1.2.1.2.2.1.2.5", value="GigabitEthernet0/1"),
        SnmpVarBindRead(oid="1.3.6.1.2.1.2.2.1.3.5", value="6"),
        SnmpVarBindRead(oid="1.3.6.1.2.1.2.2.1.4.5", value="1500"),
        SnmpVarBindRead(oid="1.3.6.1.2.1.2.2.1.5.5", value="1000000000"),
        SnmpVarBindRead(oid="1.3.6.1.2.1.2.2.1.6.5", value="0x001122334455"),
        SnmpVarBindRead(oid="1.3.6.1.2.1.2.2.1.7.5", value="1"),
        SnmpVarBindRead(oid="1.3.6.1.2.1.2.2.1.8.5", value="1"),
    ]
    ifx_vbs = [
        SnmpVarBindRead(oid="1.3.6.1.2.1.31.1.1.1.1.5", value="Gi0/1"),
        SnmpVarBindRead(oid="1.3.6.1.2.1.31.1.1.1.15.5", value="1000"),
        SnmpVarBindRead(oid="1.3.6.1.2.1.31.1.1.1.18.5", value="uplink"),
    ]
    if_by = _parse_if_table_varbinds(if_vbs)
    ifx_by = _parse_ifx_table_varbinds(ifx_vbs)
    rows = build_interface_rows(if_by, ifx_by)
    assert len(rows) == 1
    r = rows[0]
    assert r.if_index == 5
    assert r.name == "Gi0/1"
    assert r.speed_mbps == 1000
    assert r.mtu == 1500
    assert r.mac_address == "00:11:22:33:44:55"
    assert r.enabled is True
    assert r.description == "uplink"


def test_apply_interface_inventory_mocked(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_collect_a(**_kwargs: object) -> SnmpInventoryRead:
        return SnmpInventoryRead(
            ok=True,
            host="10.0.0.1",
            sys_name="sw-test",
            interfaces=[
                SnmpInterfaceRow(
                    if_index=1,
                    name="eth0",
                    description="lan",
                    if_descr="eth0",
                    if_alias=None,
                    if_type=6,
                    if_type_label="ethernetCsmacd",
                    mtu=1500,
                    speed_mbps=1000,
                    mac_address="aa:bb:cc:dd:ee:ff",
                    admin_status="up",
                    oper_status="up",
                    enabled=True,
                ),
            ],
        )

    monkeypatch.setattr(iface_imp, "collect_interface_inventory", fake_collect_a)

    async def run() -> None:
        db = SessionLocal()
        try:
            name = f"dev-{uuid.uuid4().hex[:8]}"
            dev = DeviceInstance(name=name)
            db.add(dev)
            db.commit()
            db.refresh(dev)

            out = await iface_imp.apply_interface_inventory(
                db,
                device_id=dev.id,
                host="10.0.0.1",
                port=161,
                community="public",
                timeout_sec=1.0,
                retries=0,
                max_varbinds=1000,
            )
            assert out.ok is True
            assert out.created == 1
            assert out.updated == 0
            assert out.poll is not None
            assert out.poll.sys_name == "sw-test"

            out2 = await iface_imp.apply_interface_inventory(
                db,
                device_id=dev.id,
                host="10.0.0.1",
                port=161,
                community="public",
                timeout_sec=1.0,
                retries=0,
                max_varbinds=1000,
            )
            assert out2.skipped == 1
            assert out2.updated == 0

            async def fake_collect_b(**_kwargs: object) -> SnmpInventoryRead:
                return SnmpInventoryRead(
                    ok=True,
                    host="10.0.0.1",
                    interfaces=[
                        SnmpInterfaceRow(
                            if_index=1,
                            name="eth0",
                            description="lan2",
                            if_descr="eth0",
                            if_alias="lan2",
                            if_type=6,
                            if_type_label="ethernetCsmacd",
                            mtu=1500,
                            speed_mbps=1000,
                            mac_address="aa:bb:cc:dd:ee:ff",
                            admin_status="down",
                            oper_status="down",
                            enabled=False,
                        ),
                    ],
                )

            monkeypatch.setattr(iface_imp, "collect_interface_inventory", fake_collect_b)
            out3 = await iface_imp.apply_interface_inventory(
                db,
                device_id=dev.id,
                host="10.0.0.1",
                port=161,
                community="public",
                timeout_sec=1.0,
                retries=0,
                max_varbinds=1000,
            )
            assert out3.updated == 1
        finally:
            db.close()

    asyncio.run(run())


def test_snmp_inventory_apply_api_unknown_device() -> None:
    app = create_app()
    with TestClient(app) as client:
        r = client.post(
            "/api/v1/snmp/inventory/apply",
            json={
                "device_id": 999999999,
                "host": "192.0.2.1",
                "port": 161,
                "community": "public",
            },
        )
        assert r.status_code == 200
        body = r.json()
        assert body["ok"] is False
        assert "enhet" in (body.get("error") or "").lower()
