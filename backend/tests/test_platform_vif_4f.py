"""Trinn 4f: virtuelt grensesnitt på VM uten oppfunnet MAC."""

from fastapi.testclient import TestClient

from app.main import create_app


def test_vif_crud_rejects_invented_mac() -> None:
    app = create_app()
    with TestClient(app) as client:
        cl = client.post(
            "/api/v1/clusters",
            json={"name": "px-4f", "slug": "px-4f-vif", "kind": "proxmox"},
        ).json()
        vm = client.post(
            f"/api/v1/clusters/{cl['id']}/vms",
            json={"name": "web-4f", "slug": "vm-4f-web", "status": "active"},
        ).json()
        bad = client.post(
            f"/api/v1/clusters/{cl['id']}/vms/{vm['id']}/interfaces",
            json={"name": "eth0", "slug": "vif-4f-bad", "status": "up-mystery"},
        )
        assert bad.status_code == 422
        ok = client.post(
            f"/api/v1/clusters/{cl['id']}/vms/{vm['id']}/interfaces",
            json={"name": "eth0", "slug": "vif-4f-eth0", "status": "active"},
        )
        assert ok.status_code == 200, ok.text
        body = ok.json()
        assert body["name"] == "eth0"
        assert "mac" not in body
        assert "mac_address" not in body
        got = client.get(f"/api/v1/clusters/{cl['id']}").json()
        ifaces = got["vms"][0]["interfaces"]
        assert len(ifaces) == 1
        assert ifaces[0]["name"] == "eth0"


def test_catalog_vif_plan_and_run() -> None:
    app = create_app()
    with TestClient(app) as client:
        cl = client.post(
            "/api/v1/clusters",
            json={"name": "talos-4f", "slug": "talos-4f-vif", "kind": "talos"},
        ).json()
        vm = client.post(
            f"/api/v1/clusters/{cl['id']}/vms",
            json={"name": "api-4f", "slug": "vm-4f-api", "status": "active"},
        ).json()
        tmpl = client.post(
            "/api/v1/service-catalog/templates",
            json={"name": "vif record", "slug": "svc-4f-vif", "spec": {"kind": "virtual_interface"}},
        )
        assert tmpl.status_code == 200, tmpl.text
        ver = tmpl.json()["versions"][0]
        missing = client.post(
            "/api/v1/service-catalog/deployments",
            json={"template_version_id": ver["id"], "vm_id": vm["id"]},
        )
        assert "vif_name_required" in missing.json()["plan_json"]["blockers"]

        plan = client.post(
            "/api/v1/service-catalog/deployments",
            json={
                "template_version_id": ver["id"],
                "vm_id": vm["id"],
                "name": "nic-4f",
            },
        )
        assert plan.status_code == 200, plan.text
        assert plan.json()["plan_json"]["can_run"] is True
        assert "finner ikke opp MAC" in " ".join(plan.json()["plan_json"]["notes"])

        run = client.post(f"/api/v1/service-catalog/deployments/{plan.json()['id']}/run")
        assert run.status_code == 200, run.text
        out = run.json()
        assert out["status"] == "succeeded"
        assert out["virtual_interface_id"] is not None
        assert out["instance"]["virtual_interface_id"] == out["virtual_interface_id"]
        steps = {s["name"]: s["status"] for s in out["steps"]}
        assert steps["record_vif"] == "ok"
        assert "create_nic" not in steps
        ifaces = client.get(f"/api/v1/clusters/{cl['id']}").json()["vms"][0]["interfaces"]
        assert any(i["name"] == "nic-4f" for i in ifaces)
