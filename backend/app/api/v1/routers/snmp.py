"""SNMP: MIB-bibliotek, kompilering, IANA enterprise og SNMPv2c-verktøy."""

from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, Query, UploadFile
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session
from starlette.responses import Response

from app.api.deps import get_db
from app.core.config import Settings, get_settings
from app.schemas.snmp import (
    SnmpEnterpriseAutocreateRequest,
    SnmpEnterpriseAutocreateResultRead,
    SnmpEnterpriseGroupRead,
    SnmpHostDiscoveryRead,
    SnmpHostDiscoveryRequest,
    SnmpIanaSyncRead,
    SnmpInventoryApplyRead,
    SnmpInventoryApplyRequest,
    SnmpInventoryRead,
    SnmpInventoryRequest,
    SnmpMibCompileAllQueuedRead,
    SnmpMibNormalizeRead,
    SnmpMibDetailPageRead,
    SnmpMibDetailRead,
    SnmpMibFileRead,
    SnmpMibManufacturerBrief,
    SnmpProbeRead,
    SnmpProbeRequest,
    SnmpScanRead,
    SnmpScanRequest,
    SnmpBrowserNodeRead,
    SnmpBrowserResolveRead,
    SnmpBrowserDefinitionRead,
    SnmpBrowserLocateRead,
)
from app.services import snmp_interface_import as iface_import_svc
from app.services import snmp_inventory as inv_svc
from app.services import snmp_mib_catalog as mib_cat_svc
from app.services import snmp_mibs as mib_disk_svc
from app.services.snmp_mib_dependencies import refresh_missing_imports_all
from app.services import snmp_scan as scan_svc
from app.services import snmp_probe as probe_svc
from app.services import snmp_mib_browser as mib_browser_svc

router = APIRouter(prefix="/snmp", tags=["snmp"])

_MAX_BATCH_FILES = 50


@router.get("/mibs/detailed", response_model=SnmpMibDetailPageRead)
def list_mibs_detailed(
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
    q: str | None = Query(None, description="Søk i filnavn, modul, IANA, produsent, kompilermelding"),
    sort: str = Query(
        "name",
        description=(
            "name|module_name|compile_status|modified_at|size_bytes|enterprise_number|"
            "effective_enterprise_number|iana_organization|mfr|missing_imports"
        ),
    ),
    order: str = Query("asc", description="asc eller desc"),
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=500),
    compile_status: str | None = Query(
        None,
        description="Filtrer på kompileringsstatus: pending, ok, error",
    ),
) -> SnmpMibDetailPageRead:
    data = mib_cat_svc.list_mibs_detailed_page(
        db,
        settings,
        q=q,
        sort=sort,
        order=order,
        page=page,
        page_size=page_size,
        compile_status=compile_status,
    )
    return SnmpMibDetailPageRead.model_validate(data)


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


