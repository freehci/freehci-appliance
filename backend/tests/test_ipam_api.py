"""API-tester for IPAM IPv4-prefiks (per site)."""

from fastapi.testclient import TestClient

from app.main import create_app


def test_ipam_ipv4_prefix_same_cidr_different_sites() -> None:
    app = create_app()
    with TestClient(app) as client:
        a = client.post("/api/v1/dcim/sites", json={"name": "Kontor A", "slug": "site-a"})
        b = client.post("/api/v1/dcim/sites", json={"name": "Kontor B", "slug": "site-b"})
        assert a.status_code == 200 and b.status_code == 200
        sa, sb = a.json()["id"], b.json()["id"]

        p1 = client.post(
            "/api/v1/ipam/ipv4-prefixes",
            json={
                "site_id": sa,
                "name": "LAN",
                "cidr": "192.168.1.0/24",
            },
        )
        p2 = client.post(
            "/api/v1/ipam/ipv4-prefixes",
            json={
                "site_id": sb,
                "name": "LAN",
                "cidr": "192.168.1.0/24",
            },
        )
        assert p1.status_code == 200, p1.text
        assert p2.status_code == 200, p2.text
        assert p1.json()["cidr"] == "192.168.1.0/24"
        assert p1.json()["used_count"] == 0
        assert p1.json()["address_total"] == 256
        assert p2.json()["cidr"] == "192.168.1.0/24"
        assert p2.json()["address_total"] == 256
        assert p1.json()["site_id"] == sa
        assert p2.json()["site_id"] == sb

        dup = client.post(
            "/api/v1/ipam/ipv4-prefixes",
            json={"site_id": sa, "name": "Dup", "cidr": "192.168.1.0/24"},
        )
        assert dup.status_code == 409

        li = client.get("/api/v1/ipam/ipv4-prefixes")
        assert li.status_code == 200
        rows = li.json()
        assert sum(1 for x in rows if x["site_id"] == sa and x["cidr"] == "192.168.1.0/24") == 1
        assert sum(1 for x in rows if x["site_id"] == sb and x["cidr"] == "192.168.1.0/24") == 1

        f = client.get(f"/api/v1/ipam/ipv4-prefixes?site_id={sa}")
        assert f.status_code == 200
        assert sum(1 for x in f.json() if x["cidr"] == "192.168.1.0/24") == 1

        bad = client.post(
            "/api/v1/ipam/ipv4-prefixes",
            json={"site_id": sa, "name": "V6", "cidr": "2001:db8::/32"},
        )
        assert bad.status_code == 400


def test_ipam_ipv4_prefix_unknown_site() -> None:
    app = create_app()
    with TestClient(app) as client:
        r = client.post(
            "/api/v1/ipam/ipv4-prefixes",
            json={"site_id": 99999, "name": "X", "cidr": "10.0.0.0/8"},
        )
        assert r.status_code == 404


def test_ipam_ipv4_prefix_explore_child_prefixes() -> None:
    app = create_app()
    with TestClient(app) as client:
        sa = client.post("/api/v1/dcim/sites", json={"name": "Ex", "slug": "ipam-ex"}).json()["id"]
        p16 = client.post(
            "/api/v1/ipam/ipv4-prefixes",
            json={"site_id": sa, "name": "Core", "cidr": "10.0.0.0/16"},
        )
        p24 = client.post(
            "/api/v1/ipam/ipv4-prefixes",
            json={"site_id": sa, "name": "LAN", "cidr": "10.0.1.0/24"},
        )
        assert p16.status_code == 200 and p24.status_code == 200
        id16 = p16.json()["id"]
        id24 = p24.json()["id"]

        ex = client.get(f"/api/v1/ipam/ipv4-prefixes/{id16}/explore")
        assert ex.status_code == 200, ex.text
        data = ex.json()
        assert data["prefix"]["id"] == id16
        child_ids = [x["id"] for x in data["child_prefixes"]]
        assert id24 in child_ids

        ex24 = client.get(f"/api/v1/ipam/ipv4-prefixes/{id24}/explore")
        assert ex24.status_code == 200
        assert ex24.json()["child_prefixes"] == []


def test_ipam_ipv4_prefix_patch() -> None:
    app = create_app()
    with TestClient(app) as client:
        sa = client.post("/api/v1/dcim/sites", json={"name": "PatchSite", "slug": "patch-site"}).json()["id"]
        p = client.post(
            "/api/v1/ipam/ipv4-prefixes",
            json={"site_id": sa, "name": "Old", "cidr": "10.0.0.0/24"},
        )
        assert p.status_code == 200
        pid = p.json()["id"]

        up = client.patch(
            f"/api/v1/ipam/ipv4-prefixes/{pid}",
            json={"name": "New", "cidr": "10.0.1.0/24"},
        )
        assert up.status_code == 200, up.text
        assert up.json()["name"] == "New"
        assert up.json()["cidr"] == "10.0.1.0/24"
        assert up.json()["used_count"] == 0
        assert up.json()["address_total"] == 256
