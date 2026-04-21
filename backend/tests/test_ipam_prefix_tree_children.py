"""Direkte barn-prefiks (tre-nivå) i IPAM explore."""

from fastapi.testclient import TestClient

from app.main import create_app


def test_explore_child_prefixes_only_immediate_children() -> None:
    app = create_app()
    with TestClient(app) as client:
        site_id = client.post("/api/v1/dcim/sites", json={"name": "S-tree", "slug": "s-tree"}).json()["id"]

        p24 = client.post(
            "/api/v1/ipam/ipv4-prefixes",
            json={"site_id": site_id, "name": "Root", "cidr": "10.27.13.0/24"},
        )
        assert p24.status_code == 200, p24.text
        id24 = int(p24.json()["id"])

        a25 = client.post(
            "/api/v1/ipam/ipv4-prefixes",
            json={"site_id": site_id, "name": "A /25", "cidr": "10.27.13.0/25"},
        )
        assert a25.status_code == 200, a25.text
        id_a25 = int(a25.json()["id"])

        b25 = client.post(
            "/api/v1/ipam/ipv4-prefixes",
            json={"site_id": site_id, "name": "B /25", "cidr": "10.27.13.128/25"},
        )
        assert b25.status_code == 200, b25.text

        s26 = client.post(
            "/api/v1/ipam/ipv4-prefixes",
            json={"site_id": site_id, "name": "Under A", "cidr": "10.27.13.0/26"},
        )
        assert s26.status_code == 200, s26.text

        ex24 = client.get(f"/api/v1/ipam/ipv4-prefixes/{id24}/explore")
        assert ex24.status_code == 200, ex24.text
        child_ids = {int(x["id"]) for x in ex24.json()["child_prefixes"]}
        assert child_ids == {id_a25, int(b25.json()["id"])}

        ex_a = client.get(f"/api/v1/ipam/ipv4-prefixes/{id_a25}/explore")
        assert ex_a.status_code == 200, ex_a.text
        child_a = {int(x["id"]) for x in ex_a.json()["child_prefixes"]}
        assert child_a == {int(s26.json()["id"])}
