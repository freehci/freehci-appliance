import { apiDelete, apiGet, apiGetText, apiPatch, apiPost } from "@/lib/api";
import type {
  Ipv4Address,
  Ipv4AvailablePrefixes,
  Ipv4AvailableRanges,
  Ipv4Prefix,
  Ipv4PrefixExplore,
  Ipv4PrefixSplitEqualResponse,
  Ipv4PrefixSplitResponse,
  IpamAuditEvent,
  IpamCircuit,
  IpamCircuitTermination,
  IpamVlan,
  IpamVrf,
  IpamWebhook,
  IpamWebhookDelivery,
  PrefixAddressGridRead,
  PrefixDrift,
  SiteDrift,
  SubnetScan,
  SubnetScanDetail,
  User,
  Ipv6Address,
  Ipv6AvailableRanges,
  Ipv6Prefix,
  Ipv6PrefixAddressGridRead,
  Ipv6PrefixSplitEqualResponse,
  Ipv6PrefixSplitResponse,
} from "./types";

const P = "/api/v1/ipam";

export function listIpv4Prefixes(siteId?: number, tenantId?: number, vlanId?: number): Promise<Ipv4Prefix[]> {
  const params = new URLSearchParams();
  if (siteId != null) params.set("site_id", String(siteId));
  if (tenantId != null) params.set("tenant_id", String(tenantId));
  if (vlanId != null) params.set("vlan_id", String(vlanId));
  const s = params.toString();
  return apiGet(`${P}/ipv4-prefixes${s ? `?${s}` : ""}`);
}

export function getIpv4PrefixExplore(prefixId: number): Promise<Ipv4PrefixExplore> {
  return apiGet(`${P}/ipv4-prefixes/${prefixId}/explore`);
}

export function getPrefixAddressGrid(prefixId: number): Promise<PrefixAddressGridRead> {
  return apiGet(`${P}/ipv4-prefixes/${prefixId}/address-grid`);
}

export function listAvailableChildPrefixes(
  prefixId: number,
  prefixlen: number,
  limit = 64,
): Promise<Ipv4AvailablePrefixes> {
  const q = new URLSearchParams({ prefixlen: String(prefixlen), limit: String(limit) });
  return apiGet(`${P}/ipv4-prefixes/${prefixId}/available-prefixes?${q}`);
}

export function allocateChildPrefix(
  prefixId: number,
  body: {
    prefixlen: number;
    name: string;
    slug?: string | null;
    role?: string;
    status?: string;
    description?: string | null;
    vlan_id?: number | null;
    tenant_id?: number | null;
  },
): Promise<Ipv4Prefix> {
  return apiPost(`${P}/ipv4-prefixes/${prefixId}/allocate`, body);
}

export function getAvailableRanges(prefixId: number): Promise<Ipv4AvailableRanges> {
  return apiGet(`${P}/ipv4-prefixes/${prefixId}/available-ranges`);
}

export function ensureIpv4Address(body: {
  ipv4_prefix_id: number;
  address: string;
  mode?: "reserve" | "assign";
  status?: string;
  note?: string | null;
  device_id?: number | null;
  interface_id?: number | null;
}): Promise<Ipv4Address> {
  return apiPost(`${P}/ipv4-addresses/ensure`, body);
}

export function createIpv4Prefix(body: {
  site_id: number;
  name: string;
  cidr: string;
  slug?: string | null;
  description?: string | null;
  tenant_id?: number | null;
  vlan_id?: number | null;
  vrf_id?: number | null;
  role?: string;
  status?: string;
  overlap_policy?: string;
  dual_stack_group_id?: number | null;
}): Promise<Ipv4Prefix> {
  return apiPost(`${P}/ipv4-prefixes`, body);
}

export function updateIpv4Prefix(
  id: number,
  body: {
    name?: string;
    cidr?: string;
    description?: string | null;
    subnet_services?: Record<string, unknown> | null;
    tenant_id?: number | null;
    vlan_id?: number | null;
    vrf_id?: number | null;
    role?: string;
    status?: string;
    overlap_policy?: string;
  },
): Promise<Ipv4Prefix> {
  return apiPatch(`${P}/ipv4-prefixes/${id}`, body);
}

export function deleteIpv4Prefix(id: number, cascade = true): Promise<void> {
  const q = cascade ? "?cascade=true" : "";
  return apiDelete(`${P}/ipv4-prefixes/${id}${q}`);
}

export function ipv4PrefixSplit(
  prefixId: number,
  body: {
    first: { name: string; cidr: string };
    second: { name: string; cidr: string };
    migrate_inventory: boolean;
    acknowledge_network_broadcast: boolean;
    dry_run: boolean;
  },
): Promise<Ipv4PrefixSplitResponse> {
  return apiPost(`${P}/ipv4-prefixes/${prefixId}/split`, body);
}

