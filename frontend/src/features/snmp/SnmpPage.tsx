import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { Panel } from "@/components/ui/Panel";
import { useI18n } from "@/i18n/I18nProvider";
import { ApiError } from "@/lib/api";
import dcimStyles from "@/features/dcim/dcim.module.css";
import * as snmpApi from "./snmpApi";
import { SnmpInventoryPanel } from "./SnmpInventoryPanel";

export function SnmpPage() {
  const { t } = useI18n();
  const qc = useQueryClient();
  const [searchParams] = useSearchParams();
  const hostFromQuery = searchParams.get("host")?.trim() ?? "";

  const [err, setErr] = useState<string | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [probeHost, setProbeHost] = useState(() => hostFromQuery);
  const [probePort, setProbePort] = useState("161");
  const [probeCommunity, setProbeCommunity] = useState("public");
  const [probeOid, setProbeOid] = useState("1.3.6.1.2.1.1.1.0");
  const [probeOp, setProbeOp] = useState<"get" | "walk">("get");
  const [probeResult, setProbeResult] = useState<snmpApi.SnmpProbeResult | null>(null);

  const mibsQ = useQuery({ queryKey: ["snmp", "mibs"], queryFn: snmpApi.listSnmpMibs });

  useEffect(() => {
    if (hostFromQuery !== "") setProbeHost(hostFromQuery);
  }, [hostFromQuery]);

  const uploadMib = useMutation({
    mutationFn: (f: File) => snmpApi.uploadSnmpMib(f),
    onSuccess: () => {
      setErr(null);
      setFile(null);
      void qc.invalidateQueries({ queryKey: ["snmp", "mibs"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const delMib = useMutation({
    mutationFn: (name: string) => snmpApi.deleteSnmpMib(name),
    onSuccess: () => {
      setErr(null);
      void qc.invalidateQueries({ queryKey: ["snmp", "mibs"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const probeMut = useMutation({
    mutationFn: () =>
      snmpApi.snmpProbe({
        host: probeHost.trim(),
        port: Number(probePort) || 161,
        community: probeCommunity,
        oid: probeOid.trim(),
        operation: probeOp,
      }),
    onSuccess: (r) => {
      setErr(null);
      setProbeResult(r);
    },
    onError: (e: Error) => {
      setProbeResult(null);
      setErr(e instanceof ApiError ? e.message : e.message);
    },
  });

  return (
    <Panel title={t("snmp.title")}>
      {err ? <p className={dcimStyles.err}>{err}</p> : null}
      <p className={dcimStyles.muted} style={{ marginTop: 0 }}>
        {t("snmp.intro")}
      </p>

      <section className={dcimStyles.mfrDetailSection}>
        <h3 className={dcimStyles.mfrDetailSectionTitle}>{t("snmp.mibsTitle")}</h3>
        <p className={dcimStyles.muted} style={{ marginTop: 0 }}>
          {t("snmp.mibsHint")}
        </p>
        <div className={dcimStyles.formRow} style={{ alignItems: "flex-end" }}>
          <label>
            {t("snmp.mibFile")}
            <input
              type="file"
              accept=".mib,.my,.txt,text/plain"
              onChange={(e) => setFile(e.target.files?.[0] ?? null)}
            />
          </label>
          <button
            type="button"
            className={dcimStyles.btn}
            disabled={file == null || uploadMib.isPending}
            onClick={() => file && uploadMib.mutate(file)}
          >
            {uploadMib.isPending ? "…" : t("snmp.mibUpload")}
          </button>
        </div>

        {mibsQ.isLoading ? <p className={dcimStyles.muted}>{t("dcim.common.loading")}</p> : null}
        {mibsQ.data && mibsQ.data.length > 0 ? (
          <table className={dcimStyles.table} style={{ marginTop: "var(--space-2)" }}>
            <thead>
              <tr>
                <th>{t("snmp.mibColName")}</th>
                <th>{t("snmp.mibColSize")}</th>
                <th>{t("snmp.mibColModified")}</th>
                <th>{t("ipam.ipv4.actionsCol")}</th>
              </tr>
            </thead>
            <tbody>
              {mibsQ.data.map((m) => (
                <tr key={m.name}>
                  <td>
                    <code>{m.name}</code>
                  </td>
                  <td>{m.size_bytes}</td>
                  <td className={dcimStyles.muted}>{new Date(m.modified_at).toLocaleString()}</td>
                  <td>
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
        ) : mibsQ.data && mibsQ.data.length === 0 && !mibsQ.isLoading ? (
          <p className={dcimStyles.muted}>{t("snmp.mibsEmpty")}</p>
        ) : null}
      </section>

      <section className={dcimStyles.mfrDetailSection}>
        <h3 className={dcimStyles.mfrDetailSectionTitle}>{t("snmp.probeTitle")}</h3>
        <p className={dcimStyles.muted} style={{ marginTop: 0 }}>
          {t("snmp.probeHint")}
        </p>
        <form
          className={dcimStyles.formRow}
          onSubmit={(e) => {
            e.preventDefault();
            setErr(null);
            if (probeHost.trim() === "" || probeOid.trim() === "") {
              setErr(t("snmp.probeMissing"));
              return;
            }
            probeMut.mutate();
          }}
        >
          <label>
            {t("snmp.probeHost")}
            <input value={probeHost} onChange={(e) => setProbeHost(e.target.value)} placeholder="192.168.1.1" />
          </label>
          <label>
            {t("snmp.probePort")}
            <input value={probePort} onChange={(e) => setProbePort(e.target.value)} />
          </label>
          <label>
            {t("snmp.probeCommunity")}
            <input value={probeCommunity} onChange={(e) => setProbeCommunity(e.target.value)} />
          </label>
          <label>
            {t("snmp.probeOid")}
            <input value={probeOid} onChange={(e) => setProbeOid(e.target.value)} />
          </label>
          <label>
            {t("snmp.probeOperation")}
            <select value={probeOp} onChange={(e) => setProbeOp(e.target.value as "get" | "walk")}>
              <option value="get">GET</option>
              <option value="walk">WALK (bulk)</option>
            </select>
          </label>
          <button type="submit" className={dcimStyles.btn} disabled={probeMut.isPending}>
            {probeMut.isPending ? "…" : t("snmp.probeRun")}
          </button>
        </form>

        {probeResult ? (
          <div style={{ marginTop: "var(--space-2)" }}>
            {probeResult.ok ? (
              <p className={dcimStyles.muted}>{t("snmp.probeOk")}</p>
            ) : (
              <p className={dcimStyles.err}>
                {t("snmp.probeFail")}: {probeResult.error ?? "—"}
              </p>
            )}
            {probeResult.varbinds.length > 0 ? (
              <div style={{ maxHeight: "50vh", overflow: "auto" }}>
                <table className={dcimStyles.table}>
                  <thead>
                    <tr>
                      <th>{t("snmp.colOid")}</th>
                      <th>{t("snmp.probeValue")}</th>
                    </tr>
                  </thead>
                  <tbody>
                    {probeResult.varbinds.map((vb, i) => (
                      <tr key={`${vb.oid}-${i}`}>
                        <td>
                          <code>{vb.oid}</code>
                        </td>
                        <td>
                          <code>{vb.value}</code>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : null}
          </div>
        ) : null}
      </section>

      <SnmpInventoryPanel
        mode="picker"
        initialHost={hostFromQuery}
        hostSyncKey={hostFromQuery}
      />
    </Panel>
  );
}
