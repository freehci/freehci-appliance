"""Normalize NetBox Device Type Library component templates into FreeHCI fields."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class NormalizedTemplate:
    normalized: dict[str, Any]
    quality_score: int
    warnings: list[str]


_SPEED_PATTERNS: list[tuple[re.Pattern[str], int]] = [
    (re.compile(r"(^|[^0-9])800g"), 800000),
    (re.compile(r"(^|[^0-9])400g"), 400000),
    (re.compile(r"(^|[^0-9])200g"), 200000),
    (re.compile(r"(^|[^0-9])100g"), 100000),
    (re.compile(r"(^|[^0-9])50g"), 50000),
    (re.compile(r"(^|[^0-9])40g"), 40000),
    (re.compile(r"(^|[^0-9])25g"), 25000),
    (re.compile(r"(^|[^0-9])10g"), 10000),
    (re.compile(r"(^|[^0-9])5g"), 5000),
    (re.compile(r"(^|[^0-9])2\.?5g"), 2500),
    (re.compile(r"(^|[^0-9])1000base|1g"), 1000),
    (re.compile(r"(^|[^0-9])100base|100m"), 100),
    (re.compile(r"(^|[^0-9])10base|10m"), 10),
]

_FORM_FACTOR_MAP = {
    "sfp": "sfp",
    "sfp+": "sfp+",
    "sfp28": "sfp28",
    "qsfp": "qsfp",
    "qsfp+": "qsfp+",
    "qsfp28": "qsfp28",
    "qsfp56": "qsfp56",
    "qsfp-dd": "qsfp-dd",
    "rj45": "rj45",
    "8p8c": "rj45",
}

_CONNECTOR_HINTS = {
    "c13": "iec-60320-c13",
    "c14": "iec-60320-c14",
    "c19": "iec-60320-c19",
    "c20": "iec-60320-c20",
    "nema": "nema",
    "usb": "usb",
    "rj45": "rj45",
    "de-9": "de-9",
    "db-9": "de-9",
    "8p8c": "rj45",
}


def normalize_template(component_type: str, raw: dict[str, Any]) -> NormalizedTemplate:
    warnings: list[str] = []
    normalized: dict[str, Any] = {
        "source": "netbox_dtl",
        "component_type": component_type,
        "name": _string(raw.get("name")),
        "label": _string(raw.get("label")),
        "description": _string(raw.get("description")),
    }
    if component_type == "interfaces":
        _normalize_interface(raw, normalized, warnings)
    elif component_type in {"front-ports", "rear-ports"}:
        _normalize_panel_port(component_type, raw, normalized, warnings)
    elif component_type in {"power-ports", "power-outlets"}:
        _normalize_power(component_type, raw, normalized, warnings)
    elif component_type in {"console-ports", "console-server-ports"}:
        _normalize_console(component_type, raw, normalized, warnings)
    elif component_type in {"module-bays", "device-bays"}:
        _normalize_bay(component_type, raw, normalized, warnings)
    elif component_type == "inventory-items":
        _normalize_inventory_item(raw, normalized, warnings)
    else:
        warnings.append(f"unknown_component_type:{component_type}")
    _common_required(raw, normalized, warnings)
    return NormalizedTemplate(normalized=_strip_none(normalized), quality_score=_quality_score(normalized, warnings), warnings=warnings)


def _normalize_interface(raw: dict[str, Any], out: dict[str, Any], warnings: list[str]) -> None:
    typ = _string(raw.get("type"))
    out["netbox_type"] = typ
    out["enabled"] = bool(raw.get("enabled", True))
    out["mgmt_only"] = bool(raw.get("mgmt_only", False))
    out["poe_mode"] = _string(raw.get("poe_mode"))
    out["poe_type"] = _string(raw.get("poe_type"))
    out["bridge"] = _string(raw.get("bridge"))
    out["rf_role"] = _string(raw.get("rf_role"))
    out["speed_mbps"] = _speed_from_type(typ)
    out["media_type"] = _media_type(typ)
    out["form_factor"] = _form_factor(typ)
    out["role"] = "management" if out["mgmt_only"] else "data"
    if typ and out["speed_mbps"] is None and out["media_type"] != "virtual":
        warnings.append(f"unknown_interface_type:{typ}")


def _normalize_panel_port(component_type: str, raw: dict[str, Any], out: dict[str, Any], warnings: list[str]) -> None:
    typ = _string(raw.get("type"))
    out["netbox_type"] = typ
    out["media_type"] = _media_type(typ)
    out["connector_type"] = _connector_type(typ)
    out["color"] = _string(raw.get("color"))
    out["rear_port"] = _string(raw.get("rear_port"))
    out["rear_port_position"] = _int(raw.get("rear_port_position"))
    out["positions"] = _int(raw.get("positions"))
    if component_type == "front-ports" and not out["rear_port"]:
        warnings.append("missing_rear_port")
    if typ and out["connector_type"] is None and out["media_type"] == "unknown":
        warnings.append(f"unknown_port_type:{typ}")


def _normalize_power(component_type: str, raw: dict[str, Any], out: dict[str, Any], warnings: list[str]) -> None:
    typ = _string(raw.get("type"))
    out["netbox_type"] = typ
    out["connector_type"] = _connector_type(typ)
    out["maximum_draw_watts"] = _int(raw.get("maximum_draw"))
    out["allocated_draw_watts"] = _int(raw.get("allocated_draw"))
    out["power_port"] = _string(raw.get("power_port"))
    out["feed_leg"] = _string(raw.get("feed_leg"))
    if component_type == "power-outlets" and not out["power_port"]:
        warnings.append("missing_power_port")
    if typ and out["connector_type"] is None:
        warnings.append(f"unknown_power_connector:{typ}")
    for key in ("maximum_draw", "allocated_draw"):
        if raw.get(key) is not None and _int(raw.get(key)) is None:
            warnings.append(f"invalid_{key}")


def _normalize_console(component_type: str, raw: dict[str, Any], out: dict[str, Any], warnings: list[str]) -> None:
    typ = _string(raw.get("type"))
    out["netbox_type"] = typ
    out["connector_type"] = _connector_type(typ)
    out["role"] = "server" if component_type == "console-server-ports" else "device"
    if typ and out["connector_type"] is None:
        warnings.append(f"unknown_console_connector:{typ}")


def _normalize_bay(component_type: str, raw: dict[str, Any], out: dict[str, Any], warnings: list[str]) -> None:
    out["position"] = _string(raw.get("position"))
    out["role"] = "module" if component_type == "module-bays" else "device"
    if component_type == "module-bays" and not out["position"]:
        warnings.append("missing_position")


def _normalize_inventory_item(raw: dict[str, Any], out: dict[str, Any], warnings: list[str]) -> None:
    out["manufacturer_name"] = _string(raw.get("manufacturer"))
    out["part_number"] = _string(raw.get("part_id"))
    out["component_defaults"] = _strip_none(
        {
            "name": out.get("name"),
            "manufacturer_name": out.get("manufacturer_name"),
            "part_number": out.get("part_number"),
            "description": out.get("description"),
        }
    )
    if not out.get("part_number") and not out.get("manufacturer_name"):
        warnings.append("weak_inventory_identity")


def _common_required(raw: dict[str, Any], out: dict[str, Any], warnings: list[str]) -> None:
    if not out.get("name"):
        warnings.append("missing_name")
    if raw.get("type") is None and out.get("component_type") not in {"module-bays", "device-bays", "inventory-items"}:
        warnings.append("missing_type")


def _speed_from_type(value: str | None) -> int | None:
    if not value:
        return None
    normalized = value.lower().replace("_", "-")
    for pattern, speed in _SPEED_PATTERNS:
        if pattern.search(normalized):
            return speed
    return None


def _media_type(value: str | None) -> str:
    if not value:
        return "unknown"
    v = value.lower()
    if any(token in v for token in ("sfp", "qsfp", "fiber", "100gbase-x", "40gbase-x")):
        return "fiber"
    if any(token in v for token in ("base-t", "rj45", "8p8c", "1000base-t", "10gbase-t")):
        return "copper"
    if any(token in v for token in ("lag", "virtual", "bridge", "vlan")):
        return "virtual"
    if "wireless" in v or "ieee802.11" in v:
        return "wireless"
    return "unknown"


def _form_factor(value: str | None) -> str | None:
    if not value:
        return None
    v = value.lower()
    for needle, form_factor in _FORM_FACTOR_MAP.items():
        if needle in v:
            return form_factor
    return None


def _connector_type(value: str | None) -> str | None:
    if not value:
        return None
    v = value.lower()
    for needle, connector in _CONNECTOR_HINTS.items():
        if needle in v:
            return connector
    if v.strip():
        return v.strip()
    return None


def _int(value: object) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _string(value: object) -> str | None:
    if value is None:
        return None
    s = str(value).strip()
    return s or None


def _strip_none(value: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in value.items() if v is not None}


def _quality_score(normalized: dict[str, Any], warnings: list[str]) -> int:
    score = 100 - (len(warnings) * 15)
    if normalized.get("media_type") == "unknown":
        score -= 10
    if not normalized.get("name"):
        score -= 25
    return max(0, min(100, score))
