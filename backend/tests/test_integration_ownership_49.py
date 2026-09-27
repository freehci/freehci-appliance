"""Trinn 49: objektmapping og felteierskap uten navne-inferens eller mapping_json."""

from fastapi.testclient import TestClient

from app.main import create_app


def test_matching_name_does_not_link_and_infer_is_rejected() -> None:
    app = create_app()
    with TestClient(app) as client:
        dev = client.post("/api/v1/dcim/devices", json={"name": "srv-own-49"}).json()
        conn = client.post(
            "/api/v1/integration-connections",
            json={
                "name": "NetBox lab",
                "slug": "nb-own-49",
                "plugin_id": "netbox.core",
                "mapping_json": {"fields": {"name": "netbox"}, "objects": {"srv-own-49": 1}},
            },
        )
        assert conn.status_code == 200, conn.text
        cid = conn.json()["id"]
        infer = client.post(
            "/api/v1/external-object-maps",
            json={
                "connection_id": cid,
                "object_type": "device",
                "external_id": "srv-own-49",
                "infer_from_name": True,
                "device_name": "srv-own-49",
            },
        )
        assert infer.status_code == 422
        named = client.post(
            "/api/v1/external-object-maps",
            json={"connection_id": cid, "object_type": "device", "external_id": "srv-own-49"},
        )
        assert named.status_code == 200, named.text
        assert named.json()["device_id"] is None
        assert named.json()["external_id"] == "srv-own-49"
        owns = client.get("/api/v1/field-ownerships").json()
        assert owns == []
        missing = client.post(
            "/api/v1/external-object-maps",
            json={"connection_id": 99999, "object_type": "device", "external_id": "ghost"},
        )
        assert missing.status_code == 400
        ghost_dev = client.post(
            "/api/v1/external-object-maps",
            json={"connection_id": cid, "object_type": "device", "external_id": "ext-ghost", "device_id": 99999},
        )
        assert ghost_dev.status_code == 400
        vm = client.post(
            "/api/v1/external-object-maps",
            json={"connection_id": cid, "object_type": "vm", "external_id": "vm-1", "device_id": dev["id"]},
        )
        assert vm.status_code == 422
        linked = client.patch(
            f"/api/v1/external-object-maps/{named.json()['id']}",
            json={"device_id": dev["id"]},
        )
        assert linked.status_code == 200, linked.text
        assert linked.json()["device_id"] == dev["id"]
        listed = client.get("/api/v1/external-object-maps").json()
        assert len(listed) == 1
        assert listed[0]["device_id"] == dev["id"]


def test_field_ownership_is_explicit_and_second_source_conflicts() -> None:
    app = create_app()
    with TestClient(app) as client:
        dev = client.post("/api/v1/dcim/devices", json={"name": "srv-field-49"}).json()
        a = client.post(
            "/api/v1/integration-connections",
            json={"name": "iDRAC", "slug": "idrac-own-49", "plugin_id": "dell.idrac"},
        ).json()
        b = client.post(
            "/api/v1/integration-connections",
            json={"name": "vCenter", "slug": "vc-own-49", "plugin_id": "vmware.vsphere"},
        ).json()
        infer = client.post(
            "/api/v1/field-ownerships",
            json={
                "connection_id": a["id"],
                "device_id": dev["id"],
                "field_name": "name",
                "infer_from_mapping": True,
            },
        )
        assert infer.status_code == 422
        hostname = client.post(
            "/api/v1/field-ownerships",
            json={"connection_id": a["id"], "device_id": dev["id"], "field_name": "hostname"},
        )
        assert hostname.status_code == 422
        missing_conn = client.post(
            "/api/v1/field-ownerships",
            json={"connection_id": 99999, "device_id": dev["id"], "field_name": "name"},
        )
        assert missing_conn.status_code == 400
        first = client.post(
            "/api/v1/field-ownerships",
            json={"connection_id": a["id"], "device_id": dev["id"], "field_name": "name"},
        )
        assert first.status_code == 200, first.text
        assert first.json()["connection_id"] == a["id"]
        clash = client.post(
            "/api/v1/field-ownerships",
            json={"connection_id": b["id"], "device_id": dev["id"], "field_name": "name"},
        )
        assert clash.status_code == 409
        serial = client.post(
            "/api/v1/field-ownerships",
            json={"connection_id": b["id"], "device_id": dev["id"], "field_name": "serial_number"},
        )
        assert serial.status_code == 200, serial.text
        listed = client.get(f"/api/v1/field-ownerships?device_id={dev['id']}").json()
        assert {row["field_name"] for row in listed} == {"name", "serial_number"}
        deleted = client.delete(f"/api/v1/field-ownerships/{first.json()['id']}")
        assert deleted.status_code == 204
        after = client.get(f"/api/v1/field-ownerships?device_id={dev['id']}").json()
        assert [row["field_name"] for row in after] == ["serial_number"]
