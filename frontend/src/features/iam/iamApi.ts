import { apiDelete, apiGet, apiPatch, apiPost, apiPostMultipart, apiPostNoContent } from "@/lib/api";
import type { User } from "@/features/ipam/types";

const P = "/api/v1/iam";

/** Katalograd med `users.kind === "person"` (mennesker). */
export const IAM_KIND_PERSON = "person";
/** Tekniske identiteter som kjører integrasjoner og tjenester. */
export const IAM_KIND_SERVICE_ACCOUNT = "service_account";

export type IamRef = { id: number; name: string; slug: string };

export type PersonDetail = User & {
  roles: IamRef[];
  groups_direct: IamRef[];
  groups_effective: IamRef[];
};

export type IamRole = {
  id: number;
  name: string;
  slug: string;
  description: string | null;
  system: boolean;
  created_at: string;
};

export type IamRoleDetail = IamRole & {
  member_count: number;
  assignees: { id: number; username: string; display_name: string | null }[];
};

export type IamGroup = {
  id: number;
  name: string;
  slug: string;
  description: string | null;
  external_subject_id: string | null;
  identity_provider: string | null;
  created_at: string;
};

export type IamGroupDetail = IamGroup & {
  direct_users: { user_id: number; username: string; display_name: string | null }[];
  direct_subgroups: { child_group_id: number; name: string; slug: string }[];
  effective_user_ids: number[];
};

export function listPersons(limit = 500, kind?: string): Promise<User[]> {
  const q = new URLSearchParams();
  q.set("limit", String(limit));
  if (kind != null && kind !== "") q.set("kind", kind);
  return apiGet(`${P}/persons?${q.toString()}`);
}

export function getPerson(personId: number): Promise<PersonDetail> {
  return apiGet(`${P}/persons/${personId}`);
}

export function createPerson(body: {
  username: string;
  display_name?: string | null;
  email?: string | null;
  phone?: string | null;
  kind?: string;
  notes?: string | null;
  external_subject_id?: string | null;
  identity_provider?: string | null;
}): Promise<User> {
  return apiPost(`${P}/persons`, body);
}

export function patchPerson(
  personId: number,
  body: Partial<{
    display_name: string | null;
    email: string | null;
    phone: string | null;
    kind: string | null;
    notes: string | null;
    external_subject_id: string | null;
    identity_provider: string | null;
  }>,
): Promise<User> {
  return apiPatch(`${P}/persons/${personId}`, body);
}

export function assignPersonRole(personId: number, roleId: number): Promise<void> {
  return apiPostNoContent(`${P}/persons/${personId}/roles`, { role_id: roleId });
}

export function revokePersonRole(personId: number, roleId: number): Promise<void> {
  return apiDelete(`${P}/persons/${personId}/roles/${roleId}`);
}

export function listRoles(): Promise<IamRole[]> {
  return apiGet(`${P}/roles`);
}

export function getRole(roleId: number): Promise<IamRoleDetail> {
  return apiGet(`${P}/roles/${roleId}`);
}

export function createRole(body: { name: string; slug: string; description?: string | null }): Promise<IamRole> {
  return apiPost(`${P}/roles`, body);
}

export function patchRole(roleId: number, body: { name?: string; description?: string | null }): Promise<IamRole> {
  return apiPatch(`${P}/roles/${roleId}`, body);
}

export function deleteRole(roleId: number): Promise<void> {
  return apiDelete(`${P}/roles/${roleId}`);
}

export function listGroups(): Promise<IamGroup[]> {
  return apiGet(`${P}/groups`);
}

export function getGroup(groupId: number): Promise<IamGroupDetail> {
  return apiGet(`${P}/groups/${groupId}`);
}

export function createGroup(body: {
  name: string;
  slug: string;
  description?: string | null;
  external_subject_id?: string | null;
  identity_provider?: string | null;
}): Promise<IamGroup> {
  return apiPost(`${P}/groups`, body);
}

export function patchGroup(groupId: number, body: { name?: string; description?: string | null }): Promise<IamGroup> {
  return apiPatch(`${P}/groups/${groupId}`, body);
}

export function deleteGroup(groupId: number): Promise<void> {
  return apiDelete(`${P}/groups/${groupId}`);
}

export function addGroupUserMember(groupId: number, userId: number): Promise<void> {
  return apiPostNoContent(`${P}/groups/${groupId}/members/users`, { user_id: userId });
}

export function removeGroupUserMember(groupId: number, userId: number): Promise<void> {
  return apiDelete(`${P}/groups/${groupId}/members/users/${userId}`);
}

export function addGroupSubgroupMember(groupId: number, childGroupId: number): Promise<void> {
  return apiPostNoContent(`${P}/groups/${groupId}/members/groups`, { child_group_id: childGroupId });
}

export function removeGroupSubgroupMember(groupId: number, childGroupId: number): Promise<void> {
  return apiDelete(`${P}/groups/${groupId}/members/groups/${childGroupId}`);
}

export function avatarUrl(personId: number, cacheBust?: string | number): string {
  const q = cacheBust != null ? `?v=${encodeURIComponent(String(cacheBust))}` : "";
  return `${P}/persons/${personId}/avatar${q}`;
}

export function uploadPersonAvatar(personId: number, file: File): Promise<User> {
  const fd = new FormData();
  fd.set("file", file);
  return apiPostMultipart(`${P}/persons/${personId}/avatar`, fd);
}

export function deletePersonAvatar(personId: number): Promise<void> {
  return apiDelete(`${P}/persons/${personId}/avatar`);
}
