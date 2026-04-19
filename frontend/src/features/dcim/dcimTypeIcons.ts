const FA_ICON_NAME = /^[a-z0-9-]{1,50}$/;

/** Heuristikk ut fra slug når ingen eksplisitt ikon er satt (returnerer «fa-…»-suffiks). */
export function deviceTypeFaIconClass(slug: string): string {
  const s = slug.toLowerCase();
  if (s.includes("switch")) return "fa-network-wired";
  if (s.includes("router")) return "fa-diagram-project";
  if (s.includes("firewall")) return "fa-shield-halved";
  if (s.includes("server")) return "fa-server";
  if (s.includes("storage") || s.includes("nas") || s.includes("san")) return "fa-hard-drive";
  if (s.includes("wireless") || s.includes("wifi") || s.includes("ap")) return "fa-wifi";
  if (s.includes("camera")) return "fa-video";
  if (s.includes("printer")) return "fa-print";
  if (s.includes("pdu")) return "fa-plug";
  return "fa-microchip";
}

/**
 * Font Awesome solid-klassesuffiks (f.eks. fa-server) for visning.
 * Bruker lagret `fa_icon` (navn uten fa-) når gyldig; ellers slug-heuristikk.
 */
export function deviceTypeResolvedFaIconClass(slug: string, faIcon: string | null | undefined): string {
  const raw = (faIcon ?? "").trim().toLowerCase();
  const name = raw.startsWith("fa-") ? raw.slice(3) : raw;
  if (name !== "" && FA_ICON_NAME.test(name)) return `fa-${name}`;
  return deviceTypeFaIconClass(slug);
}
