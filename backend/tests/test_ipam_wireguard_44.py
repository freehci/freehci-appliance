"""Trinn 44: WireGuard-grensesnitt og peers uten nøkkelmateriale eller BGP-gjetning."""

from fastapi.testclient import TestClient

from app.main import create_app


def test_listen_port_and_address_are_not_inferred() -> None:
    app = create_app()
    with TestClient(app) as client:
        site = client.post("/api/v1/dcim/sites", json={"name": "WG 44", "slug": "site-44-wg"}).json()
        other = client.post("/api/v1/dcim/sites", json={"name": "WG 44 B", "slug": "site-44-wg-b"}).json()
        sw = client.post("/api/v1/dcim/devices", json={"name": "rtr-44-a", "site_id": site["id"]}).json()
        other_sw = client.post("/api/v1/dcim/devices", json={"name": "rtr-44-b", "site_id": other["id"]}).json()
        iface = client.post(f"/api/v1/dcim/devices/{sw['id']}/interfaces", json={"name": "wg0"}).json()
        foreign = client.post(f"/api/v1/dcim/devices/{other_sw['id']}/interfaces", json={"name": "wg0"}).json()
        created = client.post(
            "/api/v1/ipam/wireguard-interfaces",
            json={
                "device_id": sw["id"],
                "name": "wg0",
                "slug": "wg-44-a",
                "auto_link": True,
                "match_name": True,
                "infer_port": True,
                "infer_address": True,
                "listen_port": None,
                "address": None,
            },
        )
        assert created.status_code == 200, created.text
        body = created.json()
        assert body["slug"] == "wg-44-a"
        assert body["interface_id"] is None
        assert body["listen_port"] is None
        assert body["address"] is None
        assert body["private_key_ref"] is None
        assert body["tunnel_id"] is None
        assert body["peers"] == []
        raw_key = client.post(
            "/api/v1/ipam/wireguard-interfaces",
            json={
                "device_id": sw["id"],
                "name": "wg1",
                "private_key_ref": "cN8k1Y0examplePrivateKeyMaterialXXXXXXX=",
            },
        )
        assert raw_key.status_code == 422
        bad_device = client.post(
            "/api/v1/ipam/wireguard-interfaces",
            json={"device_id": sw["id"], "name": "wg-foreign", "interface_id": foreign["id"]},
        )
        assert bad_device.status_code == 400
        assert bad_device.json()["detail"]["code"] == "wg_iface_device"
        linked = client.post(
            "/api/v1/ipam/wireguard-interfaces",
            json={
                "device_id": sw["id"],
                "name": "wg-linked",
                "slug": "wg-44-linked",
                "interface_id": iface["id"],
                "listen_port": 51820,
                "address": "10.44.0.1/32",
                "private_key_ref": "secret:wg/rtr-44-a/private",
            },
        )
        assert linked.status_code == 200, linked.text
        assert linked.json()["interface_id"] == iface["id"]
        assert linked.json()["listen_port"] == 51820
        assert linked.json()["address"] == "10.44.0.1/32"
        assert linked.json()["private_key_ref"] == "secret:wg/rtr-44-a/private"
        peer = client.post(
            f"/api/v1/ipam/wireguard-interfaces/{created.json()['id']}/peers",
            json={
                "name": "site-b",
                "slug": "peer-44-b",
                "endpoint_port": 51820,
                "allowed_ips": ["10.44.0.0/24"],
                "announce": True,
                "bgp": True,
                "import_routes": True,
                "infer_port": True,
                "public_key": "not-a-ref",
                "psk": "raw-psk",
            },
        )
        assert peer.status_code == 200, peer.text
        pbody = peer.json()
        assert pbody["endpoint_port"] == 51820
        assert pbody["allowed_ips"] == ["10.44.0.0/24"]
        assert pbody["public_key_ref"] is None
        assert pbody["psk_ref"] is None
        still = client.get(f"/api/v1/ipam/wireguard-interfaces/{created.json()['id']}").json()
        assert still["listen_port"] is None
        assert still["address"] is None
        raw_peer = client.post(
            f"/api/v1/ipam/wireguard-interfaces/{created.json()['id']}/peers",
            json={"name": "raw", "public_key_ref": "AbCdEfGhIjKlMnOpQrStUvWxYz0123456789+/="},
        )
        assert raw_peer.status_code == 422
        ok_peer = client.post(
            f"/api/v1/ipam/wireguard-interfaces/{created.json()['id']}/peers",
            json={
                "name": "ok",
                "slug": "peer-44-ok",
                "public_key_ref": "secret:wg/peer-ok/pub",
                "psk_ref": "secret:wg/peer-ok/psk",
            },
        )
        assert ok_peer.status_code == 200, ok_peer.text
        assert ok_peer.json()["public_key_ref"] == "secret:wg/peer-ok/pub"
        assert ok_peer.json()["psk_ref"] == "secret:wg/peer-ok/psk"
        dup = client.post(
            "/api/v1/ipam/wireguard-interfaces",
            json={"device_id": sw["id"], "name": "other", "slug": "wg-44-a"},
        )
        assert dup.status_code == 409
        assert dup.json()["detail"]["code"] == "wg_slug"
        listed = client.get(f"/api/v1/ipam/wireguard-interfaces?device_id={sw['id']}").json()
        assert {r["slug"] for r in listed} >= {"wg-44-a", "wg-44-linked"}
        assert client.delete(f"/api/v1/ipam/wireguard-peers/{ok_peer.json()['id']}").status_code == 204
        assert client.delete(f"/api/v1/ipam/wireguard-interfaces/{created.json()['id']}").status_code == 204
        after = client.get(f"/api/v1/ipam/wireguard-interfaces?device_id={sw['id']}").json()
        assert all(r["slug"] != "wg-44-a" for r in after)


