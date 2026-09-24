export const IPV4_RANGE_KINDS = ["allocation", "reserved", "dhcp", "other"] as const;
export type Ipv4RangeKind = (typeof IPV4_RANGE_KINDS)[number];

export type Ipv4Range = {
  id: number;
  ipv4_prefix_id: number;
  name: string;
  slug: string;
  kind: Ipv4RangeKind | string;
  start_address: string;
  end_address: string;
  description: string | null;
  created_at: string;
  updated_at?: string | null;
};

export type Ipv4Prefix = {
  id: number;
  site_id: number;
  tenant_id?: number | null;
  vlan_id?: number | null;
  vrf_id?: number | null;
  name: string;
  slug: string;
  role?: string;
  status?: string;
  overlap_policy?: string;
  dual_stack_group_id?: number | null;
  etag?: string | null;
  cidr: string;
  description: string | null;
  created_at: string;
  updated_at?: string | null;
  parent_id?: number | null;
  used_count: number;
  address_total: number;
  usable_hosts?: number;
  utilization?: number;
  created?: boolean | null;
  subnet_services?: Record<string, unknown> | null;
};

export type Ipv4AssignmentInPrefix = {
  assignment_id: number;
  address: string;
  ipv4_prefix_id: number | null;
  interface_id: number;
  interface_name: string;
  device_id: number;
  device_name: string;
};

export type Ipv4PrefixExplore = {
  prefix: Ipv4Prefix;
  child_prefixes: Ipv4Prefix[];
  assignments: Ipv4AssignmentInPrefix[];
};

export type Ipv4PrefixSplitConflict = {
  address: string;
  role: "network" | "broadcast";
  message: string;
  subnet_cidr: string;
};

export type Ipv4PrefixSplitResponse = {
  dry_run: boolean;
  has_child_prefixes: boolean;
  partition_ok: boolean;
  detail: string | null;
  first_cidr: string | null;
  second_cidr: string | null;
  ipam_inventory_on_parent: number;
  ipam_migrate_left: number;
  ipam_migrate_right: number;
  dcim_iface_on_parent: number;
  dcim_device_on_parent: number;
  conflicts: Ipv4PrefixSplitConflict[];
  first_prefix: Ipv4Prefix | null;
  second_prefix: Ipv4Prefix | null;
};

export type Ipv4PrefixSplitEqualPlanned = {
  cidr: string;
  suggested_name: string;
};

export type Ipv4PrefixSplitEqualResponse = {
  dry_run: boolean;
  has_child_prefixes: boolean;
  parent_cidr: string;
  new_prefix_len: number;
  subnet_count: number;
  partition_ok: boolean;
  detail: string | null;
  planned: Ipv4PrefixSplitEqualPlanned[];
  ipam_inventory_on_parent: number;
  dcim_iface_on_parent: number;
  dcim_device_on_parent: number;
  conflicts: Ipv4PrefixSplitConflict[];
  created_prefixes: Ipv4Prefix[];
};

export type SubnetScanHost = {
  id: number;
  address: string;
  mac_address: string | null;
  ping_responded: boolean;
};

export type SubnetScan = {
  id: number;
  site_id: number;
  ipv4_prefix_id: number | null;
  ipv6_prefix_id?: number | null;
  cidr: string;
  method: string;
  status: string;
  hosts_scanned: number;
  hosts_responding: number;
  error_message: string | null;
  started_at: string;
  completed_at: string | null;
};

export type SubnetScanDetail = SubnetScan & {
  hosts: SubnetScanHost[];
};

export type User = {
  id: number;
  username: string;
  display_name: string | null;
  email?: string | null;
  phone?: string | null;
  kind?: string;
  notes?: string | null;
  external_subject_id?: string | null;
  identity_provider?: string | null;
  avatar_file?: string | null;
  created_at: string;
};

