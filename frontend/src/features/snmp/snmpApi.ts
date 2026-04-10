import { apiDelete, apiGet, apiPost, apiPostMultipart } from "@/lib/api";

const P = "/api/v1/snmp";

export type SnmpMibFile = {
  name: string;
  size_bytes: number;
  modified_at: string;
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
