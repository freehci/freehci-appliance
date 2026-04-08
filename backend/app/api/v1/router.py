from fastapi import APIRouter

from app.api.v1.routers import dcim, health, ipam, plugins

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(plugins.router)
api_router.include_router(dcim.router)
api_router.include_router(ipam.router)
