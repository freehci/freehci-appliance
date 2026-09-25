"""Trinn 46: GRE-profil uten gjettet kryptering, endepunkt, nøkkel eller IPsec-innpakning."""

from fastapi.testclient import TestClient

from app.main import create_app


def test_gre_fields_are_not_inferred() -> None:
    app = create_app()
    with TestClient(app) as client:
        site = client.post("/api/v1/dcim/sites", json={"name": "GRE 46", "slug": "site-46-gre"}).json()
        client.post(
            "/api/v1/ipam/ipv4-prefixes",
            json={
                "site_id": site["id"],
                "name": "lan-46",
                "cidr": "10.46.0.0/24",
                "slug": "px-46-gre",
                "role": "access",
                "status": "active",
            },
        )
        vpn = client.post(
            "/api/v1/ipam/vpn-services",
            json={"name": "gre-svc", "slug": "vpn-46-gre", "vpn_type": "gre"},
        ).json()
        tun = client.post(
            f"/api/v1/ipam/vpn-services/{vpn['id']}/tunnels",
            json={"name": "site-a", "slug": "tun-46-a"},
        ).json()
        created = client.post(
            "/api/v1/ipam/gre-profiles",
            json={
                "name": "gre-46",
                "slug": "gre-46-a",
                "vpn_type": "gre",
                "encrypt": True,
                "ipsec": True,
                "infer_endpoints": True,
                "match_prefix": True,
                "prefix_cidr": "10.46.0.0/24",
                "psk_ref": "supersecret",
            },
        )
        assert created.status_code == 200, created.text
        body = created.json()
        assert body["slug"] == "gre-46-a"
        assert body["local_address"] is None
        assert body["remote_address"] is None
        assert body["key_id"] is None
        assert body["ttl"] is None
        assert body["checksum"] is None
        assert body["sequence"] is None
        assert body["tunnels"] == []
        assert "psk_ref" not in body
        bad_ip = client.post(
            "/api/v1/ipam/gre-profiles",
            json={"name": "bad-ip", "local_address": "10.46.0.0/24"},
        )
        assert bad_ip.status_code == 400
        assert bad_ip.json()["detail"]["code"] == "gre_address"
        bad_key = client.post(
            "/api/v1/ipam/gre-profiles",
            json={"name": "bad-key", "key_id": -1},
        )
        assert bad_key.status_code == 400
        assert bad_key.json()["detail"]["code"] == "gre_key"
        recorded = client.post(
            "/api/v1/ipam/gre-profiles",
            json={
                "name": "gre-46-rec",
                "slug": "gre-46-rec",
                "local_address": "203.0.113.10",
                "remote_address": "198.51.100.20",
                "key_id": 42,
                "ttl": 255,
                "checksum": False,
                "sequence": True,
            },
        )
        assert recorded.status_code == 200, recorded.text
        rec = recorded.json()
        assert rec["local_address"] == "203.0.113.10"
        assert rec["remote_address"] == "198.51.100.20"
        assert rec["key_id"] == 42
        assert rec["ttl"] == 255
        assert rec["checksum"] is False
        assert rec["sequence"] is True
        no_bind = client.get(f"/api/v1/ipam/gre-profiles/{created.json()['id']}").json()
        assert no_bind["tunnels"] == []
        bind = client.post(
            "/api/v1/ipam/gre-tunnels",
            json={"tunnel_id": tun["id"], "profile_id": recorded.json()["id"]},
        )
        assert bind.status_code == 200, bind.text
        assert bind.json()["tunnel_id"] == tun["id"]
        dup = client.post(
            "/api/v1/ipam/gre-tunnels",
            json={"tunnel_id": tun["id"], "profile_id": created.json()["id"]},
        )
        assert dup.status_code == 409
        assert dup.json()["detail"]["code"] == "gre_tunnel_taken"
        assert client.delete(f"/api/v1/ipam/gre-tunnels/{bind.json()['id']}").status_code == 204
        assert client.delete(f"/api/v1/ipam/gre-profiles/{created.json()['id']}").status_code == 204


