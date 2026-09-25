"""Trinn 45: IPsec-profil uten gjettet IKE, modus, nøkkel eller selektor fra prefiks."""

from fastapi.testclient import TestClient

from app.main import create_app


def test_ike_mode_and_selectors_are_not_inferred() -> None:
    app = create_app()
    with TestClient(app) as client:
        site = client.post("/api/v1/dcim/sites", json={"name": "IPSec 45", "slug": "site-45-ipsec"}).json()
        client.post(
            "/api/v1/ipam/ipv4-prefixes",
            json={
                "site_id": site["id"],
                "name": "lan-45",
                "cidr": "10.45.0.0/24",
                "slug": "px-45-ipsec",
                "role": "access",
                "status": "active",
            },
        )
        vpn = client.post(
            "/api/v1/ipam/vpn-services",
            json={"name": "ipsec-svc", "slug": "vpn-45-ipsec", "vpn_type": "ipsec"},
        ).json()
        tun = client.post(
            f"/api/v1/ipam/vpn-services/{vpn['id']}/tunnels",
            json={"name": "site-a", "slug": "tun-45-a"},
        ).json()
        created = client.post(
            "/api/v1/ipam/ipsec-profiles",
            json={
                "name": "ike-45",
                "slug": "ipsec-45-a",
                "vpn_type": "ipsec",
                "infer_ike": True,
                "ikev2": True,
                "lifetime": 86400,
                "dh_group": 14,
                "enc": "aes256",
                "apply": True,
            },
        )
        assert created.status_code == 200, created.text
        body = created.json()
        assert body["slug"] == "ipsec-45-a"
        assert body["ike_version"] is None
        assert body["mode"] is None
        assert body["psk_ref"] is None
        assert body["local_id"] is None
        assert body["remote_id"] is None
        assert body["selectors"] == []
        assert body["tunnels"] == []
        raw = client.post(
            "/api/v1/ipam/ipsec-profiles",
            json={"name": "raw", "psk_ref": "supersecretpsk"},
        )
        assert raw.status_code == 422
        bad_ike = client.post(
            "/api/v1/ipam/ipsec-profiles",
            json={"name": "bad-ike", "ike_version": "ikev3"},
        )
        assert bad_ike.status_code == 400
        assert bad_ike.json()["detail"]["code"] == "ipsec_ike"
        recorded = client.post(
            "/api/v1/ipam/ipsec-profiles",
            json={
                "name": "ike-45-rec",
                "slug": "ipsec-45-rec",
                "ike_version": "ikev2",
                "mode": "policy-based",
                "psk_ref": "secret:ipsec/45/psk",
                "local_id": "eggkleiva",
                "remote_id": "lade",
            },
        )
        assert recorded.status_code == 200, recorded.text
        assert recorded.json()["ike_version"] == "ikev2"
        assert recorded.json()["mode"] == "policy-based"
        assert recorded.json()["psk_ref"] == "secret:ipsec/45/psk"
        empty_sel = client.post(
            f"/api/v1/ipam/ipsec-profiles/{created.json()['id']}/selectors",
            json={
                "name": "auto",
                "slug": "sel-45-auto",
                "auto_link": True,
                "match_prefix": True,
                "prefix_cidr": "10.45.0.0/24",
                "allowed_ips": ["10.45.0.0/24"],
            },
        )
        assert empty_sel.status_code == 200, empty_sel.text
        assert empty_sel.json()["local_cidr"] is None
        assert empty_sel.json()["remote_cidr"] is None
        still = client.get(f"/api/v1/ipam/ipsec-profiles/{created.json()['id']}").json()
        assert still["mode"] is None
        assert still["ike_version"] is None
        linked = client.post(
            f"/api/v1/ipam/ipsec-profiles/{recorded.json()['id']}/selectors",
            json={"name": "lan", "slug": "sel-45-lan", "local_cidr": "10.45.0.0/24", "remote_cidr": "10.45.1.0/24"},
        )
        assert linked.status_code == 200, linked.text
        assert linked.json()["local_cidr"] == "10.45.0.0/24"
        assert linked.json()["remote_cidr"] == "10.45.1.0/24"
        bad_cidr = client.post(
            f"/api/v1/ipam/ipsec-profiles/{recorded.json()['id']}/selectors",
            json={"name": "bad", "local_cidr": "not-a-cidr"},
        )
        assert bad_cidr.status_code == 400
        assert bad_cidr.json()["detail"]["code"] == "ipsec_cidr"
        no_bind = client.get(f"/api/v1/ipam/ipsec-profiles/{created.json()['id']}").json()
        assert no_bind["tunnels"] == []
        bind = client.post(
            "/api/v1/ipam/ipsec-tunnels",
            json={"tunnel_id": tun["id"], "profile_id": recorded.json()["id"]},
        )
        assert bind.status_code == 200, bind.text
        assert bind.json()["tunnel_id"] == tun["id"]
        dup = client.post(
            "/api/v1/ipam/ipsec-tunnels",
            json={"tunnel_id": tun["id"], "profile_id": created.json()["id"]},
        )
        assert dup.status_code == 409
        assert dup.json()["detail"]["code"] == "ipsec_tunnel_taken"
        assert client.delete(f"/api/v1/ipam/ipsec-tunnels/{bind.json()['id']}").status_code == 204
        assert client.delete(f"/api/v1/ipam/ipsec-selectors/{empty_sel.json()['id']}").status_code == 204
        assert client.delete(f"/api/v1/ipam/ipsec-profiles/{created.json()['id']}").status_code == 204


