"""Trinn 20: tunnel knyttes til underlagssamband uten primær/backup eller failover."""

from fastapi.testclient import TestClient

from app.main import create_app


def _access_and_tunnel(client: TestClient, slug: str) -> tuple[int, int, int]:
    site = client.post("/api/v1/dcim/sites", json={"name": slug, "slug": slug}).json()
    circ = client.post(
        "/api/v1/ipam/circuits",
        json={
            "circuit_number": f"CIR-{slug}",
            "name": "Access",
            "circuit_type": "fiber",
            "layer": "transport",
            "a_site_id": site["id"],
        },
    )
    assert circ.status_code == 200, circ.text
    vpn = client.post(
        "/api/v1/ipam/vpn-services",
        json={"name": f"VPN {slug}", "slug": f"vpn-{slug}", "vpn_type": "wireguard"},
    )
    assert vpn.status_code == 200, vpn.text
    tun = client.post(
        f"/api/v1/ipam/vpn-services/{vpn.json()['id']}/tunnels",
        json={"name": "site-a", "slug": "tun-a"},
    )
    assert tun.status_code == 200, tun.text
    return site["id"], circ.json()["id"], tun.json()["id"]


def test_tunnel_binds_underlay_without_failover() -> None:
    app = create_app()
    with TestClient(app) as client:
        _site_id, circuit_id, tunnel_id = _access_and_tunnel(client, "site-20-tun")
        bound = client.post(
            f"/api/v1/ipam/tunnels/{tunnel_id}/transports",
            json={"circuit_id": circuit_id, "primary": True, "backup": True, "failover_percent": 99.9},
        )
        assert bound.status_code == 200, bound.text
        body = bound.json()
        assert body["circuit_id"] == circuit_id
        assert body["circuit_number"] == "CIR-site-20-tun"
        assert "primary" not in body
        assert "backup" not in body
        assert "failover" not in body
        listed = client.get(f"/api/v1/ipam/tunnels/{tunnel_id}/transports").json()
        assert [b["circuit_id"] for b in listed] == [circuit_id]
        dup = client.post(
            f"/api/v1/ipam/tunnels/{tunnel_id}/transports",
            json={"circuit_id": circuit_id},
        )
        assert dup.status_code == 409
        assert dup.json()["detail"]["code"] == "tunnel_transport_taken"
        missing = client.post(
            f"/api/v1/ipam/tunnels/{tunnel_id}/transports",
            json={"circuit_id": 999999},
        )
        assert missing.status_code == 404
        assert client.delete(f"/api/v1/ipam/tunnel-transports/{body['id']}").status_code == 204
        assert client.get(f"/api/v1/ipam/tunnels/{tunnel_id}/transports").json() == []


def test_delete_circuit_clears_transport() -> None:
    app = create_app()
    with TestClient(app) as client:
        _site_id, circuit_id, tunnel_id = _access_and_tunnel(client, "site-20-del-c")
        bound = client.post(
            f"/api/v1/ipam/tunnels/{tunnel_id}/transports",
            json={"circuit_id": circuit_id},
        )
        assert bound.status_code == 200, bound.text
        assert client.delete(f"/api/v1/ipam/circuits/{circuit_id}").status_code == 204
        assert client.get(f"/api/v1/ipam/tunnels/{tunnel_id}/transports").json() == []


def test_delete_tunnel_clears_transport() -> None:
    app = create_app()
    with TestClient(app) as client:
        _site_id, circuit_id, tunnel_id = _access_and_tunnel(client, "site-20-del-t")
        bound = client.post(
            f"/api/v1/ipam/tunnels/{tunnel_id}/transports",
            json={"circuit_id": circuit_id},
        )
        assert bound.status_code == 200, bound.text
        assert client.delete(f"/api/v1/ipam/tunnels/{tunnel_id}").status_code == 204
        assert client.get(f"/api/v1/ipam/tunnels/{tunnel_id}/transports").status_code == 404


