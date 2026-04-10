"""API-tester for SNMP MIB-lager."""

from fastapi.testclient import TestClient

from app.main import create_app


def test_snmp_mibs_upload_list_delete() -> None:
    app = create_app()
    with TestClient(app) as client:
        li = client.get("/api/v1/snmp/mibs")
        assert li.status_code == 200
        assert li.json() == []

        up = client.post(
            "/api/v1/snmp/mibs",
            files={"file": ("EXAMPLE-MIB.mib", b"-- example mib --", "text/plain")},
        )
        assert up.status_code == 200, up.text
        body = up.json()
        assert body["name"] == "EXAMPLE-MIB.mib"
        assert body["size_bytes"] == len(b"-- example mib --")

        li2 = client.get("/api/v1/snmp/mibs")
        assert li2.status_code == 200
        assert len(li2.json()) == 1
        assert li2.json()[0]["name"] == "EXAMPLE-MIB.mib"

        rm = client.delete("/api/v1/snmp/mibs/EXAMPLE-MIB.mib")
        assert rm.status_code == 204

        li3 = client.get("/api/v1/snmp/mibs")
        assert li3.status_code == 200
        assert li3.json() == []


def test_snmp_mibs_reject_bad_name() -> None:
    app = create_app()
    with TestClient(app) as client:
        up = client.post(
            "/api/v1/snmp/mibs",
            files={"file": ("not-a-mib.exe", b"x", "application/octet-stream")},
        )
        assert up.status_code == 400
