"""API-tester for SNMP MIB-lager."""

from fastapi.testclient import TestClient

from app.main import create_app


def test_snmp_mibs_upload_list_delete() -> None:
    app = create_app()
    with TestClient(app) as client:
        li = client.get("/api/v1/snmp/mibs")
        assert li.status_code == 200
        initial_names = {x["name"] for x in li.json()}
        assert "EXAMPLE-MIB.mib" not in initial_names

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
        names_after_up = {x["name"] for x in li2.json()}
        assert names_after_up == initial_names | {"EXAMPLE-MIB.mib"}
        example = next(x for x in li2.json() if x["name"] == "EXAMPLE-MIB.mib")
        assert example["size_bytes"] == len(b"-- example mib --")

        src = client.get("/api/v1/snmp/mibs/EXAMPLE-MIB.mib/source")
        assert src.status_code == 200
        assert "-- example mib --" in src.text

        rm = client.delete("/api/v1/snmp/mibs/EXAMPLE-MIB.mib")
        assert rm.status_code == 204

        li3 = client.get("/api/v1/snmp/mibs")
        assert li3.status_code == 200
        assert {x["name"] for x in li3.json()} == initial_names


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
        body = ent.json()
        pens = {g["enterprise_number"] for g in body}
        assert None in pens
        assert 42 in pens
        for g in body:
            assert "mib_tree" in g
            assert isinstance(g["mib_tree"], list)


def test_snmp_mibs_reject_bad_name() -> None:
    app = create_app()
    with TestClient(app) as client:
        up = client.post(
            "/api/v1/snmp/mibs",
            files={"file": ("not-a-mib.exe", b"x", "application/octet-stream")},
        )
        assert up.status_code == 400


def test_snmp_mibs_reject_double_suffix_mib_txt() -> None:
    """*.mib.txt matches ikke pysmis filnavnvarianter (MODUL.txt / MODUL.mib)."""
    app = create_app()
    with TestClient(app) as client:
        up = client.post(
            "/api/v1/snmp/mibs",
            files={"file": ("BROCADE-REG-MIB.mib.txt", b"X", "text/plain")},
        )
        assert up.status_code == 400
