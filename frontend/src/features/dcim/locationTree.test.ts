import { describe, expect, it } from "vitest";
import { buildLocationTree, filterLocationTree, flattenLocationTree } from "./locationTree";
import type { Building, Floor, Room, Site, Wing } from "./types";

function site(id: number, name: string): Site {
  return {
    id,
    tenant_id: 1,
    name,
    slug: name.toLowerCase(),
    description: null,
    created_at: "2026-01-01T00:00:00Z",
  };
}

function building(id: number, siteId: number, name: string): Building {
  return { id, site_id: siteId, name, slug: name.toLowerCase(), description: null };
}

function wing(id: number, buildingId: number, name: string): Wing {
  return { id, building_id: buildingId, name, slug: name.toLowerCase(), description: null };
}

function floor(id: number, buildingId: number, name: string, wingId: number | null = null, level = 1): Floor {
  return { id, building_id: buildingId, wing_id: wingId, name, slug: name.toLowerCase(), level, description: null };
}

function room(
  id: number,
  siteId: number,
  name: string,
  extra: Partial<Pick<Room, "building_id" | "wing_id" | "floor_id">> = {},
): Room {
  return {
    id,
    site_id: siteId,
    building_id: extra.building_id ?? null,
    wing_id: extra.wing_id ?? null,
    floor_id: extra.floor_id ?? null,
    name,
    description: null,
    floor: null,
    has_floorplan: false,
  };
}

describe("buildLocationTree", () => {
  it("nests building, optional wing, floor and room under a site", () => {
    const tree = buildLocationTree(
      [site(1, "Oslo")],
      [building(10, 1, "A")],
      [wing(20, 10, "North")],
      [floor(30, 10, "2", 20, 2), floor(31, 10, "1", null, 1)],
      [
        room(40, 1, "201", { building_id: 10, wing_id: 20, floor_id: 30 }),
        room(41, 1, "Lobby", { building_id: 10 }),
        room(42, 1, "Yard"),
      ],
    );

    expect(tree).toHaveLength(1);
    expect(tree[0].href).toBe("/dcim/sites/1");
    expect(tree[0].children.map((c) => c.name)).toEqual(["A", "Yard"]);
    const b = tree[0].children[0];
    expect(b.href).toBe("/dcim/sites/1/buildings/10");
    expect(b.children.map((c) => `${c.kind}:${c.name}`)).toEqual(["wing:North", "floor:1", "room:Lobby"]);
    expect(b.children[0].children[0]).toMatchObject({ kind: "floor", name: "2", extra: "2" });
    expect(b.children[0].children[0].children[0]).toMatchObject({ kind: "room", name: "201", href: "/dcim/rooms/40" });
  });

  it("lets rooms skip unused levels", () => {
    const tree = buildLocationTree(
      [site(1, "Site")],
      [],
      [],
      [],
      [room(9, 1, "Hall")],
    );
    expect(tree[0].children).toEqual([
      expect.objectContaining({ kind: "room", name: "Hall", href: "/dcim/rooms/9" }),
    ]);
  });
});

describe("filterLocationTree", () => {
  it("keeps ancestors of a matching room so buildings stay visible without site-id", () => {
    const tree = buildLocationTree(
      [site(1, "Oslo"), site(2, "Bergen")],
      [building(10, 1, "Warehouse")],
      [],
      [floor(30, 10, "Kjeller", null, -1)],
      [room(40, 1, "Cold room", { building_id: 10, floor_id: 30 })],
    );
    const filtered = filterLocationTree(tree, "cold");
    expect(filtered.map((n) => n.name)).toEqual(["Oslo"]);
    expect(flattenLocationTree(filtered).map((r) => r.node.name)).toEqual([
      "Oslo",
      "Warehouse",
      "Kjeller",
      "Cold room",
    ]);
  });
});
