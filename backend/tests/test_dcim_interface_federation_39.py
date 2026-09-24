"""Trinn 39: federer registrerte grensesnitt uten gjettet parent, MAC eller hastighet."""

from fastapi.testclient import TestClient

from app.main import create_app


def test_dotted_name_and_speed_label_are_not_interfaces_until_exported() -> None:
    app = create_app()
    with TestClient(app) as client:
        site = client.post("/api/v1/dcim/sites", json={"name": "Iface 39", "slug": "site-39-iface"}).json()
        sw = client.post("/api/v1/dcim/devices", json={"name": "sw-39-a", "site_id": site["id"]}).json()
        eth0 = client.post(
            f"/api/v1/dcim/devices/{sw['id']}/interfaces",
            json={"name": "eth0", "auto_parent": True, "infer_speed": "10G"},
        )
        assert eth0.status_code == 200, eth0.text
        assert eth0.json()["parent_interface_id"] is None
        assert eth0.json()["speed_mbps"] is None
        assert eth0.json()["mac_address"] is None
        child = client.post(
            f"/api/v1/dcim/devices/{sw['id']}/interfaces",
            json={"name": "eth0.100", "vlan_id": 100, "auto_parent": True, "match_name": True},
        )
        assert child.status_code == 200, child.text
        assert child.json()["parent_interface_id"] is None
        assert child.json()["vlan_id"] == 100
        linked = client.post(
            f"/api/v1/dcim/devices/{sw['id']}/interfaces",
            json={"name": "eth0.200", "parent_interface_id": eth0.json()["id"], "vlan_id": 200},
        )
        assert linked.status_code == 200, linked.text
        assert linked.json()["parent_interface_id"] == eth0.json()["id"]


