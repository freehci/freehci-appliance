import {
  apiDelete,
  apiDeleteJson,
  apiGet,
  apiPatch,
  apiPost,
  apiPostMultipart,
  apiUrl,
  fetchAuthedBlobUrl,
} from "@/lib/api";
import type {
  Component,
  ComponentClass,
  ComponentClassField,
  ComponentFieldImpact,
  DeviceInstance,
  DeviceInstanceComponent,
  DeviceInterface,
  DeviceIpAssignment,
  DeviceModel,
  DeviceModelComponent,
  DeviceType,
  IpAssignment,
  Manufacturer,
  ManufacturerDetail,
  Rack,
  RackPlacement,
  Room,
  Site,
  SiteAccessGrant,
  SiteRole,
} from "./types";

const P = "/api/v1/dcim";

export function listSites(): Promise<Site[]> {
  return apiGet(`${P}/sites`);
}

export function createSite(body: {
  name: string;
  slug: string;
  description?: string | null;
  tenant_id?: number | null;
}): Promise<Site> {
  return apiPost(`${P}/sites`, body);
}

export function updateSite(
  id: number,
  body: Partial<
    Pick<
      Site,
      | "tenant_id"
      | "name"
      | "description"
      | "address_line1"
      | "address_line2"
      | "postal_code"
      | "city"
      | "county"
      | "country"
      | "latitude"
      | "longitude"
      | "address_note"
    >
  >,
): Promise<Site> {
  return apiPatch(`${P}/sites/${id}`, body);
}

const PT = "/api/v1/tenants";

export type Tenant = {
  id: number;
  name: string;
  slug: string;
  description: string | null;
  created_at: string;
};

export function listTenants(): Promise<Tenant[]> {
  return apiGet(PT);
}

export function createTenant(body: { name: string; slug: string; description?: string | null }): Promise<Tenant> {
  return apiPost(PT, body);
}

export type TenantUserMembership = {
  id: number;
  tenant_id: number;
  user_id: number;
  role: string;
  created_at: string;
};

export type TenantDcimGrant = {
  id: number;
  tenant_id: number;
  scope_type: string;
  scope_id: number;
  access: string;
  created_at: string;
};

export function listTenantMembers(tenantId: number): Promise<TenantUserMembership[]> {
  return apiGet(`${PT}/${tenantId}/members`);
}

export function addTenantMember(
  tenantId: number,
  body: { user_id: number; role?: string },
): Promise<TenantUserMembership> {
  return apiPost(`${PT}/${tenantId}/members`, body);
}

export function removeTenantMember(tenantId: number, userId: number): Promise<void> {
  return apiDelete(`${PT}/${tenantId}/members/${userId}`);
}

export function listTenantDcimGrants(tenantId: number): Promise<TenantDcimGrant[]> {
  return apiGet(`${PT}/${tenantId}/dcim-grants`);
}

export function addTenantDcimGrant(
  tenantId: number,
  body: { scope_type: "site" | "room" | "rack"; scope_id: number; access?: "view" | "manage" },
): Promise<TenantDcimGrant> {
  return apiPost(`${PT}/${tenantId}/dcim-grants`, body);
}

export function removeTenantDcimGrant(tenantId: number, grantId: number): Promise<void> {
  return apiDelete(`${PT}/${tenantId}/dcim-grants/${grantId}`);
}

export type SiteGeocodeCandidate = { display_name: string; latitude: number; longitude: number };
export type SiteGeocodeResponse = { query: string; candidates: SiteGeocodeCandidate[] };

export function geocodeSite(
  id: number,
  body: { query?: string | null; limit?: number },
): Promise<SiteGeocodeResponse> {
  return apiPost(`${P}/sites/${id}/geocode`, body);
}

export function listSiteRoles(): Promise<SiteRole[]> {
  return apiGet(`${P}/site-roles`);
}

export function listSiteAccess(siteId: number, isContact?: boolean): Promise<SiteAccessGrant[]> {
  const q = isContact != null ? `?is_contact=${encodeURIComponent(String(isContact))}` : "";
  return apiGet(`${P}/sites/${siteId}/access${q}`);
}

export function createSiteAccess(siteId: number, body: {
  user_id: number;
  role_id: number;
  is_contact: boolean;
  notes?: string | null;
}): Promise<SiteAccessGrant> {
  return apiPost(`${P}/sites/${siteId}/access`, body);
}

export function deleteSiteAccess(siteId: number, grantId: number): Promise<void> {
  return apiDelete(`${P}/sites/${siteId}/access/${grantId}`);
}

