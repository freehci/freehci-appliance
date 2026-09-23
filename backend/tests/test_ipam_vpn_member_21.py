"""Trinn 21: VPN-medlem er en site, uten å gjette hub/spoke eller mesh fra antall."""

from fastapi.testclient import TestClient

from app.main import create_app


def test_vpn_member_records_site_without_invented_topology() -> None:
    app = create_app()
    with TestClient(app) as client:
        site_a = client.post("/api/v1/dcim/sites", json={"name": "MEM 21a", "slug": "site-21-mem-a"}).json()
        site_b = client.post("/api/v1/dcim/sites", json={"name": "MEM 21b", "slug": "site-21-mem-b"}).json()
        vpn = client.post(
            "/api/v1/ipam/vpn-services",
            json={"name": "Hub", "slug": "vpn-21-hub", "vpn_type": "wireguard"},
        )
        assert vpn.status_code == 200, vpn.text
        assert client.get(f"/api/v1/ipam/vpn-services/{vpn.json()['id']}/members").json() == []
        created = client.post(
            f"/api/v1/ipam/vpn-services/{vpn.json()['id']}/members",
            json={"site_id": site_a["id"], "role": "hub", "topology": "hub-spoke", "mesh": True},
        )
        assert created.status_code == 200, created.text
        body = created.json()
        assert body["site_id"] == site_a["id"]
        assert body["site_slug"] == "site-21-mem-a"
        assert body["role"] == "hub"
        assert "topology" not in body
        assert "mesh" not in body
        second = client.post(
            f"/api/v1/ipam/vpn-services/{vpn.json()['id']}/members",
            json={"site_id": site_b["id"]},
        )
        assert second.status_code == 200, second.text
        assert second.json()["role"] is None
        listed = client.get(f"/api/v1/ipam/vpn-services/{vpn.json()['id']}/members").json()
        assert {m["site_slug"] for m in listed} == {"site-21-mem-a", "site-21-mem-b"}
        dup = client.post(
            f"/api/v1/ipam/vpn-services/{vpn.json()['id']}/members",
            json={"site_id": site_a["id"]},
        )
        assert dup.status_code == 409
        assert dup.json()["detail"]["code"] == "vpn_member_taken"
        bad_role = client.post(
            f"/api/v1/ipam/vpn-services/{vpn.json()['id']}/members",
            json={"site_id": site_b["id"], "role": "core"},
        )
        assert bad_role.status_code == 422
        missing = client.post(
            f"/api/v1/ipam/vpn-services/{vpn.json()['id']}/members",
            json={"site_id": 999999},
        )
        assert missing.status_code == 404
        assert client.delete(f"/api/v1/ipam/vpn-members/{body['id']}").status_code == 204
        left = client.get(f"/api/v1/ipam/vpn-services/{vpn.json()['id']}/members").json()
        assert [m["site_slug"] for m in left] == ["site-21-mem-b"]


def test_delete_vpn_clears_members() -> None:
    app = create_app()
    with TestClient(app) as client:
        site = client.post("/api/v1/dcim/sites", json={"name": "MEM 21d", "slug": "site-21-del"}).json()
        vpn = client.post(
            "/api/v1/ipam/vpn-services",
            json={"name": "Del", "slug": "vpn-21-del", "vpn_type": "other"},
        ).json()
        member = client.post(
            f"/api/v1/ipam/vpn-services/{vpn['id']}/members",
            json={"site_id": site["id"], "role": "peer"},
        )
        assert member.status_code == 200, member.text
        assert client.delete(f"/api/v1/ipam/vpn-services/{vpn['id']}").status_code == 204
        assert client.get(f"/api/v1/ipam/vpn-services/{vpn['id']}/members").status_code == 404


def test_federation_exports_vpn_member_by_site_slug() -> None:
    from app.core.db import SessionLocal
    from app.services import federation as fed_svc

    app = create_app()
    with TestClient(app) as client:
        tenant = client.post("/api/v1/tenants", json={"name": "Mem Fed", "slug": "mem-21-fed"}).json()
        site = client.post(
            "/api/v1/dcim/sites",
            json={"name": "mem-21-fed-oslo", "slug": "mem-21-fed-oslo", "tenant_id": tenant["id"]},
        ).json()
        circ = client.post(
            "/api/v1/ipam/circuits",
            json={
                "circuit_number": "CIR-21-FED",
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
                "slug": "vpn-21-fed",
                "vpn_type": "wireguard",
                "source_circuit_id": circ.json()["id"],
            },
        )
        assert vpn.status_code == 200, vpn.text
        member = client.post(
            f"/api/v1/ipam/vpn-services/{vpn.json()['id']}/members",
            json={"site_id": site["id"], "role": "hub"},
        )
        assert member.status_code == 200, member.text
        snap = client.get("/api/v1/federation/tenants/mem-21-fed/snapshot")
        assert snap.status_code == 200, snap.text
        doc = snap.json()["document"]
        match = next(m for m in (doc["ipam"][0].get("vpn_members") or []) if m["site_slug"] == "mem-21-fed-oslo")
        assert match["vpn_slug"] == "vpn-21-fed"
        assert match["role"] == "hub"
        assert "topology" not in match
        db = SessionLocal()
        try:
            checksum = fed_svc.apply_document_locally(db, doc)
            assert checksum == snap.json()["checksum"]
        finally:
            db.close()
        client.post("/api/v1/tenants", json={"name": "Rep 21", "slug": "rep-21-mem"})
        replica = {
            "apiVersion": "freehci.inventory/v1",
            "kind": "TenantInventory",
            "tenant": {"slug": "rep-21-mem", "name": "Rep 21", "description": None},
            "sites": [{"slug": "site-21-rep", "name": "Rep site", "description": None}],
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
                    "site": {"slug": "site-21-rep", "name": "Rep site"},
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
                            "circuit_number": "CIR-21-REP",
                            "name": "Rep access",
                            "circuit_type": "fiber",
                            "layer": "transport",
                            "a_site_slug": "site-21-rep",
                        }
                    ],
                    "circuit_strands": [],
                    "vpn_services": [
                        {
                            "name": "WG",
                            "slug": "vpn-21-rep",
                            "vpn_type": "wireguard",
                            "source_circuit_number": "CIR-21-REP",
                        }
                    ],
                    "vpn_members": [{"vpn_slug": "vpn-21-rep", "site_slug": "site-21-rep", "role": "spoke"}],
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
        vpn = next(v for v in vpns if v["slug"] == "vpn-21-rep")
        members = client.get(f"/api/v1/ipam/vpn-services/{vpn['id']}/members").json()
        assert [m["site_slug"] for m in members] == ["site-21-rep"]
        assert members[0]["role"] == "spoke"
