"""Tester for sysObjectID → enterprise (PEN) og SNMP host discovery."""

from __future__ import annotations

from app.services.snmp_probe import parse_sys_object_id_for_enterprise


def test_parse_sys_object_id_symbolic_enterprises() -> None:
    pen, num = parse_sys_object_id_for_enterprise("SNMPv2-SMI::enterprises.890.3.2")
    assert pen == 890
    assert num == "1.3.6.1.4.1.890.3.2"


def test_parse_sys_object_id_numeric() -> None:
    pen, num = parse_sys_object_id_for_enterprise("1.3.6.1.4.1.2636.1.1.1.2")
    assert pen == 2636
    assert num == "1.3.6.1.4.1.2636.1.1.1.2"


def test_parse_sys_object_id_enterprises_only() -> None:
    pen, num = parse_sys_object_id_for_enterprise("enterprises.1139")
    assert pen == 1139
    assert num == "1.3.6.1.4.1.1139"


def test_parse_sys_object_id_no_enterprise() -> None:
    pen, num = parse_sys_object_id_for_enterprise("iso.org.dod.internet.mgmt.mib-2.system.sysObjectID.0")
    assert pen is None
    assert num is None
