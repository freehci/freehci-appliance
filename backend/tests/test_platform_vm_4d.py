"""Trinn 4d: VM-inventar på cluster uten å late som maskinen opprettes."""

from fastapi.testclient import TestClient

from app.main import create_app


def test_vm_requires_cluster_member_for_host() -> None:
    app = create_app()
    with TestClient(app) as client:
        host = client.post("/api/v1/dcim/devices", json={"name": "srv-4d-host"}).json()
        other = client.post("/api/v1/dcim/devices", json={"name": "srv-4d-other"}).json()
        cl = client.post(
            "/api/v1/clusters",
            json={"name": "px-4d", "slug": "px-4d-vm", "kind": "proxmox"},
        ).json()
        client.post(f"/api/v1/clusters/{cl['id']}/members", json={"device_id": host["id"]})
        bad = client.post(
            f"/api/v1/clusters/{cl['id']}/vms",
            json={"name": "vm-bad", "slug": "vm-4d-bad", "device_id": other["id"]},
        )
        assert bad.status_code == 400
        ok = client.post(
            f"/api/v1/clusters/{cl['id']}/vms",
            json={"name": "web-1", "slug": "vm-4d-web", "device_id": host["id"], "status": "active"},
        )
        assert ok.status_code == 200, ok.text
        assert ok.json()["cluster_id"] == cl["id"]
        assert ok.json()["device_id"] == host["id"]
        assert "vcpus" not in ok.json()
        got = client.get(f"/api/v1/clusters/{cl['id']}").json()
        assert len(got["vms"]) == 1
        assert got["vms"][0]["name"] == "web-1"


def test_catalog_vm_plan_and_run() -> None:
    app = create_app()
    with TestClient(app) as client:
        host = client.post("/api/v1/dcim/devices", json={"name": "srv-4d-cat"}).json()
        cl = client.post(
            "/api/v1/clusters",
            json={"name": "talos-4d", "slug": "talos-4d-vm", "kind": "talos"},
        ).json()
        client.post(f"/api/v1/clusters/{cl['id']}/members", json={"device_id": host["id"]})
        tmpl = client.post(
            "/api/v1/service-catalog/templates",
            json={"name": "vm record", "slug": "svc-4d-vm", "spec": {"kind": "virtual_machine"}},
        )
        assert tmpl.status_code == 200, tmpl.text
        ver = tmpl.json()["versions"][0]
        missing = client.post(
            "/api/v1/service-catalog/deployments",
            json={"template_version_id": ver["id"], "cluster_id": cl["id"]},
        )
        assert missing.status_code == 200, missing.text
        assert "vm_name_required" in missing.json()["plan_json"]["blockers"]

        plan = client.post(
            "/api/v1/service-catalog/deployments",
            json={
                "template_version_id": ver["id"],
                "cluster_id": cl["id"],
                "device_id": host["id"],
                "name": "api-4d",
            },
        )
        assert plan.status_code == 200, plan.text
        body = plan.json()
        assert body["plan_json"]["can_run"] is True
        assert body["plan_json"]["kind"] == "virtual_machine"
        assert "Oppretter eller starter ikke" in " ".join(body["plan_json"]["notes"])

        run = client.post(f"/api/v1/service-catalog/deployments/{body['id']}/run")
        assert run.status_code == 200, run.text
        out = run.json()
        assert out["status"] == "succeeded"
        assert out["vm_id"] is not None
        assert out["instance"]["vm_id"] == out["vm_id"]
        steps = {s["name"]: s["status"] for s in out["steps"]}
        assert steps["record_vm"] == "ok"
        assert "create_guest" not in steps
        vms = client.get(f"/api/v1/clusters/{cl['id']}").json()["vms"]
        assert any(v["name"] == "api-4d" for v in vms)
