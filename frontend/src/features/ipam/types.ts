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
