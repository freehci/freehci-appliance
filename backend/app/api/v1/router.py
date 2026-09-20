from fastapi import APIRouter

from app.api.v1.routers import (
    auth,
    catalog,
    dcim,
    federation,
    health,
    iam,
    integration_connections,
    ipam,
    network_scan,
    platform,
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
api_router.include_router(federation.router)
api_router.include_router(integration_connections.router)
api_router.include_router(catalog.router)
api_router.include_router(platform.router)
api_router.include_router(platform.cloud_router)
