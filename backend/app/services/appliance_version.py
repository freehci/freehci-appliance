"""Sammenligning av appliance-versjon (lokal `.ver` vs GitHub)."""

from __future__ import annotations

from pathlib import Path

import httpx

DEFAULT_REMOTE_VER_URL = (
    "https://raw.githubusercontent.com/freehci/freehci-appliance/main/.ver"
)


def read_local_appliance_version(ver_file: Path) -> str | None:
    try:
        text = ver_file.read_text(encoding="utf-8")
    except OSError:
        return None
    v = text.strip()
    return v or None


def version_tuple(v: str) -> tuple[int, ...]:
    parts: list[int] = []
    for seg in v.strip().split("."):
        if not seg:
            continue
        digits = "".join(ch for ch in seg if ch.isdigit())
        parts.append(int(digits) if digits else 0)
    return tuple(parts)


def remote_is_newer(remote: str, local: str) -> bool:
    return version_tuple(remote) > version_tuple(local)


def fetch_remote_version(url: str, timeout: float = 10.0) -> tuple[str | None, str | None]:
    try:
        with httpx.Client(timeout=httpx.Timeout(timeout)) as c:
            r = c.get(url)
            r.raise_for_status()
        body = (r.text or "").strip()
        return (body or None, None)
    except Exception as e:
        return (None, str(e))
