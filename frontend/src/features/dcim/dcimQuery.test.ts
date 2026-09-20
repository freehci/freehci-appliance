import { describe, expect, it } from "vitest";
import { asList, dcimKeys } from "./dcimQuery";

describe("dcim query keys", () => {
  it("keeps room list and room detail keys distinct for the same numeric id", () => {
    expect(dcimKeys.rooms(1)).not.toEqual(dcimKeys.room(1));
    expect(dcimKeys.buildings(1)).not.toEqual(dcimKeys.building(1));
    expect(dcimKeys.wings(1)).not.toEqual(dcimKeys.wing(1));
    expect(dcimKeys.floors({ buildingId: 1 })).not.toEqual(dcimKeys.floor(1));
  });

  it("treats a cached object as an empty list instead of crashing on filter", () => {
    const cachedRoom = { id: 1, name: "Hall A" };
    expect(asList(cachedRoom).filter(() => true)).toEqual([]);
    expect(asList([{ id: 2 }]).filter((x) => x.id === 2)).toEqual([{ id: 2 }]);
  });
});
