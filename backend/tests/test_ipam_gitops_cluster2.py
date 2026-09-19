"""GitOps-blokk 2: barn-prefiks, ranges, atomisk batch, bind, device site."""

from fastapi.testclient import TestClient

from app.main import create_app


def _site(client: TestClient, slug: str) -> int:
    return client.post("/api/v1/dcim/sites", json={"name": slug, "slug": slug}).json()["id"]


def test_allocate_next_child_prefix_and_slug_idempotent() -> None:
    app = create_app()
    with TestClient(app) as client:
        sid = _site(client, "site-alloc")
        parent = client.post(
            "/api/v1/ipam/ipv4-prefixes",
            json={
                "site_id": sid,
                "name": "underlay",
                "cidr": "10.71.0.0/16",
                "slug": "site-a-underlay",
                "role": "container",
            },
        )
        assert parent.status_code == 200, parent.text
        pid = parent.json()["id"]

        avail = client.get(f"/api/v1/ipam/ipv4-prefixes/{pid}/available-prefixes", params={"prefixlen": 24})
        assert avail.status_code == 200, avail.text
        assert avail.json()["available"][0] == "10.71.0.0/24"

        a1 = client.post(
            f"/api/v1/ipam/ipv4-prefixes/{pid}/allocate",
            json={"prefixlen": 24, "name": "cluster-1", "slug": "site-a-talos-c1", "role": "active"},
        )
        assert a1.status_code == 200, a1.text
        assert a1.json()["cidr"] == "10.71.0.0/24"
        assert a1.json()["created"] is True
        assert a1.json()["parent_id"] == pid

        a2 = client.post(
            f"/api/v1/ipam/ipv4-prefixes/{pid}/allocate",
            json={"prefixlen": 24, "name": "cluster-2", "slug": "site-a-talos-c2", "role": "active"},
        )
        assert a2.status_code == 200, a2.text
        assert a2.json()["cidr"] == "10.71.1.0/24"

        again = client.post(
            f"/api/v1/ipam/ipv4-prefixes/{pid}/allocate",
            json={"prefixlen": 24, "name": "other", "slug": "site-a-talos-c1", "role": "active"},
        )
        assert again.status_code == 200
        assert again.json()["id"] == a1.json()["id"]
        assert again.json()["created"] is False

        overlay = client.post(
            "/api/v1/ipam/ipv4-prefixes",
            json={"site_id": sid, "name": "pods", "cidr": "10.80.0.0/16", "role": "overlay-pod"},
        )
        bad = client.post(
            f"/api/v1/ipam/ipv4-prefixes/{overlay.json()['id']}/allocate",
            json={"prefixlen": 24, "name": "nope", "slug": "nope"},
        )
        assert bad.status_code == 409
        assert bad.json()["detail"]["code"] == "prefix_role_forbids_child_alloc"


def test_available_ranges_and_grid_limit() -> None:
    app = create_app()
    with TestClient(app) as client:
        sid = _site(client, "site-ranges")
        pool = client.post(
            "/api/v1/ipam/ipv4-prefixes",
            json={"site_id": sid, "name": "lb", "cidr": "10.82.0.0/24", "role": "lb-pool"},
        )
        pid = pool.json()["id"]
        client.post(
            "/api/v1/ipam/ipv4-addresses/ensure",
            json={"ipv4_prefix_id": pid, "address": "10.82.0.10", "mode": "reserve", "role": "lb"},
        )
        ranges = client.get(f"/api/v1/ipam/ipv4-prefixes/{pid}/available-ranges")
        assert ranges.status_code == 200, ranges.text
        body = ranges.json()
        assert body["used_count"] >= 1
        assert any(a["address"] == "10.82.0.10" for a in body["used_addresses"])
        assert "10.82.0.10/32" not in body["free_cidrs"]
        assert any(c.startswith("10.82.0.") for c in body["free_cidrs"])

        big = client.post(
            "/api/v1/ipam/ipv4-prefixes",
            json={"site_id": sid, "name": "pods", "cidr": "10.80.0.0/16", "role": "overlay-pod"},
        )
        grid = client.get(f"/api/v1/ipam/ipv4-prefixes/{big.json()['id']}/address-grid")
        assert grid.status_code == 400
        assert grid.json()["detail"]["code"] == "prefix_too_large_for_grid"


def test_request_batch_is_atomic() -> None:
    app = create_app()
    with TestClient(app) as client:
        sid = _site(client, "site-atomic")
        pfx = client.post(
            "/api/v1/ipam/ipv4-prefixes",
            json={"site_id": sid, "name": "lan", "cidr": "10.10.0.0/29"},
        )
        pid = pfx.json()["id"]
        first = client.post(
            "/api/v1/ipam/ipv4-addresses/request-batch",
            json={"ipv4_prefix_id": pid, "mode": "reserve", "count": 5},
        )
        assert first.status_code == 200
        assert first.json()["allocated_count"] == 5

        before = client.get("/api/v1/ipam/ipv4-addresses", params={"ipv4_prefix_id": pid, "status": "reserved"})
        assert len(before.json()) == 5

        second = client.post(
            "/api/v1/ipam/ipv4-addresses/request-batch",
            json={"ipv4_prefix_id": pid, "mode": "reserve", "count": 2},
        )
        assert second.status_code == 409
        assert second.json()["detail"]["code"] == "no_free_address"

        after = client.get("/api/v1/ipam/ipv4-addresses", params={"ipv4_prefix_id": pid, "status": "reserved"})
        assert len(after.json()) == 5


