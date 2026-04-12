import type { MessageKey } from "@/i18n/messages/en";

/**
 * Kompileringsfeil fra backend (pysmi) — stabile engelske strenger som mappes til i18n.
 * Eldre norske varianter i DB treffes også.
 */
const MODULE_MAP_FAILED_EN =
  /^Could not map the requested module to the pysmi compiler result \((\d+) modules: (.+)\)\.$/;
const MODULE_MAP_FAILED_NB =
  /^Kunne ikke mappe forespurt modul til pysmi-resultat \((\d+) modul\(er\): (.+)\)$/;

type TFn = (key: MessageKey, vars?: Record<string, string>) => string;

export function parseModuleMapFailed(raw: string): { count: string; modules: string } | null {
  let m = raw.match(MODULE_MAP_FAILED_EN);
  if (!m) {
    m = raw.match(MODULE_MAP_FAILED_NB);
  }
  if (!m) {
    return null;
  }
  return { count: m[1], modules: m[2] };
}

export function formatSnmpCompileMessageForUi(raw: string | null, t: TFn): string | null {
  if (raw == null || raw === "") {
    return null;
  }
  const p = parseModuleMapFailed(raw);
  if (p) {
    return t("snmp.compileErr.moduleMapFailedBefore", { count: p.count }) + p.modules + t("snmp.compileErr.moduleMapFailedAfter");
  }
  return raw;
}
