import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { lazy, Suspense, useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useI18n } from "@/i18n/I18nProvider";
import type { MessageKey } from "@/i18n/messages/en";
import { ApiError } from "@/lib/api";
import { HoverHelpCard } from "@/components/ui/HoverHelpCard";
import dcimStyles from "@/features/dcim/dcim.module.css";
import { MibCompileErrorBlock } from "./MibCompileErrorBlock";
import { mibTableRowDomId } from "./mibCompileDiagnostics";
import mibViewStyles from "./mibViewer.module.css";
import mibsTableStyles from "./snmpMibs.module.css";
import * as snmpApi from "./snmpApi";

const MibSourceModalLazy = lazy(() => import("./MibSourceModal"));

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
  const navigate = useNavigate();
  const qc = useQueryClient();
  const [err, setErr] = useState<string | null>(null);
  const [mibNormalizeReport, setMibNormalizeReport] = useState<string | null>(null);
  const [files, setFiles] = useState<File[]>([]);
  const [viewSourceName, setViewSourceName] = useState<string | null>(null);
  const [flashMibRow, setFlashMibRow] = useState<string | null>(null);
  const [bgCompileAll, setBgCompileAll] = useState(false);
  const [bgCompilePending, setBgCompilePending] = useState(false);
  const [mibPage, setMibPage] = useState(1);
  const [mibPageSize, setMibPageSize] = useState(25);
  const [mibSort, setMibSort] = useState("name");
  const [mibOrder, setMibOrder] = useState<"asc" | "desc">("asc");
  const [mibSearchInput, setMibSearchInput] = useState("");
  const [mibSearchQ, setMibSearchQ] = useState("");
  const flashTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const bgMibCompile = bgCompileAll || bgCompilePending;

  useEffect(() => {
    const t = window.setTimeout(() => setMibSearchQ(mibSearchInput.trim()), 400);
    return () => window.clearTimeout(t);
  }, [mibSearchInput]);

  useEffect(() => {
    setMibPage(1);
  }, [mibSearchQ]);

  useEffect(() => {
    setMibPage(1);
  }, [mibPageSize]);

  const mibsQ = useQuery({
    queryKey: ["snmp", "mibs", "detailed", mibPage, mibPageSize, mibSort, mibOrder, mibSearchQ],
    queryFn: () =>
      snmpApi.listSnmpMibsDetailed({
        page: mibPage,
        page_size: mibPageSize,
        sort: mibSort,
        order: mibOrder,
        q: mibSearchQ || undefined,
      }),
    staleTime: bgMibCompile ? 0 : 60_000,
    refetchInterval: bgMibCompile ? 4000 : false,
  });

  const pendingMibsQ = useQuery({
    queryKey: ["snmp", "mibs", "detailed", "pending-only"],
    queryFn: () =>
      snmpApi.listSnmpMibsDetailed({
        compile_status: "pending",
        page: 1,
        page_size: 500,
        sort: "name",
        order: "asc",
      }),
    staleTime: bgMibCompile ? 0 : 60_000,
    refetchInterval: bgMibCompile ? 4000 : false,
  });

  const mibRows = mibsQ.data?.items ?? [];
  const mibTotal = mibsQ.data?.total ?? 0;
  const pendingMibs = pendingMibsQ.data?.items ?? [];
  const pendingTotal = pendingMibsQ.data?.total ?? 0;

  const handleMibSort = useCallback((column: string) => {
    setMibPage(1);
    if (mibSort === column) {
      setMibOrder((o) => (o === "asc" ? "desc" : "asc"));
    } else {
      setMibSort(column);
      setMibOrder("asc");
    }
  }, [mibSort]);

  const mibPageCount = useMemo(
    () => Math.max(1, Math.ceil(mibTotal / mibPageSize) || 1),
    [mibTotal, mibPageSize],
  );
  const mibRangeStart = useMemo(
    () => (mibTotal === 0 ? 0 : (mibPage - 1) * mibPageSize + 1),
    [mibTotal, mibPage, mibPageSize],
  );
  const mibRangeEnd = useMemo(
    () => Math.min(mibPage * mibPageSize, mibTotal),
    [mibPage, mibPageSize, mibTotal],
  );

  useEffect(() => {
    if (mibTotal === 0) return;
    const pc = Math.max(1, Math.ceil(mibTotal / mibPageSize));
    if (mibPage > pc) setMibPage(pc);
  }, [mibTotal, mibPageSize, mibPage]);

  const mibSourceQ = useQuery({
    queryKey: ["snmp", "mibSource", viewSourceName],
    queryFn: () => snmpApi.getSnmpMibSource(viewSourceName!),
    enabled: viewSourceName != null,
  });

  const mibSourceErrorText = useMemo(() => {
    if (!mibSourceQ.isError) return null;
    if (mibSourceQ.error instanceof ApiError) {
      if (mibSourceQ.error.status === 404 && viewSourceName != null) {
        return t("snmp.mibSourceNotFound", { name: viewSourceName });
      }
      return mibSourceQ.error.message;
    }
    return String(mibSourceQ.error);
  }, [mibSourceQ.isError, mibSourceQ.error, viewSourceName, t]);

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

  const compilePending = useMutation({
    mutationFn: () => snmpApi.compilePendingSnmpMibs(),
    onSuccess: () => {
      setErr(null);
      setBgCompilePending(true);
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

  const normalizeMibFilenames = useMutation({
    mutationFn: () => snmpApi.normalizeSnmpMibFilenames(),
    onSuccess: (data) => {
      setErr(null);
      setMibNormalizeReport(
        [
          t("snmp.mibNormalizeDone", { count: String(data.moved_count) }),
          data.skipped.length > 0
            ? t("snmp.mibNormalizeSkipped", { count: String(data.skipped.length) })
            : "",
        ]
          .filter(Boolean)
          .join(" "),
      );
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
    if (!bgMibCompile) return;
    const stop = window.setTimeout(() => {
      setBgCompileAll(false);
      setBgCompilePending(false);
    }, 30 * 60 * 1000);
    return () => window.clearTimeout(stop);
  }, [bgMibCompile]);

  return (
    <>
      {viewSourceName ? (
        <Suspense
          fallback={
            <div className={mibViewStyles.backdrop} role="status" aria-live="polite">
              <div
                className={mibViewStyles.dialog}
                style={{
                  padding: "var(--space-4)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  minHeight: "12rem",
                }}
              >
                <p className={dcimStyles.muted} style={{ margin: 0 }}>
                  {t("snmp.mibSourceLoading")}
                </p>
              </div>
            </div>
          }
        >
          <MibSourceModalLazy
            filename={viewSourceName}
            content={mibSourceQ.data ?? null}
            loading={mibSourceQ.isLoading}
            error={mibSourceErrorText}
            onClose={() => setViewSourceName(null)}
            allMibs={mibRows}
          />
        </Suspense>
      ) : null}
      {err ? <p className={dcimStyles.err}>{err}</p> : null}
      {mibNormalizeReport ? <p className={dcimStyles.muted}>{mibNormalizeReport}</p> : null}
      {bgCompileAll ? <p className={dcimStyles.muted}>{t("snmp.compileAllStarted")}</p> : null}
      {bgCompilePending ? <p className={dcimStyles.muted}>{t("snmp.compilePendingStarted")}</p> : null}
      <p
        className={dcimStyles.muted}
        style={{
          marginTop: 0,
          display: "flex",
          flexWrap: "wrap",
          alignItems: "center",
          gap: "0.35rem",
        }}
      >
        {t("snmp.mibsPageIntroShort")}{" "}
        <Link to="/snmp/enterprises">{t("snmp.enterprisesTabLinkShort")}</Link>
        <HoverHelpCard ariaLabel={t("snmp.mibsPageHelpAria")}>
          <p>{t("snmp.mibsPageIntroHelpBody")}</p>
        </HoverHelpCard>
      </p>

      <section className={dcimStyles.mfrDetailSection}>
        <h3 className={dcimStyles.mfrDetailSectionTitle}>{t("snmp.mibsUploadTitle")}</h3>
        <p className={dcimStyles.muted} style={{ marginTop: 0 }}>
          {t("snmp.mibUploadMaxHint")}
        </p>
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
            disabled={normalizeMibFilenames.isPending || mibTotal === 0}
            title={t("snmp.mibNormalizeHint")}
            onClick={() => {
              if (!window.confirm(t("snmp.mibNormalizeConfirm"))) return;
              setMibNormalizeReport(null);
              normalizeMibFilenames.mutate();
            }}
          >
            {normalizeMibFilenames.isPending ? "…" : t("snmp.mibNormalizeButton")}
          </button>
          <button
            type="button"
            className={dcimStyles.btnMuted}
            disabled={
              compileAll.isPending ||
              bgCompileAll ||
              mibTotal === 0
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

      {pendingTotal > 0 ? (
        <section className={dcimStyles.mfrDetailSection}>
          <h3 className={dcimStyles.mfrDetailSectionTitle}>{t("snmp.pendingMibsTitle")}</h3>
          <p className={dcimStyles.muted} style={{ marginTop: 0 }}>
            {t("snmp.pendingMibsIntro", { count: String(pendingTotal) })}
          </p>
          <div className={dcimStyles.formRow} style={{ alignItems: "center", marginBottom: "var(--space-2)" }}>
            <button
              type="button"
              className={dcimStyles.btnMuted}
              disabled={
                compilePending.isPending ||
                bgCompilePending ||
                pendingTotal === 0
              }
              title={t("snmp.compilePendingHint")}
              onClick={() => {
                if (!window.confirm(t("snmp.compilePendingConfirm"))) return;
                compilePending.mutate();
              }}
            >
              {compilePending.isPending
                ? "…"
                : bgCompilePending
                  ? t("snmp.compilePendingRunning")
                  : t("snmp.compilePending")}
            </button>
          </div>
          <div style={{ overflowX: "auto" }}>
            <table className={dcimStyles.table}>
              <thead>
                <tr>
                  <th>{t("snmp.mibColName")}</th>
                  <th>{t("snmp.mibColModule")}</th>
                  <th>{t("snmp.missingImportsCol")}</th>
                </tr>
              </thead>
              <tbody>
                {pendingMibs.map((m) => (
                  <tr key={`p-${m.name}`}>
                    <td>
                      <button
                        type="button"
                        className={mibViewStyles.fileNameBtn}
                        title={t("snmp.browser.openMibTitle")}
                        onClick={() =>
                          navigate(`/snmp/browser?mib=${encodeURIComponent(m.name)}`)
                        }
                      >
                        <code>{m.name}</code>
                      </button>
                    </td>
                    <td className={dcimStyles.muted}>{m.module_name ?? "—"}</td>
                    <td>
                      {(m.missing_import_modules?.length ?? 0) > 0 ? (
                        <span className={dcimStyles.err} style={{ fontSize: "var(--text-xs)" }}>
                          {(m.missing_import_modules ?? []).join(", ")}
                        </span>
                      ) : (
                        <span className={dcimStyles.muted}>{t("snmp.missingImportsNone")}</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      ) : null}

      <section className={dcimStyles.mfrDetailSection}>
        <h3 className={dcimStyles.mfrDetailSectionTitle}>{t("snmp.mibsTableTitle")}</h3>
        <div className={mibsTableStyles.mibToolbar}>
          <label style={{ flex: "1 1 16rem", minWidth: "12rem", maxWidth: "28rem" }}>
            <span className={dcimStyles.muted} style={{ display: "block", marginBottom: "var(--space-1)" }}>
              {t("snmp.mibsSearchLabel")}
            </span>
            <input
              type="search"
              value={mibSearchInput}
              onChange={(e) => setMibSearchInput(e.target.value)}
              placeholder={t("snmp.mibsSearchPlaceholder")}
              autoComplete="off"
              spellCheck={false}
              style={{
                width: "100%",
                padding: "var(--space-2)",
                borderRadius: "var(--radius-sm)",
                border: "1px solid var(--color-border)",
                background: "var(--color-bg)",
                color: "var(--color-text)",
              }}
            />
          </label>
        </div>
        {mibsQ.isLoading ? <p className={dcimStyles.muted}>{t("dcim.common.loading")}</p> : null}
        {mibsQ.data != null && mibTotal > 0 ? (
          <>
            <div style={{ overflowX: "auto" }}>
              <table className={dcimStyles.table}>
                <thead>
                  <tr>
                    <th>
                      <button
                        type="button"
                        className={mibsTableStyles.sortThBtn}
                        onClick={() => handleMibSort("name")}
                      >
                        {t("snmp.mibColName")}
                        {mibSort === "name" ? (mibOrder === "asc" ? " ↑" : " ↓") : ""}
                      </button>
                    </th>
                    <th>
                      <button
                        type="button"
                        className={mibsTableStyles.sortThBtn}
                        onClick={() => handleMibSort("module_name")}
                      >
                        {t("snmp.mibColModule")}
                        {mibSort === "module_name" ? (mibOrder === "asc" ? " ↑" : " ↓") : ""}
                      </button>
                    </th>
                    <th>
                      <button
                        type="button"
                        className={mibsTableStyles.sortThBtn}
                        onClick={() => handleMibSort("enterprise_number")}
                      >
                        {t("snmp.mibColEnterprise")}
                        {mibSort === "enterprise_number" ? (mibOrder === "asc" ? " ↑" : " ↓") : ""}
                      </button>
                    </th>
                    <th>
                      <button
                        type="button"
                        className={mibsTableStyles.sortThBtn}
                        onClick={() => handleMibSort("iana_organization")}
                      >
                        {t("snmp.mibColIanaOrg")}
                        {mibSort === "iana_organization" ? (mibOrder === "asc" ? " ↑" : " ↓") : ""}
                      </button>
                    </th>
                    <th>
                      <button
                        type="button"
                        className={mibsTableStyles.sortThBtn}
                        onClick={() => handleMibSort("missing_imports")}
                      >
                        {t("snmp.missingImportsCol")}
                        {mibSort === "missing_imports" ? (mibOrder === "asc" ? " ↑" : " ↓") : ""}
                      </button>
                    </th>
                    <th>
                      <button
                        type="button"
                        className={mibsTableStyles.sortThBtn}
                        onClick={() => handleMibSort("compile_status")}
                      >
                        {t("snmp.mibColCompile")}
                        {mibSort === "compile_status" ? (mibOrder === "asc" ? " ↑" : " ↓") : ""}
                      </button>
                    </th>
                    <th>
                      <button
                        type="button"
                        className={mibsTableStyles.sortThBtn}
                        onClick={() => handleMibSort("mfr")}
                      >
                        {t("snmp.mibColMfr")}
                        {mibSort === "mfr" ? (mibOrder === "asc" ? " ↑" : " ↓") : ""}
                      </button>
                    </th>
                    <th>{t("ipam.ipv4.actionsCol")}</th>
                  </tr>
                </thead>
                <tbody>
                  {mibRows.map((m) => {
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
                          title={t("snmp.browser.openMibTitle")}
                          onClick={() =>
                            navigate(`/snmp/browser?mib=${encodeURIComponent(m.name)}`)
                          }
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
                      <td style={{ fontSize: "var(--text-xs)", maxWidth: "14rem" }}>
                        {(m.missing_import_modules?.length ?? 0) > 0 ? (
                          <span className={dcimStyles.err} title={(m.missing_import_modules ?? []).join(", ")}>
                            {(m.missing_import_modules ?? []).join(", ")}
                          </span>
                        ) : (
                          <span className={dcimStyles.muted}>{t("snmp.missingImportsNone")}</span>
                        )}
                      </td>
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
                              rows={mibRows}
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
            <div className={mibsTableStyles.mibPagination}>
              <span>
                {t("ipam.grid.pagination.showing")} {mibRangeStart}–{mibRangeEnd}{" "}
                {t("ipam.grid.pagination.of")} <strong>{mibTotal}</strong>
              </span>
              <label>
                {t("ipam.grid.pagination.perPage")}{" "}
                <select
                  className={dcimStyles.controlSelect}
                  value={String(mibPageSize)}
                  onChange={(e) => setMibPageSize(Number(e.target.value))}
                >
                  {[10, 25, 50, 100].map((n) => (
                    <option key={n} value={n}>
                      {n}
                    </option>
                  ))}
                </select>
              </label>
              <button
                type="button"
                className={dcimStyles.btnMuted}
                disabled={mibPage <= 1 || mibsQ.isLoading}
                onClick={() => setMibPage((p) => Math.max(1, p - 1))}
              >
                {t("ipam.grid.pagination.prev")}
              </button>
              <span>
                {mibPage} / {mibPageCount}
              </span>
              <button
                type="button"
                className={dcimStyles.btnMuted}
                disabled={mibPage >= mibPageCount || mibsQ.isLoading}
                onClick={() => setMibPage((p) => Math.min(mibPageCount, p + 1))}
              >
                {t("ipam.grid.pagination.next")}
              </button>
            </div>
          </>
        ) : !mibsQ.isLoading && mibTotal === 0 ? (
          <p className={dcimStyles.muted}>
            {mibSearchQ ? t("snmp.mibsEmptySearch") : t("snmp.mibsEmpty")}
          </p>
        ) : null}
      </section>

      <p
        className={dcimStyles.muted}
        style={{ display: "flex", flexWrap: "wrap", alignItems: "center", gap: "0.35rem" }}
      >
        <span>{t("snmp.mibsVendorNoteShort")}</span>
        <HoverHelpCard ariaLabel={t("snmp.mibsVendorHelpAria")}>
          <p>{t("snmp.mibsVendorNote")}</p>
        </HoverHelpCard>
      </p>
    </>
  );
}
