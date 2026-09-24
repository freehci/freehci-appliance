"""Trinn 37: eksplisitt IPAM-VLAN på grensesnitt uten gjettet medlemskap fra VID."""

from fastapi.testclient import TestClient

from app.main import create_app


def test_matching_vid_is_not_an_ipam_vlan_link() -> None:
    app = create_app()
    with TestClient(app) as client:
        site = client.post("/api/v1/dcim/sites", json={"name": "Vlan 37", "slug": "site-37-vlan"}).json()
        other = client.post("/api/v1/dcim/sites", json={"name": "Vlan 37 B", "slug": "site-37-vlan-b"}).json()
        vlan = client.post(
            "/api/v1/ipam/vlans",
            json={"site_id": site["id"], "vid": 100, "name": "access", "slug": "vlan-37-a"},
        ).json()
        foreign = client.post(
            "/api/v1/ipam/vlans",
            json={"site_id": other["id"], "vid": 100, "name": "access", "slug": "vlan-37-b"},
        ).json()
        sw = client.post("/api/v1/dcim/devices", json={"name": "sw-37-a", "site_id": site["id"]}).json()
        created = client.post(
            f"/api/v1/dcim/devices/{sw['id']}/interfaces",
            json={"name": "eth0", "vlan_id": 100, "auto_link": True, "match_vid": True, "tagged": True},
        )
        assert created.status_code == 200, created.text
        body = created.json()
        assert body["vlan_id"] == 100
        assert body["ipam_vlan_id"] is None
        assert "tagged" not in body
        listed = client.get(f"/api/v1/dcim/devices/{sw['id']}/interfaces").json()
        assert listed[0]["ipam_vlan_id"] is None
        bad_site = client.patch(
            f"/api/v1/dcim/devices/{sw['id']}/interfaces/{body['id']}",
            json={"ipam_vlan_id": foreign["id"], "auto_link": True},
        )
        assert bad_site.status_code == 400
        assert bad_site.json()["detail"]["code"] == "iface_vlan_site"
        mismatch = client.patch(
            f"/api/v1/dcim/devices/{sw['id']}/interfaces/{body['id']}",
            json={"vlan_id": 200, "ipam_vlan_id": vlan["id"]},
        )
        assert mismatch.status_code == 400
        assert mismatch.json()["detail"]["code"] == "iface_vlan_vid"
        linked = client.patch(
            f"/api/v1/dcim/devices/{sw['id']}/interfaces/{body['id']}",
            json={"ipam_vlan_id": vlan["id"], "native": True, "trunk": False},
        )
        assert linked.status_code == 200, linked.text
        assert linked.json()["ipam_vlan_id"] == vlan["id"]
        assert linked.json()["vlan_id"] == 100
        assert "native" not in linked.json()
        cleared = client.patch(
            f"/api/v1/dcim/devices/{sw['id']}/interfaces/{body['id']}",
            json={"ipam_vlan_id": None},
        )
        assert cleared.status_code == 200
        assert cleared.json()["ipam_vlan_id"] is None
        assert cleared.json()["vlan_id"] == 100


