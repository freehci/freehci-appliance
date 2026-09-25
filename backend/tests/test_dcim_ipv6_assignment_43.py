"""Trinn 43: eksplisitt IPv6-prefiks på IP-tilknytning uten gjettet CIDR-kobling."""

from fastapi.testclient import TestClient

from app.main import create_app


def test_matching_ipv6_cidr_is_not_a_prefix_link() -> None:
    app = create_app()
    with TestClient(app) as client:
        site = client.post("/api/v1/dcim/sites", json={"name": "V6 43", "slug": "site-43-v6ip"}).json()
        other = client.post("/api/v1/dcim/sites", json={"name": "V6 43 B", "slug": "site-43-v6ip-b"}).json()
        pfx = client.post(
            "/api/v1/ipam/ipv6-prefixes",
            json={
                "site_id": site["id"],
                "name": "lan-43",
                "cidr": "2001:db8:43::/64",
                "slug": "px-43-a",
                "role": "access",
                "status": "active",
            },
        )
        assert pfx.status_code == 200, pfx.text
        foreign = client.post(
            "/api/v1/ipam/ipv6-prefixes",
            json={
                "site_id": other["id"],
                "name": "lan-43-b",
                "cidr": "2001:db8:43::/64",
                "slug": "px-43-b",
                "role": "access",
                "status": "active",
            },
        )
        assert foreign.status_code == 200, foreign.text
        sw = client.post("/api/v1/dcim/devices", json={"name": "sw-43-a", "site_id": site["id"]}).json()
        iface = client.post(f"/api/v1/dcim/devices/{sw['id']}/interfaces", json={"name": "eth0"}).json()
        created = client.post(
            f"/api/v1/dcim/devices/{sw['id']}/interfaces/{iface['id']}/ip-assignments",
            json={
                "address": "2001:db8:43::1",
                "auto_link": True,
                "match_cidr": True,
                "prefix_cidr": "2001:db8:43::/64",
            },
        )
        assert created.status_code == 200, created.text
        body = created.json()
        assert body["address"] == "2001:db8:43::1"
        assert body["family"] == "ipv6"
        assert body["ipv6_prefix_id"] is None
        assert body["ipv4_prefix_id"] is None
        assert body["is_primary"] is False
        bad_site = client.post(
            f"/api/v1/dcim/devices/{sw['id']}/interfaces/{iface['id']}/ip-assignments",
            json={"address": "2001:db8:43::2", "ipv6_prefix_id": foreign.json()["id"]},
        )
        assert bad_site.status_code == 400
        assert bad_site.json()["detail"]["code"] == "iface_ip_v6pfx_site"
        linked = client.post(
            f"/api/v1/dcim/devices/{sw['id']}/interfaces/{iface['id']}/ip-assignments",
            json={"address": "2001:db8:43::2", "ipv6_prefix_id": pfx.json()["id"], "is_primary": True},
        )
        assert linked.status_code == 200, linked.text
        assert linked.json()["ipv6_prefix_id"] == pfx.json()["id"]
        assert linked.json()["is_primary"] is True
        v4_on_v6 = client.patch(
            f"/api/v1/dcim/devices/{sw['id']}/interfaces/{iface['id']}/ip-assignments/{linked.json()['id']}",
            json={"ipv4_prefix_id": 1, "auto_link": True},
        )
        assert v4_on_v6.status_code == 400
        device_ip = client.post(
            f"/api/v1/dcim/devices/{sw['id']}/device-ip-assignments",
            json={"address": "2001:db8:43::3", "auto_link": True, "match_cidr": True},
        )
        assert device_ip.status_code == 200, device_ip.text
        assert device_ip.json()["ipv6_prefix_id"] is None
        assert device_ip.json()["is_primary"] is False
        cleared = client.patch(
            f"/api/v1/dcim/devices/{sw['id']}/interfaces/{iface['id']}/ip-assignments/{linked.json()['id']}",
            json={"ipv6_prefix_id": None},
        )
        assert cleared.status_code == 200
        assert cleared.json()["ipv6_prefix_id"] is None


