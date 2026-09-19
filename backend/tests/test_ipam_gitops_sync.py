"""GitOps-sync: drift, bulk-ensure, YAML-eksport og webhook-levering."""

import datetime as dt

from fastapi.testclient import TestClient

from app.core.db import SessionLocal
from app.main import create_app
from app.models.ipam import IpamScanHost, IpamSubnetScan


def test_bulk_ensure_and_yaml_export() -> None:
    app = create_app()
    with TestClient(app) as client:
        sid = client.post("/api/v1/dcim/sites", json={"name": "sync-a", "slug": "sync-a"}).json()["id"]
        first = client.post(
            "/api/v1/ipam/bulk-ensure",
            json={
                "prefixes": [
                    {"site_id": sid, "cidr": "10.93.10.0/24", "name": "LAN", "slug": "sync-a-lan", "role": "active"},
                ],
                "addresses": [],
            },
        )
        assert first.status_code == 200, first.text
        assert first.json()["created"] == 1
        pid = first.json()["results"][0]["id"]

        pinned = client.post(
            "/api/v1/ipam/bulk-ensure",
            json={
                "update": True,
                "prefixes": [
                    {"site_id": sid, "cidr": "10.93.10.0/24", "name": "LAN-core", "slug": "sync-a-lan"},
                ],
                "addresses": [
                    {"ipv4_prefix_id": pid, "address": "10.93.10.10", "mode": "reserve", "role": "vip", "note": "talos"},
                ],
            },
        )
        assert pinned.status_code == 200, pinned.text
        assert pinned.json()["failed"] == 0
        assert any(x["kind"] == "address" and x["created"] for x in pinned.json()["results"])

        yml = client.get("/api/v1/ipam/export", params={"site_id": sid, "format": "yaml"})
        assert yml.status_code == 200
        assert "10.93.10.0/24" in yml.text
        assert "10.93.10.10" in yml.text
        assert "sync-a-lan" in yml.text


def test_drift_unmanaged_and_missing() -> None:
    app = create_app()
    with TestClient(app) as client:
        sid = client.post("/api/v1/dcim/sites", json={"name": "drift-a", "slug": "drift-a"}).json()["id"]
        pfx = client.post(
            "/api/v1/ipam/ipv4-prefixes",
            json={"site_id": sid, "name": "LAN", "cidr": "10.94.0.0/24"},
        )
        pid = pfx.json()["id"]
        reserved = client.post(
            "/api/v1/ipam/ipv4-addresses/ensure",
            json={"ipv4_prefix_id": pid, "address": "10.94.0.10", "mode": "reserve"},
        )
        assert reserved.status_code == 200

        db = SessionLocal()
        try:
            scan = IpamSubnetScan(
                site_id=sid,
                ipv4_prefix_id=pid,
                cidr="10.94.0.0/24",
                method="ping",
                status="completed",
                hosts_scanned=2,
                hosts_responding=2,
                completed_at=dt.datetime.now(dt.UTC),
            )
            db.add(scan)
            db.flush()
            db.add(IpamScanHost(scan_id=scan.id, address="10.94.0.10", ping_responded=True))
            db.add(IpamScanHost(scan_id=scan.id, address="10.94.0.77", ping_responded=True, mac_address="aa:bb"))
            db.commit()
        finally:
            db.close()

        drift = client.get(f"/api/v1/ipam/ipv4-prefixes/{pid}/drift")
        assert drift.status_code == 200, drift.text
        body = drift.json()
        assert body["aligned"] == ["10.94.0.10"]
        assert [x["address"] for x in body["seen_unmanaged"]] == ["10.94.0.77"]
        assert body["reserved_missing"] == []

        missing = client.post(
            "/api/v1/ipam/ipv4-addresses/ensure",
            json={"ipv4_prefix_id": pid, "address": "10.94.0.11", "mode": "reserve"},
        )
        assert missing.status_code == 200
        again = client.get(f"/api/v1/ipam/ipv4-prefixes/{pid}/drift")
        assert "10.94.0.11" in [x["address"] for x in again.json()["reserved_missing"]]


def test_webhook_records_delivery_on_prefix_create() -> None:
    app = create_app()
    with TestClient(app) as client:
        hook = client.post(
            "/api/v1/ipam/webhooks",
            json={"url": "http://127.0.0.1:1/hook", "events": ["prefix.created"]},
        )
        assert hook.status_code == 200, hook.text
        hid = hook.json()["id"]
        sid = client.post("/api/v1/dcim/sites", json={"name": "hook-a", "slug": "hook-a"}).json()["id"]
        pfx = client.post(
            "/api/v1/ipam/ipv4-prefixes",
            json={"site_id": sid, "name": "LAN", "cidr": "10.95.0.0/24"},
        )
        assert pfx.status_code == 200, pfx.text
        deliveries = client.get(f"/api/v1/ipam/webhooks/{hid}/deliveries")
        assert deliveries.status_code == 200
        rows = deliveries.json()
        assert rows
        assert rows[0]["event"] == "prefix.created"
        assert rows[0]["status"] in {"ok", "failed", "skipped"}
