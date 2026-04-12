"""Tester for PySMI .index (modulnavn → fil)."""

from __future__ import annotations

import time
from pathlib import Path

from app.core.config import Settings
from app.services.snmp_mib_index import extract_module_name_from_mib_text, rebuild_pysmi_mib_index
from app.services.snmp_mib_parse import guess_module_name


def test_extract_module_name_allows_leading_indent() -> None:
    text = """    JUNIPER-SMS-MIB DEFINITIONS ::= BEGIN
END
"""
    assert extract_module_name_from_mib_text(text) == "JUNIPER-SMS-MIB"


def test_guess_module_name_uses_definitions_not_filename(tmp_path: Path) -> None:
    text = """JUNIPER-JS-SMI DEFINITIONS ::= BEGIN
END
"""
    assert guess_module_name("mib-jnx-js-smi.txt", text) == "JUNIPER-JS-SMI"


def test_rebuild_index_maps_module_to_juniper_filename(tmp_path: Path) -> None:
    (tmp_path / "mib-jnx-js-smi.txt").write_text(
        "JUNIPER-JS-SMI DEFINITIONS ::= BEGIN\nEND\n",
        encoding="utf-8",
    )
    rebuild_pysmi_mib_index(tmp_path)
    idx = (tmp_path / ".index").read_text(encoding="utf-8")
    assert "JUNIPER-JS-SMI" in idx
    assert "mib-jnx-js-smi.txt" in idx


def test_rebuild_index_prefers_newer_on_duplicate_module(tmp_path: Path) -> None:
    a = tmp_path / "a.txt"
    b = tmp_path / "b.txt"
    body = "SAME-MIB DEFINITIONS ::= BEGIN\nEND\n"
    a.write_text(body, encoding="utf-8")
    time.sleep(0.05)
    b.write_text(body, encoding="utf-8")
    rebuild_pysmi_mib_index(tmp_path)
    chosen = (tmp_path / ".index").read_text(encoding="utf-8").strip().split()[1]
    assert chosen == "b.txt"


def test_compile_uses_index_for_mismatched_vendor_filename(tmp_path: Path) -> None:
    """Uten .index finnes ikke JUNIPER-JS-SMI som filvariant av mib-jnx-js-smi.txt."""
    from app.services.snmp_mib_compile import compile_mib_modules

    (tmp_path / "JUNIPER-SMI.txt").write_text(
        """JUNIPER-SMI DEFINITIONS ::= BEGIN
IMPORTS
    MODULE-IDENTITY, OBJECT-IDENTITY, enterprises, Opaque
        FROM SNMPv2-SMI
    TEXTUAL-CONVENTION
        FROM SNMPv2-TC;
juniperMIB MODULE-IDENTITY
    LAST-UPDATED "201912180000Z"
    ORGANIZATION "x"
    CONTACT-INFO "x"
    DESCRIPTION "x"
    ::= { enterprises 2636 }
jnxMibs OBJECT-IDENTITY
    STATUS current
    DESCRIPTION "x"
    ::= { juniperMIB 3 }
jnxJsMibRoot OBJECT IDENTIFIER ::= { jnxMibs 39 }
Integer64 ::= TEXTUAL-CONVENTION
    STATUS current
    DESCRIPTION "x"
    SYNTAX Opaque (SIZE(4..11))
END
""",
        encoding="utf-8",
    )
    (tmp_path / "mib-jnx-js-smi.txt").write_text(
        """JUNIPER-JS-SMI DEFINITIONS ::= BEGIN
IMPORTS
    jnxJsMibRoot FROM JUNIPER-SMI;
jnxJsSecurity OBJECT IDENTIFIER ::= { jnxJsMibRoot 1 }
jnxJsSMS OBJECT IDENTIFIER ::= { jnxJsSecurity 22 }
END
""",
        encoding="utf-8",
    )
    (tmp_path / "mib-jnx-js-sms.txt").write_text(
        """JUNIPER-SMS-MIB DEFINITIONS ::= BEGIN
IMPORTS
    MODULE-IDENTITY FROM SNMPv2-SMI
    jnxJsSMS FROM JUNIPER-JS-SMI;
x MODULE-IDENTITY
    LAST-UPDATED "202009020000Z"
    ORGANIZATION "x"
    CONTACT-INFO "x"
    DESCRIPTION "x"
    ::= { jnxJsSMS 1 }
END
""",
        encoding="utf-8",
    )
    comp = tmp_path / "compiled"
    comp.mkdir()
    s = Settings(mib_root=str(tmp_path), mib_compiled_root=str(comp))
    r = compile_mib_modules(s, ["JUNIPER-SMS-MIB"], rebuild=True)
    st, err, _ = r.get("JUNIPER-SMS-MIB", ("failed", "missing", None))
    assert st == "compiled", err
