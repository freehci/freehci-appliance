"""Tester for MIB-tre-topologi (foreldermatch)."""

from __future__ import annotations

from pathlib import Path

import pytest

from app.core.config import get_settings
from app.core.db import SessionLocal
from app.models.snmp_catalog import SnmpMibFileMeta
from app.services import snmp_mibs as mib_disk
from app.services.snmp_mib_catalog import _snmp_file_topology, upsert_mib_meta


def test_parent_resolves_when_db_module_name_stale(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Forelder skal finnes via DEFINITIONS i fila, ikke feil module_name i DB."""
    mib_root = tmp_path / "m"
    mib_root.mkdir()
    compiled = tmp_path / "c"
    compiled.mkdir()
    monkeypatch.setenv("MIB_ROOT", str(mib_root))
    monkeypatch.setenv("MIB_COMPILED_ROOT", str(compiled))
    get_settings.cache_clear()
    settings = get_settings()

    (mib_root / "PARENT.mib").write_text(
        """PARENT-MIB DEFINITIONS ::= BEGIN
IMPORTS
    MODULE-IDENTITY FROM SNMPv2-SMI;
p MODULE-IDENTITY
    LAST-UPDATED "200001010000Z"
    ORGANIZATION "t"
    CONTACT-INFO "t"
    DESCRIPTION "t"
    ::= { enterprises 1 }
END
""",
        encoding="utf-8",
    )
    # Ingen «enterprises» i OID → enterprise_number None, slik at parent_mib_missing kan testes.
    (mib_root / "CHILD.mib").write_text(
        """CHILD-MIB DEFINITIONS ::= BEGIN
IMPORTS
    MODULE-IDENTITY FROM SNMPv2-SMI
    p FROM PARENT-MIB;
c MODULE-IDENTITY
    LAST-UPDATED "200001010000Z"
    ORGANIZATION "t"
    CONTACT-INFO "t"
    DESCRIPTION "t"
    ::= { experimental 999 }
END
""",
        encoding="utf-8",
    )

    praw = (mib_root / "PARENT.mib").read_bytes()
    craw = (mib_root / "CHILD.mib").read_bytes()
    mib_disk.save_mib_file(settings, "PARENT.mib", praw)
    mib_disk.save_mib_file(settings, "CHILD.mib", craw)

    db = SessionLocal()
    try:
        upsert_mib_meta(db, settings, "PARENT.mib", praw)
        upsert_mib_meta(db, settings, "CHILD.mib", craw)

        # Simuler utdatert metadata: står feil modulnavn for forelder-fila.
        parent_meta = db.get(SnmpMibFileMeta, "PARENT.mib")
        assert parent_meta is not None
        parent_meta.module_name = "WRONG-MIB"
        db.commit()

        disk_rows = mib_disk.list_mib_files(settings)
        topo = _snmp_file_topology(db, settings, disk_rows)
        child = topo["CHILD.mib"]
        assert child["immediate_parent_file"] == "PARENT.mib"
        assert child["parent_mib_missing"] is False
    finally:
        db.close()
