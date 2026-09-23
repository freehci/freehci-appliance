"""Trinn 13: Route target er ikke RD, og påføres ikke som ruting."""

from fastapi.testclient import TestClient

from app.core.db import SessionLocal
from app.main import create_app
from app.services import federation as fed_svc


def test_route_target_rejects_rd_without_assigned_and_invented_direction() -> None:
    app = create_app()
    with TestClient(app) as client:
        site = client.post("/api/v1/dcim/sites", json={"name": "RT 13", "slug": "site-13-rt"}).json()
        vrf = client.post(
            "/api/v1/ipam/vrfs",
            json={"site_id": site["id"], "name": "core", "slug": "vrf-13-core", "route_distinguisher": "65000:13"},
        ).json()
        bare = client.post("/api/v1/ipam/route-targets", json={"name": "bare", "slug": "rt-13-bare", "value": "65000"})
        assert bare.status_code == 422
        ok = client.post(
            "/api/v1/ipam/route-targets",
            json={"name": "blue", "slug": "rt-13-blue", "value": "65000:100"},
        )
        assert ok.status_code == 200, ok.text
        assert ok.json()["value"] == "65000:100"
        assert ok.json()["slug"] == "rt-13-blue"
        dup = client.post(
            "/api/v1/ipam/route-targets",
            json={"name": "blue2", "slug": "rt-13-blue2", "value": "65000:100"},
        )
        assert dup.status_code == 409
        bad_dir = client.post(
            f"/api/v1/ipam/vrfs/{vrf['id']}/route-targets",
            json={"route_target_id": ok.json()["id"], "direction": "apply"},
        )
        assert bad_dir.status_code == 422
        bind = client.post(
            f"/api/v1/ipam/vrfs/{vrf['id']}/route-targets",
            json={"route_target_id": ok.json()["id"], "direction": "import"},
        )
        assert bind.status_code == 200, bind.text
        assert bind.json()["direction"] == "import"
        assert bind.json()["value"] == "65000:100"
        again = client.post(
            f"/api/v1/ipam/vrfs/{vrf['id']}/route-targets",
            json={"route_target_id": ok.json()["id"], "direction": "import"},
        )
        assert again.status_code == 409
        exp = client.post(
            f"/api/v1/ipam/vrfs/{vrf['id']}/route-targets",
            json={"route_target_id": ok.json()["id"], "direction": "export"},
        )
        assert exp.status_code == 200, exp.text
        listed = client.get(f"/api/v1/ipam/vrfs/{vrf['id']}/route-targets").json()
        assert {x["direction"] for x in listed} == {"import", "export"}
        gone = client.delete(f"/api/v1/ipam/route-targets/{ok.json()['id']}")
        assert gone.status_code == 204
        after = client.get(f"/api/v1/ipam/vrfs/{vrf['id']}/route-targets").json()
        assert after == []


def test_route_target_federation_export_apply() -> None:
    app = create_app()
    with TestClient(app) as client:
        tenant = client.post("/api/v1/tenants", json={"name": "Fed 13", "slug": "fed-13-rt"}).json()
        site = client.post(
            "/api/v1/dcim/sites",
            json={"name": "Fed 13 site", "slug": "site-13-fed", "tenant_id": tenant["id"]},
        ).json()
        vrf = client.post(
            "/api/v1/ipam/vrfs",
            json={"site_id": site["id"], "name": "core", "slug": "vrf-13-fed"},
        ).json()
        rt = client.post(
            "/api/v1/ipam/route-targets",
            json={"name": "fed blue", "slug": "rt-13-fed", "value": "65000:130"},
        ).json()
        bind = client.post(
            f"/api/v1/ipam/vrfs/{vrf['id']}/route-targets",
            json={"route_target_id": rt["id"], "direction": "export"},
        )
        assert bind.status_code == 200, bind.text

        exported = client.get(f"/api/v1/ipam/export?site_id={site['id']}")
        assert exported.status_code == 200, exported.text
        assert any(x["slug"] == "rt-13-fed" for x in exported.json().get("route_targets") or [])
        assert any(
            x["route_target_slug"] == "rt-13-fed" and x["direction"] == "export"
            for x in exported.json().get("vrf_route_targets") or []
        )

        snap = client.get("/api/v1/federation/tenants/fed-13-rt/snapshot")
        assert snap.status_code == 200, snap.text
        doc = snap.json()["document"]
        assert any(x["slug"] == "rt-13-fed" for x in doc["ipam"][0].get("route_targets") or [])

        db = SessionLocal()
        try:
            checksum = fed_svc.apply_document_locally(db, doc)
            assert checksum == snap.json()["checksum"]
        finally:
            db.close()

        client.post("/api/v1/tenants", json={"name": "Rep 13", "slug": "rep-13-rt"})
        replica = {
            "apiVersion": "freehci.inventory/v1",
            "kind": "TenantInventory",
            "tenant": {"slug": "rep-13-rt", "name": "Rep 13", "description": None},
            "sites": [{"slug": "site-13-rep", "name": "Rep site", "description": None}],
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
                    "site": {"slug": "site-13-rep", "name": "Rep site"},
                    "vrfs": [{"name": "core", "slug": "vrf-13-rep"}],
                    "route_targets": [{"name": "rep blue", "slug": "rt-13-rep", "value": "65000:131"}],
                    "vrf_route_targets": [
                        {"vrf_slug": "vrf-13-rep", "route_target_slug": "rt-13-rep", "direction": "import"}
                    ],
                    "vrf_instances": [],
                    "vlan_groups": [],
                    "vlans": [],
                    "prefixes": [],
                    "ipv4_ranges": [],
                    "addresses": [],
                    "ipv6_prefixes": [],
                    "ipv6_addresses": [],
                    "providers": [],
                    "circuits": [],
                    "vpn_services": [],
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
        sites = client.get("/api/v1/dcim/sites").json()
        rep_site = next(s for s in sites if s["slug"] == "site-13-rep")
        binds = client.get(f"/api/v1/ipam/vrf-route-targets?site_id={rep_site['id']}").json()
        assert any(x["route_target_slug"] == "rt-13-rep" and x["direction"] == "import" for x in binds)
