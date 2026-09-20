import { describe, expect, it } from "vitest";
import { canPlaceDeviceAt, findPlacementIssues, firstFitU, occupiedUnitsForRack } from "./rackUtils";
import type { DeviceInstance, DeviceModel, RackPlacement } from "./types";

function dev(id: number, modelId: number): DeviceInstance {
  return {
    id,
    device_model_id: modelId,
    device_type_id: null,
    effective_device_type_id: null,
    site_id: null,
    effective_site_id: null,
    name: `d${id}`,
    serial_number: null,
    asset_tag: null,
    attributes: {},
  };
}

function model(id: number, u: number): DeviceModel {
  return {
    id,
    manufacturer_id: null,
    device_type_id: null,
    name: `m${id}`,
    u_height: u,
    form_factor: null,
    image_front_url: null,
    image_back_url: null,
    image_product_url: null,
    has_image_front_file: false,
    has_image_back_file: false,
    has_image_product_file: false,
    snmp_sys_object_id_prefix: null,
  };
}

describe("rack occupancy", () => {
  const models = new Map([[1, model(1, 2)]]);
  const devices = new Map([[10, dev(10, 1)]]);
  const placements: RackPlacement[] = [{ id: 1, rack_id: 5, device_id: 10, u_position: 1, mounting: "front" }];

  it("counts occupied units", () => {
    const s = occupiedUnitsForRack(placements, 5, devices, models);
    expect([...s].sort((a, b) => a - b)).toEqual([1, 2]);
  });

  it("finds first fit above a 2U unit", () => {
    expect(firstFitU(42, 2, [{ bottom: 1, top: 2 }])).toBe(3);
  });

  it("rejects overlap", () => {
    expect(canPlaceDeviceAt(2, 2, 42, [{ bottom: 1, top: 2 }])).toBe(false);
  });

  it("flags overlapping placements", () => {
    const extra: RackPlacement[] = [
      ...placements,
      { id: 2, rack_id: 5, device_id: 10, u_position: 2, mounting: "rear" },
    ];
    const issues = findPlacementIssues(extra, [{ id: 5, u_height: 42 }], devices, models);
    expect(issues.some((i) => i.kind === "overlap")).toBe(true);
  });
});
