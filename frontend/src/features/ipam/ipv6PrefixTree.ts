import type { Ipv6Prefix } from "./types";
import type { EqualSplitOption } from "./ipv4PrefixTree";

export function parseIpv6PrefixLen(cidr: string): number | null {
  const slash = cidr.trim().lastIndexOf("/");
  if (slash < 0) return null;
  const n = Number(cidr.slice(slash + 1));
  if (!Number.isInteger(n) || n < 0 || n > 128) return null;
  return n;
}

export function ipv6EqualSplitOptions(cidr: string, maxSubnets = 256): EqualSplitOption[] {
  const pl = parseIpv6PrefixLen(cidr);
  if (pl == null || pl >= 128) return [];
  const out: EqualSplitOption[] = [];
  let subnetCount = 1;
  for (let newLen = pl + 1; newLen <= 128; newLen++) {
    subnetCount *= 2;
    if (subnetCount > maxSubnets) break;
    out.push({
      newPrefixLen: newLen,
      subnetCount,
      label: `/${String(newLen)} — ${String(subnetCount)}×`,
      rfc3021: false,
    });
  }
  return out;
}

export function buildIpv6ChildrenByParent(rows: Ipv6Prefix[]): {
  roots: Ipv6Prefix[];
  childrenByParentId: Map<number, Ipv6Prefix[]>;
} {
  const ids = new Set(rows.map((r) => r.id));
  const childrenByParentId = new Map<number, Ipv6Prefix[]>();
  const roots: Ipv6Prefix[] = [];
  const sorted = [...rows].sort((a, b) => a.cidr.localeCompare(b.cidr));
  for (const r of sorted) {
    const pid = r.parent_id != null && ids.has(r.parent_id) ? r.parent_id : null;
    if (pid == null) {
      roots.push(r);
      continue;
    }
    const kids = childrenByParentId.get(pid) ?? [];
    kids.push(r);
    childrenByParentId.set(pid, kids);
  }
  return { roots, childrenByParentId };
}

export function filterIpv6KeepingAncestors(
  all: Ipv6Prefix[],
  childrenByParentId: Map<number, Ipv6Prefix[]>,
  match: (p: Ipv6Prefix) => boolean,
): Ipv6Prefix[] {
  const parentOf = new Map<number, number>();
  for (const [pid, kids] of childrenByParentId) {
    for (const k of kids) parentOf.set(k.id, pid);
  }
  const keep = new Set<number>();
  for (const p of all) {
    if (!match(p)) continue;
    keep.add(p.id);
    let cur = parentOf.get(p.id);
    while (cur != null && !keep.has(cur)) {
      keep.add(cur);
      cur = parentOf.get(cur);
    }
  }
  return all.filter((p) => keep.has(p.id));
}

export function flattenIpv6Tree(
  roots: Ipv6Prefix[],
  childrenByParentId: Map<number, Ipv6Prefix[]>,
  expandedIds: Set<number>,
): { prefix: Ipv6Prefix; depth: number; hasChildren: boolean }[] {
  const out: { prefix: Ipv6Prefix; depth: number; hasChildren: boolean }[] = [];
  const walk = (nodes: Ipv6Prefix[], depth: number) => {
    for (const p of nodes) {
      const kids = childrenByParentId.get(p.id) ?? [];
      out.push({ prefix: p, depth, hasChildren: kids.length > 0 });
      if (kids.length > 0 && expandedIds.has(p.id)) walk(kids, depth + 1);
    }
  };
  walk(roots, 0);
  return out;
}
