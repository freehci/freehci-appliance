import { useEffect, useId, useMemo, useState, type ReactNode } from "react";
import dcimStyles from "@/features/dcim/dcim.module.css";
import { useI18n } from "@/i18n/I18nProvider";
import {
  allProblemLines,
  collectDiagnosticsForMibFile,
  type MibSourceDiagnostic,
} from "./mibCompileDiagnostics";
import type { SnmpMibDetail } from "./snmpApi";
import styles from "./mibViewer.module.css";

function triggerDownload(filename: string, text: string) {
  const blob = new Blob([text], { type: "text/plain;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.rel = "noopener";
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

/** Ord og operatorer som ofte brukes i SMI-v1/v2 MIB-er */
const TOKEN_RE =
  /("(?:[^"\\]|\\.)*")|(\b(?:DEFINITIONS|BEGIN|END|IMPORTS|FROM|SEQUENCE|OF|CHOICE|OPTIONAL|INTEGER|OBJECT-TYPE|MODULE-IDENTITY|OBJECT-IDENTITY|OBJECT\s+IDENTITY|OBJECT\s+GROUP|NOTIFICATION-TYPE|TEXTUAL-CONVENTION|MODULE-COMPLIANCE|AGENT-CAPABILITIES|MAX-ACCESS|MIN-ACCESS|SYNTAX|STATUS|ACCESS|DESCRIPTION|REVISION|ORGANIZATION|CONTACT-INFO|LAST-UPDATED|AUGMENTS|INDEX|DEFVAL|UNITS|REFERENCE|NOTIFICATION-GROUP|::=)\b)|(\{[^}\n]{0,400}\})/gi;

function highlightCodePart(s: string, baseKey: string): ReactNode[] {
  const out: ReactNode[] = [];
  let last = 0;
  let ki = 0;
  TOKEN_RE.lastIndex = 0;
  let m: RegExpExecArray | null;
  while ((m = TOKEN_RE.exec(s)) !== null) {
    if (m.index > last) {
      out.push(<span key={`${baseKey}-p-${ki++}`}>{s.slice(last, m.index)}</span>);
    }
    const token = m[0];
    let cls = "";
    if (m[1]) cls = styles.string;
    else if (m[2]) cls = styles.kw;
    else if (m[3]) cls = styles.oid;
    out.push(
      <span key={`${baseKey}-p-${ki++}`} className={cls || undefined}>
        {token}
      </span>,
    );
    last = m.index + token.length;
  }
  if (last < s.length) {
    out.push(<span key={`${baseKey}-p-${ki++}`}>{s.slice(last)}</span>);
  }
  return out.length ? out : [s];
}

function highlightLine(line: string, lineIndex: number): ReactNode {
  const c = line.indexOf("--");
  if (c >= 0) {
    const head = line.slice(0, c);
    const tail = line.slice(c);
    return (
      <>
        {highlightCodePart(head, `L${lineIndex}a`)}
        <span className={styles.comment}>{tail}</span>
      </>
    );
  }
  return <>{highlightCodePart(line, `L${lineIndex}`)}</>;
}

function makeLineDomId(filename: string, line: number): string {
  const safe = filename.replace(/[^a-zA-Z0-9_.-]+/g, "_");
  return `mib-view-line-${safe}-${line}`;
}

function MibHighlighted({
  text,
  problemLines,
  focusedLine,
  filename,
}: {
  text: string;
  problemLines: Set<number>;
  focusedLine: number | null;
  filename: string;
}) {
  const lines = useMemo(() => text.split(/\n/), [text]);
  return (
    <pre className={styles.pre}>
      {lines.map((line, i) => {
        const n = i + 1;
        const isProblem = problemLines.has(n);
        const isFocused = focusedLine === n;
        const lineCls = [styles.line, isProblem ? styles.lineProblem : "", isFocused ? styles.lineFocused : ""]
          .filter(Boolean)
          .join(" ");
        return (
          <div key={i} id={makeLineDomId(filename, n)} className={lineCls}>
            <span className={styles.ln}>{n}</span>
            <span className={styles.code}>{highlightLine(line, i)}</span>
          </div>
        );
      })}
    </pre>
  );
}

export function MibSourceModal({
  filename,
  content,
  loading,
  error,
  onClose,
  allMibs,
}: {
  filename: string;
  content: string | null;
  loading: boolean;
  error: string | null;
  onClose: () => void;
  allMibs: SnmpMibDetail[];
}) {
  const { t } = useI18n();
  const titleId = useId();
  const [focusedLine, setFocusedLine] = useState<number | null>(null);

  const diagnostics: MibSourceDiagnostic[] = useMemo(
    () => collectDiagnosticsForMibFile(filename, allMibs, content),
    [filename, allMibs, content],
  );

  const problemLines = useMemo(() => allProblemLines(diagnostics), [diagnostics]);

  useEffect(() => {
    setFocusedLine(null);
  }, [filename]);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  useEffect(() => {
    if (focusedLine == null) return;
    const id = makeLineDomId(filename, focusedLine);
    requestAnimationFrame(() => {
      document.getElementById(id)?.scrollIntoView({ block: "center", behavior: "smooth" });
    });
  }, [focusedLine, filename]);

  return (
    <div
      className={styles.backdrop}
      role="presentation"
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div
        className={styles.dialog}
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
        onClick={(e) => e.stopPropagation()}
      >
        <div className={styles.header}>
          <h2 id={titleId} className={styles.title}>
            {filename}
          </h2>
          <div className={styles.headerActions}>
            {content != null && !loading && !error ? (
              <button
                type="button"
                className={dcimStyles.btnMuted}
                title={t("snmp.mibDownloadHint")}
                aria-label={t("snmp.mibDownloadAria")}
                onClick={() => triggerDownload(filename, content)}
              >
                <i className="fas fa-download" aria-hidden />
              </button>
            ) : null}
            <button
              type="button"
              className={dcimStyles.btnMuted}
              onClick={onClose}
              aria-label={t("snmp.mibSourceCloseAria")}
            >
              ×
            </button>
          </div>
        </div>
        <div className={styles.bodyWrap}>
          <div className={styles.codeScroll}>
            {loading ? <p style={{ padding: "var(--space-3)" }}>…</p> : null}
            {error ? (
              <p className={dcimStyles.err} style={{ padding: "var(--space-3)" }}>
                {error}
              </p>
            ) : null}
            {!loading && !error && content != null ? (
              <MibHighlighted
                text={content}
                problemLines={problemLines}
                focusedLine={focusedLine}
                filename={filename}
              />
            ) : null}
          </div>
          {diagnostics.length > 0 ? (
            <div
              className={styles.problemsPanel}
              role="region"
              aria-label={t("snmp.mibViewerProblems")}
            >
              <div className={styles.problemsPanelTitle}>{t("snmp.mibViewerProblems")}</div>
              <ul className={styles.problemsList}>
                {diagnostics.map((d, i) => (
                  <li key={i} className={styles.problemItem}>
                    <button
                      type="button"
                      className={styles.problemJumpBtn}
                      disabled={d.line == null}
                      onClick={() => d.line != null && setFocusedLine(d.line)}
                      title={d.line != null ? t("snmp.mibViewerJumpToLine", { line: String(d.line) }) : undefined}
                    >
                      {d.line != null
                        ? t("snmp.mibViewerProblemLine", { line: String(d.line) })
                        : t("snmp.mibViewerProblemNoLine")}
                      {d.fromFile ? (
                        <span className={styles.problemFrom}> · {d.fromFile}</span>
                      ) : null}
                    </button>
                    <div className={styles.problemText}>{d.message}</div>
                  </li>
                ))}
              </ul>
            </div>
          ) : null}
        </div>
      </div>
    </div>
  );
}
