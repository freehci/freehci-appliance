/** DCIM-entiteter som returneres fra `/api/v1/dcim`. */

export type Site = {
  id: number;
  tenant_id: number;
  name: string;
  slug: string;
  description: string | null;
  address_line1?: string | null;
  address_line2?: string | null;
  postal_code?: string | null;
  city?: string | null;
  county?: string | null;
  country?: string | null;
  latitude?: number | null;
  longitude?: number | null;
  address_note?: string | null;
  created_at: string;
};

export type SiteRole = {
  id: number;
  name: string;
  slug: string;
  description: string | null;
};

export type SiteAccessGrant = {
  id: number;
  site_id: number;
  user_id: number;
  role_id: number;
  is_contact: boolean;
  valid_from: string | null;
  valid_to: string | null;
  notes: string | null;
};

export type Room = {
  id: number;
  site_id: number;
  name: string;
  description: string | null;
  floor: string | null;
  has_floorplan: boolean;
};

export type Rack = {
  id: number;
  room_id: number;
  tenant_id?: number | null;
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
  /** Font Awesome solid-ikonnavn uten «fa-» (f.eks. server); null = heuristikk fra slug. */
  fa_icon: string | null;
};

export type DeviceModelBrief = {
  id: number;
  name: string;
  u_height: number;
  device_type_id: number | null;
  snmp_sys_object_id_prefix?: string | null;
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
  /** Numerisk sysObjectID-prefiks for SNMP-kobling (f.eks. 1.3.6.1.4.1.890). */
  snmp_sys_object_id_prefix: string | null;
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

export type ComponentFieldType = "text" | "number" | "integer" | "boolean" | "choice" | "date";

export type ComponentClass = {
  id: number;
  name: string;
  slug: string;
  description: string | null;
  icon: string | null;
  active: boolean;
};

export type ComponentStandardCatalogSeedResponse = {
  classes_created: number;
  fields_created: number;
  parents_created: number;
  class_slugs: string[];
};

export type ComponentExternalMappingField = {
  source_path: string;
  target_field_key: string;
  transform: string | null;
  notes: string | null;
};

export type ComponentExternalMappingResource = {
  source_type: string;
  target_class_slug: string;
  relation: string;
  notes: string | null;
  fields: ComponentExternalMappingField[];
};

export type ComponentExternalMappingProfile = {
  source: string;
  display_name: string;
  description: string;
  resources: ComponentExternalMappingResource[];
};

export type ComponentExternalMappingPreview = {
  source: string;
  source_type: string;
  target_class_slug: string;
  relation: string;
  mapped_values: Record<string, unknown>;
  specs_json: Record<string, unknown>;
  component_defaults: Record<string, unknown>;
  extra_values: Record<string, unknown>;
  missing_paths: string[];
  notes: string[];
};

export type ComponentClassField = {
  id: number;
  class_id: number;
  key: string;
  label: string;
  data_type: ComponentFieldType;
  unit: string | null;
  required: boolean;
  sort_order: number;
  min_number: number | null;
  max_number: number | null;
  choices_json: string[] | null;
  default_value: unknown;
  description: string | null;
  active: boolean;
};

export type ComponentClassEffectiveField = ComponentClassField & {
  inherited_from_class_id: number | null;
  inherited_from_class_name: string | null;
  inherited: boolean;
};

export type ComponentClassParent = {
  id: number;
  child_class_id: number;
  parent_class_id: number;
  sort_order: number;
};

export type ComponentFieldImpact = {
  breaking: boolean;
  affected_components: number;
  affected_model_links: number;
  affected_instance_links: number;
  messages: string[];
};

export type Component = {
  id: number;
  class_id: number;
  manufacturer_id: number | null;
  name: string;
  part_number: string | null;
  description: string | null;
  specs_json: Record<string, unknown>;
  active: boolean;
};

export type ComponentIdentity = {
  id: number;
  component_id: number;
  identity_type: string;
  namespace: string;
  value: string;
  normalized_value: string;
  source: string | null;
  confidence: number;
  raw_json: Record<string, unknown>;
  notes: string | null;
  created_at: string;
};

export type ManufacturerIdentity = Omit<ComponentIdentity, "component_id"> & {
  manufacturer_id: number;
};

export type DeviceModelIdentity = Omit<ComponentIdentity, "component_id"> & {
  device_model_id: number;
};

export type ComponentChildTemplate = {
  id: number;
  parent_component_id: number;
  child_class_id: number;
  child_component_id: number | null;
  quantity: number;
  name_pattern: string | null;
  slot_label: string | null;
  overrides_json: Record<string, unknown>;
  materialize_as: string | null;
  sort_order: number;
};

export type DeviceModelComponent = {
  id: number;
  device_model_id: number;
  component_id: number;
  quantity: number;
  slot_label: string | null;
  notes: string | null;
  overrides_json: Record<string, unknown>;
  sort_order: number;
};

export type DeviceInstanceComponent = {
  id: number;
  device_id: number;
  component_id: number;
  quantity: number;
  slot_label: string | null;
  serial_number: string | null;
  asset_tag: string | null;
  installed_at: string | null;
  notes: string | null;
  overrides_json: Record<string, unknown>;
  sort_order: number;
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

/** IP på enheten uten kobling til et bestemt grensesnitt. */
export type DeviceIpAssignment = {
  id: number;
  device_id: number;
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
