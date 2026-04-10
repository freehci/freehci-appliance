"""SNMP IF-MIB / IF-MIB-extended (ifXTable) for grensesnittsinventar."""

from __future__ import annotations

from collections import defaultdict

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

from app.schemas.snmp import SnmpInterfaceRow, SnmpInventoryRead, SnmpVarBindRead

# ifTable.ifEntry columns (RFC 1213 / IF-MIB)
_IF_TABLE_BASE = (1, 3, 6, 1, 2, 1, 2, 2, 1)
# ifXEntry (1.3.6.1.2.1.31.1.1.1)
_IFX_TABLE_BASE = (1, 3, 6, 1, 2, 1, 31, 1, 1, 1)

_IF_TYPE_NAMES: dict[int, str] = {
    1: "other",
    6: "ethernetCsmacd",
    24: "softwareLoopback",
    131: "tunnel",
    161: "ieee80211",
}


def _parse_int(val: str) -> int | None:
    s = val.strip().split()[0] if val else ""
    if s.isdigit() or (s.startswith("-") and s[1:].isdigit()):
        try:
            return int(s)
        except ValueError:
            return None
    return None


def _normalize_mac(raw: str) -> str | None:
    s = raw.strip().replace(" ", "")
    if not s or s in ("0x", "0x00", "00:00:00:00:00:00"):
        return None
    if s.lower().startswith("0x"):
        hx = s[2:].replace(":", "")
    else:
        hx = s.replace(":", "").replace("-", "")
    if len(hx) == 12 and all(c in "0123456789abcdefABCDEF" for c in hx):
        hx = hx.lower()
        return ":".join(hx[i : i + 2] for i in range(0, 12, 2))
    return raw[:32] if raw else None


def _speed_mbps(if_speed_bits: int | None, if_high_speed: int | None) -> int | None:
    """ifSpeed er bit/s (32-bit); ifHighSpeed er Mb/s (0 betyr ukjent / bruk ifSpeed)."""
    if if_high_speed is not None and if_high_speed > 0:
        return if_high_speed
    if if_speed_bits is None or if_speed_bits <= 0:
        return None
    # unngå overflow ved 10G+ som ligger i ifSpeed som 4294967295
    if if_speed_bits >= 4_294_967_000:
        return None
    return max(1, int(round(if_speed_bits / 1_000_000)))


def _admin_oper_labels(admin: int | None, oper: int | None) -> tuple[str, str, bool]:
    """Returner (admin_label, oper_label, enabled)."""
    amap = {1: "up", 2: "down", 3: "testing"}
    omap = {1: "up", 2: "down", 3: "testing", 4: "unknown", 5: "dormant", 6: "notPresent", 7: "lowerLayerDown"}
    al = amap.get(admin, "unknown")
    ol = omap.get(oper, "unknown")
    enabled = admin == 1
    return al, ol, enabled


def _parse_if_table_varbinds(varbinds: list[SnmpVarBindRead]) -> dict[int, dict]:
    """Parse walk av 1.3.6.1.2.1.2.2.1.*."""
    by_idx: dict[int, dict] = defaultdict(dict)
    n_base = len(_IF_TABLE_BASE)
    for vb in varbinds:
        parts = [int(x) for x in vb.oid.split(".") if x.isdigit()]
        if len(parts) < n_base + 2:
            continue
        if tuple(parts[:n_base]) != _IF_TABLE_BASE:
            continue
        col = parts[n_base]
        idx = parts[n_base + 1]
        by_idx[idx]["if_index"] = idx
        v = vb.value
        if col == 2:
            by_idx[idx]["if_descr"] = v
        elif col == 3:
            by_idx[idx]["if_type"] = _parse_int(v)
        elif col == 4:
            by_idx[idx]["mtu"] = _parse_int(v)
        elif col == 5:
            by_idx[idx]["if_speed"] = _parse_int(v)
        elif col == 6:
            by_idx[idx]["phys"] = v
        elif col == 7:
            by_idx[idx]["admin"] = _parse_int(v)
        elif col == 8:
            by_idx[idx]["oper"] = _parse_int(v)
    return by_idx


def _parse_ifx_table_varbinds(varbinds: list[SnmpVarBindRead]) -> dict[int, dict]:
    by_idx: dict[int, dict] = defaultdict(dict)
    n_base = len(_IFX_TABLE_BASE)
    for vb in varbinds:
        parts = [int(x) for x in vb.oid.split(".") if x.isdigit()]
        if len(parts) < n_base + 2:
            continue
        if tuple(parts[:n_base]) != _IFX_TABLE_BASE:
            continue
        col = parts[n_base]
        idx = parts[n_base + 1]
        v = vb.value
        if col == 1:
            by_idx[idx]["if_name"] = v
        elif col == 15:
            by_idx[idx]["if_high_speed"] = _parse_int(v)
        elif col == 18:
            by_idx[idx]["if_alias"] = v
    return by_idx


