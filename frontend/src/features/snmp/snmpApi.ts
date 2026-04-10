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
