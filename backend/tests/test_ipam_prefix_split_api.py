"""API for deling av IPv4-prefiks (split)."""

from fastapi.testclient import TestClient

from app.main import create_app


def test_split_dry_run_ok_halves() -> None:
    app = create_app()
    with TestClient(app) as client:
        site_id = client.post("/api/v1/dcim/sites", json={"name": "S-split", "slug": "s-split"}).json()["id"]
        p = client.post(
            "/api/v1/ipam/ipv4-prefixes",
            json={"site_id": site_id, "name": "Root", "cidr": "10.40.0.0/24"},
        )
        assert p.status_code == 200, p.text
        pid = int(p.json()["id"])

        r = client.post(
            f"/api/v1/ipam/ipv4-prefixes/{pid}/split",
            json={
                "first": {"name": "A", "cidr": "10.40.0.0/25"},
                "second": {"name": "B", "cidr": "10.40.0.128/25"},
                "dry_run": True,
                "migrate_inventory": True,
                "acknowledge_network_broadcast": False,
            },
        )
        assert r.status_code == 200, r.text
        j = r.json()
        assert j["has_child_prefixes"] is False
        assert j["partition_ok"] is True
        assert j["first_cidr"] == "10.40.0.0/25"
        assert j["second_cidr"] == "10.40.0.128/25"
        assert j["first_prefix"] is None


def test_split_blocked_when_child_prefix_exists() -> None:
    app = create_app()
    with TestClient(app) as client:
        site_id = client.post("/api/v1/dcim/sites", json={"name": "S-split2", "slug": "s-split2"}).json()["id"]
        p24 = client.post(
            "/api/v1/ipam/ipv4-prefixes",
            json={"site_id": site_id, "name": "R", "cidr": "10.41.0.0/24"},
        )
        assert p24.status_code == 200, p24.text
        pid = int(p24.json()["id"])
        c = client.post(
            "/api/v1/ipam/ipv4-prefixes",
            json={"site_id": site_id, "name": "C", "cidr": "10.41.0.0/25"},
        )
        assert c.status_code == 200, c.text

        r = client.post(
            f"/api/v1/ipam/ipv4-prefixes/{pid}/split",
            json={
                "first": {"name": "A", "cidr": "10.41.0.0/25"},
                "second": {"name": "B", "cidr": "10.41.0.128/25"},
                "dry_run": True,
                "migrate_inventory": True,
                "acknowledge_network_broadcast": False,
            },
        )
        assert r.status_code == 200, r.text
        assert r.json()["has_child_prefixes"] is True
        assert r.json()["partition_ok"] is False


def test_split_execute_migrates_inventory() -> None:
    app = create_app()
    with TestClient(app) as client:
        site_id = client.post("/api/v1/dcim/sites", json={"name": "S-split3", "slug": "s-split3"}).json()["id"]
        p = client.post(
            "/api/v1/ipam/ipv4-prefixes",
            json={"site_id": site_id, "name": "R", "cidr": "10.42.0.0/24"},
        )
        assert p.status_code == 200, p.text
        pid = int(p.json()["id"])
        e = client.post(
            "/api/v1/ipam/ipv4-addresses/ensure",
            json={"ipv4_prefix_id": pid, "address": "10.42.0.10"},
        )
        assert e.status_code == 200, e.text
        aid = int(e.json()["id"])

        r = client.post(
            f"/api/v1/ipam/ipv4-prefixes/{pid}/split",
            json={
                "first": {"name": "Lo", "cidr": "10.42.0.0/25"},
                "second": {"name": "Hi", "cidr": "10.42.0.128/25"},
                "dry_run": False,
                "migrate_inventory": True,
                "acknowledge_network_broadcast": False,
            },
        )
        assert r.status_code == 200, r.text
        j = r.json()
        assert j["first_prefix"] is not None
        assert j["second_prefix"] is not None
        lid = int(j["first_prefix"]["id"])
        rid = int(j["second_prefix"]["id"])

        row = client.get(f"/api/v1/ipam/ipv4-addresses?site_id={site_id}&limit=50").json()
        inv = next(x for x in row if int(x["id"]) == aid)
        assert int(inv["ipv4_prefix_id"]) == lid


