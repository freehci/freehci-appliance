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
                # Stub-kontrakter for DCIM-enhetsdetalj (ekte hardware: f.eks. dell.idrac)
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

        @router.get("/devices/{device_id}/hardware")
        def device_hardware(device_id: int) -> dict[str, object]:
            """Stub: ekte hardware-agenter (f.eks. iDRAC) erstatter dette i produksjon."""
            return {
                "plugin_id": "freehci.example",
                "device_id": device_id,
                "kind": "hardware_stub",
                "message": "Placeholder until a hardware inventory integration is implemented.",
            }

        @router.get("/devices/{device_id}/os")
        def device_os(device_id: int) -> dict[str, object]:
            """Stub: ekte OS-agenter kan returnere OS-navn, versjon, hostname, …"""
            return {
                "plugin_id": "freehci.example",
                "device_id": device_id,
                "kind": "os_stub",
                "message": "Placeholder until an OS inventory integration is implemented.",
                "fields": {
                    "os_name": None,
                    "os_version": None,
                    "hostname": None,
                },
            }

        return router


plugin = ExamplePlugin()
