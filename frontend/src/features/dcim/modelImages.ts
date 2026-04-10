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

export function deviceModelImageProductUrl(id: number, version?: string): string {
  const q = version != null && version !== "" ? `?v=${encodeURIComponent(version)}` : "";
  return apiUrl(`${P}/device-models/${id}/image-product${q}`);
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

/** Produktfoto uten front/bak-rolle (vegg, DIN-skinne, panel, …). */
export function deviceModelProductSrc(m: DeviceModel, version?: string): string | null {
  if (m.has_image_product_file) return deviceModelImageProductUrl(m.id, version);
  if (m.image_product_url) return m.image_product_url;
  return null;
}

/** Rack «forside» mot betrakter: eksplisitt front, ellers produkt, ellers bak. */
export function deviceModelRackFaceSrc(m: DeviceModel, version?: string): string | null {
  return deviceModelFrontSrc(m, version) ?? deviceModelProductSrc(m, version) ?? deviceModelBackSrc(m, version);
}

/** Modelltabell / katalog: produktfoto først, deretter klassisk front/bak. */
export function deviceModelListThumbSrc(m: DeviceModel, version?: string): string | null {
  return deviceModelProductSrc(m, version) ?? deviceModelFrontSrc(m, version) ?? deviceModelBackSrc(m, version);
}
