"""Enhetstester for MAC-parsing (Linux ARP / ip neigh)."""

from app.services.ipam_subnet_scan import _parse_linux_arp_a, _parse_proc_net_arp, _parse_ip_neigh_output


def test_parse_linux_arp_a_parentheses_at_format() -> None:
    txt = (
        "? (192.168.1.1) at aa:bb:cc:dd:ee:01 [ether] on eth0\n"
        "host (10.0.0.5) at AA:BB:CC:DD:EE:02 [ether] on docker0\n"
    )
    m = _parse_linux_arp_a(txt)
    assert m["192.168.1.1"] == "aa:bb:cc:dd:ee:01"
    assert m["10.0.0.5"] == "aa:bb:cc:dd:ee:02"


def test_parse_proc_net_arp_skips_incomplete() -> None:
    txt = """IP address       HW type     Flags       HW address            Mask     Device
192.168.2.3      0x1         0x0         00:00:00:00:00:00     *        eth0
192.168.2.4      0x1         0x2         11:22:33:44:55:66     *        eth0
"""
    m = _parse_proc_net_arp(txt)
    assert "192.168.2.3" not in m
    assert m["192.168.2.4"] == "11:22:33:44:55:66"


def test_parse_ip_neigh_lladdr() -> None:
    txt = (
        "192.168.3.1 dev eth0 lladdr aa:bb:cc:dd:ee:ff REACHABLE\n"
        "fe80::1 dev eth0 lladdr 00:11:22:33:44:55 router STALE\n"
    )
    m = _parse_ip_neigh_output(txt)
    assert m == {"192.168.3.1": "aa:bb:cc:dd:ee:ff"}
