import { describe, expect, it } from "vitest";
import { buildSiteCards, ipv4Inventory, siteInitials, topPrefixesByUsage } from "./dashboardUtils";
import type { Ipv4Prefix } from "@/features/ipam/types";
import type { Rack, Room, Site } from "@/features/dcim/types";

function prefix(partial: Partial<Ipv4Prefix> & Pick<Ipv4Prefix, "id" | "cidr" | "used_count" | "address_total">): Ipv4Prefix {
  return {
    site_id: 1,
    name: partial.cidr,
    slug: partial.cidr,
    description: null,
    created_at: "",
    ...partial,
  };
}

describe("dashboard summaries", () => {
  it("counts rooms and racks per site", () => {
    const sites = [
      { id: 1, tenant_id: 0, name: "Oslo", slug: "osl", description: null, created_at: "" },
    ] as Site[];
    const rooms = [
      {
        id: 10,
        site_id: 1,
        building_id: null,
        wing_id: null,
        floor_id: null,
        name: "A",
        description: null,
        floor: null,
        has_floorplan: false,
      },
    ] as Room[];
    const racks = [{ id: 1, room_id: 10, name: "R1", u_height: 42, sort_order: 0 }] as Rack[];
    expect(buildSiteCards(sites, rooms, racks)[0]).toMatchObject({ rooms: 1, racks: 1 });
  });

  it("orders prefixes by utilization", () => {
    const list = [
      prefix({ id: 1, cidr: "10.0.0.0/24", used_count: 10, address_total: 256 }),
      prefix({ id: 2, cidr: "10.1.0.0/24", used_count: 200, address_total: 256 }),
    ];
    expect(topPrefixesByUsage(list, 1)[0]?.id).toBe(2);
  });

  it("sums IPv4 inventory", () => {
    const inv = ipv4Inventory([
      prefix({ id: 1, cidr: "10.0.0.0/24", used_count: 10, address_total: 100 }),
      prefix({ id: 2, cidr: "10.1.0.0/24", used_count: 20, address_total: 100 }),
    ]);
    expect(inv).toEqual({ used: 30, total: 200, pct: 15 });
  });

  it("builds site initials", () => {
    expect(siteInitials("Oslo DC")).toBe("OD");
    expect(siteInitials("Hitra")).toBe("HI");
  });
});
