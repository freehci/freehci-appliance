"""Trinn 24: navngitt VPN-klient uten site, uten nøkler eller påfunnet topologi."""

from fastapi.testclient import TestClient

from app.main import create_app


def test_vpn_client_recorded_without_site_or_keys() -> None:
    app = create_app()
    with TestClient(app) as client:
        site = client.post("/api/v1/dcim/sites", json={"name": "CLI 24", "slug": "site-24-cli"}).json()
        vpn = client.post(
            "/api/v1/ipam/vpn-services",
            json={"name": "Remote", "slug": "vpn-24-cli", "vpn_type": "wireguard"},
        )
        assert vpn.status_code == 200, vpn.text
        vpn_id = vpn.json()["id"]
        neither = client.post(f"/api/v1/ipam/vpn-services/{vpn_id}/members", json={"role": "client"})
        assert neither.status_code == 400
        assert neither.json()["detail"]["code"] == "vpn_member_target"
        both = client.post(
            f"/api/v1/ipam/vpn-services/{vpn_id}/members",
            json={"site_id": site["id"], "name": "Laptop"},
        )
        assert both.status_code == 400
        assert both.json()["detail"]["code"] == "vpn_member_target"
        created = client.post(
            f"/api/v1/ipam/vpn-services/{vpn_id}/members",
            json={
                "name": "Laptop Roy",
                "public_key": "abc",
                "allowed_ips": "10.0.0.2/32",
                "endpoint": "1.2.3.4:51820",
                "topology": "star",
            },
        )
        assert created.status_code == 200, created.text
        body = created.json()
        assert body["site_id"] is None
        assert body["site_slug"] is None
        assert body["name"] == "Laptop Roy"
        assert body["slug"] == "laptop-roy"
        assert body["role"] is None
        assert "public_key" not in body
        assert "allowed_ips" not in body
        assert "endpoint" not in body
        sites = client.get("/api/v1/dcim/sites").json()
        assert all(s["slug"] != "laptop-roy" for s in sites)
        dup = client.post(f"/api/v1/ipam/vpn-services/{vpn_id}/members", json={"name": "Laptop Roy"})
        assert dup.status_code == 409
        site_m = client.post(f"/api/v1/ipam/vpn-services/{vpn_id}/members", json={"site_id": site["id"]})
        assert site_m.status_code == 200, site_m.text
        listed = client.get(f"/api/v1/ipam/vpn-services/{vpn_id}/members").json()
        assert {m["slug"] for m in listed if m["slug"]} == {"laptop-roy"}
        assert {m["site_slug"] for m in listed if m["site_slug"]} == {"site-24-cli"}
        assert client.delete(f"/api/v1/ipam/vpn-members/{body['id']}").status_code == 204
        left = client.get(f"/api/v1/ipam/vpn-services/{vpn_id}/members").json()
        assert [m["site_slug"] for m in left] == ["site-24-cli"]


def test_federation_exports_vpn_client_without_invented_site() -> None:
    from app.core.db import SessionLocal
    from app.services import federation as fed_svc

    app = create_app()
    with TestClient(app) as client:
        tenant = client.post("/api/v1/tenants", json={"name": "Cli Fed", "slug": "cli-24-fed"}).json()
        site = client.post(
            "/api/v1/dcim/sites",
            json={"name": "cli-24-fed-oslo", "slug": "cli-24-fed-oslo", "tenant_id": tenant["id"]},
        ).json()
        circ = client.post(
            "/api/v1/ipam/circuits",
            json={
                "circuit_number": "CIR-24-FED",
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
                "slug": "vpn-24-fed",
                "vpn_type": "wireguard",
                "source_circuit_id": circ.json()["id"],
            },
        )
        assert vpn.status_code == 200, vpn.text
        member = client.post(
            f"/api/v1/ipam/vpn-services/{vpn.json()['id']}/members",
            json={"name": "Road warrior", "slug": "road-warrior"},
        )
        assert member.status_code == 200, member.text
        snap = client.get("/api/v1/federation/tenants/cli-24-fed/snapshot")
        assert snap.status_code == 200, snap.text
        doc = snap.json()["document"]
        match = next(m for m in (doc["ipam"][0].get("vpn_members") or []) if m.get("slug") == "road-warrior")
        assert match["vpn_slug"] == "vpn-24-fed"
        assert match["site_slug"] is None
        assert match["name"] == "Road warrior"
        assert "public_key" not in match
        db = SessionLocal()
        try:
            checksum = fed_svc.apply_document_locally(db, doc)
            assert checksum == snap.json()["checksum"]
        finally:
            db.close()
        client.post("/api/v1/tenants", json={"name": "Rep 24", "slug": "rep-24-cli"})
        replica = {
            "apiVersion": "freehci.inventory/v1",
            "kind": "TenantInventory",
            "tenant": {"slug": "rep-24-cli", "name": "Rep 24", "description": None},
            "sites": [{"slug": "site-24-rep", "name": "Rep site", "description": None}],
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
                    "site": {"slug": "site-24-rep", "name": "Rep site"},
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
                    "circuits": [],
                    "circuit_strands": [],
                    "vpn_services": [{"name": "WG", "slug": "vpn-24-rep", "vpn_type": "wireguard"}],
                    "vpn_members": [
                        {
                            "vpn_slug": "vpn-24-rep",
                            "name": "Road warrior",
                            "slug": "road-warrior",
                            "site_slug": None,
                            "public_key": "abc",
                        }
                    ],
                    "tunnels": [],
                    "tunnel_transports": [],
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
        vpn_rep = next(v for v in vpns if v["slug"] == "vpn-24-rep")
        members = client.get(f"/api/v1/ipam/vpn-services/{vpn_rep['id']}/members").json()
        assert [m["slug"] for m in members] == ["road-warrior"]
        assert members[0]["site_id"] is None
        assert "public_key" not in members[0]
        sites = client.get("/api/v1/dcim/sites").json()
        assert all(s["slug"] != "road-warrior" for s in sites)
