"""Trinn 35: uttak-til-inntak uten gjettet gjennomgang fra portnavn eller last."""

from fastapi.testclient import TestClient

from app.main import create_app


def test_same_power_port_name_is_not_an_inlet_map() -> None:
    app = create_app()
    with TestClient(app) as client:
        site = client.post("/api/v1/dcim/sites", json={"name": "Pwr 35", "slug": "site-35-pwr"}).json()
        pdu = client.post("/api/v1/dcim/devices", json={"name": "pdu-35-a", "site_id": site["id"]}).json()
        other = client.post("/api/v1/dcim/devices", json={"name": "pdu-35-b", "site_id": site["id"]}).json()
        inlet = client.post(
            f"/api/v1/dcim/devices/{pdu['id']}/ports",
            json={"kind": "power-port", "name": "Inlet"},
        ).json()
        outlet = client.post(
            f"/api/v1/dcim/devices/{pdu['id']}/ports",
            json={"kind": "power-outlet", "name": "Inlet", "watts": 2300, "observed_load": 12},
        )
        assert outlet.status_code == 200, outlet.text
        assert outlet.json()["power_port_id"] is None
        other_inlet = client.post(
            f"/api/v1/dcim/devices/{other['id']}/ports",
            json={"kind": "power-port", "name": "Inlet"},
        ).json()
        path = client.get(f"/api/v1/dcim/device-ports/{outlet.json()['id']}/path")
        assert path.status_code == 200, path.text
        hops = path.json()["hops"]
        assert len(hops) == 1
        assert hops[0]["object_id"] == outlet.json()["id"]
        assert all(h.get("via") != "internal" for h in hops)
        bad_dev = client.patch(
            f"/api/v1/dcim/device-ports/{outlet.json()['id']}",
            json={"power_port_id": other_inlet["id"], "watts": 2300},
        )
        assert bad_dev.status_code == 400
        assert bad_dev.json()["detail"]["code"] == "port_power"
        bad_kind = client.patch(
            f"/api/v1/dcim/device-ports/{inlet['id']}",
            json={"power_port_id": outlet.json()["id"]},
        )
        assert bad_kind.status_code == 400
        assert bad_kind.json()["detail"]["code"] == "port_power_kind"
        mapped = client.patch(
            f"/api/v1/dcim/device-ports/{outlet.json()['id']}",
            json={"power_port_id": inlet["id"], "watts": 2300, "observed_load": 12, "phase": "L1"},
        )
        assert mapped.status_code == 200, mapped.text
        body = mapped.json()
        assert body["power_port_id"] == inlet["id"]
        assert "watts" not in body
        assert "observed_load" not in body
        after = client.get(f"/api/v1/dcim/device-ports/{outlet.json()['id']}/path").json()["hops"]
        assert len(after) == 2
        assert after[1]["object_id"] == inlet["id"]
        assert after[1]["via"] == "internal"
        cleared = client.patch(
            f"/api/v1/dcim/device-ports/{outlet.json()['id']}",
            json={"power_port_id": None},
        )
        assert cleared.status_code == 200
        assert cleared.json()["power_port_id"] is None
        gone = client.get(f"/api/v1/dcim/device-ports/{outlet.json()['id']}/path").json()["hops"]
        assert len(gone) == 1
