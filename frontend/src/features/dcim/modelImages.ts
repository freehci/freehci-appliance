import { apiUrl } from "@/lib/api";
import type { DeviceModel } from "./types";

const P = "/api/v1/dcim";

export function deviceModelImageFrontUrl(id: number, version?: string): string {
  const q = version != null && version !== "" ? `?v=${encodeURIComponent(version)}` : "";
  return apiUrl(`${P}/device-models/${id}/image-front${q}`);
}

export function deviceModelImageBackUrl(id: number, version?: string): string {
  const q = version != null && version !== "" ? `?v=${encodeURIComponent(version)}` : "";
  return apiUrl(`${P}/device-models/${id}/image-back${q}`);
}

/** Fil fra API har forrang; ellers ekstern URL. */
export function deviceModelFrontSrc(m: DeviceModel, version?: string): string | null {
  if (m.has_image_front_file) return deviceModelImageFrontUrl(m.id, version);
  if (m.image_front_url) return m.image_front_url;
  return null;
}

export function deviceModelBackSrc(m: DeviceModel, version?: string): string | null {
  if (m.has_image_back_file) return deviceModelImageBackUrl(m.id, version);
  if (m.image_back_url) return m.image_back_url;
  return null;
}
