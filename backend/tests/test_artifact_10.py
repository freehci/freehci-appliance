"""Trinn 10: Artifact som registrert versjon, uten firmware-/OS-påføring."""

from fastapi.testclient import TestClient

from app.main import create_app


def test_artifact_crud_rejects_invented_kind() -> None:
    app = create_app()
    with TestClient(app) as client:
        bad = client.post(
            "/api/v1/dcim/device-artifacts",
            json={"name": "mystery", "slug": "art-10-bad", "kind": "flash-now", "version": "1"},
        )
        assert bad.status_code == 422
        ok = client.post(
            "/api/v1/dcim/device-artifacts",
            json={
                "name": "iDRAC 7",
                "slug": "art-10-idrac",
                "kind": "firmware",
                "version": "2.81.81.81",
            },
        )
        assert ok.status_code == 200, ok.text
        body = ok.json()
        assert body["kind"] == "firmware"
        assert body["version"] == "2.81.81.81"
        listed = client.get("/api/v1/dcim/device-artifacts").json()
        assert any(a["slug"] == "art-10-idrac" for a in listed)


def test_artifact_recorded_on_device_not_applied() -> None:
    app = create_app()
    with TestClient(app) as client:
        art = client.post(
            "/api/v1/dcim/device-artifacts",
            json={"name": "BIOS 10", "slug": "art-10-bios", "kind": "bios", "version": "1.4.0"},
        ).json()
        site = client.post("/api/v1/dcim/sites", json={"name": "Art 10", "slug": "site-10-art"}).json()
        dev = client.post(
            "/api/v1/dcim/devices",
            json={"name": "srv-10-art", "site_id": site["id"]},
        ).json()
        rec = client.post(
            f"/api/v1/dcim/devices/{dev['id']}/artifacts",
            json={"artifact_id": art["id"], "intent": "recorded"},
        )
        assert rec.status_code == 200, rec.text
        assert rec.json()["intent"] == "recorded"
        assert rec.json()["artifact"]["slug"] == "art-10-bios"
        dup = client.post(
            f"/api/v1/dcim/devices/{dev['id']}/artifacts",
            json={"artifact_id": art["id"], "intent": "intended"},
        )
        assert dup.status_code == 409
        listed = client.get(f"/api/v1/dcim/devices/{dev['id']}/artifacts").json()
        assert len(listed) == 1

        gone = client.delete(f"/api/v1/dcim/device-artifacts/{art['id']}")
        assert gone.status_code == 204
        after = client.get(f"/api/v1/dcim/devices/{dev['id']}/artifacts").json()
        assert after == []


def test_catalog_artifact_records_without_flash() -> None:
    app = create_app()
    with TestClient(app) as client:
        site = client.post("/api/v1/dcim/sites", json={"name": "Cat 10", "slug": "site-10-cat-art"}).json()
        dev = client.post(
            "/api/v1/dcim/devices",
            json={"name": "hv-10-art", "site_id": site["id"]},
        ).json()
        tmpl = client.post(
            "/api/v1/service-catalog/templates",
            json={
                "name": "bios record",
                "slug": "svc-10-art",
                "spec": {"kind": "artifact", "artifact_kind": "bios", "version": "3.2.1"},
            },
        )
        assert tmpl.status_code == 200, tmpl.text
        missing = client.post(
            "/api/v1/service-catalog/deployments",
            json={"template_version_id": tmpl.json()["versions"][0]["id"]},
        )
        assert missing.status_code == 200, missing.text
        assert "artifact_name_required" in missing.json()["plan_json"]["blockers"]

        plan = client.post(
            "/api/v1/service-catalog/deployments",
            json={
                "template_version_id": tmpl.json()["versions"][0]["id"],
                "name": "bios-10-rec",
                "device_id": dev["id"],
            },
        )
        assert plan.status_code == 200, plan.text
        assert plan.json()["plan_json"]["can_run"] is True
        notes = " ".join(plan.json()["plan_json"]["notes"])
        assert "Påfører ikke" in notes

        run = client.post(f"/api/v1/service-catalog/deployments/{plan.json()['id']}/run")
        assert run.status_code == 200, run.text
        out = run.json()
        assert out["status"] == "succeeded"
        assert out["instance"]["artifact_id"] is not None
        steps = {s["name"]: s["status"] for s in out["steps"]}
        assert steps["record_artifact"] == "ok"
        assert steps["record_on_device"] == "ok"
        assert "apply_firmware" not in steps
        assert "flash" not in steps
        recs = client.get(f"/api/v1/dcim/devices/{dev['id']}/artifacts").json()
        assert any(r["artifact"]["slug"] == "bios-10-rec" for r in recs)
