"""Trinn 31: VLAN-strekning uten gjettet medlemskap fra VID, navn eller VNI."""

from fastapi.testclient import TestClient

from app.main import create_app


def test_vlan_stretch_is_not_invented_from_vid_or_name() -> None:
    app = create_app()
    with TestClient(app) as client:
        site_a = client.post("/api/v1/dcim/sites", json={"name": "St 31 A", "slug": "site-31-st"}).json()
        site_b = client.post("/api/v1/dcim/sites", json={"name": "St 31 B", "slug": "site-31-st-b"}).json()
        vlan_a = client.post(
            "/api/v1/ipam/vlans",
            json={"site_id": site_a["id"], "vid": 100, "name": "access", "slug": "vlan-31-a"},
        ).json()
        vlan_b = client.post(
            "/api/v1/ipam/vlans",
            json={"site_id": site_b["id"], "vid": 100, "name": "access", "slug": "vlan-31-b"},
        ).json()
        listed = client.get("/api/v1/ipam/vlan-stretches").json()
        assert all(s["slug"] != "st-31-l2" for s in listed)
        same_site = client.post(
            "/api/v1/ipam/vlans",
            json={"site_id": site_a["id"], "vid": 200, "name": "other", "slug": "vlan-31-a2"},
        ).json()
        bad_site = client.post(
            "/api/v1/ipam/vlan-stretches",
            json={"vlan_a_id": vlan_a["id"], "vlan_b_id": same_site["id"], "name": "local"},
        )
        assert bad_site.status_code == 400
        assert bad_site.json()["detail"]["code"] == "vlan_stretch_same_site"
        created = client.post(
            "/api/v1/ipam/vlan-stretches",
            json={
                "vlan_a_id": vlan_a["id"],
                "vlan_b_id": vlan_b["id"],
                "name": "L2 stretch",
                "slug": "st-31-l2",
                "vni": 100,
                "independent": True,
                "stretched": True,
            },
        )
        assert created.status_code == 200, created.text
        body = created.json()
        assert body["slug"] == "st-31-l2"
        assert body["vlan_a_vid"] == 100
        assert body["vlan_b_vid"] == 100
        assert body["site_a_id"] != body["site_b_id"]
        assert "vni" not in body
        assert "independent" not in body
        rev = client.post(
            "/api/v1/ipam/vlan-stretches",
            json={"vlan_a_id": vlan_b["id"], "vlan_b_id": vlan_a["id"], "name": "rev", "slug": "st-31-rev"},
        )
        assert rev.status_code == 409
        assert rev.json()["detail"]["code"] == "vlan_stretch_exists"
        slug_clash = client.post(
            "/api/v1/ipam/vlan-stretches",
            json={"vlan_a_id": vlan_a["id"], "vlan_b_id": vlan_b["id"], "name": "clash", "slug": "st-31-l2"},
        )
        assert slug_clash.status_code == 409
        assert client.delete(f"/api/v1/ipam/vlan-stretches/{body['id']}").status_code == 204
        leftover = client.get("/api/v1/ipam/vlan-stretches").json()
        assert all(s["slug"] != "st-31-l2" for s in leftover)


def test_federation_exports_vlan_stretch_by_slug_not_vid() -> None:
    from app.core.db import SessionLocal
    from app.services import federation as fed_svc

    app = create_app()
    with TestClient(app) as client:
        tenant = client.post("/api/v1/tenants", json={"name": "St Fed", "slug": "st-31-fed"}).json()
        site_a = client.post(
            "/api/v1/dcim/sites",
            json={"name": "st-31-fed-oslo", "slug": "st-31-fed-oslo", "tenant_id": tenant["id"]},
        ).json()
        site_b = client.post(
            "/api/v1/dcim/sites",
            json={"name": "st-31-fed-bergen", "slug": "st-31-fed-bergen", "tenant_id": tenant["id"]},
        ).json()
        vlan_a = client.post(
            "/api/v1/ipam/vlans",
            json={"site_id": site_a["id"], "vid": 100, "name": "access", "slug": "vlan-31-fed-a"},
        ).json()
        vlan_b = client.post(
            "/api/v1/ipam/vlans",
            json={"site_id": site_b["id"], "vid": 200, "name": "other", "slug": "vlan-31-fed-b"},
        ).json()
        st = client.post(
            "/api/v1/ipam/vlan-stretches",
            json={
                "vlan_a_id": vlan_a["id"],
                "vlan_b_id": vlan_b["id"],
                "name": "metro",
                "slug": "st-31-fed",
            },
        )
        assert st.status_code == 200, st.text
        snap = client.get("/api/v1/federation/tenants/st-31-fed/snapshot")
        assert snap.status_code == 200, snap.text
        doc = snap.json()["document"]
        assert isinstance(doc["vlan_stretches"], list)
        match = next(s for s in doc["vlan_stretches"] if s["slug"] == "st-31-fed")
        assert match["a_vlan_slug"] == "vlan-31-fed-a"
        assert match["z_vlan_slug"] == "vlan-31-fed-b"
        assert match["a_site_slug"] == "st-31-fed-oslo"
        assert match["z_site_slug"] == "st-31-fed-bergen"
        assert "vni" not in match
        db = SessionLocal()
        try:
            checksum = fed_svc.apply_document_locally(db, doc)
            assert checksum == snap.json()["checksum"]
        finally:
            db.close()
        client.post("/api/v1/tenants", json={"name": "Rep 31", "slug": "rep-31-st"})
        replica = {
            "apiVersion": "freehci.inventory/v1",
            "kind": "TenantInventory",
            "tenant": {"slug": "rep-31-st", "name": "Rep 31", "description": None},
            "sites": [
                {"slug": "site-31-rep-a", "name": "Rep A", "description": None},
                {"slug": "site-31-rep-b", "name": "Rep B", "description": None},
            ],
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
                    "site": {"slug": "site-31-rep-a", "name": "Rep A"},
                    "vrfs": [],
                    "vlan_groups": [],
                    "vlans": [{"vid": 100, "name": "access", "slug": "vlan-31-rep-a"}],
                    "overlay_segments": [],
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
                    "autonomous_systems": [],
                    "as_assignments": [],
                    "bgp_instances": [],
                    "bgp_sessions": [],
                },
                {
                    "site": {"slug": "site-31-rep-b", "name": "Rep B"},
                    "vrfs": [],
                    "vlan_groups": [],
                    "vlans": [{"vid": 100, "name": "access", "slug": "vlan-31-rep-b"}],
                    "overlay_segments": [],
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
                    "autonomous_systems": [],
                    "as_assignments": [],
                    "bgp_instances": [],
                    "bgp_sessions": [],
                },
            ],
            "vlan_stretches": [
                {
                    "slug": "st-31-rep",
                    "name": "metro",
                    "a_site_slug": "site-31-rep-a",
                    "a_vlan_slug": "vlan-31-rep-a",
                    "z_site_slug": "site-31-rep-b",
                    "z_vlan_slug": "vlan-31-rep-b",
                    "vni": 100,
                    "independent": True,
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
        copied = client.get("/api/v1/ipam/vlan-stretches").json()
        rep = next(s for s in copied if s["slug"] == "st-31-rep")
        assert rep["vlan_a_vid"] == 100
        assert rep["vlan_b_vid"] == 100
        assert "vni" not in rep
        assert "independent" not in rep
