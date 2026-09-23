"""Prefiks-status reserved/deprecated skal blokkere host-request med 409, ikke 500."""

from fastapi.testclient import TestClient

from app.main import create_app


def test_reserved_access_prefix_request_is_409() -> None:
    app = create_app()
    with TestClient(app) as client:
        site = client.post("/api/v1/dcim/sites", json={"name": "S-rsv", "slug": "site-rsv-alloc"}).json()
        pfx = client.post(
            "/api/v1/ipam/ipv4-prefixes",
            json={
                "site_id": site["id"],
                "name": "LAN reserved",
                "slug": "site-rsv-lan",
                "cidr": "10.219.96.0/28",
                "role": "access",
                "status": "reserved",
            },
        )
        assert pfx.status_code == 200, pfx.text
        assert pfx.json()["role"] == "access"
        assert pfx.json()["status"] == "reserved"
        pid = pfx.json()["id"]

        req = client.post(
            "/api/v1/ipam/ipv4-addresses/request",
            json={"ipv4_prefix_id": pid, "mode": "reserve"},
        )
        assert req.status_code == 409, req.text
        assert req.json()["detail"]["code"] == "prefix_status_forbids_alloc"
        assert req.json()["detail"]["status"] == "reserved"

        ens = client.post(
            "/api/v1/ipam/ipv4-addresses/ensure",
            json={"ipv4_prefix_id": pid, "address": "10.219.96.5", "mode": "reserve"},
        )
        assert ens.status_code == 409, ens.text
        assert ens.json()["detail"]["code"] == "prefix_status_forbids_alloc"

        batch = client.post(
            "/api/v1/ipam/ipv4-addresses/request-batch",
            json={"ipv4_prefix_id": pid, "mode": "reserve", "count": 2},
        )
        assert batch.status_code == 409, batch.text
        assert batch.json()["detail"]["code"] == "prefix_status_forbids_alloc"
