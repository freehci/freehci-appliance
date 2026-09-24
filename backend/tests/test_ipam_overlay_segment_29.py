"""Trinn 29: Overlay-segment (VNI) uten gjettet VNI, kind eller påføring."""

from fastapi.testclient import TestClient

from app.main import create_app


def test_overlay_segment_does_not_invent_vni_or_kind() -> None:
    app = create_app()
    with TestClient(app) as client:
        site = client.post("/api/v1/dcim/sites", json={"name": "Ovl 29", "slug": "site-29-ovl"}).json()
        other = client.post("/api/v1/dcim/sites", json={"name": "Ovl 29 B", "slug": "site-29-ovl-b"}).json()
        vrf = client.post(
            "/api/v1/ipam/vrfs",
            json={"site_id": site["id"], "name": "tenant-a", "slug": "vrf-29-ovl"},
        ).json()
        vlan = client.post(
            "/api/v1/ipam/vlans",
            json={
                "site_id": site["id"],
                "vid": 100,
                "name": "access",
                "slug": "vlan-29-access",
                "vrf_id": vrf["id"],
            },
        ).json()
        assert vlan["vid"] == 100
        other_vlan = client.post(
            "/api/v1/ipam/vlans",
            json={"site_id": other["id"], "vid": 100, "name": "other-access", "slug": "vlan-29-other"},
        ).json()
        bad_kind = client.post(
            "/api/v1/ipam/overlay-segments",
            json={"site_id": site["id"], "vni": 10029, "name": "bad", "kind": "applied"},
        )
        assert bad_kind.status_code == 422
        bad_vni = client.post(
            "/api/v1/ipam/overlay-segments",
            json={"site_id": site["id"], "vni": 0, "name": "zero"},
        )
        assert bad_vni.status_code == 422
        too_big = client.post(
            "/api/v1/ipam/overlay-segments",
            json={"site_id": site["id"], "vni": 16_777_216, "name": "huge"},
        )
        assert too_big.status_code == 422
        created = client.post(
            "/api/v1/ipam/overlay-segments",
            json={
                "site_id": site["id"],
                "vni": 10029,
                "name": "pod overlay",
                "slug": "ovl-29-pod",
                "vlan_id": vlan["id"],
                "vrf_id": vrf["id"],
                "multicast": "239.1.1.1",
                "anycast": True,
                "mac_vrf": "tenant-a",
            },
        )
        assert created.status_code == 200, created.text
        body = created.json()
        assert body["slug"] == "ovl-29-pod"
        assert body["vni"] == 10029
        assert body["vni"] != vlan["vid"]
        assert body["kind"] == "vxlan"
        assert body["vlan_id"] == vlan["id"]
        assert body["vlan_vid"] == 100
        assert body["vrf_id"] == vrf["id"]
        assert body["vrf_name"] == "tenant-a"
        assert "multicast" not in body
        assert "anycast" not in body
        assert "mac_vrf" not in body
        no_vrf = client.post(
            "/api/v1/ipam/overlay-segments",
            json={
                "site_id": site["id"],
                "vni": 10030,
                "name": "plain",
                "slug": "ovl-29-plain",
                "vlan_id": vlan["id"],
            },
        )
        assert no_vrf.status_code == 200, no_vrf.text
        assert no_vrf.json()["vrf_id"] is None
        assert no_vrf.json()["kind"] == "vxlan"
        dup = client.post(
            "/api/v1/ipam/overlay-segments",
            json={"site_id": site["id"], "vni": 10029, "name": "dup", "slug": "ovl-29-dup"},
        )
        assert dup.status_code == 409
        assert dup.json()["detail"]["code"] == "overlay_vni_exists"
        slug_clash = client.post(
            "/api/v1/ipam/overlay-segments",
            json={"site_id": site["id"], "vni": 10031, "name": "clash", "slug": "ovl-29-pod"},
        )
        assert slug_clash.status_code == 409
        assert slug_clash.json()["detail"]["code"] == "overlay_slug"
        same_vni_other_site = client.post(
            "/api/v1/ipam/overlay-segments",
            json={"site_id": other["id"], "vni": 10029, "name": "other fabric", "slug": "ovl-29-other"},
        )
        assert same_vni_other_site.status_code == 200, same_vni_other_site.text
        cross = client.post(
            "/api/v1/ipam/overlay-segments",
            json={
                "site_id": site["id"],
                "vni": 10032,
                "name": "cross",
                "slug": "ovl-29-cross",
                "vlan_id": other_vlan["id"],
            },
        )
        assert cross.status_code == 400
        assert cross.json()["detail"]["code"] == "overlay_vlan_site"
        assert client.delete(f"/api/v1/ipam/overlay-segments/{body['id']}").status_code == 204
        leftover = client.get(f"/api/v1/ipam/overlay-segments?site_id={site['id']}").json()
        assert all(o["slug"] != "ovl-29-pod" for o in leftover)


