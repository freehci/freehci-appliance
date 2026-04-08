"""API-tester for DCIM (enkel flyt)."""

from fastapi.testclient import TestClient

from app.main import create_app


def test_dcim_site_room_rack_device_flow() -> None:
    app = create_app()
    with TestClient(app) as client:
        s = client.post(
            "/api/v1/dcim/sites",
            json={"name": "Oslo DC", "slug": "oslo-dc"},
        )
        assert s.status_code == 200
        site_id = s.json()["id"]

        r = client.post(
            "/api/v1/dcim/rooms",
            json={"site_id": site_id, "name": "Hall A"},
        )
        assert r.status_code == 200, r.text
        room_id = r.json()["id"]

        k = client.post(
            "/api/v1/dcim/racks",
            json={"room_id": room_id, "name": "R42", "u_height": 42},
        )
        assert k.status_code == 200
        rack_id = k.json()["id"]

        m = client.post(
            "/api/v1/dcim/manufacturers",
            json={"name": "Dell"},
        )
        assert m.status_code == 200
        mid = m.json()["id"]

        dm = client.post(
            "/api/v1/dcim/device-models",
            json={"manufacturer_id": mid, "name": "R740", "u_height": 2},
        )
        assert dm.status_code == 200
        dmod_id = dm.json()["id"]

        d = client.post(
            "/api/v1/dcim/devices",
            json={"device_model_id": dmod_id, "name": "srv-01"},
        )
        assert d.status_code == 200
        dev_id = d.json()["id"]

        p = client.post(
            "/api/v1/dcim/placements",
            json={
                "rack_id": rack_id,
                "device_id": dev_id,
                "u_position": 10,
                "mounting": "front",
            },
        )
        assert p.status_code == 200, p.text
        assert p.json()["u_position"] == 10

        p2 = client.post(
            "/api/v1/dcim/placements",
            json={
                "rack_id": rack_id,
                "device_id": dev_id,
                "u_position": 20,
                "mounting": "front",
            },
        )
        assert p2.status_code == 400

        pid = p.json()["id"]
        mv = client.patch(
            f"/api/v1/dcim/placements/{pid}",
            json={"u_position": 25},
        )
        assert mv.status_code == 200, mv.text
        assert mv.json()["u_position"] == 25
