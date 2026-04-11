import { apiDelete, apiGet, apiGetText, apiPost, apiPostMultipart } from "@/lib/api";

const P = "/api/v1/snmp";

export type SnmpMibFile = {
  name: string;
  size_bytes: number;
  modified_at: string;
};

export type SnmpMibManufacturerBrief = { id: number; name: string };

export type SnmpMibDetail = SnmpMibFile & {
  module_name: string | null;
  enterprise_number: number | null;
  iana_organization: string | null;
  compile_status: string;
  compile_message: string | null;
  compiled_module_name: string | null;
  compiled_at: string | null;
  linked_manufacturer: SnmpMibManufacturerBrief | null;
  effective_enterprise_number?: number | null;
  extends_mib_module?: string | null;
  parent_mib_missing?: boolean;
};

export type SnmpMibTreeNode = {
  filename: string;
  module_name: string | null;
  compile_status: string | null;
  extension_parent_module: string | null;
  parent_mib_missing: boolean;
  children: SnmpMibTreeNode[];
};

export type SnmpEnterpriseGroup = {
  enterprise_number: number | null;
  iana_organization: string | null;
  mib_files: string[];
  mib_tree: SnmpMibTreeNode[];
  linked_manufacturer: SnmpMibManufacturerBrief | null;
};

export type SnmpVarBind = { oid: string; value: string };

export type SnmpProbeResult = {
  ok: boolean;
  error: string | null;
  varbinds: SnmpVarBind[];
};

export function listSnmpMibs(): Promise<SnmpMibFile[]> {
  return apiGet(`${P}/mibs`);
}

export function uploadSnmpMib(file: File): Promise<SnmpMibFile> {
  const fd = new FormData();
  fd.set("file", file);
  return apiPostMultipart(`${P}/mibs`, fd);
}

export function deleteSnmpMib(name: string): Promise<void> {
  return apiDelete(`${P}/mibs/${encodeURIComponent(name)}`);
}

export function listSnmpMibsDetailed(): Promise<SnmpMibDetail[]> {
  return apiGet(`${P}/mibs/detailed`);
}

export function getSnmpMibSource(name: string): Promise<string> {
  return apiGetText(`${P}/mibs/${encodeURIComponent(name)}/source`);
}

export function listSnmpEnterprises(): Promise<SnmpEnterpriseGroup[]> {
  return apiGet(`${P}/enterprises`);
}

export type SnmpAutocreateDcimResult = {
  created: Array<{ enterprise_number: number; manufacturer_id: number; name: string }>;
  skipped: string[];
};

export function autocreateSnmpDcimManufacturers(body: {
  enterprise_number?: number | null;
}): Promise<SnmpAutocreateDcimResult> {
  return apiPost(`${P}/enterprises/autocreate-dcim`, body);
}

export function syncSnmpIana(): Promise<{ rows_imported: number }> {
  return apiPost(`${P}/iana/sync`, {});
}

export function uploadSnmpMibsBatch(files: File[]): Promise<SnmpMibDetail[]> {
  const fd = new FormData();
  for (const f of files) {
    fd.append("files", f);
  }
  return apiPostMultipart(`${P}/mibs/batch`, fd);
}

export function compileSnmpMib(name: string): Promise<SnmpMibDetail> {
  return apiPost(`${P}/mibs/${encodeURIComponent(name)}/compile`, {});
}

export function compileAllSnmpMibs(): Promise<SnmpMibDetail[]> {
  return apiPost(`${P}/mibs/compile-all`, {});
}

export function snmpProbe(body: {
  host: string;
  port?: number;
  community?: string;
  oid: string;
  operation?: "get" | "walk";
  max_oids?: number;
  timeout_sec?: number;
  retries?: number;
}): Promise<SnmpProbeResult> {
  return apiPost(`${P}/probe`, body);
}

export type SnmpInterfaceRow = {
  if_index: number;
  name: string;
  description: string | null;
  if_descr: string | null;
  if_alias: string | null;
  if_type: number | null;
  if_type_label: string | null;
  mtu: number | null;
  speed_mbps: number | null;
  mac_address: string | null;
  admin_status: string;
  oper_status: string;
  enabled: boolean;
};

export type SnmpInventoryResult = {
  ok: boolean;
  error: string | null;
  host: string;
  sys_name: string | null;
  sys_descr: string | null;
  interfaces: SnmpInterfaceRow[];
  truncated: boolean;
  varbinds_collected: number | null;
};

export function snmpInventory(body: {
  host: string;
  port?: number;
  community?: string;
  max_varbinds?: number;
  timeout_sec?: number;
  retries?: number;
}): Promise<SnmpInventoryResult> {
  return apiPost(`${P}/inventory`, body);
}

export type SnmpIpAddressRow = {
  address: string;
  if_index: number;
  netmask: string | null;
  interface_name: string | null;
};

export type SnmpVlanRow = { vlan_id: number; name: string | null };

export type SnmpInterfaceVlanRow = {
  if_index: number;
  native_vlan_id: number;
  bridge_port: number | null;
  interface_name: string | null;
};

export type SnmpScanResult = {
  ok: boolean;
  error: string | null;
  host: string;
  sys_name: string | null;
  sys_descr: string | null;
  interfaces: SnmpInterfaceRow[];
  ip_addresses: SnmpIpAddressRow[];
  vlans: SnmpVlanRow[];
  interface_vlans: SnmpInterfaceVlanRow[];
  warnings: string[];
  truncated: boolean;
  varbinds_collected: number | null;
};

export function snmpScan(body: {
  host: string;
  port?: number;
  community?: string;
  max_varbinds?: number;
  timeout_sec?: number;
  retries?: number;
}): Promise<SnmpScanResult> {
  return apiPost(`${P}/scan`, body);
}

export type SnmpInventoryApplyResult = {
  ok: boolean;
  error: string | null;
  device_id: number;
  host: string | null;
  created: number;
  updated: number;
  skipped: number;
  poll: SnmpInventoryResult | null;
};

export function snmpInventoryApply(body: {
  device_id: number;
  host: string;
  port?: number;
  community?: string;
  max_varbinds?: number;
  timeout_sec?: number;
  retries?: number;
}): Promise<SnmpInventoryApplyResult> {
  return apiPost(`${P}/inventory/apply`, body);
}
