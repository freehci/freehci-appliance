"""Trinn 26: firmware-baseline og BIOS-profil uten flashing eller samsvarsprosent."""

from fastapi.testclient import TestClient

from app.main import create_app


def test_artifact_baseline_does_not_flash_or_score_or_mix_kinds() -> None:
    app = create_app()
    with TestClient(app) as client:
        fw = client.post(
            "/api/v1/dcim/device-artifacts",
            json={"name": "iDRAC 26", "slug": "art-26-fw", "kind": "firmware", "version": "2.81"},
        )
        assert fw.status_code == 200, fw.text
        bios = client.post(
            "/api/v1/dcim/device-artifacts",
            json={"name": "BIOS 26", "slug": "art-26-bios", "kind": "bios", "version": "1.4.0"},
        )
        assert bios.status_code == 200, bios.text
        bad_kind = client.post(
            "/api/v1/dcim/device-artifact-baselines",
            json={"name": "Mixed", "slug": "bl-26-mixed", "kind": "os-image"},
        )
        assert bad_kind.status_code == 422
        created = client.post(
            "/api/v1/dcim/device-artifact-baselines",
            json={
                "name": "R640 firmware",
                "slug": "bl-26-fw",
                "kind": "firmware",
                "flash": True,
                "compliance_pct": 100,
                "applied": True,
            },
        )
        assert created.status_code == 200, created.text
        body = created.json()
        assert body["slug"] == "bl-26-fw"
        assert body["kind"] == "firmware"
        assert body["members"] == []
        assert "compliance_pct" not in body
        assert "applied" not in body
        assert "flash" not in body
        dup = client.post(
            "/api/v1/dcim/device-artifact-baselines",
            json={"name": "R640 firmware", "slug": "bl-26-fw", "kind": "firmware"},
        )
        assert dup.status_code == 409
        listed = client.get("/api/v1/dcim/device-artifact-baselines").json()
        assert any(b["slug"] == "bl-26-fw" and b["members"] == [] for b in listed)
        mixed = client.post(
            f"/api/v1/dcim/device-artifact-baselines/{body['id']}/members",
            json={"artifact_id": bios.json()["id"]},
        )
        assert mixed.status_code == 400
        assert mixed.json()["detail"] == "artifact_baseline_kind"
        bound = client.post(
            f"/api/v1/dcim/device-artifact-baselines/{body['id']}/members",
            json={"artifact_id": fw.json()["id"], "flash": True, "compliance_pct": 12},
        )
        assert bound.status_code == 200, bound.text
        members = bound.json()["members"]
        assert [m["artifact_slug"] for m in members] == ["art-26-fw"]
        assert members[0]["artifact_kind"] == "firmware"
        assert "compliance_pct" not in bound.json()
        again = client.post(
            f"/api/v1/dcim/device-artifact-baselines/{body['id']}/members",
            json={"artifact_id": fw.json()["id"]},
        )
        assert again.status_code == 409
        assert again.json()["detail"] == "artifact_baseline_member_taken"
        bios_bl = client.post(
            "/api/v1/dcim/device-artifact-baselines",
            json={"name": "R640 BIOS", "slug": "bl-26-bios", "kind": "bios"},
        )
        assert bios_bl.status_code == 200, bios_bl.text
        bios_mem = client.post(
            f"/api/v1/dcim/device-artifact-baselines/{bios_bl.json()['id']}/members",
            json={"artifact_id": bios.json()["id"]},
        )
        assert bios_mem.status_code == 200, bios_mem.text
        assert [m["artifact_slug"] for m in bios_mem.json()["members"]] == ["art-26-bios"]
        mid = bound.json()["members"][0]["id"]
        assert client.delete(f"/api/v1/dcim/device-artifact-baseline-members/{mid}").status_code == 204
        after = client.get(f"/api/v1/dcim/device-artifact-baselines/{body['id']}").json()
        assert after["members"] == []
        assert client.delete(f"/api/v1/dcim/device-artifact-baselines/{body['id']}").status_code == 204
        remaining = client.get("/api/v1/dcim/device-artifact-baselines").json()
        assert all(b["slug"] != "bl-26-fw" for b in remaining)
        arts = client.get("/api/v1/dcim/device-artifacts").json()
        assert any(a["slug"] == "art-26-fw" for a in arts)
        assert any(a["slug"] == "art-26-bios" for a in arts)


