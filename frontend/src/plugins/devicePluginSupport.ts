import type { PluginManifest } from "./types";

/** Tom `device_type_slugs` på manifest = gjelder alle typer. */
export function pluginAppliesToDeviceType(
  p: PluginManifest,
  deviceTypeSlug: string | null,
): boolean {
  if (p.device_type_slugs.length === 0) return true;
  if (deviceTypeSlug == null || deviceTypeSlug === "") return false;
  return p.device_type_slugs.includes(deviceTypeSlug);
}

export function pluginsWithCapability(
  plugins: PluginManifest[],
  capabilityId: string,
  deviceTypeSlug: string | null,
): PluginManifest[] {
  return plugins.filter(
    (p) =>
      p.capabilities.some((c) => c.id === capabilityId) &&
      pluginAppliesToDeviceType(p, deviceTypeSlug),
  );
}
