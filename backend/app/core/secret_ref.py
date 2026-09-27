"""Referanser til hemmeligheter — aldri nøkkelmateriale."""

from __future__ import annotations

import re

_REF = re.compile(r"^secret:[A-Za-z0-9._:/-]{1,200}$")


def is_secret_ref(value: str | None) -> bool:
    if value is None:
        return False
    return bool(_REF.match(value.strip()))


def normalize_secret_ref(value: str | None) -> str | None:
    if value is None:
        return None
    s = value.strip()
    if not s:
        return None
    if _REF.match(s):
        return s
    raise ValueError("nøkkel må være referanse (secret:…) — nøkkelmateriale lagres ikke")
