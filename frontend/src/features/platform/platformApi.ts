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

export type PlatformVirtualInterface = {
  id: number;
  name: string;
  slug: string;
  vm_id: number;
  status: string;
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
  interfaces?: PlatformVirtualInterface[];
  disks?: PlatformVirtualDisk[];
};

export type PlatformVirtualDisk = {
  id: number;
  name: string;
  slug: string;
  vm_id: number;
  storage_pool_id: number | null;
  kind: string;
  status: string;
  created_at: string;
};

export type PlatformStoragePool = {
  id: number;
  name: string;
  slug: string;
  cluster_id: number;
  kind: string;
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
  storage_pools: PlatformStoragePool[];
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

export function createStoragePool(
  clusterId: number,
  body: { name: string; slug?: string | null; kind: string; status?: string },
): Promise<PlatformStoragePool> {
  return apiPost(`${P}/${clusterId}/storage-pools`, body);
}

export function createVm(
  clusterId: number,
  body: { name: string; slug?: string | null; device_id?: number | null; status?: string },
): Promise<PlatformVirtualMachine> {
  return apiPost(`${P}/${clusterId}/vms`, body);
}

export function createVif(
  clusterId: number,
  vmId: number,
  body: { name: string; slug?: string | null; status?: string },
): Promise<PlatformVirtualInterface> {
  return apiPost(`${P}/${clusterId}/vms/${vmId}/interfaces`, body);
}

export function createDisk(
  clusterId: number,
  vmId: number,
  body: { name: string; slug?: string | null; kind: string; status?: string; storage_pool_id?: number | null },
): Promise<PlatformVirtualDisk> {
  return apiPost(`${P}/${clusterId}/vms/${vmId}/disks`, body);
}

const CLOUD = "/api/v1/cloud-subscriptions";

export type PlatformCloudSubscription = {
  id: number;
  name: string;
  slug: string;
  kind: string;
  status: string;
  description: string | null;
  created_at: string;
};

export function listCloudSubscriptions(): Promise<PlatformCloudSubscription[]> {
  return apiGet(CLOUD);
}

export function createCloudSubscription(body: {
  name: string;
  slug?: string | null;
  kind: string;
  status?: string;
}): Promise<PlatformCloudSubscription> {
  return apiPost(CLOUD, body);
}
