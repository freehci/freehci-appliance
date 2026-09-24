"""Trinn 32: overlay-strekning uten gjettet medlemskap fra VNI, navn eller VLAN-VID."""

from fastapi.testclient import TestClient

from app.main import create_app


def test_overlay_stretch_is_not_invented_from_vni_or_name() -> None:
    app = create_app()
    with TestClient(app) as client:
        site_a = client.post("/api/v1/dcim/sites", json={"name": "Ost 32 A", "slug": "site-32-ov-a"}).json()
        site_b = client.post("/api/v1/dcim/sites", json={"name": "Ost 32 B", "slug": "site-32-ov-b"}).json()
        ov_a = client.post(
            "/api/v1/ipam/overlay-segments",
            json={"site_id": site_a["id"], "vni": 10032, "name": "prod", "slug": "ov-32-a"},
        ).json()
        ov_b = client.post(
            "/api/v1/ipam/overlay-segments",
            json={"site_id": site_b["id"], "vni": 10032, "name": "prod", "slug": "ov-32-b"},
        ).json()
        listed = client.get("/api/v1/ipam/overlay-stretches").json()
        assert all(s["slug"] != "ost-32-l2" for s in listed)
        same_site = client.post(
            "/api/v1/ipam/overlay-segments",
            json={"site_id": site_a["id"], "vni": 20032, "name": "other", "slug": "ov-32-a2"},
        ).json()
        bad_site = client.post(
            "/api/v1/ipam/overlay-stretches",
            json={"overlay_a_id": ov_a["id"], "overlay_b_id": same_site["id"], "name": "local"},
        )
        assert bad_site.status_code == 400
        assert bad_site.json()["detail"]["code"] == "overlay_stretch_same_site"
        created = client.post(
            "/api/v1/ipam/overlay-stretches",
            json={
                "overlay_a_id": ov_a["id"],
                "overlay_b_id": ov_b["id"],
                "name": "metro overlay",
                "slug": "ost-32-l2",
                "vni": 10032,
                "vlan_vid": 100,
                "multicast": "239.1.1.1",
                "independent": True,
            },
        )
        assert created.status_code == 200, created.text
        body = created.json()
        assert body["slug"] == "ost-32-l2"
        assert body["overlay_a_vni"] == 10032
        assert body["overlay_b_vni"] == 10032
        assert body["site_a_id"] != body["site_b_id"]
        assert "vni" not in body
        assert "vlan_vid" not in body
        assert "multicast" not in body
        assert "independent" not in body
        rev = client.post(
            "/api/v1/ipam/overlay-stretches",
            json={"overlay_a_id": ov_b["id"], "overlay_b_id": ov_a["id"], "name": "rev", "slug": "ost-32-rev"},
        )
        assert rev.status_code == 409
        assert rev.json()["detail"]["code"] == "overlay_stretch_exists"
        slug_clash = client.post(
            "/api/v1/ipam/overlay-stretches",
            json={"overlay_a_id": ov_a["id"], "overlay_b_id": ov_b["id"], "name": "clash", "slug": "ost-32-l2"},
        )
        assert slug_clash.status_code == 409
        assert client.delete(f"/api/v1/ipam/overlay-stretches/{body['id']}").status_code == 204
        leftover = client.get("/api/v1/ipam/overlay-stretches").json()
        assert all(s["slug"] != "ost-32-l2" for s in leftover)


def test_federation_exports_overlay_stretch_by_slug_not_vni() -> None:
    from app.core.db import SessionLocal
    from app.services import federation as fed_svc

    app = create_app()
    with TestClient(app) as client:
        tenant = client.post("/api/v1/tenants", json={"name": "Ost Fed", "slug": "ost-32-fed"}).json()
        site_a = client.post(
            "/api/v1/dcim/sites",
            json={"name": "ost-32-fed-oslo", "slug": "ost-32-fed-oslo", "tenant_id": tenant["id"]},
        ).json()
        site_b = client.post(
            "/api/v1/dcim/sites",
            json={"name": "ost-32-fed-bergen", "slug": "ost-32-fed-bergen", "tenant_id": tenant["id"]},
        ).json()
        ov_a = client.post(
            "/api/v1/ipam/overlay-segments",
            json={"site_id": site_a["id"], "vni": 10032, "name": "prod", "slug": "ov-32-fed-a"},
        ).json()
        ov_b = client.post(
            "/api/v1/ipam/overlay-segments",
            json={"site_id": site_b["id"], "vni": 20032, "name": "other", "slug": "ov-32-fed-b"},
        ).json()
        st = client.post(
            "/api/v1/ipam/overlay-stretches",
            json={
                "overlay_a_id": ov_a["id"],
                "overlay_b_id": ov_b["id"],
                "name": "metro",
                "slug": "ost-32-fed",
            },
        )
        assert st.status_code == 200, st.text
        snap = client.get("/api/v1/federation/tenants/ost-32-fed/snapshot")
        assert snap.status_code == 200, snap.text
        doc = snap.json()["document"]
        assert isinstance(doc["overlay_stretches"], list)
        match = next(s for s in doc["overlay_stretches"] if s["slug"] == "ost-32-fed")
        assert match["a_overlay_slug"] == "ov-32-fed-a"
        assert match["z_overlay_slug"] == "ov-32-fed-b"
        assert match["a_site_slug"] == "ost-32-fed-oslo"
        assert match["z_site_slug"] == "ost-32-fed-bergen"
        assert "vni" not in match
        db = SessionLocal()
        try:
            checksum = fed_svc.apply_document_locally(db, doc)
            assert checksum == snap.json()["checksum"]
        finally:
            db.close()
        client.post("/api/v1/tenants", json={"name": "Rep 32", "slug": "rep-32-ost"})
        replica = {
            "apiVersion": "freehci.inventory/v1",
            "kind": "TenantInventory",
            "tenant": {"slug": "rep-32-ost", "name": "Rep 32", "description": None},
            "sites": [
                {"slug": "site-32-rep-a", "name": "Rep A", "description": None},
                {"slug": "site-32-rep-b", "name": "Rep B", "description": None},
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
                    "site": {"slug": "site-32-rep-a", "name": "Rep A"},
                    "vrfs": [],
                    "vlan_groups": [],
                    "vlans": [],
                    "overlay_segments": [{"vid": 100, "vni": 10032, "name": "prod", "slug": "ov-32-rep-a"}],
                    "overlay_stretches": [],
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
                    "site": {"slug": "site-32-rep-b", "name": "Rep B"},
                    "vrfs": [],
                    "vlan_groups": [],
                    "vlans": [],
                    "overlay_segments": [{"vid": 100, "vni": 10032, "name": "prod", "slug": "ov-32-rep-b"}],
                    "overlay_stretches": [],
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
            "vlan_stretches": [],
            "overlay_stretches": [
                {
                    "slug": "ost-32-rep",
                    "name": "metro",
                    "a_site_slug": "site-32-rep-a",
                    "a_overlay_slug": "ov-32-rep-a",
                    "z_site_slug": "site-32-rep-b",
                    "z_overlay_slug": "ov-32-rep-b",
                    "vni": 10032,
                    "vlan_vid": 100,
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
        copied = client.get("/api/v1/ipam/overlay-stretches").json()
        rep = next(s for s in copied if s["slug"] == "ost-32-rep")
        assert rep["overlay_a_vni"] == 10032
        assert rep["overlay_b_vni"] == 10032
        assert "vni" not in rep
        assert "vlan_vid" not in rep
        assert "independent" not in rep
