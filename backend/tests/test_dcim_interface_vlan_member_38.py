"""Trinn 38: ekstra VLAN-medlemmer uten gjettet trunk, native eller primærkopiering."""

from fastapi.testclient import TestClient

from app.main import create_app


def test_matching_vid_is_not_a_vlan_member_until_posted() -> None:
    app = create_app()
    with TestClient(app) as client:
        site = client.post("/api/v1/dcim/sites", json={"name": "Vlan 38", "slug": "site-38-vmem"}).json()
        other = client.post("/api/v1/dcim/sites", json={"name": "Vlan 38 B", "slug": "site-38-vmem-b"}).json()
        vlan_a = client.post(
            "/api/v1/ipam/vlans",
            json={"site_id": site["id"], "vid": 100, "name": "access", "slug": "vlan-38-a"},
        ).json()
        vlan_b = client.post(
            "/api/v1/ipam/vlans",
            json={"site_id": site["id"], "vid": 200, "name": "voice", "slug": "vlan-38-b"},
        ).json()
        foreign = client.post(
            "/api/v1/ipam/vlans",
            json={"site_id": other["id"], "vid": 100, "name": "access", "slug": "vlan-38-foreign"},
        ).json()
        sw = client.post("/api/v1/dcim/devices", json={"name": "sw-38-a", "site_id": site["id"]}).json()
        iface = client.post(
            f"/api/v1/dcim/devices/{sw['id']}/interfaces",
            json={"name": "eth0", "vlan_id": 100, "auto_link": True, "match_vid": True},
        )
        assert iface.status_code == 200, iface.text
        assert iface.json()["vlan_id"] == 100
        assert iface.json()["ipam_vlan_id"] is None
        listed = client.get(f"/api/v1/dcim/devices/{sw['id']}/interface-vlans")
        assert listed.status_code == 200, listed.text
        assert listed.json() == []
        extras = client.post(
            f"/api/v1/dcim/devices/{sw['id']}/interfaces/{iface.json()['id']}/vlans",
            json={
                "ipam_vlan_id": vlan_b["id"],
                "allowed_vlans": "100,200",
                "trunk": True,
                "pvid": 100,
            },
        )
        assert extras.status_code == 200, extras.text
        body = extras.json()
        assert body["interface_name"] == "eth0"
        assert body["ipam_vlan_id"] == vlan_b["id"]
        assert body["vlan_vid"] == 200
        assert body["vlan_slug"] == "vlan-38-b"
        assert body["role"] is None
        assert "allowed_vlans" not in body
        assert "trunk" not in body
        assert "pvid" not in body
        listed = client.get(f"/api/v1/dcim/devices/{sw['id']}/interface-vlans").json()
        assert [r["vlan_slug"] for r in listed] == ["vlan-38-b"]
        again = client.post(
            f"/api/v1/dcim/devices/{sw['id']}/interfaces/{iface.json()['id']}/vlans",
            json={"ipam_vlan_id": vlan_b["id"], "role": "tagged"},
        )
        assert again.status_code == 409
        assert again.json()["detail"]["code"] == "iface_vlan_member_taken"
        bad_site = client.post(
            f"/api/v1/dcim/devices/{sw['id']}/interfaces/{iface.json()['id']}/vlans",
            json={"ipam_vlan_id": foreign["id"]},
        )
        assert bad_site.status_code == 400
        assert bad_site.json()["detail"]["code"] == "iface_vlan_site"
        bad_role = client.post(
            f"/api/v1/dcim/devices/{sw['id']}/interfaces/{iface.json()['id']}/vlans",
            json={"ipam_vlan_id": vlan_a["id"], "role": "trunk"},
        )
        assert bad_role.status_code == 400
        assert bad_role.json()["detail"]["code"] == "iface_vlan_role"
        tagged = client.post(
            f"/api/v1/dcim/devices/{sw['id']}/interfaces/{iface.json()['id']}/vlans",
            json={"ipam_vlan_id": vlan_a["id"], "role": "tagged"},
        )
        assert tagged.status_code == 200, tagged.text
        assert tagged.json()["role"] == "tagged"
        assert tagged.json()["vlan_slug"] == "vlan-38-a"
        assert client.delete(f"/api/v1/dcim/interface-vlans/{tagged.json()['id']}").status_code == 204
        remaining = client.get(f"/api/v1/dcim/devices/{sw['id']}/interface-vlans").json()
        assert [r["vlan_slug"] for r in remaining] == ["vlan-38-b"]
        linked = client.patch(
            f"/api/v1/dcim/devices/{sw['id']}/interfaces/{iface.json()['id']}",
            json={"ipam_vlan_id": vlan_a["id"]},
        )
        assert linked.status_code == 200, linked.text
        assert linked.json()["ipam_vlan_id"] == vlan_a["id"]
        still = client.get(f"/api/v1/dcim/devices/{sw['id']}/interface-vlans").json()
        assert [r["vlan_slug"] for r in still] == ["vlan-38-b"]
        copied = client.post(
            f"/api/v1/dcim/devices/{sw['id']}/interfaces/{iface.json()['id']}/vlans",
            json={"ipam_vlan_id": vlan_a["id"], "role": "native"},
        )
        assert copied.status_code == 409
        assert copied.json()["detail"]["code"] == "iface_vlan_member_taken"


