"""SNMP GET / bulk walk mot en vert (SNMPv2c community)."""

from __future__ import annotations

from pysnmp.hlapi.v3arch.asyncio import (
    CommunityData,
    ContextData,
    ObjectIdentity,
    ObjectType,
    SnmpEngine,
    UdpTransportTarget,
    bulk_walk_cmd,
    get_cmd,
)

from app.schemas.snmp import SnmpProbeRead, SnmpSysInfoRead, SnmpVarBindRead

_SYS_DESCR_OID = "1.3.6.1.2.1.1.1.0"
_SYS_NAME_OID = "1.3.6.1.2.1.1.5.0"


def varbinds_to_read(varbinds: tuple) -> list[SnmpVarBindRead]:
    out: list[SnmpVarBindRead] = []
    for vb in varbinds:
        oid_obj = vb[0]
        try:
            val_obj = vb[1]
        except IndexError:
            val_obj = None
        oid_str = ""
        tup_fn = getattr(oid_obj, "asTuple", None)
        if callable(tup_fn):
            tup = tup_fn()
            if tup:
                try:
                    oid_str = ".".join(str(int(x)) for x in tup)
                except (TypeError, ValueError):
                    oid_str = ""
        if not oid_str:
            oid_str = oid_obj.prettyPrint()
        val_str = val_obj.prettyPrint() if val_obj is not None else ""
        out.append(SnmpVarBindRead(oid=oid_str, value=val_str))
    return out


async def run_snmp_probe(
    *,
    host: str,
    port: int,
    community: str,
    oid: str,
    operation: str,
    max_oids: int,
    timeout_sec: float,
    retries: int,
) -> SnmpProbeRead:
    snmp_engine = SnmpEngine()
    try:
        transport = await UdpTransportTarget.create(
            (host, port),
            timeout=timeout_sec,
            retries=retries,
        )
        auth = CommunityData(community, mpModel=1)
        ctx = ContextData()
        root_oid = ObjectType(ObjectIdentity(oid))

        if operation == "get":
            error_indication, error_status, error_index, varbinds = await get_cmd(
                snmp_engine,
                auth,
                transport,
                ctx,
                root_oid,
            )
            if error_indication:
                return SnmpProbeRead(ok=False, error=str(error_indication), varbinds=[])
            if error_status:
                return SnmpProbeRead(
                    ok=False,
                    error=f"SNMP errorStatus={error_status} index={error_index}",
                    varbinds=varbinds_to_read(varbinds),
                )
            return SnmpProbeRead(ok=True, varbinds=varbinds_to_read(varbinds))

        collected: list[SnmpVarBindRead] = []
        async for error_indication, error_status, error_index, varbinds in bulk_walk_cmd(
            snmp_engine,
            auth,
            transport,
            ctx,
            0,
            25,
            root_oid,
            lexicographicMode=False,
        ):
            if error_indication:
                return SnmpProbeRead(ok=False, error=str(error_indication), varbinds=collected)
            if error_status:
                return SnmpProbeRead(
                    ok=False,
                    error=f"SNMP errorStatus={error_status} index={error_index}",
                    varbinds=collected,
                )
            collected.extend(varbinds_to_read(varbinds))
            if len(collected) >= max_oids:
                break

        return SnmpProbeRead(ok=True, varbinds=collected[:max_oids])
    finally:
        snmp_engine.close_dispatcher()


async def run_snmp_sys_info(
    *,
    host: str,
    port: int,
    community: str,
    timeout_sec: float = 2.0,
    retries: int = 1,
) -> SnmpSysInfoRead:
    """GET sysDescr.0 og sysName.0 (SNMPv2c)."""
    snmp_engine = SnmpEngine()
    try:
        transport = await UdpTransportTarget.create(
            (host, port),
            timeout=timeout_sec,
            retries=retries,
        )
        auth = CommunityData(community, mpModel=1)
        ctx = ContextData()
        o_descr = ObjectType(ObjectIdentity(_SYS_DESCR_OID))
        o_name = ObjectType(ObjectIdentity(_SYS_NAME_OID))
        error_indication, error_status, error_index, varbinds = await get_cmd(
            snmp_engine,
            auth,
            transport,
            ctx,
            o_descr,
            o_name,
        )
        if error_indication:
            return SnmpSysInfoRead(ok=False, error=str(error_indication))
        if error_status:
            return SnmpSysInfoRead(
                ok=False,
                error=f"SNMP errorStatus={error_status} index={error_index}",
            )
        vbs = varbinds_to_read(varbinds)
        sys_descr: str | None = None
        sys_name: str | None = None
        for vb in vbs:
            o = vb.oid.replace(" ", "").strip()
            v = vb.value.strip()
            if not v or v == "":
                continue
            if o == _SYS_DESCR_OID or o.endswith(".1.1.1.0"):
                sys_descr = v
            elif o == _SYS_NAME_OID or o.endswith(".1.1.5.0"):
                sys_name = v
        return SnmpSysInfoRead(ok=True, sys_name=sys_name, sys_descr=sys_descr)
    finally:
        snmp_engine.close_dispatcher()
