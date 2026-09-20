"""Trinn 2b: leverandør, layer, klassifisering, terminering, VPN uten å gjette type."""

from fastapi.testclient import TestClient

from app.core.secret_ref import normalize_secret_ref
from app.main import create_app


def test_secret_ref_rejects_key_material() -> None:
    assert normalize_secret_ref(None) is None
    assert normalize_secret_ref("secret:wg-peer-edge") == "secret:wg-peer-edge"
    try:
        normalize_secret_ref("c3VwZXJzZWNyZXRrZXltYXRlcmlhbA==")
        raise AssertionError("expected ValueError")
    except ValueError:
        pass


def test_provider_not_invented_from_free_text() -> None:
    app = create_app()
    with TestClient(app) as client:
        c = client.post(
            "/api/v1/ipam/circuits",
            json={"circuit_number": "CIR-FT-1", "name": "Dark fiber", "circuit_type": "fiber", "provider_name": "Telenor"},
        )
        assert c.status_code == 200, c.text
        assert c.json()["provider_name"] == "Telenor"
        assert c.json()["provider_id"] is None
        listed = client.get("/api/v1/ipam/providers").json()
        assert listed == []


def test_new_fiber_sets_layer_only_when_client_sends_it() -> None:
    app = create_app()
    with TestClient(app) as client:
        implicit = client.post(
            "/api/v1/ipam/circuits",
            json={"circuit_number": "CIR-IMPL", "name": "Old style", "circuit_type": "fiber"},
        )
        assert implicit.status_code == 200, implicit.text
        assert implicit.json()["layer"] is None
        explicit = client.post(
            "/api/v1/ipam/circuits",
            json={"circuit_number": "CIR-EXP", "name": "New fiber", "circuit_type": "fiber", "layer": "transport"},
        )
        assert explicit.status_code == 200, explicit.text
        assert explicit.json()["layer"] == "transport"


def test_classify_does_not_rewrite_circuit_type() -> None:
    app = create_app()
    with TestClient(app) as client:
        other = client.post(
            "/api/v1/ipam/circuits",
            json={"circuit_number": "CIR-OTH", "name": "Mystery", "circuit_type": "other"},
        )
        assert other.status_code == 200, other.text
        body = other.json()
        assert body["layer"] is None
        assert body["needs_classification"] is True
        assert body["circuit_type"] == "other"
        classified = client.post(
            f"/api/v1/ipam/circuits/{body['id']}/classify",
            json={"layer": "overlay", "create_vpn": True},
        )
        assert classified.status_code == 200, classified.text
        out = classified.json()
        assert out["circuit"]["circuit_type"] == "other"
        assert out["circuit"]["layer"] == "overlay"
        assert out["circuit"]["needs_classification"] is False
        assert out["vpn_service_id"]
        vpn = client.get(f"/api/v1/ipam/vpn-services/{out['vpn_service_id']}").json()
        assert vpn["source_circuit_id"] == body["id"]
        assert vpn["vpn_type"] == "other"
        again = client.get(f"/api/v1/ipam/circuits/{body['id']}").json() if False else client.get("/api/v1/ipam/circuits").json()
        match = next(x for x in again if x["id"] == body["id"])
        assert match["circuit_type"] == "other"


def test_wireguard_classify_maps_vpn_type_from_stored_type() -> None:
    app = create_app()
    with TestClient(app) as client:
        row = client.post(
            "/api/v1/ipam/circuits",
            json={"circuit_number": "CIR-WG", "name": "WG tunnel", "circuit_type": "wireguard"},
        ).json()
        assert row["needs_classification"] is True
        classified = client.post(
            f"/api/v1/ipam/circuits/{row['id']}/classify",
            json={"layer": "overlay"},
        )
        assert classified.status_code == 200, classified.text
        assert classified.json()["circuit"]["circuit_type"] == "wireguard"
        vpn = client.get(f"/api/v1/ipam/vpn-services/{classified.json()['vpn_service_id']}").json()
        assert vpn["vpn_type"] == "wireguard"


def test_provider_and_termination_picker() -> None:
    app = create_app()
    with TestClient(app) as client:
        site = client.post("/api/v1/dcim/sites", json={"name": "Lab", "slug": "lab-2b-term"}).json()
        prov = client.post("/api/v1/ipam/providers", json={"name": "GlobalConnect", "slug": "globalconnect"}).json()
        assert prov["slug"] == "globalconnect"
        acc = client.post(
            f"/api/v1/ipam/providers/{prov['id']}/accounts",
            json={"name": "Colo", "account_number": "ACC-1"},
        )
        assert acc.status_code == 200, acc.text
        circuit = client.post(
            "/api/v1/ipam/circuits",
            json={
                "circuit_number": "CIR-GC",
                "name": "GC fiber",
                "circuit_type": "fiber",
                "layer": "transport",
                "provider_id": prov["id"],
                "provider_account_id": acc.json()["id"],
                "a_site_id": site["id"],
            },
        )
        assert circuit.status_code == 200, circuit.text
        assert circuit.json()["provider_id"] == prov["id"]
        device = client.post("/api/v1/dcim/devices", json={"name": "edge-1", "site_id": site["id"]}).json()
        iface = client.post(
            f"/api/v1/dcim/devices/{device['id']}/interfaces",
            json={"name": "xe-0/0/0"},
        ).json()
        term = client.post(
            f"/api/v1/ipam/circuits/{circuit.json()['id']}/terminations",
            json={"endpoint": "a", "device_id": device["id"], "interface_id": iface["id"], "site_id": site["id"]},
        )
        assert term.status_code == 200, term.text
        assert term.json()["device_id"] == device["id"]
        assert term.json()["interface_id"] == iface["id"]
        assert term.json()["device_name"] == "edge-1"
        assert term.json()["interface_name"] == "xe-0/0/0"


def test_vpn_peer_rejects_raw_key() -> None:
    app = create_app()
    with TestClient(app) as client:
        vpn = client.post("/api/v1/ipam/vpn-services", json={"name": "HQ mesh", "vpn_type": "wireguard"}).json()
        tun = client.post(f"/api/v1/ipam/vpn-services/{vpn['id']}/tunnels", json={"name": "site-a"}).json()
        bad = client.post(
            f"/api/v1/ipam/tunnels/{tun['id']}/peers",
            json={"name": "peer-a", "public_key_ref": "not-a-ref"},
        )
        assert bad.status_code == 422
        ok = client.post(
            f"/api/v1/ipam/tunnels/{tun['id']}/peers",
            json={"name": "peer-a", "public_key_ref": "secret:wg-peer-a", "allowed_ips": "10.8.0.2/32"},
        )
        assert ok.status_code == 200, ok.text
        assert ok.json()["public_key_ref"] == "secret:wg-peer-a"
        assert ok.json()["allowed_ips"] == ["10.8.0.2/32"]
