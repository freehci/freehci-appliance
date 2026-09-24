"""Trinn 40: federer IP-tilknytning uten gjettet prefiks, primary eller VIP."""

from fastapi.testclient import TestClient

from app.main import create_app


def test_matching_cidr_is_not_a_prefix_link_or_primary() -> None:
    app = create_app()
    with TestClient(app) as client:
        site = client.post("/api/v1/dcim/sites", json={"name": "Ip 40", "slug": "site-40-ipas"}).json()
        pfx = client.post(
            "/api/v1/ipam/ipv4-prefixes",
            json={
                "site_id": site["id"],
                "name": "lan-40",
                "cidr": "10.219.97.0/28",
                "slug": "px-40-a",
                "role": "access",
                "status": "active",
            },
        )
        assert pfx.status_code == 200, pfx.text
        sw = client.post("/api/v1/dcim/devices", json={"name": "sw-40-a", "site_id": site["id"]}).json()
        iface = client.post(f"/api/v1/dcim/devices/{sw['id']}/interfaces", json={"name": "eth0"}).json()
        created = client.post(
            f"/api/v1/dcim/devices/{sw['id']}/interfaces/{iface['id']}/ip-assignments",
            json={
                "address": "10.219.97.1",
                "auto_link": True,
                "match_cidr": True,
                "vip": True,
                "anycast": True,
            },
        )
        assert created.status_code == 200, created.text
        body = created.json()
        assert body["address"] == "10.219.97.1"
        assert body["ipv4_prefix_id"] is None
        assert body["is_primary"] is False
        assert "vip" not in body
        assert "anycast" not in body
        linked = client.post(
            f"/api/v1/dcim/devices/{sw['id']}/interfaces/{iface['id']}/ip-assignments",
            json={"address": "10.219.97.2", "ipv4_prefix_id": pfx.json()["id"], "is_primary": True},
        )
        assert linked.status_code == 200, linked.text
        assert linked.json()["ipv4_prefix_id"] == pfx.json()["id"]
        assert linked.json()["is_primary"] is True
        listed = client.get(f"/api/v1/dcim/devices/{sw['id']}/interfaces").json()
        addrs = {a["address"]: a for a in listed[0]["ip_assignments"]}
        assert addrs["10.219.97.1"]["ipv4_prefix_id"] is None
        assert addrs["10.219.97.1"]["is_primary"] is False
        assert addrs["10.219.97.2"]["is_primary"] is True
        device_ip = client.post(
            f"/api/v1/dcim/devices/{sw['id']}/device-ip-assignments",
            json={"address": "10.219.97.3", "auto_link": True, "match_cidr": True},
        )
        assert device_ip.status_code == 200, device_ip.text
        assert device_ip.json()["ipv4_prefix_id"] is None
        assert device_ip.json()["is_primary"] is False


