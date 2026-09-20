"""Trinn 3: tavle → kurs → feed → PDU-uttak → PSU, pluss kabel-path."""

from fastapi.testclient import TestClient

from app.main import create_app


def _site_room_rack(client: TestClient, slug: str) -> tuple[int, int, int]:
    site = client.post("/api/v1/dcim/sites", json={"name": slug, "slug": slug}).json()
    room = client.post("/api/v1/dcim/rooms", json={"site_id": site["id"], "name": f"{slug}-hall"}).json()
    rack = client.post("/api/v1/dcim/racks", json={"room_id": room["id"], "name": f"{slug}-rack", "u_height": 42}).json()
    return site["id"], room["id"], rack["id"]


def test_power_chain_and_unique_panel() -> None:
    app = create_app()
    with TestClient(app) as client:
        site_id, room_id, rack_id = _site_room_rack(client, "pwr-oslo-a")
        panel = client.post(
            "/api/v1/dcim/power-panels",
            json={"site_id": site_id, "room_id": room_id, "name": "Tavle A", "slug": "tavle-a"},
        )
        assert panel.status_code == 200, panel.text
        dup = client.post(
            "/api/v1/dcim/power-panels",
            json={"site_id": site_id, "name": "Tavle A2", "slug": "tavle-a"},
        )
        assert dup.status_code == 409
        circuit = client.post(
            "/api/v1/dcim/power-circuits",
            json={"panel_id": panel.json()["id"], "name": "Q1", "rating_amps": 32, "voltage": 230},
        )
        assert circuit.status_code == 200, circuit.text
        feed = client.post(
            "/api/v1/dcim/power-feeds",
            json={
                "circuit_id": circuit.json()["id"],
                "name": "Feed A",
                "slug": "feed-a",
                "rack_id": rack_id,
                "status": "active",
                "supply": "ac",
            },
        )
        assert feed.status_code == 200, feed.text
        body = feed.json()
        assert body["rack_id"] == rack_id
        assert "observed" not in body
        assert body.get("watts") is None
        listed = client.get(f"/api/v1/dcim/power-feeds?rack_id={rack_id}").json()
        assert len(listed) == 1
        assert listed[0]["circuit_name"] == "Q1"


def test_server_traces_to_pdu_and_feed() -> None:
    app = create_app()
    with TestClient(app) as client:
        site_id, room_id, rack_id = _site_room_rack(client, "pwr-oslo-b")
        panel = client.post(
            "/api/v1/dcim/power-panels",
            json={"site_id": site_id, "room_id": room_id, "name": "Tavle B"},
        ).json()
        circuit = client.post("/api/v1/dcim/power-circuits", json={"panel_id": panel["id"], "name": "Q2"}).json()
        feed = client.post(
            "/api/v1/dcim/power-feeds",
            json={"circuit_id": circuit["id"], "name": "Rack feed", "rack_id": rack_id},
        ).json()
        pdu = client.post("/api/v1/dcim/devices", json={"name": "pdu-pwr-1", "site_id": site_id}).json()
        srv = client.post("/api/v1/dcim/devices", json={"name": "srv-pwr-1", "site_id": site_id}).json()
        inlet = client.post(
            f"/api/v1/dcim/devices/{pdu['id']}/ports",
            json={"kind": "power-port", "name": "Inlet", "connector": "iec-60320-c20"},
        ).json()
        outlet = client.post(
            f"/api/v1/dcim/devices/{pdu['id']}/ports",
            json={"kind": "power-outlet", "name": "C13-1", "power_port_id": inlet["id"]},
        ).json()
        psu = client.post(
            f"/api/v1/dcim/devices/{srv['id']}/ports",
            json={"kind": "power-port", "name": "PSU1"},
        ).json()
        c1 = client.post(
            "/api/v1/dcim/cables",
            json={
                "site_id": site_id,
                "name": "Feed-PDU",
                "cable_type": "power",
                "a": {"object_type": "power-feed", "object_id": feed["id"]},
                "z": {"object_type": "device-port", "object_id": inlet["id"]},
            },
        )
        assert c1.status_code == 200, c1.text
        c2 = client.post(
            "/api/v1/dcim/cables",
            json={
                "site_id": site_id,
                "name": "PDU-PSU",
                "cable_type": "power",
                "a": {"object_type": "device-port", "object_id": outlet["id"]},
                "z": {"object_type": "device-port", "object_id": psu["id"]},
            },
        )
        assert c2.status_code == 200, c2.text
        taken = client.post(
            "/api/v1/dcim/cables",
            json={
                "site_id": site_id,
                "name": "dup",
                "cable_type": "power",
                "a": {"object_type": "power-feed", "object_id": feed["id"]},
                "z": {"object_type": "device-port", "object_id": psu["id"]},
            },
        )
        assert taken.status_code == 409
        path = client.get(f"/api/v1/dcim/device-ports/{psu['id']}/path").json()
        labels = [h["label"] for h in path["hops"]]
        assert any("PSU1" in x for x in labels)
        assert any("C13-1" in x for x in labels)
        assert any("Inlet" in x for x in labels)
        assert any("feed:" in x for x in labels)


