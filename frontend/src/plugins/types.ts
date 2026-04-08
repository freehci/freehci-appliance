export type PluginCapability = {
  id: string;
  description: string;
};

export type PluginManifest = {
  id: string;
  name: string;
  version: string;
  description: string;
  capabilities: PluginCapability[];
  frontend_module_url: string | null;
  frontend_route_prefix: string | null;
  /** device_type.slug fra DCIM som pluginen retter seg mot (tom = ikke filtrert). */
  device_type_slugs: string[];
  api_route_prefix: string | null;
};

export type PluginListResponse = {
  plugins: PluginManifest[];
};
