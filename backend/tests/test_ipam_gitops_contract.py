"""GitOps-kontrakt: rolle, VRF-scope, VLAN/VRF-ensure, gateway og feilkoder."""

from fastapi.testclient import TestClient

from app.main import create_app


def test_prefix_role_blocks_host_alloc() -> None:
    app = create_app()
    with TestClient(app) as client:
        site = client.post("/api/v1/dcim/sites", json={"name": "S-role", "slug": "s-role"}).json()
        pfx = client.post(
            "/api/v1/ipam/ipv4-prefixes",
            json={
                "site_id": site["id"],
                "name": "Pod",
                "slug": "site-a-pod",
                "cidr": "10.80.0.0/16",
                "role": "overlay-pod",
            },
        )
        assert pfx.status_code == 200, pfx.text
        assert pfx.json()["role"] == "overlay-pod"
        pid = pfx.json()["id"]

        req = client.post("/api/v1/ipam/ipv4-addresses/request", json={"ipv4_prefix_id": pid, "mode": "reserve"})
        assert req.status_code == 409
        assert req.json()["detail"]["code"] == "prefix_role_forbids_alloc"

        ens = client.post(
            "/api/v1/ipam/ipv4-addresses/ensure",
            json={"ipv4_prefix_id": pid, "address": "10.80.0.5", "mode": "reserve"},
        )
        assert ens.status_code == 409
        assert ens.json()["detail"]["code"] == "prefix_role_forbids_alloc"


def test_same_cidr_allowed_in_different_vrf() -> None:
    app = create_app()
    with TestClient(app) as client:
        site = client.post("/api/v1/dcim/sites", json={"name": "S-vrf", "slug": "s-vrf"}).json()
        under = client.post("/api/v1/ipam/vrfs", json={"site_id": site["id"], "name": "underlay", "slug": "underlay"})
        over = client.post("/api/v1/ipam/vrfs", json={"site_id": site["id"], "name": "overlay", "slug": "overlay"})
        assert under.status_code == 200 and over.status_code == 200
        a = client.post(
            "/api/v1/ipam/ipv4-prefixes",
            json={
                "site_id": site["id"],
                "name": "Under",
                "cidr": "10.80.0.0/16",
                "vrf_id": under.json()["id"],
                "role": "active",
            },
        )
        b = client.post(
            "/api/v1/ipam/ipv4-prefixes",
            json={
                "site_id": site["id"],
                "name": "Over",
                "cidr": "10.80.0.0/16",
                "vrf_id": over.json()["id"],
                "role": "overlay-pod",
            },
        )
        assert a.status_code == 200, a.text
        assert b.status_code == 200, b.text
        assert a.json()["id"] != b.json()["id"]


def test_vlan_vrf_get_patch_ensure() -> None:
    app = create_app()
    with TestClient(app) as client:
        site = client.post("/api/v1/dcim/sites", json={"name": "S-vle", "slug": "s-vle"}).json()
        vlan = client.post(
            "/api/v1/ipam/vlans/ensure",
            json={"site_id": site["id"], "vid": 50, "name": "k8s", "slug": "site-a-vlan-k8s"},
        )
        assert vlan.status_code == 200, vlan.text
        assert vlan.json()["created"] is True
        vid = vlan.json()["id"]

        again = client.post(
            "/api/v1/ipam/vlans/ensure",
            json={"site_id": site["id"], "vid": 50, "name": "other"},
        )
        assert again.json()["id"] == vid
        assert again.json()["created"] is False
        assert again.json()["name"] == "k8s"

        patched = client.patch(f"/api/v1/ipam/vlans/{vid}", json={"name": "k8s-core"})
        assert patched.status_code == 200
        assert patched.json()["name"] == "k8s-core"
        got = client.get(f"/api/v1/ipam/vlans/{vid}")
        assert got.json()["name"] == "k8s-core"
        assert got.json()["slug"] == "site-a-vlan-k8s"

        vrf = client.post(
            "/api/v1/ipam/vrfs/ensure",
            json={"site_id": site["id"], "name": "OOB", "slug": "oob"},
        )
        assert vrf.status_code == 200
        assert client.get(f"/api/v1/ipam/vrfs/{vrf.json()['id']}").status_code == 200


