"""Trinn 4c: cluster-inventar og katalog-kind uten OS/hypervisor-install."""

from fastapi.testclient import TestClient

from app.main import create_app


def test_cluster_crud_and_unique_member() -> None:
    app = create_app()
    with TestClient(app) as client:
        a = client.post("/api/v1/dcim/devices", json={"name": "srv-4c-a", "serial_number": "4C-A"}).json()
        b = client.post("/api/v1/dcim/devices", json={"name": "srv-4c-b", "serial_number": "4C-B"}).json()
        cl = client.post(
            "/api/v1/clusters",
            json={"name": "px-lab", "slug": "px-lab-4c", "kind": "proxmox"},
        )
        assert cl.status_code == 200, cl.text
        assert cl.json()["kind"] == "proxmox"
        assert cl.json()["members"] == []
        m1 = client.post(f"/api/v1/clusters/{cl.json()['id']}/members", json={"device_id": a["id"]})
        assert m1.status_code == 200, m1.text
        dup = client.post(f"/api/v1/clusters/{cl.json()['id']}/members", json={"device_id": a["id"]})
        assert dup.status_code == 409
        m2 = client.post(f"/api/v1/clusters/{cl.json()['id']}/members", json={"device_id": b["id"], "role": "control"})
        assert m2.status_code == 200, m2.text
        got = client.get(f"/api/v1/clusters/{cl.json()['id']}")
        assert len(got.json()["members"]) == 2
        bad = client.post("/api/v1/clusters", json={"name": "x", "slug": "bad-kind-4c", "kind": "esxi"})
        assert bad.status_code == 422


def test_catalog_cluster_plan_and_run_records_membership() -> None:
    app = create_app()
    with TestClient(app) as client:
        d1 = client.post("/api/v1/dcim/devices", json={"name": "srv-4c-c1"}).json()
        d2 = client.post("/api/v1/dcim/devices", json={"name": "srv-4c-c2"}).json()
        tmpl = client.post(
            "/api/v1/service-catalog/templates",
            json={
                "name": "cluster record",
                "slug": "svc-4c-cluster",
                "spec": {"kind": "cluster", "reserve_ipv4": False},
            },
        )
        assert tmpl.status_code == 200, tmpl.text
        ver = tmpl.json()["versions"][0]
        missing = client.post(
            "/api/v1/service-catalog/deployments",
            json={"template_version_id": ver["id"], "device_ids": [d1["id"], d2["id"]], "cluster_kind": "talos"},
        )
        assert missing.status_code == 200, missing.text
        assert missing.json()["plan_json"]["can_run"] is False
        assert "cluster_name_required" in missing.json()["plan_json"]["blockers"]

        plan = client.post(
            "/api/v1/service-catalog/deployments",
            json={
                "template_version_id": ver["id"],
                "device_ids": [d1["id"], d2["id"]],
                "name": "talos-4c",
                "cluster_kind": "talos",
            },
        )
        assert plan.status_code == 200, plan.text
        body = plan.json()
        assert body["plan_json"]["can_run"] is True
        assert body["plan_json"]["kind"] == "cluster"
        assert "Installerer ikke OS" in " ".join(body["plan_json"]["notes"])
        assert {d["id"] for d in body["plan_json"]["devices"]} == {d1["id"], d2["id"]}

        run = client.post(f"/api/v1/service-catalog/deployments/{body['id']}/run")
        assert run.status_code == 200, run.text
        out = run.json()
        assert out["status"] == "succeeded"
        assert out["cluster_id"] is not None
        assert out["instance"]["cluster_id"] == out["cluster_id"]
        steps = {s["name"]: s["status"] for s in out["steps"]}
        assert steps["validate_devices"] == "ok"
        assert steps["record_cluster"] == "ok"
        assert steps["record_instance"] == "ok"
        assert "install_os" not in steps

        cl = client.get(f"/api/v1/clusters/{out['cluster_id']}").json()
        assert cl["kind"] == "talos"
        assert {m["device_id"] for m in cl["members"]} == {d1["id"], d2["id"]}
