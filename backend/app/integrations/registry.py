"""Oppdager og holder backend-plugins (entry points + innebygde)."""

from __future__ import annotations

import importlib
import logging
from importlib import metadata
from typing import TYPE_CHECKING

from app.integrations.base.plugin import BackendPlugin, PluginManifest

if TYPE_CHECKING:
    from fastapi import FastAPI

log = logging.getLogger(__name__)

_ENTRY_GROUP = "freehci.backend_plugins"


class PluginRegistry:
    def __init__(self) -> None:
        self._plugins: dict[str, BackendPlugin] = {}

    def clear(self) -> None:
        self._plugins.clear()

    @property
    def plugins(self) -> tuple[BackendPlugin, ...]:
        return tuple(self._plugins.values())

    def manifests(self) -> tuple[PluginManifest, ...]:
        return tuple(p.manifest for p in self._plugins.values())

    def register(self, plugin: BackendPlugin) -> None:
        pid = plugin.manifest.id
        if pid in self._plugins:
            log.warning("Plugin %s overstyrer tidligere registrering", pid)
        self._plugins[pid] = plugin

    def load_entry_points(self) -> None:
        try:
            eps = metadata.entry_points(group=_ENTRY_GROUP)
        except TypeError:
            eps = metadata.entry_points().get(_ENTRY_GROUP, ())
        for ep in eps:
            try:
                loaded = ep.load()
                if isinstance(loaded, BackendPlugin):
                    self.register(loaded)
                elif callable(loaded):
                    candidate = loaded()
                    if isinstance(candidate, BackendPlugin):
                        self.register(candidate)
            except Exception:
                log.exception("Kunne ikke laste plugin entry point %s", ep.name)

    def load_builtin_module(self, module_path: str) -> None:
        mod = importlib.import_module(module_path)
        plugin = getattr(mod, "plugin", None)
        if isinstance(plugin, BackendPlugin):
            self.register(plugin)

    def mount_all(self, app: FastAPI, *, api_v1_prefix: str) -> None:
        base = f"{api_v1_prefix.rstrip('/')}/plugins"
        for plugin in self._plugins.values():
            plugin.register_routes(app, api_prefix=base)


registry = PluginRegistry()
