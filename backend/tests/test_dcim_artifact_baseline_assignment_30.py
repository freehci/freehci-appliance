"""Trinn 30: baseline på enhet uten flashing, samsvar eller kopierte medlemmer."""

from fastapi.testclient import TestClient

from app.main import create_app


def test_baseline_assignment_does_not_flash_or_copy_members() -> None:
    app = create_app()
    with TestClient(app) as client:
        site = client.post("/api/v1/dcim/sites", json={"name": "Bl 30", "slug": "site-30-bl"}).json()
        dev = client.post("/api/v1/dcim/devices", json={"name": "srv-30-a", "site_id": site["id"]}).json()
        fw = client.post(
            "/api/v1/dcim/device-artifacts",
            json={"name": "iDRAC 30", "slug": "art-30-fw", "kind": "firmware", "version": "2.90"},
        ).json()
        bl = client.post(
            "/api/v1/dcim/device-artifact-baselines",
            json={"name": "R640 firmware 30", "slug": "bl-30-fw", "kind": "firmware"},
        ).json()
        bound = client.post(
            f"/api/v1/dcim/device-artifact-baselines/{bl['id']}/members",
            json={"artifact_id": fw["id"]},
        )
        assert bound.status_code == 200, bound.text
        bad_intent = client.post(
            f"/api/v1/dcim/devices/{dev['id']}/artifact-baselines",
            json={"baseline_id": bl["id"], "intent": "applied"},
        )
        assert bad_intent.status_code == 422
        created = client.post(
            f"/api/v1/dcim/devices/{dev['id']}/artifact-baselines",
            json={
                "baseline_id": bl["id"],
                "intent": "intended",
                "flash": True,
                "applied": True,
                "compliance_pct": 100,
            },
        )
        assert created.status_code == 200, created.text
        body = created.json()
        assert body["baseline_slug"] == "bl-30-fw"
        assert body["baseline_kind"] == "firmware"
        assert body["intent"] == "intended"
        assert "compliance_pct" not in body
        assert "flash" not in body
        assert "applied" not in body
        records = client.get(f"/api/v1/dcim/devices/{dev['id']}/artifacts").json()
        assert records == []
        dup = client.post(
            f"/api/v1/dcim/devices/{dev['id']}/artifact-baselines",
            json={"baseline_id": bl["id"], "intent": "recorded"},
        )
        assert dup.status_code == 409
        assert dup.json()["detail"] == "artifact_baseline_assignment_taken"
        listed = client.get(f"/api/v1/dcim/devices/{dev['id']}/artifact-baselines").json()
        assert [r["baseline_slug"] for r in listed] == ["bl-30-fw"]
        assert client.delete(f"/api/v1/dcim/devices/{dev['id']}/artifact-baselines/{body['id']}").status_code == 204
        leftover = client.get(f"/api/v1/dcim/devices/{dev['id']}/artifact-baselines").json()
        assert leftover == []
        still = client.get("/api/v1/dcim/device-artifact-baselines").json()
        assert any(b["slug"] == "bl-30-fw" for b in still)