@router.post("/mibs/normalize-filenames", response_model=SnmpMibNormalizeRead)
def normalize_mib_filenames(
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> SnmpMibNormalizeRead:
    """Døp om eksisterende *.txt/*.my m.m. til *.mib på disk og oppdater metadata. Kjør deretter «kompiler ventende» ved behov."""
    r = mib_cat_svc.normalize_mib_library_filenames_on_disk(db, settings)
    return SnmpMibNormalizeRead.model_validate(r)


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
        mib_cat_svc.upsert_mib_meta(db, settings, row["name"], raw)
        saved.append(row["name"])
    refresh_missing_imports_all(db, settings)
    disk_rows = {r["name"]: r for r in mib_disk_svc.list_mib_files(settings)}
    return [
        SnmpMibDetailRead.model_validate(mib_cat_svc.mib_detail_dict(db, settings, disk_rows[n]))
        for n in saved
    ]


@router.get("/mibs/{name}/source", response_class=PlainTextResponse)
def get_mib_source(
    name: str,
    settings: Settings = Depends(get_settings),
) -> PlainTextResponse:
    """Rå MIB-kildetekst (UTF-8) for feilsøking i GUI."""
    text = mib_disk_svc.read_mib_text(settings, name)
    return PlainTextResponse(content=text, media_type="text/plain; charset=utf-8")


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
    mib_cat_svc.upsert_mib_meta(db, settings, row["name"], raw)
    refresh_missing_imports_all(db, settings)
    return SnmpMibFileRead.model_validate(row)


@router.post("/mibs/{name}/compile", response_model=SnmpMibDetailRead)
def compile_mib(
    name: str,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> SnmpMibDetailRead:
    row = mib_cat_svc.compile_mib_file(db, settings, name)
    return SnmpMibDetailRead.model_validate(row)


@router.post(
    "/mibs/compile-all",
    response_model=SnmpMibCompileAllQueuedRead,
    status_code=202,
)
def compile_all_mibs(
    background_tasks: BackgroundTasks,
) -> SnmpMibCompileAllQueuedRead:
    """Kjør pysmi for hver MIB-fil i bakgrunnen (unngår 504 ved store biblioteker)."""
    background_tasks.add_task(mib_cat_svc.run_compile_all_mibs_background)
    return SnmpMibCompileAllQueuedRead()


@router.post(
    "/mibs/compile-pending",
    response_model=SnmpMibCompileAllQueuedRead,
    status_code=202,
)
def compile_pending_mibs(
    background_tasks: BackgroundTasks,
) -> SnmpMibCompileAllQueuedRead:
    """Kompiler kun filer med status pending (bakgrunn)."""
    background_tasks.add_task(mib_cat_svc.run_compile_pending_mibs_background)
    return SnmpMibCompileAllQueuedRead()


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


@router.post("/host-discovery", response_model=SnmpHostDiscoveryRead)
async def snmp_host_discovery(
    data: SnmpHostDiscoveryRequest,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> SnmpHostDiscoveryRead:
    """Hent system-gruppe (sys*), trekk ut PEN fra sysObjectID, slå opp IANA/DCIM og MIB-filer i biblioteket."""
    host = data.host.strip()
    raw = await probe_svc.run_snmp_system_group_get(
        host=host,
        port=data.port,
        community=data.community,
        timeout_sec=data.timeout_sec,
        retries=data.retries,
    )
    err = raw.pop("_error", None)
    if err:
        return SnmpHostDiscoveryRead(ok=False, host=host, error=err)
    sys_object_id = raw.get("sys_object_id")
    pen, num_oid = probe_svc.parse_sys_object_id_for_enterprise(sys_object_id or "")
    ctx = mib_cat_svc.discovery_context_for_pen(db, settings, pen)
    lm = ctx.get("linked_manufacturer")
    brief = SnmpMibManufacturerBrief.model_validate(lm) if lm else None
    return SnmpHostDiscoveryRead(
        ok=True,
        host=host,
        sys_descr=raw.get("sys_descr"),
        sys_object_id=sys_object_id,
        sys_object_id_numeric=num_oid,
        sys_uptime=raw.get("sys_uptime"),
        sys_contact=raw.get("sys_contact"),
        sys_name=raw.get("sys_name"),
        sys_location=raw.get("sys_location"),
        enterprise_number=pen,
        iana_organization=ctx.get("iana_organization"),
        linked_manufacturer=brief,
        mib_files_in_library=list(ctx.get("mib_files_in_library") or []),
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


@router.get("/browser/children", response_model=list[SnmpBrowserNodeRead])
def snmp_browser_children(
    oid: str = Query("1", description="Parent OID (dotted), default iso=1"),
    settings: Settings = Depends(get_settings),
) -> list[SnmpBrowserNodeRead]:
    """Lazy-load barn for en OID i browser-treet."""
    rows = mib_browser_svc.list_children(settings, oid)
    return [SnmpBrowserNodeRead.model_validate(r) for r in rows]


@router.get("/browser/resolve", response_model=SnmpBrowserResolveRead)
def snmp_browser_resolve(
    oid: str = Query(..., description="OID (dotted) som skal resolves til (label, modul, symbol)"),
    settings: Settings = Depends(get_settings),
) -> SnmpBrowserResolveRead:
    r = mib_browser_svc.resolve_oid(settings, oid)
    return SnmpBrowserResolveRead.model_validate(r)


@router.get("/browser/definition", response_model=SnmpBrowserDefinitionRead)
def snmp_browser_definition(
    oid: str = Query(..., description="OID (dotted). Hvis modul/symbol finnes, returneres definisjon-snutt."),
    settings: Settings = Depends(get_settings),
) -> SnmpBrowserDefinitionRead:
    r = mib_browser_svc.resolve_oid(settings, oid)
    text = mib_browser_svc.definition_snippet(settings, module_name=r.get("module"), symbol=r.get("symbol"))
    return SnmpBrowserDefinitionRead(
        oid=r.get("oid") or oid,
        module=r.get("module"),
        symbol=r.get("symbol"),
        text=text,
    )


@router.get("/browser/locate", response_model=SnmpBrowserLocateRead)
def snmp_browser_locate(
    mib: str | None = Query(None, description="MIB-filnavn i biblioteket (f.eks. FOO-MIB.mib)"),
    module: str | None = Query(None, description="ASN.1 MODULE DEFINITIONS-navn"),
    settings: Settings = Depends(get_settings),
) -> SnmpBrowserLocateRead:
    """Finn en OID i browser-indeksen for en MIB-modul (krever kompilert PySNMP-modul)."""
    if mib and mib.strip():
        r = mib_browser_svc.locate_from_mib_filename(settings, mib.strip())
    elif module and module.strip():
        r = mib_browser_svc.locate_module_oid(settings, module.strip())
    else:
        return SnmpBrowserLocateRead(found=False, error="Oppgi «mib» eller «module».")
    return SnmpBrowserLocateRead.model_validate(r)
