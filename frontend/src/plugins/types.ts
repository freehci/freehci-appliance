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
  api_route_prefix: string | null;
};

export type PluginListResponse = {
  plugins: PluginManifest[];
};
