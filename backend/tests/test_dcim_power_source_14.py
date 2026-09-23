"""Trinn 14: strømkilde er start på kjeden, uten oppdiktet last."""

from fastapi.testclient import TestClient

from app.main import create_app


def test_power_source_rejects_invented_kind_and_links_panel() -> None:
    app = create_app()
    with TestClient(app) as client:
        site = client.post("/api/v1/dcim/sites", json={"name": "SRC 14", "slug": "site-14-src"}).json()
        other = client.post("/api/v1/dcim/sites", json={"name": "SRC 14b", "slug": "site-14-src-b"}).json()
        bad = client.post(
            "/api/v1/dcim/power-sources",
            json={"site_id": site["id"], "name": "solar", "slug": "src-14-solar", "kind": "solar"},
        )
        assert bad.status_code == 422
        grid = client.post(
            "/api/v1/dcim/power-sources",
            json={"site_id": site["id"], "name": "Nett A", "slug": "src-14-grid", "kind": "grid"},
        )
        assert grid.status_code == 200, grid.text
        body = grid.json()
        assert body["kind"] == "grid"
        assert body["slug"] == "src-14-grid"
        assert body["device_id"] is None
        assert "watts" not in body
        assert "observed" not in body
        dup = client.post(
            "/api/v1/dcim/power-sources",
            json={"site_id": site["id"], "name": "Nett B", "slug": "src-14-grid", "kind": "grid"},
        )
        assert dup.status_code == 409
        with_dev = client.post(
            "/api/v1/dcim/power-sources",
            json={
                "site_id": site["id"],
                "name": "Nett+dev",
                "slug": "src-14-grid-dev",
                "kind": "grid",
                "device_id": 1,
            },
        )
        assert with_dev.status_code == 400
        panel = client.post(
            "/api/v1/dcim/power-panels",
            json={
                "site_id": site["id"],
                "name": "Tavle 14",
                "slug": "panel-14-src",
                "source_id": body["id"],
            },
        )
        assert panel.status_code == 200, panel.text
        assert panel.json()["source_id"] == body["id"]
        cross = client.post(
            "/api/v1/dcim/power-panels",
            json={"site_id": other["id"], "name": "Fremmed", "source_id": body["id"]},
        )
        assert cross.status_code == 400
        listed = client.get(f"/api/v1/dcim/power-sources?site_id={site['id']}").json()
        assert [s["slug"] for s in listed] == ["src-14-grid"]
        assert client.delete(f"/api/v1/dcim/power-sources/{body['id']}").status_code == 204
        refreshed = client.get("/api/v1/dcim/power-panels").json()
        match = next(p for p in refreshed if p["slug"] == "panel-14-src")
        assert match["source_id"] is None


def test_ups_device_source_requires_same_site_device() -> None:
    app = create_app()
    with TestClient(app) as client:
        site = client.post("/api/v1/dcim/sites", json={"name": "SRC 14u", "slug": "site-14-ups"}).json()
        other = client.post("/api/v1/dcim/sites", json={"name": "SRC 14u2", "slug": "site-14-ups-b"}).json()
        missing = client.post(
            "/api/v1/dcim/power-sources",
            json={"site_id": site["id"], "name": "UPS", "slug": "src-14-ups", "kind": "ups-device"},
        )
        assert missing.status_code == 400
        local = client.post("/api/v1/dcim/devices", json={"name": "ups-14-local", "site_id": site["id"]}).json()
        remote = client.post("/api/v1/dcim/devices", json={"name": "ups-14-remote", "site_id": other["id"]}).json()
        mismatch = client.post(
            "/api/v1/dcim/power-sources",
            json={
                "site_id": site["id"],
                "name": "UPS remote",
                "slug": "src-14-ups-remote",
                "kind": "ups-device",
                "device_id": remote["id"],
            },
        )
        assert mismatch.status_code == 400
        ok = client.post(
            "/api/v1/dcim/power-sources",
            json={
                "site_id": site["id"],
                "name": "UPS local",
                "slug": "src-14-ups",
                "kind": "ups-device",
                "device_id": local["id"],
            },
        )
        assert ok.status_code == 200, ok.text
        assert ok.json()["device_id"] == local["id"]
        assert ok.json()["kind"] == "ups-device"


def test_federation_exports_power_source_by_slug() -> None:
    from app.core.db import SessionLocal
    from app.services import federation as fed_svc

    app = create_app()
    with TestClient(app) as client:
        tenant = client.post("/api/v1/tenants", json={"name": "Src Fed", "slug": "src-14-fed"}).json()
        site = client.post(
            "/api/v1/dcim/sites",
            json={"name": "src-14-fed-oslo", "slug": "src-14-fed-oslo", "tenant_id": tenant["id"]},
        ).json()
        src = client.post(
            "/api/v1/dcim/power-sources",
            json={"site_id": site["id"], "name": "Nett", "slug": "src-14-fed-grid", "kind": "grid"},
        )
        assert src.status_code == 200, src.text
        client.post(
            "/api/v1/dcim/power-panels",
            json={
                "site_id": site["id"],
                "name": "Tavle",
                "slug": "panel-14-fed",
                "source_id": src.json()["id"],
            },
        )
        snap = client.get("/api/v1/federation/tenants/src-14-fed/snapshot")
        assert snap.status_code == 200, snap.text
        doc = snap.json()["document"]
        assert any(s["slug"] == "src-14-fed-grid" for s in doc["power_sources"])
        doc["tenant"] = {"slug": "src-14-fed-rep", "name": "Src Fed Rep", "description": None}
        doc["sites"][0]["slug"] = "src-14-fed-rep-oslo"
        for s in doc["power_sources"]:
            s["site_slug"] = "src-14-fed-rep-oslo"
        for p in doc["power_panels"]:
            p["site_slug"] = "src-14-fed-rep-oslo"
        db = SessionLocal()
        try:
            fed_svc.apply_document_locally(db, doc)
        finally:
            db.close()
        replica = next(s for s in client.get("/api/v1/dcim/sites").json() if s["slug"] == "src-14-fed-rep-oslo")
        sources = client.get(f"/api/v1/dcim/power-sources?site_id={replica['id']}").json()
        assert any(s["slug"] == "src-14-fed-grid" for s in sources)
        panels = client.get(f"/api/v1/dcim/power-panels?site_id={replica['id']}").json()
        panel = next(p for p in panels if p["slug"] == "panel-14-fed")
        assert panel["source_id"] == next(s["id"] for s in sources if s["slug"] == "src-14-fed-grid")