export type Ipv4Address = {
  id: number;
  site_id: number;
  ipv4_prefix_id: number | null;
  address: string;
  status: string;
  role?: string;
  hostname?: string | null;
  fqdn?: string | null;
  dns_name?: string | null;
  created?: boolean | null;
  owner_user_id: number | null;
  note: string | null;
  mac_address: string | null;
  last_seen_at: string | null;
  device_type_id: number | null;
  device_model_id: number | null;
  device_id: number | null;
  interface_id: number | null;
  interface_name: string | null;
  interface_ip_assignment_id: number | null;
  created_at: string;
  updated_at: string;
  etag?: string | null;
};

export type PrefixAddressGridRow = {
  address: string;
  address_role?: string | null;
  inventory: Ipv4Address | null;
  assignment: Ipv4AssignmentInPrefix | null;
  scan_ping_responded: boolean | null;
  scan_mac: string | null;
};

export type PrefixAddressGridRead = {
  prefix_id: number;
  cidr: string;
  active_scan: SubnetScan | null;
  rows: PrefixAddressGridRow[];
};

export type Ipv4AvailablePrefixes = {
  parent_id: number;
  cidr: string;
  prefixlen: number;
  available: string[];
  truncated: boolean;
};

export type IpRange = {
  start: string;
  end: string;
  count: number;
};

export type Ipv4AvailableRanges = {
  prefix_id: number;
  cidr: string;
  role: string;
  used_count: number;
  used_addresses: Ipv4Address[];
  used_ranges: IpRange[];
  free_ranges: IpRange[];
  free_cidrs: string[];
};

export type IpamVrf = {
  id: number;
  site_id: number;
  name: string;
  slug: string;
  route_distinguisher: string | null;
  created?: boolean | null;
  description: string | null;
  created_at: string;
};

export type IpamRouteTarget = {
  id: number;
  name: string;
  slug: string;
  value: string;
  description: string | null;
  created_at: string;
};

export type IpamVrfRouteTarget = {
  id: number;
  vrf_id: number;
  vrf_name: string;
  vrf_slug: string;
  route_target_id: number;
  route_target_slug: string;
  route_target_name: string;
  value: string;
  direction: "import" | "export" | string;
};

export type IpamVrfInstance = {
  id: number;
  vrf_id: number;
  vrf_name: string;
  vrf_slug: string;
  device_id: number;
  device_name: string;
  slug: string;
  intent: "recorded" | "intended" | string;
  route_distinguisher: string | null;
  effective_rd: string | null;
  description: string | null;
  created_at: string;
};

export type IpamAutonomousSystem = {
  id: number;
  asn: number;
  name: string;
  slug: string;
  is_private: boolean;
  tenant_id: number | null;
  description: string | null;
  created_at: string;
};

export type IpamAsAssignment = {
  id: number;
  autonomous_system_id: number;
  site_id: number;
  vrf_id: number | null;
  asn: number | null;
  as_name: string | null;
  site_name: string | null;
  vrf_name: string | null;
  created_at: string;
};

export type IpamBgpInstance = {
  id: number;
  site_id: number;
  device_id: number;
  device_name: string | null;
  local_as_id: number;
  local_asn: number | null;
  vrf_id: number | null;
  vrf_name: string | null;
  name: string;
  slug: string;
  intent: "recorded" | "intended" | string;
  router_id: string | null;
  description: string | null;
  created_at: string;
};

export type IpamBgpSession = {
  id: number;
  site_id: number;
  bgp_instance_id: number | null;
  local_as_id: number;
  remote_as_id: number | null;
  remote_asn: number;
  peer_ip: string;
  vrf_id: number | null;
  name: string;
  slug: string;
  address_families: string[];
  desired_status: string;
  observed_status: string | null;
  local_device_id: number | null;
  local_interface_id: number | null;
  description: string | null;
  created_at: string;
};

export type IpamVlanGroup = {
  id: number;
  site_id: number;
  name: string;
  slug: string;
  description: string | null;
  created_at: string;
};

