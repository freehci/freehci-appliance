"""SNMP: MIB-opplasting og enkel SNMPv2c-probe."""

from __future__ import annotations

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session
from starlette.responses import Response

from app.api.deps import get_db
from app.core.config import Settings, get_settings
from app.schemas.snmp import (
    SnmpInventoryApplyRead,
    SnmpInventoryApplyRequest,
    SnmpInventoryRead,
    SnmpInventoryRequest,
    SnmpMibFileRead,
    SnmpProbeRead,
    SnmpProbeRequest,
    SnmpScanRead,
    SnmpScanRequest,
)
from app.services import snmp_interface_import as iface_import_svc
from app.services import snmp_inventory as inv_svc
from app.services import snmp_scan as scan_svc
from app.services import snmp_mibs as mib_svc
from app.services import snmp_probe as probe_svc

router = APIRouter(prefix="/snmp", tags=["snmp"])


@router.get("/mibs", response_model=list[SnmpMibFileRead])
def list_mibs(settings: Settings = Depends(get_settings)) -> list[SnmpMibFileRead]:
    rows = mib_svc.list_mib_files(settings)
    return [SnmpMibFileRead.model_validate(r) for r in rows]


@router.post("/mibs", response_model=SnmpMibFileRead)
async def upload_mib(
    file: UploadFile = File(...),
    settings: Settings = Depends(get_settings),
) -> SnmpMibFileRead:
    raw = await file.read()
    row = mib_svc.save_mib_file(settings, file.filename or "upload.mib", raw)
    return SnmpMibFileRead.model_validate(row)


@router.delete("/mibs/{name}")
def delete_mib(name: str, settings: Settings = Depends(get_settings)) -> Response:
    mib_svc.delete_mib_file(settings, name)
    return Response(status_code=204)


@router.post("/probe", response_model=SnmpProbeRead)
async def snmp_probe(data: SnmpProbeRequest) -> SnmpProbeRead:
    """SNMPv2c GET eller bulk walk. Bruk numerisk OID for pålitelig resultat uten kompilerte MIB-er."""
    return await probe_svc.run_snmp_probe(
        host=data.host.strip(),
        port=data.port,
        community=data.community,
        oid=data.oid.strip(),
        operation=data.operation,
        max_oids=data.max_oids,
        timeout_sec=data.timeout_sec,
        retries=data.retries,
    )


@router.post("/inventory", response_model=SnmpInventoryRead)
async def snmp_inventory(data: SnmpInventoryRequest) -> SnmpInventoryRead:
    """Hent sysName/sysDescr og IF-MIB/ifX-grensesnitt (SNMPv2c)."""
    return await inv_svc.collect_interface_inventory(
        host=data.host.strip(),
        port=data.port,
        community=data.community,
        timeout_sec=data.timeout_sec,
        retries=data.retries,
        max_varbinds=data.max_varbinds,
    )


@router.post("/scan", response_model=SnmpScanRead)
async def snmp_scan(data: SnmpScanRequest) -> SnmpScanRead:
    """Utvidet skanning: grensesnitt, IPv4 (ipAddrTable) og VLAN (BRIDGE/Q-BRIDGE) der støttet."""
    return await scan_svc.collect_full_scan(
        host=data.host.strip(),
        port=data.port,
        community=data.community,
        timeout_sec=data.timeout_sec,
        retries=data.retries,
        max_varbinds=data.max_varbinds,
    )


@router.post("/inventory/apply", response_model=SnmpInventoryApplyRead)
async def snmp_inventory_apply(
    data: SnmpInventoryApplyRequest,
    db: Session = Depends(get_db),
) -> SnmpInventoryApplyRead:
    """Én SNMP-poll og oppdater DCIM-grensesnitt på enheten (match på navn)."""
    return await iface_import_svc.apply_interface_inventory(
        db,
        device_id=data.device_id,
        host=data.host.strip(),
        port=data.port,
        community=data.community,
        timeout_sec=data.timeout_sec,
        retries=data.retries,
        max_varbinds=data.max_varbinds,
    )