export function listRooms(siteId?: number): Promise<Room[]> {
  const q = siteId != null ? `?site_id=${encodeURIComponent(String(siteId))}` : "";
  return apiGet(`${P}/rooms${q}`);
}

export function getRoom(id: number): Promise<Room> {
  return apiGet(`${P}/rooms/${id}`);
}

export function createRoom(body: {
  site_id: number;
  name: string;
  description?: string | null;
  floor?: string | null;
}): Promise<Room> {
  return apiPost(`${P}/rooms`, body);
}

export function updateRoom(
  id: number,
  body: {
    site_id?: number;
    name?: string;
    description?: string | null;
    floor?: string | null;
  },
): Promise<Room> {
  return apiPatch(`${P}/rooms/${id}`, body);
}

export function deleteRoom(id: number): Promise<void> {
  return apiDelete(`${P}/rooms/${id}`);
}

export function roomFloorplanUrl(id: number, version?: string): string {
  const q = version != null && version !== "" ? `?v=${encodeURIComponent(version)}` : "";
  return apiUrl(`${P}/rooms/${id}/floorplan${q}`);
}

/** Blob-URL for bruk i `<img src>` når API krever Bearer (må revokeObjectURL ved opprydding). */
export function fetchRoomFloorplanBlobUrl(id: number, version?: string): Promise<string> {
  const q = version != null && version !== "" ? `?v=${encodeURIComponent(version)}` : "";
  return fetchAuthedBlobUrl(`${P}/rooms/${id}/floorplan${q}`);
}

export function uploadRoomFloorplan(id: number, file: File): Promise<Room> {
  const fd = new FormData();
  fd.append("file", file);
  return apiPostMultipart(`${P}/rooms/${id}/floorplan`, fd);
}

export function deleteRoomFloorplan(id: number): Promise<Room> {
  return apiDeleteJson(`${P}/rooms/${id}/floorplan`);
}

export function listRacks(roomId?: number): Promise<Rack[]> {
  const q = roomId != null ? `?room_id=${encodeURIComponent(String(roomId))}` : "";
  return apiGet(`${P}/racks${q}`);
}

export type RackWriteFields = {
  tenant_id?: number | null;
  u_height?: number;
  sort_order?: number;
  height_mm?: number | null;
  width_mm?: number | null;
  depth_mm?: number | null;
  brand?: string | null;
  purchase_date?: string | null;
  commissioned_date?: string | null;
  notes?: string | null;
  attributes?: Record<string, unknown> | null;
};

export function createRack(
  body: {
    room_id: number;
    name: string;
  } & RackWriteFields,
): Promise<Rack> {
  return apiPost(`${P}/racks`, body);
}

export function updateRack(id: number, body: { name?: string } & RackWriteFields): Promise<Rack> {
  return apiPatch(`${P}/racks/${id}`, body);
}

export function listManufacturers(): Promise<Manufacturer[]> {
  return apiGet(`${P}/manufacturers`);
}

export function getManufacturer(id: number): Promise<ManufacturerDetail> {
  return apiGet(`${P}/manufacturers/${id}`);
}

export function createManufacturer(body: {
  name: string;
  description?: string | null;
  website_url?: string | null;
}): Promise<Manufacturer> {
  return apiPost(`${P}/manufacturers`, body);
}

export function updateManufacturer(
  id: number,
  body: {
    name?: string;
    description?: string | null;
    website_url?: string | null;
    iana_enterprise_number?: number | null;
  },
): Promise<Manufacturer> {
  return apiPatch(`${P}/manufacturers/${id}`, body);
}

export function manufacturerLogoUrl(id: number, version?: string): string {
  const q = version != null && version !== "" ? `?v=${encodeURIComponent(version)}` : "";
  return apiUrl(`${P}/manufacturers/${id}/logo${q}`);
}

export function uploadManufacturerLogo(id: number, file: File): Promise<Manufacturer> {
  const fd = new FormData();
  fd.append("file", file);
  return apiPostMultipart(`${P}/manufacturers/${id}/logo`, fd);
}

export function deleteManufacturerLogo(id: number): Promise<Manufacturer> {
  return apiDeleteJson(`${P}/manufacturers/${id}/logo`);
}

export function deleteManufacturer(id: number): Promise<void> {
  return apiDelete(`${P}/manufacturers/${id}`);
}

export function listDeviceTypes(): Promise<DeviceType[]> {
  return apiGet(`${P}/device-types`);
}

export function getDeviceType(id: number): Promise<DeviceType> {
  return apiGet(`${P}/device-types/${id}`);
}

export function createDeviceType(body: {
  name: string;
  slug: string;
  description?: string | null;
  fa_icon?: string | null;
}): Promise<DeviceType> {
  return apiPost(`${P}/device-types`, body);
}