def test_delete_artifact_removes_baseline_member_not_baseline() -> None:
    app = create_app()
    with TestClient(app) as client:
        fw = client.post(
            "/api/v1/dcim/device-artifacts",
            json={"name": "iDRAC 26b", "slug": "art-26-fw-del", "kind": "firmware", "version": "3.00"},
        ).json()
        bl = client.post(
            "/api/v1/dcim/device-artifact-baselines",
            json={"name": "Temp fw", "slug": "bl-26-fw-del", "kind": "firmware"},
        ).json()
        client.post(
            f"/api/v1/dcim/device-artifact-baselines/{bl['id']}/members",
            json={"artifact_id": fw["id"]},
        )
        assert client.delete(f"/api/v1/dcim/device-artifacts/{fw['id']}").status_code == 204
        after = client.get(f"/api/v1/dcim/device-artifact-baselines/{bl['id']}").json()
        assert after["slug"] == "bl-26-fw-del"
        assert after["members"] == []


def test_federation_exports_artifact_baseline_by_slug() -> None:
    from app.core.db import SessionLocal
    from app.services import federation as fed_svc

    app = create_app()
    with TestClient(app) as client:
        tenant = client.post("/api/v1/tenants", json={"name": "Bl Fed", "slug": "bl-26-fed"}).json()
        client.post(
            "/api/v1/dcim/sites",
            json={"name": "bl-26-fed-oslo", "slug": "bl-26-fed-oslo", "tenant_id": tenant["id"]},
        )
        fw = client.post(
            "/api/v1/dcim/device-artifacts",
            json={"name": "iDRAC 26 fed", "slug": "art-26-fed-fw", "kind": "firmware", "version": "2.81"},
        )
        assert fw.status_code == 200, fw.text
        bl = client.post(
            "/api/v1/dcim/device-artifact-baselines",
            json={"name": "R640 firmware fed", "slug": "bl-26-fed-fw", "kind": "firmware"},
        )
        assert bl.status_code == 200, bl.text
        bound = client.post(
            f"/api/v1/dcim/device-artifact-baselines/{bl.json()['id']}/members",
            json={"artifact_id": fw.json()["id"]},
        )
        assert bound.status_code == 200, bound.text
        snap = client.get("/api/v1/federation/tenants/bl-26-fed/snapshot")
        assert snap.status_code == 200, snap.text
        doc = snap.json()["document"]
        assert isinstance(doc["device_artifact_baselines"], list)
        match = next(b for b in doc["device_artifact_baselines"] if b["slug"] == "bl-26-fed-fw")
        assert match["kind"] == "firmware"
        assert match["artifact_slugs"] == ["art-26-fed-fw"]
        assert "compliance_pct" not in match
        assert any(a["slug"] == "art-26-fed-fw" for a in doc["device_artifacts"])
        db = SessionLocal()
        try:
            checksum = fed_svc.apply_document_locally(db, doc)
            assert checksum == snap.json()["checksum"]
        finally:
            db.close()
        client.post("/api/v1/tenants", json={"name": "Rep 26", "slug": "rep-26-bl"})
        replica = {
            "apiVersion": "freehci.inventory/v1",
            "kind": "TenantInventory",
            "tenant": {"slug": "rep-26-bl", "name": "Rep 26", "description": None},
            "sites": [{"slug": "site-26-rep", "name": "Rep site", "description": None}],
            "rooms": [],
            "racks": [],
            "manufacturers": [],
            "device_types": [],
            "device_models": [],
            "device_roles": [],
            "devices": [],
            "device_artifacts": [
                {
                    "slug": "art-26-rep-fw",
                    "name": "iDRAC 26 rep",
                    "kind": "firmware",
                    "version": "2.81",
                    "description": None,
                }
            ],
            "device_artifact_baselines": [
                {
                    "slug": "bl-26-rep-fw",
                    "name": "R640 firmware rep",
                    "kind": "firmware",
                    "description": None,
                    "artifact_slugs": ["art-26-rep-fw"],
                    "flash": True,
                    "compliance_pct": 100,
                }
            ],
            "device_artifact_records": [],
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
        arts = client.get("/api/v1/dcim/device-artifacts").json()
        assert any(a["slug"] == "art-26-rep-fw" for a in arts)
        baselines = client.get("/api/v1/dcim/device-artifact-baselines").json()
        rep = next(b for b in baselines if b["slug"] == "bl-26-rep-fw")
        assert rep["kind"] == "firmware"
        assert [m["artifact_slug"] for m in rep["members"]] == ["art-26-rep-fw"]
        assert "compliance_pct" not in rep
        assert "flash" not in rep
