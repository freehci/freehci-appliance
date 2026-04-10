"""Krever Bearer-JWT for /api/v1 unntatt helse, innlogging og offentlige DCIM-bilder (GET)."""

from __future__ import annotations

import re

import jwt
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.core.config import Settings
from app.services.auth_admin import decode_token_payload


def _is_public_dcim_media_get(path: str, api_v1_prefix: str) -> bool:
    """GET av logo/bilder brukes i <img src>; nettleseren sender ikke Authorization."""
    api = api_v1_prefix.rstrip("/")
    return bool(
        re.fullmatch(rf"{re.escape(api)}/dcim/manufacturers/\d+/logo", path)
        or re.fullmatch(rf"{re.escape(api)}/dcim/device-models/\d+/image-front", path)
        or re.fullmatch(rf"{re.escape(api)}/dcim/device-models/\d+/image-back", path)
        or re.fullmatch(rf"{re.escape(api)}/dcim/device-models/\d+/image-product", path)
    )


class ApiAuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, settings: Settings) -> None:
        super().__init__(app)
        self.settings = settings

    async def dispatch(self, request: Request, call_next) -> Response:
        if self.settings.freehci_skip_auth:
            return await call_next(request)
        if request.method == "OPTIONS":
            return await call_next(request)

        api = self.settings.api_v1_prefix.rstrip("/")
        path = request.url.path
        if not path.startswith(f"{api}/"):
            return await call_next(request)

        if path.startswith(f"{api}/health"):
            return await call_next(request)
        if path == f"{api}/auth/login":
            return await call_next(request)
        if request.method == "GET" and _is_public_dcim_media_get(path, self.settings.api_v1_prefix):
            return await call_next(request)

        authz = request.headers.get("Authorization")
        if not authz or not authz.lower().startswith("bearer "):
            return JSONResponse({"detail": "mangler innlogging"}, status_code=401)
        token = authz[7:].strip()
        try:
            payload = decode_token_payload(token, self.settings)
        except jwt.ExpiredSignatureError:
            return JSONResponse({"detail": "innlogging utløpt"}, status_code=401)
        except jwt.InvalidTokenError:
            return JSONResponse({"detail": "ugyldig innlogging"}, status_code=401)

        try:
            sub = payload.get("sub")
            request.state.admin_id = int(sub) if sub is not None else None
        except (TypeError, ValueError):
            return JSONResponse({"detail": "ugyldig innlogging"}, status_code=401)

        if request.state.admin_id is None:
            return JSONResponse({"detail": "ugyldig innlogging"}, status_code=401)

        return await call_next(request)
