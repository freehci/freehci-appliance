"""API-tester for IPAM subnett-skann (ping + MAC, med mock av bakgrunnsjobb)."""

from fastapi.testclient import TestClient

from app.main import create_app
from app.services import ipam_subnet_scan as scan_svc


def test_ipam_subnet_scan_creates_and_lists(monkeypatch) -> None:
    real_run = scan_svc.run_scan_background

    def run_mocked(scan_id: int) -> None:
        real_run(
            scan_id,
            ping_fn=lambda ip: ip == "10.0.1.1",
            load_mac_fn=lambda: {"10.0.1.1": "aa:bb:cc:dd:ee:01"},
        )

    monkeypatch.setattr("app.api.v1.routers.ipam.scan_svc.run_scan_background", run_mocked)

    app = create_app()
    with TestClient(app) as client:
        sa = client.post("/api/v1/dcim/sites", json={"name": "ScanSite", "slug": "scan-site"}).json()["id"]
        p = client.post(
            "/api/v1/ipam/ipv4-prefixes",
            json={"site_id": sa, "name": "LAN", "cidr": "10.0.1.0/24"},
        )
        assert p.status_code == 200, p.text
        pid = p.json()["id"]

        r = client.post("/api/v1/ipam/subnet-scans", json={"ipv4_prefix_id": pid})
        assert r.status_code == 200, r.text
        scan_id = r.json()["id"]
        assert r.json()["status"] in ("pending", "running", "completed")

        d = client.get(f"/api/v1/ipam/subnet-scans/{scan_id}")
        assert d.status_code == 200, d.text
        body = d.json()
        assert body["status"] == "completed"
        assert body["hosts_scanned"] == 256
        assert body["hosts_responding"] == 1
        assert len(body["hosts"]) == 256
        alive = [h for h in body["hosts"] if h["ping_responded"]]
        assert len(alive) == 1
        assert alive[0]["address"] == "10.0.1.1"
        assert alive[0]["mac_address"] == "aa:bb:cc:dd:ee:01"

        li = client.get(f"/api/v1/ipam/subnet-scans?ipv4_prefix_id={pid}")
        assert li.status_code == 200
        assert any(x["id"] == scan_id for x in li.json())

        inv = client.get(f"/api/v1/ipam/ipv4-addresses?ipv4_prefix_id={pid}")
        assert inv.status_code == 200, inv.text
        assert any(x["address"] == "10.0.1.1" and x["status"] == "discovered" for x in inv.json())


def test_ipam_subnet_scan_unknown_prefix() -> None:
    app = create_app()
    with TestClient(app) as client:
        r = client.post("/api/v1/ipam/subnet-scans", json={"ipv4_prefix_id": 99999})
        assert r.status_code == 404


def test_ipam_subnet_scan_too_large_prefix(monkeypatch) -> None:
    """Senk maksgrense midlertidig så /24 blir «for stort» uten å bygge millioner av mål."""
    monkeypatch.setattr("app.services.ipam_subnet_scan.MAX_SCAN_HOSTS", 10)
    real_run = scan_svc.run_scan_background

    def run_quick(scan_id: int) -> None:
        real_run(
            scan_id,
            ping_fn=lambda ip: False,
            load_mac_fn=dict,
        )

    monkeypatch.setattr("app.api.v1.routers.ipam.scan_svc.run_scan_background", run_quick)

    app = create_app()
    with TestClient(app) as client:
        sa = client.post("/api/v1/dcim/sites", json={"name": "Big", "slug": "big-net"}).json()["id"]
        p = client.post(
            "/api/v1/ipam/ipv4-prefixes",
            json={"site_id": sa, "name": "LAN", "cidr": "10.0.1.0/24"},
        )
        assert p.status_code == 200
        pid = p.json()["id"]

        r = client.post("/api/v1/ipam/subnet-scans", json={"ipv4_prefix_id": pid})
        assert r.status_code == 200
        scan_id = r.json()["id"]

        d = client.get(f"/api/v1/ipam/subnet-scans/{scan_id}")
        assert d.status_code == 200
        assert d.json()["status"] == "failed"
        assert "for mange" in (d.json().get("error_message") or "").lower()


def test_ipam_subnet_scan_get_unknown() -> None:
    app = create_app()
    with TestClient(app) as client:
        r = client.get("/api/v1/ipam/subnet-scans/999999")
        assert r.status_code == 404


def test_ipam_subnet_scan_fails_when_ping_binary_missing(monkeypatch) -> None:
    monkeypatch.setattr("app.services.ipam_subnet_scan.shutil.which", lambda _cmd: None)

    app = create_app()
    with TestClient(app) as client:
        sa = client.post("/api/v1/dcim/sites", json={"name": "NoPing", "slug": "no-ping"}).json()["id"]
        p = client.post(
            "/api/v1/ipam/ipv4-prefixes",
            json={"site_id": sa, "name": "Tiny", "cidr": "192.168.99.0/30"},
        )
        assert p.status_code == 200
        pid = p.json()["id"]

        r = client.post("/api/v1/ipam/subnet-scans", json={"ipv4_prefix_id": pid})
        assert r.status_code == 200
        scan_id = r.json()["id"]

        d = client.get(f"/api/v1/ipam/subnet-scans/{scan_id}")
        assert d.status_code == 200
        assert d.json()["status"] == "failed"
        assert "ping" in (d.json().get("error_message") or "").lower()
