import { apiDelete, apiGet, apiPost } from "@/lib/api";

const P = "/api/v1/integration-connections";

export type IntegrationConnection = {
  id: number;
  name: string;
  slug: string;
  plugin_id: string;
  base_url: string | null;
  credential_ref: string | null;
  status: string;
  last_sync_at: string | null;
  mapping_json: Record<string, unknown> | null;
  description: string | null;
  created_at: string;
};

export type IdentityConflict = {
  id: number;
  identity_type: string;
  namespace: string;
  value: string;
  connection_a_id: number | null;
  connection_b_id: number | null;
  device_a_id: number | null;
  device_b_id: number | null;
  status: string;
  created_at: string;
};

export function listConnections(): Promise<IntegrationConnection[]> {
  return apiGet(P);
}

export function createConnection(body: {
  name: string;
  slug?: string | null;
  plugin_id: string;
  base_url?: string | null;
  credential_ref?: string | null;
}): Promise<IntegrationConnection> {
  return apiPost(P, body);
}

export function deleteConnection(id: number): Promise<void> {
  return apiDelete(`${P}/${id}`);
}

export function listConflicts(): Promise<IdentityConflict[]> {
  return apiGet(`${P}/conflicts`);
}
