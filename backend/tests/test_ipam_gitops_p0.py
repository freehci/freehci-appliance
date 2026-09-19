"""P0 IPAM-oppførsel for GitOps: oppslag, ensure, tildeling og sletting."""

from fastapi.testclient import TestClient

from app.main import create_app


def _site_and_prefix(client: TestClient, *, slug: str, cidr: str = "192.0.2.0/24", name: str = "LAN"):
    site = client.post("/api/v1/dcim/sites", json={"name": f"S-{slug}", "slug": slug}).json()
    pfx = client.post(
        "/api/v1/ipam/ipv4-prefixes",
        json={
            "site_id": site["id"],
            "name": name,
            "slug": f"{slug}-lan",
            "cidr": cidr,
            "subnet_services": {"gateway": "192.0.2.1"},
        },
    )
    assert pfx.status_code == 200, pfx.text
    return site["id"], pfx.json()


def test_prefix_lookup_filters_and_ensure() -> None:
    app = create_app()
    with TestClient(app) as client:
        site_id, pfx = _site_and_prefix(client, slug="p0-lookup")
        pid = pfx["id"]
        assert pfx["slug"] == "p0-lookup-lan"
        assert pfx["subnet_services"]["gateway"] == "192.0.2.1"

        by_cidr = client.get("/api/v1/ipam/ipv4-prefixes", params={"cidr": "192.0.2.0/24"})
        assert by_cidr.status_code == 200
        assert [x["id"] for x in by_cidr.json()] == [pid]

        by_slug = client.get("/api/v1/ipam/ipv4-prefixes", params={"slug": "p0-lookup-lan", "site_id": site_id})
        assert by_slug.status_code == 200
        assert [x["id"] for x in by_slug.json()] == [pid]

        by_name = client.get("/api/v1/ipam/ipv4-prefixes", params={"name": "lan", "site_id": site_id})
        assert by_name.status_code == 200
        assert [x["id"] for x in by_name.json()] == [pid]

        by_q = client.get("/api/v1/ipam/ipv4-prefixes", params={"q": "lookup-lan"})
        assert by_q.status_code == 200
        assert any(x["id"] == pid for x in by_q.json())

        by_addr = client.get("/api/v1/ipam/ipv4-prefixes", params={"address": "192.0.2.10", "site_id": site_id})
        assert by_addr.status_code == 200
        assert any(x["id"] == pid for x in by_addr.json())

        miss = client.get("/api/v1/ipam/ipv4-prefixes", params={"cidr": "10.9.9.0/24"})
        assert miss.status_code == 200
        assert miss.json() == []

        ens = client.post(
            "/api/v1/ipam/ipv4-prefixes/ensure",
            json={"site_id": site_id, "cidr": "192.0.2.0/24", "name": "Other"},
        )
        assert ens.status_code == 200, ens.text
        assert ens.json()["id"] == pid
        assert ens.json()["name"] == "LAN"
        assert ens.json()["created"] is False

        created = client.post(
            "/api/v1/ipam/ipv4-prefixes/ensure",
            json={"site_id": site_id, "cidr": "10.41.10.0/24", "name": "Pod", "slug": "site-a-pod"},
        )
        assert created.status_code == 200, created.text
        assert created.json()["cidr"] == "10.41.10.0/24"
        assert created.json()["slug"] == "site-a-pod"

        again = client.post(
            "/api/v1/ipam/ipv4-prefixes/ensure",
            json={"site_id": site_id, "cidr": "10.41.10.0/24", "slug": "ignored"},
        )
        assert again.status_code == 200
        assert again.json()["id"] == created.json()["id"]
        assert again.json()["slug"] == "site-a-pod"


def test_request_skips_gateway_and_counts_inventory() -> None:
    app = create_app()
    with TestClient(app) as client:
        _site_id, pfx = _site_and_prefix(client, slug="p0-gw")
        pid = pfx["id"]
        assert pfx["used_count"] == 0

        r1 = client.post("/api/v1/ipam/ipv4-addresses/request", json={"ipv4_prefix_id": pid, "mode": "reserve"})
        assert r1.status_code == 200, r1.text
        assert r1.json()["address"] == "192.0.2.2"
        assert r1.json()["status"] == "reserved"

        got = client.get(f"/api/v1/ipam/ipv4-prefixes/{pid}")
        assert got.status_code == 200
        assert got.json()["used_count"] == 1

        r2 = client.post(
            "/api/v1/ipam/ipv4-addresses/request",
            json={"ipv4_prefix_id": pid, "mode": "assign", "note": "talos-vip"},
        )
        assert r2.status_code == 200, r2.text
        assert r2.json()["address"] == "192.0.2.3"
        assert r2.json()["status"] == "assigned"
        assert r2.json()["interface_id"] is None
        assert r2.json()["note"] == "talos-vip"

        got2 = client.get(f"/api/v1/ipam/ipv4-prefixes/{pid}")
        assert got2.json()["used_count"] == 2