export function ipv4PrefixSplitEqual(
  prefixId: number,
  body: {
    new_prefix_len: number;
    migrate_inventory: boolean;
    acknowledge_network_broadcast: boolean;
    dry_run: boolean;
    names_by_cidr?: Record<string, string> | null;
  },
): Promise<Ipv4PrefixSplitEqualResponse> {
  return apiPost(`${P}/ipv4-prefixes/${prefixId}/split-equal`, body);
}

export function listSubnetScans(params?: {
  site_id?: number;
  ipv4_prefix_id?: number;
  ipv6_prefix_id?: number;
  limit?: number;
}): Promise<SubnetScan[]> {
  const q = new URLSearchParams();
  if (params?.site_id != null) q.set("site_id", String(params.site_id));
  if (params?.ipv4_prefix_id != null) q.set("ipv4_prefix_id", String(params.ipv4_prefix_id));
  if (params?.ipv6_prefix_id != null) q.set("ipv6_prefix_id", String(params.ipv6_prefix_id));
  if (params?.limit != null) q.set("limit", String(params.limit));
  const s = q.toString();
  return apiGet(`${P}/subnet-scans${s ? `?${s}` : ""}`);
}

export function createSubnetScan(ipv4_prefix_id: number): Promise<SubnetScan> {
  return apiPost(`${P}/subnet-scans`, { ipv4_prefix_id });
}

export function createIpv6SubnetScan(ipv6_prefix_id: number): Promise<SubnetScan> {
  return apiPost(`${P}/subnet-scans`, { ipv6_prefix_id });
}

export function getSubnetScan(scanId: number): Promise<SubnetScanDetail> {
  return apiGet(`${P}/subnet-scans/${scanId}`);
}

export function listUsers(limit = 200): Promise<User[]> {
  return apiGet(`${P}/users?limit=${encodeURIComponent(String(limit))}`);
}

export function createUser(body: {
  username: string;
  display_name?: string | null;
  email?: string | null;
  phone?: string | null;
  kind?: string;
  notes?: string | null;
}): Promise<User> {
  return apiPost(`${P}/users`, body);
}

export function getIpv4Address(id: number): Promise<Ipv4Address> {
  return apiGet(`${P}/ipv4-addresses/${id}`);
}

export function listIpv4Addresses(params?: {
  site_id?: number;
  ipv4_prefix_id?: number;
  status?: string;
  limit?: number;
}): Promise<Ipv4Address[]> {
  const q = new URLSearchParams();
  if (params?.site_id != null) q.set("site_id", String(params.site_id));
  if (params?.ipv4_prefix_id != null) q.set("ipv4_prefix_id", String(params.ipv4_prefix_id));
  if (params?.status != null) q.set("status", params.status);
  if (params?.limit != null) q.set("limit", String(params.limit));
  const s = q.toString();
  return apiGet(`${P}/ipv4-addresses${s ? `?${s}` : ""}`);
}

export function patchIpv4Address(
  id: number,
  body: Partial<{
    status: string;
    owner_user_id: number | null;
    note: string | null;
    mac_address: string | null;
    device_type_id: number | null;
    device_model_id: number | null;
    device_id: number | null;
    interface_id: number | null;
  }>,
): Promise<Ipv4Address> {
  return apiPatch(`${P}/ipv4-addresses/${id}`, body);
}

export function bindIpv4Address(
  id: number,
  body: { device_id: number; interface_id?: number | null },
): Promise<Ipv4Address> {
  return apiPost(`${P}/ipv4-addresses/${id}/bind`, body);
}

export function releaseIpv4Address(id: number): Promise<Ipv4Address> {
  return apiPost(`${P}/ipv4-addresses/${id}/release`, {});
}

export function deleteIpv4Address(id: number): Promise<void> {
  return apiDelete(`${P}/ipv4-addresses/${id}`);
}

export function requestIpv4Address(body: {
  ipv4_prefix_id: number;
  mode: "reserve" | "assign";
  interface_id?: number | null;
  owner_user_id?: number | null;
  note?: string | null;
  device_type_id?: number | null;
  device_model_id?: number | null;
  device_id?: number | null;
}): Promise<Ipv4Address> {
  return apiPost(`${P}/ipv4-addresses/request`, body);
}

export function listIpamVrfs(siteId?: number): Promise<IpamVrf[]> {
  const q = siteId != null ? `?site_id=${encodeURIComponent(String(siteId))}` : "";
  return apiGet(`${P}/vrfs${q}`);
}

