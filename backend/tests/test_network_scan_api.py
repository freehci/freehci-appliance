"""API-tester for nettverksskann (maler, jobber, oppdagelseskø)."""

from fastapi.testclient import TestClient

from app.main import create_app


def _ping_only_dot1(ip: str) -> bool:
    return ip.endswith(".1")


def test_network_scan_templates_and_ping_job(monkeypatch) -> None:
    monkeypatch.setattr("app.services.network_scan.ping_one_ip", _ping_only_dot1)

    app = create_app()
    with TestClient(app) as client:
        sa = client.post("/api/v1/dcim/sites", json={"name": "NsSite", "slug": "ns-site"}).json()["id"]
        p = client.post(
            "/api/v1/ipam/ipv4-prefixes",
            json={"site_id": sa, "name": "Tiny", "cidr": "10.50.0.0/30"},
        )
        assert p.status_code == 200, p.text
        pid = p.json()["id"]

        tlist = client.get("/api/v1/network-scans/templates")
        assert tlist.status_code == 200, tlist.text
        templates = tlist.json()
        ping_tpl = next(x for x in templates if x["slug"] == "builtin-ping")
        tid = ping_tpl["id"]

        j = client.post(
            "/api/v1/network-scans/jobs",
            json={
                "template_id": tid,
                "ipv4_prefix_id": pid,
                "options": {"inventory_mode": "none"},
            },
        )
        assert j.status_code == 200, j.text
        job_id = j.json()["id"]

        d = client.get(f"/api/v1/network-scans/jobs/{job_id}")
        assert d.status_code == 200, d.text
        body = d.json()
        assert body["status"] == "completed"
        assert body["hosts_matched"] >= 1
        alive = [h for h in body["host_results"] if h["result_json"].get("alive")]
        assert any(h["address"] == "10.50.0.1" for h in alive)


def test_network_scan_prefix_binding_blocks_unlisted_template(monkeypatch) -> None:
    monkeypatch.setattr("app.services.network_scan.ping_one_ip", lambda _ip: False)

    app = create_app()
    with TestClient(app) as client:
        sa = client.post("/api/v1/dcim/sites", json={"name": "BindSite", "slug": "bind-site"}).json()["id"]
        p = client.post(
            "/api/v1/ipam/ipv4-prefixes",
            json={"site_id": sa, "name": "LAN", "cidr": "10.51.0.0/30"},
        )
        pid = p.json()["id"]

        templates = client.get("/api/v1/network-scans/templates").json()
        ping_id = next(x["id"] for x in templates if x["slug"] == "builtin-ping")
        snmp_id = next(x["id"] for x in templates if x["slug"] == "builtin-snmp-inventory")

        b = client.post(
            "/api/v1/network-scans/prefix-bindings",
            json={"template_id": ping_id, "ipv4_prefix_id": pid, "enabled": True},
        )
        assert b.status_code == 200, b.text

        bad = client.post(
            "/api/v1/network-scans/jobs",
            json={"template_id": snmp_id, "ipv4_prefix_id": pid, "options": {}},
        )
        assert bad.status_code == 400

        ok = client.post(
            "/api/v1/network-scans/jobs",
            json={"template_id": ping_id, "ipv4_prefix_id": pid, "options": {}},
        )
        assert ok.status_code == 200, ok.text


