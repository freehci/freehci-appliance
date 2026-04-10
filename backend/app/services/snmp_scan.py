"""Samlet SNMP-skanning: grensesnitt, IPv4-adresser og VLAN (BRIDGE/Q-BRIDGE)."""

from __future__ import annotations

from collections import defaultdict

from pysnmp.hlapi.v3arch.asyncio import (
    CommunityData,
    ContextData,
    ObjectIdentity,
    ObjectType,
    SnmpEngine,
    UdpTransportTarget,
    get_cmd,
)

from app.schemas.snmp import (
    SnmpInterfaceRow,
    SnmpIpAddressRow,
    SnmpInterfaceVlanRow,
    SnmpScanRead,
    SnmpVarBindRead,
    SnmpVlanRow,
)
from app.services.snmp_inventory import (
    _parse_if_table_varbinds,
    _parse_ifx_table_varbinds,
    _parse_int,
    _walk_prefix,
    build_interface_rows,
)
from app.services.snmp_probe import varbinds_to_read

# ipAddrTable 1.3.6.1.2.1.4.20.1 — kolonne 2 = ipAdEntIfIndex, 3 = ipAdEntNetMask
_IP_ADDR_BASE = (1, 3, 6, 1, 2, 1, 4, 20, 1)
# dot1dBasePortIfIndex 1.3.6.1.2.1.17.1.4.1.2.<bridgePort>
_DOT1D_PORT_IFIDX_BASE = (1, 3, 6, 1, 2, 1, 17, 1, 4, 1, 2)
# dot1qPvid 1.3.6.1.2.1.17.7.1.4.5.1.1.<bridgePort>
_DOT1Q_PVID_BASE = (1, 3, 6, 1, 2, 1, 17, 7, 1, 4, 5, 1, 1)
# dot1qVlanStaticName 1.3.6.1.2.1.17.7.1.4.3.1.1.<vlanId>
_DOT1Q_VLAN_NAME_BASE = (1, 3, 6, 1, 2, 1, 17, 7, 1, 4, 3, 1, 1)


def parse_ip_addr_table(varbinds: list[SnmpVarBindRead]) -> list[SnmpIpAddressRow]:
    by_ip: dict[tuple[int, int, int, int], dict] = defaultdict(dict)
    n = len(_IP_ADDR_BASE)
    for vb in varbinds:
        parts = [int(x) for x in vb.oid.split(".") if x.isdigit()]
        if len(parts) < n + 1 + 4:
            continue
        if tuple(parts[:n]) != _IP_ADDR_BASE:
            continue
        col = parts[n]
        ip_t = tuple(parts[n + 1 : n + 5])
        if len(ip_t) != 4 or not all(0 <= o <= 255 for o in ip_t):
            continue
        if col == 2:
            idx = _parse_int(vb.value)
            if idx is not None:
                by_ip[ip_t]["if_index"] = idx
        elif col == 3:
            by_ip[ip_t]["netmask"] = vb.value.strip() or None
    out: list[SnmpIpAddressRow] = []
    for ip_t in sorted(by_ip.keys()):
        d = by_ip[ip_t]
        if "if_index" not in d:
            continue
        addr = ".".join(str(x) for x in ip_t)
        out.append(
            SnmpIpAddressRow(
                address=addr,
                if_index=d["if_index"],
                netmask=d.get("netmask"),
            ),
        )
    return out


def parse_dot1d_base_port_if_index(varbinds: list[SnmpVarBindRead]) -> dict[int, int]:
    """bridgePort -> ifIndex."""
    n = len(_DOT1D_PORT_IFIDX_BASE)
    m: dict[int, int] = {}
    for vb in varbinds:
        parts = [int(x) for x in vb.oid.split(".") if x.isdigit()]
        if len(parts) != n + 1:
            continue
        if tuple(parts[:n]) != _DOT1D_PORT_IFIDX_BASE:
            continue
        bport = parts[n]
        ifidx = _parse_int(vb.value)
        if ifidx is not None and bport >= 1:
            m[bport] = ifidx
    return m