def test_federation_exports_ip_assignments_by_prefix_slug() -> None:
    from app.core.db import SessionLocal
    from app.services import federation as fed_svc

    app = create_app()
    with TestClient(app) as client:
        tenant = client.post("/api/v1/tenants", json={"name": "Ip Fed 40", "slug": "ip-40-fed"}).json()
        site = client.post(
            "/api/v1/dcim/sites",
            json={"name": "ip-40-fed-oslo", "slug": "ip-40-fed-oslo", "tenant_id": tenant["id"]},
        ).json()
        pfx = client.post(
            "/api/v1/ipam/ipv4-prefixes",
            json={
                "site_id": site["id"],
                "name": "lan-40-fed",
                "cidr": "10.219.97.16/28",
                "slug": "px-40-fed",
                "role": "access",
                "status": "active",
            },
        )
        assert pfx.status_code == 200, pfx.text
        sw = client.post("/api/v1/dcim/devices", json={"name": "sw-40-fed", "site_id": site["id"]}).json()
        snap_empty = client.get("/api/v1/federation/tenants/ip-40-fed/snapshot")
        assert snap_empty.status_code == 200, snap_empty.text
        assert isinstance(snap_empty.json()["document"]["device_interface_ips"], list)
        assert snap_empty.json()["document"]["device_interface_ips"] == []
        assert isinstance(snap_empty.json()["document"]["device_ips"], list)
        assert snap_empty.json()["document"]["device_ips"] == []
        iface = client.post(f"/api/v1/dcim/devices/{sw['id']}/interfaces", json={"name": "eth0"}).json()
        bound = client.post(
            f"/api/v1/dcim/devices/{sw['id']}/interfaces/{iface['id']}/ip-assignments",
            json={"address": "10.219.97.17", "ipv4_prefix_id": pfx.json()["id"], "is_primary": True},
        )
        assert bound.status_code == 200, bound.text
        loose = client.post(
            f"/api/v1/dcim/devices/{sw['id']}/device-ip-assignments",
            json={"address": "10.219.97.18"},
        )
        assert loose.status_code == 200, loose.text
        snap = client.get("/api/v1/federation/tenants/ip-40-fed/snapshot")
        assert snap.status_code == 200, snap.text
        doc = snap.json()["document"]
        iface_ip = next(r for r in doc["device_interface_ips"] if r["address"] == "10.219.97.17")
        assert iface_ip["device_name"] == "sw-40-fed"
        assert iface_ip["site_slug"] == "ip-40-fed-oslo"
        assert iface_ip["interface_name"] == "eth0"
        assert iface_ip["prefix_slug"] == "px-40-fed"
        assert iface_ip["is_primary"] is True
        assert "prefix_cidr" not in iface_ip
        assert "vip" not in iface_ip
        device_ip = next(r for r in doc["device_ips"] if r["address"] == "10.219.97.18")
        assert device_ip["prefix_slug"] is None
        assert device_ip["is_primary"] is False
        db = SessionLocal()
        try:
            checksum = fed_svc.apply_document_locally(db, doc)
            assert checksum == snap.json()["checksum"]
        finally:
            db.close()
        client.post("/api/v1/tenants", json={"name": "Rep 40", "slug": "rep-40-ipas"})
        replica = {
            "apiVersion": "freehci.inventory/v1",
            "kind": "TenantInventory",
            "tenant": {"slug": "rep-40-ipas", "name": "Rep 40", "description": None},
            "sites": [{"slug": "site-40-rep", "name": "Rep site", "description": None}],
            "rooms": [],
            "racks": [],
            "manufacturers": [],
            "device_types": [],
            "device_models": [],
            "device_roles": [],
            "devices": [{"name": "sw-40-rep", "site_slug": "site-40-rep"}],
            "device_artifacts": [],
            "device_artifact_records": [],
            "device_interfaces": [
                {
                    "device_name": "sw-40-rep",
                    "site_slug": "site-40-rep",
                    "name": "eth0",
                }
            ],
            "device_interface_lags": [],
            "device_interface_vlans": [],
            "device_interface_vlan_members": [],
            "device_interface_ips": [],
            "device_ips": [],
            "placements": [],
            "ipam": [
                {
                    "site": {"slug": "site-40-rep", "name": "Rep site"},
                    "vrfs": [],
                    "vlans": [],
                    "prefixes": [
                        {
                            "cidr": "10.219.97.32/28",
                            "slug": "px-40-rep",
                            "name": "rep-40",
                            "role": "access",
                            "status": "active",
                            "site_slug": "site-40-rep",
                        }
                    ],
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
        replica_site = next(s for s in client.get("/api/v1/dcim/sites").json() if s["slug"] == "site-40-rep")
        replica_sw = next(
            d
            for d in client.get("/api/v1/dcim/devices").json()
            if d["name"] == "sw-40-rep" and d["site_id"] == replica_site["id"]
        )
        replica_pfx = next(
            p
            for p in client.get(f"/api/v1/ipam/ipv4-prefixes?site_id={replica_site['id']}").json()
            if p["slug"] == "px-40-rep"
        )
        ifaces = client.get(f"/api/v1/dcim/devices/{replica_sw['id']}/interfaces").json()
        assert [i["name"] for i in ifaces] == ["eth0"]
        assert ifaces[0]["ip_assignments"] == []
        assert client.get(f"/api/v1/dcim/devices/{replica_sw['id']}/device-ip-assignments").json() == []
        replica["device_interface_ips"] = [
            {
                "device_name": "sw-40-rep",
                "site_slug": "site-40-rep",
                "interface_name": "eth0",
                "address": "10.219.97.33",
                "is_primary": True,
                "prefix_slug": "px-40-rep",
                "prefix_cidr": "10.219.97.32/28",
                "vip": True,
                "auto_link": True,
            },
            {
                "device_name": "sw-40-rep",
                "site_slug": "site-40-rep",
                "interface_name": "eth0",
                "address": "10.219.97.34",
                "match_cidr": True,
                "prefix_cidr": "10.219.97.32/28",
            },
        ]
        replica["device_ips"] = [
            {
                "device_name": "sw-40-rep",
                "site_slug": "site-40-rep",
                "address": "10.219.97.35",
                "match_cidr": True,
                "prefix_cidr": "10.219.97.32/28",
                "anycast": True,
            }
        ]
        db = SessionLocal()
        try:
            fed_svc.apply_document_locally(db, replica)
        finally:
            db.close()
        after_if = client.get(f"/api/v1/dcim/devices/{replica_sw['id']}/interfaces").json()
        addrs = {a["address"]: a for a in after_if[0]["ip_assignments"]}
        assert set(addrs) == {"10.219.97.33", "10.219.97.34"}
        assert addrs["10.219.97.33"]["ipv4_prefix_id"] == replica_pfx["id"]
        assert addrs["10.219.97.33"]["is_primary"] is True
        assert addrs["10.219.97.34"]["ipv4_prefix_id"] is None
        assert addrs["10.219.97.34"]["is_primary"] is False
        after_dev = client.get(f"/api/v1/dcim/devices/{replica_sw['id']}/device-ip-assignments").json()
        assert [a["address"] for a in after_dev] == ["10.219.97.35"]
        assert after_dev[0]["ipv4_prefix_id"] is None
        assert after_dev[0]["is_primary"] is False
