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
        assert p2.json()["cidr"] == "192.168.1.0/24"
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