export function createIpamVrf(body: {
  site_id: number;
  name: string;
  slug?: string | null;
  route_distinguisher?: string | null;
  description?: string | null;
}): Promise<IpamVrf> {
  return apiPost(`${P}/vrfs`, body);
}

export function patchIpamVrf(
  id: number,
  body: Partial<{ name: string; slug: string; route_distinguisher: string | null; description: string | null }>,
): Promise<IpamVrf> {
  return apiPatch(`${P}/vrfs/${id}`, body);
}

export function deleteIpamVrf(id: number): Promise<void> {
  return apiDelete(`${P}/vrfs/${id}`);
}

export function listIpamVlans(siteId?: number): Promise<IpamVlan[]> {
  const q = siteId != null ? `?site_id=${encodeURIComponent(String(siteId))}` : "";
  return apiGet(`${P}/vlans${q}`);
}

export function createIpamVlan(body: {
  site_id: number;
  vid: number;
  name: string;
  slug?: string | null;
  vrf_id?: number | null;
  description?: string | null;
  tenant_id?: number | null;
}): Promise<IpamVlan> {
  return apiPost(`${P}/vlans`, body);
}

export function patchIpamVlan(
  id: number,
  body: Partial<{
    name: string;
    slug: string;
    vrf_id: number | null;
    description: string | null;
    tenant_id: number | null;
  }>,
): Promise<IpamVlan> {
  return apiPatch(`${P}/vlans/${id}`, body);
}

export function deleteIpamVlan(id: number): Promise<void> {
  return apiDelete(`${P}/vlans/${id}`);
}

export function listIpamCircuits(tenantId?: number): Promise<IpamCircuit[]> {
  const q = tenantId != null ? `?tenant_id=${encodeURIComponent(String(tenantId))}` : "";
  return apiGet(`${P}/circuits${q}`);
}

export function createIpamCircuit(body: {
  tenant_id?: number | null;
  circuit_number: string;
  name: string;
  circuit_type: string;
  description?: string | null;
  is_leased?: boolean;
  provider_name?: string | null;
  established_on?: string | null;
  contract_end_on?: string | null;
  a_site_id?: number | null;
  z_site_id?: number | null;
}): Promise<IpamCircuit> {
  return apiPost(`${P}/circuits`, body);
}

export function patchIpamCircuit(
  id: number,
  body: Partial<{
    name: string;
    description: string | null;
    circuit_type: string;
    is_leased: boolean;
    provider_name: string | null;
    established_on: string | null;
    contract_end_on: string | null;
  }>,
): Promise<IpamCircuit> {
  return apiPatch(`${P}/circuits/${id}`, body);
}

export function deleteIpamCircuit(id: number): Promise<void> {
  return apiDelete(`${P}/circuits/${id}`);
}

export function listCircuitTerminations(circuitId: number): Promise<IpamCircuitTermination[]> {
  return apiGet(`${P}/circuits/${circuitId}/terminations`);
}

export function upsertCircuitTermination(
  circuitId: number,
  body: { endpoint: "a" | "z"; interface_id?: number | null; site_id?: number | null; label?: string | null },
): Promise<IpamCircuitTermination> {
  return apiPost(`${P}/circuits/${circuitId}/terminations`, body);
}

export function requestIpv4AddressBatch(body: {
  ipv4_prefix_id: number;
  mode: "reserve" | "assign";
  count: number;
  preferred_addresses?: string[];
  interface_id?: number | null;
  owner_user_id?: number | null;
  note?: string | null;
  device_type_id?: number | null;
  device_model_id?: number | null;
  device_id?: number | null;
}): Promise<{ addresses: Ipv4Address[]; requested_count: number; allocated_count: number }> {
  return apiPost(`${P}/ipv4-addresses/request-batch`, body);
}

export function getIpv6PrefixAddressGrid(prefixId: number): Promise<Ipv6PrefixAddressGridRead> {
  return apiGet(`${P}/ipv6-prefixes/${prefixId}/address-grid`);
}

export function getIpv6AvailableRanges(prefixId: number): Promise<Ipv6AvailableRanges> {
  return apiGet(`${P}/ipv6-prefixes/${prefixId}/available-ranges`);
}

export function ipv6PrefixSplit(
  prefixId: number,
  body: {
    first: { name: string; cidr: string };
    second: { name: string; cidr: string };
    migrate_inventory?: boolean;
    dry_run?: boolean;
  },
): Promise<Ipv6PrefixSplitResponse> {
  return apiPost(`${P}/ipv6-prefixes/${prefixId}/split`, body);
}