def test_gateway_protected_and_dhcp_range_skipped() -> None:
    app = create_app()
    with TestClient(app) as client:
        site = client.post("/api/v1/dcim/sites", json={"name": "S-gw", "slug": "s-gw2"}).json()
        pfx = client.post(
            "/api/v1/ipam/ipv4-prefixes",
            json={
                "site_id": site["id"],
                "name": "LAN",
                "cidr": "10.71.10.0/24",
                "role": "active",
                "subnet_services": {
                    "gateway": "10.71.10.1",
                    "dns": ["10.70.0.10"],
                    "dhcp_range": {"start": "10.71.10.100", "end": "10.71.10.200"},
                    "domain": "site-a.axionet.local",
                    "mtu": 1500,
                },
            },
        )
        assert pfx.status_code == 200, pfx.text
        pid = pfx.json()["id"]
        assert pfx.json()["subnet_services"]["dns"] == ["10.70.0.10"]
        assert pfx.json()["usable_hosts"] == 254

        bad = client.post(
            "/api/v1/ipam/ipv4-addresses/ensure",
            json={"ipv4_prefix_id": pid, "address": "10.71.10.1", "mode": "reserve"},
        )
        assert bad.status_code == 409
        assert bad.json()["detail"]["code"] == "gateway_protected"

        gw = client.post(
            "/api/v1/ipam/ipv4-addresses/ensure",
            json={"ipv4_prefix_id": pid, "address": "10.71.10.1", "mode": "reserve", "role": "gateway"},
        )
        assert gw.status_code == 200, gw.text
        assert gw.json()["role"] == "gateway"

        dhcp = client.post(
            "/api/v1/ipam/ipv4-addresses/ensure",
            json={"ipv4_prefix_id": pid, "address": "10.71.10.150", "mode": "reserve"},
        )
        assert dhcp.status_code == 409
        assert dhcp.json()["detail"]["code"] == "dhcp_range_protected"

        r = client.post("/api/v1/ipam/ipv4-addresses/request", json={"ipv4_prefix_id": pid, "mode": "reserve"})
        assert r.status_code == 200, r.text
        assert r.json()["address"] == "10.71.10.2"


def test_prefix_ensure_update_and_error_code_on_delete() -> None:
    app = create_app()
    with TestClient(app) as client:
        site = client.post("/api/v1/dcim/sites", json={"name": "S-ens", "slug": "s-ens2"}).json()
        first = client.post(
            "/api/v1/ipam/ipv4-prefixes/ensure",
            json={"site_id": site["id"], "cidr": "10.41.10.0/24", "name": "Pod", "slug": "site-a-lan"},
        )
        assert first.json()["created"] is True
        pid = first.json()["id"]

        silent = client.post(
            "/api/v1/ipam/ipv4-prefixes/ensure",
            json={"site_id": site["id"], "cidr": "10.41.10.0/24", "name": "Changed", "slug": "site-a-lan"},
        )
        assert silent.json()["created"] is False
        assert silent.json()["name"] == "Pod"

        upd = client.post(
            "/api/v1/ipam/ipv4-prefixes/ensure?update=true",
            json={"site_id": site["id"], "cidr": "10.41.10.0/24", "name": "Changed", "slug": "site-a-lan"},
        )
        assert upd.json()["name"] == "Changed"

        child = client.post(
            "/api/v1/ipam/ipv4-prefixes",
            json={"site_id": site["id"], "name": "C", "cidr": "10.41.10.0/25"},
        )
        assert child.status_code == 200
        blocked = client.delete(f"/api/v1/ipam/ipv4-prefixes/{pid}")
        assert blocked.status_code == 409
        assert blocked.json()["detail"]["code"] == "prefix_has_children"

        locked = client.patch(f"/api/v1/ipam/ipv4-prefixes/{pid}", json={"cidr": "10.41.11.0/24"})
        assert locked.status_code == 409
        assert locked.json()["detail"]["code"] == "prefix_cidr_locked"


def test_address_filter_and_offset() -> None:
    app = create_app()
    with TestClient(app) as client:
        site = client.post("/api/v1/dcim/sites", json={"name": "S-off", "slug": "s-off"}).json()
        pfx = client.post(
            "/api/v1/ipam/ipv4-prefixes",
            json={"site_id": site["id"], "name": "LAN", "cidr": "10.0.0.0/29"},
        )
        pid = pfx.json()["id"]
        a = client.post("/api/v1/ipam/ipv4-addresses/request", json={"ipv4_prefix_id": pid, "mode": "reserve"})
        b = client.post("/api/v1/ipam/ipv4-addresses/request", json={"ipv4_prefix_id": pid, "mode": "reserve"})
        assert a.status_code == 200 and b.status_code == 200

        exact = client.get("/api/v1/ipam/ipv4-addresses", params={"address": a.json()["address"]})
        assert exact.status_code == 200
        assert [x["address"] for x in exact.json()] == [a.json()["address"]]

        page = client.get("/api/v1/ipam/ipv4-addresses", params={"ipv4_prefix_id": pid, "limit": 1, "offset": 1})
        assert page.status_code == 200
        assert len(page.json()) == 1
        assert page.json()[0]["address"] == b.json()["address"]
