import { apiGet, apiPost } from "@/lib/api";

const P = "/api/v1/service-catalog";

export type ServiceTemplateSpec = {
  kind: "device_instance";
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
  device_id: number;
  ipv4_address_id: number | null;
  status: string;
  created_at: string;
};

export type ServicePlan = {
  kind: string;
  template: { id: number; name: string | null; version: string };
  device: { id: number; name: string; site_id: number | null };
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
  device_id: number;
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
  device_id: number;
  ipv4_prefix_id?: number | null;
  name?: string | null;
}): Promise<ServiceDeployment> {
  return apiPost(`${P}/deployments`, body);
}

export function runDeployment(id: number): Promise<ServiceDeployment> {
  return apiPost(`${P}/deployments/${id}/run`, {});
}

export function listInstances(): Promise<ServiceInstance[]> {
  return apiGet(`${P}/instances`);
}