def test_federation_exports_tunnel_transport_by_slug() -> None:
    from app.core.db import SessionLocal
    from app.services import federation as fed_svc

    app = create_app()
    with TestClient(app) as client:
        tenant = client.post("/api/v1/tenants", json={"name": "Tun Fed", "slug": "tun-20-fed"}).json()
        site = client.post(
            "/api/v1/dcim/sites",
            json={"name": "tun-20-fed-oslo", "slug": "tun-20-fed-oslo", "tenant_id": tenant["id"]},
        ).json()
        circ = client.post(
            "/api/v1/ipam/circuits",
            json={
                "circuit_number": "CIR-20-ACC",
                "name": "Access",
                "circuit_type": "fiber",
                "layer": "transport",
                "a_site_id": site["id"],
            },
        )
        assert circ.status_code == 200, circ.text
        vpn = client.post(
            "/api/v1/ipam/vpn-services",
            json={
                "name": "WG",
                "slug": "vpn-20-wg",
                "vpn_type": "wireguard",
                "source_circuit_id": circ.json()["id"],
            },
        )
        assert vpn.status_code == 200, vpn.text
        tun = client.post(
            f"/api/v1/ipam/vpn-services/{vpn.json()['id']}/tunnels",
            json={"name": "site-a", "slug": "tun-20-a"},
        )
        assert tun.status_code == 200, tun.text
        bound = client.post(
            f"/api/v1/ipam/tunnels/{tun.json()['id']}/transports",
            json={"circuit_id": circ.json()["id"]},
        )
        assert bound.status_code == 200, bound.text
        snap = client.get("/api/v1/federation/tenants/tun-20-fed/snapshot")
        assert snap.status_code == 200, snap.text
        doc = snap.json()["document"]
        tunnels = doc["ipam"][0].get("tunnels") or []
        assert any(t["slug"] == "tun-20-a" and t["vpn_slug"] == "vpn-20-wg" for t in tunnels)
        match = next(b for b in (doc["ipam"][0].get("tunnel_transports") or []) if b["circuit_number"] == "CIR-20-ACC")
        assert match["tunnel_slug"] == "tun-20-a"
        assert "failover" not in match
        db = SessionLocal()
        try:
            checksum = fed_svc.apply_document_locally(db, doc)
            assert checksum == snap.json()["checksum"]
        finally:
            db.close()
        client.post("/api/v1/tenants", json={"name": "Rep 20", "slug": "rep-20-tun"})
        replica = {
            "apiVersion": "freehci.inventory/v1",
            "kind": "TenantInventory",
            "tenant": {"slug": "rep-20-tun", "name": "Rep 20", "description": None},
            "sites": [{"slug": "site-20-rep", "name": "Rep site", "description": None}],
            "rooms": [],
            "racks": [],
            "manufacturers": [],
            "device_types": [],
            "device_models": [],
            "device_roles": [],
            "devices": [],
            "device_artifacts": [],
            "device_artifact_records": [],
            "placements": [],
            "ipam": [
                {
                    "site": {"slug": "site-20-rep", "name": "Rep site"},
                    "vrfs": [],
                    "vlan_groups": [],
                    "vlans": [],
                    "prefixes": [],
                    "ipv4_ranges": [],
                    "addresses": [],
                    "ipv6_prefixes": [],
                    "ipv6_addresses": [],
                    "providers": [],
                    "circuit_groups": [],
                    "contracts": [],
                    "circuits": [
                        {
                            "circuit_number": "CIR-20-REP",
                            "name": "Rep access",
                            "circuit_type": "fiber",
                            "layer": "transport",
                            "a_site_slug": "site-20-rep",
                        }
                    ],
                    "circuit_strands": [],
                    "vpn_services": [
                        {
                            "name": "WG",
                            "slug": "vpn-20-rep",
                            "vpn_type": "wireguard",
                            "source_circuit_number": "CIR-20-REP",
                        }
                    ],
                    "tunnels": [{"vpn_slug": "vpn-20-rep", "name": "site-a", "slug": "tun-20-a", "status": "planned"}],
                    "tunnel_transports": [
                        {
                            "vpn_slug": "vpn-20-rep",
                            "tunnel_slug": "tun-20-a",
                            "circuit_number": "CIR-20-REP",
                        }
                    ],
                    "autonomous_systems": [],
                    "as_assignments": [],
                    "bgp_sessions": [],
                }
            ],
            "clusters": [],
            "catalog_templates": [],
            "catalog_instances": [],
        }
        db = SessionLocal()
        try:
            fed_svc.apply_document_locally(db, replica)
        finally:
            db.close()
        vpns = client.get("/api/v1/ipam/vpn-services").json()
        vpn = next(v for v in vpns if v["slug"] == "vpn-20-rep")
        tunnels = client.get(f"/api/v1/ipam/vpn-services/{vpn['id']}/tunnels").json()
        tunnel = next(t for t in tunnels if t["slug"] == "tun-20-a")
        binds = client.get(f"/api/v1/ipam/tunnels/{tunnel['id']}/transports").json()
        assert [b["circuit_number"] for b in binds] == ["CIR-20-REP"]
