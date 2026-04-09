export type Ipv4Prefix = {
  id: number;
  site_id: number;
  name: string;
  cidr: string;
  description: string | null;
  created_at: string;
  used_count: number;
  address_total: number;
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
