"""Trinn 41: eksplisitt IPAM-VRF på grensesnitt uten gjettet kobling fra navn, enhet eller prefiks."""

from fastapi.testclient import TestClient

from app.main import create_app


def test_matching_name_device_vrf_or_prefix_is_not_an_interface_vrf() -> None:
    app = create_app()
    with TestClient(app) as client:
        site = client.post("/api/v1/dcim/sites", json={"name": "Vrf 41", "slug": "site-41-ivrf"}).json()
        other = client.post("/api/v1/dcim/sites", json={"name": "Vrf 41 B", "slug": "site-41-ivrf-b"}).json()
        vrf = client.post(
            "/api/v1/ipam/vrfs",
            json={"site_id": site["id"], "name": "core", "slug": "vrf-41-core"},
        ).json()
        foreign = client.post(
            "/api/v1/ipam/vrfs",
            json={"site_id": other["id"], "name": "core", "slug": "vrf-41-foreign"},
        ).json()
        sw = client.post("/api/v1/dcim/devices", json={"name": "sw-41-a", "site_id": site["id"]}).json()
        inst = client.post(
            f"/api/v1/ipam/vrfs/{vrf['id']}/instances",
            json={"device_id": sw["id"], "slug": "inst-41-sw", "intent": "recorded"},
        )
        assert inst.status_code == 200, inst.text
        pfx = client.post(
            "/api/v1/ipam/ipv4-prefixes",
            json={
                "site_id": site["id"],
                "name": "lan-41",
                "cidr": "10.219.98.0/28",
                "slug": "px-41-a",
                "role": "access",
                "status": "active",
                "vrf_id": vrf["id"],
            },
        )
        assert pfx.status_code == 200, pfx.text
        created = client.post(
            f"/api/v1/dcim/devices/{sw['id']}/interfaces",
            json={"name": "core", "auto_link": True, "match_name": True, "inherit_device": True, "match_prefix": True},
        )
        assert created.status_code == 200, created.text
        body = created.json()
        assert body["ipam_vrf_id"] is None
        listed = client.get(f"/api/v1/dcim/devices/{sw['id']}/interfaces").json()
        assert listed[0]["ipam_vrf_id"] is None
        bad_site = client.patch(
            f"/api/v1/dcim/devices/{sw['id']}/interfaces/{body['id']}",
            json={"ipam_vrf_id": foreign["id"], "auto_link": True},
        )
        assert bad_site.status_code == 400
        assert bad_site.json()["detail"]["code"] == "iface_vrf_site"
        linked = client.patch(
            f"/api/v1/dcim/devices/{sw['id']}/interfaces/{body['id']}",
            json={"ipam_vrf_id": vrf["id"]},
        )
        assert linked.status_code == 200, linked.text
        assert linked.json()["ipam_vrf_id"] == vrf["id"]
        cleared = client.patch(
            f"/api/v1/dcim/devices/{sw['id']}/interfaces/{body['id']}",
            json={"ipam_vrf_id": None},
        )
        assert cleared.status_code == 200
        assert cleared.json()["ipam_vrf_id"] is None


