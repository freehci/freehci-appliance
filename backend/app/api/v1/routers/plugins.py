"""Plugin-manifest for frontend og integrasjoner."""

from fastapi import APIRouter

from app.core.config import get_settings
from app.integrations.registry import registry
from app.schemas.plugin import PluginListResponse
from app.services.plugins import list_plugins

router = APIRouter(prefix="/plugins", tags=["plugins"])


@router.get("", response_model=PluginListResponse)
def list_plugin_manifests() -> PluginListResponse:
    settings = get_settings()
    return list_plugins(registry.plugins, api_v1_prefix=settings.api_v1_prefix)
