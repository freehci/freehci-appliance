"""Trinn 4g: disk/volum på VM uten oppfunnet kapasitet."""

from fastapi.testclient import TestClient

from app.main import create_app


def test_disk_crud_rejects_invented_kind_and_foreign_pool() -> None:
    app = create_app()
    with TestClient(app) as client:
        cl = client.post(
            "/api/v1/clusters",
            json={"name": "px-4g", "slug": "px-4g-dsk", "kind": "proxmox"},
        ).json()
        other = client.post(
            "/api/v1/clusters",
            json={"name": "other-4g", "slug": "other-4g-dsk", "kind": "other"},
        ).json()
        vm = client.post(
            f"/api/v1/clusters/{cl['id']}/vms",
            json={"name": "web-4g", "slug": "vm-4g-web", "status": "active"},
        ).json()
        pool = client.post(
            f"/api/v1/clusters/{cl['id']}/storage-pools",
            json={"name": "local", "slug": "pool-4g-local", "kind": "datastore", "status": "active"},
        ).json()
        foreign = client.post(
            f"/api/v1/clusters/{other['id']}/storage-pools",
            json={"name": "away", "slug": "pool-4g-away", "kind": "pool", "status": "active"},
        ).json()
        bad_kind = client.post(
            f"/api/v1/clusters/{cl['id']}/vms/{vm['id']}/disks",
            json={"name": "root", "slug": "dsk-4g-bad", "kind": "nvme-mystery"},
        )
        assert bad_kind.status_code == 422
        bad_pool = client.post(
            f"/api/v1/clusters/{cl['id']}/vms/{vm['id']}/disks",
            json={"name": "root", "slug": "dsk-4g-foreign", "kind": "disk", "storage_pool_id": foreign["id"]},
        )
        assert bad_pool.status_code == 400
        ok = client.post(
            f"/api/v1/clusters/{cl['id']}/vms/{vm['id']}/disks",
            json={
                "name": "root",
                "slug": "dsk-4g-root",
                "kind": "disk",
                "status": "active",
                "storage_pool_id": pool["id"],
            },
        )
        assert ok.status_code == 200, ok.text
        body = ok.json()
        assert body["kind"] == "disk"
        assert body["storage_pool_id"] == pool["id"]
        assert "bytes" not in body
        assert "capacity" not in body
        got = client.get(f"/api/v1/clusters/{cl['id']}").json()
        disks = got["vms"][0]["disks"]
        assert len(disks) == 1
        assert disks[0]["name"] == "root"


def test_catalog_disk_plan_and_run() -> None:
    app = create_app()
    with TestClient(app) as client:
        cl = client.post(
            "/api/v1/clusters",
            json={"name": "talos-4g", "slug": "talos-4g-dsk", "kind": "talos"},
        ).json()
        vm = client.post(
            f"/api/v1/clusters/{cl['id']}/vms",
            json={"name": "api-4g", "slug": "vm-4g-api", "status": "active"},
        ).json()
        tmpl = client.post(
            "/api/v1/service-catalog/templates",
            json={"name": "disk record", "slug": "svc-4g-dsk", "spec": {"kind": "virtual_disk"}},
        )
        assert tmpl.status_code == 200, tmpl.text
        ver = tmpl.json()["versions"][0]
        missing = client.post(
            "/api/v1/service-catalog/deployments",
            json={"template_version_id": ver["id"], "vm_id": vm["id"]},
        )
        assert "disk_name_required" in missing.json()["plan_json"]["blockers"]

        plan = client.post(
            "/api/v1/service-catalog/deployments",
            json={
                "template_version_id": ver["id"],
                "vm_id": vm["id"],
                "name": "vol-4g",
                "disk_kind": "volume",
            },
        )
        assert plan.status_code == 200, plan.text
        assert plan.json()["plan_json"]["can_run"] is True
        assert "oppretter ikke LUN" in " ".join(plan.json()["plan_json"]["notes"])

        run = client.post(f"/api/v1/service-catalog/deployments/{plan.json()['id']}/run")
        assert run.status_code == 200, run.text
        out = run.json()
        assert out["status"] == "succeeded"
        assert out["virtual_disk_id"] is not None
        assert out["instance"]["virtual_disk_id"] == out["virtual_disk_id"]
        steps = {s["name"]: s["status"] for s in out["steps"]}
        assert steps["record_disk"] == "ok"
        assert "provision_lun" not in steps
        disks = client.get(f"/api/v1/clusters/{cl['id']}").json()["vms"][0]["disks"]
        assert any(d["name"] == "vol-4g" and d["kind"] == "volume" for d in disks)
