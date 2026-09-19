"""Optimistic concurrency for IPAM: ETag fra updated_at + If-Match."""

from __future__ import annotations

import datetime as dt
from typing import Any

from fastapi import Response

from app.services.ipam_errors import ipam_error

EXPOSE_HEADERS = ("ETag", "Last-Modified", "X-Total-Count", "X-Offset", "X-Truncated")


def _utc(ts: dt.datetime | None) -> dt.datetime | None:
    if ts is None:
        return None
    if ts.tzinfo is None:
        return ts.replace(tzinfo=dt.UTC)
    return ts.astimezone(dt.UTC)


def etag_token(row: Any) -> str:
    ts = _utc(getattr(row, "updated_at", None)) or _utc(getattr(row, "created_at", None))
    stamp = ts.isoformat() if ts is not None else "0"
    return f"{getattr(row, 'id', 0)}-{stamp}"


def format_etag(row: Any) -> str:
    return f'W/"{etag_token(row)}"'


def last_modified(row: Any) -> str | None:
    ts = _utc(getattr(row, "updated_at", None)) or _utc(getattr(row, "created_at", None))
    if ts is None:
        return None
    return ts.strftime("%a, %d %b %Y %H:%M:%S GMT")


def _normalize_if_match(raw: str) -> str:
    s = raw.strip()
    if s.startswith("W/") or s.startswith("w/"):
        s = s[2:].strip()
    if len(s) >= 2 and s[0] == s[-1] == '"':
        s = s[1:-1]
    return s


def require_if_match(row: Any, if_match: str | None) -> None:
    """Utelatt If-Match = bakoverkompatibelt. Feil treff = 412."""
    if if_match is None or not if_match.strip() or if_match.strip() == "*":
        return
    got = _normalize_if_match(if_match)
    want = etag_token(row)
    ts = _utc(getattr(row, "updated_at", None))
    alt = ts.isoformat() if ts is not None else None
    if got not in {want, format_etag(row)} and got != alt:
        raise ipam_error(
            412,
            "precondition_failed",
            "If-Match matcher ikke gjeldende ETag",
            etag=format_etag(row),
        )


def attach_etag(response: Response, row: Any) -> None:
    response.headers["ETag"] = format_etag(row)
    lm = last_modified(row)
    if lm:
        response.headers["Last-Modified"] = lm


def attach_page(response: Response, *, total: int, offset: int, count: int) -> None:
    response.headers["X-Total-Count"] = str(total)
    response.headers["X-Offset"] = str(offset)
    truncated = offset + count < total
    response.headers["X-Truncated"] = "true" if truncated else "false"
