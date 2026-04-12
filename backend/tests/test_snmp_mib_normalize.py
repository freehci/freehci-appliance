"""Tester for MIB-kildenormalisering (Juniper JUNIPER-SMI / pysmi)."""

from app.services.snmp_mib_normalize import normalize_mib_source_text

_JUNIPER_HEAD = """JUNIPER-SMI DEFINITIONS ::= BEGIN
IMPORTS
    MODULE-IDENTITY, OBJECT-IDENTITY, enterprises
        FROM SNMPv2-SMI;
juniperMIB MODULE-IDENTITY
    LAST-UPDATED "201912180000Z"
    ::= { enterprises 2636 }
Integer64 ::= TEXTUAL-CONVENTION
    STATUS current
    DESCRIPTION "x"
    SYNTAX Opaque (SIZE(4..11))
END
"""


def test_normalize_juniper_smi_adds_tc_and_opaque_imports() -> None:
    out, changed = normalize_mib_source_text(_JUNIPER_HEAD)
    assert changed is True
    assert "FROM SNMPv2-TC" in out
    assert "TEXTUAL-CONVENTION" in out.split("FROM SNMPv2-TC")[0][-80:]
    assert "Opaque" in out
    assert "MODULE-IDENTITY, OBJECT-IDENTITY, enterprises, Opaque" in out


def test_normalize_idempotent_when_tc_present() -> None:
    fixed, _ = normalize_mib_source_text(_JUNIPER_HEAD)
    again, changed = normalize_mib_source_text(fixed)
    assert changed is False
    assert again == fixed


def test_normalize_skips_unrelated_mib() -> None:
    text = "OTHER-MIB DEFINITIONS ::= BEGIN\nIMPORTS\n    a FROM B;\nEND\n"
    out, changed = normalize_mib_source_text(text)
    assert changed is False
    assert out == text