def test_ensure_address_mode_note_and_reject_network() -> None:
    app = create_app()
    with TestClient(app) as client:
        _site_id, pfx = _site_and_prefix(client, slug="p0-ens")
        pid = pfx["id"]

        pin = client.post(
            "/api/v1/ipam/ipv4-addresses/ensure",
            json={
                "ipv4_prefix_id": pid,
                "address": "192.0.2.10",
                "mode": "reserve",
                "note": "cilium-lb",
            },
        )
        assert pin.status_code == 200, pin.text
        assert pin.json()["status"] == "reserved"
        assert pin.json()["note"] == "cilium-lb"
        assert pin.json()["address"] == "192.0.2.10"

        lookup = client.post(
            "/api/v1/ipam/ipv4-addresses/ensure",
            json={"ipv4_prefix_id": pid, "address": "192.0.2.10", "note": "should-not-stick"},
        )
        assert lookup.status_code == 200
        assert lookup.json()["id"] == pin.json()["id"]
        assert lookup.json()["note"] == "cilium-lb"
        assert lookup.json()["created"] is False

        again = client.post(
            "/api/v1/ipam/ipv4-addresses/ensure?update=true",
            json={"ipv4_prefix_id": pid, "address": "192.0.2.10", "note": "updated"},
        )
        assert again.status_code == 200
        assert again.json()["id"] == pin.json()["id"]
        assert again.json()["note"] == "updated"
        assert again.json()["status"] == "reserved"

        one = client.get(f"/api/v1/ipam/ipv4-addresses/{pin.json()['id']}")
        assert one.status_code == 200
        assert one.json()["address"] == "192.0.2.10"

        net = client.post(
            "/api/v1/ipam/ipv4-addresses/ensure",
            json={"ipv4_prefix_id": pid, "address": "192.0.2.0", "mode": "reserve"},
        )
        assert net.status_code == 400

        bcast = client.post(
            "/api/v1/ipam/ipv4-addresses/ensure",
            json={"ipv4_prefix_id": pid, "address": "192.0.2.255", "mode": "assign"},
        )
        assert bcast.status_code == 400

        discovered = client.post(
            "/api/v1/ipam/ipv4-addresses/ensure",
            json={"ipv4_prefix_id": pid, "address": "192.0.2.0"},
        )
        assert discovered.status_code == 200
        assert discovered.json()["status"] == "discovered"


def test_hard_delete_address_and_prefix_409_or_cascade() -> None:
    app = create_app()
    with TestClient(app) as client:
        site_id, pfx = _site_and_prefix(client, slug="p0-del")
        pid = pfx["id"]
        child = client.post(
            "/api/v1/ipam/ipv4-prefixes",
            json={"site_id": site_id, "name": "Child", "cidr": "192.0.2.0/25"},
        )
        assert child.status_code == 200, child.text
        cid = child.json()["id"]

        reserved = client.post(
            "/api/v1/ipam/ipv4-addresses/request",
            json={"ipv4_prefix_id": pid, "mode": "reserve"},
        )
        assert reserved.status_code == 200
        addr_id = reserved.json()["id"]

        blocked = client.delete(f"/api/v1/ipam/ipv4-prefixes/{pid}")
        assert blocked.status_code == 409, blocked.text

        gone = client.delete(f"/api/v1/ipam/ipv4-addresses/{addr_id}")
        assert gone.status_code == 204
        missing = client.get(f"/api/v1/ipam/ipv4-addresses/{addr_id}")
        assert missing.status_code == 404

        still = client.delete(f"/api/v1/ipam/ipv4-prefixes/{pid}")
        assert still.status_code == 409

        casc = client.delete(f"/api/v1/ipam/ipv4-prefixes/{pid}?cascade=true")
        assert casc.status_code == 204, casc.text
        assert client.get(f"/api/v1/ipam/ipv4-prefixes/{pid}").status_code == 404
        assert client.get(f"/api/v1/ipam/ipv4-prefixes/{cid}").status_code == 404

        leftover = client.get("/api/v1/ipam/ipv4-addresses", params={"site_id": site_id})
        assert leftover.status_code == 200
        assert leftover.json() == []
