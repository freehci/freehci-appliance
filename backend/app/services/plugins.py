"""Mapping domain → API-responser for plugins."""

from app.integrations.base.plugin import BackendPlugin, PluginManifest
from app.schemas.plugin import PluginCapability, PluginListResponse, PluginManifestResponse


def manifest_to_response(m: PluginManifest, api_route_prefix: str | None = None) -> PluginManifestResponse:
    caps = [PluginCapability(id=c, description="") for c in m.capabilities]
    return PluginManifestResponse(
        id=m.id,
        name=m.name,
        version=m.version,
        description=m.description,
        capabilities=caps,
        frontend_module_url=m.frontend_module_url,
        frontend_route_prefix=m.frontend_route_prefix,
        api_route_prefix=api_route_prefix,
    )


def list_plugins(plugins: tuple[BackendPlugin, ...], *, api_v1_prefix: str) -> PluginListResponse:
    items: list[PluginManifestResponse] = []
    base = f"{api_v1_prefix.rstrip('/')}/plugins"
    for p in plugins:
        m = p.manifest
        prefix = f"{base}/{m.id.replace('.', '/')}"
        items.append(manifest_to_response(m, api_route_prefix=prefix))
    return PluginListResponse(plugins=items)
