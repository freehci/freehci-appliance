"""Trinn 27: BGP-instans på ruter, uten naboer, RIB eller påføring."""

from fastapi.testclient import TestClient

from app.main import create_app


def test_bgp_instance_does_not_invent_neighbors_or_router_id() -> None:
    app = create_app()
    with TestClient(app) as client:
        site = client.post("/api/v1/dcim/sites", json={"name": "BGP 27", "slug": "site-27-bgp"}).json()
        local = client.post("/api/v1/ipam/autonomous-systems", json={"asn": 65027, "name": "Local 27"}).json()
        other = client.post("/api/v1/ipam/autonomous-systems", json={"asn": 65028, "name": "Other 27"}).json()
        vrf = client.post("/api/v1/ipam/vrfs", json={"site_id": site["id"], "name": "core", "slug": "vrf-27-core"}).json()
        dev = client.post(
            "/api/v1/dcim/devices",
            json={"name": "pe-27-a", "site_id": site["id"]},
        ).json()
        bad_intent = client.post(
            "/api/v1/ipam/bgp-instances",
            json={"device_id": dev["id"], "local_as_id": local["id"], "intent": "applied"},
        )
        assert bad_intent.status_code == 422
        bad_rid = client.post(
            "/api/v1/ipam/bgp-instances",
            json={"device_id": dev["id"], "local_as_id": local["id"], "router_id": "2001:db8::1"},
        )
        assert bad_rid.status_code == 422
        created = client.post(
            "/api/v1/ipam/bgp-instances",
            json={
                "device_id": dev["id"],
                "local_as_id": local["id"],
                "slug": "bi-27-pe",
                "neighbors": [{"peer_ip": "192.0.2.1"}],
                "route_count": 1200,
                "established": True,
                "import_policy": "ALLOW-ALL",
            },
        )
        assert created.status_code == 200, created.text
        body = created.json()
        assert body["slug"] == "bi-27-pe"
        assert body["device_name"] == "pe-27-a"
        assert body["local_asn"] == 65027
        assert body["intent"] == "recorded"
        assert body["router_id"] is None
        assert "neighbors" not in body
        assert "route_count" not in body
        assert "established" not in body
        sessions = client.get(f"/api/v1/ipam/bgp-sessions?site_id={site['id']}").json()
        assert all(s.get("bgp_instance_id") != body["id"] for s in sessions)
        assert not any(s["peer_ip"] == "192.0.2.1" for s in sessions)
        dup = client.post(
            "/api/v1/ipam/bgp-instances",
            json={"device_id": dev["id"], "local_as_id": local["id"], "slug": "bi-27-dup"},
        )
        assert dup.status_code == 409
        assert dup.json()["detail"]["code"] == "bgp_instance_exists"
        vrf_ok = client.post(
            "/api/v1/ipam/bgp-instances",
            json={
                "device_id": dev["id"],
                "local_as_id": local["id"],
                "vrf_id": vrf["id"],
                "slug": "bi-27-vrf",
                "router_id": "192.0.2.99",
                "intent": "intended",
            },
        )
        assert vrf_ok.status_code == 200, vrf_ok.text
        assert vrf_ok.json()["router_id"] == "192.0.2.99"
        assert vrf_ok.json()["intent"] == "intended"
        sess = client.post(
            "/api/v1/ipam/bgp-sessions",
            json={
                "bgp_instance_id": body["id"],
                "remote_asn": 65029,
                "peer_ip": "198.51.100.1",
                "import_policy": "DENY",
            },
        )
        assert sess.status_code == 200, sess.text
        assert sess.json()["bgp_instance_id"] == body["id"]
        assert sess.json()["site_id"] == site["id"]
        assert sess.json()["local_as_id"] == local["id"]
        assert sess.json()["local_device_id"] == dev["id"]
        assert sess.json()["observed_status"] is None
        clash = client.post(
            "/api/v1/ipam/bgp-sessions",
            json={
                "bgp_instance_id": body["id"],
                "local_as_id": other["id"],
                "remote_asn": 65030,
                "peer_ip": "198.51.100.2",
            },
        )
        assert clash.status_code == 400
        assert clash.json()["detail"]["code"] == "bgp_instance_as"
        assert client.delete(f"/api/v1/ipam/bgp-instances/{body['id']}").status_code == 204
        leftover = client.get(f"/api/v1/ipam/bgp-sessions?site_id={site['id']}").json()
        match = next(s for s in leftover if s["peer_ip"] == "198.51.100.1")
        assert match["bgp_instance_id"] is None
        listed = client.get("/api/v1/ipam/bgp-instances").json()
        assert all(b["slug"] != "bi-27-pe" for b in listed)


