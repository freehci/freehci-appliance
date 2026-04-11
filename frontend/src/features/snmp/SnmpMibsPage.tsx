import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { Link } from "react-router-dom";
import { useI18n } from "@/i18n/I18nProvider";
import { ApiError } from "@/lib/api";
import dcimStyles from "@/features/dcim/dcim.module.css";
import { MibSourceModal } from "./MibSourceModal";
import mibViewStyles from "./mibViewer.module.css";
import * as snmpApi from "./snmpApi";

export function SnmpMibsPage() {
  const { t } = useI18n();
  const qc = useQueryClient();
  const [err, setErr] = useState<string | null>(null);
  const [files, setFiles] = useState<File[]>([]);
  const [viewSourceName, setViewSourceName] = useState<string | null>(null);

  const mibsQ = useQuery({ queryKey: ["snmp", "mibs", "detailed"], queryFn: snmpApi.listSnmpMibsDetailed });

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
      void qc.invalidateQueries({ queryKey: ["snmp", "mibs", "detailed"] });
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
        />
      ) : null}
      {err ? <p className={dcimStyles.err}>{err}</p> : null}
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
            disabled={compileAll.isPending || (mibsQ.data?.length ?? 0) === 0}
            onClick={() => {
              if (!window.confirm(t("snmp.compileAllConfirm"))) return;
              compileAll.mutate();
            }}
            title={t("snmp.compileAllHint")}
          >
            {compileAll.isPending ? "…" : t("snmp.compileAll")}
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
                {mibsQ.data.map((m) => (
                  <tr key={m.name}>
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
                        <span className={m.compile_status === "error" ? dcimStyles.err : dcimStyles.muted}>
                          {m.compile_status}
                        </span>
                      </div>
                      {m.compile_message ? (
                        <div
                          className={dcimStyles.err}
                          style={{
                            fontSize: "var(--text-xs)",
                            marginTop: 4,
                            maxWidth: "28rem",
                            whiteSpace: "pre-wrap",
                            wordBreak: "break-word",
                          }}
                        >
                          {m.compile_message}
                        </div>
                      ) : null}
                    </td>
                    <td>{m.linked_manufacturer?.name ?? "—"}</td>
                    <td>
                      <button
                        type="button"
                        className={dcimStyles.btnLink}
                        style={{ marginRight: "var(--space-2)" }}
                        disabled={compileOne.isPending}
                        onClick={() => compileOne.mutate(m.name)}
                      >
                        {t("snmp.compileOne")}
                      </button>
                      <button
                        type="button"
                        className={dcimStyles.btnDanger}
                        disabled={delMib.isPending}
                        onClick={() => {
                          if (!window.confirm(t("snmp.mibDeleteConfirm"))) return;
                          delMib.mutate(m.name);
                        }}
                      >
                        {t("dcim.common.delete")}
                      </button>
                    </td>
                  </tr>
                ))}
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
