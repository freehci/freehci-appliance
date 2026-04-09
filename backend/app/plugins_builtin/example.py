"""Eksempel-plugin: viser router-registrering og manifest for frontend."""

from fastapi import APIRouter

from app.integrations.base.plugin import BackendPlugin, PluginManifest


class ExamplePlugin(BackendPlugin):
    @property
    def manifest(self) -> PluginManifest:
        return PluginManifest(
            id="freehci.example",
            name="Eksempel-plugin",
            version="0.1.0",
            description="Demonstrerer plugin-API og samspill med React.",
            capabilities=(
                "demo.ping",
                # Reserverte kontrakter for DCIM-enhetsdetalj (UI kobles senere)
                "dcim.device.hardware_view",
                "dcim.device.os_view",
            ),
            frontend_module_url=None,
            frontend_route_prefix="/plugins/freehci.example",
            device_type_slugs=("server",),
        )

    def get_router(self) -> APIRouter:
        router = APIRouter()

        @router.get("/hello")
        def hello() -> dict[str, str]:
            return {"message": "Hello from freehci.example backend plugin"}

        return router


plugin = ExamplePlugin()
