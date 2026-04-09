import { apiDelete, apiGet, apiPatch, apiPost } from "@/lib/api";
import type { Ipv4Prefix, Ipv4PrefixExplore, SubnetScan, SubnetScanDetail } from "./types";

const P = "/api/v1/ipam";

export function listIpv4Prefixes(siteId?: number): Promise<Ipv4Prefix[]> {
  const q = siteId != null ? `?site_id=${encodeURIComponent(String(siteId))}` : "";
  return apiGet(`${P}/ipv4-prefixes${q}`);
}

export function getIpv4PrefixExplore(prefixId: number): Promise<Ipv4PrefixExplore> {
  return apiGet(`${P}/ipv4-prefixes/${prefixId}/explore`);
}

export function createIpv4Prefix(body: {
  site_id: number;
  name: string;
  cidr: string;
  description?: string | null;
}): Promise<Ipv4Prefix> {
  return apiPost(`${P}/ipv4-prefixes`, body);
}

export function updateIpv4Prefix(
  id: number,
  body: { name?: string; cidr?: string; description?: string | null },
): Promise<Ipv4Prefix> {
  return apiPatch(`${P}/ipv4-prefixes/${id}`, body);
}

export function deleteIpv4Prefix(id: number): Promise<void> {
  return apiDelete(`${P}/ipv4-prefixes/${id}`);
}

export function listSubnetScans(params?: {
  site_id?: number;
  ipv4_prefix_id?: number;
  limit?: number;
}): Promise<SubnetScan[]> {
  const q = new URLSearchParams();
  if (params?.site_id != null) q.set("site_id", String(params.site_id));
  if (params?.ipv4_prefix_id != null) q.set("ipv4_prefix_id", String(params.ipv4_prefix_id));
  if (params?.limit != null) q.set("limit", String(params.limit));
  const s = q.toString();
  return apiGet(`${P}/subnet-scans${s ? `?${s}` : ""}`);
}

export function createSubnetScan(ipv4_prefix_id: number): Promise<SubnetScan> {
  return apiPost(`${P}/subnet-scans`, { ipv4_prefix_id });
}

export function getSubnetScan(scanId: number): Promise<SubnetScanDetail> {
  return apiGet(`${P}/subnet-scans/${scanId}`);
}