def parse_dot1q_pvid(varbinds: list[SnmpVarBindRead]) -> dict[int, int]:
    """bridgePort -> native/access VLAN (PVID)."""
    n = len(_DOT1Q_PVID_BASE)
    m: dict[int, int] = {}
    for vb in varbinds:
        parts = [int(x) for x in vb.oid.split(".") if x.isdigit()]
        if len(parts) != n + 1:
            continue
        if tuple(parts[:n]) != _DOT1Q_PVID_BASE:
            continue
        bport = parts[n]
        pvid = _parse_int(vb.value)
        if pvid is not None and 1 <= pvid <= 4094 and bport >= 1:
            m[bport] = pvid
    return m


def parse_dot1q_vlan_static_names(varbinds: list[SnmpVarBindRead]) -> list[SnmpVlanRow]:
    n = len(_DOT1Q_VLAN_NAME_BASE)
    by_id: dict[int, str] = {}
    for vb in varbinds:
        parts = [int(x) for x in vb.oid.split(".") if x.isdigit()]
        if len(parts) != n + 1:
            continue
        if tuple(parts[:n]) != _DOT1Q_VLAN_NAME_BASE:
            continue
        vid = parts[n]
        if 1 <= vid <= 4094:
            name = vb.value.strip()
            by_id[vid] = name[:256] if name else ""
    return [SnmpVlanRow(vlan_id=vid, name=(nm or None)) for vid, nm in sorted(by_id.items())]


def build_interface_vlan_rows(
    port_if: dict[int, int],
    port_pvid: dict[int, int],
) -> list[SnmpInterfaceVlanRow]:
    out: list[SnmpInterfaceVlanRow] = []
    for bport, pvid in sorted(port_pvid.items()):
        ifidx = port_if.get(bport)
        if ifidx is None:
            continue
        out.append(
            SnmpInterfaceVlanRow(
                if_index=ifidx,
                native_vlan_id=pvid,
                bridge_port=bport,
            ),
        )
    return out


def _attach_interface_names(
    interfaces: list[SnmpInterfaceRow],
    ip_rows: list[SnmpIpAddressRow],
    if_vlan_rows: list[SnmpInterfaceVlanRow],
) -> tuple[list[SnmpIpAddressRow], list[SnmpInterfaceVlanRow]]:
    name_by_idx = {r.if_index: r.name for r in interfaces}
    ips = [
        SnmpIpAddressRow(
            address=r.address,
            if_index=r.if_index,
            netmask=r.netmask,
            interface_name=name_by_idx.get(r.if_index),
        )
        for r in ip_rows
    ]
    iv = [
        SnmpInterfaceVlanRow(
            if_index=r.if_index,
            native_vlan_id=r.native_vlan_id,
            bridge_port=r.bridge_port,
            interface_name=name_by_idx.get(r.if_index),
        )
        for r in if_vlan_rows
    ]
    return ips, iv


