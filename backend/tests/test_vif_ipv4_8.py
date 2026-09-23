"""Trinn 8: IPv4 på virtuelt grensesnitt uten oppfunnet MAC."""

from fastapi.testclient import TestClient

from app.main import create_app


def test_assign_ipv4_to_vif_without_mac() -> None:
    app = create_app()
    with TestClient(app) as client:
        site = client.post("/api/v1/dcim/sites", json={"name": "VIF 8", "slug": "site-8-vif"}).json()
        cl = client.post(
            "/api/v1/clusters",
            json={"name": "px-8", "slug": "px-8-vif", "kind": "proxmox", "site_id": site["id"]},
        ).json()
        vm = client.post(
            f"/api/v1/clusters/{cl['id']}/vms",
            json={"name": "web-8", "slug": "vm-8-web", "status": "active"},
        ).json()
        iface = client.post(
            f"/api/v1/clusters/{cl['id']}/vms/{vm['id']}/interfaces",
            json={"name": "eth0", "slug": "vif-8-eth0", "status": "active"},
        )
        assert iface.status_code == 200, iface.text
        assert iface.json()["ipv4_addresses"] == []
        assert "mac" not in iface.json()

        pfx = client.post(
            "/api/v1/ipam/ipv4-prefixes",
            json={"site_id": site["id"], "name": "vif-8", "cidr": "10.219.80.0/29"},
        )
        assert pfx.status_code == 200, pfx.text
        assigned = client.post(
            f"/api/v1/clusters/{cl['id']}/vms/{vm['id']}/interfaces/{iface.json()['id']}/ipv4",
            json={"ipv4_prefix_id": pfx.json()["id"]},
        )
        assert assigned.status_code == 200, assigned.text
        body = assigned.json()
        assert body["address"].startswith("10.219.80.")
        assert body["virtual_interface_id"] == iface.json()["id"]
        assert body["mac_address"] is None

        listed = client.get(f"/api/v1/clusters/{cl['id']}").json()
        ips = listed["vms"][0]["interfaces"][0]["ipv4_addresses"]
        assert any(a["address"] == body["address"] for a in ips)


def test_catalog_vif_reserves_ipv4_when_asked() -> None:
    app = create_app()
    with TestClient(app) as client:
        site = client.post("/api/v1/dcim/sites", json={"name": "Cat 8", "slug": "site-8-cat-vif"}).json()
        cl = client.post(
            "/api/v1/clusters",
            json={"name": "talos-8", "slug": "talos-8-vif", "kind": "talos", "site_id": site["id"]},
        ).json()
        vm = client.post(
            f"/api/v1/clusters/{cl['id']}/vms",
            json={"name": "api-8", "slug": "vm-8-api", "status": "active"},
        ).json()
        pfx = client.post(
            "/api/v1/ipam/ipv4-prefixes",
            json={"site_id": site["id"], "name": "cat-8-vif", "cidr": "10.219.81.0/29"},
        ).json()
        tmpl = client.post(
            "/api/v1/service-catalog/templates",
            json={
                "name": "vif ip",
                "slug": "svc-8-vif",
                "spec": {"kind": "virtual_interface", "reserve_ipv4": True},
            },
        )
        assert tmpl.status_code == 200, tmpl.text
        ver = tmpl.json()["versions"][0]
        missing = client.post(
            "/api/v1/service-catalog/deployments",
            json={"template_version_id": ver["id"], "vm_id": vm["id"], "name": "nic-8-need-pfx"},
        )
        assert "prefix_required" in missing.json()["plan_json"]["blockers"]

        plan = client.post(
            "/api/v1/service-catalog/deployments",
            json={
                "template_version_id": ver["id"],
                "vm_id": vm["id"],
                "name": "nic-8-ip",
                "ipv4_prefix_id": pfx["id"],
            },
        )
        assert plan.status_code == 200, plan.text
        assert plan.json()["plan_json"]["can_run"] is True
        assert "finner ikke opp MAC" in " ".join(plan.json()["plan_json"]["notes"])

        run = client.post(f"/api/v1/service-catalog/deployments/{plan.json()['id']}/run")
        assert run.status_code == 200, run.text
        out = run.json()
        assert out["status"] == "succeeded"
        assert out["instance"]["ipv4_address_id"] is not None
        steps = {s["name"]: s["status"] for s in out["steps"]}
        assert steps["record_vif"] == "ok"
        assert steps["reserve_ipv4"] == "ok"
        assert "create_nic" not in steps
        ifaces = client.get(f"/api/v1/clusters/{cl['id']}").json()["vms"][0]["interfaces"]
        nic = next(i for i in ifaces if i["name"] == "nic-8-ip")
        assert nic["ipv4_addresses"]
        assert "mac" not in nic
