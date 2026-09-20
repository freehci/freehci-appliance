import type { DeviceInstance, DeviceModel, RackPlacement } from "./types";

export function deviceUHeight(device: DeviceInstance, modelsById: Map<number, DeviceModel>): number {
  if (device.device_model_id == null) return 1;
  const uh = modelsById.get(device.device_model_id)?.u_height;
  if (uh === undefined) return 1;
  return uh;
}

/** u_position on placement = bottom RU (inclusive). */
export function occupiesRange(bottom: number, uH: number): { bottom: number; top: number } {
  return { bottom, top: bottom + uH - 1 };
}

function rangesOverlap(a1: number, a2: number, b1: number, b2: number): boolean {
  return !(a2 < b1 || b2 < a1);
}

export function existingRangesForRack(
  placements: RackPlacement[],
  rackId: number,
  devicesById: Map<number, DeviceInstance>,
  modelsById: Map<number, DeviceModel>,
  excludePlacementId?: number,
): { bottom: number; top: number }[] {
  const out: { bottom: number; top: number }[] = [];
  for (const p of placements) {
    if (p.rack_id !== rackId) continue;
    if (excludePlacementId != null && p.id === excludePlacementId) continue;
    const dev = devicesById.get(p.device_id);
    if (!dev) continue;
    const h = deviceUHeight(dev, modelsById);
    if (h === 0) continue;
    out.push(occupiesRange(p.u_position, h));
  }
  return out;
}

export function canPlaceDeviceAt(
  uBottom: number,
  deviceU: number,
  rackUHeight: number,
  existing: { bottom: number; top: number }[],
): boolean {
  if (deviceU === 0) {
    return uBottom === 0;
  }
  if (uBottom < 1 || deviceU < 1) return false;
  const top = uBottom + deviceU - 1;
  if (top > rackUHeight) return false;
  for (const o of existing) {
    if (rangesOverlap(uBottom, top, o.bottom, o.top)) return false;
  }
  return true;
}

export function occupiedUnitsForRack(
  placements: RackPlacement[],
  rackId: number,
  devicesById: Map<number, DeviceInstance>,
  modelsById: Map<number, DeviceModel>,
): Set<number> {
  const occupied = new Set<number>();
  for (const p of placements) {
    if (p.rack_id !== rackId) continue;
    const dev = devicesById.get(p.device_id);
    if (!dev) continue;
    const h = deviceUHeight(dev, modelsById);
    if (h === 0) continue;
    const { bottom, top } = occupiesRange(p.u_position, h);
    for (let u = bottom; u <= top; u += 1) occupied.add(u);
  }
  return occupied;
}

export type PlacementIssue = {
  placementId: number;
  kind: "overlap" | "out_of_range";
};

/** Overlapp eller U utenfor rackhøyde (0U ignoreres for overslagsjekk). */
export function findPlacementIssues(
  placements: RackPlacement[],
  racks: { id: number; u_height: number }[],
  devicesById: Map<number, DeviceInstance>,
  modelsById: Map<number, DeviceModel>,
): PlacementIssue[] {
  const rackH = new Map(racks.map((r) => [r.id, r.u_height]));
  const issues: PlacementIssue[] = [];
  const byRack = new Map<number, RackPlacement[]>();
  for (const p of placements) {
    const arr = byRack.get(p.rack_id) ?? [];
    arr.push(p);
    byRack.set(p.rack_id, arr);
  }
  for (const [rackId, list] of byRack) {
    const n = rackH.get(rackId);
    if (n == null) continue;
    const ranges: { id: number; bottom: number; top: number }[] = [];
    for (const p of list) {
      const dev = devicesById.get(p.device_id);
      if (!dev) continue;
      const h = deviceUHeight(dev, modelsById);
      if (h === 0) {
        if (p.u_position !== 0) issues.push({ placementId: p.id, kind: "out_of_range" });
        continue;
      }
      const { bottom, top } = occupiesRange(p.u_position, h);
      if (bottom < 1 || top > n) issues.push({ placementId: p.id, kind: "out_of_range" });
      ranges.push({ id: p.id, bottom, top });
    }
    for (let i = 0; i < ranges.length; i += 1) {
      for (let j = i + 1; j < ranges.length; j += 1) {
        const a = ranges[i]!;
        const b = ranges[j]!;
        if (!(a.top < b.bottom || b.top < a.bottom)) {
          issues.push({ placementId: a.id, kind: "overlap" });
          issues.push({ placementId: b.id, kind: "overlap" });
        }
      }
    }
  }
  const seen = new Set<string>();
  return issues.filter((x) => {
    const k = `${x.placementId}:${x.kind}`;
    if (seen.has(k)) return false;
    seen.add(k);
    return true;
  });
}

export function firstFitU(
  rackUHeight: number,
  deviceU: number,
  existing: { bottom: number; top: number }[],
): number | null {
  if (deviceU === 0) return 0;
  for (let u = 1; u <= rackUHeight - deviceU + 1; u += 1) {
    if (canPlaceDeviceAt(u, deviceU, rackUHeight, existing)) return u;
  }
  return null;
}

/** CSS grid row from top (1 = top of rack = highest U). */
export function gridRowStartForPlacement(n: number, uBottom: number, uHeight: number): number {
  const topRu = uBottom + uHeight - 1;
  return n - topRu + 1;
}

function isInsideAnyRange(u: number, ranges: { bottom: number; top: number }[]): boolean {
  for (const r of ranges) {
    if (u >= r.bottom && u <= r.top) return true;
  }
  return false;
}

export { isInsideAnyRange };

/** EIA RU height used to convert wall-mount elevation to visual U offset. */
export const MM_PER_U = 44.45;

export type RackScaleInput = {
  u_height: number;
  mounting?: string | null;
  elevation_mm?: number | null;
};

export function rackMounting(rack: { mounting?: string | null }): "floor" | "wall" {
  return rack.mounting === "wall" ? "wall" : "floor";
}

/** Visual U-offset from floor to the bottom of a wall-mounted rack. */
export function rackElevationU(rack: RackScaleInput): number {
  if (rackMounting(rack) !== "wall" || rack.elevation_mm == null || rack.elevation_mm <= 0) return 0;
  return rack.elevation_mm / MM_PER_U;
}

/** Shared column height in U so mixed 15U/42U racks keep the same unit size. */
export function rackColumnU(racks: RackScaleInput[]): number {
  let max = 1;
  for (const r of racks) {
    const top = r.u_height + rackElevationU(r);
    if (top > max) max = top;
  }
  return max;
}
