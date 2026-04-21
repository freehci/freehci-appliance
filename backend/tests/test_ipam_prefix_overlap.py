"""Tester for overlapp-regler på IPv4-prefiks per site."""

from fastapi.testclient import TestClient

from app.main import create_app


def test_ipam_prefix_allows_hierarchy() -> None:
    app = create_app()
    with TestClient(app) as client:
        site_id = client.post("/api/v1/dcim/sites", json={"name": "S-overlap", "slug": "s-overlap"}).json()["id"]

        # Parent
        p24 = client.post(
            "/api/v1/ipam/ipv4-prefixes",
            json={"site_id": site_id, "name": "P24", "cidr": "10.0.0.0/24"},
        )
        assert p24.status_code == 200, p24.text

        # Child (tillatt)
        p25 = client.post(
            "/api/v1/ipam/ipv4-prefixes",
            json={"site_id": site_id, "name": "P25", "cidr": "10.0.0.0/25"},
        )
        assert p25.status_code == 200, p25.text


def test_ipam_prefix_disjoint_allowed_on_patch() -> None:
    app = create_app()
    with TestClient(app) as client:
        site_id = client.post("/api/v1/dcim/sites", json={"name": "S-overlap2", "slug": "s-overlap2"}).json()["id"]

        a = client.post(
            "/api/v1/ipam/ipv4-prefixes",
            json={"site_id": site_id, "name": "A", "cidr": "10.1.0.0/24"},
        )
        assert a.status_code == 200, a.text
        a_id = int(a.json()["id"])

        b = client.post(
            "/api/v1/ipam/ipv4-prefixes",
            json={"site_id": site_id, "name": "B", "cidr": "10.1.1.0/24"},
        )
        assert b.status_code == 200, b.text

        # Flytt A slik at den er disjunkt med B.
        ok = client.patch(f"/api/v1/ipam/ipv4-prefixes/{a_id}", json={"cidr": "10.1.2.0/24"})
        assert ok.status_code == 200, ok.text

