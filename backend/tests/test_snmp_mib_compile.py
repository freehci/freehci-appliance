"""Tester for pysmi-MIB-kompilering (kildevalg og avhengigheter)."""

from __future__ import annotations

import shutil
import textwrap

import pytest

from app.core.config import get_settings
from app.services.snmp_mib_compile import compile_mib_modules, compile_status_is_success


_BROCADE_REG_OLD = textwrap.dedent(
    """\
    Brocade-REG-MIB DEFINITIONS ::= BEGIN
    IMPORTS
        MODULE-IDENTITY, OBJECT-IDENTITY, enterprises FROM SNMPv2-SMI;
    bcsi MODULE-IDENTITY
        LAST-UPDATED "201202030000Z"
        ORGANIZATION "x"
        CONTACT-INFO "x"
        DESCRIPTION "x"
        REVISION "201202030000Z"
        DESCRIPTION "x"
        ::= { enterprises 1588 }
    bcsiReg OBJECT-IDENTITY
        STATUS current
        DESCRIPTION "x"
        ::= { bcsi 3 }
    END
    """
)

_BROCADE_REG_NEW = _BROCADE_REG_OLD.replace(
    "END",
    textwrap.dedent(
        """\
        brocadeAgentCapability OBJECT-IDENTITY
            STATUS current
            DESCRIPTION "x"
            ::= { bcsiReg 2 }
        END
        """
    ),
)

# Filnavn «SHORT» men DEFINITIONS «MY-LONG-VENDOR-MIB» — pysmi må slå opp via stem.
_VENDOR_STEM_MISMATCH = textwrap.dedent(
    """\
    MY-LONG-VENDOR-MIB DEFINITIONS ::= BEGIN
    IMPORTS
        MODULE-IDENTITY, OBJECT-IDENTITY, enterprises FROM SNMPv2-SMI;
    x MODULE-IDENTITY
        LAST-UPDATED "202001010000Z"
        ORGANIZATION "x"
        CONTACT-INFO "x"
        DESCRIPTION "x"
        REVISION "202001010000Z"
        DESCRIPTION "x"
        ::= { enterprises 99999 }
    END
    """
)

_TEST_CONSUMER = textwrap.dedent(
    """\
    TEST-CONS-MIB DEFINITIONS ::= BEGIN
    IMPORTS
        OBJECT-IDENTITY FROM SNMPv2-SMI
        brocadeAgentCapability FROM Brocade-REG-MIB;
    t OBJECT-IDENTITY
        STATUS current
        DESCRIPTION "x"
        ::= { brocadeAgentCapability 1 }
    END
    """
)


def test_local_mib_prefers_suffixed_file_over_extensionless(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    """Uten .my/.mib først kan en gammel fil uten suffiks velges og gi manglende symboler."""
    mib_root = tmp_path / "mibs"
    compiled = tmp_path / "compiled"
    mib_root.mkdir()
    compiled.mkdir()
    monkeypatch.setenv("MIB_ROOT", str(mib_root))
    monkeypatch.setenv("MIB_COMPILED_ROOT", str(compiled))
    get_settings.cache_clear()

    (mib_root / "Brocade-REG-MIB").write_text(_BROCADE_REG_OLD, encoding="utf-8")
    (mib_root / "Brocade-REG-MIB.my").write_text(_BROCADE_REG_NEW, encoding="utf-8")
    (mib_root / "TEST-CONS-MIB.mib").write_text(_TEST_CONSUMER, encoding="utf-8")

    settings = get_settings()
    results = compile_mib_modules(settings, ["TEST-CONS-MIB"], rebuild=True)
    st, err, _ = results["TEST-CONS-MIB"]
    assert compile_status_is_success(st), f"forventet ok, fikk {st!r}: {err}"


def test_mib_dot_index_rebuilt_from_sources(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    """Ved kompilering overskrives .index fra DEFINITIONS på disk — utdatert manuell .index erstattes."""
    mib_root = tmp_path / "mibs"
    compiled = tmp_path / "compiled"
    mib_root.mkdir()
    compiled.mkdir()
    monkeypatch.setenv("MIB_ROOT", str(mib_root))
    monkeypatch.setenv("MIB_COMPILED_ROOT", str(compiled))
    get_settings.cache_clear()

    (mib_root / "Brocade-REG-MIB").write_text(_BROCADE_REG_OLD, encoding="utf-8")
    (mib_root / "Brocade-REG-MIB.my").write_text(_BROCADE_REG_NEW, encoding="utf-8")
    (mib_root / "TEST-CONS-MIB.mib").write_text(_TEST_CONSUMER, encoding="utf-8")
    (mib_root / ".index").write_text("Brocade-REG-MIB Brocade-REG-MIB\n", encoding="utf-8")

    settings = get_settings()
    results = compile_mib_modules(settings, ["TEST-CONS-MIB"], rebuild=True)
    st, err, _ = results["TEST-CONS-MIB"]
    assert compile_status_is_success(st), f"forventet ok, fikk {st!r}: {err}"


def test_compile_finds_file_when_stem_differs_from_definitions_name(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    """Filnavn (SHORT.txt) kan avvike fra DEFINITIONS (MY-LONG-VENDOR-MIB) via regenerert .index."""
    mib_root = tmp_path / "mibs"
    compiled = tmp_path / "compiled"
    mib_root.mkdir()
    compiled.mkdir()
    monkeypatch.setenv("MIB_ROOT", str(mib_root))
    monkeypatch.setenv("MIB_COMPILED_ROOT", str(compiled))
    get_settings.cache_clear()

    (mib_root / "SHORT.txt").write_text(_VENDOR_STEM_MISMATCH, encoding="utf-8")

    settings = get_settings()
    by_module = compile_mib_modules(settings, ["MY-LONG-VENDOR-MIB"], rebuild=True)
    st_mod, err_mod, _ = by_module["MY-LONG-VENDOR-MIB"]
    assert compile_status_is_success(st_mod), f"forventet ok via .index, fikk {st_mod!r}: {err_mod}"

    shutil.rmtree(compiled)
    compiled.mkdir()
    by_stem = compile_mib_modules(
        settings,
        ["SHORT"],
        rebuild=True,
        resolution_hints=["MY-LONG-VENDOR-MIB", "SHORT"],
    )
    st_ok, err, _ = by_stem["SHORT"]
    assert compile_status_is_success(st_ok), f"forventet ok, fikk {st_ok!r}: {err}"