export function updateDeviceType(
  id: number,
  body: { name?: string; description?: string | null; fa_icon?: string | null },
): Promise<DeviceType> {
  return apiPatch(`${P}/device-types/${id}`, body);
}

export function deleteDeviceType(id: number): Promise<void> {
  return apiDelete(`${P}/device-types/${id}`);
}

export function listComponentClasses(): Promise<ComponentClass[]> {
  return apiGet(`${P}/component-classes`);
}

export function createComponentClass(body: {
  name: string;
  slug: string;
  description?: string | null;
  icon?: string | null;
  active?: boolean;
}): Promise<ComponentClass> {
  return apiPost(`${P}/component-classes`, body);
}

export function updateComponentClass(
  id: number,
  body: { name?: string; description?: string | null; icon?: string | null; active?: boolean },
): Promise<ComponentClass> {
  return apiPatch(`${P}/component-classes/${id}`, body);
}

export function deleteComponentClass(id: number): Promise<void> {
  return apiDelete(`${P}/component-classes/${id}`);
}

export function listComponentClassFields(classId: number): Promise<ComponentClassField[]> {
  return apiGet(`${P}/component-classes/${classId}/fields`);
}

export function createComponentClassField(
  classId: number,
  body: Omit<ComponentClassField, "id" | "class_id">,
): Promise<ComponentClassField> {
  return apiPost(`${P}/component-classes/${classId}/fields`, body);
}

export function updateComponentClassField(
  fieldId: number,
  body: Partial<Omit<ComponentClassField, "id" | "class_id" | "key">>,
  force = false,
): Promise<ComponentClassField> {
  const q = force ? "?force=true" : "";
  return apiPatch(`${P}/component-class-fields/${fieldId}${q}`, body);
}

export function componentFieldImpact(
  fieldId: number,
  body: Partial<Omit<ComponentClassField, "id" | "class_id" | "key">>,
): Promise<ComponentFieldImpact> {
  return apiPost(`${P}/component-class-fields/${fieldId}/impact`, body);
}

export function deleteComponentClassField(fieldId: number, force = false): Promise<void> {
  const q = force ? "?force=true" : "";
  return apiDelete(`${P}/component-class-fields/${fieldId}${q}`);
}

export function listComponents(filters?: { class_id?: number; manufacturer_id?: number }): Promise<Component[]> {
  const qs = new URLSearchParams();
  if (filters?.class_id != null) qs.set("class_id", String(filters.class_id));
  if (filters?.manufacturer_id != null) qs.set("manufacturer_id", String(filters.manufacturer_id));
  const q = qs.toString();
  return apiGet(`${P}/components${q ? `?${q}` : ""}`);
}

export function createComponent(body: {
  class_id: number;
  manufacturer_id?: number | null;
  name: string;
  part_number?: string | null;
  description?: string | null;
  specs_json?: Record<string, unknown> | null;
  active?: boolean;
}): Promise<Component> {
  return apiPost(`${P}/components`, body);
}

export function updateComponent(
  id: number,
  body: Partial<{
    class_id: number;
    manufacturer_id: number | null;
    name: string;
    part_number: string | null;
    description: string | null;
    specs_json: Record<string, unknown> | null;
    active: boolean;
  }>,
): Promise<Component> {
  return apiPatch(`${P}/components/${id}`, body);
}

export function deleteComponent(id: number): Promise<void> {
  return apiDelete(`${P}/components/${id}`);
}

export function listDeviceModels(): Promise<DeviceModel[]> {
  return apiGet(`${P}/device-models`);
}

export function getDeviceModel(id: number): Promise<DeviceModel> {
  return apiGet(`${P}/device-models/${id}`);
}

export function createDeviceModel(body: {
  manufacturer_id?: number | null;
  device_type_id?: number | null;
  name: string;
  u_height?: number;
  form_factor?: string | null;
  image_front_url?: string | null;
  image_back_url?: string | null;
  image_product_url?: string | null;
  snmp_sys_object_id_prefix?: string | null;
}): Promise<DeviceModel> {
  return apiPost(`${P}/device-models`, body);
}

export function updateDeviceModel(
  id: number,
  body: {
    manufacturer_id?: number | null;
    device_type_id?: number | null;
    name?: string;
    u_height?: number;
    form_factor?: string | null;
    image_front_url?: string | null;
    image_back_url?: string | null;
    image_product_url?: string | null;
    snmp_sys_object_id_prefix?: string | null;
  },
): Promise<DeviceModel> {
  return apiPatch(`${P}/device-models/${id}`, body);
}

