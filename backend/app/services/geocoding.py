"""Geokoding (adresse → lat/lon) for DCIM Sites.

Fase 1: offentlig Nominatim (OpenStreetMap). Dette er best-effort og bør byttes
til egen instans eller provider senere.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx


@dataclass(frozen=True)
class GeocodeCandidate:
    display_name: str
    latitude: float
    longitude: float


def build_site_query(parts: dict[str, str | None]) -> str:
    seq = [
        parts.get("address_line1"),
        parts.get("address_line2"),
        parts.get("postal_code"),
        parts.get("city"),
        parts.get("county"),
        parts.get("country"),
    ]
    out = [str(x).strip() for x in seq if isinstance(x, str) and x.strip()]
    return ", ".join(out)


def geocode_nominatim(query: str, *, limit: int = 5, timeout_s: float = 20.0) -> list[GeocodeCandidate]:
    q = (query or "").strip()
    if not q:
        return []
    lim = max(1, min(int(limit), 10))
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": q, "format": "jsonv2", "limit": str(lim), "addressdetails": "0"}
    headers = {"User-Agent": "FreeHCI/0.1 (DCIM geocode)"}
    with httpx.Client(timeout=timeout_s, headers=headers) as client:
        r = client.get(url, params=params)
        r.raise_for_status()
        data = r.json()
    if not isinstance(data, list):
        return []
    out: list[GeocodeCandidate] = []
    for row in data:
        if not isinstance(row, dict):
            continue
        dn = row.get("display_name")
        lat = row.get("lat")
        lon = row.get("lon")
        if not isinstance(dn, str) or not dn.strip():
            continue
        try:
            lf = float(lat)
            gf = float(lon)
        except Exception:
            continue
        out.append(GeocodeCandidate(display_name=dn.strip(), latitude=lf, longitude=gf))
    return out

