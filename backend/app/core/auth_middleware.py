"""Krever Bearer-JWT eller API-nøkkel for /api/v1 unntatt helse, innlogging og offentlige stier."""

from __future__ import annotations

import re

import jwt
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.core.config import Settings
from app.core.db import SessionLocal
from app.core.request_context import AuthActor, ipam_scope_allows, set_actor
from app.services.auth_admin import API_TOKEN_PREFIX, authenticate_api_token, decode_token_payload


def _is_public_dcim_media_get(path: str, api_v1_prefix: str) -> bool:
    """GET av logo/bilder brukes i <img src>; nettleseren sender ikke Authorization."""
    api = api_v1_prefix.rstrip("/")
    return bool(
        re.fullmatch(rf"{re.escape(api)}/dcim/manufacturers/\d+/logo", path)
        or re.fullmatch(rf"{re.escape(api)}/dcim/device-models/\d+/image-front", path)
        or re.fullmatch(rf"{re.escape(api)}/dcim/device-models/\d+/image-back", path)
        or re.fullmatch(rf"{re.escape(api)}/dcim/device-models/\d+/image-product", path)
        or re.fullmatch(rf"{re.escape(api)}/iam/persons/\d+/avatar", path)
    )


class ApiAuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, settings: Settings) -> None:
        super().__init__(app)
        self.settings = settings

    async def dispatch(self, request: Request, call_next) -> Response:
        if self.settings.freehci_skip_auth:
            set_actor(AuthActor(actor_type="system", actor_name="test"))
            return await call_next(request)
        if request.method == "OPTIONS":
            return await call_next(request)

        api = self.settings.api_v1_prefix.rstrip("/")
        path = request.url.path
        if not path.startswith(f"{api}/"):
            return await call_next(request)

        if path.startswith(f"{api}/health"):
            return await call_next(request)
        if path == f"{api}/auth/login" or path == f"{api}/auth/agent":
            return await call_next(request)
        if path in {f"{api}/openapi.json", f"{api}/docs", f"{api}/redoc"} or path.startswith(f"{api}/docs/"):
            return await call_next(request)
        if request.method == "GET" and _is_public_dcim_media_get(path, self.settings.api_v1_prefix):
            return await call_next(request)

        authz = request.headers.get("Authorization")
        if not authz or not authz.lower().startswith("bearer "):
            return JSONResponse({"detail": "mangler innlogging"}, status_code=401)
        token = authz[7:].strip()

        if token.startswith(API_TOKEN_PREFIX):
            db = SessionLocal()
            try:
                row = authenticate_api_token(db, token)
                if row is None:
                    admin_id = token_id = None
                    token_name = None
                    scopes = None
                else:
                    admin_id = row.admin_id
                    token_id = row.id
                    token_name = row.name
                    raw_scopes = getattr(row, "scopes", None) or []
                    scopes = frozenset(str(s) for s in raw_scopes) if raw_scopes else None
            finally:
                db.close()
            if token_id is None:
                return JSONResponse({"detail": "ugyldig innlogging"}, status_code=401)
            request.state.admin_id = admin_id
            set_actor(
                AuthActor(
                    actor_type="token",
                    actor_id=token_id,
                    actor_name=token_name,
                    scopes=scopes,
                    token_id=token_id,
                ),
            )
            denied = _deny_ipam_scope(request, scopes)
            if denied is not None:
                return denied
            return await call_next(request)

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

        set_actor(AuthActor(actor_type="admin", actor_id=request.state.admin_id, actor_name="admin"))
        return await call_next(request)


def _deny_ipam_scope(request: Request, scopes: frozenset[str] | None) -> JSONResponse | None:
    path = request.url.path
    if "/ipam/" not in path:
        return None
    if ipam_scope_allows(request.method, path, scopes):
        return None
    return JSONResponse(
        {"detail": {"code": "insufficient_scope", "detail": "API-nøkkelen mangler nødvendig IPAM-scope"}},
        status_code=403,
    )
