import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { Panel } from "@/components/ui/Panel";
import { useI18n } from "@/i18n/I18nProvider";
import { ApiError } from "@/lib/api";
import dcimStyles from "@/features/dcim/dcim.module.css";
import * as dcimApi from "@/features/dcim/dcimApi";
import * as snmpApi from "./snmpApi";

export function SnmpPage() {
  const { t } = useI18n();
  const qc = useQueryClient();
  const [err, setErr] = useState<string | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [probeHost, setProbeHost] = useState("");
  const [probePort, setProbePort] = useState("161");
  const [probeCommunity, setProbeCommunity] = useState("public");
  const [probeOid, setProbeOid] = useState("1.3.6.1.2.1.1.1.0");
  const [probeOp, setProbeOp] = useState<"get" | "walk">("get");
  const [probeResult, setProbeResult] = useState<snmpApi.SnmpProbeResult | null>(null);
  const [invResult, setInvResult] = useState<snmpApi.SnmpInventoryResult | null>(null);
  const [scanResult, setScanResult] = useState<snmpApi.SnmpScanResult | null>(null);
  const [invDeviceId, setInvDeviceId] = useState("");
  const [applyMsg, setApplyMsg] = useState<string | null>(null);

  const mibsQ = useQuery({ queryKey: ["snmp", "mibs"], queryFn: snmpApi.listSnmpMibs });
  const devicesQ = useQuery({ queryKey: ["dcim", "devices"], queryFn: dcimApi.listDevices });

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

  const invMut = useMutation({
    mutationFn: () =>
      snmpApi.snmpInventory({
        host: probeHost.trim(),
        port: Number(probePort) || 161,
        community: probeCommunity,
      }),
    onSuccess: (r) => {
      setErr(null);
      setApplyMsg(null);
      setInvResult(r);
      setScanResult(null);
    },
    onError: (e: Error) => {
      setInvResult(null);
      setErr(e instanceof ApiError ? e.message : e.message);
    },
  });

  const scanMut = useMutation({
    mutationFn: () =>
      snmpApi.snmpScan({
        host: probeHost.trim(),
        port: Number(probePort) || 161,
        community: probeCommunity,
        max_varbinds: 8000,
      }),
    onSuccess: (r) => {
      setErr(null);
      setApplyMsg(null);
      setScanResult(r);
      if (r.ok) {
        setInvResult({
          ok: true,
          error: null,
          host: r.host,
          sys_name: r.sys_name,
          sys_descr: r.sys_descr,
          interfaces: r.interfaces,
          truncated: r.truncated,
          varbinds_collected: r.varbinds_collected,
        });
      }
    },
    onError: (e: Error) => {
      setScanResult(null);
      setErr(e instanceof ApiError ? e.message : e.message);
    },
  });

  const applyMut = useMutation({
    mutationFn: () =>
      snmpApi.snmpInventoryApply({
        device_id: Number(invDeviceId),
        host: probeHost.trim(),
        port: Number(probePort) || 161,
        community: probeCommunity,
      }),
    onSuccess: (r) => {
      setApplyMsg(null);
      if (!r.ok) {
        setErr(r.error ?? t("snmp.probeFail"));
        return;
      }
      setErr(null);
      const stats = t("snmp.invApplyStats")
        .replace(/\{created\}/g, String(r.created))
        .replace(/\{updated\}/g, String(r.updated))
        .replace(/\{skipped\}/g, String(r.skipped));
      setApplyMsg(`${t("snmp.invApplyOk")} ${stats}`);
      if (r.poll) setInvResult(r.poll);
      const did = r.device_id;
      void qc.invalidateQueries({ queryKey: ["dcim", "devices", did, "interfaces"] });
      void qc.invalidateQueries({ queryKey: ["dcim", "devices"] });
    },
    onError: (e: Error) => {
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

      <section className={dcimStyles.mfrDetailSection}>
        <h3 className={dcimStyles.mfrDetailSectionTitle}>{t("snmp.invTitle")}</h3>
        <p className={dcimStyles.muted} style={{ marginTop: 0 }}>
          {t("snmp.invHint")}
        </p>
        <div className={dcimStyles.formRow} style={{ alignItems: "flex-end", flexWrap: "wrap" }}>
          <label>
            {t("snmp.invDevice")}
            <select
              value={invDeviceId}
              onChange={(e) => setInvDeviceId(e.target.value)}
              style={{ minWidth: "12rem" }}
            >
              <option value="">{t("snmp.invDevicePlaceholder")}</option>
              {(devicesQ.data ?? []).map((d) => (
                <option key={d.id} value={String(d.id)}>
                  {d.name} (id {d.id})
                </option>
              ))}
            </select>
          </label>
          <button
            type="button"
            className={dcimStyles.btn}
            disabled={invMut.isPending || scanMut.isPending || probeHost.trim() === ""}
            onClick={() => {
              setErr(null);
              setApplyMsg(null);
              if (probeHost.trim() === "") {
                setErr(t("snmp.invMissingHost"));
                return;
              }
              invMut.mutate();
            }}
          >
            {invMut.isPending ? "…" : t("snmp.invFetch")}
          </button>
          <button
            type="button"
            className={dcimStyles.btn}
            disabled={invMut.isPending || scanMut.isPending || probeHost.trim() === ""}
            onClick={() => {
              setErr(null);
              setApplyMsg(null);
              if (probeHost.trim() === "") {
                setErr(t("snmp.invMissingHost"));
                return;
              }
              scanMut.mutate();
            }}
            title={t("snmp.scanHint")}
          >
            {scanMut.isPending ? "…" : t("snmp.scanFetch")}
          </button>
          <button
            type="button"
            className={dcimStyles.btn}
            disabled={
              applyMut.isPending ||
              invMut.isPending ||
              scanMut.isPending ||
              probeHost.trim() === "" ||
              invDeviceId === "" ||
              !Number(invDeviceId)
            }
            onClick={() => {
              setErr(null);
              setApplyMsg(null);
              if (probeHost.trim() === "") {
                setErr(t("snmp.invMissingHost"));
                return;
              }
              if (invDeviceId === "" || !Number(invDeviceId)) {
                setErr(t("snmp.invMissingDevice"));
                return;
              }
              applyMut.mutate();
            }}
          >
            {applyMut.isPending ? "…" : t("snmp.invApply")}
          </button>
        </div>
        {applyMsg ? <p className={dcimStyles.muted}>{applyMsg}</p> : null}

        {invResult ? (
          <div style={{ marginTop: "var(--space-2)" }}>
            {!invResult.ok ? (
              <p className={dcimStyles.err}>
                {t("snmp.probeFail")}: {invResult.error ?? "—"}
              </p>
            ) : (
              <>
                <p className={dcimStyles.muted}>
                  <strong>{t("snmp.invSysName")}:</strong> {invResult.sys_name ?? "—"}{" "}
                  <span className={dcimStyles.muted}>
                    ({t("snmp.invVarbinds")}: {invResult.varbinds_collected ?? "—"})
                  </span>
                </p>
                {invResult.sys_descr ? (
                  <p className={dcimStyles.muted} style={{ whiteSpace: "pre-wrap", maxHeight: "6rem", overflow: "auto" }}>
                    <strong>{t("snmp.invSysDescr")}:</strong> {invResult.sys_descr}
                  </p>
                ) : null}
                {invResult.truncated ? <p className={dcimStyles.err}>{t("snmp.invTruncated")}</p> : null}
                {invResult.interfaces.length > 0 ? (
                  <div style={{ maxHeight: "55vh", overflow: "auto" }}>
                    <table className={dcimStyles.table}>
                      <thead>
                        <tr>
                          <th>{t("snmp.invColIfIndex")}</th>
                          <th>{t("snmp.invColName")}</th>
                          <th>{t("snmp.invColDescr")}</th>
                          <th>{t("snmp.invColMac")}</th>
                          <th>{t("snmp.invColSpeed")}</th>
                          <th>{t("snmp.invColMtu")}</th>
                          <th>{t("snmp.invColAdmin")}</th>
                          <th>{t("snmp.invColOper")}</th>
                          <th>{t("snmp.invColEnabled")}</th>
                        </tr>
                      </thead>
                      <tbody>
                        {invResult.interfaces.map((row) => (
                          <tr key={row.if_index}>
                            <td>{row.if_index}</td>
                            <td>
                              <code>{row.name}</code>
                            </td>
                            <td>{row.description ?? "—"}</td>
                            <td>
                              <code>{row.mac_address ?? "—"}</code>
                            </td>
                            <td>{row.speed_mbps ?? "—"}</td>
                            <td>{row.mtu ?? "—"}</td>
                            <td>{row.admin_status}</td>
                            <td>{row.oper_status}</td>
                            <td>{row.enabled ? "✓" : "—"}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <p className={dcimStyles.muted}>—</p>
                )}
              </>
            )}
          </div>
        ) : null}

        {scanResult && !scanResult.ok ? (
          <p className={dcimStyles.err} style={{ marginTop: "var(--space-2)" }}>
            {t("snmp.probeFail")}: {scanResult.error ?? "—"}
          </p>
        ) : null}

        {scanResult && scanResult.warnings.length > 0 ? (
          <ul className={dcimStyles.muted} style={{ marginTop: "var(--space-2)" }}>
            {scanResult.warnings.map((w) => (
              <li key={w}>{w}</li>
            ))}
          </ul>
        ) : null}

        {scanResult && scanResult.ok ? (
          <div style={{ marginTop: "var(--space-3)" }}>
            {scanResult.ip_addresses.length > 0 ? (
              <>
                <h4 className={dcimStyles.mfrDetailSectionTitle} style={{ fontSize: "1rem" }}>
                  {t("snmp.scanIpTitle")}
                </h4>
                <div style={{ maxHeight: "40vh", overflow: "auto" }}>
                  <table className={dcimStyles.table}>
                    <thead>
                      <tr>
                        <th>{t("snmp.scanColAddress")}</th>
                        <th>{t("snmp.invColIfIndex")}</th>
                        <th>{t("snmp.invColName")}</th>
                        <th>{t("snmp.scanColNetmask")}</th>
                      </tr>
                    </thead>
                    <tbody>
                      {scanResult.ip_addresses.map((row) => (
                        <tr key={`${row.address}-${row.if_index}`}>
                          <td>
                            <code>{row.address}</code>
                          </td>
                          <td>{row.if_index}</td>
                          <td>{row.interface_name ?? "—"}</td>
                          <td>
                            <code>{row.netmask ?? "—"}</code>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </>
            ) : null}

            {scanResult.vlans.length > 0 ? (
              <>
                <h4 className={dcimStyles.mfrDetailSectionTitle} style={{ fontSize: "1rem", marginTop: "var(--space-2)" }}>
                  {t("snmp.scanVlanTitle")}
                </h4>
                <div style={{ maxHeight: "30vh", overflow: "auto" }}>
                  <table className={dcimStyles.table}>
                    <thead>
                      <tr>
                        <th>{t("snmp.scanColVlanId")}</th>
                        <th>{t("snmp.scanColVlanName")}</th>
                      </tr>
                    </thead>
                    <tbody>
                      {scanResult.vlans.map((row) => (
                        <tr key={row.vlan_id}>
                          <td>{row.vlan_id}</td>
                          <td>{row.name ?? "—"}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </>
            ) : null}

            {scanResult.interface_vlans.length > 0 ? (
              <>
                <h4 className={dcimStyles.mfrDetailSectionTitle} style={{ fontSize: "1rem", marginTop: "var(--space-2)" }}>
                  {t("snmp.scanPvidTitle")}
                </h4>
                <p className={dcimStyles.muted} style={{ marginTop: 0 }}>
                  {t("snmp.scanPvidHint")}
                </p>
                <div style={{ maxHeight: "40vh", overflow: "auto" }}>
                  <table className={dcimStyles.table}>
                    <thead>
                      <tr>
                        <th>{t("snmp.invColIfIndex")}</th>
                        <th>{t("snmp.invColName")}</th>
                        <th>{t("snmp.scanColBridgePort")}</th>
                        <th>{t("snmp.scanColPvid")}</th>
                      </tr>
                    </thead>
                    <tbody>
                      {scanResult.interface_vlans.map((row) => (
                        <tr key={`${row.if_index}-${row.bridge_port ?? 0}`}>
                          <td>{row.if_index}</td>
                          <td>{row.interface_name ?? "—"}</td>
                          <td>{row.bridge_port ?? "—"}</td>
                          <td>{row.native_vlan_id}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </>
            ) : null}
          </div>
        ) : null}
      </section>
    </Panel>
  );
}
