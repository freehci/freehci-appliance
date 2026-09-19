"""Maskinbare IPAM-feil: FastAPI detail = {code, detail, ...}."""

from __future__ import annotations

from typing import Any

from fastapi import HTTPException


def ipam_error(status: int, code: str, detail: str, **extra: Any) -> HTTPException:
    payload: dict[str, Any] = {"code": code, "detail": detail}
    payload.update(extra)
    return HTTPException(status_code=status, detail=payload)


def error_code(exc: HTTPException) -> str | None:
    d = exc.detail
    if isinstance(d, dict):
        raw = d.get("code")
        return str(raw) if raw is not None else None
    return None
