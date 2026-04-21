import { describe, expect, it } from "vitest";
import {
  buildPrefixTreeIndex,
  immediateParentFor,
  ipv4EqualSplitOptions,
  splitIpv4IntoHalves,
} from "./ipv4PrefixTree";
import type { Ipv4Prefix } from "./types";

function p(
  id: number,
  site_id: number,
  name: string,
  cidr: string,
  overrides: Partial<Ipv4Prefix> = {},
): Ipv4Prefix {
  return {
    id,
    site_id,
    tenant_id: null,
    vlan_id: null,
    vrf_id: null,
    name,
    cidr,
    description: null,
    created_at: "2026-01-01T00:00:00Z",
    used_count: 0,
    address_total: 256,
    subnet_services: null,
    ...overrides,
  };
}

describe("splitIpv4IntoHalves", () => {
  it("splits /24 into two /25", () => {
    const h = splitIpv4IntoHalves("10.27.13.0/24");
    expect(h).toEqual(["10.27.13.0/25", "10.27.13.128/25"]);
  });

  it("returns null for /32", () => {
    expect(splitIpv4IntoHalves("10.0.0.1/32")).toBeNull();
  });
});

describe("ipv4EqualSplitOptions", () => {
  it("lists /25 through /32 for /24 and caps at 256 subnets", () => {
    const o = ipv4EqualSplitOptions("10.0.0.0/24");
    expect(o[0]).toMatchObject({ newPrefixLen: 25, subnetCount: 2 });
    expect(o[o.length - 1]).toMatchObject({ newPrefixLen: 32, subnetCount: 256 });
    expect(o).toHaveLength(8);
    const m = o.find((x) => x.newPrefixLen === 31);
    expect(m?.rfc3021).toBe(true);
    expect(m?.label).toContain("RFC 3021");
  });

  it("returns empty for /32", () => {
    expect(ipv4EqualSplitOptions("10.0.0.1/32")).toEqual([]);
  });
});

describe("prefix tree", () => {
  it("assigns immediate parent and roots", () => {
    const site = 1;
    const root = p(1, site, "R", "10.27.13.0/24");
    const a = p(2, site, "A", "10.27.13.0/25");
    const b = p(3, site, "B", "10.27.13.128/25");
    const s = p(4, site, "S", "10.27.13.0/26");
    const all = [root, a, b, s];
    expect(immediateParentFor(a, all)?.id).toBe(1);
    expect(immediateParentFor(b, all)?.id).toBe(1);
    expect(immediateParentFor(s, all)?.id).toBe(2);
    const { roots, childrenByParentId } = buildPrefixTreeIndex(all);
    expect(roots.map((r) => r.id)).toEqual([1]);
    expect((childrenByParentId.get(1) ?? []).map((c) => c.id).sort()).toEqual([2, 3]);
    expect((childrenByParentId.get(2) ?? []).map((c) => c.id)).toEqual([4]);
  });
});
