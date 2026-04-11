"""Hent og parse IANA Private Enterprise Numbers (enterprise-numbers.txt)."""

from __future__ import annotations

import httpx


IANA_ENTERPRISE_TXT_URL = "https://www.iana.org/assignments/enterprise-numbers/enterprise-numbers.txt"


def parse_enterprise_numbers_txt(content: str) -> list[tuple[int, str]]:
    """Returner (pen, organization) for hver post (4 linjer per post etter header)."""
    lines = content.splitlines()
    out: list[tuple[int, str]] = []
    i = 0
    while i + 3 < len(lines):
        dec = lines[i].strip()
        if not dec.isdigit():
            i += 1
            continue
        try:
            pen = int(dec)
        except ValueError:
            i += 1
            continue
        org = lines[i + 1].strip() if i + 1 < len(lines) else ""
        if len(org) > 1024:
            org = org[:1024]
        out.append((pen, org))
        i += 4
    return out


def fetch_iana_enterprise_rows(*, timeout_sec: float = 120.0) -> list[tuple[int, str]]:
    with httpx.Client(timeout=timeout_sec) as client:
        r = client.get(IANA_ENTERPRISE_TXT_URL)
        r.raise_for_status()
        return parse_enterprise_numbers_txt(r.text)
