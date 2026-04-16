"""Hjelpefunksjoner for out-of-band (iDRAC/iLO) mot DCIM-enheter."""

from __future__ import annotations

from typing import Any

from app.models.dcim import DeviceInstance


def _str_attr(attrs: dict[str, Any] | None, *keys: str) -> str | None:
    if not attrs:
        return None
    for k in keys:
        v = attrs.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return None


def resolve_oob_management_host(device: DeviceInstance) -> str | None:
    """Velg beste gjett på iDRAC/BMC-vertsnavn eller IP."""
    attrs = device.attributes if isinstance(device.attributes, dict) else None
    host = _str_attr(attrs, "idrac_host", "bmc_host", "ilo_host", "oob_host")
    if host:
        return host
    # BMC-navngitte grensesnitt
    for iface in device.interfaces or []:
        nl = (iface.name or "").casefold()
        if any(x in nl for x in ("idrac", "bmc", "ilo", "mgmt", "ipmi")):
            for ip in iface.ip_assignments or []:
                if ip.family == "ipv4" and ip.address:
                    return ip.address.strip()
    # Primær enhets-IPv4
    dev_ips = list(device.device_ip_assignments or [])
    dev_ips.sort(key=lambda a: (not a.is_primary, a.address))
    for ip in dev_ips:
        if ip.family == "ipv4" and ip.address:
            return ip.address.strip()
    return None


def resolve_idrac_credentials(device: DeviceInstance) -> tuple[str | None, str | None]:
    """Brukernavn/passord fra device.attributes (lagres kun i DB — ikke returner passord i API-svar)."""
    attrs = device.attributes if isinstance(device.attributes, dict) else None
    user = _str_attr(attrs, "idrac_username", "idrac_user", "bmc_username", "bmc_user")
    password = _str_attr(attrs, "idrac_password", "bmc_password")
    return user, password
