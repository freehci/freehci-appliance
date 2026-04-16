"""Oppdager og holder backend-plugins (entry points + innebygde)."""

from __future__ import annotations

import importlib
import importlib.util
import logging
import sys
from importlib import metadata
from pathlib import Path
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

    def load_from_installed_directories(self, plugins_root: Path) -> None:
        """Last dynamiske plugins fra ``<plugins_root>/installed/<slug>/plugin.py``."""
        installed = plugins_root.expanduser().resolve() / "installed"
        if not installed.is_dir():
            return
        for child in sorted(installed.iterdir()):
            if not child.is_dir():
                continue
            plugin_file = child / "plugin.py"
            if not plugin_file.is_file():
                log.debug("Hopper over plugin-mappe uten plugin.py: %s", child)
                continue
            modname = f"freehci_dynamic_plugin_{child.name.replace('.', '_').replace('-', '_')}"
            dir_s = str(child.resolve())
            inserted = False
            try:
                if dir_s not in sys.path:
                    sys.path.insert(0, dir_s)
                    inserted = True
                spec = importlib.util.spec_from_file_location(modname, plugin_file)
                if spec is None or spec.loader is None:
                    log.warning("Kunne ikke lage import-spec for %s", plugin_file)
                    continue
                mod = importlib.util.module_from_spec(spec)
                sys.modules[modname] = mod
                spec.loader.exec_module(mod)
                plugin = getattr(mod, "plugin", None)
                if isinstance(plugin, BackendPlugin):
                    self.register(plugin)
                    log.info("Lastet dynamisk plugin fra %s", child)
                else:
                    log.warning("Fil %s mangler «plugin» av type BackendPlugin", plugin_file)
            except Exception:
                log.exception("Feil ved lasting av dynamisk plugin %s", child)
            finally:
                if inserted and dir_s in sys.path:
                    sys.path.remove(dir_s)

    def mount_all(self, app: FastAPI, *, api_v1_prefix: str) -> None:
        base = f"{api_v1_prefix.rstrip('/')}/plugins"
        for plugin in self._plugins.values():
            plugin.register_routes(app, api_prefix=base)


registry = PluginRegistry()
