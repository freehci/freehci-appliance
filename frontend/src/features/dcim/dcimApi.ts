import { apiDelete, apiGet, apiPost } from "@/lib/api";
import type {
  DeviceInstance,
  DeviceModel,
  Manufacturer,
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

export function createRack(body: {
  room_id: number;
  name: string;
  u_height?: number;
  sort_order?: number;
}): Promise<Rack> {
  return apiPost(`${P}/racks`, body);
}

export function listManufacturers(): Promise<Manufacturer[]> {
  return apiGet(`${P}/manufacturers`);
}

export function createManufacturer(body: { name: string }): Promise<Manufacturer> {
  return apiPost(`${P}/manufacturers`, body);
}

export function deleteManufacturer(id: number): Promise<void> {
  return apiDelete(`${P}/manufacturers/${id}`);
}

export function listDeviceModels(): Promise<DeviceModel[]> {
  return apiGet(`${P}/device-models`);
}

export function createDeviceModel(body: {
  manufacturer_id?: number | null;
  name: string;
  u_height?: number;
  form_factor?: string | null;
  image_front_url?: string | null;
  image_back_url?: string | null;
}): Promise<DeviceModel> {
  return apiPost(`${P}/device-models`, body);
}

export function listDevices(): Promise<DeviceInstance[]> {
  return apiGet(`${P}/devices`);
}

export function createDevice(body: {
  device_model_id?: number | null;
  name: string;
  serial_number?: string | null;
  asset_tag?: string | null;
}): Promise<DeviceInstance> {
  return apiPost(`${P}/devices`, body);
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

export function deletePlacement(id: number): Promise<void> {
  return apiDelete(`${P}/placements/${id}`);
}
