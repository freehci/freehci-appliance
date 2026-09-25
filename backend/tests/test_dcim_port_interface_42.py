"""Trinn 42: eksplisitt port-til-grensesnitt uten gjettet kobling fra samme navn."""

from fastapi.testclient import TestClient

from app.main import create_app


def test_matching_name_is_not_a_port_interface() -> None:
    app = create_app()
    with TestClient(app) as client:
        site = client.post("/api/v1/dcim/sites", json={"name": "Port 42", "slug": "site-42-pif"}).json()
        other = client.post("/api/v1/dcim/sites", json={"name": "Port 42 B", "slug": "site-42-pif-b"}).json()
        sw = client.post("/api/v1/dcim/devices", json={"name": "sw-42-a", "site_id": site["id"]}).json()
        peer = client.post("/api/v1/dcim/devices", json={"name": "sw-42-b", "site_id": other["id"]}).json()
        iface = client.post(f"/api/v1/dcim/devices/{sw['id']}/interfaces", json={"name": "eth0"})
        assert iface.status_code == 200, iface.text
        foreign = client.post(f"/api/v1/dcim/devices/{peer['id']}/interfaces", json={"name": "eth0"})
        assert foreign.status_code == 200, foreign.text
        created = client.post(
            f"/api/v1/dcim/devices/{sw['id']}/ports",
            json={"kind": "front-port", "name": "eth0", "auto_link": True, "match_name": True},
        )
        assert created.status_code == 200, created.text
        assert created.json()["interface_id"] is None
        listed = client.get(f"/api/v1/dcim/devices/{sw['id']}/ports").json()
        assert listed[0]["interface_id"] is None
        power = client.post(
            f"/api/v1/dcim/devices/{sw['id']}/ports",
            json={"kind": "power-port", "name": "PSU0", "interface_id": iface.json()["id"]},
        )
        assert power.status_code == 400
        assert power.json()["detail"]["code"] == "port_iface_kind"
        bad_dev = client.patch(
            f"/api/v1/dcim/device-ports/{created.json()['id']}",
            json={"interface_id": foreign.json()["id"], "auto_link": True},
        )
        assert bad_dev.status_code == 400
        assert bad_dev.json()["detail"]["code"] == "port_iface_device"
        linked = client.patch(
            f"/api/v1/dcim/device-ports/{created.json()['id']}",
            json={"interface_id": iface.json()["id"]},
        )
        assert linked.status_code == 200, linked.text
        assert linked.json()["interface_id"] == iface.json()["id"]
        other_port = client.post(
            f"/api/v1/dcim/devices/{sw['id']}/ports",
            json={"kind": "rear-port", "name": "eth0", "interface_id": iface.json()["id"]},
        )
        assert other_port.status_code == 409
        assert other_port.json()["detail"]["code"] == "port_iface_taken"
        cleared = client.patch(
            f"/api/v1/dcim/device-ports/{created.json()['id']}",
            json={"interface_id": None},
        )
        assert cleared.status_code == 200
        assert cleared.json()["interface_id"] is None


