import { useState } from "react";
import * as dcimApi from "@/features/dcim/dcimApi";
import dcimStyles from "@/features/dcim/dcim.module.css";
import type { MessageKey } from "@/i18n/messages/en";
import type { NameSource, NetworkScanDiscovery } from "@/features/networkScans/networkScanApi";

export function DiscoveryTable({
  rows,
  models,
  onApprove,
  onReject,
  busy,
  t,
  styles = dcimStyles,
}: {
  rows: NetworkScanDiscovery[];
  models: Awaited<ReturnType<typeof dcimApi.listDeviceModels>>;
  onApprove: (id: number, body: { chosen_name_source: NameSource; chosen_name?: string; device_model_id: number }) => void;
  onReject: (id: number) => void;
  busy: boolean;
  t: (k: MessageKey) => string;
  styles?: typeof dcimStyles;
}) {
  return (
    <table className={styles.table}>
      <thead>
        <tr>
          <th>IP</th>
          <th>{t("netscan.candidates")}</th>
          <th>{t("netscan.approveCol")}</th>
        </tr>
      </thead>
      <tbody>
        {rows.map((d) => (
          <DiscoveryRow key={d.id} d={d} models={models} onApprove={onApprove} onReject={onReject} busy={busy} t={t} styles={styles} />
        ))}
      </tbody>
    </table>
  );
}

function DiscoveryRow({
  d,
  models,
  onApprove,
  onReject,
  busy,
  t,
  styles,
}: {
  d: NetworkScanDiscovery;
  models: Awaited<ReturnType<typeof dcimApi.listDeviceModels>>;
  onApprove: (id: number, body: { chosen_name_source: NameSource; chosen_name?: string; device_model_id: number }) => void;
  onReject: (id: number) => void;
  busy: boolean;
  t: (k: MessageKey) => string;
  styles: typeof dcimStyles;
}) {
  const [src, setSrc] = useState<NameSource>("ip");
  const [custom, setCustom] = useState("");
  const [mid, setMid] = useState("");

  const c = d.name_candidates_json ?? {};

  return (
    <tr>
      <td>
        <code>{d.address}</code>
        <div className={styles.muted} style={{ fontSize: "var(--text-xs)" }}>
          job #{d.job_id}
        </div>
      </td>
      <td style={{ fontSize: "var(--text-xs)" }}>
        <div>
          <strong>IP:</strong> {c.ip ?? d.address}
        </div>
        {c.ptr ? (
          <div>
            <strong>PTR:</strong> {c.ptr}
          </div>
        ) : null}
        {c.snmp_sysname ? (
          <div>
            <strong>sysName:</strong> {c.snmp_sysname}
          </div>
        ) : null}
      </td>
      <td>
        <div className={styles.formRow} style={{ flexWrap: "wrap", alignItems: "flex-end" }}>
          <label>
            {t("netscan.nameSource")}
            <select value={src} onChange={(e) => setSrc(e.target.value as NameSource)}>
              <option value="ip">IP</option>
              <option value="ptr">PTR</option>
              <option value="snmp_sysname">sysName</option>
              <option value="custom">{t("netscan.nameCustom")}</option>
            </select>
          </label>
          {src === "custom" ? (
            <label>
              {t("netscan.customDeviceName")}
              <input value={custom} onChange={(e) => setCustom(e.target.value)} />
            </label>
          ) : null}
          <label>
            {t("netscan.fieldDefaultModel")}
            <select value={mid} onChange={(e) => setMid(e.target.value)}>
              <option value="">{t("dcim.common.none")}</option>
              {models.map((m) => (
                <option key={m.id} value={String(m.id)}>
                  {m.name}
                </option>
              ))}
            </select>
          </label>
          <button
            type="button"
            className={styles.btn}
            disabled={busy || !mid}
            onClick={() => {
              const device_model_id = Number(mid);
              if (!device_model_id) return;
              if (src === "custom") {
                onApprove(d.id, { chosen_name_source: "custom", chosen_name: custom.trim(), device_model_id });
              } else {
                onApprove(d.id, { chosen_name_source: src, device_model_id });
              }
            }}
          >
            {t("netscan.promote")}
          </button>
          <button type="button" className={styles.btnMuted} disabled={busy} onClick={() => onReject(d.id)}>
            {t("netscan.reject")}
          </button>
        </div>
      </td>
    </tr>
  );
}
