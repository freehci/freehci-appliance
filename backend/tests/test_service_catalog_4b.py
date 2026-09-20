"""Trinn 4b: ærlig katalogflyt — plan og kjøring uten OS-install."""

from fastapi.testclient import TestClient

from app.main import create_app


def _template(client: TestClient, *, slug: str, reserve: bool) -> dict:
    r = client.post(
        "/api/v1/service-catalog/templates",
        json={
            "name": slug,
            "slug": slug,
            "description": "device instance record",
            "spec": {"kind": "device_instance", "reserve_ipv4": reserve},
        },
    )
    assert r.status_code == 200, r.text
    return r.json()


def test_unknown_kind_rejected() -> None:
    app = create_app()
    with TestClient(app) as client:
        r = client.post(
            "/api/v1/service-catalog/templates",
            json={"name": "esxi", "slug": "svc-4b-bad-kind", "spec": {"kind": "os_install"}},
        )
        assert r.status_code == 422


def test_plan_and_run_without_ip_creates_instance() -> None:
    app = create_app()
    with TestClient(app) as client:
        dev = client.post("/api/v1/dcim/devices", json={"name": "srv-4b-plain"}).json()
        tmpl = _template(client, slug="svc-4b-plain", reserve=False)
        ver = tmpl["versions"][0]
        plan = client.post(
            "/api/v1/service-catalog/deployments",
            json={"template_version_id": ver["id"], "device_id": dev["id"]},
        )
        assert plan.status_code == 200, plan.text
        body = plan.json()
        assert body["status"] == "planned"
        assert body["plan_json"]["can_run"] is True
        assert body["plan_json"]["reserve_ipv4"] is False
        assert "Installerer ikke OS" in " ".join(body["plan_json"]["notes"])
        assert body["instance"] is None

        run = client.post(f"/api/v1/service-catalog/deployments/{body['id']}/run")
        assert run.status_code == 200, run.text
        out = run.json()
        assert out["status"] == "succeeded"
        assert out["finished_at"] is not None
        assert out["instance"] is not None
        assert out["instance"]["device_id"] == dev["id"]
        assert out["instance"]["ipv4_address_id"] is None
        steps = {s["name"]: s["status"] for s in out["steps"]}
        assert steps["validate_device"] == "ok"
        assert steps["reserve_ipv4"] == "skipped"
        assert steps["record_instance"] == "ok"

        again = client.post(f"/api/v1/service-catalog/deployments/{body['id']}/run")
        assert again.status_code == 409


def test_reserve_without_prefix_cannot_run() -> None:
    app = create_app()
    with TestClient(app) as client:
        dev = client.post("/api/v1/dcim/devices", json={"name": "srv-4b-nopfx"}).json()
        tmpl = _template(client, slug="svc-4b-need-pfx", reserve=True)
        ver = tmpl["versions"][0]
        plan = client.post(
            "/api/v1/service-catalog/deployments",
            json={"template_version_id": ver["id"], "device_id": dev["id"]},
        )
        assert plan.status_code == 200, plan.text
        assert plan.json()["plan_json"]["can_run"] is False
        assert "prefix_required" in plan.json()["plan_json"]["blockers"]
        run = client.post(f"/api/v1/service-catalog/deployments/{plan.json()['id']}/run")
        assert run.status_code == 400
        assert run.json()["detail"]["code"] == "cannot_run"


def test_run_reserves_real_ipv4_and_records_instance() -> None:
    app = create_app()
    with TestClient(app) as client:
        site = client.post("/api/v1/dcim/sites", json={"name": "Cat 4b", "slug": "site-4b-cat"}).json()
        dev = client.post(
            "/api/v1/dcim/devices",
            json={"name": "srv-4b-ip", "site_id": site["id"], "serial_number": "4B-CAT-IP"},
        ).json()
        pfx = client.post(
            "/api/v1/ipam/ipv4-prefixes",
            json={"site_id": site["id"], "name": "cat-4b", "cidr": "10.219.61.0/29"},
        )
        assert pfx.status_code == 200, pfx.text
        tmpl = _template(client, slug="svc-4b-ip", reserve=True)
        ver = tmpl["versions"][0]
        plan = client.post(
            "/api/v1/service-catalog/deployments",
            json={
                "template_version_id": ver["id"],
                "device_id": dev["id"],
                "ipv4_prefix_id": pfx.json()["id"],
            },
        )
        assert plan.status_code == 200, plan.text
        pj = plan.json()["plan_json"]
        assert pj["can_run"] is True
        assert pj["prefix"]["cidr"] == "10.219.61.0/29"
        assert "address" not in pj.get("prefix", {})

        run = client.post(f"/api/v1/service-catalog/deployments/{plan.json()['id']}/run")
        assert run.status_code == 200, run.text
        out = run.json()
        assert out["status"] == "succeeded"
        assert out["instance"]["ipv4_address_id"] is not None
        reserve = next(s for s in out["steps"] if s["name"] == "reserve_ipv4")
        assert reserve["status"] == "ok"
        assert reserve["detail"]
        assert reserve["detail"].startswith("10.219.61.")

        insts = client.get("/api/v1/service-catalog/instances")
        assert insts.status_code == 200
        assert any(i["id"] == out["instance"]["id"] for i in insts.json())


def test_new_version_is_immutable_record() -> None:
    app = create_app()
    with TestClient(app) as client:
        tmpl = _template(client, slug="svc-4b-ver", reserve=False)
        dup = client.post(
            f"/api/v1/service-catalog/templates/{tmpl['id']}/versions",
            json={"version": "1.0.0", "spec": {"kind": "device_instance", "reserve_ipv4": True}},
        )
        assert dup.status_code == 409
        nxt = client.post(
            f"/api/v1/service-catalog/templates/{tmpl['id']}/versions",
            json={"version": "1.1.0", "spec": {"kind": "device_instance", "reserve_ipv4": True}},
        )
        assert nxt.status_code == 200, nxt.text
        assert nxt.json()["version"] == "1.1.0"
        assert nxt.json()["spec"]["reserve_ipv4"] is True
        first = tmpl["versions"][0]
        assert first["spec"]["reserve_ipv4"] is False
