"""Enkel uthenting av enterprise-nummer og modulnavn fra MIB-kildetekst."""

from __future__ import annotations

import re
from pathlib import Path

from app.services.snmp_mib_index import extract_module_name_from_mib_text

_ENTERPRISES_BRACE_RE = re.compile(r"\{\s*enterprises\s+(\d+)\s*\}", re.IGNORECASE)
_OID_ENTERPRISE_RE = re.compile(
    r"1\s*\.\s*3\s*\.\s*6\s*\.\s*1\s*\.\s*4\s*\.\s*1\s*\.\s*(\d+)",
    re.IGNORECASE,
)
# ASN.1 «subidentifiers»: { 1 3 6 1 4 1 2636 ... }
_OID_ENTERPRISE_BRACE_RE = re.compile(
    r"\{\s*1\s+3\s+6\s+1\s+4\s+1\s+(\d+)",
    re.IGNORECASE,
)
def _strip_mib_bom(mib_text: str) -> str:
    """Fjern UTF-8 BOM slik at DEFINITIONS-regex treffer første linje."""
    return mib_text.lstrip("\ufeff")


_FROM_MODULE_RE = re.compile(r"\bFROM\s+([A-Za-z][A-Za-z0-9-]*)\b")

# Vanlige IETF/infra-MIB-moduler — ikke brukt som «vendor-parent» for tre under enterprise.
_STD_IMPORT_MIBS = frozenset(
    {
        "SNMPv2-SMI",
        "SNMPv2-TC",
        "SNMPv2-CONF",
        "SNMPv2-TM",
        "SNMPv2-MIB",
        "SNMP-FRAMEWORK-MIB",
        "SNMP-TARGET-MIB",
        "SNMP-NOTIFICATION-MIB",
        "SNMP-COMMUNITY-MIB",
        "SNMP-USER-BASED-SM-MIB",
        "SNMP-VIEW-BASED-ACM-MIB",
        "IANAifType-MIB",
        "IANA-ADDRESS-FAMILY-NUMBERS-MIB",
        "INET-ADDRESS-MIB",
        "IP-MIB",
        "IF-MIB",
        "TCP-MIB",
        "UDP-MIB",
        "ENTITY-MIB",
        "ENTITY-SENSOR-MIB",
        "TRANSPORT-ADDRESS-MIB",
        "RFC1213-MIB",
        "RFC-1212",
        "RFC1212",
        "RFC1155-SMI",
        "RFC1158-MIB",
        "RFC1065-SMI",
        "BRIDGE-MIB",
        "Q-BRIDGE-MIB",
        "VLAN-TC-MIB",
        "DIFFSERV-DSCP-TC",
        "HC-TC-100MBPS-TM",
        "HCNUM-TC",
        "PerfHist-TC-MIB",
        "ATM-TC-MIB",
        "ATM-MIB",
        "SNMP-USM-DH-OBJECTS-MIB",
        "ASN1",
        "ASN1-ENUMERATION",
        "ASN1-REFINEMENT",
    },
)


def extract_enterprise_numbers(mib_text: str) -> list[int]:
    mib_text = _strip_mib_bom(mib_text)
    pens: set[int] = set()
    for m in _ENTERPRISES_BRACE_RE.finditer(mib_text):
        pens.add(int(m.group(1)))
    for m in _OID_ENTERPRISE_RE.finditer(mib_text):
        pens.add(int(m.group(1)))
    for m in _OID_ENTERPRISE_BRACE_RE.finditer(mib_text):
        pens.add(int(m.group(1)))
    return sorted(pens)


def primary_enterprise_number(mib_text: str) -> int | None:
    pens = extract_enterprise_numbers(mib_text)
    return pens[0] if pens else None


def guess_module_name(filename: str, mib_text: str) -> str:
    mib_text = _strip_mib_bom(mib_text)
    mod = extract_module_name_from_mib_text(mib_text)
    if mod:
        return mod
    return Path(filename).stem


def imported_mib_modules(mib_text: str) -> list[str]:
    """Modulnavn fra «FROM Modul» i IMPORTS (rekkefølge bevart, unike)."""
    mib_text = _strip_mib_bom(mib_text)
    seen: set[str] = set()
    out: list[str] = []
    for m in _FROM_MODULE_RE.finditer(mib_text):
        name = m.group(1)
        if name not in seen:
            seen.add(name)
            out.append(name)
    return out


def imported_vendor_mib_modules(mib_text: str) -> list[str]:
    """IMPORTS minus typiske standard-/infra-MIB-er (kandidater for vendor-parent)."""
    return [x for x in imported_mib_modules(mib_text) if x not in _STD_IMPORT_MIBS]