def test_federation_exports_interface_vrf_by_slug() -> None:
    from app.core.db import SessionLocal
    from app.services import federation as fed_svc

    app = create_app()
    with TestClient(app) as client:
        tenant = client.post("/api/v1/tenants", json={"name": "Vrf Iface Fed", "slug": "vrf-41-fed"}).json()
        site = client.post(
            "/api/v1/dcim/sites",
            json={"name": "vrf-41-fed-oslo", "slug": "vrf-41-fed-oslo", "tenant_id": tenant["id"]},
        ).json()
        vrf = client.post(
            "/api/v1/ipam/vrfs",
            json={"site_id": site["id"], "name": "core", "slug": "vrf-41-fed-core"},
        ).json()
        sw = client.post("/api/v1/dcim/devices", json={"name": "sw-41-fed", "site_id": site["id"]}).json()
        iface = client.post(f"/api/v1/dcim/devices/{sw['id']}/interfaces", json={"name": "eth0"})
        assert iface.status_code == 200, iface.text
        snap_empty = client.get("/api/v1/federation/tenants/vrf-41-fed/snapshot")
        assert snap_empty.status_code == 200, snap_empty.text
        assert isinstance(snap_empty.json()["document"]["device_interface_vrfs"], list)
        assert all(r.get("interface_name") != "eth0" for r in snap_empty.json()["document"]["device_interface_vrfs"])
        linked = client.patch(
            f"/api/v1/dcim/devices/{sw['id']}/interfaces/{iface.json()['id']}",
            json={"ipam_vrf_id": vrf["id"]},
        )
        assert linked.status_code == 200, linked.text
        snap = client.get("/api/v1/federation/tenants/vrf-41-fed/snapshot")
        assert snap.status_code == 200, snap.text
        doc = snap.json()["document"]
        match = next(r for r in doc["device_interface_vrfs"] if r["interface_name"] == "eth0")
        assert match["device_name"] == "sw-41-fed"
        assert match["site_slug"] == "vrf-41-fed-oslo"
        assert match["vrf_slug"] == "vrf-41-fed-core"
        assert "route_distinguisher" not in match
        db = SessionLocal()
        try:
            checksum = fed_svc.apply_document_locally(db, doc)
            assert checksum == snap.json()["checksum"]
        finally:
            db.close()
        client.post("/api/v1/tenants", json={"name": "Rep 41", "slug": "rep-41-ivrf"})
        replica = {
            "apiVersion": "freehci.inventory/v1",
            "kind": "TenantInventory",
            "tenant": {"slug": "rep-41-ivrf", "name": "Rep 41", "description": None},
            "sites": [{"slug": "site-41-rep", "name": "Rep site", "description": None}],
            "rooms": [],
            "racks": [],
            "manufacturers": [],
            "device_types": [],
            "device_models": [],
            "device_roles": [],
            "devices": [{"name": "sw-41-rep", "site_slug": "site-41-rep"}],
            "device_artifacts": [],
            "device_artifact_records": [],
            "device_interfaces": [
                {"device_name": "sw-41-rep", "site_slug": "site-41-rep", "name": "eth0"}
            ],
            "device_interface_lags": [],
            "device_interface_vlans": [],
            "device_interface_vlan_members": [],
            "device_interface_vrfs": [],
            "device_interface_ips": [],
            "device_ips": [],
            "placements": [],
            "ipam": [
                {
                    "site": {"slug": "site-41-rep", "name": "Rep site"},
                    "vrfs": [{"name": "core", "slug": "vrf-41-rep-core"}],
                    "vlans": [],
                    "prefixes": [],
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
        replica_site = next(s for s in client.get("/api/v1/dcim/sites").json() if s["slug"] == "site-41-rep")
        replica_sw = next(
            d
            for d in client.get("/api/v1/dcim/devices").json()
            if d["name"] == "sw-41-rep" and d["site_id"] == replica_site["id"]
        )
        i0 = client.get(f"/api/v1/dcim/devices/{replica_sw['id']}/interfaces").json()
        assert i0[0]["ipam_vrf_id"] is None
        replica["device_interface_vrfs"] = [
            {
                "device_name": "sw-41-rep",
                "site_slug": "site-41-rep",
                "interface_name": "eth0",
                "vrf_slug": "vrf-41-rep-core",
                "match_name": True,
                "route_distinguisher": "65000:41",
            }
        ]
        db = SessionLocal()
        try:
            fed_svc.apply_document_locally(db, replica)
        finally:
            db.close()
        after = client.get(f"/api/v1/dcim/devices/{replica_sw['id']}/interfaces").json()
        vrf_rep = next(v for v in client.get(f"/api/v1/ipam/vrfs?site_id={replica_site['id']}").json() if v["slug"] == "vrf-41-rep-core")
        assert after[0]["ipam_vrf_id"] == vrf_rep["id"]
