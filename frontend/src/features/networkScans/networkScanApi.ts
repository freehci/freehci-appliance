import { apiDelete, apiGet, apiPatch, apiPost, apiPostNoContent } from "@/lib/api";

const P = "/api/v1/network-scans";

export type NetworkScanTemplate = {
  id: number;
  slug: string;
  name: string;
  kind: string;
  is_builtin: boolean;
  default_config: Record<string, unknown> | null;
};

export type NetworkScanPrefixBinding = {
  id: number;
  template_id: number;
  ipv4_prefix_id: number;
  enabled: boolean;
};

export type NetworkScanJob = {
  id: number;
  template_id: number;
  ipv4_prefix_id: number;
  site_id: number;
  cidr: string;
  parent_job_id: number | null;
  status: string;
  options_json: Record<string, unknown> | null;
  error_message: string | null;
  hosts_scanned: number;
  hosts_matched: number;
  started_at: string;
  completed_at: string | null;
};

export type NetworkScanHostResult = {
  id: number;
  job_id: number;
  address: string;
  result_json: Record<string, unknown>;
};

export type NetworkScanJobDetail = NetworkScanJob & { host_results: NetworkScanHostResult[] };

export type NetworkScanDiscovery = {
  id: number;
  job_id: number;
  site_id: number;
  address: string;
  name_candidates_json: Record<string, string>;
  chosen_name_source: string | null;
  chosen_name: string | null;
  status: string;
  dcim_device_id: number | null;
  created_at: string;
};

export type NameSource = "snmp_sysname" | "ptr" | "ip" | "custom";
export type ParentFilter = "alive" | "snmp_ok";
export type InventoryMode = "none" | "discovered_queue" | "auto";

export function listNetworkScanTemplates(): Promise<NetworkScanTemplate[]> {
  return apiGet(`${P}/templates`);
}

export function createNetworkScanTemplate(body: {
  slug: string;
  name: string;
  kind: "ping" | "snmp_quick" | "tcp_ports";
  default_config?: Record<string, unknown> | null;
}): Promise<NetworkScanTemplate> {
  return apiPost(`${P}/templates`, body);
}

export function listPrefixBindings(ipv4PrefixId?: number): Promise<NetworkScanPrefixBinding[]> {
  const q = ipv4PrefixId != null ? `?ipv4_prefix_id=${encodeURIComponent(String(ipv4PrefixId))}` : "";
  return apiGet(`${P}/prefix-bindings${q}`);
}

export function createPrefixBinding(body: {
  template_id: number;
  ipv4_prefix_id: number;
  enabled?: boolean;
}): Promise<NetworkScanPrefixBinding> {
  return apiPost(`${P}/prefix-bindings`, body);
}

export function deletePrefixBinding(id: number): Promise<void> {
  return apiDelete(`${P}/prefix-bindings/${id}`);
}

export function createNetworkScanJob(body: {
  template_id: number;
  ipv4_prefix_id: number;
  options: {
    parent_job_id?: number | null;
    parent_filter?: ParentFilter | null;
    inventory_mode?: InventoryMode;
    name_priority?: NameSource[];
    default_device_model_id?: number | null;
    snmp_community?: string | null;
    snmp_port?: number | null;
  };
}): Promise<NetworkScanJob> {
  return apiPost(`${P}/jobs`, body);
}

export function listNetworkScanJobs(params?: { ipv4_prefix_id?: number; limit?: number }): Promise<NetworkScanJob[]> {
  const sp = new URLSearchParams();
  if (params?.ipv4_prefix_id != null) sp.set("ipv4_prefix_id", String(params.ipv4_prefix_id));
  if (params?.limit != null) sp.set("limit", String(params.limit));
  const q = sp.toString();
  return apiGet(`${P}/jobs${q ? `?${q}` : ""}`);
}

export function getNetworkScanJob(id: number): Promise<NetworkScanJobDetail> {
  return apiGet(`${P}/jobs/${id}`);
}

export function deleteNetworkScanJob(id: number): Promise<void> {
  return apiDelete(`${P}/jobs/${id}`);
}

export function listDiscoveries(params?: { status?: string; site_id?: number; limit?: number }): Promise<NetworkScanDiscovery[]> {
  const sp = new URLSearchParams();
  if (params?.status) sp.set("status", params.status);
  if (params?.site_id != null) sp.set("site_id", String(params.site_id));
  if (params?.limit != null) sp.set("limit", String(params.limit));
  const q = sp.toString();
  return apiGet(`${P}/discoveries${q ? `?${q}` : ""}`);
}

export function approveDiscovery(
  id: number,
  body: { chosen_name_source: NameSource; chosen_name?: string | null; device_model_id: number },
): Promise<NetworkScanDiscovery> {
  return apiPatch(`${P}/discoveries/${id}`, body);
}

export function rejectDiscovery(id: number): Promise<void> {
  return apiPostNoContent(`${P}/discoveries/${id}/reject`, {});
}
