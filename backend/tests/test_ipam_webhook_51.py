"""Trinn 51: webhook-HMAC er secret:-referanse, aldri nøkkelmateriale eller URL-gjetning."""

from fastapi.testclient import TestClient

from app.main import create_app


def test_raw_secret_and_matching_url_do_not_invent_hmac() -> None:
    app = create_app()
    with TestClient(app) as client:
        raw = client.post(
            "/api/v1/ipam/webhooks",
            json={"url": "http://127.0.0.1:1/hook-raw", "secret": "supersecrethmac"},
        )
        assert raw.status_code == 422, raw.text
        material = client.post(
            "/api/v1/ipam/webhooks",
            json={"url": "http://127.0.0.1:1/hook-mat", "secret_ref": "supersecrethmac"},
        )
        assert material.status_code == 422, material.text
        inferred = client.post(
            "/api/v1/ipam/webhooks",
            json={
                "url": "http://127.0.0.1:1/hook-infer",
                "infer_from_url": True,
                "match_host": "127.0.0.1",
            },
        )
        assert inferred.status_code == 422, inferred.text
        bare = client.post(
            "/api/v1/ipam/webhooks",
            json={"url": "http://127.0.0.1:1/hook-bare", "events": ["prefix.created"]},
        )
        assert bare.status_code == 200, bare.text
        assert bare.json()["secret_ref"] is None
        ok = client.post(
            "/api/v1/ipam/webhooks",
            json={
                "url": "http://127.0.0.1:1/hook-ref",
                "secret_ref": "secret:hooks/51/hmac",
                "events": ["prefix.created"],
            },
        )
        assert ok.status_code == 200, ok.text
        assert ok.json()["secret_ref"] == "secret:hooks/51/hmac"
        listed = client.get("/api/v1/ipam/webhooks").json()
        match = next(r for r in listed if r["url"].endswith("/hook-ref"))
        assert match["secret_ref"] == "secret:hooks/51/hmac"
        sid = client.post("/api/v1/dcim/sites", json={"name": "WH 51", "slug": "site-51-wh"}).json()["id"]
        pfx = client.post(
            "/api/v1/ipam/ipv4-prefixes",
            json={"site_id": sid, "name": "lan", "cidr": "10.51.0.0/24", "slug": "px-51-wh"},
        )
        assert pfx.status_code == 200, pfx.text
        deliveries = client.get(f"/api/v1/ipam/webhooks/{ok.json()['id']}/deliveries")
        assert deliveries.status_code == 200, deliveries.text
        rows = deliveries.json()
        assert rows
        assert rows[0]["event"] == "prefix.created"
        assert client.delete(f"/api/v1/ipam/webhooks/{bare.json()['id']}").status_code == 204
        assert client.delete(f"/api/v1/ipam/webhooks/{ok.json()['id']}").status_code == 204
