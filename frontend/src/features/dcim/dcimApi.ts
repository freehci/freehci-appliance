import { apiDelete, apiDeleteJson, apiGet, apiPatch, apiPost, apiPostMultipart, apiUrl } from "@/lib/api";
import type {
  DeviceInstance,
  DeviceInterface,
  DeviceModel,
  DeviceType,
  IpAssignment,
  Manufacturer,
  ManufacturerDetail,
  Rack,
  RackPlacement,
  Room,
  Site,
} from "./types";

const P = "/api/v1/dcim";

export function listSites(): Promise<Site[]> {
  return apiGet(`${P}/sites`);
}

export function createSite(body: { name: string; slug: string; description?: string | null }): Promise<Site> {
  return apiPost(`${P}/sites`, body);
}

export function listRooms(siteId?: number): Promise<Room[]> {
  const q = siteId != null ? `?site_id=${encodeURIComponent(String(siteId))}` : "";
  return apiGet(`${P}/rooms${q}`);
}

export function createRoom(body: { site_id: number; name: string; description?: string | null }): Promise<Room> {
  return apiPost(`${P}/rooms`, body);
}

export function listRacks(roomId?: number): Promise<Rack[]> {
  const q = roomId != null ? `?room_id=${encodeURIComponent(String(roomId))}` : "";
  return apiGet(`${P}/racks${q}`);
}

export type RackWriteFields = {
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

export function createDeviceType(body: {
  name: string;
  slug: string;
  description?: string | null;
}): Promise<DeviceType> {
  return apiPost(`${P}/device-types`, body);
}

export function deleteDeviceType(id: number): Promise<void> {
  return apiDelete(`${P}/device-types/${id}`);
}

export function listDeviceModels(): Promise<DeviceModel[]> {
  return apiGet(`${P}/device-models`);
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
}): Promise<DeviceModel> {
  return apiPost(`${P}/device-models`, body);
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
