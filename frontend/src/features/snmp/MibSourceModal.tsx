import { useEffect, useId, useMemo, useState } from "react";
import { SourceCodeEditor } from "@/components/source-editor";
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

function MibSourceModal({
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
              <SourceCodeEditor
                value={content}
                filename={filename}
                path={`mib-library://${encodeURIComponent(filename)}`}
                readOnly
                problemLineNumbers={problemLines}
                focusedLine={focusedLine}
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

export { MibSourceModal };
export default MibSourceModal;
