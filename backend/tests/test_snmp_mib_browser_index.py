"""Indeks for SNMP MIB browser: PySNMP getName()-formater og locate."""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from app.core.config import get_settings
from app.services.snmp_mib_browser import (
    _oid_and_label_from_get_name,
    definition_for_browser,
    locate_from_mib_filename,
    locate_module_oid,
)
from app.services.snmp_mib_compile import compile_mib_modules


_MIN_APACHE_LIKE = textwrap.dedent(
    r"""
    APACHE-MIB DEFINITIONS ::= BEGIN
    IMPORTS
        MODULE-IDENTITY, enterprises FROM SNMPv2-SMI;
    apache MODULE-IDENTITY
        LAST-UPDATED "202001010000Z"
        ORGANIZATION "x"
        CONTACT-INFO "x"
        DESCRIPTION "x"
        REVISION "202001010000Z"
        DESCRIPTION "x"
        ::= { enterprises 10892 }
    END
    """
).strip()


def test_oid_and_label_accepts_plain_oid_tuple() -> None:
    r = _oid_and_label_from_get_name("apache", (1, 3, 6, 1, 4, 1, 10892))
    assert r is not None
    oid_t, label = r
    assert oid_t == (1, 3, 6, 1, 4, 1, 10892)
    assert label == "apache"


def test_oid_and_label_accepts_name_oid_pair() -> None:
    r = _oid_and_label_from_get_name("x", ("sysDescr", (1, 3, 6, 1, 2, 1, 1, 1)))
    assert r is not None
    oid_t, label = r
    assert oid_t == (1, 3, 6, 1, 2, 1, 1, 1)
    assert label == "sysDescr"


@pytest.fixture
def apache_like_mib_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    mib_root = tmp_path / "mibs"
    compiled = tmp_path / "compiled"
    mib_root.mkdir()
    compiled.mkdir()
    (mib_root / "APACHE-MIB.mib").write_text(_MIN_APACHE_LIKE + "\n", encoding="utf-8")
    monkeypatch.setenv("MIB_ROOT", str(mib_root))
    monkeypatch.setenv("MIB_COMPILED_ROOT", str(compiled))
    get_settings.cache_clear()
    yield mib_root, compiled
    get_settings.cache_clear()


_MIB_TWO_OBJECTS = textwrap.dedent(
    r"""
    X-TEST-MIB DEFINITIONS ::= BEGIN
    IMPORTS
        MODULE-IDENTITY, enterprises FROM SNMPv2-SMI
        OBJECT-TYPE FROM SNMPv2-SMI;
    root MODULE-IDENTITY
        LAST-UPDATED "202001010000Z"
        ORGANIZATION "x"
        CONTACT-INFO "x"
        DESCRIPTION "x"
        REVISION "202001010000Z"
        DESCRIPTION "x"
        ::= { enterprises 424242 }
    a OBJECT-TYPE
        SYNTAX INTEGER
        MAX-ACCESS read-only
        STATUS current
        DESCRIPTION "a"
        ::= { root 1 }
    b OBJECT-TYPE
        SYNTAX INTEGER
        MAX-ACCESS read-only
        STATUS current
        DESCRIPTION "b"
        ::= { root 2 }
    END
    """
).strip()


def test_definition_for_browser_returns_full_file_and_highlight_lines(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    mib_root = tmp_path / "mibs"
    compiled = tmp_path / "compiled"
    mib_root.mkdir()
    compiled.mkdir()
    (mib_root / "X-TEST-MIB.mib").write_text(_MIB_TWO_OBJECTS + "\n", encoding="utf-8")
    monkeypatch.setenv("MIB_ROOT", str(mib_root))
    monkeypatch.setenv("MIB_COMPILED_ROOT", str(compiled))
    get_settings.cache_clear()
    settings = get_settings()
    d = definition_for_browser(settings, module_name="X-TEST-MIB", symbol="a")
    assert "a OBJECT-TYPE" in d["text"]
    assert "b OBJECT-TYPE" in d["text"]
    assert d["source_filename"] == "X-TEST-MIB.mib"
    assert d["highlight_start_line"] is not None
    assert d["highlight_end_line"] is not None
    assert d["highlight_end_line"] >= d["highlight_start_line"]
    # «b» starter på egen linje etter «a»-blokken
    assert d["highlight_end_line"] < d["text"].count("\n") + 1


def test_locate_finds_module_identity_only_mib(apache_like_mib_env) -> None:
    """MODULE-IDENTITY uten OBJECT-TYPE skal fortsatt gi OID i browser-indeksen."""
    import app.services.snmp_mib_browser as br

    settings = get_settings()
    r = compile_mib_modules(settings, ["APACHE-MIB"], rebuild=True)
    st, err, _ = r["APACHE-MIB"]
    assert st == "compiled", err
    br._idx.built_from_compiled_mtime = None  # type: ignore[attr-defined]
    loc = locate_module_oid(settings, "APACHE-MIB")
    assert loc["found"] is True
    assert loc["oid"] == "1.3.6.1.4.1.10892"
    loc2 = locate_from_mib_filename(settings, "APACHE-MIB.mib")
    assert loc2["found"] is True
    assert loc2["oid"] == "1.3.6.1.4.1.10892"
