"""FastAPI entrypoint."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.logging import setup_logging
from app.integrations.registry import registry

settings = get_settings()
setup_logging(settings.debug)


def _load_plugins() -> None:
    registry.load_builtin_module("app.plugins_builtin.example")
    registry.load_entry_points()


@asynccontextmanager
async def lifespan(app: FastAPI):
    registry.clear()
    _load_plugins()
    registry.mount_all(app, api_v1_prefix=settings.api_v1_prefix)
    yield


def create_app() -> FastAPI:
    application = FastAPI(
        title=settings.app_name,
        lifespan=lifespan,
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.include_router(api_router, prefix=settings.api_v1_prefix)
    return application


app = create_app()
