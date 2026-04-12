import type { SnmpMibDetail } from "./snmpApi";

export function escapeRegExp(s: string): string {
  return s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

/** Unngå treff midt i identifikatorer (f.eks. «FOO-MIB» inni «MYFOO-MIB»). */
export function mibModuleTokenBoundaryPattern(display: string): string {
  return `(?<![A-Za-z0-9-])${escapeRegExp(display)}(?![A-Za-z0-9-])`;
}

export function normalizeMibKey(s: string): string {
  return s.trim().toUpperCase();
}

export function buildMibModuleResolveMap(rows: SnmpMibDetail[]): Map<string, string> {
  const m = new Map<string, string>();
  for (const r of rows) {
    const stem = r.name.replace(/\.[^.]+$/i, "");
    const add = (id: string | null | undefined) => {
      if (!id?.trim()) return;
      const k = normalizeMibKey(id);
      if (!m.has(k)) m.set(k, r.name);
    };
    add(stem);
    add(r.module_name ?? null);
    add(r.compiled_module_name ?? null);
  }
  return m;
}

export function sortedMibDisplaysForLinkify(rows: SnmpMibDetail[]): string[] {
  const seen = new Set<string>();
  const out: string[] = [];
  for (const r of rows) {
    for (const id of [r.module_name, r.name.replace(/\.[^.]+$/i, ""), r.compiled_module_name]) {
      if (!id?.trim()) continue;
      const u = normalizeMibKey(id);
      if (seen.has(u)) continue;
      seen.add(u);
      out.push(id.trim());
    }
  }
  out.sort((a, b) => b.length - a.length);
  return out;
}

export function extractModuleRefsFromCompileMessage(msg: string): string[] {
  const out = new Set<string>();
  const patterns = [
    /\bat\s+MIB\s+([A-Za-z][A-Za-z0-9-]*)/gi,
    /\bin\s+module\s+"([^"]+)"/gi,
    /\bmodule\s+"([^"]+)"/gi,
  ];
  for (const re of patterns) {
    const r = new RegExp(re.source, re.flags);
    let m: RegExpExecArray | null;
    while ((m = r.exec(msg)) !== null) {
      out.add(m[1].trim());
    }
  }
  return [...out];
}

export function compileMessageReferencesFilename(
  msg: string,
  targetFilename: string,
  upperToFile: Map<string, string>,
): boolean {
  for (const tok of extractModuleRefsFromCompileMessage(msg)) {
    if (upperToFile.get(normalizeMibKey(tok)) === targetFilename) return true;
  }
  return false;
}

export type MibSourceDiagnostic = {
  line: number | null;
  message: string;
  fromFile?: string;
};

export function guessErrorLineFromMessage(content: string, msg: string): number | null {
  const sym = msg.match(/no symbol "([^"]+)"/i);
  if (sym) {
    const needle = sym[1];
    const lines = content.split(/\n/);
    const re = new RegExp(`\\b${escapeRegExp(needle)}\\b`);
    for (let i = 0; i < lines.length; i++) {
      if (re.test(lines[i])) {
        return i + 1;
      }
    }
  }
  return null;
}

export function guessImportLineForModule(content: string, moduleName: string): number | null {
  const lines = content.split(/\n/);
  const re = new RegExp(`FROM\\s+${escapeRegExp(moduleName)}\\b`, "i");
  for (let i = 0; i < lines.length; i++) {
    if (re.test(lines[i])) {
      return i + 1;
    }
  }
  return null;
}

export function guessRelatedLineInOpenFile(content: string, foreignError: string): number | null {
  const modM = foreignError.match(/in\s+module\s+"([^"]+)"/i);
  const mod = modM?.[1];
  if (mod) {
    const ln = guessImportLineForModule(content, mod);
    if (ln != null) return ln;
  }
  return guessErrorLineFromMessage(content, foreignError);
}

export function collectDiagnosticsForMibFile(
  filename: string,
  rows: SnmpMibDetail[],
  content: string | null,
): MibSourceDiagnostic[] {
  const resolve = buildMibModuleResolveMap(rows);
  const out: MibSourceDiagnostic[] = [];
  const seen = new Set<string>();

  const push = (d: MibSourceDiagnostic) => {
    const k = `${d.line ?? "x"}|${d.message}|${d.fromFile ?? ""}`;
    if (seen.has(k)) return;
    seen.add(k);
    out.push(d);
  };

  const row = rows.find((r) => r.name === filename);
  if (row?.compile_message && row.compile_status === "error") {
    push({
      line: content ? guessErrorLineFromMessage(content, row.compile_message) : null,
      message: row.compile_message,
    });
  }

  if (!content) {
    return out;
  }

  for (const r of rows) {
    if (r.name === filename || !r.compile_message || r.compile_status !== "error") continue;
    if (!compileMessageReferencesFilename(r.compile_message, filename, resolve)) continue;
    const ln = guessRelatedLineInOpenFile(content, r.compile_message);
    push({
      line: ln,
      message: r.compile_message,
      fromFile: r.name,
    });
  }

  return out;
}

export function mibTableRowDomId(filename: string): string {
  return `mib-row-${filename.replace(/[^a-zA-Z0-9_.-]+/g, "_")}`;
}

export function allProblemLines(diags: MibSourceDiagnostic[]): Set<number> {
  const s = new Set<number>();
  for (const d of diags) {
    if (d.line != null && d.line > 0) s.add(d.line);
  }
  return s;
}