export function ipv6PrefixSplitEqual(
  prefixId: number,
  body: {
    new_prefix_len: number;
    migrate_inventory?: boolean;
    dry_run?: boolean;
    names_by_cidr?: Record<string, string> | null;
  },
): Promise<Ipv6PrefixSplitEqualResponse> {
  return apiPost(`${P}/ipv6-prefixes/${prefixId}/split-equal`, body);
}

export function allocateIpv6ChildPrefix(
  prefixId: number,
  body: { prefixlen: number; name: string; slug?: string | null; role?: string; status?: string },
): Promise<Ipv6Prefix> {
  return apiPost(`${P}/ipv6-prefixes/${prefixId}/allocate`, body);
}

export function ensureIpv6Address(body: {
  ipv6_prefix_id: number;
  address: string;
  mode?: "reserve" | "assign";
  status?: string;
  role?: string;
  note?: string | null;
}): Promise<Ipv6Address> {
  return apiPost(`${P}/ipv6-addresses/ensure`, body);
}

export function listIpv6Prefixes(siteId?: number): Promise<Ipv6Prefix[]> {
  const params = new URLSearchParams();
  if (siteId != null) params.set("site_id", String(siteId));
  const s = params.toString();
  return apiGet(`${P}/ipv6-prefixes${s ? `?${s}` : ""}`);
}

export function createIpv6Prefix(body: {
  site_id: number;
  name: string;
  cidr: string;
  slug?: string | null;
  role?: string;
  status?: string;
  overlap_policy?: string;
  dual_stack_group_id?: number | null;
  tenant_id?: number | null;
  vlan_id?: number | null;
  vrf_id?: number | null;
}): Promise<Ipv6Prefix> {
  return apiPost(`${P}/ipv6-prefixes`, body);
}

export function deleteIpv6Prefix(id: number, cascade = true): Promise<void> {
  const q = cascade ? "?cascade=true" : "";
  return apiDelete(`${P}/ipv6-prefixes/${id}${q}`);
}

export function listIpv6Addresses(params?: {
  site_id?: number;
  ipv6_prefix_id?: number;
  limit?: number;
}): Promise<Ipv6Address[]> {
  const q = new URLSearchParams();
  if (params?.site_id != null) q.set("site_id", String(params.site_id));
  if (params?.ipv6_prefix_id != null) q.set("ipv6_prefix_id", String(params.ipv6_prefix_id));
  if (params?.limit != null) q.set("limit", String(params.limit));
  const s = q.toString();
  return apiGet(`${P}/ipv6-addresses${s ? `?${s}` : ""}`);
}

export function requestIpv6Address(body: {
  ipv6_prefix_id: number;
  mode?: "reserve" | "assign";
  preferred_address?: string | null;
  role?: string;
  note?: string | null;
}): Promise<Ipv6Address> {
  return apiPost(`${P}/ipv6-addresses/request`, body);
}

export function releaseIpv6Address(id: number): Promise<Ipv6Address> {
  return apiPost(`${P}/ipv6-addresses/${id}/release`, {});
}

export function listIpamAudit(params?: {
  site_id?: number;
  resource_type?: string;
  action?: string;
  limit?: number;
}): Promise<IpamAuditEvent[]> {
  const q = new URLSearchParams();
  if (params?.site_id != null) q.set("site_id", String(params.site_id));
  if (params?.resource_type) q.set("resource_type", params.resource_type);
  if (params?.action) q.set("action", params.action);
  if (params?.limit != null) q.set("limit", String(params.limit));
  const s = q.toString();
  return apiGet(`${P}/audit${s ? `?${s}` : ""}`);
}

export function getSiteDrift(siteId: number): Promise<SiteDrift> {
  return apiGet(`${P}/drift?site_id=${encodeURIComponent(String(siteId))}`);
}

export function getPrefixDrift(prefixId: number): Promise<PrefixDrift> {
  return apiGet(`${P}/ipv4-prefixes/${prefixId}/drift`);
}

export function exportSiteIpam(siteId: number, format: "json" | "yaml"): Promise<string> {
  return apiGetText(`${P}/export?site_id=${encodeURIComponent(String(siteId))}&format=${format}`);
}

export function listIpamWebhooks(): Promise<IpamWebhook[]> {
  return apiGet(`${P}/webhooks`);
}

export function createIpamWebhook(body: {
  url: string;
  secret?: string | null;
  events?: string[] | null;
  enabled?: boolean;
}): Promise<IpamWebhook> {
  return apiPost(`${P}/webhooks`, body);
}

export function deleteIpamWebhook(id: number): Promise<void> {
  return apiDelete(`${P}/webhooks/${id}`);
}

export function listIpamWebhookDeliveries(id: number): Promise<IpamWebhookDelivery[]> {
  return apiGet(`${P}/webhooks/${id}/deliveries`);
}