def test_federation_exports_port_interface_by_name() -> None:
    from app.core.db import SessionLocal
    from app.services import federation as fed_svc

    app = create_app()
    with TestClient(app) as client:
        tenant = client.post("/api/v1/tenants", json={"name": "Port Iface Fed", "slug": "pif-42-fed"}).json()
        site = client.post(
            "/api/v1/dcim/sites",
            json={"name": "pif-42-fed-oslo", "slug": "pif-42-fed-oslo", "tenant_id": tenant["id"]},
        ).json()
        sw = client.post("/api/v1/dcim/devices", json={"name": "sw-42-fed", "site_id": site["id"]}).json()
        iface = client.post(f"/api/v1/dcim/devices/{sw['id']}/interfaces", json={"name": "eth0"})
        assert iface.status_code == 200, iface.text
        port = client.post(
            f"/api/v1/dcim/devices/{sw['id']}/ports",
            json={"kind": "front-port", "name": "eth0"},
        )
        assert port.status_code == 200, port.text
        snap_empty = client.get("/api/v1/federation/tenants/pif-42-fed/snapshot")
        assert snap_empty.status_code == 200, snap_empty.text
        assert isinstance(snap_empty.json()["document"]["device_port_interfaces"], list)
        assert all(r.get("port_name") != "eth0" for r in snap_empty.json()["document"]["device_port_interfaces"])
        linked = client.patch(
            f"/api/v1/dcim/device-ports/{port.json()['id']}",
            json={"interface_id": iface.json()["id"]},
        )
        assert linked.status_code == 200, linked.text
        snap = client.get("/api/v1/federation/tenants/pif-42-fed/snapshot")
        assert snap.status_code == 200, snap.text
        doc = snap.json()["document"]
        match = next(r for r in doc["device_port_interfaces"] if r["port_name"] == "eth0")
        assert match["device_name"] == "sw-42-fed"
        assert match["site_slug"] == "pif-42-fed-oslo"
        assert match["port_kind"] == "front-port"
        assert match["interface_name"] == "eth0"
        db = SessionLocal()
        try:
            checksum = fed_svc.apply_document_locally(db, doc)
            assert checksum == snap.json()["checksum"]
        finally:
            db.close()
        client.post("/api/v1/tenants", json={"name": "Rep 42", "slug": "rep-42-pif"})
        replica = {
            "apiVersion": "freehci.inventory/v1",
            "kind": "TenantInventory",
            "tenant": {"slug": "rep-42-pif", "name": "Rep 42", "description": None},
            "sites": [{"slug": "site-42-rep", "name": "Rep site", "description": None}],
            "rooms": [],
            "racks": [],
            "manufacturers": [],
            "device_types": [],
            "device_models": [],
            "device_roles": [],
            "devices": [{"name": "sw-42-rep", "site_slug": "site-42-rep"}],
            "device_artifacts": [],
            "device_artifact_records": [],
            "device_interfaces": [{"device_name": "sw-42-rep", "site_slug": "site-42-rep", "name": "eth0"}],
            "device_interface_lags": [],
            "device_interface_vlans": [],
            "device_interface_vlan_members": [],
            "device_interface_vrfs": [],
            "device_interface_ips": [],
            "device_ips": [],
            "device_port_interfaces": [],
            "device_ports": [
                {"device_name": "sw-42-rep", "kind": "front-port", "name": "eth0", "interface_name": "eth0"}
            ],
            "placements": [],
            "ipam": [{"site": {"slug": "site-42-rep", "name": "Rep site"}, "vrfs": [], "vlans": [], "prefixes": []}],
            "clusters": [],
            "catalog_templates": [],
            "catalog_instances": [],
        }
        db = SessionLocal()
        try:
            fed_svc.apply_document_locally(db, replica)
        finally:
            db.close()
        replica_site = next(s for s in client.get("/api/v1/dcim/sites").json() if s["slug"] == "site-42-rep")
        replica_sw = next(
            d
            for d in client.get("/api/v1/dcim/devices").json()
            if d["name"] == "sw-42-rep" and d["site_id"] == replica_site["id"]
        )
        ports0 = client.get(f"/api/v1/dcim/devices/{replica_sw['id']}/ports").json()
        assert ports0[0]["interface_id"] is None
        replica["device_port_interfaces"] = [
            {
                "device_name": "sw-42-rep",
                "site_slug": "site-42-rep",
                "port_kind": "front-port",
                "port_name": "eth0",
                "interface_name": "eth0",
                "match_name": True,
                "auto_link": True,
            }
        ]
        db = SessionLocal()
        try:
            fed_svc.apply_document_locally(db, replica)
        finally:
            db.close()
        after = client.get(f"/api/v1/dcim/devices/{replica_sw['id']}/ports").json()
        iface_rep = client.get(f"/api/v1/dcim/devices/{replica_sw['id']}/interfaces").json()
        assert after[0]["interface_id"] == iface_rep[0]["id"]
