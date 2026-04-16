"""Dell PowerEdge iDRAC via Redfish (out-of-band)."""

from __future__ import annotations

import logging

import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_db
from app.core.config import Settings, get_settings
from app.integrations.base.plugin import BackendPlugin, PluginManifest
from app.models.dcim import DeviceInstance, DeviceInterface
from app.services import dell_idrac_redfish as idrac_rf
from app.services import oob_device as oob

log = logging.getLogger(__name__)


def _load_device(db: Session, device_id: int) -> DeviceInstance | None:
    return db.execute(
        select(DeviceInstance)
        .where(DeviceInstance.id == device_id)
        .options(
            selectinload(DeviceInstance.interfaces).selectinload(DeviceInterface.ip_assignments),
            selectinload(DeviceInstance.device_ip_assignments),
        ),
    ).scalar_one_or_none()


class DellIdracPlugin(BackendPlugin):
    @property
    def manifest(self) -> PluginManifest:
        return PluginManifest(
            id="dell.idrac",
            name="Dell iDRAC (Redfish)",
            version="0.1.0",
            description="Henter maskinvarestatus fra iDRAC på PowerEdge via Redfish.",
            capabilities=("dcim.device.hardware_view",),
            frontend_module_url=None,
            frontend_route_prefix="/plugins/dell.idrac",
            device_type_slugs=("server",),
        )

    def get_router(self) -> APIRouter:
        router = APIRouter()

        @router.get("/devices/{device_id}/hardware")
        def device_hardware(
            device_id: int,
            db: Session = Depends(get_db),
            settings: Settings = Depends(get_settings),
        ) -> dict[str, object]:
            dev = _load_device(db, device_id)
            if dev is None:
                raise HTTPException(status_code=404, detail="enhet ikke funnet")
            host = oob.resolve_oob_management_host(dev)
            if not host:
                raise HTTPException(
                    status_code=400,
                    detail="Mangler OOB-vert: sett attributes.idrac_host (eller bmc_host), "
                    "eller legg IPv4 på et grensesnitt med «idrac»/«bmc» i navnet, "
                    "eller primær enhets-IPv4.",
                )
            user, password = oob.resolve_idrac_credentials(dev)
            if not user or not password:
                raise HTTPException(
                    status_code=400,
                    detail="Mangler iDRAC-legitimasjon: sett attributes.idrac_username og attributes.idrac_password.",
                )
            try:
                fields = idrac_rf.fetch_idrac_hardware_summary(
                    host,
                    user,
                    password,
                    verify_tls=settings.idrac_redfish_tls_verify,
                )
            except httpx.HTTPStatusError as e:
                log.warning("iDRAC Redfish HTTP-feil for enhet %s: %s", device_id, e)
                raise HTTPException(
                    status_code=502,
                    detail=f"iDRAC svarte med HTTP {e.response.status_code}",
                ) from e
            except Exception as e:
                log.exception("iDRAC Redfish feilet for enhet %s", device_id)
                raise HTTPException(status_code=502, detail=f"Kunne ikke nå iDRAC: {e!s}") from e

            return {
                "plugin_id": "dell.idrac",
                "device_id": device_id,
                "kind": "idrac_redfish",
                "oob_host": host,
                "fields": fields,
            }

        return router


plugin = DellIdracPlugin()
