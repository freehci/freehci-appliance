export type Ipv4Prefix = {
  id: number;
  site_id: number;
  tenant_id?: number | null;
  vlan_id?: number | null;
  vrf_id?: number | null;
  name: string;
  cidr: string;
  description: string | null;
  created_at: string;
  used_count: number;
  address_total: number;
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

export type IpamVrf = {
  id: number;
  site_id: number;
  name: string;
  route_distinguisher: string | null;
  description: string | null;
  created_at: string;
};

export type IpamVlan = {
  id: number;
  site_id: number;
  tenant_id?: number | null;
  vid: number;
  name: string;
  vrf_id: number | null;
  description: string | null;
  created_at: string;
};

export type IpamCircuit = {
  id: number;
  tenant_id: number;
  circuit_number: string;
  name: string;
  description: string | null;
  circuit_type: string;
  is_leased: boolean;
  provider_name: string | null;
  established_on: string | null;
  contract_end_on: string | null;
  created_at: string;
};

export type IpamCircuitTermination = {
  id: number;
  circuit_id: number;
  endpoint: string;
  interface_id: number | null;
  label: string | null;
};