export function matchDeviceModelsBySnmpOid(numericOid: string): Promise<DeviceModel[]> {
  const q = `?numeric_oid=${encodeURIComponent(numericOid)}`;
  return apiGet(`${P}/device-models/match-snmp${q}`);
}

export function deleteDeviceModel(id: number): Promise<void> {
  return apiDelete(`${P}/device-models/${id}`);
}

export function listDeviceModelComponents(modelId: number): Promise<DeviceModelComponent[]> {
  return apiGet(`${P}/device-models/${modelId}/components`);
}

export function createDeviceModelComponent(
  modelId: number,
  body: {
    component_id: number;
    quantity?: number;
    slot_label?: string | null;
    notes?: string | null;
    overrides_json?: Record<string, unknown> | null;
    sort_order?: number;
  },
): Promise<DeviceModelComponent> {
  return apiPost(`${P}/device-models/${modelId}/components`, body);
}

export function updateDeviceModelComponent(
  modelId: number,
  linkId: number,
  body: Partial<{
    component_id: number;
    quantity: number;
    slot_label: string | null;
    notes: string | null;
    overrides_json: Record<string, unknown> | null;
    sort_order: number;
  }>,
): Promise<DeviceModelComponent> {
  return apiPatch(`${P}/device-models/${modelId}/components/${linkId}`, body);
}

export function deleteDeviceModelComponent(modelId: number, linkId: number): Promise<void> {
  return apiDelete(`${P}/device-models/${modelId}/components/${linkId}`);
}

export function uploadDeviceModelImageFront(id: number, file: File): Promise<DeviceModel> {
  const fd = new FormData();
  fd.append("file", file);
  return apiPostMultipart(`${P}/device-models/${id}/image-front`, fd);
}

export function uploadDeviceModelImageBack(id: number, file: File): Promise<DeviceModel> {
  const fd = new FormData();
  fd.append("file", file);
  return apiPostMultipart(`${P}/device-models/${id}/image-back`, fd);
}

export function deleteDeviceModelImageFront(id: number): Promise<DeviceModel> {
  return apiDeleteJson(`${P}/device-models/${id}/image-front`);
}

export function deleteDeviceModelImageBack(id: number): Promise<DeviceModel> {
  return apiDeleteJson(`${P}/device-models/${id}/image-back`);
}

export function uploadDeviceModelImageProduct(id: number, file: File): Promise<DeviceModel> {
  const fd = new FormData();
  fd.append("file", file);
  return apiPostMultipart(`${P}/device-models/${id}/image-product`, fd);
}

export function deleteDeviceModelImageProduct(id: number): Promise<DeviceModel> {
  return apiDeleteJson(`${P}/device-models/${id}/image-product`);
}

export function listDevices(): Promise<DeviceInstance[]> {
  return apiGet(`${P}/devices`);
}

export function getDevice(id: number): Promise<DeviceInstance> {
  return apiGet(`${P}/devices/${id}`);
}

export function listDeviceInterfaces(deviceId: number): Promise<DeviceInterface[]> {
  return apiGet(`${P}/devices/${deviceId}/interfaces`);
}

export function listDeviceInstanceComponents(deviceId: number): Promise<DeviceInstanceComponent[]> {
  return apiGet(`${P}/devices/${deviceId}/components`);
}

export function createDeviceInstanceComponent(
  deviceId: number,
  body: {
    component_id: number;
    quantity?: number;
    slot_label?: string | null;
    serial_number?: string | null;
    asset_tag?: string | null;
    installed_at?: string | null;
    notes?: string | null;
    overrides_json?: Record<string, unknown> | null;
    sort_order?: number;
  },
): Promise<DeviceInstanceComponent> {
  return apiPost(`${P}/devices/${deviceId}/components`, body);
}

export function copyDeviceComponentsFromModel(deviceId: number): Promise<DeviceInstanceComponent[]> {
  return apiPost(`${P}/devices/${deviceId}/components/copy-from-model`, {});
}

export function updateDeviceInstanceComponent(
  deviceId: number,
  linkId: number,
  body: Partial<{
    component_id: number;
    quantity: number;
    slot_label: string | null;
    serial_number: string | null;
    asset_tag: string | null;
    installed_at: string | null;
    notes: string | null;
    overrides_json: Record<string, unknown> | null;
    sort_order: number;
  }>,
): Promise<DeviceInstanceComponent> {
  return apiPatch(`${P}/devices/${deviceId}/components/${linkId}`, body);
}

export function deleteDeviceInstanceComponent(deviceId: number, linkId: number): Promise<void> {
  return apiDelete(`${P}/devices/${deviceId}/components/${linkId}`);
}

