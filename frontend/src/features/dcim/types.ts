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
  /** Ytre høyde i mm (H). */
  height_mm: number | null;
  /** Bredde i mm (B). */
  width_mm: number | null;
  /** Dybde i mm (D). */
  depth_mm: number | null;
  brand: string | null;
  purchase_date: string | null;
  commissioned_date: string | null;
  notes: string | null;
  /** Tilpassede nøkkel/verdi; f.eks. rack_type for fremtidige skjemaer eller plugin-data. */
  attributes: Record<string, unknown> | null;
};

export type Manufacturer = {
  id: number;
  name: string;
  description: string | null;
  website_url: string | null;
  has_logo: boolean;
  /** IANA private enterprise number (1.3.6.1.4.1.<pen>) — kobling mot SNMP MIB-enterprise. */
  iana_enterprise_number?: number | null;
};

export type DeviceType = {
  id: number;
  name: string;
  slug: string;
  description: string | null;
};

export type DeviceModelBrief = {
  id: number;
  name: string;
  u_height: number;
  device_type_id: number | null;
};

export type ManufacturerDetail = Manufacturer & {
  device_models: DeviceModelBrief[];
};

export type DeviceModel = {
  id: number;
  manufacturer_id: number | null;
  device_type_id: number | null;
  name: string;
  u_height: number;
  form_factor: string | null;
  image_front_url: string | null;
  image_back_url: string | null;
  image_product_url: string | null;
  has_image_front_file: boolean;
  has_image_back_file: boolean;
  has_image_product_file: boolean;
};

export type DeviceInstance = {
  id: number;
  device_model_id: number | null;
  device_type_id: number | null;
  effective_device_type_id: number | null;
  /** Site fra rack-plassering; null hvis enheten ikke er plassert */
  effective_site_id: number | null;
  name: string;
  serial_number: string | null;
  asset_tag: string | null;
  attributes: Record<string, unknown>;
};

/** IP-tildeling på et grensesnitt (IPAM-forberedelse). */
export type IpAssignment = {
  id: number;
  interface_id: number;
  ipv4_prefix_id: number | null;
  family: string;
  address: string;
  is_primary: boolean;
};

/** Port / interface on a device (forberedelse for IPAM). */
export type DeviceInterface = {
  id: number;
  device_id: number;
  /** Fysisk/logisk hierarki (f.eks. Juniper me0 → me0.0). */
  parent_interface_id: number | null;
  name: string;
  description: string | null;
  mac_address: string | null;
  speed_mbps: number | null;
  mtu: number | null;
  /** 802.1Q (1–4094), valgfritt */
  vlan_id: number | null;
  enabled: boolean;
  sort_order: number;
  ip_assignments: IpAssignment[];
};

export type RackPlacement = {
  id: number;
  rack_id: number;
  device_id: number;
  u_position: number;
  mounting: string;
};
