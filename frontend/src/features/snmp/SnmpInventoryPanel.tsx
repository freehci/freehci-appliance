import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useI18n } from "@/i18n/I18nProvider";
import { ApiError } from "@/lib/api";
import dcimStyles from "@/features/dcim/dcim.module.css";
import * as dcimApi from "@/features/dcim/dcimApi";
import * as snmpApi from "./snmpApi";

export type SnmpInventoryPanelProps = {
  /** Velg DCIM-enhet i UI, eller bruk fast deviceId (enhetsvisning). */
  mode: "picker" | "fixed_device";
  /** Påkrevd når mode === "fixed_device". */
  deviceId?: number;
  /** Fyller SNMP-vert ved navigasjon / første IPv4 på enhet. */
  initialHost?: string;
  initialCommunity?: string;
  /** Endre når URL/query oppdateres (f.eks. snmpHost fra IPAM). */
  hostSyncKey?: string;
};

export function SnmpInventoryPanel({
  mode,
  deviceId: fixedDeviceId,
  initialHost = "",
  initialCommunity = "public",
  hostSyncKey = "",
}: SnmpInventoryPanelProps) {
  const { t } = useI18n();
  const qc = useQueryClient();
  const [err, setErr] = useState<string | null>(null);
  const [probeHost, setProbeHost] = useState("");
  const [probePort, setProbePort] = useState("161");
  const [probeCommunity, setProbeCommunity] = useState(initialCommunity);
  const [invResult, setInvResult] = useState<snmpApi.SnmpInventoryResult | null>(null);
  const [scanResult, setScanResult] = useState<snmpApi.SnmpScanResult | null>(null);
  const [invDeviceId, setInvDeviceId] = useState("");
  const [applyMsg, setApplyMsg] = useState<string | null>(null);

  const devicesQ = useQuery({
    queryKey: ["dcim", "devices"],
    queryFn: dcimApi.listDevices,
    enabled: mode === "picker",
  });

  useEffect(() => {
    setProbeCommunity(initialCommunity);
  }, [initialCommunity]);

  useEffect(() => {
    const h = initialHost?.trim() ?? "";
    if (h !== "") setProbeHost(h);
  }, [initialHost, hostSyncKey]);

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

  const applyDeviceId =
    mode === "fixed_device" && fixedDeviceId != null && fixedDeviceId > 0
      ? fixedDeviceId
      : Number(invDeviceId);

  const applyMut = useMutation({
    mutationFn: () =>
      snmpApi.snmpInventoryApply({
        device_id: applyDeviceId,
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

  const canApply =
    mode === "fixed_device"
      ? fixedDeviceId != null && fixedDeviceId > 0
      : invDeviceId !== "" && Number(invDeviceId) > 0;

  return (
    <section className={dcimStyles.mfrDetailSection}>
      <h3 className={dcimStyles.mfrDetailSectionTitle}>
        {mode === "fixed_device" ? t("dcim.equip.dev.snmpSectionTitle") : t("snmp.invTitle")}
      </h3>
      <p className={dcimStyles.muted} style={{ marginTop: 0 }}>
        {mode === "fixed_device" ? t("dcim.equip.dev.snmpSectionHint") : t("snmp.invHint")}
      </p>

      {err ? <p className={dcimStyles.err}>{err}</p> : null}

      <div className={dcimStyles.formRow} style={{ alignItems: "flex-end", flexWrap: "wrap" }}>
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
        {mode === "picker" ? (
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
        ) : null}
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
            !canApply
          }
          onClick={() => {
            setErr(null);
            setApplyMsg(null);
            if (probeHost.trim() === "") {
              setErr(t("snmp.invMissingHost"));
              return;
            }
            if (!canApply) {
              setErr(t("snmp.invMissingDevice"));
              return;
            }
            applyMut.mutate();
          }}
        >
          {applyMut.isPending ? "…" : t("snmp.invApply")}
        </button>
      </div>

      {mode === "fixed_device" ? (
        <p className={dcimStyles.muted} style={{ marginTop: "var(--space-2)" }}>
          <Link
            to={probeHost.trim() ? `/snmp/tools?host=${encodeURIComponent(probeHost.trim())}` : "/snmp/tools"}
            className={dcimStyles.tableLink}
          >
            {t("dcim.equip.dev.snmpOpenTools")}
          </Link>
        </p>
      ) : null}

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
                <p
                  className={dcimStyles.muted}
                  style={{ whiteSpace: "pre-wrap", maxHeight: "6rem", overflow: "auto" }}
                >
                  <strong>{t("snmp.invSysDescr")}:</strong> {invResult.sys_descr}
                </p>
              ) : null}
              {invResult.truncated ? <p className={dcimStyles.err}>{t("snmp.invTruncated")}</p> : null}
              {invResult.interfaces.length > 0 ? (
                <div style={{ maxHeight: mode === "fixed_device" ? "35vh" : "55vh", overflow: "auto" }}>
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
              <div style={{ maxHeight: mode === "fixed_device" ? "28vh" : "40vh", overflow: "auto" }}>
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
              <h4
                className={dcimStyles.mfrDetailSectionTitle}
                style={{ fontSize: "1rem", marginTop: "var(--space-2)" }}
              >
                {t("snmp.scanVlanTitle")}
              </h4>
              <div style={{ maxHeight: "24vh", overflow: "auto" }}>
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
              <h4
                className={dcimStyles.mfrDetailSectionTitle}
                style={{ fontSize: "1rem", marginTop: "var(--space-2)" }}
              >
                {t("snmp.scanPvidTitle")}
              </h4>
              <p className={dcimStyles.muted} style={{ marginTop: 0 }}>
                {t("snmp.scanPvidHint")}
              </p>
              <div style={{ maxHeight: "28vh", overflow: "auto" }}>
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
  );
}
