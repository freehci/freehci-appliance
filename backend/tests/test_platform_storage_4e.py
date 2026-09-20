"""Trinn 4e: lagringspool på cluster uten oppfunnet kapasitet."""

from fastapi.testclient import TestClient

from app.main import create_app


def test_storage_pool_crud_rejects_invented_kind() -> None:
    app = create_app()
    with TestClient(app) as client:
        cl = client.post(
            "/api/v1/clusters",
            json={"name": "px-4e", "slug": "px-4e-st", "kind": "proxmox"},
        ).json()
        bad = client.post(
            f"/api/v1/clusters/{cl['id']}/storage-pools",
            json={"name": "fast", "slug": "st-4e-bad", "kind": "ceph-mystery"},
        )
        assert bad.status_code == 422
        ok = client.post(
            f"/api/v1/clusters/{cl['id']}/storage-pools",
            json={"name": "local-lvm", "slug": "st-4e-lvm", "kind": "datastore", "status": "active"},
        )
        assert ok.status_code == 200, ok.text
        body = ok.json()
        assert body["kind"] == "datastore"
        assert "bytes" not in body
        assert "capacity" not in body
        got = client.get(f"/api/v1/clusters/{cl['id']}").json()
        assert len(got["storage_pools"]) == 1


def test_catalog_storage_plan_and_run() -> None:
    app = create_app()
    with TestClient(app) as client:
        cl = client.post(
            "/api/v1/clusters",
            json={"name": "talos-4e", "slug": "talos-4e-st", "kind": "talos"},
        ).json()
        tmpl = client.post(
            "/api/v1/service-catalog/templates",
            json={"name": "storage record", "slug": "svc-4e-st", "spec": {"kind": "storage_pool"}},
        )
        assert tmpl.status_code == 200, tmpl.text
        ver = tmpl.json()["versions"][0]
        missing = client.post(
            "/api/v1/service-catalog/deployments",
            json={"template_version_id": ver["id"], "cluster_id": cl["id"]},
        )
        assert "storage_name_required" in missing.json()["plan_json"]["blockers"]

        plan = client.post(
            "/api/v1/service-catalog/deployments",
            json={
                "template_version_id": ver["id"],
                "cluster_id": cl["id"],
                "name": "rook-4e",
                "storage_kind": "pool",
            },
        )
        assert plan.status_code == 200, plan.text
        assert plan.json()["plan_json"]["can_run"] is True
        assert "Måler ikke kapasitet" in " ".join(plan.json()["plan_json"]["notes"])

        run = client.post(f"/api/v1/service-catalog/deployments/{plan.json()['id']}/run")
        assert run.status_code == 200, run.text
        out = run.json()
        assert out["status"] == "succeeded"
        assert out["storage_pool_id"] is not None
        assert out["instance"]["storage_pool_id"] == out["storage_pool_id"]
        steps = {s["name"]: s["status"] for s in out["steps"]}
        assert steps["record_storage"] == "ok"
        assert "provision_lun" not in steps
        pools = client.get(f"/api/v1/clusters/{cl['id']}").json()["storage_pools"]
        assert any(p["name"] == "rook-4e" and p["kind"] == "pool" for p in pools)