def test_idempotency_key_on_request() -> None:
    app = create_app()
    with TestClient(app) as client:
        sid = _site(client, "site-idem")
        pfx = client.post(
            "/api/v1/ipam/ipv4-prefixes",
            json={"site_id": sid, "name": "lan", "cidr": "10.71.10.0/24"},
        )
        pid = pfx.json()["id"]
        headers = {"Idempotency-Key": "vip-bootstrap-1"}
        body = {"ipv4_prefix_id": pid, "mode": "reserve", "role": "vip"}
        r1 = client.post("/api/v1/ipam/ipv4-addresses/request", json=body, headers=headers)
        assert r1.status_code == 200, r1.text
        r2 = client.post("/api/v1/ipam/ipv4-addresses/request", json=body, headers=headers)
        assert r2.status_code == 200
        assert r2.json()["id"] == r1.json()["id"]
        assert r2.json()["address"] == r1.json()["address"]

        other = client.post(
            "/api/v1/ipam/ipv4-addresses/request",
            json={"ipv4_prefix_id": pid, "mode": "reserve", "role": "host"},
            headers=headers,
        )
        assert other.status_code == 409
        assert other.json()["detail"]["code"] == "idempotency_key_reuse"


def test_bind_existing_ip_and_device_site() -> None:
    app = create_app()
    with TestClient(app) as client:
        sid = _site(client, "site-bind")
        pfx = client.post(
            "/api/v1/ipam/ipv4-prefixes",
            json={"site_id": sid, "name": "lan", "cidr": "10.71.10.0/24"},
        )
        pid = pfx.json()["id"]
        reserved = client.post(
            "/api/v1/ipam/ipv4-addresses/ensure",
            json={"ipv4_prefix_id": pid, "address": "10.71.10.11", "mode": "reserve", "role": "host"},
        )
        assert reserved.status_code == 200
        addr_id = reserved.json()["id"]

        mid = client.post("/api/v1/dcim/manufacturers", json={"name": "M-bind"}).json()["id"]
        tid = client.post("/api/v1/dcim/device-types", json={"name": "T-bind", "slug": "t-bind"}).json()["id"]
        dmod = client.post(
            "/api/v1/dcim/device-models",
            json={"manufacturer_id": mid, "device_type_id": tid, "name": "N1", "u_height": 1},
        ).json()["id"]
        dev = client.post("/api/v1/dcim/devices", json={"device_model_id": dmod, "name": "talos-1", "site_id": sid})
        assert dev.status_code == 200, dev.text
        assert dev.json()["site_id"] == sid
        assert dev.json()["effective_site_id"] == sid
        dev_id = dev.json()["id"]
        if_id = client.post(f"/api/v1/dcim/devices/{dev_id}/interfaces", json={"name": "eth0"}).json()["id"]

        bound = client.post(f"/api/v1/ipam/ipv4-addresses/{addr_id}/bind", json={"device_id": dev_id, "interface_id": if_id})
        assert bound.status_code == 200, bound.text
        assert bound.json()["id"] == addr_id
        assert bound.json()["device_id"] == dev_id
        assert bound.json()["interface_id"] == if_id
        assert bound.json()["status"] == "assigned"

        listed = client.get("/api/v1/ipam/ipv4-addresses", params={"address": "10.71.10.11"})
        assert len(listed.json()) == 1

        got = client.get(f"/api/v1/ipam/ipv4-prefixes/{pid}")
        assert got.json()["used_count"] == 1


def test_placement_inherits_device_site() -> None:
    app = create_app()
    with TestClient(app) as client:
        sid = _site(client, "site-inherit")
        room = client.post("/api/v1/dcim/rooms", json={"site_id": sid, "name": "R"}).json()["id"]
        rack = client.post("/api/v1/dcim/racks", json={"room_id": room, "name": "K"}).json()["id"]
        mid = client.post("/api/v1/dcim/manufacturers", json={"name": "M-inh"}).json()["id"]
        tid = client.post("/api/v1/dcim/device-types", json={"name": "T-inh", "slug": "t-inh"}).json()["id"]
        dmod = client.post(
            "/api/v1/dcim/device-models",
            json={"manufacturer_id": mid, "device_type_id": tid, "name": "N", "u_height": 1},
        ).json()["id"]
        dev = client.post("/api/v1/dcim/devices", json={"device_model_id": dmod, "name": "srv"})
        assert dev.json()["effective_site_id"] is None
        dev_id = dev.json()["id"]
        pl = client.post(
            "/api/v1/dcim/placements",
            json={"rack_id": rack, "device_id": dev_id, "u_position": 1, "mounting": "front"},
        )
        assert pl.status_code == 200, pl.text
        got = client.get(f"/api/v1/dcim/devices/{dev_id}")
        assert got.json()["site_id"] == sid
        assert got.json()["effective_site_id"] == sid
