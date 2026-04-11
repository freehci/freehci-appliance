"""Enhetstester for MIB-parsing og IANA enterprise-numbers.txt."""

from app.services.snmp_iana import parse_enterprise_numbers_txt
from app.services.snmp_mib_parse import (
    extract_enterprise_numbers,
    guess_module_name,
    imported_mib_modules,
    imported_vendor_mib_modules,
    primary_enterprise_number,
)


def test_extract_enterprise_from_braces() -> None:
    text = "foo OBJECT IDENTIFIER ::= { enterprises 9 }\n"
    assert extract_enterprise_numbers(text) == [9]
    assert primary_enterprise_number(text) == 9


def test_extract_enterprise_from_numeric_oid() -> None:
    text = "  oid ::= { 1 3 6 1 4 1 2636 1 }\n"
    assert 2636 in extract_enterprise_numbers(text)


def test_guess_module_name_from_definitions() -> None:
    src = "MY-CUSTOM-MIB DEFINITIONS ::= BEGIN\nEND\n"
    assert guess_module_name("x.mib", src) == "MY-CUSTOM-MIB"


def test_imported_mib_modules_order() -> None:
    src = """
FOO DEFINITIONS ::= BEGIN
IMPORTS
    a FROM SNMPv2-SMI
    b FROM CISCO-SMI;
END
"""
    assert imported_mib_modules(src) == ["SNMPv2-SMI", "CISCO-SMI"]
    assert imported_vendor_mib_modules(src) == ["CISCO-SMI"]


def test_parse_iana_txt_minimal() -> None:
    sample = """Decimal
| Organization
0
 Reserved
 IANA
 x@y
1
 Acme
 Bob
 bob@acme
"""
    rows = parse_enterprise_numbers_txt(sample)
    assert (0, "Reserved") in rows
    assert (1, "Acme") in rows