def test_federation_exports_gre_without_inventing_links() -> None:
    from app.core.db import SessionLocal
    from app.services import federation as fed_svc

    app = create_app()
    with TestClient(app) as client:
        tenant = client.post("/api/v1/tenants", json={"name": "GRE Fed 46", "slug": "gre-46-fed"}).json()
        site = client.post(
            "/api/v1/dcim/sites",
            json={"name": "gre-46-fed-oslo", "slug": "gre-46-fed-oslo", "tenant_id": tenant["id"]},
        ).json()
        vpn = client.post(
            "/api/v1/ipam/vpn-services",
            json={"name": "fed-gre", "slug": "vpn-46-fed", "vpn_type": "gre"},
        ).json()
        tun = client.post(
            f"/api/v1/ipam/vpn-services/{vpn['id']}/tunnels",
            json={"name": "oslo", "slug": "tun-46-fed"},
        ).json()
        prof = client.post(
            "/api/v1/ipam/gre-profiles",
            json={
                "name": "fed-gre",
                "slug": "gre-46-fed",
                "local_address": "203.0.113.46",
                "remote_address": "198.51.100.46",
                "key_id": 46,
            },
        )
        assert prof.status_code == 200, prof.text
        bind = client.post(
            "/api/v1/ipam/gre-tunnels",
            json={"tunnel_id": tun["id"], "profile_id": prof.json()["id"]},
        )
        assert bind.status_code == 200, bind.text
        snap = client.get("/api/v1/federation/tenants/gre-46-fed/snapshot")
        assert snap.status_code == 200, snap.text
        doc = snap.json()["document"]
        assert isinstance(doc["gre_profiles"], list)
        assert isinstance(doc["gre_tunnels"], list)
        match = next(r for r in doc["gre_profiles"] if r["slug"] == "gre-46-fed")
        assert match["local_address"] == "203.0.113.46"
        assert match["remote_address"] == "198.51.100.46"
        assert match["key_id"] == 46
        assert match["checksum"] is None
        tmatch = next(r for r in doc["gre_tunnels"] if r["profile_slug"] == "gre-46-fed")
        assert tmatch["vpn_slug"] == "vpn-46-fed"
        assert tmatch["tunnel_slug"] == "tun-46-fed"
        db = SessionLocal()
        try:
            checksum = fed_svc.apply_document_locally(db, doc)
            assert checksum == snap.json()["checksum"]
        finally:
            db.close()
        client.post("/api/v1/tenants", json={"name": "Rep 46", "slug": "rep-46-gre"})
        replica = {
            "apiVersion": "freehci.inventory/v1",
            "kind": "TenantInventory",
            "tenant": {"slug": "rep-46-gre", "name": "Rep 46", "description": None},
            "sites": [{"slug": "site-46-rep", "name": "Rep site", "description": None}],
            "rooms": [],
            "racks": [],
            "manufacturers": [],
            "device_types": [],
            "device_models": [],
            "device_roles": [],
            "devices": [],
            "device_artifacts": [],
            "device_artifact_records": [],
            "device_interfaces": [],
            "device_interface_lags": [],
            "device_interface_vlans": [],
            "device_interface_vlan_members": [],
            "device_interface_vrfs": [],
            "device_interface_ips": [],
            "device_ips": [],
            "device_port_interfaces": [],
            "wireguard_interfaces": [],
            "wireguard_peers": [],
            "ipsec_profiles": [],
            "ipsec_selectors": [],
            "ipsec_tunnels": [],
            "gre_profiles": [],
            "gre_tunnels": [],
            "placements": [],
            "ipam": [
                {
                    "site": {"slug": "site-46-rep", "name": "Rep site"},
                    "vrfs": [],
                    "vlans": [],
                    "prefixes": [{"cidr": "10.46.9.0/24", "slug": "px-46-rep", "role": "access", "status": "active"}],
                    "vpn_services": [{"name": "rep-gre", "slug": "vpn-46-rep", "vpn_type": "gre"}],
                    "tunnels": [{"vpn_slug": "vpn-46-rep", "name": "oslo", "slug": "tun-46-rep", "status": "planned"}],
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
        replica["gre_profiles"] = [
            {
                "slug": "gre-46-rep",
                "name": "rep-gre",
                "vpn_type": "gre",
                "encrypt": True,
                "infer_endpoints": True,
                "match_prefix": True,
                "prefix_cidr": "10.46.9.0/24",
            }
        ]
        db = SessionLocal()
        try:
            fed_svc.apply_document_locally(db, replica)
        finally:
            db.close()
        after = client.get("/api/v1/ipam/gre-profiles").json()
        row = next(r for r in after if r["slug"] == "gre-46-rep")
        assert row["local_address"] is None
        assert row["remote_address"] is None
        assert row["key_id"] is None
        assert row["checksum"] is None
        assert row["tunnels"] == []
        replica["gre_profiles"] = [
            {
                "slug": "gre-46-rep-linked",
                "name": "rep-gre-linked",
                "local_address": "192.0.2.46",
                "remote_address": "198.51.100.10",
                "key_id": 100,
                "checksum": True,
            }
        ]
        replica["gre_tunnels"] = [
            {
                "vpn_slug": "vpn-46-rep",
                "tunnel_slug": "tun-46-rep",
                "profile_slug": "gre-46-rep-linked",
            }
        ]
        db = SessionLocal()
        try:
            fed_svc.apply_document_locally(db, replica)
        finally:
            db.close()
        linked = client.get("/api/v1/ipam/gre-profiles").json()
        row2 = next(r for r in linked if r["slug"] == "gre-46-rep-linked")
        assert row2["local_address"] == "192.0.2.46"
        assert row2["remote_address"] == "198.51.100.10"
        assert row2["key_id"] == 100
        assert row2["checksum"] is True
        assert len(row2["tunnels"]) == 1
        assert row2["tunnels"][0]["tunnel_slug"] == "tun-46-rep"
        _ = site
