import type { DeviceInterface } from "./types";

/** Dybde ut fra tre-rekkefølge (forelder alltid før barn i liste fra API). */
export function interfaceDepthByInterfaceList(rows: DeviceInterface[]): Map<number, number> {
  const m = new Map<number, number>();
  for (const r of rows) {
    const p = r.parent_interface_id;
    const depth = p == null ? 0 : (m.get(p) ?? 0) + 1;
    m.set(r.id, depth);
  }
  return m;
}

export function interfaceIndentedName(x: DeviceInterface, depthById: Map<number, number>): string {
  const d = depthById.get(x.id) ?? 0;
  return `${"\u00A0\u00A0".repeat(d)}${x.name}`;
}
