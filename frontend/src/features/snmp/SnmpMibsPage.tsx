import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useCallback, useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { useI18n } from "@/i18n/I18nProvider";
import type { MessageKey } from "@/i18n/messages/en";
import { ApiError } from "@/lib/api";
import dcimStyles from "@/features/dcim/dcim.module.css";
import { MibCompileErrorBlock } from "./MibCompileErrorBlock";
import { mibTableRowDomId } from "./mibCompileDiagnostics";
import { MibSourceModal } from "./MibSourceModal";
import mibViewStyles from "./mibViewer.module.css";
import mibsTableStyles from "./snmpMibs.module.css";
import * as snmpApi from "./snmpApi";

function labelForStoredCompileStatus(status: string, t: (k: MessageKey) => string) {
  switch (status) {
    case "pending":
      return t("snmp.compileStatus.pending");
    case "ok":
      return t("snmp.compileStatus.ok");
    case "error":
      return t("snmp.compileStatus.error");
    default:
      return status;
  }
}

export function SnmpMibsPage() {
  const { t } = useI18n();
  const qc = useQueryClient();
  const [err, setErr] = useState<string | null>(null);
  const [files, setFiles] = useState<File[]>([]);
  const [viewSourceName, setViewSourceName] = useState<string | null>(null);
  const [flashMibRow, setFlashMibRow] = useState<string | null>(null);
  const [bgCompileAll, setBgCompileAll] = useState(false);
  const flashTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const mibsQ = useQuery({
    queryKey: ["snmp", "mibs", "detailed"],
    queryFn: snmpApi.listSnmpMibsDetailed,
    refetchInterval: bgCompileAll ? 4000 : false,
  });

  const mibSourceQ = useQuery({
    queryKey: ["snmp", "mibSource", viewSourceName],
    queryFn: () => snmpApi.getSnmpMibSource(viewSourceName!),
    enabled: viewSourceName != null,
  });

  const invalidate = () => {
    void qc.invalidateQueries({ queryKey: ["snmp", "mibs"] });
    void qc.invalidateQueries({ queryKey: ["snmp", "enterprises"] });
  };

  const uploadBatch = useMutation({
    mutationFn: (fs: File[]) => snmpApi.uploadSnmpMibsBatch(fs),
    onSuccess: () => {
      setErr(null);
      setFiles([]);
      invalidate();
      void qc.invalidateQueries({ queryKey: ["snmp", "mibs", "detailed"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const syncIana = useMutation({
    mutationFn: () => snmpApi.syncSnmpIana(),
    onSuccess: () => {
      setErr(null);
      invalidate();
      void qc.invalidateQueries({ queryKey: ["snmp", "mibs", "detailed"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const compileAll = useMutation({
    mutationFn: () => snmpApi.compileAllSnmpMibs(),
    onSuccess: () => {
      setErr(null);
      setBgCompileAll(true);
      void qc.invalidateQueries({ queryKey: ["snmp", "mibs", "detailed"] });
      invalidate();
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const compileOne = useMutation({
    mutationFn: (name: string) => snmpApi.compileSnmpMib(name),
    onSuccess: () => {
      setErr(null);
      void qc.invalidateQueries({ queryKey: ["snmp", "mibs", "detailed"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const delMib = useMutation({
    mutationFn: (name: string) => snmpApi.deleteSnmpMib(name),
    onSuccess: () => {
      setErr(null);
      invalidate();
      void qc.invalidateQueries({ queryKey: ["snmp", "mibs", "detailed"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const compilingName = compileOne.isPending ? compileOne.variables : undefined;
  const deletingName = delMib.isPending ? delMib.variables : undefined;

  const handleMibRefNavigate = useCallback((filename: string) => {
    if (flashTimerRef.current) window.clearTimeout(flashTimerRef.current);
    setFlashMibRow(filename);
    flashTimerRef.current = window.setTimeout(() => setFlashMibRow(null), 4500);
    requestAnimationFrame(() => {
      document.getElementById(mibTableRowDomId(filename))?.scrollIntoView({
        behavior: "smooth",
        block: "center",
      });
    });
  }, []);

  useEffect(
    () => () => {
      if (flashTimerRef.current) window.clearTimeout(flashTimerRef.current);
    },
    [],
  );

  useEffect(() => {
    if (!bgCompileAll) return;
    const stop = window.setTimeout(() => setBgCompileAll(false), 30 * 60 * 1000);
    return () => window.clearTimeout(stop);
  }, [bgCompileAll]);

  return (
    <>
      {viewSourceName ? (
        <MibSourceModal
          filename={viewSourceName}
          content={mibSourceQ.data ?? null}
          loading={mibSourceQ.isLoading}
          error={
            mibSourceQ.isError
              ? mibSourceQ.error instanceof ApiError
                ? mibSourceQ.error.message
                : String(mibSourceQ.error)
              : null
          }
          onClose={() => setViewSourceName(null)}
          allMibs={mibsQ.data ?? []}
        />
      ) : null}
      {err ? <p className={dcimStyles.err}>{err}</p> : null}
      {bgCompileAll ? <p className={dcimStyles.muted}>{t("snmp.compileAllStarted")}</p> : null}
      <p className={dcimStyles.muted} style={{ marginTop: 0 }}>
        {t("snmp.mibsPageIntro")}{" "}
        <Link to="/snmp/enterprises">{t("snmp.enterprisesTabLink")}</Link>
      </p>

      <section className={dcimStyles.mfrDetailSection}>
        <h3 className={dcimStyles.mfrDetailSectionTitle}>{t("snmp.mibsUploadTitle")}</h3>
        <div className={dcimStyles.formRow} style={{ alignItems: "flex-end" }}>
          <label>
            {t("snmp.mibFilesMulti")}
            <input
              type="file"
              multiple
              accept=".mib,.my,.txt,text/plain"
              onChange={(e) => setFiles(e.target.files ? Array.from(e.target.files) : [])}
            />
          </label>
          <button
            type="button"
            className={dcimStyles.btn}
            disabled={files.length === 0 || uploadBatch.isPending}
            onClick={() => uploadBatch.mutate(files)}
          >
            {uploadBatch.isPending ? "…" : t("snmp.mibUploadBatch")}
          </button>
          <button
            type="button"
            className={dcimStyles.btnMuted}
            disabled={syncIana.isPending}
            onClick={() => syncIana.mutate()}
            title={t("snmp.ianaSyncHint")}
          >
            {syncIana.isPending ? "…" : t("snmp.ianaSync")}
          </button>
          <button
            type="button"
            className={dcimStyles.btnMuted}
            disabled={
              compileAll.isPending || bgCompileAll || (mibsQ.data?.length ?? 0) === 0
            }
            onClick={() => {
              if (!window.confirm(t("snmp.compileAllConfirm"))) return;
              compileAll.mutate();
            }}
            title={t("snmp.compileAllHint")}
          >
            {compileAll.isPending
              ? "…"
              : bgCompileAll
                ? t("snmp.compileAllRunning")
                : t("snmp.compileAll")}
          </button>
        </div>
      </section>

      <section className={dcimStyles.mfrDetailSection}>
        <h3 className={dcimStyles.mfrDetailSectionTitle}>{t("snmp.mibsTableTitle")}</h3>
        {mibsQ.isLoading ? <p className={dcimStyles.muted}>{t("dcim.common.loading")}</p> : null}
        {mibsQ.data && mibsQ.data.length > 0 ? (
          <div style={{ overflowX: "auto" }}>
            <table className={dcimStyles.table}>
              <thead>
                <tr>
                  <th>{t("snmp.mibColName")}</th>
                  <th>{t("snmp.mibColModule")}</th>
                  <th>{t("snmp.mibColEnterprise")}</th>
                  <th>{t("snmp.mibColIanaOrg")}</th>
                  <th>{t("snmp.mibColCompile")}</th>
                  <th>{t("snmp.mibColMfr")}</th>
                  <th>{t("ipam.ipv4.actionsCol")}</th>
                </tr>
              </thead>
              <tbody>
                {mibsQ.data.map((m) => {
                  const compilingThis = compilingName === m.name;
                  const statusLabel = compilingThis
                    ? t("snmp.compileStatus.compiling")
                    : labelForStoredCompileStatus(m.compile_status, t);
                  const statusClass = compilingThis
                    ? `${mibsTableStyles.compileStatusCompiling} ${mibsTableStyles.compileStatusCompilingPulse}`
                    : m.compile_status === "error"
                      ? dcimStyles.err
                      : m.compile_status === "ok"
                        ? mibsTableStyles.compileStatusOk
                        : mibsTableStyles.compileStatusPending;

                  return (
                    <tr
                      key={m.name}
                      id={mibTableRowDomId(m.name)}
                      className={flashMibRow === m.name ? mibsTableStyles.mibRowFlash : undefined}
                    >
                      <td>
                        <button
                          type="button"
                          className={mibViewStyles.fileNameBtn}
                          title={t("snmp.mibFilenameOpenHint")}
                          onClick={() => setViewSourceName(m.name)}
                        >
                          <code>{m.name}</code>
                        </button>
                        {m.parent_mib_missing ? (
                          <div className={dcimStyles.err} style={{ fontSize: "var(--text-xs)", marginTop: 4 }}>
                            {t("snmp.mibParentMissingShort", { module: m.extends_mib_module ?? "?" })}
                          </div>
                        ) : null}
                      </td>
                      <td className={dcimStyles.muted}>{m.module_name ?? "—"}</td>
                      <td>
                        {m.enterprise_number ?? "—"}
                        {m.enterprise_number == null && m.effective_enterprise_number != null ? (
                          <span className={dcimStyles.muted}>
                            {" "}
                            ({t("snmp.effectivePenShort", { pen: String(m.effective_enterprise_number) })})
                          </span>
                        ) : null}
                      </td>
                      <td className={dcimStyles.muted}>{m.iana_organization ?? "—"}</td>
                      <td>
                        <div>
                          <span className={statusClass} title={statusLabel}>
                            {statusLabel}
                          </span>
                        </div>
                        {m.compile_message ? (
                          <div className={dcimStyles.err} style={{ marginTop: 4 }}>
                            <MibCompileErrorBlock
                              raw={m.compile_message}
                              rows={mibsQ.data ?? []}
                              t={t}
                              onMibRefNavigate={handleMibRefNavigate}
                            />
                          </div>
                        ) : null}
                      </td>
                      <td>{m.linked_manufacturer?.name ?? "—"}</td>
                      <td>
                        <div className={mibsTableStyles.mibTableActions}>
                          <button
                            type="button"
                            className={mibsTableStyles.mibIconBtn}
                            title={t("snmp.compileOne")}
                            aria-label={t("snmp.mibCompileAria")}
                            disabled={
                              compileOne.isPending || (deletingName != null && deletingName === m.name)
                            }
                            onClick={() => compileOne.mutate(m.name)}
                          >
                            <i className="fas fa-gears" aria-hidden />
                          </button>
                          <button
                            type="button"
                            className={`${mibsTableStyles.mibIconBtn} ${mibsTableStyles.mibIconBtnDanger}`.trim()}
                            title={t("dcim.common.delete")}
                            aria-label={t("snmp.mibDeleteAria")}
                            disabled={
                              delMib.isPending || (compilingName != null && compilingName === m.name)
                            }
                            onClick={() => {
                              if (!window.confirm(t("snmp.mibDeleteConfirm"))) return;
                              delMib.mutate(m.name);
                            }}
                          >
                            <i className="fas fa-trash-can" aria-hidden />
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        ) : mibsQ.data && mibsQ.data.length === 0 && !mibsQ.isLoading ? (
          <p className={dcimStyles.muted}>{t("snmp.mibsEmpty")}</p>
        ) : null}
      </section>

      <p className={dcimStyles.muted}>{t("snmp.mibsVendorNote")}</p>
    </>
  );
}