def test_network_scan_discovery_queue_and_approve(monkeypatch) -> None:
    monkeypatch.setattr("app.services.network_scan.ping_one_ip", _ping_only_dot1)
    monkeypatch.setattr("app.services.network_scan.reverse_dns_ptr", lambda _ip: "ptr.example.test.")

    app = create_app()
    with TestClient(app) as client:
        sa = client.post("/api/v1/dcim/sites", json={"name": "DqSite", "slug": "dq-site"}).json()["id"]
        p = client.post(
            "/api/v1/ipam/ipv4-prefixes",
            json={"site_id": sa, "name": "LAN", "cidr": "10.52.0.0/30"},
        )
        pid = p.json()["id"]

        templates = client.get("/api/v1/network-scans/templates").json()
        ping_id = next(x["id"] for x in templates if x["slug"] == "builtin-ping")

        job = client.post(
            "/api/v1/network-scans/jobs",
            json={
                "template_id": ping_id,
                "ipv4_prefix_id": pid,
                "options": {"inventory_mode": "discovered_queue"},
            },
        )
        assert job.status_code == 200, job.text

        disc = client.get("/api/v1/network-scans/discoveries?status=pending")
        assert disc.status_code == 200, disc.text
        rows = disc.json()
        assert len(rows) >= 1
        did = rows[0]["id"]
        assert rows[0]["name_candidates_json"].get("ptr")

        mfr = client.post("/api/v1/dcim/manufacturers", json={"name": "NS Mfr Approve"}).json()
        dt = client.post("/api/v1/dcim/device-types", json={"name": "NS Type", "slug": "ns-type"}).json()
        dm = client.post(
            "/api/v1/dcim/device-models",
            json={"manufacturer_id": mfr["id"], "device_type_id": dt["id"], "name": "NS Model", "u_height": 1},
        ).json()

        ap = client.patch(
            f"/api/v1/network-scans/discoveries/{did}",
            json={"chosen_name_source": "ptr", "device_model_id": dm["id"]},
        )
        assert ap.status_code == 200, ap.text
        assert ap.json()["status"] == "promoted"
        assert ap.json()["dcim_device_id"] is not None


def test_network_scan_snmp_job_mocked(monkeypatch) -> None:
    async def fake_sys(**_kwargs):  # noqa: ANN003
        from app.schemas.snmp import SnmpSysInfoRead

        return SnmpSysInfoRead(ok=True, sys_name="router.lab", sys_descr="test")

    monkeypatch.setattr("app.services.network_scan.run_snmp_sys_info", fake_sys)

    app = create_app()
    with TestClient(app) as client:
        sa = client.post("/api/v1/dcim/sites", json={"name": "SnmpSite", "slug": "snmp-site"}).json()["id"]
        p = client.post(
            "/api/v1/ipam/ipv4-prefixes",
            json={"site_id": sa, "name": "Tiny", "cidr": "10.53.0.0/30"},
        )
        pid = p.json()["id"]
        snmp_id = next(
            x["id"] for x in client.get("/api/v1/network-scans/templates").json() if x["slug"] == "builtin-snmp-inventory"
        )

        j = client.post(
            "/api/v1/network-scans/jobs",
            json={"template_id": snmp_id, "ipv4_prefix_id": pid, "options": {"inventory_mode": "none"}},
        )
        assert j.status_code == 200, j.text
        job_id = j.json()["id"]
        d = client.get(f"/api/v1/network-scans/jobs/{job_id}").json()
        ok_hosts = [h for h in d["host_results"] if h["result_json"].get("ok")]
        assert len(ok_hosts) >= 1
        assert ok_hosts[0]["result_json"].get("sys_name") == "router.lab"


def test_network_scan_delete_job() -> None:
    app = create_app()
    with TestClient(app) as client:
        sa = client.post("/api/v1/dcim/sites", json={"name": "DelSite", "slug": "del-site"}).json()["id"]
        p = client.post(
            "/api/v1/ipam/ipv4-prefixes",
            json={"site_id": sa, "name": "Tiny", "cidr": "10.54.0.0/30"},
        )
        pid = p.json()["id"]
        ping_id = next(
            x["id"] for x in client.get("/api/v1/network-scans/templates").json() if x["slug"] == "builtin-ping"
        )

        j = client.post(
            "/api/v1/network-scans/jobs",
            json={"template_id": ping_id, "ipv4_prefix_id": pid, "options": {}},
        )
        job_id = j.json()["id"]
        dl = client.delete(f"/api/v1/network-scans/jobs/{job_id}")
        assert dl.status_code == 204
        assert client.get(f"/api/v1/network-scans/jobs/{job_id}").status_code == 404
