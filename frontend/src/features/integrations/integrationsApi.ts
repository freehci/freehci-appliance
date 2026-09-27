import { apiDelete, apiGet, apiPatch, apiPost } from "@/lib/api";

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

export const OWNED_DEVICE_FIELDS = [
  "name",
  "serial_number",
  "asset_tag",
  "site_id",
  "device_role_id",
  "device_type_id",
  "device_model_id",
] as const;

export type ExternalObjectMapping = {
  id: number;
  connection_id: number;
  object_type: string;
  external_id: string;
  device_id: number | null;
  created_at: string;
};

export type FieldOwnership = {
  id: number;
  connection_id: number;
  device_id: number;
  field_name: string;
  created_at: string;
};

export function listObjectMaps(): Promise<ExternalObjectMapping[]> {
  return apiGet("/api/v1/external-object-maps");
}

export function createObjectMap(body: {
  connection_id: number;
  object_type: string;
  external_id: string;
  device_id?: number | null;
}): Promise<ExternalObjectMapping> {
  return apiPost("/api/v1/external-object-maps", body);
}

export function patchObjectMap(id: number, body: { device_id: number | null }): Promise<ExternalObjectMapping> {
  return apiPatch(`/api/v1/external-object-maps/${id}`, body);
}

export function deleteObjectMap(id: number): Promise<void> {
  return apiDelete(`/api/v1/external-object-maps/${id}`);
}

export function listFieldOwns(): Promise<FieldOwnership[]> {
  return apiGet("/api/v1/field-ownerships");
}

export function createFieldOwn(body: {
  connection_id: number;
  device_id: number;
  field_name: string;
}): Promise<FieldOwnership> {
  return apiPost("/api/v1/field-ownerships", body);
}

export function deleteFieldOwn(id: number): Promise<void> {
  return apiDelete(`/api/v1/field-ownerships/${id}`);
}
