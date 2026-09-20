import { describe, expect, it } from "vitest";
import { buildIpv6ChildrenByParent, filterIpv6KeepingAncestors } from "./ipv6PrefixTree";
import type { Ipv6Prefix } from "./types";

function p(id: number, cidr: string, name: string, parentId: number | null = null): Ipv6Prefix {
  return {
    id,
    site_id: 1,
    name,
    slug: name.toLowerCase(),
    cidr,
    parent_id: parentId,
    role: "active",
    status: "active",
    created_at: "2026-01-01T00:00:00Z",
  };
}

describe("filterIpv6KeepingAncestors", () => {
  it("keeps parent containers when a child name matches", () => {
    const rows = [p(1, "fd00::/48", "Root"), p(2, "fd00:1::/64", "Leaf", 1)];
    const tree = buildIpv6ChildrenByParent(rows);
    const filtered = filterIpv6KeepingAncestors(rows, tree.childrenByParentId, (x) => x.name === "Leaf");
    expect(filtered.map((x) => x.name)).toEqual(["Root", "Leaf"]);
  });
});
