"""Trinn 12: VRF-instans på enhet, uten påføring av routing."""

from fastapi.testclient import TestClient

from app.core.db import SessionLocal
from app.main import create_app
from app.services import federation as fed_svc


def test_vrf_instance_rejects_invented_intent() -> None:
    app = create_app()
    with TestClient(app) as client:
        site = client.post("/api/v1/dcim/sites", json={"name": "VRF 12", "slug": "site-12-vrfi"}).json()
        vrf = client.post(
            "/api/v1/ipam/vrfs",
            json={"site_id": site["id"], "name": "core", "slug": "vrf-12-core", "route_distinguisher": "65000:12"},
        ).json()
        dev = client.post("/api/v1/dcim/devices", json={"name": "pe-12-a", "site_id": site["id"]}).json()
        bad = client.post(
            f"/api/v1/ipam/vrfs/{vrf['id']}/instances",
            json={"device_id": dev["id"], "slug": "inst-12-bad", "intent": "applied"},
        )
        assert bad.status_code == 422
        ok = client.post(
            f"/api/v1/ipam/vrfs/{vrf['id']}/instances",
            json={"device_id": dev["id"], "slug": "inst-12-pe1", "intent": "recorded"},
        )
        assert ok.status_code == 200, ok.text
        body = ok.json()
        assert body["intent"] == "recorded"
        assert body["device_name"] == "pe-12-a"
        assert body["effective_rd"] == "65000:12"
        assert body["route_distinguisher"] is None
        dup = client.post(
            f"/api/v1/ipam/vrfs/{vrf['id']}/instances",
            json={"device_id": dev["id"], "slug": "inst-12-dup", "intent": "intended"},
        )
        assert dup.status_code == 409
        other = client.post("/api/v1/dcim/sites", json={"name": "VRF 12b", "slug": "site-12-vrfi-b"}).json()
        stray = client.post("/api/v1/dcim/devices", json={"name": "pe-12-b", "site_id": other["id"]}).json()
        mismatch = client.post(
            f"/api/v1/ipam/vrfs/{vrf['id']}/instances",
            json={"device_id": stray["id"], "slug": "inst-12-mis"},
        )
        assert mismatch.status_code == 400
        assert mismatch.json()["detail"]["code"] == "site_mismatch"
        listed = client.get(f"/api/v1/ipam/vrf-instances?device_id={dev['id']}").json()
        assert len(listed) == 1
        gone = client.delete(f"/api/v1/ipam/vrf-instances/{body['id']}")
        assert gone.status_code == 204
        after = client.get(f"/api/v1/ipam/vrfs/{vrf['id']}/instances").json()
        assert after == []


def test_vrf_instance_rd_override_and_delete_with_vrf() -> None:
    app = create_app()
    with TestClient(app) as client:
        site = client.post("/api/v1/dcim/sites", json={"name": "VRF 12c", "slug": "site-12-vrfi-c"}).json()
        vrf = client.post(
            "/api/v1/ipam/vrfs",
            json={"site_id": site["id"], "name": "edge", "slug": "vrf-12-edge", "route_distinguisher": "65000:13"},
        ).json()
        dev = client.post("/api/v1/dcim/devices", json={"name": "pe-12-c", "site_id": site["id"]}).json()
        inst = client.post(
            f"/api/v1/ipam/vrfs/{vrf['id']}/instances",
            json={
                "device_id": dev["id"],
                "slug": "inst-12-edge",
                "intent": "intended",
                "route_distinguisher": "192.0.2.12:100",
            },
        )
        assert inst.status_code == 200, inst.text
        assert inst.json()["route_distinguisher"] == "192.0.2.12:100"
        assert inst.json()["effective_rd"] == "192.0.2.12:100"
        assert inst.json()["intent"] == "intended"
        gone = client.delete(f"/api/v1/ipam/vrfs/{vrf['id']}")
        assert gone.status_code == 204
        leftover = client.get(f"/api/v1/ipam/vrf-instances?device_id={dev['id']}").json()
        assert leftover == []


def test_vrf_instance_federation_export_apply() -> None:
    app = create_app()
    with TestClient(app) as client:
        tenant = client.post("/api/v1/tenants", json={"name": "Fed 12", "slug": "fed-12-vrfi"}).json()
        site = client.post(
            "/api/v1/dcim/sites",
            json={"name": "Fed 12 site", "slug": "site-12-fed", "tenant_id": tenant["id"]},
        ).json()
        vrf = client.post(
            "/api/v1/ipam/vrfs",
            json={"site_id": site["id"], "name": "core", "slug": "vrf-12-fed", "route_distinguisher": "65000:14"},
        ).json()
        dev = client.post("/api/v1/dcim/devices", json={"name": "pe-12-fed", "site_id": site["id"]}).json()
        inst = client.post(
            f"/api/v1/ipam/vrfs/{vrf['id']}/instances",
            json={"device_id": dev["id"], "slug": "inst-12-fed", "intent": "recorded"},
        )
        assert inst.status_code == 200, inst.text

        exported = client.get(f"/api/v1/ipam/export?site_id={site['id']}")
        assert exported.status_code == 200, exported.text
        assert any(x["slug"] == "inst-12-fed" for x in exported.json().get("vrf_instances") or [])

        snap = client.get("/api/v1/federation/tenants/fed-12-vrfi/snapshot")
        assert snap.status_code == 200, snap.text
        doc = snap.json()["document"]
        instances = doc["ipam"][0].get("vrf_instances") or []
        assert any(x["slug"] == "inst-12-fed" and x["device_name"] == "pe-12-fed" for x in instances)

        db = SessionLocal()
        try:
            checksum = fed_svc.apply_document_locally(db, doc)
            assert checksum == snap.json()["checksum"]
        finally:
            db.close()

        client.post("/api/v1/tenants", json={"name": "Rep 12", "slug": "rep-12-vrfi"})
        replica = {
            "apiVersion": "freehci.inventory/v1",
            "kind": "TenantInventory",
            "tenant": {"slug": "rep-12-vrfi", "name": "Rep 12", "description": None},
            "sites": [{"slug": "site-12-rep", "name": "Rep site", "description": None}],
            "rooms": [],
            "racks": [],
            "manufacturers": [],
            "device_types": [],
            "device_models": [],
            "device_roles": [],
            "devices": [{"name": "pe-12-rep", "site_slug": "site-12-rep"}],
            "device_artifacts": [],
            "device_artifact_records": [],
            "placements": [],
            "ipam": [
                {
                    "site": {"slug": "site-12-rep", "name": "Rep site"},
                    "vrfs": [{"name": "core", "slug": "vrf-12-rep"}],
                    "vrf_instances": [
                        {
                            "vrf_slug": "vrf-12-rep",
                            "site_slug": "site-12-rep",
                            "device_name": "pe-12-rep",
                            "slug": "inst-12-rep",
                            "intent": "recorded",
                        }
                    ],
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
        rep_site = next(s for s in sites if s["slug"] == "site-12-rep")
        listed = client.get(f"/api/v1/ipam/vrf-instances?site_id={rep_site['id']}").json()
        assert any(x["slug"] == "inst-12-rep" for x in listed)
