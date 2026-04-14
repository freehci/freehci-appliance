"""API-tester for SNMP MIB-lager."""

import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from app.services import snmp_mib_catalog as mib_cat


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


def test_snmp_mibs_source_reads_legacy_mib_txt_filename_on_disk() -> None:
    """Filer som fortsatt heter *.mib.txt på disk skal kunne åpnes når UI/API bruker det navnet."""
    root = Path(os.environ["MIB_ROOT"])
    legacy = root / "BROCADE-LLDP-EXT-DOT3-CAPABILITY-MIB.mib.txt"
    legacy.write_text("LEGACY-ON-DISK\n", encoding="utf-8")
    try:
        app = create_app()
        with TestClient(app) as client:
            src = client.get(
                "/api/v1/snmp/mibs/BROCADE-LLDP-EXT-DOT3-CAPABILITY-MIB.mib.txt/source",
            )
            assert src.status_code == 200, src.text
            assert "LEGACY-ON-DISK" in src.text
    finally:
        legacy.unlink(missing_ok=True)


def test_snmp_mibs_source_prefers_canonical_mib_when_legacy_double_suffix_exists() -> None:
    root = Path(os.environ["MIB_ROOT"])
    norm = root / "DUP-MIB.mib"
    legacy = root / "DUP-MIB.mib.txt"
    norm.write_text("from-mib\n", encoding="utf-8")
    legacy.write_text("from-mib-txt\n", encoding="utf-8")
    try:
        app = create_app()
        with TestClient(app) as client:
            src = client.get("/api/v1/snmp/mibs/DUP-MIB.mib.txt/source")
            assert src.status_code == 200, src.text
            assert "from-mib" in src.text
            assert "from-mib-txt" not in src.text
    finally:
        norm.unlink(missing_ok=True)
        legacy.unlink(missing_ok=True)


def test_snmp_mibs_normalizes_double_suffix_mib_txt() -> None:
    """*.mib.txt normaliseres til MODUL.mib ved lagring."""
    app = create_app()
    with TestClient(app) as client:
        up = client.post(
            "/api/v1/snmp/mibs",
            files={"file": ("BROCADE-REG-MIB.mib.txt", b"X", "text/plain")},
        )
        assert up.status_code == 200, up.text
        assert up.json()["name"] == "BROCADE-REG-MIB.mib"


def test_snmp_mibs_normalizes_double_suffix_my_txt() -> None:
    app = create_app()
    with TestClient(app) as client:
        up = client.post(
            "/api/v1/snmp/mibs",
            files={"file": ("FOO-MIB.my.txt", b"Y", "text/plain")},
        )
        assert up.status_code == 200, up.text
        assert up.json()["name"] == "FOO-MIB.mib"


def test_snmp_mibs_normalize_filenames_endpoint() -> None:
    root = Path(os.environ["MIB_ROOT"])
    legacy = root / "ORPHAN-NORM-MIB.txt"
    legacy.write_text("M DEFINITIONS ::= BEGIN END\n", encoding="utf-8")
    try:
        app = create_app()
        with TestClient(app) as client:
            r = client.post("/api/v1/snmp/mibs/normalize-filenames")
            assert r.status_code == 200, r.text
            body = r.json()
            assert body["moved_count"] >= 1
            assert any(m.get("to") == "ORPHAN-NORM-MIB.mib" for m in body["moved"])
        assert not (root / "ORPHAN-NORM-MIB.txt").exists()
        assert (root / "ORPHAN-NORM-MIB.mib").is_file()
    finally:
        (root / "ORPHAN-NORM-MIB.mib").unlink(missing_ok=True)
        (root / "ORPHAN-NORM-MIB.txt").unlink(missing_ok=True)


def test_snmp_mibs_compile_pending_returns_202_and_runs_background(monkeypatch: pytest.MonkeyPatch) -> None:
    called: list[int] = []

    def fake_bg() -> None:
        called.append(1)

    monkeypatch.setattr(mib_cat, "run_compile_pending_mibs_background", fake_bg)
    app = create_app()
    with TestClient(app) as client:
        r = client.post("/api/v1/snmp/mibs/compile-pending", json={})
        assert r.status_code == 202, r.text
        assert r.json() == {"queued": True}
    assert called == [1]


def test_snmp_mibs_compile_all_returns_202_and_runs_background(monkeypatch: pytest.MonkeyPatch) -> None:
    called: list[int] = []

    def fake_bg() -> None:
        called.append(1)

    monkeypatch.setattr(mib_cat, "run_compile_all_mibs_background", fake_bg)
    app = create_app()
    with TestClient(app) as client:
        r = client.post("/api/v1/snmp/mibs/compile-all", json={})
        assert r.status_code == 202, r.text
        assert r.json() == {"queued": True}
    assert called == [1]
