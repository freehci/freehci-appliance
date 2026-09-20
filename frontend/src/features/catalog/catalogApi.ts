import { apiGet, apiPost } from "@/lib/api";

const P = "/api/v1/service-catalog";

export type ServiceTemplateSpec = {
  kind: "device_instance" | "cluster" | "virtual_machine" | "storage_pool" | "virtual_interface";
  reserve_ipv4: boolean;
};

export type ServiceTemplateVersion = {
  id: number;
  template_id: number;
  version: string;
  spec: ServiceTemplateSpec;
  created_at: string;
};

export type ServiceTemplate = {
  id: number;
  name: string;
  slug: string;
  description: string | null;
  created_at: string;
  versions: ServiceTemplateVersion[];
};

export type ServiceDeploymentStep = {
  id: number;
  name: string;
  status: string;
  detail: string | null;
  created_at: string;
};

export type ServiceInstance = {
  id: number;
  name: string;
  slug: string;
  template_version_id: number;
  deployment_id: number;
  device_id: number | null;
  cluster_id: number | null;
  vm_id: number | null;
  storage_pool_id: number | null;
  virtual_interface_id: number | null;
  ipv4_address_id: number | null;
  status: string;
  created_at: string;
};

export type ServicePlan = {
  kind: string;
  template: { id: number; name: string | null; version: string };
  device?: { id: number; name: string; site_id: number | null };
  devices?: { id: number; name: string; site_id: number | null }[];
  cluster?: { id?: number; name: string | null; kind: string; slug: string | null } | null;
  vm?: { name: string | null; slug: string | null };
  storage?: { name: string | null; slug: string | null; kind: string };
  vif?: { name: string | null; slug: string | null };
  reserve_ipv4: boolean;
  prefix: {
    id: number;
    cidr: string;
    name: string;
    site_id: number;
    used_count: number;
    usable_hosts: number;
  } | null;
  blockers: string[];
  can_run: boolean;
  notes: string[];
  requested_name?: string | null;
};

export type ServiceDeployment = {
  id: number;
  template_version_id: number;
  device_id: number | null;
  cluster_id: number | null;
  vm_id: number | null;
  storage_pool_id: number | null;
  virtual_interface_id: number | null;
  ipv4_prefix_id: number | null;
  status: string;
  plan_json: ServicePlan | null;
  created_at: string;
  started_at: string | null;
  finished_at: string | null;
  steps: ServiceDeploymentStep[];
  instance: ServiceInstance | null;
};

export function listTemplates(): Promise<ServiceTemplate[]> {
  return apiGet(`${P}/templates`);
}

export function createTemplate(body: {
  name: string;
  slug?: string | null;
  description?: string | null;
  spec: ServiceTemplateSpec;
}): Promise<ServiceTemplate> {
  return apiPost(`${P}/templates`, body);
}

export function listDeployments(): Promise<ServiceDeployment[]> {
  return apiGet(`${P}/deployments`);
}

export function createDeployment(body: {
  template_version_id: number;
  device_id?: number | null;
  device_ids?: number[];
  ipv4_prefix_id?: number | null;
  name?: string | null;
  cluster_kind?: string | null;
  cluster_id?: number | null;
  storage_kind?: string | null;
  vm_id?: number | null;
}): Promise<ServiceDeployment> {
  return apiPost(`${P}/deployments`, body);
}

export function runDeployment(id: number): Promise<ServiceDeployment> {
  return apiPost(`${P}/deployments/${id}/run`, {});
}

export function listInstances(): Promise<ServiceInstance[]> {
  return apiGet(`${P}/instances`);
}
