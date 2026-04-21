import type { Ipv4Prefix } from "./types";

/** Parsed IPv4 CIDR (nettverksadresse som uint32, inkl. nett og broadcast-intervall). */
export type ParsedIpv4 = { first: number; last: number; prefixLen: number };

function ipv4OctetsToUint32(parts: string[]): number | null {
  if (parts.length !== 4) return null;
  let n = 0;
  for (const p of parts) {
    const x = Number(p);
    if (!Number.isInteger(x) || x < 0 || x > 255) return null;
    n = ((n << 8) >>> 0) + x;
  }
  return n >>> 0;
}

/** Tolker kanonisk IPv4 CIDR til nettverks-adresse og prefikslengde. */
export function parseIpv4Cidr(cidr: string): ParsedIpv4 | null {
  const s = cidr.trim();
  const slash = s.indexOf("/");
  if (slash < 0) return null;
  const hostPart = s.slice(0, slash);
  const len = Number(s.slice(slash + 1));
  if (!Number.isFinite(len) || len < 0 || len > 32) return null;
  const octets = hostPart.split(".");
  if (octets.length !== 4) return null;
  const addr = ipv4OctetsToUint32(octets);
  if (addr == null) return null;
  if (len === 0) {
    return { first: 0, last: 0xffffffff, prefixLen: 0 };
  }
  if (len === 32) {
    return { first: addr >>> 0, last: addr >>> 0, prefixLen: 32 };
  }
  const hostBits = 32 - len;
  const mask = ((0xffffffff << (32 - len)) >>> 0) >>> 0;
  const first = (addr & mask) >>> 0;
  const last = (first + ((1 << hostBits) >>> 0) - 1) >>> 0;
  return { first, last, prefixLen: len };
}

export function intToIpv4(n: number): string {
  const x = n >>> 0;
  return `${(x >>> 24) & 255}.${(x >>> 16) & 255}.${(x >>> 8) & 255}.${x & 255}`;
}

export function formatIpv4Cidr(first: number, prefixLen: number): string {
  return `${intToIpv4(first)}/${prefixLen}`;
}

/** True hvis `inner` er lik eller strengere delnett av `outer`. */
export function subnetOf(outer: ParsedIpv4, inner: ParsedIpv4): boolean {
  return (
    inner.prefixLen >= outer.prefixLen &&
    inner.first >= outer.first &&
    inner.last <= outer.last
  );
}

/** Nærmeste omsluttende prefiks på samme site (strammeste supernett blant radene). */
export function immediateParentFor(child: Ipv4Prefix, sameSite: Ipv4Prefix[]): Ipv4Prefix | null {
  const c = parseIpv4Cidr(child.cidr);
  if (!c) return null;
  let best: Ipv4Prefix | null = null;
  let bestPl = -1;
  for (const p of sameSite) {
    if (p.id === child.id) continue;
    const P = parseIpv4Cidr(p.cidr);
    if (!P) continue;
    if (!subnetOf(P, c) || P.prefixLen >= c.prefixLen) continue;
    if (P.prefixLen > bestPl) {
      bestPl = P.prefixLen;
      best = p;
    }
  }
  return best;
}

function prefixTreeSortKey(p: Ipv4Prefix): [number, number, number] {
  const n = parseIpv4Cidr(p.cidr);
  if (!n) return [999, 0, p.id];
  return [n.prefixLen, n.first >>> 0, p.id];
}

function comparePrefixes(a: Ipv4Prefix, b: Ipv4Prefix): number {
  const ka = prefixTreeSortKey(a);
  const kb = prefixTreeSortKey(b);
  for (let i = 0; i < ka.length; i++) {
    if (ka[i] !== kb[i]) return ka[i]! - kb[i]!;
  }
  return 0;
}

export type PrefixTreeIndex = {
  roots: Ipv4Prefix[];
  childrenByParentId: Map<number, Ipv4Prefix[]>;
};

/** Bygger skog: røtter = prefiks uten forelder blant listeraden, barn grupperes på forelder-id. */
export function buildPrefixTreeIndex(prefs: Ipv4Prefix[]): PrefixTreeIndex {
  const bySite = new Map<number, Ipv4Prefix[]>();
  for (const p of prefs) {
    const arr = bySite.get(p.site_id) ?? [];
    arr.push(p);
    bySite.set(p.site_id, arr);
  }
  const childrenByParentId = new Map<number, Ipv4Prefix[]>();
  const roots: Ipv4Prefix[] = [];
  for (const sitePrefs of bySite.values()) {
    for (const c of sitePrefs) {
      const par = immediateParentFor(c, sitePrefs);
      if (par == null) roots.push(c);
      else {
        const ch = childrenByParentId.get(par.id) ?? [];
        ch.push(c);
        childrenByParentId.set(par.id, ch);
      }
    }
  }
  roots.sort(comparePrefixes);
  for (const ch of childrenByParentId.values()) {
    ch.sort(comparePrefixes);
  }
  return { roots, childrenByParentId };
}

export type PrefixTreeRow = {
  prefix: Ipv4Prefix;
  depth: number;
  hasChildren: boolean;
};

export function flattenVisiblePrefixTree(
  roots: Ipv4Prefix[],
  childrenByParentId: Map<number, Ipv4Prefix[]>,
  expandedIds: ReadonlySet<number>,
): PrefixTreeRow[] {
  const out: PrefixTreeRow[] = [];

  const walk = (nodes: Ipv4Prefix[], depth: number) => {
    for (const p of nodes) {
      const kids = childrenByParentId.get(p.id) ?? [];
      const hasChildren = kids.length > 0;
      out.push({ prefix: p, depth, hasChildren });
      if (hasChildren && expandedIds.has(p.id)) {
        walk(kids, depth + 1);
      }
    }
  };

  walk(roots, 0);
  return out;
}

/** Del IPv4-prefiks i to like store halvdeler (/n → to /(n+1)). */
export function splitIpv4IntoHalves(cidr: string): [string, string] | null {
  const p = parseIpv4Cidr(cidr);
  if (!p || p.prefixLen >= 32) return null;
  const newLen = p.prefixLen + 1;
  const hostBits = 32 - newLen;
  if (hostBits < 0) return null;
  const step = (1 << hostBits) >>> 0;
  const firstLow = p.first >>> 0;
  const firstHigh = (p.first + step) >>> 0;
  return [formatIpv4Cidr(firstLow, newLen), formatIpv4Cidr(firstHigh, newLen)];
}
