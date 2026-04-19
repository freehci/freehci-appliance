import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { Panel } from "@/components/ui/Panel";
import { useI18n } from "@/i18n/I18nProvider";
import { ApiError } from "@/lib/api";
import * as api from "./dcimApi";
import { DCIM_DEVICE_ICON_URL_ATTR } from "./modelImages";
import styles from "./dcim.module.css";

export function DcimDeviceNewPage() {
  const { t } = useI18n();
  const qc = useQueryClient();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [err, setErr] = useState<string | null>(null);
  const [devModel, setDevModel] = useState("");
  const [devDt, setDevDt] = useState("");
  const [devName, setDevName] = useState("");
  const [devAttrsJson, setDevAttrsJson] = useState("{}");
  const [devIconUrl, setDevIconUrl] = useState("");

  const modelsQ = useQuery({ queryKey: ["dcim", "device-models"], queryFn: api.listDeviceModels });
  const deviceTypesQ = useQuery({ queryKey: ["dcim", "device-types"], queryFn: api.listDeviceTypes });

  useEffect(() => {
    const name = searchParams.get("prefillDeviceName")?.trim() ?? "";
    const snmpHost = searchParams.get("snmpHost")?.trim() ?? "";
    if (name !== "") setDevName(name);
    if (snmpHost !== "") {
      setDevAttrsJson((prev) => {
        try {
          const raw = prev.trim() === "" ? "{}" : prev;
          const obj = JSON.parse(raw) as unknown;
          if (obj !== null && typeof obj === "object" && !Array.isArray(obj)) {
            return JSON.stringify({ ...(obj as Record<string, unknown>), snmp_host: snmpHost }, null, 2);
          }
        } catch {
          /* ignore */
        }
        return JSON.stringify({ snmp_host: snmpHost }, null, 2);
      });
    }
  }, [searchParams]);

  const createDev = useMutation({
    mutationFn: () => {
      let attrs: Record<string, unknown> = {};
      const raw = devAttrsJson.trim();
      if (raw !== "") {
        try {
          const parsed: unknown = JSON.parse(raw);
          if (parsed === null || typeof parsed !== "object" || Array.isArray(parsed)) {
            throw new Error(t("dcim.equip.dev.attributesInvalid"));
          }
          attrs = { ...(parsed as Record<string, unknown>) };
        } catch {
          throw new Error(t("dcim.equip.dev.attributesInvalid"));
        }
      }
      const icon = devIconUrl.trim();
      if (icon !== "") attrs[DCIM_DEVICE_ICON_URL_ATTR] = icon;
      else delete attrs[DCIM_DEVICE_ICON_URL_ATTR];
      const attrsOut = Object.keys(attrs).length > 0 ? attrs : null;
      return api.createDevice({
        name: devName.trim(),
        device_model_id: devModel === "" ? null : Number(devModel),
        device_type_id: devDt === "" ? null : Number(devDt),
        attributes: attrsOut,
      });
    },
    onSuccess: (d) => {
      setErr(null);
      void qc.invalidateQueries({ queryKey: ["dcim", "devices"] });
      void navigate(`/dcim/equipment/devices/${d.id}`, { replace: true });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  return (
    <>
      <p className={styles.mfrDetailBack}>
        <Link to="/dcim/equipment" className={styles.tableLink}>
          ← {t("dcim.equip.dev.backToList")}
        </Link>
      </p>
      <Panel title={t("dcim.equip.dev.newPageTitle")}>
        {err ? <p className={styles.err}>{err}</p> : null}
        <form
          className={styles.formRow}
          style={{ flexDirection: "column", alignItems: "stretch", maxWidth: "42rem" }}
          onSubmit={(e) => {
            e.preventDefault();
            setErr(null);
            createDev.mutate();
          }}
        >
          <label>
            {t("dcim.equip.dev.model")}
            <select value={devModel} onChange={(e) => setDevModel(e.target.value)}>
              <option value="">{t("dcim.common.none")}</option>
              {(modelsQ.data ?? []).map((x) => (
                <option key={x.id} value={String(x.id)}>
                  {x.name}
                </option>
              ))}
            </select>
          </label>
          <label>
            {t("dcim.equip.dev.dtOverride")}
            <select value={devDt} onChange={(e) => setDevDt(e.target.value)}>
              <option value="">{t("dcim.equip.dev.dtInherit")}</option>
              {(deviceTypesQ.data ?? []).map((d) => (
                <option key={d.id} value={String(d.id)}>
                  {d.name}
                </option>
              ))}
            </select>
          </label>
          <label>
            {t("dcim.equip.dev.hostname")}
            <input value={devName} onChange={(e) => setDevName(e.target.value)} required />
          </label>
          <label title={t("dcim.equip.dev.iconUrlHint")}>
            {t("dcim.equip.dev.iconUrl")}
            <input
              type="url"
              value={devIconUrl}
              onChange={(e) => setDevIconUrl(e.target.value)}
              placeholder="https://"
            />
          </label>
          <label style={{ minWidth: "12rem" }}>
            {t("dcim.equip.dev.attributesJson")}
            <textarea
              value={devAttrsJson}
              onChange={(e) => setDevAttrsJson(e.target.value)}
              rows={6}
              className={styles.mfrTextarea}
              placeholder='{"os":"Linux"}'
              spellCheck={false}
            />
          </label>
          <div>
            <button type="submit" className={styles.btn} disabled={createDev.isPending || !devName.trim()}>
              {createDev.isPending ? "…" : t("dcim.equip.dev.create")}
            </button>
          </div>
        </form>
      </Panel>
    </>
  );
}