export type IpamVlan = {
  id: number;
  site_id: number;
  vlan_group_id: number;
  tenant_id?: number | null;
  vid: number;
  name: string;
  slug: string;
  vrf_id: number | null;
  created?: boolean | null;
  description: string | null;
  created_at: string;
};

export type IpamCircuit = {
  id: number;
  tenant_id: number | null;
  a_site_id?: number | null;
  z_site_id?: number | null;
  circuit_number: string;
  name: string;
  description: string | null;
  circuit_type: string;
  layer: string | null;
  service_type: string | null;
  medium: string | null;
  operational_status: string | null;
  ownership: string | null;
  is_leased: boolean;
  provider_name: string | null;
  provider_id: number | null;
  provider_account_id: number | null;
  contract_id: number | null;
  group_id: number | null;
  provider_circuit_id: string | null;
  capacity_mbps: number | null;
  cir_mbps: number | null;
  needs_classification: boolean;
  established_on: string | null;
  contract_end_on: string | null;
  created_at: string;
};

export type IpamCircuitGroup = {
  id: number;
  tenant_id: number | null;
  name: string;
  slug: string;
  shared_risk: string | null;
  description: string | null;
  created_at: string;
};

export type IpamCircuitStrand = {
  id: number;
  circuit_id: number;
  strand_id: number;
  cable_id: number;
  cable_slug: string;
  position: number;
  label: string | null;
  status: string;
  created_at: string;
};

export type IpamCircuitTermination = {
  id: number;
  circuit_id: number;
  endpoint: string;
  kind: string | null;
  device_id: number | null;
  interface_id: number | null;
  site_id?: number | null;
  label: string | null;
  device_name: string | null;
  interface_name: string | null;
};

export type IpamProvider = {
  id: number;
  name: string;
  slug: string;
  asn: number | null;
  website: string | null;
  description: string | null;
  created_at: string;
};

export type IpamProviderAccount = {
  id: number;
  provider_id: number;
  tenant_id: number | null;
  name: string;
  slug: string;
  account_number: string | null;
  description: string | null;
  created_at: string;
};

export type IpamContract = {
  id: number;
  provider_id: number;
  provider_account_id: number | null;
  tenant_id: number | null;
  name: string;
  slug: string;
  reference: string | null;
  starts_on: string | null;
  ends_on: string | null;
  description: string | null;
  created_at: string;
};

export type IpamVpnService = {
  id: number;
  tenant_id: number | null;
  name: string;
  slug: string;
  vpn_type: string;
  source_circuit_id: number | null;
  description: string | null;
  created_at: string;
};

export type IpamVpnMember = {
  id: number;
  vpn_service_id: number;
  site_id: number | null;
  site_name: string | null;
  site_slug: string | null;
  name: string | null;
  slug: string | null;
  role: string | null;
  created_at: string;
};

export type IpamTunnel = {
  id: number;
  vpn_service_id: number;
  profile_id: number | null;
  name: string;
  slug: string;
  status: string;
  description: string | null;
  created_at: string;
};

export type IpamTunnelTransport = {
  id: number;
  tunnel_id: number;
  circuit_id: number;
  circuit_number: string;
  circuit_name: string;
  created_at: string;
};

export type IpamTunnelEndpoint = {
  id: number;
  tunnel_id: number;
  endpoint: string;
  device_id: number | null;
  interface_id: number | null;
  site_id: number | null;
  label: string | null;
  device_name: string | null;
  interface_name: string | null;
};

export type IpamTunnelPeer = {
  id: number;
  tunnel_id: number;
  name: string;
  public_key_ref: string | null;
  allowed_ips: string[] | null;
  endpoint_host: string | null;
  endpoint_port: number | null;
  persistent_keepalive: number | null;
  device_id: number | null;
  interface_id: number | null;
  notes: string | null;
  created_at: string;
};

export type IpamTunnelProfile = {
  id: number;
  name: string;
  slug: string;
  vpn_type: string;
  settings: Record<string, unknown> | null;
  description: string | null;
  created_at: string;
};

