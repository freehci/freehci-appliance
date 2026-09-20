import { apiDelete, apiGet, apiPost } from "@/lib/api";

const P = "/api/v1/clusters";

export type ClusterKind = "proxmox" | "talos" | "other";

export type PlatformClusterMember = {
  id: number;
  cluster_id: number;
  device_id: number;
  role: string;
  created_at: string;
};

export type PlatformVirtualMachine = {
  id: number;
  name: string;
  slug: string;
  cluster_id: number;
  device_id: number | null;
  status: string;
  created_at: string;
};

export type PlatformCluster = {
  id: number;
  name: string;
  slug: string;
  kind: ClusterKind | string;
  site_id: number | null;
  description: string | null;
  created_at: string;
  members: PlatformClusterMember[];
  vms: PlatformVirtualMachine[];
};

export function listClusters(): Promise<PlatformCluster[]> {
  return apiGet(P);
}

export function createCluster(body: {
  name: string;
  slug?: string | null;
  kind: ClusterKind;
  description?: string | null;
}): Promise<PlatformCluster> {
  return apiPost(P, body);
}

export function addClusterMember(
  clusterId: number,
  body: { device_id: number; role?: string },
): Promise<PlatformClusterMember> {
  return apiPost(`${P}/${clusterId}/members`, body);
}

export function deleteCluster(id: number): Promise<void> {
  return apiDelete(`${P}/${id}`);
}

export function createVm(
  clusterId: number,
  body: { name: string; slug?: string | null; device_id?: number | null; status?: string },
): Promise<PlatformVirtualMachine> {
  return apiPost(`${P}/${clusterId}/vms`, body);
}
