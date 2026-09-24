import { apiDelete, apiGet, apiGetText, apiPatch, apiPost } from "@/lib/api";
import type {
  Ipv4Address,
  Ipv4AvailablePrefixes,
  Ipv4AvailableRanges,
  Ipv4Prefix,
  Ipv4PrefixExplore,
  Ipv4Range,
  Ipv4PrefixSplitEqualResponse,
  Ipv4PrefixSplitResponse,
  IpamAuditEvent,
  IpamCircuit,
  IpamCircuitGroup,
  IpamCircuitStrand,
  IpamCircuitTermination,
  IpamContract,
  IpamProvider,
  IpamProviderAccount,
  IpamTunnel,
  IpamTunnelEndpoint,
  IpamTunnelPeer,
  IpamTunnelTransport,
  IpamTunnelProfile,
  IpamVpnMember,
  IpamVpnService,
  IpamOverlaySegment,
  IpamVlan,
  IpamVlanStretch,
  IpamVlanGroup,
  IpamAsAssignment,
  IpamAutonomousSystem,
  IpamBgpInstance,
  IpamBgpSession,
  IpamRouteTarget,
  IpamVrf,
  IpamVrfInstance,
  IpamVrfRouteTarget,
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

export function listIpv4Ranges(prefixId: number): Promise<Ipv4Range[]> {
  return apiGet(`${P}/ipv4-prefixes/${prefixId}/ranges`);
}

export function createIpv4Range(
  prefixId: number,
  body: {
    name: string;
    slug?: string | null;
    kind?: string;
    start_address: string;
    end_address: string;
    description?: string | null;
  },
): Promise<Ipv4Range> {
  return apiPost(`${P}/ipv4-prefixes/${prefixId}/ranges`, body);
}

export function deleteIpv4Range(rangeId: number): Promise<void> {
  return apiDelete(`${P}/ipv4-ranges/${rangeId}`);
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
    role: string;
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

export function listVrfInstances(opts?: { vrfId?: number; deviceId?: number; siteId?: number }): Promise<IpamVrfInstance[]> {
  const params = new URLSearchParams();
  if (opts?.vrfId != null) params.set("vrf_id", String(opts.vrfId));
  if (opts?.deviceId != null) params.set("device_id", String(opts.deviceId));
  if (opts?.siteId != null) params.set("site_id", String(opts.siteId));
  const s = params.toString();
  return apiGet(`${P}/vrf-instances${s ? `?${s}` : ""}`);
}

export function createVrfInstance(
  vrfId: number,
  body: {
    device_id: number;
    slug?: string | null;
    intent?: string;
    route_distinguisher?: string | null;
    description?: string | null;
  },
): Promise<IpamVrfInstance> {
  return apiPost(`${P}/vrfs/${vrfId}/instances`, body);
}

export function deleteVrfInstance(id: number): Promise<void> {
  return apiDelete(`${P}/vrf-instances/${id}`);
}

export function listRouteTargets(): Promise<IpamRouteTarget[]> {
  return apiGet(`${P}/route-targets`);
}

export function createRouteTarget(body: {
  name: string;
  slug?: string | null;
  value: string;
  description?: string | null;
}): Promise<IpamRouteTarget> {
  return apiPost(`${P}/route-targets`, body);
}

export function deleteRouteTarget(id: number): Promise<void> {
  return apiDelete(`${P}/route-targets/${id}`);
}

export function listVrfRouteTargets(opts?: { siteId?: number; vrfId?: number }): Promise<IpamVrfRouteTarget[]> {
  if (opts?.vrfId != null) return apiGet(`${P}/vrfs/${opts.vrfId}/route-targets`);
  const q = opts?.siteId != null ? `?site_id=${encodeURIComponent(String(opts.siteId))}` : "";
  return apiGet(`${P}/vrf-route-targets${q}`);
}

export function bindVrfRouteTarget(
  vrfId: number,
  body: { route_target_id: number; direction: string },
): Promise<IpamVrfRouteTarget> {
  return apiPost(`${P}/vrfs/${vrfId}/route-targets`, body);
}

export function unbindVrfRouteTarget(bindingId: number): Promise<void> {
  return apiDelete(`${P}/vrf-route-targets/${bindingId}`);
}

export function listAutonomousSystems(tenantId?: number): Promise<IpamAutonomousSystem[]> {
  const q = tenantId != null ? `?tenant_id=${encodeURIComponent(String(tenantId))}` : "";
  return apiGet(`${P}/autonomous-systems${q}`);
}

export function createAutonomousSystem(body: {
  asn: number;
  name: string;
  slug?: string | null;
  tenant_id?: number | null;
  description?: string | null;
}): Promise<IpamAutonomousSystem> {
  return apiPost(`${P}/autonomous-systems`, body);
}

export function deleteAutonomousSystem(id: number): Promise<void> {
  return apiDelete(`${P}/autonomous-systems/${id}`);
}

export function listAsAssignments(siteId?: number, asId?: number): Promise<IpamAsAssignment[]> {
  const params = new URLSearchParams();
  if (siteId != null) params.set("site_id", String(siteId));
  if (asId != null) params.set("as_id", String(asId));
  const s = params.toString();
  return apiGet(`${P}/as-assignments${s ? `?${s}` : ""}`);
}

export function createAsAssignment(body: {
  autonomous_system_id: number;
  site_id: number;
  vrf_id?: number | null;
}): Promise<IpamAsAssignment> {
  return apiPost(`${P}/as-assignments`, body);
}

export function deleteAsAssignment(id: number): Promise<void> {
  return apiDelete(`${P}/as-assignments/${id}`);
}

export function listBgpInstances(siteId?: number): Promise<IpamBgpInstance[]> {
  const q = siteId != null ? `?site_id=${encodeURIComponent(String(siteId))}` : "";
  return apiGet(`${P}/bgp-instances${q}`);
}

export function createBgpInstance(body: {
  device_id: number;
  local_as_id: number;
  vrf_id?: number | null;
  name?: string | null;
  slug?: string | null;
  intent?: string;
  router_id?: string | null;
  description?: string | null;
}): Promise<IpamBgpInstance> {
  return apiPost(`${P}/bgp-instances`, body);
}

export function deleteBgpInstance(id: number): Promise<void> {
  return apiDelete(`${P}/bgp-instances/${id}`);
}

export function listBgpSessions(siteId?: number): Promise<IpamBgpSession[]> {
  const q = siteId != null ? `?site_id=${encodeURIComponent(String(siteId))}` : "";
  return apiGet(`${P}/bgp-sessions${q}`);
}

export function createBgpSession(body: {
  site_id?: number | null;
  bgp_instance_id?: number | null;
  local_as_id?: number | null;
  remote_as_id?: number | null;
  remote_asn?: number | null;
  peer_ip: string;
  vrf_id?: number | null;
  name?: string | null;
  address_families?: string[];
  desired_status?: string;
}): Promise<IpamBgpSession> {
  return apiPost(`${P}/bgp-sessions`, body);
}

export function deleteBgpSession(id: number): Promise<void> {
  return apiDelete(`${P}/bgp-sessions/${id}`);
}

export function listIpamVlanGroups(siteId?: number): Promise<IpamVlanGroup[]> {
  const q = siteId != null ? `?site_id=${encodeURIComponent(String(siteId))}` : "";
  return apiGet(`${P}/vlan-groups${q}`);
}

export function createIpamVlanGroup(body: {
  site_id: number;
  name: string;
  slug?: string | null;
  description?: string | null;
}): Promise<IpamVlanGroup> {
  return apiPost(`${P}/vlan-groups`, body);
}

export function listIpamVlans(siteId?: number, vlanGroupId?: number): Promise<IpamVlan[]> {
  const params = new URLSearchParams();
  if (siteId != null) params.set("site_id", String(siteId));
  if (vlanGroupId != null) params.set("vlan_group_id", String(vlanGroupId));
  const s = params.toString();
  return apiGet(`${P}/vlans${s ? `?${s}` : ""}`);
}

export function createIpamVlan(body: {
  site_id: number;
  vlan_group_id?: number | null;
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
    vlan_group_id: number | null;
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

export function listOverlaySegments(siteId?: number): Promise<IpamOverlaySegment[]> {
  const q = siteId != null ? `?site_id=${encodeURIComponent(String(siteId))}` : "";
  return apiGet(`${P}/overlay-segments${q}`);
}

export function createOverlaySegment(body: {
  site_id: number;
  vni: number;
  name: string;
  slug?: string | null;
  kind?: string;
  vlan_id?: number | null;
  vrf_id?: number | null;
  description?: string | null;
}): Promise<IpamOverlaySegment> {
  return apiPost(`${P}/overlay-segments`, body);
}

export function deleteOverlaySegment(id: number): Promise<void> {
  return apiDelete(`${P}/overlay-segments/${id}`);
}

export function listVlanStretches(siteId?: number): Promise<IpamVlanStretch[]> {
  const q = siteId != null ? `?site_id=${encodeURIComponent(String(siteId))}` : "";
  return apiGet(`${P}/vlan-stretches${q}`);
}

export function createVlanStretch(body: {
  vlan_a_id: number;
  vlan_b_id: number;
  name: string;
  slug?: string | null;
  description?: string | null;
}): Promise<IpamVlanStretch> {
  return apiPost(`${P}/vlan-stretches`, body);
}

export function deleteVlanStretch(id: number): Promise<void> {
  return apiDelete(`${P}/vlan-stretches/${id}`);
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
  layer?: string | null;
  description?: string | null;
  ownership?: string | null;
  is_leased?: boolean;
  provider_name?: string | null;
  provider_id?: number | null;
  provider_account_id?: number | null;
  contract_id?: number | null;
  group_id?: number | null;
  provider_circuit_id?: string | null;
  capacity_mbps?: number | null;
  cir_mbps?: number | null;
  established_on?: string | null;
  contract_end_on?: string | null;
  a_site_id?: number | null;
  z_site_id?: number | null;
  service_type?: string | null;
  medium?: string | null;
  operational_status?: string | null;
}): Promise<IpamCircuit> {
  return apiPost(`${P}/circuits`, body);
}

export function patchIpamCircuit(
  id: number,
  body: Partial<{
    name: string;
    description: string | null;
    circuit_type: string;
    layer: string | null;
    ownership?: string | null;
    is_leased: boolean;
    provider_name: string | null;
    provider_id: number | null;
    provider_account_id: number | null;
    contract_id: number | null;
    group_id: number | null;
    provider_circuit_id: string | null;
    capacity_mbps: number | null;
    cir_mbps: number | null;
    established_on: string | null;
    contract_end_on: string | null;
    service_type: string | null;
    medium: string | null;
    operational_status: string | null;
  }>,
): Promise<IpamCircuit> {
  return apiPatch(`${P}/circuits/${id}`, body);
}

export function deleteIpamCircuit(id: number): Promise<void> {
  return apiDelete(`${P}/circuits/${id}`);
}

export function listIpamCircuitGroups(tenantId?: number): Promise<IpamCircuitGroup[]> {
  const q = tenantId != null ? `?tenant_id=${encodeURIComponent(String(tenantId))}` : "";
  return apiGet(`${P}/circuit-groups${q}`);
}

export function createIpamCircuitGroup(body: {
  name: string;
  slug?: string | null;
  shared_risk?: string | null;
  description?: string | null;
  tenant_id?: number | null;
}): Promise<IpamCircuitGroup> {
  return apiPost(`${P}/circuit-groups`, body);
}

export function deleteIpamCircuitGroup(id: number): Promise<void> {
  return apiDelete(`${P}/circuit-groups/${id}`);
}

export function classifyIpamCircuit(
  id: number,
  body: { layer: "transport" | "overlay"; create_vpn?: boolean },
): Promise<{ circuit: IpamCircuit; vpn_service_id: number | null }> {
  return apiPost(`${P}/circuits/${id}/classify`, body);
}

export function listCircuitTerminations(circuitId: number): Promise<IpamCircuitTermination[]> {
  return apiGet(`${P}/circuits/${circuitId}/terminations`);
}

export function listCircuitStrands(circuitId: number): Promise<IpamCircuitStrand[]> {
  return apiGet(`${P}/circuits/${circuitId}/strands`);
}

export function bindCircuitStrand(circuitId: number, strandId: number): Promise<IpamCircuitStrand> {
  return apiPost(`${P}/circuits/${circuitId}/strands`, { strand_id: strandId });
}

export function unbindCircuitStrand(bindId: number): Promise<void> {
  return apiDelete(`${P}/circuit-strands/${bindId}`);
}

export function upsertCircuitTermination(
  circuitId: number,
  body: {
    endpoint: "a" | "z";
    kind?: string | null;
    device_id?: number | null;
    interface_id?: number | null;
    site_id?: number | null;
    label?: string | null;
  },
): Promise<IpamCircuitTermination> {
  return apiPost(`${P}/circuits/${circuitId}/terminations`, body);
}

export function listIpamProviders(): Promise<IpamProvider[]> {
  return apiGet(`${P}/providers`);
}

export function createIpamProvider(body: {
  name: string;
  slug?: string | null;
  asn?: number | null;
  website?: string | null;
  description?: string | null;
}): Promise<IpamProvider> {
  return apiPost(`${P}/providers`, body);
}

export function deleteIpamProvider(id: number): Promise<void> {
  return apiDelete(`${P}/providers/${id}`);
}

export function listProviderAccounts(providerId: number): Promise<IpamProviderAccount[]> {
  return apiGet(`${P}/providers/${providerId}/accounts`);
}

export function createProviderAccount(
  providerId: number,
  body: {
    name: string;
    slug?: string | null;
    tenant_id?: number | null;
    account_number?: string | null;
    description?: string | null;
  },
): Promise<IpamProviderAccount> {
  return apiPost(`${P}/providers/${providerId}/accounts`, body);
}

export function deleteProviderAccount(id: number): Promise<void> {
  return apiDelete(`${P}/provider-accounts/${id}`);
}

export function listIpamContracts(providerId?: number): Promise<IpamContract[]> {
  const q = providerId != null ? `?provider_id=${encodeURIComponent(String(providerId))}` : "";
  return apiGet(`${P}/contracts${q}`);
}

export function createIpamContract(body: {
  provider_id: number;
  provider_account_id?: number | null;
  tenant_id?: number | null;
  name: string;
  slug?: string | null;
  reference?: string | null;
  starts_on?: string | null;
  ends_on?: string | null;
  description?: string | null;
}): Promise<IpamContract> {
  return apiPost(`${P}/contracts`, body);
}

export function deleteIpamContract(id: number): Promise<void> {
  return apiDelete(`${P}/contracts/${id}`);
}

export function listVpnServices(tenantId?: number): Promise<IpamVpnService[]> {
  const q = tenantId != null ? `?tenant_id=${encodeURIComponent(String(tenantId))}` : "";
  return apiGet(`${P}/vpn-services${q}`);
}

export function createVpnService(body: {
  name: string;
  slug?: string | null;
  vpn_type: string;
  tenant_id?: number | null;
  source_circuit_id?: number | null;
  description?: string | null;
}): Promise<IpamVpnService> {
  return apiPost(`${P}/vpn-services`, body);
}

export function deleteVpnService(id: number): Promise<void> {
  return apiDelete(`${P}/vpn-services/${id}`);
}

export function listVpnMembers(vpnId: number): Promise<IpamVpnMember[]> {
  return apiGet(`${P}/vpn-services/${vpnId}/members`);
}

export function createVpnMember(
  vpnId: number,
  body: { site_id?: number | null; name?: string | null; slug?: string | null; role?: string | null },
): Promise<IpamVpnMember> {
  return apiPost(`${P}/vpn-services/${vpnId}/members`, body);
}

export function deleteVpnMember(id: number): Promise<void> {
  return apiDelete(`${P}/vpn-members/${id}`);
}

export function listVpnTunnels(vpnId: number): Promise<IpamTunnel[]> {
  return apiGet(`${P}/vpn-services/${vpnId}/tunnels`);
}

export function createVpnTunnel(
  vpnId: number,
  body: { name: string; slug?: string | null; status?: string; profile_id?: number | null; description?: string | null },
): Promise<IpamTunnel> {
  return apiPost(`${P}/vpn-services/${vpnId}/tunnels`, body);
}

export function deleteVpnTunnel(id: number): Promise<void> {
  return apiDelete(`${P}/tunnels/${id}`);
}

export function listTunnelTransports(tunnelId: number): Promise<IpamTunnelTransport[]> {
  return apiGet(`${P}/tunnels/${tunnelId}/transports`);
}

export function bindTunnelTransport(tunnelId: number, circuitId: number): Promise<IpamTunnelTransport> {
  return apiPost(`${P}/tunnels/${tunnelId}/transports`, { circuit_id: circuitId });
}

export function unbindTunnelTransport(bindId: number): Promise<void> {
  return apiDelete(`${P}/tunnel-transports/${bindId}`);
}

export function listTunnelEndpoints(tunnelId: number): Promise<IpamTunnelEndpoint[]> {
  return apiGet(`${P}/tunnels/${tunnelId}/endpoints`);
}

export function upsertTunnelEndpoint(
  tunnelId: number,
  body: {
    endpoint: "a" | "z";
    device_id?: number | null;
    interface_id?: number | null;
    site_id?: number | null;
    label?: string | null;
  },
): Promise<IpamTunnelEndpoint> {
  return apiPost(`${P}/tunnels/${tunnelId}/endpoints`, body);
}

export function listTunnelPeers(tunnelId: number): Promise<IpamTunnelPeer[]> {
  return apiGet(`${P}/tunnels/${tunnelId}/peers`);
}

export function createTunnelPeer(
  tunnelId: number,
  body: {
    name: string;
    public_key_ref?: string | null;
    allowed_ips?: string[] | null;
    endpoint_host?: string | null;
    endpoint_port?: number | null;
  },
): Promise<IpamTunnelPeer> {
  return apiPost(`${P}/tunnels/${tunnelId}/peers`, body);
}

export function deleteTunnelPeer(id: number): Promise<void> {
  return apiDelete(`${P}/tunnel-peers/${id}`);
}

export function listTunnelProfiles(): Promise<IpamTunnelProfile[]> {
  return apiGet(`${P}/tunnel-profiles`);
}

export function createTunnelProfile(body: {
  name: string;
  slug?: string | null;
  vpn_type: string;
  description?: string | null;
}): Promise<IpamTunnelProfile> {
  return apiPost(`${P}/tunnel-profiles`, body);
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
