"""Trinn 2a: VLAN-gruppe, RD-validering, status/role, IP uten rack."""

from fastapi.testclient import TestClient

from app.core.route_distinguisher import normalize_route_distinguisher
from app.main import create_app
from app.schemas.ipam import Ipv4PrefixCreate


def test_normalize_route_distinguisher() -> None:
    assert normalize_route_distinguisher(None) is None
    assert normalize_route_distinguisher("  ") is None
    assert normalize_route_distinguisher("65000:1") == "65000:1"
    assert normalize_route_distinguisher("192.0.2.1:100") == "192.0.2.1:100"
    assert normalize_route_distinguisher("4200000000:10") == "4200000000:10"
    try:
        normalize_route_distinguisher("not-an-rd")
        raise AssertionError("expected ValueError")
    except ValueError:
        pass
    try:
        normalize_route_distinguisher("4200000000:70000")
        raise AssertionError("expected ValueError")
    except ValueError:
        pass


def test_prefix_role_alias_active_becomes_access() -> None:
    row = Ipv4PrefixCreate(site_id=1, name="LAN", cidr="10.1.0.0/24", role="active")
    assert row.role == "access"
    reserved = Ipv4PrefixCreate(site_id=1, name="Hold", cidr="10.1.1.0/24", role="reserved")
    assert reserved.role == "container"


def test_vlan_vid_unique_per_group_not_site() -> None:
    app = create_app()
    with TestClient(app) as client:
        site = client.post("/api/v1/dcim/sites", json={"name": "Lab", "slug": "lab-vlan-grp"}).json()
        sid = site["id"]
        a = client.post("/api/v1/ipam/vlans", json={"site_id": sid, "vid": 100, "name": "Prod"})
        assert a.status_code == 200, a.text
        assert a.json()["vlan_group_id"] > 0
        dup = client.post("/api/v1/ipam/vlans", json={"site_id": sid, "vid": 100, "name": "Prod-dup"})
        assert dup.status_code == 409
        grp = client.post(
            "/api/v1/ipam/vlan-groups",
            json={"site_id": sid, "name": "Colo A", "slug": "colo-a"},
        )
        assert grp.status_code == 200, grp.text
        b = client.post(
            "/api/v1/ipam/vlans",
            json={"site_id": sid, "vid": 100, "name": "Colo servers", "vlan_group_id": grp.json()["id"]},
        )
        assert b.status_code == 200, b.text
        assert b.json()["vid"] == 100
        assert b.json()["vlan_group_id"] == grp.json()["id"]
        listed = client.get(f"/api/v1/ipam/vlans?site_id={sid}").json()
        assert len(listed) == 2


def test_vrf_rd_validation() -> None:
    app = create_app()
    with TestClient(app) as client:
        site = client.post("/api/v1/dcim/sites", json={"name": "Lab", "slug": "lab-rd"}).json()
        ok = client.post(
            "/api/v1/ipam/vrfs",
            json={"site_id": site["id"], "name": "evpn", "route_distinguisher": "65000:1"},
        )
        assert ok.status_code == 200, ok.text
        bad = client.post(
            "/api/v1/ipam/vrfs",
            json={"site_id": site["id"], "name": "bad", "route_distinguisher": "foo"},
        )
        assert bad.status_code == 422


def test_prefix_create_returns_access_role() -> None:
    app = create_app()
    with TestClient(app) as client:
        site = client.post("/api/v1/dcim/sites", json={"name": "Lab", "slug": "lab-role"}).json()
        pfx = client.post(
            "/api/v1/ipam/ipv4-prefixes",
            json={"site_id": site["id"], "name": "LAN", "cidr": "10.203.42.0/24", "role": "active"},
        )
        assert pfx.status_code == 200, pfx.text
        body = pfx.json()
        assert body["role"] == "access"
        assert body["status"] == "active"


def test_assign_ip_without_rack_placement() -> None:
    app = create_app()
    with TestClient(app) as client:
        sid = client.post("/api/v1/dcim/sites", json={"name": "S1", "slug": "s-norack"}).json()["id"]
        mid = client.post("/api/v1/dcim/manufacturers", json={"name": "M-NoRack"}).json()["id"]
        tid = client.post(
            "/api/v1/dcim/device-types",
            json={"name": "SrvNoRack", "slug": "srv-norack"},
        ).json()["id"]
        dmod = client.post(
            "/api/v1/dcim/device-models",
            json={"manufacturer_id": mid, "device_type_id": tid, "name": "X1", "u_height": 1},
        ).json()["id"]
        dev = client.post(
            "/api/v1/dcim/devices",
            json={"device_model_id": dmod, "name": "vip-host", "site_id": sid},
        )
        assert dev.status_code == 200, dev.text
        dev_id = dev.json()["id"]
        if_id = client.post(f"/api/v1/dcim/devices/{dev_id}/interfaces", json={"name": "lo"}).json()["id"]
        pfx = client.post(
            "/api/v1/ipam/ipv4-prefixes",
            json={"site_id": sid, "name": "LAN", "cidr": "10.204.77.0/30"},
        )
        assert pfx.status_code == 200, pfx.text
        pid = pfx.json()["id"]
        r = client.post(
            "/api/v1/ipam/ipv4-addresses/request",
            json={"ipv4_prefix_id": pid, "mode": "assign", "interface_id": if_id},
        )
        assert r.status_code == 200, r.text
        assert r.json()["status"] == "assigned"
        explore = client.get(f"/api/v1/ipam/ipv4-prefixes/{pid}/explore")
        assert explore.status_code == 200, explore.text
        addrs = [a["address"] for a in explore.json().get("assignments") or []]
        assert r.json()["address"] in addrs