def test_split_network_address_conflict_requires_ack() -> None:
    app = create_app()
    with TestClient(app) as client:
        site_id = client.post("/api/v1/dcim/sites", json={"name": "S-split4", "slug": "s-split4"}).json()["id"]
        p = client.post(
            "/api/v1/ipam/ipv4-prefixes",
            json={"site_id": site_id, "name": "R", "cidr": "10.43.0.0/24"},
        )
        assert p.status_code == 200, p.text
        pid = int(p.json()["id"])
        e = client.post(
            "/api/v1/ipam/ipv4-addresses/ensure",
            json={"ipv4_prefix_id": pid, "address": "10.43.0.0"},
        )
        assert e.status_code == 200, e.text

        bad = client.post(
            f"/api/v1/ipam/ipv4-prefixes/{pid}/split",
            json={
                "first": {"name": "Lo", "cidr": "10.43.0.0/25"},
                "second": {"name": "Hi", "cidr": "10.43.0.128/25"},
                "dry_run": False,
                "migrate_inventory": True,
                "acknowledge_network_broadcast": False,
            },
        )
        assert bad.status_code == 409, bad.text

        ok = client.post(
            f"/api/v1/ipam/ipv4-prefixes/{pid}/split",
            json={
                "first": {"name": "Lo", "cidr": "10.43.0.0/25"},
                "second": {"name": "Hi", "cidr": "10.43.0.128/25"},
                "dry_run": False,
                "migrate_inventory": True,
                "acknowledge_network_broadcast": True,
            },
        )
        assert ok.status_code == 200, ok.text
        assert ok.json()["first_prefix"] is not None


def test_split_equal_dry_run_quarters() -> None:
    app = create_app()
    with TestClient(app) as client:
        site_id = client.post("/api/v1/dcim/sites", json={"name": "S-eq1", "slug": "s-eq1"}).json()["id"]
        p = client.post(
            "/api/v1/ipam/ipv4-prefixes",
            json={"site_id": site_id, "name": "R", "cidr": "10.44.0.0/24"},
        )
        assert p.status_code == 200, p.text
        pid = int(p.json()["id"])

        r = client.post(
            f"/api/v1/ipam/ipv4-prefixes/{pid}/split-equal",
            json={
                "new_prefix_len": 26,
                "dry_run": True,
                "migrate_inventory": True,
                "acknowledge_network_broadcast": False,
            },
        )
        assert r.status_code == 200, r.text
        j = r.json()
        assert j["subnet_count"] == 4
        assert j["partition_ok"] is True
        assert len(j["planned"]) == 4
        assert j["planned"][0]["cidr"] == j["planned"][0]["suggested_name"]


def test_split_equal_too_many_subnets_returns_400() -> None:
    app = create_app()
    with TestClient(app) as client:
        site_id = client.post("/api/v1/dcim/sites", json={"name": "S-eq2", "slug": "s-eq2"}).json()["id"]
        p = client.post(
            "/api/v1/ipam/ipv4-prefixes",
            json={"site_id": site_id, "name": "R", "cidr": "10.45.0.0/16"},
        )
        assert p.status_code == 200, p.text
        pid = int(p.json()["id"])

        r = client.post(
            f"/api/v1/ipam/ipv4-prefixes/{pid}/split-equal",
            json={
                "new_prefix_len": 25,
                "dry_run": True,
                "migrate_inventory": True,
                "acknowledge_network_broadcast": False,
            },
        )
        assert r.status_code == 400, r.text


def test_split_equal_execute_migrates_inventory() -> None:
    app = create_app()
    with TestClient(app) as client:
        site_id = client.post("/api/v1/dcim/sites", json={"name": "S-eq3", "slug": "s-eq3"}).json()["id"]
        p = client.post(
            "/api/v1/ipam/ipv4-prefixes",
            json={"site_id": site_id, "name": "R", "cidr": "10.46.0.0/24"},
        )
        assert p.status_code == 200, p.text
        pid = int(p.json()["id"])
        e = client.post(
            "/api/v1/ipam/ipv4-addresses/ensure",
            json={"ipv4_prefix_id": pid, "address": "10.46.0.200"},
        )
        assert e.status_code == 200, e.text
        aid = int(e.json()["id"])

        r = client.post(
            f"/api/v1/ipam/ipv4-prefixes/{pid}/split-equal",
            json={
                "new_prefix_len": 25,
                "dry_run": False,
                "migrate_inventory": True,
                "acknowledge_network_broadcast": False,
            },
        )
        assert r.status_code == 200, r.text
        created = r.json()["created_prefixes"]
        assert len(created) == 2
        hi = next(x for x in created if x["cidr"] == "10.46.0.128/25")
        row = client.get(f"/api/v1/ipam/ipv4-addresses?site_id={site_id}&limit=50").json()
        inv = next(x for x in row if int(x["id"]) == aid)
        assert int(inv["ipv4_prefix_id"]) == int(hi["id"])
        assert inv["address"] == "10.46.0.200"