def test_federation_exports_interface_vlan_by_slug_not_vid() -> None:
    from app.core.db import SessionLocal
    from app.services import federation as fed_svc

    app = create_app()
    with TestClient(app) as client:
        tenant = client.post("/api/v1/tenants", json={"name": "Vlan Fed", "slug": "vlan-37-fed"}).json()
        site = client.post(
            "/api/v1/dcim/sites",
            json={"name": "vlan-37-fed-oslo", "slug": "vlan-37-fed-oslo", "tenant_id": tenant["id"]},
        ).json()
        vlan = client.post(
            "/api/v1/ipam/vlans",
            json={"site_id": site["id"], "vid": 100, "name": "access", "slug": "vlan-37-fed-a"},
        ).json()
        sw = client.post("/api/v1/dcim/devices", json={"name": "sw-37-fed", "site_id": site["id"]}).json()
        iface = client.post(
            f"/api/v1/dcim/devices/{sw['id']}/interfaces",
            json={"name": "eth0", "vlan_id": 100},
        )
        assert iface.status_code == 200, iface.text
        snap_empty = client.get("/api/v1/federation/tenants/vlan-37-fed/snapshot")
        assert snap_empty.status_code == 200, snap_empty.text
        assert isinstance(snap_empty.json()["document"]["device_interface_vlans"], list)
        assert all(r.get("interface_name") != "eth0" for r in snap_empty.json()["document"]["device_interface_vlans"])
        linked = client.patch(
            f"/api/v1/dcim/devices/{sw['id']}/interfaces/{iface.json()['id']}",
            json={"ipam_vlan_id": vlan["id"]},
        )
        assert linked.status_code == 200, linked.text
        snap = client.get("/api/v1/federation/tenants/vlan-37-fed/snapshot")
        assert snap.status_code == 200, snap.text
        doc = snap.json()["document"]
        match = next(r for r in doc["device_interface_vlans"] if r["interface_name"] == "eth0")
        assert match["device_name"] == "sw-37-fed"
        assert match["site_slug"] == "vlan-37-fed-oslo"
        assert match["vlan_slug"] == "vlan-37-fed-a"
        assert "vlan_vid" not in match
        db = SessionLocal()
        try:
            checksum = fed_svc.apply_document_locally(db, doc)
            assert checksum == snap.json()["checksum"]
        finally:
            db.close()
        client.post("/api/v1/tenants", json={"name": "Rep 37", "slug": "rep-37-vlan"})
        replica = {
            "apiVersion": "freehci.inventory/v1",
            "kind": "TenantInventory",
            "tenant": {"slug": "rep-37-vlan", "name": "Rep 37", "description": None},
            "sites": [{"slug": "site-37-rep", "name": "Rep site", "description": None}],
            "rooms": [],
            "racks": [],
            "manufacturers": [],
            "device_types": [],
            "device_models": [],
            "device_roles": [],
            "devices": [{"name": "sw-37-rep", "site_slug": "site-37-rep"}],
            "device_artifacts": [],
            "device_artifact_records": [],
            "device_interface_lags": [],
            "device_interface_vlans": [],
            "placements": [],
            "ipam": [],
            "clusters": [],
            "catalog_templates": [],
            "catalog_instances": [],
        }
        db = SessionLocal()
        try:
            fed_svc.apply_document_locally(db, replica)
        finally:
            db.close()
        replica_site = next(s for s in client.get("/api/v1/dcim/sites").json() if s["slug"] == "site-37-rep")
        replica_sw = next(
            d
            for d in client.get("/api/v1/dcim/devices").json()
            if d["name"] == "sw-37-rep" and d["site_id"] == replica_site["id"]
        )
        vlan_rep = client.post(
            "/api/v1/ipam/vlans",
            json={"site_id": replica_site["id"], "vid": 100, "name": "access", "slug": "vlan-37-rep-a"},
        )
        assert vlan_rep.status_code == 200, vlan_rep.text
        i0 = client.post(
            f"/api/v1/dcim/devices/{replica_sw['id']}/interfaces",
            json={"name": "eth0", "vlan_id": 100},
        )
        assert i0.status_code == 200, i0.text
        assert i0.json()["ipam_vlan_id"] is None
        replica["device_interface_vlans"] = [
            {
                "device_name": "sw-37-rep",
                "site_slug": "site-37-rep",
                "interface_name": "eth0",
                "vlan_slug": "vlan-37-rep-a",
                "vlan_vid": 100,
            }
        ]
        db = SessionLocal()
        try:
            fed_svc.apply_document_locally(db, replica)
        finally:
            db.close()
        after = client.get(f"/api/v1/dcim/devices/{replica_sw['id']}/interfaces").json()
        eth0 = next(i for i in after if i["name"] == "eth0")
        assert eth0["ipam_vlan_id"] == vlan_rep.json()["id"]
        assert eth0["vlan_id"] == 100