def test_federation_exports_ipv6_assignment_by_prefix_slug() -> None:
    from app.core.db import SessionLocal
    from app.services import federation as fed_svc

    app = create_app()
    with TestClient(app) as client:
        tenant = client.post("/api/v1/tenants", json={"name": "V6 Fed 43", "slug": "v6-43-fed"}).json()
        site = client.post(
            "/api/v1/dcim/sites",
            json={"name": "v6-43-fed-oslo", "slug": "v6-43-fed-oslo", "tenant_id": tenant["id"]},
        ).json()
        pfx = client.post(
            "/api/v1/ipam/ipv6-prefixes",
            json={
                "site_id": site["id"],
                "name": "lan-43-fed",
                "cidr": "2001:db8:43:1::/64",
                "slug": "px-43-fed",
                "role": "access",
                "status": "active",
            },
        )
        assert pfx.status_code == 200, pfx.text
        sw = client.post("/api/v1/dcim/devices", json={"name": "sw-43-fed", "site_id": site["id"]}).json()
        iface = client.post(f"/api/v1/dcim/devices/{sw['id']}/interfaces", json={"name": "eth0"}).json()
        created = client.post(
            f"/api/v1/dcim/devices/{sw['id']}/interfaces/{iface['id']}/ip-assignments",
            json={"address": "2001:db8:43:1::1", "ipv6_prefix_id": pfx.json()["id"], "is_primary": True},
        )
        assert created.status_code == 200, created.text
        snap = client.get("/api/v1/federation/tenants/v6-43-fed/snapshot")
        assert snap.status_code == 200, snap.text
        doc = snap.json()["document"]
        assert isinstance(doc["device_interface_ips"], list)
        match = next(r for r in doc["device_interface_ips"] if r["address"] == "2001:db8:43:1::1")
        assert match["device_name"] == "sw-43-fed"
        assert match["site_slug"] == "v6-43-fed-oslo"
        assert match["interface_name"] == "eth0"
        assert match["prefix_slug"] == "px-43-fed"
        assert match["is_primary"] is True
        db = SessionLocal()
        try:
            checksum = fed_svc.apply_document_locally(db, doc)
            assert checksum == snap.json()["checksum"]
        finally:
            db.close()
        client.post("/api/v1/tenants", json={"name": "Rep 43", "slug": "rep-43-v6ip"})
        replica = {
            "apiVersion": "freehci.inventory/v1",
            "kind": "TenantInventory",
            "tenant": {"slug": "rep-43-v6ip", "name": "Rep 43", "description": None},
            "sites": [{"slug": "site-43-rep", "name": "Rep site", "description": None}],
            "rooms": [],
            "racks": [],
            "manufacturers": [],
            "device_types": [],
            "device_models": [],
            "device_roles": [],
            "devices": [{"name": "sw-43-rep", "site_slug": "site-43-rep"}],
            "device_artifacts": [],
            "device_artifact_records": [],
            "device_interfaces": [{"device_name": "sw-43-rep", "site_slug": "site-43-rep", "name": "eth0"}],
            "device_interface_lags": [],
            "device_interface_vlans": [],
            "device_interface_vlan_members": [],
            "device_interface_vrfs": [],
            "device_interface_ips": [],
            "device_ips": [],
            "device_port_interfaces": [],
            "placements": [],
            "ipam": [
                {
                    "site": {"slug": "site-43-rep", "name": "Rep site"},
                    "vrfs": [],
                    "vlans": [],
                    "prefixes": [],
                    "ipv6_prefixes": [
                        {"cidr": "2001:db8:43:2::/64", "slug": "px-43-rep", "role": "access", "status": "active"}
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
        replica_site = next(s for s in client.get("/api/v1/dcim/sites").json() if s["slug"] == "site-43-rep")
        replica_sw = next(
            d
            for d in client.get("/api/v1/dcim/devices").json()
            if d["name"] == "sw-43-rep" and d["site_id"] == replica_site["id"]
        )
        replica["device_interface_ips"] = [
            {
                "device_name": "sw-43-rep",
                "site_slug": "site-43-rep",
                "interface_name": "eth0",
                "address": "2001:db8:43:2::1",
                "prefix_cidr": "2001:db8:43:2::/64",
                "auto_link": True,
                "match_cidr": True,
            }
        ]
        db = SessionLocal()
        try:
            fed_svc.apply_document_locally(db, replica)
        finally:
            db.close()
        after = client.get(f"/api/v1/dcim/devices/{replica_sw['id']}/interfaces").json()
        addrs = after[0]["ip_assignments"]
        assert addrs[0]["address"] == "2001:db8:43:2::1"
        assert addrs[0]["ipv6_prefix_id"] is None
        replica["device_interface_ips"] = [
            {
                "device_name": "sw-43-rep",
                "site_slug": "site-43-rep",
                "interface_name": "eth0",
                "address": "2001:db8:43:2::2",
                "prefix_slug": "px-43-rep",
                "is_primary": True,
            }
        ]
        db = SessionLocal()
        try:
            fed_svc.apply_document_locally(db, replica)
        finally:
            db.close()
        linked = client.get(f"/api/v1/dcim/devices/{replica_sw['id']}/interfaces").json()[0]["ip_assignments"]
        pfx_rep = next(
            p
            for p in client.get(f"/api/v1/ipam/ipv6-prefixes?site_id={replica_site['id']}").json()
            if p["slug"] == "px-43-rep"
        )
        by_addr = {a["address"]: a for a in linked}
        assert by_addr["2001:db8:43:2::1"]["ipv6_prefix_id"] is None
        assert by_addr["2001:db8:43:2::2"]["ipv6_prefix_id"] == pfx_rep["id"]
        assert by_addr["2001:db8:43:2::2"]["is_primary"] is True
