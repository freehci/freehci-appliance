import { apiGet, apiPost } from "@/lib/api";

export type FederationPeer = {
  id: number;
  instance_uuid: string;
  name: string;
  base_url: string;
  status: string;
  last_seen_at: string | null;
};

export type FederationTenantRole = {
  tenant_id: number;
  tenant_slug: string;
  tenant_name: string;
  primary_instance_uuid: string;
  is_primary_here: boolean;
  frozen: boolean;
  last_pull_at: string | null;
};

export type FederationStatus = {
  instance_uuid: string;
  name: string;
  peers: FederationPeer[];
  tenants: FederationTenantRole[];
};

export type FederationPairingCreated = {
  token: string;
  instance_uuid: string;
  name: string;
  expires_at: string;
};

export type FederationConsistency = {
  tenant_slug: string;
  checksum: string;
  peer_checksum: string | null;
  match: boolean | null;
  frozen: boolean;
  is_primary_here: boolean;
};

export type FederationPromote = {
  tenant_slug: string;
  primary_instance_uuid: string;
  checksum: string;
  match: boolean;
};

export function federationStatus(): Promise<FederationStatus> {
  return apiGet("/api/v1/federation/status");
}

export function createPairingToken(): Promise<FederationPairingCreated> {
  return apiPost("/api/v1/federation/pairing-tokens", {});
}

export function connectToExisting(body: {
  base_url: string;
  pairing_token: string;
  advertised_base_url?: string | null;
}): Promise<FederationPeer> {
  return apiPost("/api/v1/federation/connect", body);
}

export function pingPeer(peerId: number): Promise<FederationPeer> {
  return apiPost(`/api/v1/federation/peers/${peerId}/ping`, {});
}

export function pullTenant(tenantSlug: string, peerId?: number): Promise<{ checksum: string; applied: boolean }> {
  return apiPost("/api/v1/federation/pull", { tenant_slug: tenantSlug, peer_id: peerId ?? null });
}

export function consistency(tenantSlug: string, peerId?: number): Promise<FederationConsistency> {
  const q = peerId != null ? `?peer_id=${peerId}` : "";
  return apiGet(`/api/v1/federation/tenants/${encodeURIComponent(tenantSlug)}/consistency${q}`);
}

export function promoteTenant(tenantSlug: string, peerId?: number): Promise<FederationPromote> {
  return apiPost("/api/v1/federation/promote", { tenant_slug: tenantSlug, peer_id: peerId ?? null });
}

export function freezeTenant(tenantSlug: string, frozen: boolean): Promise<FederationTenantRole> {
  return apiPost(`/api/v1/federation/tenants/${encodeURIComponent(tenantSlug)}/freeze`, { frozen });
}
