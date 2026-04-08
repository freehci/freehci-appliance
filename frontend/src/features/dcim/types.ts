/** DCIM-entiteter som returneres fra `/api/v1/dcim`. */

export type Site = {
  id: number;
  name: string;
  slug: string;
  description: string | null;
  created_at: string;
};

export type Room = {
  id: number;
  site_id: number;
  name: string;
  description: string | null;
};

export type Rack = {
  id: number;
  room_id: number;
  name: string;
  u_height: number;
  sort_order: number;
};

export type Manufacturer = {
  id: number;
  name: string;
};

export type DeviceModel = {
  id: number;
  manufacturer_id: number | null;
  name: string;
  u_height: number;
  form_factor: string | null;
};

export type DeviceInstance = {
  id: number;
  device_model_id: number | null;
  name: string;
  serial_number: string | null;
  asset_tag: string | null;
};

export type RackPlacement = {
  id: number;
  rack_id: number;
  device_id: number;
  u_position: number;
  mounting: string;
};