export function createDeviceInterface(
  deviceId: number,
  body: {
    name: string;
    description?: string | null;
    mac_address?: string | null;
    speed_mbps?: number | null;
    mtu?: number | null;
    vlan_id?: number | null;
    enabled?: boolean;
    sort_order?: number;
    parent_interface_id?: number | null;
  },
): Promise<DeviceInterface> {
  return apiPost(`${P}/devices/${deviceId}/interfaces`, body);
}

export function updateDeviceInterface(
  deviceId: number,
  interfaceId: number,
  body: {
    name?: string;
    description?: string | null;
    mac_address?: string | null;
    speed_mbps?: number | null;
    mtu?: number | null;
    vlan_id?: number | null;
    enabled?: boolean;
    sort_order?: number;
    parent_interface_id?: number | null;
  },
): Promise<DeviceInterface> {
  return apiPatch(`${P}/devices/${deviceId}/interfaces/${interfaceId}`, body);
}

export function deleteDeviceInterface(deviceId: number, interfaceId: number): Promise<void> {
  return apiDelete(`${P}/devices/${deviceId}/interfaces/${interfaceId}`);
}

export function createIfaceIpAssignment(
  deviceId: number,
  interfaceId: number,
  body: { address: string; is_primary?: boolean; ipv4_prefix_id?: number | null },
): Promise<IpAssignment> {
  return apiPost(`${P}/devices/${deviceId}/interfaces/${interfaceId}/ip-assignments`, body);
}

export function updateIfaceIpAssignment(
  deviceId: number,
  interfaceId: number,
  assignmentId: number,
  body: { is_primary?: boolean; ipv4_prefix_id?: number | null },
): Promise<IpAssignment> {
  return apiPatch(`${P}/devices/${deviceId}/interfaces/${interfaceId}/ip-assignments/${assignmentId}`, body);
}

export function deleteIfaceIpAssignment(
  deviceId: number,
  interfaceId: number,
  assignmentId: number,
): Promise<void> {
  return apiDelete(`${P}/devices/${deviceId}/interfaces/${interfaceId}/ip-assignments/${assignmentId}`);
}

export function listDeviceIpAssignments(deviceId: number): Promise<DeviceIpAssignment[]> {
  return apiGet(`${P}/devices/${deviceId}/device-ip-assignments`);
}

export function createDeviceIpAssignment(
  deviceId: number,
  body: { address: string; is_primary?: boolean; ipv4_prefix_id?: number | null },
): Promise<DeviceIpAssignment> {
  return apiPost(`${P}/devices/${deviceId}/device-ip-assignments`, body);
}

export function updateDeviceIpAssignment(
  deviceId: number,
  assignmentId: number,
  body: { is_primary?: boolean; ipv4_prefix_id?: number | null },
): Promise<DeviceIpAssignment> {
  return apiPatch(`${P}/devices/${deviceId}/device-ip-assignments/${assignmentId}`, body);
}

export function deleteDeviceIpAssignment(deviceId: number, assignmentId: number): Promise<void> {
  return apiDelete(`${P}/devices/${deviceId}/device-ip-assignments/${assignmentId}`);
}

export function createDevice(body: {
  device_model_id?: number | null;
  device_type_id?: number | null;
  name: string;
  serial_number?: string | null;
  asset_tag?: string | null;
  attributes?: Record<string, unknown> | null;
}): Promise<DeviceInstance> {
  return apiPost(`${P}/devices`, body);
}

export function updateDevice(
  id: number,
  body: {
    device_model_id?: number | null;
    device_type_id?: number | null;
    name?: string;
    serial_number?: string | null;
    asset_tag?: string | null;
    attributes?: Record<string, unknown> | null;
  },
): Promise<DeviceInstance> {
  return apiPatch(`${P}/devices/${id}`, body);
}

export function listPlacements(rackId?: number): Promise<RackPlacement[]> {
  const q = rackId != null ? `?rack_id=${encodeURIComponent(String(rackId))}` : "";
  return apiGet(`${P}/placements${q}`);
}

export function createPlacement(body: {
  rack_id: number;
  device_id: number;
  u_position: number;
  mounting?: string;
}): Promise<RackPlacement> {
  return apiPost(`${P}/placements`, body);
}

export function updatePlacement(
  id: number,
  body: { rack_id?: number; u_position?: number; mounting?: string },
): Promise<RackPlacement> {
  return apiPatch(`${P}/placements/${id}`, body);
}

export function deletePlacement(id: number): Promise<void> {
  return apiDelete(`${P}/placements/${id}`);
}
