"""IPv6 GitOps: address-grid, available-ranges, split og subnet-scan."""

from fastapi.testclient import TestClient

from app.main import create_app
from app.services import ipam_subnet_scan as scan_svc


def _site(client: TestClient, slug: str) -> int:
    return client.post("/api/v1/dcim/sites", json={"name": slug, "slug": slug}).json()["id"]


def test_ipv6_grid_too_large_and_available_ranges() -> None:
    app = create_app()
    with TestClient(app) as client:
        sid = _site(client, "site-v6-grid")
        big = client.post(
            "/api/v1/ipam/ipv6-prefixes",
            json={"site_id": sid, "name": "ula64", "cidr": "fd91:10::/64", "role": "active"},
        )
        assert big.status_code == 200, big.text
        pid = big.json()["id"]
        grid = client.get(f"/api/v1/ipam/ipv6-prefixes/{pid}/address-grid")
        assert grid.status_code == 400
        assert grid.json()["detail"]["code"] == "prefix_too_large_for_grid"

        pin = client.post(
            "/api/v1/ipam/ipv6-addresses/ensure",
            json={"ipv6_prefix_id": pid, "address": "fd91:10::10", "mode": "reserve", "role": "host"},
        )
        assert pin.status_code == 200, pin.text
        ranges = client.get(f"/api/v1/ipam/ipv6-prefixes/{pid}/available-ranges")
        assert ranges.status_code == 200, ranges.text
        body = ranges.json()
        assert body["used_count"] >= 1
        assert any(a["address"] == "fd91:10::10" for a in body["used_addresses"])
        assert "fd91:10::10/128" not in body["free_cidrs"]
        assert any(c.startswith("fd91:10::") for c in body["free_cidrs"])

        small = client.post(
            "/api/v1/ipam/ipv6-prefixes",
            json={"site_id": sid, "name": "ula120", "cidr": "fd91:11::/120", "role": "active"},
        )
        assert small.status_code == 200, small.text
        g2 = client.get(f"/api/v1/ipam/ipv6-prefixes/{small.json()['id']}/address-grid")
        assert g2.status_code == 200, g2.text
        assert len(g2.json()["rows"]) == 256
        assert g2.json()["rows"][0]["address_role"] == "network"


def test_ipv6_allocate_prefixlen_above_32() -> None:
    app = create_app()
    with TestClient(app) as client:
        sid = _site(client, "site-v6-alloc")
        parent = client.post(
            "/api/v1/ipam/ipv6-prefixes",
            json={"site_id": sid, "name": "cont", "cidr": "fd91:20::/48", "role": "container"},
        )
        assert parent.status_code == 200, parent.text
        child = client.post(
            f"/api/v1/ipam/ipv6-prefixes/{parent.json()['id']}/allocate",
            json={"prefixlen": 64, "name": "lan64", "role": "active"},
        )
        assert child.status_code == 200, child.text
        assert child.json()["cidr"].endswith("/64")