def test_federation_exports_baseline_assignment_without_applying() -> None:
    from app.core.db import SessionLocal
    from app.services import federation as fed_svc

    app = create_app()
    with TestClient(app) as client:
        tenant = client.post("/api/v1/tenants", json={"name": "Bl 30 Fed", "slug": "bl-30-fed"}).json()
        site = client.post(
            "/api/v1/dcim/sites",
            json={"name": "bl-30-fed-oslo", "slug": "bl-30-fed-oslo", "tenant_id": tenant["id"]},
        ).json()
        dev = client.post(
            "/api/v1/dcim/devices",
            json={"name": "srv-30-fed", "site_id": site["id"]},
        ).json()
        fw = client.post(
            "/api/v1/dcim/device-artifacts",
            json={"name": "iDRAC 30 fed", "slug": "art-30-fed-fw", "kind": "firmware", "version": "2.90"},
        ).json()
        bl = client.post(
            "/api/v1/dcim/device-artifact-baselines",
            json={"name": "R640 firmware 30 fed", "slug": "bl-30-fed-fw", "kind": "firmware"},
        ).json()
        client.post(f"/api/v1/dcim/device-artifact-baselines/{bl['id']}/members", json={"artifact_id": fw["id"]})
        assigned = client.post(
            f"/api/v1/dcim/devices/{dev['id']}/artifact-baselines",
            json={"baseline_id": bl["id"], "intent": "intended"},
        )
        assert assigned.status_code == 200, assigned.text
        snap = client.get("/api/v1/federation/tenants/bl-30-fed/snapshot")
        assert snap.status_code == 200, snap.text
        doc = snap.json()["document"]
        assert isinstance(doc["device_artifact_baseline_assignments"], list)
        match = next(a for a in doc["device_artifact_baseline_assignments"] if a["baseline_slug"] == "bl-30-fed-fw")
        assert match["device_name"] == "srv-30-fed"
        assert match["site_slug"] == "bl-30-fed-oslo"
        assert match["intent"] == "intended"
        assert "compliance_pct" not in match
        assert "flash" not in match
        db = SessionLocal()
        try:
            checksum = fed_svc.apply_document_locally(db, doc)
            assert checksum == snap.json()["checksum"]
        finally:
            db.close()
        client.post("/api/v1/tenants", json={"name": "Rep 30", "slug": "rep-30-bl"})
        replica = {
            "apiVersion": "freehci.inventory/v1",
            "kind": "TenantInventory",
            "tenant": {"slug": "rep-30-bl", "name": "Rep 30", "description": None},
            "sites": [{"slug": "site-30-rep", "name": "Rep site", "description": None}],
            "rooms": [],
            "racks": [],
            "manufacturers": [],
            "device_types": [],
            "device_models": [],
            "device_roles": [],
            "devices": [{"name": "srv-30-rep", "site_slug": "site-30-rep"}],
            "device_artifacts": [
                {
                    "slug": "art-30-rep-fw",
                    "name": "iDRAC 30 rep",
                    "kind": "firmware",
                    "version": "2.90",
                    "description": None,
                }
            ],
            "device_artifact_baselines": [
                {
                    "slug": "bl-30-rep-fw",
                    "name": "R640 firmware 30 rep",
                    "kind": "firmware",
                    "description": None,
                    "artifact_slugs": ["art-30-rep-fw"],
                }
            ],
            "device_artifact_records": [],
            "device_artifact_baseline_assignments": [
                {
                    "device_name": "srv-30-rep",
                    "site_slug": "site-30-rep",
                    "baseline_slug": "bl-30-rep-fw",
                    "intent": "intended",
                    "flash": True,
                    "compliance_pct": 44,
                    "members": [{"artifact_slug": "art-30-rep-fw"}],
                }
            ],
            "placements": [],
            "ipam": [],
            "clusters": [],
            "catalog_templates": [],
            "catalog_instances": [],
        }
        db = SessionLocal()
        try:
            fed_svc.apply_document_locally(db, replica)
        finally:
            db.close()
        replica_site = next(s for s in client.get("/api/v1/dcim/sites").json() if s["slug"] == "site-30-rep")
        replica_dev = next(
            d for d in client.get("/api/v1/dcim/devices").json() if d["name"] == "srv-30-rep" and d["site_id"] == replica_site["id"]
        )
        copied = client.get(f"/api/v1/dcim/devices/{replica_dev['id']}/artifact-baselines").json()
        rep = next(a for a in copied if a["baseline_slug"] == "bl-30-rep-fw")
        assert rep["intent"] == "intended"
        assert "compliance_pct" not in rep
        records = client.get(f"/api/v1/dcim/devices/{replica_dev['id']}/artifacts").json()
        assert records == []
