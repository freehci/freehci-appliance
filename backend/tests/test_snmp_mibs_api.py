"""API-tester for SNMP MIB-lager."""

import uuid
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.main import create_app
from app.services import snmp_mib_catalog as mib_cat


def _mib_root_dir() -> Path:
    """Samme MIB-katalog som API (etter eventuell cache_clear)."""
    get_settings.cache_clear()
    return get_settings().mib_root_path.resolve()


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
        body = det.json()
        assert "items" in body and "total" in body
        by_name = {r["name"]: r for r in body["items"]}
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


def test_snmp_mibs_detailed_pagination_and_search() -> None:
    """Paginering og søk på /mibs/detailed."""
    app = create_app()
    with TestClient(app) as client:
        for name in ("ZZZ-PAGINATION-MIB.mib", "AAA-PAGINATION-MIB.mib", "MMM-PAGINATION-MIB.mib"):
            up = client.post(
                "/api/v1/snmp/mibs",
                files={"file": (name, b"X DEFINITIONS ::= BEGIN\nEND\n", "text/plain")},
            )
            assert up.status_code == 200, up.text
        p1 = client.get("/api/v1/snmp/mibs/detailed?page=1&page_size=2&sort=name&order=asc")
        assert p1.status_code == 200, p1.text
        b1 = p1.json()
        assert b1["total"] >= 3
        assert len(b1["items"]) == 2
        assert b1["page"] == 1
        assert b1["page_size"] == 2
        names = [x["name"] for x in b1["items"]]
        assert names == sorted(names)
        q = client.get("/api/v1/snmp/mibs/detailed?q=ZZZ-PAGINATION")
        assert q.status_code == 200
        bq = q.json()
        assert bq["total"] >= 1
        assert any("ZZZ-PAGINATION" in x["name"] for x in bq["items"])


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
    u = uuid.uuid4().hex[:10]
    legacy_name = f"LEGACY-BROCADE-{u}.mib.txt"
    root = _mib_root_dir()
    legacy = root / legacy_name
    legacy.write_text("LEGACY-ON-DISK\n", encoding="utf-8")
    try:
        app = create_app()
        with TestClient(app) as client:
            src = client.get(f"/api/v1/snmp/mibs/{legacy_name}/source")
            assert src.status_code == 200, src.text
            assert "LEGACY-ON-DISK" in src.text
    finally:
        legacy.unlink(missing_ok=True)


def test_snmp_mibs_source_prefers_canonical_mib_when_legacy_double_suffix_exists() -> None:
    u = uuid.uuid4().hex[:10]
    base = f"DUP-MIB-{u}"
    root = _mib_root_dir()
    norm = root / f"{base}.mib"
    legacy = root / f"{base}.mib.txt"
    norm.write_text("from-mib\n", encoding="utf-8")
    legacy.write_text("from-mib-txt\n", encoding="utf-8")
    try:
        app = create_app()
        with TestClient(app) as client:
            src = client.get(f"/api/v1/snmp/mibs/{base}.mib.txt/source")
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
    u = uuid.uuid4().hex[:10]
    base = f"ORPHAN-NORM-{u}"
    legacy_name = f"{base}.txt"
    canon_name = f"{base}.mib"
    root = _mib_root_dir()
    legacy = root / legacy_name
    legacy.write_text("M DEFINITIONS ::= BEGIN END\n", encoding="utf-8")
    try:
        app = create_app()
        with TestClient(app) as client:
            r = client.post("/api/v1/snmp/mibs/normalize-filenames")
            assert r.status_code == 200, r.text
            body = r.json()
            assert body["moved_count"] >= 1, body
            assert any(m.get("to") == canon_name for m in body["moved"]), body
        assert not (root / legacy_name).exists()
        assert (root / canon_name).is_file()
    finally:
        (root / canon_name).unlink(missing_ok=True)
        (root / legacy_name).unlink(missing_ok=True)


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