def test_federation_exports_overlay_segment_without_inventing_vni() -> None:
    from app.core.db import SessionLocal
    from app.services import federation as fed_svc

    app = create_app()
    with TestClient(app) as client:
        tenant = client.post("/api/v1/tenants", json={"name": "Ovl Fed", "slug": "ovl-29-fed"}).json()
        site = client.post(
            "/api/v1/dcim/sites",
            json={"name": "ovl-29-fed-oslo", "slug": "ovl-29-fed-oslo", "tenant_id": tenant["id"]},
        ).json()
        vrf = client.post(
            "/api/v1/ipam/vrfs",
            json={"site_id": site["id"], "name": "core", "slug": "vrf-29-fed"},
        ).json()
        vlan = client.post(
            "/api/v1/ipam/vlans",
            json={"site_id": site["id"], "vid": 100, "name": "access", "slug": "vlan-29-fed"},
        ).json()
        ovl = client.post(
            "/api/v1/ipam/overlay-segments",
            json={
                "site_id": site["id"],
                "vni": 10029,
                "name": "pod",
                "slug": "ovl-29-fed",
                "kind": "evpn",
                "vlan_id": vlan["id"],
                "vrf_id": vrf["id"],
            },
        )
        assert ovl.status_code == 200, ovl.text
        snap = client.get("/api/v1/federation/tenants/ovl-29-fed/snapshot")
        assert snap.status_code == 200, snap.text
        doc = snap.json()["document"]
        ipam = doc["ipam"][0]
        assert isinstance(ipam["overlay_segments"], list)
        match = next(o for o in ipam["overlay_segments"] if o["slug"] == "ovl-29-fed")
        assert match["vni"] == 10029
        assert match["vni"] != match.get("vlan_vid")
        assert match["vlan_vid"] == 100
        assert match["vlan_slug"] == "vlan-29-fed"
        assert match["vrf_slug"] == "vrf-29-fed"
        assert match["kind"] == "evpn"
        assert "multicast" not in match
        db = SessionLocal()
        try:
            checksum = fed_svc.apply_document_locally(db, doc)
            assert checksum == snap.json()["checksum"]
        finally:
            db.close()
        client.post("/api/v1/tenants", json={"name": "Rep 29", "slug": "rep-29-ovl"})
        replica = {
            "apiVersion": "freehci.inventory/v1",
            "kind": "TenantInventory",
            "tenant": {"slug": "rep-29-ovl", "name": "Rep 29", "description": None},
            "sites": [{"slug": "site-29-rep", "name": "Rep site", "description": None}],
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
                    "site": {"slug": "site-29-rep", "name": "Rep site"},
                    "vrfs": [{"name": "core", "slug": "vrf-29-rep"}],
                    "vlan_groups": [],
                    "vlans": [{"vid": 100, "name": "access", "slug": "vlan-29-rep"}],
                    "overlay_segments": [
                        {
                            "slug": "ovl-29-rep",
                            "name": "pod",
                            "vni": 10029,
                            "kind": "vxlan",
                            "vlan_vid": 100,
                            "vlan_slug": "vlan-29-rep",
                            "vrf_slug": "vrf-29-rep",
                            "multicast": "239.1.1.1",
                            "anycast": True,
                        }
                    ],
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
        replica_site = next(s for s in client.get("/api/v1/dcim/sites").json() if s["slug"] == "site-29-rep")
        copied = client.get(f"/api/v1/ipam/overlay-segments?site_id={replica_site['id']}").json()
        rep = next(o for o in copied if o["slug"] == "ovl-29-rep")
        assert rep["vni"] == 10029
        assert rep["vni"] != 100
        assert rep["kind"] == "vxlan"
        assert rep["vlan_vid"] == 100
        assert "multicast" not in rep
        assert "anycast" not in rep
