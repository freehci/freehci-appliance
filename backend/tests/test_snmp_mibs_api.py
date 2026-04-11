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


def test_snmp_mibs_batch_and_detailed() -> None:
    app = create_app()
    with TestClient(app) as client:
        up = client.post(
            "/api/v1/snmp/mibs/batch",
            files=[
                ("files", ("A.mib", b"X DEFINITIONS ::= BEGIN\nEND\n{ enterprises 42 }\n", "text/plain")),
                ("files", ("B.mib", b"Y DEFINITIONS ::= BEGIN\nEND\n", "text/plain")),
            ],
        )
        assert up.status_code == 200, up.text
        bodies = up.json()
        assert len(bodies) == 2
        names = {b["name"] for b in bodies}
        assert names == {"A.mib", "B.mib"}

        det = client.get("/api/v1/snmp/mibs/detailed")
        assert det.status_code == 200
        by_name = {r["name"]: r for r in det.json()}
        assert by_name["A.mib"]["enterprise_number"] == 42
        assert by_name["B.mib"]["enterprise_number"] is None

        ent = client.get("/api/v1/snmp/enterprises")
        assert ent.status_code == 200
        pens = {g["enterprise_number"] for g in ent.json()}
        assert None in pens
        assert 42 in pens


def test_snmp_mibs_reject_bad_name() -> None:
    app = create_app()
    with TestClient(app) as client:
        up = client.post(
            "/api/v1/snmp/mibs",
            files={"file": ("not-a-mib.exe", b"x", "application/octet-stream")},
        )
        assert up.status_code == 400
