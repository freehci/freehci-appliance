from fastapi import APIRouter

from app.api.v1.routers import (
    auth,
    dcim,
    health,
    iam,
    ipam,
    network_scan,
    plugin_install,
    plugins,
    snmp,
    system_update,
    tenants,
)

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(iam.router)
api_router.include_router(tenants.router)
api_router.include_router(plugins.router)
api_router.include_router(plugin_install.router)
api_router.include_router(dcim.router)
api_router.include_router(ipam.router)
api_router.include_router(system_update.router)
api_router.include_router(network_scan.router)
api_router.include_router(snmp.router)