def test_federation_exports_ipsec_without_inventing_links() -> None:
    from app.core.db import SessionLocal
    from app.services import federation as fed_svc

    app = create_app()
    with TestClient(app) as client:
        tenant = client.post("/api/v1/tenants", json={"name": "IPSec Fed 45", "slug": "ipsec-45-fed"}).json()
        site = client.post(
            "/api/v1/dcim/sites",
            json={"name": "ipsec-45-fed-oslo", "slug": "ipsec-45-fed-oslo", "tenant_id": tenant["id"]},
        ).json()
        vpn = client.post(
            "/api/v1/ipam/vpn-services",
            json={"name": "fed-ipsec", "slug": "vpn-45-fed", "vpn_type": "ipsec"},
        ).json()
        tun = client.post(
            f"/api/v1/ipam/vpn-services/{vpn['id']}/tunnels",
            json={"name": "oslo", "slug": "tun-45-fed"},
        ).json()
        prof = client.post(
            "/api/v1/ipam/ipsec-profiles",
            json={
                "name": "fed-ike",
                "slug": "ipsec-45-fed",
                "ike_version": "ikev2",
                "mode": "route-based",
                "psk_ref": "secret:ipsec/fed/psk",
            },
        )
        assert prof.status_code == 200, prof.text
        sel = client.post(
            f"/api/v1/ipam/ipsec-profiles/{prof.json()['id']}/selectors",
            json={"name": "lan", "slug": "sel-45-fed", "local_cidr": "10.45.8.0/24"},
        )
        assert sel.status_code == 200, sel.text
        bind = client.post(
            "/api/v1/ipam/ipsec-tunnels",
            json={"tunnel_id": tun["id"], "profile_id": prof.json()["id"]},
        )
        assert bind.status_code == 200, bind.text
        snap = client.get("/api/v1/federation/tenants/ipsec-45-fed/snapshot")
        assert snap.status_code == 200, snap.text
        doc = snap.json()["document"]
        assert isinstance(doc["ipsec_profiles"], list)
        assert isinstance(doc["ipsec_selectors"], list)
        assert isinstance(doc["ipsec_tunnels"], list)
        match = next(r for r in doc["ipsec_profiles"] if r["slug"] == "ipsec-45-fed")
        assert match["ike_version"] == "ikev2"
        assert match["mode"] == "route-based"
        assert match["psk_ref"] == "secret:ipsec/fed/psk"
        smatch = next(r for r in doc["ipsec_selectors"] if r["slug"] == "sel-45-fed")
        assert smatch["profile_slug"] == "ipsec-45-fed"
        assert smatch["local_cidr"] == "10.45.8.0/24"
        assert smatch["remote_cidr"] is None
        tmatch = next(r for r in doc["ipsec_tunnels"] if r["profile_slug"] == "ipsec-45-fed")
        assert tmatch["vpn_slug"] == "vpn-45-fed"
        assert tmatch["tunnel_slug"] == "tun-45-fed"
        db = SessionLocal()
        try:
            checksum = fed_svc.apply_document_locally(db, doc)
            assert checksum == snap.json()["checksum"]
        finally:
            db.close()
        client.post("/api/v1/tenants", json={"name": "Rep 45", "slug": "rep-45-ipsec"})
        replica = {
            "apiVersion": "freehci.inventory/v1",
            "kind": "TenantInventory",
            "tenant": {"slug": "rep-45-ipsec", "name": "Rep 45", "description": None},
            "sites": [{"slug": "site-45-rep", "name": "Rep site", "description": None}],
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
            "placements": [],
            "ipam": [
                {
                    "site": {"slug": "site-45-rep", "name": "Rep site"},
                    "vrfs": [],
                    "vlans": [],
                    "prefixes": [{"cidr": "10.45.9.0/24", "slug": "px-45-rep", "role": "access", "status": "active"}],
                    "vpn_services": [{"name": "rep-ipsec", "slug": "vpn-45-rep", "vpn_type": "ipsec"}],
                    "tunnels": [{"vpn_slug": "vpn-45-rep", "name": "oslo", "slug": "tun-45-rep", "status": "planned"}],
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
        replica["ipsec_profiles"] = [
            {
                "slug": "ipsec-45-rep",
                "name": "rep-ike",
                "vpn_type": "ipsec",
                "infer_ike": True,
                "match_prefix": True,
                "prefix_cidr": "10.45.9.0/24",
            }
        ]
        db = SessionLocal()
        try:
            fed_svc.apply_document_locally(db, replica)
        finally:
            db.close()
        after = client.get("/api/v1/ipam/ipsec-profiles").json()
        row = next(r for r in after if r["slug"] == "ipsec-45-rep")
        assert row["ike_version"] is None
        assert row["mode"] is None
        assert row["selectors"] == []
        assert row["tunnels"] == []
        replica["ipsec_profiles"] = [
            {
                "slug": "ipsec-45-rep-linked",
                "name": "rep-ike-linked",
                "ike_version": "ikev1",
                "mode": "policy-based",
                "psk_ref": "secret:ipsec/rep/psk",
            }
        ]
        replica["ipsec_selectors"] = [
            {
                "profile_slug": "ipsec-45-rep-linked",
                "slug": "sel-45-rep",
                "name": "lan",
                "local_cidr": "10.45.9.0/24",
                "auto_link": True,
                "match_prefix": True,
            }
        ]
        replica["ipsec_tunnels"] = [
            {
                "vpn_slug": "vpn-45-rep",
                "tunnel_slug": "tun-45-rep",
                "profile_slug": "ipsec-45-rep-linked",
            }
        ]
        db = SessionLocal()
        try:
            fed_svc.apply_document_locally(db, replica)
        finally:
            db.close()
        linked = client.get("/api/v1/ipam/ipsec-profiles").json()
        row2 = next(r for r in linked if r["slug"] == "ipsec-45-rep-linked")
        assert row2["ike_version"] == "ikev1"
        assert row2["mode"] == "policy-based"
        assert row2["psk_ref"] == "secret:ipsec/rep/psk"
        assert len(row2["selectors"]) == 1
        assert row2["selectors"][0]["local_cidr"] == "10.45.9.0/24"
        assert row2["selectors"][0]["remote_cidr"] is None
        assert len(row2["tunnels"]) == 1
        assert row2["tunnels"][0]["tunnel_slug"] == "tun-45-rep"
        _ = site