def test_federation_exports_bgp_instance_by_slug() -> None:
    from app.core.db import SessionLocal
    from app.services import federation as fed_svc

    app = create_app()
    with TestClient(app) as client:
        tenant = client.post("/api/v1/tenants", json={"name": "Bi Fed", "slug": "bi-27-fed"}).json()
        site = client.post(
            "/api/v1/dcim/sites",
            json={"name": "bi-27-fed-oslo", "slug": "bi-27-fed-oslo", "tenant_id": tenant["id"]},
        ).json()
        local = client.post(
            "/api/v1/ipam/autonomous-systems",
            json={"asn": 65031, "name": "Fed 27", "tenant_id": tenant["id"]},
        ).json()
        dev = client.post("/api/v1/dcim/devices", json={"name": "pe-27-fed", "site_id": site["id"]}).json()
        inst = client.post(
            "/api/v1/ipam/bgp-instances",
            json={"device_id": dev["id"], "local_as_id": local["id"], "slug": "bi-27-fed", "router_id": "192.0.2.7"},
        )
        assert inst.status_code == 200, inst.text
        sess = client.post(
            "/api/v1/ipam/bgp-sessions",
            json={
                "bgp_instance_id": inst.json()["id"],
                "remote_asn": 65032,
                "peer_ip": "198.51.100.8",
                "name": "edge-27",
            },
        )
        assert sess.status_code == 200, sess.text
        snap = client.get("/api/v1/federation/tenants/bi-27-fed/snapshot")
        assert snap.status_code == 200, snap.text
        doc = snap.json()["document"]
        ipam = doc["ipam"][0]
        assert isinstance(ipam["bgp_instances"], list)
        match = next(i for i in ipam["bgp_instances"] if i["slug"] == "bi-27-fed")
        assert match["device_name"] == "pe-27-fed"
        assert match["local_asn"] == 65031
        assert match["router_id"] == "192.0.2.7"
        assert "neighbors" not in match
        bgp = next(s for s in ipam["bgp_sessions"] if s["peer_ip"] == "198.51.100.8")
        assert bgp["instance_slug"] == "bi-27-fed"
        db = SessionLocal()
        try:
            checksum = fed_svc.apply_document_locally(db, doc)
            assert checksum == snap.json()["checksum"]
        finally:
            db.close()
        client.post("/api/v1/tenants", json={"name": "Rep 27", "slug": "rep-27-bi"})
        replica = {
            "apiVersion": "freehci.inventory/v1",
            "kind": "TenantInventory",
            "tenant": {"slug": "rep-27-bi", "name": "Rep 27", "description": None},
            "sites": [{"slug": "site-27-rep", "name": "Rep site", "description": None}],
            "rooms": [],
            "racks": [],
            "manufacturers": [],
            "device_types": [],
            "device_models": [],
            "device_roles": [],
            "devices": [{"name": "pe-27-rep", "site_slug": "site-27-rep"}],
            "device_artifacts": [],
            "device_artifact_records": [],
            "placements": [],
            "ipam": [
                {
                    "site": {"slug": "site-27-rep", "name": "Rep site"},
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
                    "circuit_terminations": [],
                    "circuit_strands": [],
                    "vpn_services": [],
                    "vpn_members": [],
                    "tunnels": [],
                    "tunnel_transports": [],
                    "autonomous_systems": [{"asn": 65033, "name": "Rep 27", "slug": "as-27-rep", "is_private": True}],
                    "as_assignments": [],
                    "bgp_instances": [
                        {
                            "slug": "bi-27-rep",
                            "name": "PE 27",
                            "device_name": "pe-27-rep",
                            "local_asn": 65033,
                            "intent": "recorded",
                            "router_id": "192.0.2.33",
                            "neighbors": [{"peer_ip": "203.0.113.1"}],
                            "route_count": 9,
                        }
                    ],
                    "bgp_sessions": [
                        {
                            "name": "rep-peer",
                            "slug": "rep-peer",
                            "local_asn": 65033,
                            "remote_asn": 65034,
                            "peer_ip": "198.51.100.33",
                            "instance_slug": "bi-27-rep",
                            "address_families": ["ipv4-unicast"],
                            "desired_status": "planned",
                        }
                    ],
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
        replica_site = next(s for s in client.get("/api/v1/dcim/sites").json() if s["slug"] == "site-27-rep")
        instances = client.get(f"/api/v1/ipam/bgp-instances?site_id={replica_site['id']}").json()
        rep = next(i for i in instances if i["slug"] == "bi-27-rep")
        assert rep["router_id"] == "192.0.2.33"
        assert "neighbors" not in rep
        copied = client.get(f"/api/v1/ipam/bgp-sessions?site_id={replica_site['id']}").json()
        assert [s["peer_ip"] for s in copied if s["bgp_instance_id"] == rep["id"]] == ["198.51.100.33"]
        assert all(s["peer_ip"] != "203.0.113.1" for s in copied)
