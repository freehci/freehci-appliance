"""Trinn 36: eksplisitt LAG uten gjettet medlemskap, LACP eller hastighet."""

from fastapi.testclient import TestClient

from app.main import create_app


def _device_with_ifaces(client: TestClient, site_slug: str, name: str) -> tuple[int, int, int, int]:
    site = client.post("/api/v1/dcim/sites", json={"name": site_slug, "slug": site_slug}).json()
    sw = client.post("/api/v1/dcim/devices", json={"name": name, "site_id": site["id"]}).json()
    eth0 = client.post(
        f"/api/v1/dcim/devices/{sw['id']}/interfaces",
        json={"name": "eth0", "speed_mbps": 10000},
    ).json()
    eth1 = client.post(
        f"/api/v1/dcim/devices/{sw['id']}/interfaces",
        json={"name": "eth1", "speed_mbps": 10000},
    ).json()
    return site["id"], sw["id"], eth0["id"], eth1["id"]


def test_same_speed_is_not_a_lag_until_posted() -> None:
    app = create_app()
    with TestClient(app) as client:
        _site_id, did, eth0, eth1 = _device_with_ifaces(client, "site-36-lag", "sw-36-a")
        listed = client.get(f"/api/v1/dcim/devices/{did}/interface-lags")
        assert listed.status_code == 200, listed.text
        assert listed.json() == []
        created = client.post(
            f"/api/v1/dcim/devices/{did}/interface-lags",
            json={
                "name": "ae0",
                "protocol": "lacp",
                "min_links": 2,
                "lacp": {"mode": "active"},
                "speed": 20000,
            },
        )
        assert created.status_code == 200, created.text
        body = created.json()
        assert body["name"] == "ae0"
        assert body["slug"] == "ae0"
        assert body["members"] == []
        assert "protocol" not in body
        assert "min_links" not in body
        assert "lacp" not in body
        assert "speed" not in body
        listed = client.get(f"/api/v1/dcim/devices/{did}/interface-lags").json()
        assert [r["slug"] for r in listed] == ["ae0"]
        bound = client.post(
            f"/api/v1/dcim/interface-lags/{body['id']}/members",
            json={"interface_id": eth0, "protocol": "lacp", "role": "active"},
        )
        assert bound.status_code == 200, bound.text
        assert [m["interface_name"] for m in bound.json()["members"]] == ["eth0"]
        assert bound.json()["members"][0]["speed_mbps"] == 10000
        again = client.post(
            f"/api/v1/dcim/interface-lags/{body['id']}/members",
            json={"interface_id": eth0},
        )
        assert again.status_code == 409
        assert again.json()["detail"]["code"] == "lag_member_taken"
        other = client.post(f"/api/v1/dcim/devices/{did}/interface-lags", json={"name": "ae1"})
        assert other.status_code == 200, other.text
        stolen = client.post(
            f"/api/v1/dcim/interface-lags/{other.json()['id']}/members",
            json={"interface_id": eth0},
        )
        assert stolen.status_code == 409
        assert stolen.json()["detail"]["code"] == "lag_member_taken"
        second = client.post(
            f"/api/v1/dcim/interface-lags/{body['id']}/members",
            json={"interface_id": eth1},
        )
        assert second.status_code == 200, second.text
        assert [m["interface_name"] for m in second.json()["members"]] == ["eth0", "eth1"]
        member_id = next(m["id"] for m in second.json()["members"] if m["interface_name"] == "eth1")
        assert client.delete(f"/api/v1/dcim/interface-lag-members/{member_id}").status_code == 204
        after = client.get(f"/api/v1/dcim/interface-lags/{body['id']}").json()
        assert [m["interface_name"] for m in after["members"]] == ["eth0"]
        assert client.delete(f"/api/v1/dcim/interface-lags/{body['id']}").status_code == 204
        remaining = client.get(f"/api/v1/dcim/devices/{did}/interface-lags").json()
        assert [r["slug"] for r in remaining] == ["ae1"]
        assert remaining[0]["members"] == []
        parent = client.post(
            f"/api/v1/dcim/devices/{did}/interfaces",
            json={"name": "eth0.100", "parent_interface_id": eth0, "vlan_id": 100},
        )
        assert parent.status_code == 200, parent.text
        assert parent.json()["parent_interface_id"] == eth0
        assert parent.json()["name"] == "eth0.100"


def test_lag_rejects_foreign_interface_and_duplicate_slug() -> None:
    app = create_app()
    with TestClient(app) as client:
        _site_a, did_a, eth0_a, _eth1_a = _device_with_ifaces(client, "site-36-a", "sw-36-local")
        _site_b, _did_b, eth0_b, _eth1_b = _device_with_ifaces(client, "site-36-b", "sw-36-other")
        lag = client.post(f"/api/v1/dcim/devices/{did_a}/interface-lags", json={"name": "ae0", "slug": "ae0"})
        assert lag.status_code == 200, lag.text
        cross = client.post(
            f"/api/v1/dcim/interface-lags/{lag.json()['id']}/members",
            json={"interface_id": eth0_b},
        )
        assert cross.status_code == 400
        assert cross.json()["detail"]["code"] == "lag_member_device"
        missing = client.post(
            f"/api/v1/dcim/interface-lags/{lag.json()['id']}/members",
            json={"interface_id": 999999},
        )
        assert missing.status_code == 404
        dup = client.post(f"/api/v1/dcim/devices/{did_a}/interface-lags", json={"name": "Other", "slug": "ae0"})
        assert dup.status_code == 409
        assert dup.json()["detail"]["code"] == "lag_slug"
        unused = eth0_a
        bound = client.post(
            f"/api/v1/dcim/interface-lags/{lag.json()['id']}/members",
            json={"interface_id": unused},
        )
        assert bound.status_code == 200, bound.text


