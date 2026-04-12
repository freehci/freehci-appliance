"""Normalisering av kjente MIB-kildeskavanker før pysmi-kompilering."""

from __future__ import annotations

import re

# Juniper JUNIPER-SMI (mib-jnx-smi.txt) definerer Integer64 som TEXTUAL-CONVENTION med SYNTAX Opaque,
# men IMPORTS nevner verken TEXTUAL-CONVENTION (SNMPv2-TC) eller Opaque (SNMPv2-SMI) → pysmi:
# «Unknown parents for symbols: Integer64».
_JUNIPER_SMI_DEF_RE = re.compile(r"\bJUNIPER-SMI\s+DEFINITIONS\b", re.IGNORECASE)
_INTEGER64_TC_RE = re.compile(r"\bInteger64\s*::=\s*TEXTUAL-CONVENTION\b", re.IGNORECASE)
_HAS_SNMPV2_TC_IMPORT_RE = re.compile(
    r"\bTEXTUAL-CONVENTION\b[\s\S]{0,200}?\bFROM\s+SNMPv2-TC\b",
    re.IGNORECASE,
)
_JNX_IMPORTS_FIX_RE = re.compile(
    r"""
    IMPORTS\s+
    MODULE-IDENTITY\s*,\s*
    OBJECT-IDENTITY\s*,\s*
    enterprises\s+
    FROM\s+SNMPv2-SMI\s*;
    """,
    re.IGNORECASE | re.VERBOSE,
)


def normalize_mib_source_text(text: str) -> tuple[str, bool]:
    """Returner (tekst, True) hvis kilden ble endret for kompatibilitet med pysmi."""
    if not _JUNIPER_SMI_DEF_RE.search(text) or not _INTEGER64_TC_RE.search(text):
        return text, False
    if _HAS_SNMPV2_TC_IMPORT_RE.search(text):
        return text, False

    def _repl(m: re.Match[str]) -> str:  # noqa: ARG001
        return (
            "IMPORTS\n"
            "    MODULE-IDENTITY, OBJECT-IDENTITY, enterprises, Opaque\n"
            "        FROM SNMPv2-SMI,\n"
            "    TEXTUAL-CONVENTION\n"
            "        FROM SNMPv2-TC;"
        )

    new_text, n = _JNX_IMPORTS_FIX_RE.subn(_repl, text, count=1)
    if n == 0:
        return text, False
    return new_text, True
