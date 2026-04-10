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

from app.schemas.snmp import SnmpProbeRead, SnmpVarBindRead


def _varbinds_to_read(varbinds: tuple) -> list[SnmpVarBindRead]:
    out: list[SnmpVarBindRead] = []
    for vb in varbinds:
        parts = [x.prettyPrint() for x in vb]
        if len(parts) >= 2:
            out.append(SnmpVarBindRead(oid=parts[0], value=parts[1]))
        elif len(parts) == 1:
            out.append(SnmpVarBindRead(oid=parts[0], value=""))
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
                    varbinds=_varbinds_to_read(varbinds),
                )
            return SnmpProbeRead(ok=True, varbinds=_varbinds_to_read(varbinds))

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
            collected.extend(_varbinds_to_read(varbinds))
            if len(collected) >= max_oids:
                break

        return SnmpProbeRead(ok=True, varbinds=collected[:max_oids])
    finally:
        snmp_engine.close_dispatcher()
