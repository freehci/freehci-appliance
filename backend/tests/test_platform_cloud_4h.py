"""Trinn 4h: skyabonnement uten oppfunnet kostnad eller kvote."""

from fastapi.testclient import TestClient

from app.main import create_app


def test_cloud_crud_rejects_invented_kind() -> None:
    app = create_app()
    with TestClient(app) as client:
        bad = client.post(
            "/api/v1/cloud-subscriptions",
            json={"name": "mystery", "slug": "cloud-4h-bad", "kind": "oracle-mystery"},
        )
        assert bad.status_code == 422
        ok = client.post(
            "/api/v1/cloud-subscriptions",
            json={"name": "lab-aws", "slug": "aws-4h-lab", "kind": "aws", "status": "active"},
        )
        assert ok.status_code == 200, ok.text
        body = ok.json()
        assert body["kind"] == "aws"
        assert "cost" not in body
        assert "quota" not in body
        listed = client.get("/api/v1/cloud-subscriptions").json()
        assert any(r["slug"] == "aws-4h-lab" for r in listed)


def test_catalog_cloud_plan_and_run() -> None:
    app = create_app()
    with TestClient(app) as client:
        tmpl = client.post(
            "/api/v1/service-catalog/templates",
            json={"name": "cloud record", "slug": "svc-4h-cloud", "spec": {"kind": "cloud_subscription"}},
        )
        assert tmpl.status_code == 200, tmpl.text
        ver = tmpl.json()["versions"][0]
        missing = client.post(
            "/api/v1/service-catalog/deployments",
            json={"template_version_id": ver["id"]},
        )
        assert "cloud_name_required" in missing.json()["plan_json"]["blockers"]

        plan = client.post(
            "/api/v1/service-catalog/deployments",
            json={
                "template_version_id": ver["id"],
                "name": "gcp-4h",
                "cloud_kind": "gcp",
            },
        )
        assert plan.status_code == 200, plan.text
        assert plan.json()["plan_json"]["can_run"] is True
        assert "finner ikke opp kostnad" in " ".join(plan.json()["plan_json"]["notes"])

        run = client.post(f"/api/v1/service-catalog/deployments/{plan.json()['id']}/run")
        assert run.status_code == 200, run.text
        out = run.json()
        assert out["status"] == "succeeded"
        assert out["cloud_subscription_id"] is not None
        assert out["instance"]["cloud_subscription_id"] == out["cloud_subscription_id"]
        steps = {s["name"]: s["status"] for s in out["steps"]}
        assert steps["record_cloud"] == "ok"
        assert "provision_cloud" not in steps
        listed = client.get("/api/v1/cloud-subscriptions").json()
        assert any(r["name"] == "gcp-4h" and r["kind"] == "gcp" for r in listed)
