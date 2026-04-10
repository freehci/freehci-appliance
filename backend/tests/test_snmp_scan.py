"""Tester for SNMP fullskann (parser for IP- og VLAN-tabeller)."""

from __future__ import annotations

from app.schemas.snmp import SnmpIpAddressRow, SnmpInterfaceVlanRow, SnmpVarBindRead, SnmpVlanRow
from app.services.snmp_scan import (
    build_interface_vlan_rows,
    parse_dot1d_base_port_if_index,
    parse_dot1q_pvid,
    parse_dot1q_vlan_static_names,
    parse_ip_addr_table,
)


def test_parse_ip_addr_table() -> None:
    vbs = [
        SnmpVarBindRead(oid="1.3.6.1.2.1.4.20.1.2.192.168.5.10", value="3"),
        SnmpVarBindRead(oid="1.3.6.1.2.1.4.20.1.3.192.168.5.10", value="255.255.255.0"),
    ]
    rows = parse_ip_addr_table(vbs)
    assert len(rows) == 1
    assert rows[0].address == "192.168.5.10"
    assert rows[0].if_index == 3
    assert rows[0].netmask == "255.255.255.0"


def test_parse_bridge_and_pvid_merge() -> None:
    port_vbs = [
        SnmpVarBindRead(oid="1.3.6.1.2.1.17.1.4.1.2.5", value="42"),
    ]
    pvid_vbs = [
        SnmpVarBindRead(oid="1.3.6.1.2.1.17.7.1.4.5.1.1.5", value="100"),
    ]
    port_map = parse_dot1d_base_port_if_index(port_vbs)
    pvid_map = parse_dot1q_pvid(pvid_vbs)
    assert port_map[5] == 42
    assert pvid_map[5] == 100
    iv = build_interface_vlan_rows(port_map, pvid_map)
    assert iv == [
        SnmpInterfaceVlanRow(if_index=42, native_vlan_id=100, bridge_port=5, interface_name=None),
    ]


def test_parse_vlan_names() -> None:
    vbs = [
        SnmpVarBindRead(oid="1.3.6.1.2.1.17.7.1.4.3.1.1.100", value="Servers"),
    ]
    rows = parse_dot1q_vlan_static_names(vbs)
    assert rows == [SnmpVlanRow(vlan_id=100, name="Servers")]


def test_parse_ip_addr_table_ignores_other_oids() -> None:
    vbs = [
        SnmpVarBindRead(oid="1.3.6.1.2.1.2.2.1.2.1", value="eth0"),
    ]
    assert parse_ip_addr_table(vbs) == []
