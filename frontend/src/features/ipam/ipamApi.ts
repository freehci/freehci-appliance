import { apiDelete, apiGet, apiPatch, apiPost } from "@/lib/api";
import type {
  Ipv4Address,
  Ipv4Prefix,
  Ipv4PrefixExplore,
  IpamCircuit,
  IpamCircuitTermination,
  IpamVlan,
  IpamVrf,
  PrefixAddressGridRead,
  SubnetScan,
  SubnetScanDetail,
  User,
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

export function ensureIpv4Address(body: { ipv4_prefix_id: number; address: string }): Promise<Ipv4Address> {
  return apiPost(`${P}/ipv4-addresses/ensure`, body);
}

export function createIpv4Prefix(body: {
  site_id: number;
  name: string;
  cidr: string;
  description?: string | null;
  tenant_id?: number | null;
  vlan_id?: number | null;
  vrf_id?: number | null;
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
  },
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

export function releaseIpv4Address(id: number): Promise<Ipv4Address> {
  return apiPost(`${P}/ipv4-addresses/${id}/release`, {});
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
  route_distinguisher?: string | null;
  description?: string | null;
}): Promise<IpamVrf> {
  return apiPost(`${P}/vrfs`, body);
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
  vrf_id?: number | null;
  description?: string | null;
  tenant_id?: number | null;
}): Promise<IpamVlan> {
  return apiPost(`${P}/vlans`, body);
}

export function deleteIpamVlan(id: number): Promise<void> {
  return apiDelete(`${P}/vlans/${id}`);
}

export function listIpamCircuits(tenantId?: number): Promise<IpamCircuit[]> {
  const q = tenantId != null ? `?tenant_id=${encodeURIComponent(String(tenantId))}` : "";
  return apiGet(`${P}/circuits${q}`);
}

export function createIpamCircuit(body: {
  tenant_id: number;
  circuit_number: string;
  name: string;
  circuit_type: string;
  description?: string | null;
  is_leased?: boolean;
  provider_name?: string | null;
  established_on?: string | null;
  contract_end_on?: string | null;
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
  body: { endpoint: "a" | "z"; interface_id?: number | null; label?: string | null },
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
