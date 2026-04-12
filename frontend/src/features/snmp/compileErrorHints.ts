import type { MessageKey } from "@/i18n/messages/en";

/**
 * Matcher typiske pysmi-/backend-feilstrenger og returnerer i18n-nøkler til forklaringer.
 * Rekkefølge: mest spesifikke først; ingen duplikater.
 */
export function mibCompileErrorHintKeys(raw: string): MessageKey[] {
  const out: MessageKey[] = [];
  const seen = new Set<MessageKey>();
  const add = (k: MessageKey) => {
    if (seen.has(k)) return;
    seen.add(k);
    out.push(k);
  };

  const r = raw;

  if (/unknown\s+parents\s+for\s+symbols/i.test(r) && /integer64/i.test(r)) {
    add("snmp.compileHint.integer64Imports");
  }

  if (/bad\s+grammar/i.test(r) && /token\s+type\s*,/i.test(r)) {
    add("snmp.compileHint.badGrammarComma");
  }

  if (/bad\s+grammar/i.test(r) && /object[-_\s]?type/i.test(r)) {
    add("snmp.compileHint.badGrammarObjectType");
  }

  if (/no\s+symbol\s+.+\s+in\s+module/i.test(r)) {
    add("snmp.compileHint.noSymbolInModule");
  }

  if (
    /mangler\s+asn/i.test(r) ||
    /asn\.1-kilde/i.test(r) ||
    /not\s+found\s+anywhere/i.test(r) ||
    /MIB\s+source.*not\s+found/i.test(r) ||
    /no\s+suitable\s+compiled/i.test(r)
  ) {
    add("snmp.compileHint.missingDependency");
  }

  if (/unprocessed|Could not map the requested module|Kunne ikke koble|Kompilering stoppet/i.test(r)) {
    add("snmp.compileHint.compilerState");
  }

  return out;
}

/** Hint når panelet er utvidet: spesifikke treff, ellers én generell veiledning. */
export function mibCompileErrorHintsForExpanded(raw: string): MessageKey[] {
  const specific = mibCompileErrorHintKeys(raw);
  return specific.length > 0 ? specific : ["snmp.compileHint.generic"];
}

const PREVIEW_MAX = 140;

export function mibCompileErrorNeedsToggle(raw: string): boolean {
  const line = raw.split("\n")[0]?.trim() ?? "";
  if (line.length > PREVIEW_MAX) return true;
  const nonEmptyLines = raw.trim().split(/\n/).filter((x) => x.trim());
  if (nonEmptyLines.length > 1) return true;
  if (mibCompileErrorHintKeys(raw).length > 0) return true;
  return false;
}

export function mibCompileErrorPreview(raw: string): string {
  const first = raw.split("\n")[0]?.trim() ?? raw.trim();
  if (first.length <= PREVIEW_MAX) return first;
  return `${first.slice(0, PREVIEW_MAX - 1)}…`;
}
