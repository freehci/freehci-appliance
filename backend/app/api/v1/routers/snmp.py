"""SNMP: MIB-bibliotek, kompilering, IANA enterprise og SNMPv2c-verktøy."""

from __future__ import annotations

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session
from starlette.responses import Response

from app.api.deps import get_db
from app.core.config import Settings, get_settings
from app.schemas.snmp import (
    SnmpEnterpriseAutocreateRequest,
    SnmpEnterpriseAutocreateResultRead,
    SnmpEnterpriseGroupRead,
    SnmpIanaSyncRead,
    SnmpInventoryApplyRead,
    SnmpInventoryApplyRequest,
    SnmpInventoryRead,
    SnmpInventoryRequest,
    SnmpMibDetailRead,
    SnmpMibFileRead,
    SnmpProbeRead,
    SnmpProbeRequest,
    SnmpScanRead,
    SnmpScanRequest,
)
from app.services import snmp_interface_import as iface_import_svc
from app.services import snmp_inventory as inv_svc
from app.services import snmp_mib_catalog as mib_cat_svc
from app.services import snmp_mibs as mib_disk_svc
from app.services import snmp_scan as scan_svc
from app.services import snmp_probe as probe_svc

router = APIRouter(prefix="/snmp", tags=["snmp"])

_MAX_BATCH_FILES = 50


@router.get("/mibs/detailed", response_model=list[SnmpMibDetailRead])
def list_mibs_detailed(
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> list[SnmpMibDetailRead]:
    rows = mib_cat_svc.list_mibs_detailed(db, settings)
    return [SnmpMibDetailRead.model_validate(r) for r in rows]


@router.get("/enterprises", response_model=list[SnmpEnterpriseGroupRead])
def list_snmp_enterprises(
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> list[SnmpEnterpriseGroupRead]:
    rows = mib_cat_svc.list_enterprise_groups(db, settings)
    return [SnmpEnterpriseGroupRead.model_validate(r) for r in rows]


@router.post("/enterprises/autocreate-dcim", response_model=SnmpEnterpriseAutocreateResultRead)
def snmp_enterprises_autocreate_dcim(
    data: SnmpEnterpriseAutocreateRequest,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> SnmpEnterpriseAutocreateResultRead:
    r = mib_cat_svc.autocreate_dcim_manufacturers(
        db,
        settings,
        enterprise_number=data.enterprise_number,
    )
    return SnmpEnterpriseAutocreateResultRead.model_validate(r)


@router.post("/iana/sync", response_model=SnmpIanaSyncRead)
def sync_iana_enterprises(db: Session = Depends(get_db)) -> SnmpIanaSyncRead:
    n = mib_cat_svc.sync_iana_enterprises(db)
    return SnmpIanaSyncRead(rows_imported=n)


@router.post("/mibs/batch", response_model=list[SnmpMibDetailRead])
async def upload_mibs_batch(
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
    files: list[UploadFile] = File(...),
) -> list[SnmpMibDetailRead]:
    if not files:
        raise HTTPException(status_code=400, detail="ingen filer")
    if len(files) > _MAX_BATCH_FILES:
        raise HTTPException(status_code=400, detail=f"maks {_MAX_BATCH_FILES} filer per opplasting")
    saved: list[str] = []
    for f in files:
        raw = await f.read()
        row = mib_disk_svc.save_mib_file(settings, f.filename or "upload.mib", raw)
        mib_cat_svc.upsert_mib_meta(db, row["name"], raw)
        saved.append(row["name"])
    disk_rows = {r["name"]: r for r in mib_disk_svc.list_mib_files(settings)}
    return [
        SnmpMibDetailRead.model_validate(mib_cat_svc.mib_detail_dict(db, settings, disk_rows[n]))
        for n in saved
    ]


@router.get("/mibs", response_model=list[SnmpMibFileRead])
def list_mibs(settings: Settings = Depends(get_settings)) -> list[SnmpMibFileRead]:
    rows = mib_disk_svc.list_mib_files(settings)
    return [SnmpMibFileRead.model_validate(r) for r in rows]


@router.post("/mibs", response_model=SnmpMibFileRead)
async def upload_mib(
    db: Session = Depends(get_db),
    file: UploadFile = File(...),
    settings: Settings = Depends(get_settings),
) -> SnmpMibFileRead:
    raw = await file.read()
    row = mib_disk_svc.save_mib_file(settings, file.filename or "upload.mib", raw)
    mib_cat_svc.upsert_mib_meta(db, row["name"], raw)
    return SnmpMibFileRead.model_validate(row)


@router.post("/mibs/{name}/compile", response_model=SnmpMibDetailRead)
def compile_mib(
    name: str,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> SnmpMibDetailRead:
    row = mib_cat_svc.compile_mib_file(db, settings, name)
    return SnmpMibDetailRead.model_validate(row)


@router.post("/mibs/compile-all", response_model=list[SnmpMibDetailRead])
def compile_all_mibs(
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> list[SnmpMibDetailRead]:
    rows = mib_cat_svc.compile_all_mibs(db, settings)
    return [SnmpMibDetailRead.model_validate(r) for r in rows]


@router.delete("/mibs/{name}", status_code=204)
def delete_mib(
    name: str,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> Response:
    mib_cat_svc.delete_mib_complete(db, settings, name)
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