export type Ipv6Prefix = {
  id: number;
  site_id: number;
  tenant_id?: number | null;
  vlan_id?: number | null;
  vrf_id?: number | null;
  name: string;
  slug: string;
  role?: string;
  status?: string;
  overlap_policy?: string;
  dual_stack_group_id?: number | null;
  cidr: string;
  description?: string | null;
  parent_id?: number | null;
  used_count?: number;
  created?: boolean | null;
  created_at: string;
  updated_at?: string | null;
  etag?: string | null;
};

export type Ipv6Address = {
  id: number;
  site_id: number;
  ipv6_prefix_id: number | null;
  address: string;
  status: string;
  role?: string;
  created?: boolean | null;
  note?: string | null;
  device_id?: number | null;
  interface_id?: number | null;
  created_at: string;
  updated_at: string;
  etag?: string | null;
};

export type Ipv6PrefixAddressGridRead = {
  prefix_id: number;
  cidr: string;
  active_scan: SubnetScan | null;
  rows: {
    address: string;
    address_role?: string | null;
    inventory: Ipv6Address | null;
    scan_ping_responded: boolean | null;
    scan_mac: string | null;
  }[];
};

export type Ipv6AvailableRanges = {
  prefix_id: number;
  cidr: string;
  role: string;
  used_count: number;
  used_addresses: Ipv6Address[];
  used_ranges: { start: string; end: string; count: number }[];
  free_ranges: { start: string; end: string; count: number }[];
  free_cidrs: string[];
};

export type Ipv6PrefixSplitResponse = {
  dry_run: boolean;
  has_child_prefixes: boolean;
  partition_ok: boolean;
  detail: string | null;
  first_cidr: string | null;
  second_cidr: string | null;
  ipam_inventory_on_parent: number;
  ipam_migrate_left: number;
  ipam_migrate_right: number;
  first_prefix: Ipv6Prefix | null;
  second_prefix: Ipv6Prefix | null;
};

export const PREFIX_ROLES = [
  "container",
  "access",
  "overlay-pod",
  "overlay-service",
  "lb-pool",
  "p2p",
] as const;

export const PREFIX_STATUSES = ["planned", "active", "reserved", "deprecated"] as const;
export const OVERLAP_POLICIES = ["site-local", "global-unique"] as const;
export const ADDRESS_ROLES = ["gateway", "vip", "anycast", "lb", "host", "dhcp", "reserved"] as const;
export const ADDRESS_STATUSES = ["discovered", "reserved", "assigned"] as const;

export type IpamAuditEvent = {
  id: number;
  created_at: string;
  actor_type: string;
  actor_id: number | null;
  actor_name: string | null;
  action: string;
  resource_type: string;
  resource_id: number | null;
  site_id: number | null;
  detail?: Record<string, unknown> | null;
};

export type IpamDriftAddress = {
  address: string;
  status?: string | null;
  role?: string | null;
  mac_address?: string | null;
};

export type PrefixDrift = {
  prefix_id: number;
  cidr: string;
  scan_id?: number | null;
  scanned_at?: string | null;
  aligned: string[];
  seen_unmanaged: IpamDriftAddress[];
  reserved_missing: IpamDriftAddress[];
};

export type SiteDrift = {
  site_id: number;
  prefixes: PrefixDrift[];
};

export type IpamWebhook = {
  id: number;
  url: string;
  events?: string[] | null;
  enabled: boolean;
  created_at: string;
};

export type IpamWebhookDelivery = {
  id: number;
  webhook_id: number;
  event: string;
  status: string;
  status_code?: number | null;
  error?: string | null;
  created_at: string;
};

export type Ipv6PrefixSplitEqualResponse = {
  dry_run: boolean;
  has_child_prefixes: boolean;
  parent_cidr: string;
  new_prefix_len: number;
  subnet_count: number;
  partition_ok: boolean;
  detail: string | null;
  planned: { cidr: string; suggested_name: string }[];
  ipam_inventory_on_parent: number;
  created_prefixes: Ipv6Prefix[];
};