def test_tunnel_is_not_inferred_from_vpn_type() -> None:
    app = create_app()
    with TestClient(app) as client:
        site = client.post("/api/v1/dcim/sites", json={"name": "WG 44 tun", "slug": "site-44-wgtun"}).json()
        sw = client.post("/api/v1/dcim/devices", json={"name": "rtr-44-tun", "site_id": site["id"]}).json()
        vpn = client.post(
            "/api/v1/ipam/vpn-services",
            json={"name": "wg-svc", "slug": "vpn-44-wg", "vpn_type": "wireguard"},
        ).json()
        tun = client.post(f"/api/v1/ipam/vpn-services/{vpn['id']}/tunnels", json={"name": "site-a", "slug": "tun-44-a"}).json()
        created = client.post(
            "/api/v1/ipam/wireguard-interfaces",
            json={"device_id": sw["id"], "name": "wg0", "slug": "wg-44-tun", "vpn_type": "wireguard"},
        )
        assert created.status_code == 200, created.text
        assert created.json()["tunnel_id"] is None
        linked = client.patch(
            f"/api/v1/ipam/wireguard-interfaces/{created.json()['id']}",
            json={"tunnel_id": tun["id"]},
        )
        assert linked.status_code == 200, linked.text
        assert linked.json()["tunnel_id"] == tun["id"]
        assert linked.json()["tunnel_slug"] == "tun-44-a"
        assert linked.json()["vpn_slug"] == "vpn-44-wg"


