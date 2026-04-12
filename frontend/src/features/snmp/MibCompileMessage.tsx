import { Fragment, type ReactNode } from "react";
import type { MessageKey } from "@/i18n/messages/en";
import { parseModuleMapFailed } from "./compileMessages";
import {
  buildMibModuleResolveMap,
  mibModuleTokenBoundaryPattern,
  normalizeMibKey,
  sortedMibDisplaysForLinkify,
} from "./mibCompileDiagnostics";
import mibViewStyles from "./mibViewer.module.css";
import type { SnmpMibDetail } from "./snmpApi";

type TFn = (key: MessageKey, vars?: Record<string, string>) => string;

function linkifyRawSegments(
  raw: string,
  displays: string[],
  resolve: Map<string, string>,
  onMibClick: (filename: string) => void,
  errorTitle: string,
): ReactNode[] {
  if (!displays.length) {
    return [<span key="t0">{raw}</span>];
  }
  const alt = displays.map((d) => mibModuleTokenBoundaryPattern(d)).join("|");
  const r = new RegExp(alt, "gi");
  const nodes: ReactNode[] = [];
  let last = 0;
  let m: RegExpExecArray | null;
  let k = 0;
  while ((m = r.exec(raw)) !== null) {
    if (m.index > last) {
      nodes.push(<span key={`t${k++}`}>{raw.slice(last, m.index)}</span>);
    }
    const matched = m[0];
    const file = resolve.get(normalizeMibKey(matched));
    if (file) {
      nodes.push(
        <button
          key={`l${k++}`}
          type="button"
          className={mibViewStyles.mibRefLink}
          title={errorTitle}
          onClick={() => onMibClick(file)}
        >
          {matched}
        </button>,
      );
    } else {
      nodes.push(<span key={`t${k++}`}>{matched}</span>);
    }
    last = m.index + matched.length;
  }
  if (last < raw.length) {
    nodes.push(<span key={`t${k++}`}>{raw.slice(last)}</span>);
  }
  return nodes.length ? nodes : [<span key="t0">{raw}</span>];
}

function linkifyCommaModuleList(
  modulesCsv: string,
  displays: string[],
  resolve: Map<string, string>,
  onMibClick: (filename: string) => void,
  errorTitle: string,
): ReactNode[] {
  const tokens = modulesCsv.split(/\s*,\s*/).filter(Boolean);
  const nodes: ReactNode[] = [];
  let k = 0;
  tokens.forEach((tok, i) => {
    if (i > 0) {
      nodes.push(<span key={`sep${k++}`}>, </span>);
    }
    nodes.push(
      <Fragment key={`frag${k++}`}>
        {linkifyRawSegments(tok, displays, resolve, onMibClick, errorTitle)}
      </Fragment>,
    );
  });
  return nodes;
}

export function MibCompileMessage({
  raw,
  rows,
  t,
  onMibRefNavigate,
}: {
  raw: string;
  rows: SnmpMibDetail[];
  t: TFn;
  onMibRefNavigate: (filename: string) => void;
}) {
  const resolve = buildMibModuleResolveMap(rows);
  const displays = sortedMibDisplaysForLinkify(rows);
  const title = raw;

  const p = parseModuleMapFailed(raw);
  if (p) {
    return (
      <>
        {t("snmp.compileErr.moduleMapFailedBefore", { count: p.count })}
        {linkifyCommaModuleList(p.modules, displays, resolve, onMibRefNavigate, title)}
        {t("snmp.compileErr.moduleMapFailedAfter")}
      </>
    );
  }

  return <>{linkifyRawSegments(raw, displays, resolve, onMibRefNavigate, title)}</>;
}
