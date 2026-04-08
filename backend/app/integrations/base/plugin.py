"""Backend plugin-kontrakt.

En plugin kan:
- registrere egne API-routere under et prefix
- eksponere manifest med frontend-metadata (modul-URL og rute-prefix)
- koble seg på livssyklus via register()/startup hooks (utvid senere)
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastapi import APIRouter, FastAPI


@dataclass(frozen=True)
class PluginManifest:
    id: str
    name: str
    version: str
    description: str = ""
    capabilities: tuple[str, ...] = ()
    # Hvis satt: last inn frontend via import() / ESM fra denne URL-en i React-shell
    frontend_module_url: str | None = None
    frontend_route_prefix: str | None = None


class BackendPlugin(ABC):
    """Grunnleggende backend-plugin."""

    @property
    @abstractmethod
    def manifest(self) -> PluginManifest:
        ...

    def register_routes(self, app: FastAPI, *, api_prefix: str) -> None:
        """Registrer HTTP-endepunkter. Standard: ingen ruter."""
        router = self.get_router()
        if router is not None:
            prefix = f"{api_prefix.rstrip('/')}/{self.manifest.id.replace('.', '/')}"
            app.include_router(router, prefix=prefix, tags=[f"plugin:{self.manifest.id}"])

    def get_router(self) -> APIRouter | None:
        return None
