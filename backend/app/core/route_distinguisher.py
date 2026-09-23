"""Validering av BGP route distinguisher (RFC 4364)."""

from __future__ import annotations

import ipaddress
import re

_ASN_ASSIGNED = re.compile(r"^(\d{1,10}):(\d{1,10})$")
_IPV4_ASSIGNED = re.compile(r"^(\d{1,3}(?:\.\d{1,3}){3}):(\d{1,5})$")

_MAX_ASN16 = 65_535
_MAX_ASN32 = 4_294_967_295


def normalize_route_distinguisher(value: str | None) -> str | None:
    """Returner kanonisk RD, eller None hvis tomt.

    Godkjente former:
    - Type 0: `ASN:nn` med 16-bit ASN og 32-bit assigned (`65000:1`)
    - Type 2: `ASN:nn` med 32-bit ASN og 16-bit assigned (`4200000000:1`)
    - Type 1: `IPv4:nn` med 16-bit assigned (`192.0.2.1:100`)
    """
    if value is None:
        return None
    s = value.strip()
    if not s:
        return None

    m4 = _IPV4_ASSIGNED.fullmatch(s)
    if m4 is not None:
        ip_s, num_s = m4.group(1), m4.group(2)
        try:
            ip = ipaddress.IPv4Address(ip_s)
        except ValueError as e:
            raise ValueError("RD IPv4-adresse er ugyldig") from e
        assigned = int(num_s)
        if assigned > _MAX_ASN16:
            raise ValueError("RD type 1 (IPv4:nn) tillater assigned 0–65535")
        return f"{ip}:{assigned}"

    m = _ASN_ASSIGNED.fullmatch(s)
    if m is None:
        raise ValueError("RD må være ASN:nn (f.eks. 65000:1) eller IPv4:nn (f.eks. 192.0.2.1:100)")

    asn = int(m.group(1))
    assigned = int(m.group(2))
    if asn > _MAX_ASN32:
        raise ValueError("RD ASN kan ikke være større enn 4294967295")
    if asn <= _MAX_ASN16:
        if assigned > _MAX_ASN32:
            raise ValueError("RD type 0 (16-bit ASN) tillater assigned 0–4294967295")
    elif assigned > _MAX_ASN16:
        raise ValueError("RD type 2 (32-bit ASN) tillater assigned 0–65535")
    return f"{asn}:{assigned}"


def normalize_route_target(value: str | None) -> str | None:
    """Samme RFC 4364-form som RD, men RT er ikke RD."""
    try:
        return normalize_route_distinguisher(value)
    except ValueError as e:
        raise ValueError(str(e).replace("RD", "RT")) from e