def test_front_rear_patch_path() -> None:
    app = create_app()
    with TestClient(app) as client:
        site = client.post("/api/v1/dcim/sites", json={"name": "Patch Site", "slug": "pwr-patch"}).json()
        panel_dev = client.post("/api/v1/dcim/devices", json={"name": "pp-1", "site_id": site["id"]}).json()
        sw = client.post("/api/v1/dcim/devices", json={"name": "sw-1", "site_id": site["id"]}).json()
        rear = client.post(
            f"/api/v1/dcim/devices/{panel_dev['id']}/ports",
            json={"kind": "rear-port", "name": "R1"},
        ).json()
        front = client.post(
            f"/api/v1/dcim/devices/{panel_dev['id']}/ports",
            json={"kind": "front-port", "name": "F1", "rear_port_id": rear["id"]},
        ).json()
        sw_port = client.post(
            f"/api/v1/dcim/devices/{sw['id']}/ports",
            json={"kind": "front-port", "name": "Gi0/1"},
        ).json()
        cab = client.post(
            "/api/v1/dcim/cables",
            json={
                "site_id": site["id"],
                "name": "SW-PP",
                "cable_type": "cat6",
                "a": {"object_type": "device-port", "object_id": sw_port["id"]},
                "z": {"object_type": "device-port", "object_id": front["id"]},
            },
        )
        assert cab.status_code == 200, cab.text
        path = client.get(f"/api/v1/dcim/cables/{cab.json()['id']}/path").json()
        kinds = [h["object_type"] for h in path["hops"]]
        assert kinds[0] == "device-port"
        labels = [h["label"] for h in path["hops"]]
        assert any("Gi0/1" in x for x in labels)
        assert any("F1" in x for x in labels)
        assert any("R1" in x for x in labels)


def test_federation_snapshot_includes_power() -> None:
    from app.core.db import SessionLocal
    from app.services import federation as fed_svc

    app = create_app()
    with TestClient(app) as client:
        tenant = client.post("/api/v1/tenants", json={"name": "Pwr Fed", "slug": "pwr-fed"}).json()
        site = client.post(
            "/api/v1/dcim/sites",
            json={"name": "pwr-fed-oslo", "slug": "pwr-fed-oslo", "tenant_id": tenant["id"]},
        ).json()
        client.post(
            "/api/v1/dcim/power-panels",
            json={"site_id": site["id"], "name": "Fed tavle", "slug": "fed-tavle"},
        )
        snap = client.get("/api/v1/federation/tenants/pwr-fed/snapshot")
        assert snap.status_code == 200, snap.text
        doc = snap.json()["document"]
        assert any(p["slug"] == "fed-tavle" for p in doc["power_panels"])
        doc["tenant"] = {"slug": "pwr-fed-replica", "name": "Pwr Fed Replica", "description": None}
        doc["sites"][0]["slug"] = "pwr-fed-replica-oslo"
        for p in doc["power_panels"]:
            p["site_slug"] = "pwr-fed-replica-oslo"
        db = SessionLocal()
        try:
            fed_svc.apply_document_locally(db, doc)
        finally:
            db.close()
        replica = next(s for s in client.get("/api/v1/dcim/sites").json() if s["slug"] == "pwr-fed-replica-oslo")
        panels = client.get(f"/api/v1/dcim/power-panels?site_id={replica['id']}").json()
        assert any(p["slug"] == "fed-tavle" for p in panels)