def test_federation_exports_interface_lag_by_device_and_iface_name() -> None:
    from app.core.db import SessionLocal
    from app.services import federation as fed_svc

    app = create_app()
    with TestClient(app) as client:
        tenant = client.post("/api/v1/tenants", json={"name": "Lag Fed", "slug": "lag-36-fed"}).json()
        site = client.post(
            "/api/v1/dcim/sites",
            json={"name": "lag-36-fed-oslo", "slug": "lag-36-fed-oslo", "tenant_id": tenant["id"]},
        ).json()
        sw = client.post("/api/v1/dcim/devices", json={"name": "sw-36-fed", "site_id": site["id"]}).json()
        eth0 = client.post(
            f"/api/v1/dcim/devices/{sw['id']}/interfaces",
            json={"name": "eth0", "speed_mbps": 10000},
        )
        assert eth0.status_code == 200, eth0.text
        eth1 = client.post(
            f"/api/v1/dcim/devices/{sw['id']}/interfaces",
            json={"name": "eth1", "speed_mbps": 10000},
        )
        assert eth1.status_code == 200, eth1.text
        lag = client.post(
            f"/api/v1/dcim/devices/{sw['id']}/interface-lags",
            json={"name": "ae0", "slug": "ae0"},
        )
        assert lag.status_code == 200, lag.text
        bound = client.post(
            f"/api/v1/dcim/interface-lags/{lag.json()['id']}/members",
            json={"interface_id": eth0.json()["id"]},
        )
        assert bound.status_code == 200, bound.text
        snap = client.get("/api/v1/federation/tenants/lag-36-fed/snapshot")
        assert snap.status_code == 200, snap.text
        doc = snap.json()["document"]
        assert isinstance(doc["device_interface_lags"], list)
        match = next(r for r in doc["device_interface_lags"] if r["slug"] == "ae0")
        assert match["device_name"] == "sw-36-fed"
        assert match["site_slug"] == "lag-36-fed-oslo"
        assert match["interface_names"] == ["eth0"]
        assert "protocol" not in match
        assert "min_links" not in match
        db = SessionLocal()
        try:
            checksum = fed_svc.apply_document_locally(db, doc)
            assert checksum == snap.json()["checksum"]
        finally:
            db.close()
        client.post("/api/v1/tenants", json={"name": "Rep 36", "slug": "rep-36-lag"})
        replica = {
            "apiVersion": "freehci.inventory/v1",
            "kind": "TenantInventory",
            "tenant": {"slug": "rep-36-lag", "name": "Rep 36", "description": None},
            "sites": [{"slug": "site-36-rep", "name": "Rep site", "description": None}],
            "rooms": [],
            "racks": [],
            "manufacturers": [],
            "device_types": [],
            "device_models": [],
            "device_roles": [],
            "devices": [{"name": "sw-36-rep", "site_slug": "site-36-rep"}],
            "device_artifacts": [],
            "device_artifact_records": [],
            "device_interface_lags": [],
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
        replica_site = next(s for s in client.get("/api/v1/dcim/sites").json() if s["slug"] == "site-36-rep")
        replica_sw = next(
            d for d in client.get("/api/v1/dcim/devices").json() if d["name"] == "sw-36-rep" and d["site_id"] == replica_site["id"]
        )
        i0 = client.post(
            f"/api/v1/dcim/devices/{replica_sw['id']}/interfaces",
            json={"name": "eth0", "speed_mbps": 10000},
        )
        assert i0.status_code == 200, i0.text
        i1 = client.post(
            f"/api/v1/dcim/devices/{replica_sw['id']}/interfaces",
            json={"name": "eth1", "speed_mbps": 10000},
        )
        assert i1.status_code == 200, i1.text
        assert client.get(f"/api/v1/dcim/devices/{replica_sw['id']}/interface-lags").json() == []
        replica["device_interface_lags"] = [
            {
                "device_name": "sw-36-rep",
                "site_slug": "site-36-rep",
                "slug": "ae0",
                "name": "ae0",
                "description": None,
                "interface_names": ["eth0", "eth1"],
                "protocol": "lacp",
                "min_links": 2,
            }
        ]
        db = SessionLocal()
        try:
            fed_svc.apply_document_locally(db, replica)
        finally:
            db.close()
        lags = client.get(f"/api/v1/dcim/devices/{replica_sw['id']}/interface-lags").json()
        assert [r["slug"] for r in lags] == ["ae0"]
        assert [m["interface_name"] for m in lags[0]["members"]] == ["eth0", "eth1"]
        assert "protocol" not in lags[0]
        assert "min_links" not in lags[0]
