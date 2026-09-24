"""Trinn 34: front-til-bak-mapping uten gjettet gjennomgang fra portnavn."""

from fastapi.testclient import TestClient

from app.main import create_app


def test_same_port_name_is_not_a_passthrough() -> None:
    app = create_app()
    with TestClient(app) as client:
        site = client.post("/api/v1/dcim/sites", json={"name": "Pass 34", "slug": "site-34-pass"}).json()
        panel = client.post("/api/v1/dcim/devices", json={"name": "panel-34-a", "site_id": site["id"]}).json()
        other = client.post("/api/v1/dcim/devices", json={"name": "panel-34-b", "site_id": site["id"]}).json()
        front = client.post(
            f"/api/v1/dcim/devices/{panel['id']}/ports",
            json={"kind": "front-port", "name": "1", "auto_map": True, "pairs": 1},
        )
        assert front.status_code == 200, front.text
        assert front.json()["rear_port_id"] is None
        rear = client.post(
            f"/api/v1/dcim/devices/{panel['id']}/ports",
            json={"kind": "rear-port", "name": "1"},
        ).json()
        other_rear = client.post(
            f"/api/v1/dcim/devices/{other['id']}/ports",
            json={"kind": "rear-port", "name": "1"},
        ).json()
        path = client.get(f"/api/v1/dcim/device-ports/{front.json()['id']}/path")
        assert path.status_code == 200, path.text
        hops = path.json()["hops"]
        assert len(hops) == 1
        assert hops[0]["object_id"] == front.json()["id"]
        assert all(h.get("via") != "internal" for h in hops)
        bad_dev = client.patch(
            f"/api/v1/dcim/device-ports/{front.json()['id']}",
            json={"rear_port_id": other_rear["id"], "auto_map": True},
        )
        assert bad_dev.status_code == 400
        assert bad_dev.json()["detail"]["code"] == "port_rear"
        bad_kind = client.patch(
            f"/api/v1/dcim/device-ports/{rear['id']}",
            json={"rear_port_id": front.json()["id"]},
        )
        assert bad_kind.status_code == 400
        assert bad_kind.json()["detail"]["code"] == "port_rear_kind"
        mapped = client.patch(
            f"/api/v1/dcim/device-ports/{front.json()['id']}",
            json={"rear_port_id": rear["id"], "auto_map": True, "pairs": 12, "position": 1},
        )
        assert mapped.status_code == 200, mapped.text
        body = mapped.json()
        assert body["rear_port_id"] == rear["id"]
        assert "auto_map" not in body
        assert "pairs" not in body
        after = client.get(f"/api/v1/dcim/device-ports/{front.json()['id']}/path").json()["hops"]
        assert len(after) == 2
        assert after[1]["object_id"] == rear["id"]
        assert after[1]["via"] == "internal"
        cleared = client.patch(
            f"/api/v1/dcim/device-ports/{front.json()['id']}",
            json={"rear_port_id": None},
        )
        assert cleared.status_code == 200
        assert cleared.json()["rear_port_id"] is None
        gone = client.get(f"/api/v1/dcim/device-ports/{front.json()['id']}/path").json()["hops"]
        assert len(gone) == 1
