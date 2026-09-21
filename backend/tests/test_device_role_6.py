"""Trinn 6: DeviceRole som funksjon, atskilt fra fysisk type."""

from fastapi.testclient import TestClient

from app.main import create_app


def test_role_crud_rejects_invented_kind() -> None:
    app = create_app()
    with TestClient(app) as client:
        bad = client.post(
            "/api/v1/dcim/device-roles",
            json={"name": "mystery", "slug": "role-6-bad", "kind": "spine-mystery"},
        )
        assert bad.status_code == 422
        ok = client.post(
            "/api/v1/dcim/device-roles",
            json={"name": "Core routers", "slug": "role-6-core", "kind": "core"},
        )
        assert ok.status_code == 200, ok.text
        body = ok.json()
        assert body["kind"] == "core"
        assert body["slug"] == "role-6-core"
        listed = client.get("/api/v1/dcim/device-roles").json()
        assert any(r["slug"] == "role-6-core" for r in listed)


def test_role_slug_unique_and_assignable_to_device() -> None:
    app = create_app()
    with TestClient(app) as client:
        first = client.post(
            "/api/v1/dcim/device-roles",
            json={"name": "Edge", "slug": "role-6-edge", "kind": "edge"},
        )
        assert first.status_code == 200, first.text
        role_id = first.json()["id"]
        clash = client.post(
            "/api/v1/dcim/device-roles",
            json={"name": "Edge 2", "slug": "role-6-edge", "kind": "edge"},
        )
        assert clash.status_code == 409

        dt = client.post(
            "/api/v1/dcim/device-types",
            json={"name": "Server 6", "slug": "server-6-role"},
        )
        assert dt.status_code == 200, dt.text
        dev = client.post(
            "/api/v1/dcim/devices",
            json={
                "name": "hv-6-role",
                "device_type_id": dt.json()["id"],
                "device_role_id": role_id,
            },
        )
        assert dev.status_code == 200, dev.text
        assert dev.json()["device_role_id"] == role_id
        assert dev.json()["device_type_id"] == dt.json()["id"]

        cleared = client.patch(
            f"/api/v1/dcim/devices/{dev.json()['id']}",
            json={"device_role_id": None},
        )
        assert cleared.status_code == 200, cleared.text
        assert cleared.json()["device_role_id"] is None

        assigned = client.patch(
            f"/api/v1/dcim/devices/{dev.json()['id']}",
            json={"device_role_id": role_id},
        )
        assert assigned.status_code == 200, assigned.text
        assert assigned.json()["device_role_id"] == role_id

        gone = client.delete(f"/api/v1/dcim/device-roles/{role_id}")
        assert gone.status_code == 204
        after = client.get(f"/api/v1/dcim/devices/{dev.json()['id']}")
        assert after.status_code == 200
        assert after.json()["device_role_id"] is None
