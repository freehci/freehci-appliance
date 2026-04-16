"""Minimal Redfish-klient mot Dell iDRAC (PowerEdge)."""

from __future__ import annotations

from typing import Any

import httpx


def _pick_system_uri(systems_payload: dict[str, Any]) -> str | None:
    members = systems_payload.get("Members")
    if not isinstance(members, list) or not members:
        return None
    first = members[0]
    if isinstance(first, dict):
        ref = first.get("@odata.id")
        if isinstance(ref, str) and ref.startswith("/"):
            return ref
    if isinstance(first, str) and first.startswith("/"):
        return first
    return None


def fetch_idrac_hardware_summary(
    host: str,
    username: str,
    password: str,
    *,
    verify_tls: bool,
    timeout_s: float = 25.0,
) -> dict[str, Any]:
    """Hent System.Embedded.1 eller første system fra Redfish."""
    base = host.strip().rstrip("/")
    if not base.lower().startswith("https://"):
        base = f"https://{base}"
    auth = (username, password)
    with httpx.Client(verify=verify_tls, timeout=timeout_s) as client:
        sys_url = f"{base}/redfish/v1/Systems/System.Embedded.1"
        r = client.get(sys_url, auth=auth)
        if r.status_code == 404:
            col = client.get(f"{base}/redfish/v1/Systems", auth=auth)
            col.raise_for_status()
            uri = _pick_system_uri(col.json())
            if not uri:
                raise ValueError("Redfish Systems-kolleksjon er tom")
            sys_url = f"{base}{uri}" if uri.startswith("/") else f"{base}/{uri}"
            r = client.get(sys_url, auth=auth)
        r.raise_for_status()
        data = r.json()

    mem = data.get("MemorySummary")
    proc = data.get("ProcessorSummary")
    status = data.get("Status") if isinstance(data.get("Status"), dict) else {}
    health = status.get("HealthRollup") if isinstance(status, dict) else None

    return {
        "source": "dell.idrac.redfish",
        "redfish_system_uri": sys_url,
        "manufacturer": data.get("Manufacturer"),
        "model": data.get("Model"),
        "sku": data.get("SKU"),
        "serial_number": data.get("SerialNumber"),
        "bios_version": data.get("BiosVersion"),
        "host_name": data.get("HostName"),
        "power_state": data.get("PowerState"),
        "health_rollup": health,
        "memory_summary": mem if isinstance(mem, dict) else None,
        "processor_summary": proc if isinstance(proc, dict) else None,
    }
