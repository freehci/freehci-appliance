"""32-bit AS-nummer (RFC 6793 / RFC 6996)."""

from __future__ import annotations

_MIN_ASN = 1
_MAX_ASN = 4_294_967_294
_RESERVED = frozenset({0, 65_535, 4_294_967_295})


def is_private_asn(asn: int) -> bool:
    return 64_512 <= asn <= 65_534 or 4_200_000_000 <= asn <= 4_294_967_294


def normalize_asn(value: int) -> int:
    asn = int(value)
    if asn in _RESERVED or asn < _MIN_ASN or asn > _MAX_ASN:
        raise ValueError("ASN må være 1–4294967294 (ikke reservert 0/65535/4294967295)")
    return asn
