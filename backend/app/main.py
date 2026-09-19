"""FastAPI entrypoint."""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from app.api.v1.router import api_router
from app.core.auth_middleware import ApiAuthMiddleware
from app.core.config import get_settings
from app.core.db import SessionLocal
from app.core.logging import setup_logging
from app.integrations.registry import registry
from app.services.auth_admin import ensure_default_admin

settings = get_settings()
setup_logging(settings.debug)

_OPENAPI_DESCRIPTION = """
Appliance API for DCIM, IPAM, IAM and integrations.

## Authentication

Send `Authorization: Bearer <token>` on `/api/v1` routes.

- **API token (recommended for agents):** create a token via the UI or `POST /api/v1/auth/tokens`. Tokens start with `fhci_`.
- **Login JWT:** `POST /api/v1/auth/login` with username and password, then use `access_token`.

Machine-readable connect info: `GET /api/v1/auth/agent` (no auth).

## IPAM (IPv4, GitOps)

- Look up prefixes: `GET /api/v1/ipam/ipv4-prefixes?cidr=` / `?slug=` / `?q=` / `?address=` / `?role=`
- Idempotent create: `POST /api/v1/ipam/ipv4-prefixes/ensure` (`site_id` + `vrf_id` + `cidr`). Lookup by default; `?update=true` applies desired state. Response includes `created`.
- Prefix `role` (`container|active|reserved|overlay-pod|overlay-service|lb-pool|p2p`) and `status` (`planned|active|reserved|deprecated`) are enforced on host alloc.
- VLAN/VRF: `GET`/`PATCH`/`POST .../ensure` on `/ipam/vlans` and `/ipam/vrfs`.
- Errors are `{code, detail}` so agents can match `prefix_has_children`, `gateway_protected`, `prefix_role_forbids_alloc`.
- Next child prefix: `GET /ipv4-prefixes/{id}/available-prefixes?prefixlen=` and `POST /ipv4-prefixes/{id}/allocate`. Idempotent on `slug` or `Idempotency-Key`.
- LB/pool ranges: `GET /ipv4-prefixes/{id}/available-ranges`. `address-grid` is 400 for prefixes larger than /22.
- `request` / `request-batch` are atomic and accept `Idempotency-Key`. Bind inventory IP: `POST /ipv4-addresses/{id}/bind`.
- Pin or allocate hosts: `POST /api/v1/ipam/ipv4-addresses/ensure` and `/request` (`mode=reserve|assign`, interface optional)
- Hard-delete address: `DELETE /api/v1/ipam/ipv4-addresses/{id}`
- Prefix delete is 409 if children or addresses exist; pass `?cascade=true` to remove them
"""


def _load_plugins() -> None:
    registry.load_builtin_module("app.plugins_builtin.example")
    registry.load_builtin_module("app.plugins_builtin.dell_idrac")
    registry.load_entry_points()
    registry.load_from_installed_directories(Path(settings.plugins_path))


@asynccontextmanager
async def lifespan(app: FastAPI):
    db = SessionLocal()
    try:
        ensure_default_admin(db)
    finally:
        db.close()

    registry.clear()
    _load_plugins()
    registry.mount_all(app, api_v1_prefix=settings.api_v1_prefix)
    yield


def create_app() -> FastAPI:
    api = settings.api_v1_prefix.rstrip("/")
    application = FastAPI(
        title=settings.app_name,
        description=_OPENAPI_DESCRIPTION,
        lifespan=lifespan,
        openapi_url=f"{api}/openapi.json",
        docs_url=f"{api}/docs",
        redoc_url=f"{api}/redoc",
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.add_middleware(ApiAuthMiddleware, settings=get_settings())
    application.include_router(api_router, prefix=settings.api_v1_prefix)

    def custom_openapi() -> dict:
        if application.openapi_schema:
            return application.openapi_schema
        schema = get_openapi(
            title=application.title,
            version=application.version or "0.1.0",
            description=application.description,
            routes=application.routes,
        )
        components = schema.setdefault("components", {})
        schemes = components.setdefault("securitySchemes", {})
        schemes["BearerAuth"] = {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT or API token",
            "description": "JWT from POST /api/v1/auth/login, or a long-lived API token (fhci_…).",
        }
        schema["security"] = [{"BearerAuth": []}]
        application.openapi_schema = schema
        return schema

    application.openapi = custom_openapi  # type: ignore[method-assign]
    return application


app = create_app()