async def collect_full_scan(
    *,
    host: str,
    port: int,
    community: str,
    timeout_sec: float,
    retries: int,
    max_varbinds: int,
) -> SnmpScanRead:
    """Én økt: IF-MIB, ifX, IP-MIB IPv4, BRIDGE/Q-BRIDGE VLAN der agenten støtter det."""
    snmp_engine = SnmpEngine()
    warnings: list[str] = []
    total_vb = 0

    try:
        transport = await UdpTransportTarget.create((host, port), timeout=timeout_sec, retries=retries)
        auth = CommunityData(community, mpModel=1)
        ctx = ContextData()

        ei, es, _ei2, vbs_sys = await get_cmd(
            snmp_engine,
            auth,
            transport,
            ctx,
            ObjectType(ObjectIdentity("1.3.6.1.2.1.1.5.0")),
            ObjectType(ObjectIdentity("1.3.6.1.2.1.1.1.0")),
        )
        if ei:
            return SnmpScanRead(ok=False, error=str(ei), host=host)
        if es:
            return SnmpScanRead(
                ok=False,
                error=f"SNMP error ved sysName/sysDescr: {es}",
                host=host,
            )

        sys_rows = varbinds_to_read(vbs_sys)
        sys_name = sys_rows[0].value if len(sys_rows) >= 1 else ""
        sys_descr = sys_rows[1].value if len(sys_rows) >= 2 else ""

        budget = max_varbinds
        half = max(500, budget // 2)
        if_vbs, err = await _walk_prefix(snmp_engine, auth, transport, ctx, "1.3.6.1.2.1.2.2.1", half)
        if err:
            return SnmpScanRead(
                ok=False,
                error=err,
                host=host,
                sys_name=sys_name or None,
                sys_descr=sys_descr or None,
            )
        total_vb += len(if_vbs)

        ifx_vbs, err = await _walk_prefix(
            snmp_engine,
            auth,
            transport,
            ctx,
            "1.3.6.1.2.1.31.1.1.1",
            budget - len(if_vbs),
        )
        if err:
            return SnmpScanRead(
                ok=False,
                error=err,
                host=host,
                sys_name=sys_name or None,
                sys_descr=sys_descr or None,
            )
        total_vb += len(ifx_vbs)

        truncated_if = len(if_vbs) + len(ifx_vbs) >= budget
        if_by = _parse_if_table_varbinds(if_vbs)
        ifx_by = _parse_ifx_table_varbinds(ifx_vbs)
        interfaces = build_interface_rows(if_by, ifx_by)

        remaining = max(0, budget - total_vb)
        ip_max = max(200, min(4000, remaining // 3))
        vlan_each = max(150, (remaining - ip_max) // 3) if remaining > ip_max else max(50, remaining // 4)

        ip_vbs: list[SnmpVarBindRead] = []
        if ip_max > 0 and remaining > 0:
            ip_vbs, ip_err = await _walk_prefix(
                snmp_engine,
                auth,
                transport,
                ctx,
                "1.3.6.1.2.1.4.20.1",
                min(ip_max, remaining),
            )
            if ip_err:
                warnings.append(f"IP-MIB (IPv4): {ip_err}")
            total_vb += len(ip_vbs)

        remaining = max(0, budget - total_vb)
        port_vbs: list[SnmpVarBindRead] = []
        pvid_vbs: list[SnmpVarBindRead] = []
        vname_vbs: list[SnmpVarBindRead] = []

        if remaining > 0:
            take = min(vlan_each, remaining)
            port_vbs, pe = await _walk_prefix(
                snmp_engine,
                auth,
                transport,
                ctx,
                "1.3.6.1.2.1.17.1.4.1.2",
                take,
            )
            if pe:
                warnings.append(f"BRIDGE-MIB (dot1dBasePortIfIndex): {pe}")
            total_vb += len(port_vbs)

        remaining = max(0, budget - total_vb)
        if remaining > 0:
            take = min(vlan_each, remaining)
            pvid_vbs, qe = await _walk_prefix(
                snmp_engine,
                auth,
                transport,
                ctx,
                "1.3.6.1.2.1.17.7.1.4.5.1.1",
                take,
            )
            if qe:
                warnings.append(f"Q-BRIDGE-MIB (dot1qPvid): {qe}")
            total_vb += len(pvid_vbs)

        remaining = max(0, budget - total_vb)
        if remaining > 0:
            take = min(vlan_each, remaining)
            vname_vbs, ve = await _walk_prefix(
                snmp_engine,
                auth,
                transport,
                ctx,
                "1.3.6.1.2.1.17.7.1.4.3.1.1",
                take,
            )
            if ve:
                warnings.append(f"Q-BRIDGE-MIB (dot1qVlanStaticName): {ve}")
            total_vb += len(vname_vbs)

        ip_rows = parse_ip_addr_table(ip_vbs)
        port_map = parse_dot1d_base_port_if_index(port_vbs)
        pvid_map = parse_dot1q_pvid(pvid_vbs)
        vlan_rows = parse_dot1q_vlan_static_names(vname_vbs)
        if_vlan_rows = build_interface_vlan_rows(port_map, pvid_map)

        ip_rows, if_vlan_rows = _attach_interface_names(interfaces, ip_rows, if_vlan_rows)

        truncated = truncated_if or total_vb >= max_varbinds

        return SnmpScanRead(
            ok=True,
            host=host,
            sys_name=sys_name or None,
            sys_descr=sys_descr or None,
            interfaces=interfaces,
            ip_addresses=ip_rows,
            vlans=vlan_rows,
            interface_vlans=if_vlan_rows,
            warnings=warnings,
            truncated=truncated,
            varbinds_collected=total_vb,
        )
    finally:
        snmp_engine.close_dispatcher()
