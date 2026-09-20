"""Trinn 4a: tilkobling ≠ plugin-pakke; to kilder gir konflikt, ikke duplikat."""

from fastapi.testclient import TestClient

from app.main import create_app


def test_connection_rejects_raw_secret_and_keeps_sync_empty() -> None:
    app = create_app()
    with TestClient(app) as client:
        bad = client.post(
            "/api/v1/integration-connections",
            json={"name": "Bad", "plugin_id": "dell.idrac", "credential_ref": "hunter2"},
        )
        assert bad.status_code == 422
        ok = client.post(
            "/api/v1/integration-connections",
            json={
                "name": "iDRAC lab",
                "slug": "idrac-lab-a",
                "plugin_id": "dell.idrac",
                "credential_ref": "secret:idrac-lab",
                "base_url": "https://idrac.example.test",
            },
        )
        assert ok.status_code == 200, ok.text
        body = ok.json()
        assert body["credential_ref"] == "secret:idrac-lab"
        assert body["last_sync_at"] is None
        assert body["status"] == "planned"
        assert body["plugin_id"] == "dell.idrac"


def test_two_sources_same_serial_same_device_no_conflict() -> None:
    app = create_app()
    with TestClient(app) as client:
        dev = client.post(
            "/api/v1/dcim/devices",
            json={"name": "srv-ident-1", "serial_number": "ABC123XYZ"},
        ).json()
        a = client.post(
            "/api/v1/integration-connections",
            json={"name": "vCenter A", "slug": "vc-a", "plugin_id": "vmware.vsphere"},
        ).json()
        b = client.post(
            "/api/v1/integration-connections",
            json={"name": "iDRAC B", "slug": "idrac-b", "plugin_id": "dell.idrac"},
        ).json()
        ia = client.post(
            f"/api/v1/integration-connections/{a['id']}/ingest",
            json={"identity_type": "serial", "namespace": "dell", "value": "ABC123XYZ"},
        )
        ib = client.post(
            f"/api/v1/integration-connections/{b['id']}/ingest",
            json={"identity_type": "serial", "namespace": "dell", "value": "ABC123XYZ"},
        )
        assert ia.status_code == 200, ia.text
        assert ib.status_code == 200, ib.text
        assert ia.json()["action"] == "matched"
        assert ib.json()["action"] == "matched"
        assert ia.json()["device_id"] == dev["id"]
        assert ib.json()["device_id"] == dev["id"]
        conflicts = client.get("/api/v1/integration-connections/conflicts").json()
        assert conflicts == []


def test_two_devices_same_serial_is_conflict_not_duplicate() -> None:
    app = create_app()
    with TestClient(app) as client:
        client.post("/api/v1/dcim/devices", json={"name": "srv-dup-a", "serial_number": "DUP-SER-9"})
        client.post("/api/v1/dcim/devices", json={"name": "srv-dup-b", "serial_number": "DUP-SER-9"})
        conn = client.post(
            "/api/v1/integration-connections",
            json={"name": "NetBox", "slug": "netbox-lab", "plugin_id": "netbox.core"},
        ).json()
        before = client.get("/api/v1/dcim/devices").json()
        ingest = client.post(
            f"/api/v1/integration-connections/{conn['id']}/ingest",
            json={"identity_type": "serial", "namespace": "default", "value": "DUP-SER-9", "create_if_missing": True},
        )
        assert ingest.status_code == 200, ingest.text
        assert ingest.json()["action"] == "conflict"
        assert ingest.json()["created"] is False
        after = client.get("/api/v1/dcim/devices").json()
        assert len(after) == len(before)
        conflicts = client.get("/api/v1/integration-connections/conflicts").json()
        assert len(conflicts) == 1
        assert conflicts[0]["value"] == "DUP-SER-9"


def test_second_source_cannot_rebind_identity_to_other_device() -> None:
    app = create_app()
    with TestClient(app) as client:
        a = client.post("/api/v1/dcim/devices", json={"name": "srv-bind-a", "serial_number": "BIND-1"}).json()
        b = client.post("/api/v1/dcim/devices", json={"name": "srv-bind-b", "serial_number": "BIND-2"}).json()
        conn = client.post(
            "/api/v1/integration-connections",
            json={"name": "Redfish", "slug": "rf-lab", "plugin_id": "dell.idrac"},
        ).json()
        first = client.post(
            f"/api/v1/integration-connections/{conn['id']}/ingest",
            json={"identity_type": "serial", "namespace": "dell", "value": "BIND-1"},
        )
        assert first.json()["device_id"] == a["id"]
        other = client.post(
            "/api/v1/integration-connections",
            json={"name": "vCenter", "slug": "vc-rebind", "plugin_id": "vmware.vsphere"},
        ).json()
        clash = client.post(
            f"/api/v1/integration-connections/{other['id']}/ingest",
            json={"identity_type": "serial", "namespace": "dell", "value": "BIND-1", "device_id": b["id"]},
        )
        assert clash.status_code == 200, clash.text
        assert clash.json()["action"] == "conflict"
        assert clash.json()["device_id"] == a["id"]
        devices = client.get("/api/v1/dcim/devices").json()
        names = {d["name"] for d in devices}
        assert "srv-bind-a" in names and "srv-bind-b" in names
