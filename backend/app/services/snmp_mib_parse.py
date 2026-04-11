"""Enkel uthenting av enterprise-nummer og modulnavn fra MIB-kildetekst."""

from __future__ import annotations

import re
from pathlib import Path

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
_MODULE_DEF_RE = re.compile(
    r"^([A-Za-z][A-Za-z0-9-]*)\s+DEFINITIONS\s*::=",
    re.MULTILINE,
)


def extract_enterprise_numbers(mib_text: str) -> list[int]:
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
    m = _MODULE_DEF_RE.search(mib_text)
    if m:
        return m.group(1)
    return Path(filename).stem
