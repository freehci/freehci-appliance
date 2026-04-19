/** Font Awesome-klasse for visuell type-ikon (ingen lagring i DB). */
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