def build_interface_rows(
    if_by_idx: dict[int, dict],
    ifx_by_idx: dict[int, dict],
) -> list[SnmpInterfaceRow]:
    all_idx = sorted(set(if_by_idx.keys()) | set(ifx_by_idx.keys()))
    out: list[SnmpInterfaceRow] = []
    for idx in all_idx:
        a = if_by_idx.get(idx, {})
        x = ifx_by_idx.get(idx, {})
        if not a and not x:
            continue
        if_name = (x.get("if_name") or "").strip() or None
        if_descr = (a.get("if_descr") or "").strip() or None
        name = (if_name or if_descr or f"if-{idx}")[:128]
        alias = (x.get("if_alias") or "").strip() or None
        descr_for_dcim = alias
        if not descr_for_dcim and if_descr and if_descr != name:
            descr_for_dcim = (if_descr[:512] if if_descr else None)
        if_type = a.get("if_type")
        if_type_label = _IF_TYPE_NAMES.get(if_type) if isinstance(if_type, int) else None
        mtu = a.get("mtu")
        if isinstance(mtu, int) and (mtu < 68 or mtu > 65535):
            mtu = None
        speed = _speed_mbps(a.get("if_speed"), x.get("if_high_speed"))
        mac = _normalize_mac(str(a.get("phys", "")))
        admin_l, oper_l, enabled = _admin_oper_labels(a.get("admin"), a.get("oper"))
        out.append(
            SnmpInterfaceRow(
                if_index=idx,
                name=name,
                description=descr_for_dcim,
                if_descr=if_descr,
                if_alias=alias,
                if_type=if_type,
                if_type_label=if_type_label,
                mtu=mtu,
                speed_mbps=speed,
                mac_address=mac,
                admin_status=admin_l,
                oper_status=oper_l,
                enabled=enabled,
            ),
        )
    return out


async def _walk_prefix(
    snmp_engine: SnmpEngine,
    auth: CommunityData,
    transport,
    ctx: ContextData,
    oid_prefix: str,
    max_varbinds: int,
) -> tuple[list[SnmpVarBindRead], str | None]:
    root = ObjectType(ObjectIdentity(oid_prefix))
    collected: list[SnmpVarBindRead] = []
    async for error_indication, error_status, error_index, varbinds in bulk_walk_cmd(
        snmp_engine,
        auth,
        transport,
        ctx,
        0,
        25,
        root,
        lexicographicMode=False,
    ):
        if error_indication:
            return collected, str(error_indication)
        if error_status:
            return collected, f"SNMP errorStatus={error_status} index={error_index}"
        collected.extend(varbinds_to_read(varbinds))
        if len(collected) >= max_varbinds:
            break
    return collected, None


async def collect_interface_inventory(
    *,
    host: str,
    port: int,
    community: str,
    timeout_sec: float,
    retries: int,
    max_varbinds: int,
) -> SnmpInventoryRead:
    """Hent sysName/sysDescr + IF-MIB + ifXTable."""
    snmp_engine = SnmpEngine()
    sys_name = ""
    sys_descr = ""
    if_vbs: list[SnmpVarBindRead] = []
    ifx_vbs: list[SnmpVarBindRead] = []
    err: str | None = None
    truncated = False

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
            return SnmpInventoryRead(ok=False, error=str(ei), host=host)
        if es:
            return SnmpInventoryRead(
                ok=False,
                error=f"SNMP error ved sysName/sysDescr: {es}",
                host=host,
            )
        sys_rows = varbinds_to_read(vbs_sys)
        if len(sys_rows) >= 1:
            sys_name = sys_rows[0].value
        if len(sys_rows) >= 2:
            sys_descr = sys_rows[1].value

        budget = max_varbinds
        half = max(500, budget // 2)
        if_vbs, err = await _walk_prefix(
            snmp_engine,
            auth,
            transport,
            ctx,
            "1.3.6.1.2.1.2.2.1",
            half,
        )
        if err:
            return SnmpInventoryRead(
                ok=False,
                error=err,
                host=host,
                sys_name=sys_name or None,
                sys_descr=sys_descr or None,
            )

        ifx_vbs, err = await _walk_prefix(
            snmp_engine,
            auth,
            transport,
            ctx,
            "1.3.6.1.2.1.31.1.1.1",
            budget - len(if_vbs),
        )
        if err:
            return SnmpInventoryRead(
                ok=False,
                error=err,
                host=host,
                sys_name=sys_name or None,
                sys_descr=sys_descr or None,
            )

        truncated = len(if_vbs) + len(ifx_vbs) >= max_varbinds

        if_by = _parse_if_table_varbinds(if_vbs)
        ifx_by = _parse_ifx_table_varbinds(ifx_vbs)
        rows = build_interface_rows(if_by, ifx_by)

        return SnmpInventoryRead(
            ok=True,
            host=host,
            sys_name=sys_name or None,
            sys_descr=sys_descr or None,
            interfaces=rows,
            truncated=truncated,
            varbinds_collected=len(if_vbs) + len(ifx_vbs),
        )
    finally:
        snmp_engine.close_dispatcher()
