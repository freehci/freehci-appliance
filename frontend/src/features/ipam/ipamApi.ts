import { apiDelete, apiGet, apiPost } from "@/lib/api";
import type { Ipv4Prefix } from "./types";

const P = "/api/v1/ipam";

export function listIpv4Prefixes(siteId?: number): Promise<Ipv4Prefix[]> {
  const q = siteId != null ? `?site_id=${encodeURIComponent(String(siteId))}` : "";
  return apiGet(`${P}/ipv4-prefixes${q}`);
}

export function createIpv4Prefix(body: {
  site_id: number;
  name: string;
  cidr: string;
  description?: string | null;
}): Promise<Ipv4Prefix> {
  return apiPost(`${P}/ipv4-prefixes`, body);
}

export function deleteIpv4Prefix(id: number): Promise<void> {
  return apiDelete(`${P}/ipv4-prefixes/${id}`);
}
