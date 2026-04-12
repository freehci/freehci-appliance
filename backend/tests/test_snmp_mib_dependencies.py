"""Tester for MIB IMPORTS vs lokale filer / standardmoduler."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.core.config import get_settings
from app.core.db import SessionLocal
from app.models.snmp_catalog import SnmpMibFileMeta
from app.services import snmp_mibs as mib_disk
from app.services.snmp_mib_catalog import upsert_mib_meta
from app.services.snmp_mib_dependencies import (
    missing_vendor_import_modules,
    refresh_missing_imports_all,
)


def test_missing_vendor_import_detects_juniper_smi() -> None:
    consumer = """MY-MIB DEFINITIONS ::= BEGIN
IMPORTS
    MODULE-IDENTITY, OBJECT-TYPE FROM SNMPv2-SMI
    jnxMibs FROM JUNIPER-SMI;
x MODULE-IDENTITY
    LAST-UPDATED "200001010000Z"
    ORGANIZATION "t"
    CONTACT-INFO "t"
    DESCRIPTION "t"
    ::= { enterprises 1 }
END
"""
    miss = missing_vendor_import_modules(consumer, "MY-MIB", {"MY-MIB", "SNMPv2-SMI"})
    assert "JUNIPER-SMI" in miss
    assert "SNMPv2-SMI" not in miss


def test_no_missing_when_local_has_module() -> None:
    text = """X DEFINITIONS ::= BEGIN
IMPORTS
    MODULE-IDENTITY FROM SNMPv2-SMI
    y FROM Z-MIB;
m MODULE-IDENTITY
    LAST-UPDATED "200001010000Z"
    ORGANIZATION "t"
    CONTACT-INFO "t"
    DESCRIPTION "t"
    ::= { enterprises 1 }
END
"""
    assert missing_vendor_import_modules(text, "X", {"X", "Z-MIB"}) == []


def test_refresh_missing_after_upload(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    mib_root = tmp_path / "mibs"
    mib_root.mkdir()
    compiled = tmp_path / "compiled"
    compiled.mkdir()
    monkeypatch.setenv("MIB_ROOT", str(mib_root))
    monkeypatch.setenv("MIB_COMPILED_ROOT", str(compiled))
    get_settings.cache_clear()
    settings = get_settings()

    (mib_root / "child.txt").write_text(
        """CHILD-MIB DEFINITIONS ::= BEGIN
IMPORTS
    MODULE-IDENTITY FROM SNMPv2-SMI
    rootNode FROM PARENT-MIB;
c MODULE-IDENTITY
    LAST-UPDATED "200001010000Z"
    ORGANIZATION "t"
    CONTACT-INFO "t"
    DESCRIPTION "t"
    ::= { enterprises 42 }
END
""",
        encoding="utf-8",
    )
    raw = (mib_root / "child.txt").read_bytes()
    mib_disk.save_mib_file(settings, "child.txt", raw)

    db = SessionLocal()
    try:
        upsert_mib_meta(db, settings, "child.txt", raw)
        refresh_missing_imports_all(db, settings)
        meta = db.get(SnmpMibFileMeta, "child.txt")
        assert meta is not None
        assert json.loads(meta.missing_import_modules_json) == ["PARENT-MIB"]

        (mib_root / "parent.txt").write_text(
            """PARENT-MIB DEFINITIONS ::= BEGIN
IMPORTS
    MODULE-IDENTITY FROM SNMPv2-SMI;
rootNode MODULE-IDENTITY
    LAST-UPDATED "200001010000Z"
    ORGANIZATION "t"
    CONTACT-INFO "t"
    DESCRIPTION "t"
    ::= { enterprises 42 1 }
END
""",
            encoding="utf-8",
        )
        praw = (mib_root / "parent.txt").read_bytes()
        mib_disk.save_mib_file(settings, "parent.txt", praw)
        upsert_mib_meta(db, settings, "parent.txt", praw)
        refresh_missing_imports_all(db, settings)
        db.refresh(meta)
        assert json.loads(meta.missing_import_modules_json) == []
    finally:
        db.close()
