"""GitOps-kontrakt: If-Match, release vs DELETE, liste-total."""

from fastapi.testclient import TestClient

from app.main import create_app


def _site_prefix(client: TestClient, slug: str, cidr: str = "10.90.0.0/24") -> tuple[int, int]:
    sid = client.post("/api/v1/dcim/sites", json={"name": slug, "slug": slug}).json()["id"]
    pfx = client.post("/api/v1/ipam/ipv4-prefixes", json={"site_id": sid, "name": "lan", "cidr": cidr})
    assert pfx.status_code == 200, pfx.text
    return sid, pfx.json()["id"]


def test_if_match_rejects_stale_prefix_patch() -> None:
    app = create_app()
    with TestClient(app) as client:
        _, pid = _site_prefix(client, "etag-pfx")
        got = client.get(f"/api/v1/ipam/ipv4-prefixes/{pid}")
        assert got.status_code == 200
        etag = got.json()["etag"]
        assert etag
        assert got.headers.get("etag") == etag

        stale = client.patch(
            f"/api/v1/ipam/ipv4-prefixes/{pid}",
            json={"name": "nope"},
            headers={"If-Match": 'W/"0-1970-01-01T00:00:00+00:00"'},
        )
        assert stale.status_code == 412
        assert stale.json()["detail"]["code"] == "precondition_failed"

        ok = client.patch(
            f"/api/v1/ipam/ipv4-prefixes/{pid}",
            json={"name": "lan-ok"},
            headers={"If-Match": etag},
        )
        assert ok.status_code == 200, ok.text
        assert ok.json()["name"] == "lan-ok"
        assert ok.json()["etag"] != etag


def test_release_keeps_row_delete_requires_force() -> None:
    app = create_app()
    with TestClient(app) as client:
        _, pid = _site_prefix(client, "rel-del", "10.91.0.0/29")
        req = client.post("/api/v1/ipam/ipv4-addresses/request", json={"ipv4_prefix_id": pid, "mode": "reserve"})
        assert req.status_code == 200
        aid = req.json()["id"]
        etag = req.json()["etag"]

        denied = client.delete(f"/api/v1/ipam/ipv4-addresses/{aid}")
        assert denied.status_code == 409
        assert denied.json()["detail"]["code"] == "address_must_release"

        rel = client.post(f"/api/v1/ipam/ipv4-addresses/{aid}/release", headers={"If-Match": etag})
        assert rel.status_code == 200, rel.text
        assert rel.json()["status"] == "discovered"
        still = client.get(f"/api/v1/ipam/ipv4-addresses/{aid}")
        assert still.status_code == 200

        gone = client.delete(f"/api/v1/ipam/ipv4-addresses/{aid}")
        assert gone.status_code == 204
        assert client.get(f"/api/v1/ipam/ipv4-addresses/{aid}").status_code == 404


def test_address_list_reports_total_when_truncated() -> None:
    app = create_app()
    with TestClient(app) as client:
        _, pid = _site_prefix(client, "list-tot", "10.92.0.0/28")
        for _ in range(3):
            r = client.post("/api/v1/ipam/ipv4-addresses/request", json={"ipv4_prefix_id": pid, "mode": "reserve"})
            assert r.status_code == 200
        page = client.get("/api/v1/ipam/ipv4-addresses", params={"ipv4_prefix_id": pid, "limit": 1})
        assert page.status_code == 200
        assert len(page.json()) == 1
        assert page.headers["x-total-count"] == "3"
        assert page.headers["x-truncated"] == "true"

        rest = client.get("/api/v1/ipam/ipv4-addresses", params={"ipv4_prefix_id": pid, "limit": 1, "offset": 1})
        assert rest.headers["x-offset"] == "1"
        assert rest.headers["x-total-count"] == "3"


def test_ipv6_release_and_list_headers() -> None:
    app = create_app()
    with TestClient(app) as client:
        sid = client.post("/api/v1/dcim/sites", json={"name": "v6c", "slug": "v6c"}).json()["id"]
        pfx = client.post(
            "/api/v1/ipam/ipv6-prefixes",
            json={"site_id": sid, "name": "ula", "cidr": "fd92::/64", "role": "active"},
        )
        assert pfx.status_code == 200, pfx.text
        pid = pfx.json()["id"]
        req = client.post("/api/v1/ipam/ipv6-addresses/request", json={"ipv6_prefix_id": pid, "mode": "reserve"})
        assert req.status_code == 200, req.text
        aid = req.json()["id"]
        blocked = client.delete(f"/api/v1/ipam/ipv6-addresses/{aid}")
        assert blocked.status_code == 409
        rel = client.post(f"/api/v1/ipam/ipv6-addresses/{aid}/release")
        assert rel.status_code == 200
        assert rel.json()["status"] == "discovered"
        listing = client.get("/api/v1/ipam/ipv6-addresses", params={"ipv6_prefix_id": pid})
        assert listing.headers["x-total-count"] == "1"
        assert listing.headers["x-truncated"] == "false"
