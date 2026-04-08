import type { DeviceInstance, DeviceModel, RackPlacement } from "./types";

export function deviceUHeight(device: DeviceInstance, modelsById: Map<number, DeviceModel>): number {
  if (device.device_model_id == null) return 1;
  return modelsById.get(device.device_model_id)?.u_height ?? 1;
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
  if (uBottom < 1 || deviceU < 1) return false;
  const top = uBottom + deviceU - 1;
  if (top > rackUHeight) return false;
  for (const o of existing) {
    if (rangesOverlap(uBottom, top, o.bottom, o.top)) return false;
  }
  return true;
}