def test_federation_exports_interface_vlan_members_by_slug() -> None:
    from app.core.db import SessionLocal
    from app.services import federation as fed_svc

    app = create_app()
    with TestClient(app) as client:
        tenant = client.post("/api/v1/tenants", json={"name": "Vlan Mem Fed", "slug": "vlan-38-fed"}).json()
        site = client.post(
            "/api/v1/dcim/sites",
            json={"name": "vlan-38-fed-oslo", "slug": "vlan-38-fed-oslo", "tenant_id": tenant["id"]},
        ).json()
        vlan = client.post(
            "/api/v1/ipam/vlans",
            json={"site_id": site["id"], "vid": 200, "name": "voice", "slug": "vlan-38-fed-b"},
        ).json()
        sw = client.post("/api/v1/dcim/devices", json={"name": "sw-38-fed", "site_id": site["id"]}).json()
        iface = client.post(
            f"/api/v1/dcim/devices/{sw['id']}/interfaces",
            json={"name": "eth0", "vlan_id": 100},
        )
        assert iface.status_code == 200, iface.text
        snap_empty = client.get("/api/v1/federation/tenants/vlan-38-fed/snapshot")
        assert snap_empty.status_code == 200, snap_empty.text
        assert isinstance(snap_empty.json()["document"]["device_interface_vlan_members"], list)
        assert all(
            r.get("interface_name") != "eth0"
            for r in snap_empty.json()["document"]["device_interface_vlan_members"]
        )
        bound = client.post(
            f"/api/v1/dcim/devices/{sw['id']}/interfaces/{iface.json()['id']}/vlans",
            json={"ipam_vlan_id": vlan["id"], "role": "tagged"},
        )
        assert bound.status_code == 200, bound.text
        snap = client.get("/api/v1/federation/tenants/vlan-38-fed/snapshot")
        assert snap.status_code == 200, snap.text
        doc = snap.json()["document"]
        match = next(r for r in doc["device_interface_vlan_members"] if r["interface_name"] == "eth0")
        assert match["device_name"] == "sw-38-fed"
        assert match["site_slug"] == "vlan-38-fed-oslo"
        assert match["vlan_slug"] == "vlan-38-fed-b"
        assert match["role"] == "tagged"
        assert "vlan_vid" not in match
        db = SessionLocal()
        try:
            checksum = fed_svc.apply_document_locally(db, doc)
            assert checksum == snap.json()["checksum"]
        finally:
            db.close()
        client.post("/api/v1/tenants", json={"name": "Rep 38", "slug": "rep-38-vmem"})
        replica = {
            "apiVersion": "freehci.inventory/v1",
            "kind": "TenantInventory",
            "tenant": {"slug": "rep-38-vmem", "name": "Rep 38", "description": None},
            "sites": [{"slug": "site-38-rep", "name": "Rep site", "description": None}],
            "rooms": [],
            "racks": [],
            "manufacturers": [],
            "device_types": [],
            "device_models": [],
            "device_roles": [],
            "devices": [{"name": "sw-38-rep", "site_slug": "site-38-rep"}],
            "device_artifacts": [],
            "device_artifact_records": [],
            "device_interface_lags": [],
            "device_interface_vlans": [],
            "device_interface_vlan_members": [],
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
        replica_site = next(s for s in client.get("/api/v1/dcim/sites").json() if s["slug"] == "site-38-rep")
        replica_sw = next(
            d
            for d in client.get("/api/v1/dcim/devices").json()
            if d["name"] == "sw-38-rep" and d["site_id"] == replica_site["id"]
        )
        vlan_rep = client.post(
            "/api/v1/ipam/vlans",
            json={"site_id": replica_site["id"], "vid": 200, "name": "voice", "slug": "vlan-38-rep-b"},
        )
        assert vlan_rep.status_code == 200, vlan_rep.text
        i0 = client.post(
            f"/api/v1/dcim/devices/{replica_sw['id']}/interfaces",
            json={"name": "eth0", "vlan_id": 100},
        )
        assert i0.status_code == 200, i0.text
        assert client.get(f"/api/v1/dcim/devices/{replica_sw['id']}/interface-vlans").json() == []
        replica["device_interface_vlan_members"] = [
            {
                "device_name": "sw-38-rep",
                "site_slug": "site-38-rep",
                "interface_name": "eth0",
                "vlan_slug": "vlan-38-rep-b",
                "role": "tagged",
                "vlan_vid": 200,
                "trunk": True,
            }
        ]
        db = SessionLocal()
        try:
            fed_svc.apply_document_locally(db, replica)
        finally:
            db.close()
        after = client.get(f"/api/v1/dcim/devices/{replica_sw['id']}/interface-vlans").json()
        assert [r["vlan_slug"] for r in after] == ["vlan-38-rep-b"]
        assert after[0]["role"] == "tagged"
        assert after[0]["vlan_vid"] == 200
        iface_after = client.get(f"/api/v1/dcim/devices/{replica_sw['id']}/interfaces").json()
        eth0 = next(i for i in iface_after if i["name"] == "eth0")
        assert eth0["ipam_vlan_id"] is None
        assert eth0["vlan_id"] == 100
