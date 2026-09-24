"""Trinn 33: VRF-strekning uten gjettet medlemskap fra navn, slug eller RD."""

from fastapi.testclient import TestClient

from app.main import create_app


def test_vrf_stretch_is_not_invented_from_name_or_rd() -> None:
    app = create_app()
    with TestClient(app) as client:
        site_a = client.post("/api/v1/dcim/sites", json={"name": "Vst 33 A", "slug": "site-33-vrf-a"}).json()
        site_b = client.post("/api/v1/dcim/sites", json={"name": "Vst 33 B", "slug": "site-33-vrf-b"}).json()
        vrf_a = client.post(
            "/api/v1/ipam/vrfs",
            json={
                "site_id": site_a["id"],
                "name": "tenant-a",
                "slug": "vrf-33-a",
                "route_distinguisher": "65000:100",
            },
        ).json()
        vrf_b = client.post(
            "/api/v1/ipam/vrfs",
            json={
                "site_id": site_b["id"],
                "name": "tenant-a",
                "slug": "vrf-33-b",
                "route_distinguisher": "65000:100",
            },
        ).json()
        listed = client.get("/api/v1/ipam/vrf-stretches").json()
        assert all(s["slug"] != "vst-33-l3" for s in listed)
        same_site = client.post(
            "/api/v1/ipam/vrfs",
            json={"site_id": site_a["id"], "name": "other", "slug": "vrf-33-a2"},
        ).json()
        bad_site = client.post(
            "/api/v1/ipam/vrf-stretches",
            json={"vrf_a_id": vrf_a["id"], "vrf_b_id": same_site["id"], "name": "local"},
        )
        assert bad_site.status_code == 400
        assert bad_site.json()["detail"]["code"] == "vrf_stretch_same_site"
        created = client.post(
            "/api/v1/ipam/vrf-stretches",
            json={
                "vrf_a_id": vrf_a["id"],
                "vrf_b_id": vrf_b["id"],
                "name": "metro vrf",
                "slug": "vst-33-l3",
                "route_distinguisher": "65000:100",
                "rt": "65000:1",
                "independent": True,
            },
        )
        assert created.status_code == 200, created.text
        body = created.json()
        assert body["slug"] == "vst-33-l3"
        assert body["vrf_a_name"] == "tenant-a"
        assert body["vrf_b_name"] == "tenant-a"
        assert body["site_a_id"] != body["site_b_id"]
        assert "route_distinguisher" not in body
        assert "rt" not in body
        assert "independent" not in body
        rev = client.post(
            "/api/v1/ipam/vrf-stretches",
            json={"vrf_a_id": vrf_b["id"], "vrf_b_id": vrf_a["id"], "name": "rev", "slug": "vst-33-rev"},
        )
        assert rev.status_code == 409
        assert rev.json()["detail"]["code"] == "vrf_stretch_exists"
        slug_clash = client.post(
            "/api/v1/ipam/vrf-stretches",
            json={"vrf_a_id": vrf_a["id"], "vrf_b_id": vrf_b["id"], "name": "clash", "slug": "vst-33-l3"},
        )
        assert slug_clash.status_code == 409
        assert client.delete(f"/api/v1/ipam/vrf-stretches/{body['id']}").status_code == 204
        leftover = client.get("/api/v1/ipam/vrf-stretches").json()
        assert all(s["slug"] != "vst-33-l3" for s in leftover)


def test_federation_exports_vrf_stretch_by_slug_not_name_or_rd() -> None:
    from app.core.db import SessionLocal
    from app.services import federation as fed_svc

    app = create_app()
    with TestClient(app) as client:
        tenant = client.post("/api/v1/tenants", json={"name": "Vst Fed", "slug": "vst-33-fed"}).json()
        site_a = client.post(
            "/api/v1/dcim/sites",
            json={"name": "vst-33-fed-oslo", "slug": "vst-33-fed-oslo", "tenant_id": tenant["id"]},
        ).json()
        site_b = client.post(
            "/api/v1/dcim/sites",
            json={"name": "vst-33-fed-bergen", "slug": "vst-33-fed-bergen", "tenant_id": tenant["id"]},
        ).json()
        vrf_a = client.post(
            "/api/v1/ipam/vrfs",
            json={"site_id": site_a["id"], "name": "tenant-a", "slug": "vrf-33-fed-a"},
        ).json()
        vrf_b = client.post(
            "/api/v1/ipam/vrfs",
            json={"site_id": site_b["id"], "name": "tenant-b", "slug": "vrf-33-fed-b"},
        ).json()
        st = client.post(
            "/api/v1/ipam/vrf-stretches",
            json={
                "vrf_a_id": vrf_a["id"],
                "vrf_b_id": vrf_b["id"],
                "name": "metro",
                "slug": "vst-33-fed",
            },
        )
        assert st.status_code == 200, st.text
        snap = client.get("/api/v1/federation/tenants/vst-33-fed/snapshot")
        assert snap.status_code == 200, snap.text
        doc = snap.json()["document"]
        assert isinstance(doc["vrf_stretches"], list)
        match = next(s for s in doc["vrf_stretches"] if s["slug"] == "vst-33-fed")
        assert match["a_vrf_slug"] == "vrf-33-fed-a"
        assert match["z_vrf_slug"] == "vrf-33-fed-b"
        assert match["a_site_slug"] == "vst-33-fed-oslo"
        assert match["z_site_slug"] == "vst-33-fed-bergen"
        assert "route_distinguisher" not in match
        db = SessionLocal()
        try:
            checksum = fed_svc.apply_document_locally(db, doc)
            assert checksum == snap.json()["checksum"]
        finally:
            db.close()
        client.post("/api/v1/tenants", json={"name": "Rep 33", "slug": "rep-33-vst"})
        replica = {
            "apiVersion": "freehci.inventory/v1",
            "kind": "TenantInventory",
            "tenant": {"slug": "rep-33-vst", "name": "Rep 33", "description": None},
            "sites": [
                {"slug": "site-33-rep-a", "name": "Rep A", "description": None},
                {"slug": "site-33-rep-b", "name": "Rep B", "description": None},
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
                    "site": {"slug": "site-33-rep-a", "name": "Rep A"},
                    "vrfs": [{"name": "tenant-a", "slug": "vrf-33-rep-a", "route_distinguisher": "65000:100"}],
                    "vlan_groups": [],
                    "vlans": [],
                    "overlay_segments": [],
                    "overlay_stretches": [],
                    "vrf_stretches": [],
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
                    "site": {"slug": "site-33-rep-b", "name": "Rep B"},
                    "vrfs": [{"name": "tenant-a", "slug": "vrf-33-rep-b", "route_distinguisher": "65000:100"}],
                    "vlan_groups": [],
                    "vlans": [],
                    "overlay_segments": [],
                    "overlay_stretches": [],
                    "vrf_stretches": [],
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
            "overlay_stretches": [],
            "vrf_stretches": [
                {
                    "slug": "vst-33-rep",
                    "name": "metro",
                    "a_site_slug": "site-33-rep-a",
                    "a_vrf_slug": "vrf-33-rep-a",
                    "z_site_slug": "site-33-rep-b",
                    "z_vrf_slug": "vrf-33-rep-b",
                    "route_distinguisher": "65000:100",
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
        copied = client.get("/api/v1/ipam/vrf-stretches").json()
        rep = next(s for s in copied if s["slug"] == "vst-33-rep")
        assert rep["vrf_a_name"] == "tenant-a"
        assert rep["vrf_b_name"] == "tenant-a"
        assert "route_distinguisher" not in rep
        assert "independent" not in rep
