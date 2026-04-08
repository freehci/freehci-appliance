"""API-skjemaer for plugin-registrering."""

from pydantic import BaseModel, Field


class PluginCapability(BaseModel):
    """Funksjon pluginen tilbyr (koblet til fremtidige kjerne-løftekroker)."""

    id: str
    description: str = ""


class PluginManifestResponse(BaseModel):
    """Manifest eksponert til UI og andre tjenester."""

    id: str = Field(..., description="Stabil plugin-ID, f.eks. vendor.integrasjon")
    name: str
    version: str
    description: str = ""
    capabilities: list[PluginCapability] = Field(default_factory=list)
    # Frontend: valgfritt modul-URL (ESM) eller tom for innebygde ruter
    frontend_module_url: str | None = None
    # React-router sti-prefix som kjerne eller plugin eier
    frontend_route_prefix: str | None = None
    # FastAPI-prefix for denne pluginens API
    api_route_prefix: str | None = None


class PluginListResponse(BaseModel):
    plugins: list[PluginManifestResponse]