def test_federation_exports_interfaces_and_applies_without_inventing_parent() -> None:
    from app.core.db import SessionLocal
    from app.services import federation as fed_svc

    app = create_app()
    with TestClient(app) as client:
        tenant = client.post("/api/v1/tenants", json={"name": "Iface Fed", "slug": "iface-39-fed"}).json()
        site = client.post(
            "/api/v1/dcim/sites",
            json={"name": "iface-39-fed-oslo", "slug": "iface-39-fed-oslo", "tenant_id": tenant["id"]},
        ).json()
        sw = client.post("/api/v1/dcim/devices", json={"name": "sw-39-fed", "site_id": site["id"]}).json()
        snap_empty = client.get("/api/v1/federation/tenants/iface-39-fed/snapshot")
        assert snap_empty.status_code == 200, snap_empty.text
        assert isinstance(snap_empty.json()["document"]["device_interfaces"], list)
        assert snap_empty.json()["document"]["device_interfaces"] == []
        eth0 = client.post(
            f"/api/v1/dcim/devices/{sw['id']}/interfaces",
            json={"name": "eth0", "speed_mbps": 10000, "mac_address": "00:11:22:33:44:55"},
        )
        assert eth0.status_code == 200, eth0.text
        sub = client.post(
            f"/api/v1/dcim/devices/{sw['id']}/interfaces",
            json={"name": "eth0.100", "parent_interface_id": eth0.json()["id"], "vlan_id": 100},
        )
        assert sub.status_code == 200, sub.text
        dotted = client.post(
            f"/api/v1/dcim/devices/{sw['id']}/interfaces",
            json={"name": "TenGigE0/1.50", "vlan_id": 50},
        )
        assert dotted.status_code == 200, dotted.text
        snap = client.get("/api/v1/federation/tenants/iface-39-fed/snapshot")
        assert snap.status_code == 200, snap.text
        doc = snap.json()["document"]
        names = {r["name"]: r for r in doc["device_interfaces"]}
        assert set(names) == {"eth0", "eth0.100", "TenGigE0/1.50"}
        assert names["eth0"]["device_name"] == "sw-39-fed"
        assert names["eth0"]["site_slug"] == "iface-39-fed-oslo"
        assert names["eth0"]["speed_mbps"] == 10000
        assert names["eth0"]["mac_address"] == "00:11:22:33:44:55"
        assert names["eth0"]["parent_name"] is None
        assert names["eth0.100"]["parent_name"] == "eth0"
        assert names["eth0.100"]["vlan_id"] == 100
        assert names["TenGigE0/1.50"]["parent_name"] is None
        assert names["TenGigE0/1.50"]["speed_mbps"] is None
        assert "ipam_vlan_id" not in names["eth0"]
        db = SessionLocal()
        try:
            checksum = fed_svc.apply_document_locally(db, doc)
            assert checksum == snap.json()["checksum"]
        finally:
            db.close()
        client.post("/api/v1/tenants", json={"name": "Rep 39", "slug": "rep-39-iface"})
        replica = {
            "apiVersion": "freehci.inventory/v1",
            "kind": "TenantInventory",
            "tenant": {"slug": "rep-39-iface", "name": "Rep 39", "description": None},
            "sites": [{"slug": "site-39-rep", "name": "Rep site", "description": None}],
            "rooms": [],
            "racks": [],
            "manufacturers": [],
            "device_types": [],
            "device_models": [],
            "device_roles": [],
            "devices": [{"name": "sw-39-rep", "site_slug": "site-39-rep"}],
            "device_artifacts": [],
            "device_artifact_records": [],
            "device_interfaces": [],
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
        replica_site = next(s for s in client.get("/api/v1/dcim/sites").json() if s["slug"] == "site-39-rep")
        replica_sw = next(
            d
            for d in client.get("/api/v1/dcim/devices").json()
            if d["name"] == "sw-39-rep" and d["site_id"] == replica_site["id"]
        )
        assert client.get(f"/api/v1/dcim/devices/{replica_sw['id']}/interfaces").json() == []
        replica["device_interfaces"] = [
            {
                "device_name": "sw-39-rep",
                "site_slug": "site-39-rep",
                "name": "eth0.100",
                "parent_name": "eth0",
                "vlan_id": 100,
                "auto_parent": True,
            },
            {
                "device_name": "sw-39-rep",
                "site_slug": "site-39-rep",
                "name": "eth0",
                "speed_mbps": 10000,
                "mac_address": "00:11:22:33:44:55",
                "infer_speed": "10G",
            },
            {
                "device_name": "sw-39-rep",
                "site_slug": "site-39-rep",
                "name": "TenGigE0/1.50",
                "vlan_id": 50,
                "auto_parent": True,
                "infer_speed": "10G",
                "match_name": True,
            },
        ]
        replica["device_interface_lags"] = [
            {
                "device_name": "sw-39-rep",
                "site_slug": "site-39-rep",
                "slug": "ae0",
                "name": "ae0",
                "description": None,
                "interface_names": ["eth0"],
            }
        ]
        db = SessionLocal()
        try:
            fed_svc.apply_document_locally(db, replica)
        finally:
            db.close()
        after = {i["name"]: i for i in client.get(f"/api/v1/dcim/devices/{replica_sw['id']}/interfaces").json()}
        assert set(after) == {"eth0", "eth0.100", "TenGigE0/1.50"}
        assert after["eth0"]["speed_mbps"] == 10000
        assert after["eth0"]["mac_address"] == "00:11:22:33:44:55"
        assert after["eth0"]["parent_interface_id"] is None
        assert after["eth0.100"]["parent_interface_id"] == after["eth0"]["id"]
        assert after["eth0.100"]["vlan_id"] == 100
        assert after["TenGigE0/1.50"]["parent_interface_id"] is None
        assert after["TenGigE0/1.50"]["speed_mbps"] is None
        assert after["TenGigE0/1.50"]["mac_address"] is None
        lags = client.get(f"/api/v1/dcim/devices/{replica_sw['id']}/interface-lags").json()
        assert [r["slug"] for r in lags] == ["ae0"]
        assert [m["interface_name"] for m in lags[0]["members"]] == ["eth0"]