def test_ipv6_split_and_split_equal() -> None:
    app = create_app()
    with TestClient(app) as client:
        sid = _site(client, "site-v6-split")
        parent = client.post(
            "/api/v1/ipam/ipv6-prefixes",
            json={"site_id": sid, "name": "split64", "cidr": "fd91:30::/64", "role": "active"},
        )
        assert parent.status_code == 200, parent.text
        pid = parent.json()["id"]
        pinned = client.post(
            "/api/v1/ipam/ipv6-addresses/ensure",
            json={"ipv6_prefix_id": pid, "address": "fd91:30::20", "mode": "reserve"},
        )
        assert pinned.status_code == 200, pinned.text

        dry = client.post(
            f"/api/v1/ipam/ipv6-prefixes/{pid}/split",
            json={
                "first": {"name": "A", "cidr": "fd91:30::/65"},
                "second": {"name": "B", "cidr": "fd91:30:0:0:8000::/65"},
                "dry_run": True,
            },
        )
        assert dry.status_code == 200, dry.text
        assert dry.json()["partition_ok"] is True
        assert dry.json()["first_prefix"] is None
        assert dry.json()["ipam_inventory_on_parent"] == 1

        exe = client.post(
            f"/api/v1/ipam/ipv6-prefixes/{pid}/split",
            json={
                "first": {"name": "A", "cidr": "fd91:30::/65"},
                "second": {"name": "B", "cidr": "fd91:30:0:0:8000::/65"},
                "dry_run": False,
                "migrate_inventory": True,
            },
        )
        assert exe.status_code == 200, exe.text
        assert exe.json()["first_prefix"]["cidr"] == "fd91:30::/65"
        left_id = exe.json()["first_prefix"]["id"]
        listing = client.get("/api/v1/ipam/ipv6-addresses", params={"ipv6_prefix_id": left_id})
        assert listing.status_code == 200
        assert any(x["address"] == "fd91:30::20" for x in listing.json())

        eq_parent = client.post(
            "/api/v1/ipam/ipv6-prefixes",
            json={"site_id": sid, "name": "eq64", "cidr": "fd91:31::/64", "role": "active"},
        )
        eq_id = eq_parent.json()["id"]
        too_many = client.post(
            f"/api/v1/ipam/ipv6-prefixes/{eq_id}/split-equal",
            json={"new_prefix_len": 80, "dry_run": True},
        )
        assert too_many.status_code == 400
        assert too_many.json()["detail"]["code"] == "too_many_subnets"

        eq = client.post(
            f"/api/v1/ipam/ipv6-prefixes/{eq_id}/split-equal",
            json={"new_prefix_len": 66, "dry_run": False, "migrate_inventory": True},
        )
        assert eq.status_code == 200, eq.text
        assert eq.json()["subnet_count"] == 4
        assert len(eq.json()["created_prefixes"]) == 4


def test_ipv6_subnet_scan(monkeypatch) -> None:
    real_run = scan_svc.run_scan_background

    def run_mocked(scan_id: int) -> None:
        real_run(
            scan_id,
            ping_fn=lambda ip: ip == "fd91:40::1",
            load_mac_fn=lambda: {"fd91:40::1": "aa:bb:cc:dd:ee:02"},
        )

    monkeypatch.setattr("app.api.v1.routers.ipam.scan_svc.run_scan_background", run_mocked)

    app = create_app()
    with TestClient(app) as client:
        sid = _site(client, "site-v6-scan")
        pfx = client.post(
            "/api/v1/ipam/ipv6-prefixes",
            json={"site_id": sid, "name": "scan120", "cidr": "fd91:40::/120", "role": "active"},
        )
        assert pfx.status_code == 200, pfx.text
        pid = pfx.json()["id"]

        too_big = client.post(
            "/api/v1/ipam/ipv6-prefixes",
            json={"site_id": sid, "name": "scan64", "cidr": "fd91:41::/64", "role": "active"},
        )
        blocked = client.post("/api/v1/ipam/subnet-scans", json={"ipv6_prefix_id": too_big.json()["id"]})
        assert blocked.status_code == 400
        assert blocked.json()["detail"]["code"] == "prefix_too_large_for_scan"

        r = client.post("/api/v1/ipam/subnet-scans", json={"ipv6_prefix_id": pid})
        assert r.status_code == 200, r.text
        assert r.json()["ipv6_prefix_id"] == pid
        scan_id = r.json()["id"]
        d = client.get(f"/api/v1/ipam/subnet-scans/{scan_id}")
        assert d.status_code == 200, d.text
        assert d.json()["status"] == "completed"
        assert d.json()["hosts_scanned"] == 256
        assert d.json()["hosts_responding"] == 1
        alive = [h for h in d.json()["hosts"] if h["ping_responded"]]
        assert alive[0]["address"] == "fd91:40::1"
        assert alive[0]["mac_address"] == "aa:bb:cc:dd:ee:02"

        li = client.get("/api/v1/ipam/subnet-scans", params={"ipv6_prefix_id": pid})
        assert any(x["id"] == scan_id for x in li.json())

        inv = client.get("/api/v1/ipam/ipv6-addresses", params={"ipv6_prefix_id": pid})
        assert any(x["address"] == "fd91:40::1" and x["status"] == "discovered" for x in inv.json())