def test_federation_exports_wireguard_without_inventing_links() -> None:
    from app.core.db import SessionLocal
    from app.services import federation as fed_svc

    app = create_app()
    with TestClient(app) as client:
        tenant = client.post("/api/v1/tenants", json={"name": "WG Fed 44", "slug": "wg-44-fed"}).json()
        site = client.post(
            "/api/v1/dcim/sites",
            json={"name": "wg-44-fed-oslo", "slug": "wg-44-fed-oslo", "tenant_id": tenant["id"]},
        ).json()
        sw = client.post("/api/v1/dcim/devices", json={"name": "rtr-44-fed", "site_id": site["id"]}).json()
        iface = client.post(f"/api/v1/dcim/devices/{sw['id']}/interfaces", json={"name": "wg0"}).json()
        vpn = client.post(
            "/api/v1/ipam/vpn-services",
            json={"name": "fed-wg", "slug": "vpn-44-fed", "vpn_type": "wireguard"},
        ).json()
        tun = client.post(
            f"/api/v1/ipam/vpn-services/{vpn['id']}/tunnels",
            json={"name": "oslo", "slug": "tun-44-fed"},
        ).json()
        wg = client.post(
            "/api/v1/ipam/wireguard-interfaces",
            json={
                "device_id": sw["id"],
                "name": "wg0",
                "slug": "wg-44-fed",
                "interface_id": iface["id"],
                "listen_port": 51820,
                "address": "10.44.8.1/32",
                "private_key_ref": "secret:wg/fed/private",
                "tunnel_id": tun["id"],
            },
        )
        assert wg.status_code == 200, wg.text
        peer = client.post(
            f"/api/v1/ipam/wireguard-interfaces/{wg.json()['id']}/peers",
            json={
                "name": "remote",
                "slug": "peer-44-fed",
                "public_key_ref": "secret:wg/fed/peer-pub",
                "allowed_ips": ["10.44.8.0/24"],
                "endpoint_host": "203.0.113.44",
                "endpoint_port": 51820,
            },
        )
        assert peer.status_code == 200, peer.text
        snap = client.get("/api/v1/federation/tenants/wg-44-fed/snapshot")
        assert snap.status_code == 200, snap.text
        doc = snap.json()["document"]
        assert isinstance(doc["wireguard_interfaces"], list)
        assert isinstance(doc["wireguard_peers"], list)
        match = next(r for r in doc["wireguard_interfaces"] if r["slug"] == "wg-44-fed")
        assert match["device_name"] == "rtr-44-fed"
        assert match["site_slug"] == "wg-44-fed-oslo"
        assert match["interface_name"] == "wg0"
        assert match["listen_port"] == 51820
        assert match["address"] == "10.44.8.1/32"
        assert match["private_key_ref"] == "secret:wg/fed/private"
        assert match["vpn_slug"] == "vpn-44-fed"
        assert match["tunnel_slug"] == "tun-44-fed"
        pmatch = next(r for r in doc["wireguard_peers"] if r["slug"] == "peer-44-fed")
        assert pmatch["wg_slug"] == "wg-44-fed"
        assert pmatch["public_key_ref"] == "secret:wg/fed/peer-pub"
        assert pmatch["allowed_ips"] == ["10.44.8.0/24"]
        db = SessionLocal()
        try:
            checksum = fed_svc.apply_document_locally(db, doc)
            assert checksum == snap.json()["checksum"]
        finally:
            db.close()
        client.post("/api/v1/tenants", json={"name": "Rep 44", "slug": "rep-44-wg"})
        replica = {
            "apiVersion": "freehci.inventory/v1",
            "kind": "TenantInventory",
            "tenant": {"slug": "rep-44-wg", "name": "Rep 44", "description": None},
            "sites": [{"slug": "site-44-rep", "name": "Rep site", "description": None}],
            "rooms": [],
            "racks": [],
            "manufacturers": [],
            "device_types": [],
            "device_models": [],
            "device_roles": [],
            "devices": [{"name": "rtr-44-rep", "site_slug": "site-44-rep"}],
            "device_artifacts": [],
            "device_artifact_records": [],
            "device_interfaces": [{"device_name": "rtr-44-rep", "site_slug": "site-44-rep", "name": "wg0"}],
            "device_interface_lags": [],
            "device_interface_vlans": [],
            "device_interface_vlan_members": [],
            "device_interface_vrfs": [],
            "device_interface_ips": [],
            "device_ips": [],
            "device_port_interfaces": [],
            "wireguard_interfaces": [],
            "wireguard_peers": [],
            "placements": [],
            "ipam": [
                {
                    "site": {"slug": "site-44-rep", "name": "Rep site"},
                    "vrfs": [],
                    "vlans": [],
                    "prefixes": [],
                    "vpn_services": [{"name": "rep-wg", "slug": "vpn-44-rep", "vpn_type": "wireguard"}],
                    "tunnels": [{"vpn_slug": "vpn-44-rep", "name": "oslo", "slug": "tun-44-rep", "status": "planned"}],
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
        replica["wireguard_interfaces"] = [
            {
                "device_name": "rtr-44-rep",
                "site_slug": "site-44-rep",
                "slug": "wg-44-rep",
                "name": "wg0",
                "auto_link": True,
                "match_name": True,
                "infer_port": True,
                "infer_address": True,
                "endpoint_port": 51820,
                "allowed_ips": ["10.44.9.0/24"],
                "tunnel_slug": "tun-44-rep",
            }
        ]
        db = SessionLocal()
        try:
            fed_svc.apply_document_locally(db, replica)
        finally:
            db.close()
        replica_site = next(s for s in client.get("/api/v1/dcim/sites").json() if s["slug"] == "site-44-rep")
        replica_sw = next(
            d
            for d in client.get("/api/v1/dcim/devices").json()
            if d["name"] == "rtr-44-rep" and d["site_id"] == replica_site["id"]
        )
        after = client.get(f"/api/v1/ipam/wireguard-interfaces?device_id={replica_sw['id']}").json()
        row = next(r for r in after if r["slug"] == "wg-44-rep")
        assert row["interface_id"] is None
        assert row["listen_port"] is None
        assert row["address"] is None
        assert row["tunnel_id"] is None
        replica["wireguard_interfaces"] = [
            {
                "device_name": "rtr-44-rep",
                "site_slug": "site-44-rep",
                "slug": "wg-44-rep-linked",
                "name": "wg-linked",
                "interface_name": "wg0",
                "listen_port": 51821,
                "address": "10.44.9.1/32",
                "private_key_ref": "secret:wg/rep/private",
                "vpn_slug": "vpn-44-rep",
                "tunnel_slug": "tun-44-rep",
            }
        ]
        replica["wireguard_peers"] = [
            {
                "device_name": "rtr-44-rep",
                "site_slug": "site-44-rep",
                "wg_slug": "wg-44-rep-linked",
                "slug": "peer-44-rep",
                "name": "remote",
                "public_key_ref": "secret:wg/rep/peer-pub",
                "psk_ref": "secret:wg/rep/psk",
                "allowed_ips": ["10.44.9.0/24"],
                "announce": True,
                "import_routes": True,
            }
        ]
        db = SessionLocal()
        try:
            fed_svc.apply_document_locally(db, replica)
        finally:
            db.close()
        linked = client.get(f"/api/v1/ipam/wireguard-interfaces?device_id={replica_sw['id']}").json()
        row2 = next(r for r in linked if r["slug"] == "wg-44-rep-linked")
        dcim_ifaces = client.get(f"/api/v1/dcim/devices/{replica_sw['id']}/interfaces").json()
        assert row2["interface_id"] == dcim_ifaces[0]["id"]
        assert row2["listen_port"] == 51821
        assert row2["address"] == "10.44.9.1/32"
        assert row2["private_key_ref"] == "secret:wg/rep/private"
        assert row2["tunnel_slug"] == "tun-44-rep"
        assert row2["vpn_slug"] == "vpn-44-rep"
        peers = row2["peers"]
        assert len(peers) == 1
        assert peers[0]["slug"] == "peer-44-rep"
        assert peers[0]["public_key_ref"] == "secret:wg/rep/peer-pub"
        assert peers[0]["psk_ref"] == "secret:wg/rep/psk"
        assert peers[0]["allowed_ips"] == ["10.44.9.0/24"]
        prefixes = client.get(f"/api/v1/ipam/ipv4-prefixes?site_id={replica_site['id']}").json()
        assert prefixes == []
