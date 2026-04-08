import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { Panel } from "@/components/ui/Panel";
import { useI18n } from "@/i18n/I18nProvider";
import { ApiError } from "@/lib/api";
import * as api from "./dcimApi";
import styles from "./dcim.module.css";

export function DcimDeviceDetailPage() {
  const { t } = useI18n();
  const qc = useQueryClient();
  const { deviceId } = useParams<{ deviceId: string }>();
  const id = Number(deviceId);

  const [err, setErr] = useState<string | null>(null);
  const [ifName, setIfName] = useState("");
  const [ifMac, setIfMac] = useState("");
  const [ifSpeed, setIfSpeed] = useState("");
  const [ifMtu, setIfMtu] = useState("");
  const [ifDesc, setIfDesc] = useState("");
  const [ifSort, setIfSort] = useState("0");

  const deviceQ = useQuery({
    queryKey: ["dcim", "devices", id],
    queryFn: () => api.getDevice(id),
    enabled: Number.isFinite(id) && id > 0,
  });

  const interfacesQ = useQuery({
    queryKey: ["dcim", "devices", id, "interfaces"],
    queryFn: () => api.listDeviceInterfaces(id),
    enabled: Number.isFinite(id) && id > 0,
  });

  const typesQ = useQuery({
    queryKey: ["dcim", "device-types"],
    queryFn: api.listDeviceTypes,
  });

  const modelsQ = useQuery({
    queryKey: ["dcim", "device-models"],
    queryFn: api.listDeviceModels,
  });

  const typeLabel = useMemo(() => {
    const tid = deviceQ.data?.effective_device_type_id;
    if (tid == null) return null;
    const row = (typesQ.data ?? []).find((x) => x.id === tid);
    return row ? `${row.name} (${row.slug})` : `#${tid}`;
  }, [deviceQ.data?.effective_device_type_id, typesQ.data]);

  const modelLabel = useMemo(() => {
    const mid = deviceQ.data?.device_model_id;
    if (mid == null) return null;
    const row = (modelsQ.data ?? []).find((x) => x.id === mid);
    return row ? row.name : `#${mid}`;
  }, [deviceQ.data?.device_model_id, modelsQ.data]);

  const createIf = useMutation({
    mutationFn: () => {
      const sp = ifSpeed.trim();
      const mtuS = ifMtu.trim();
      let speed_mbps: number | null = null;
      let mtu: number | null = null;
      if (sp !== "") {
        const n = Number(sp);
        if (!Number.isFinite(n) || n < 0) throw new Error(t("dcim.equip.if.badNumber"));
        speed_mbps = n;
      }
      if (mtuS !== "") {
        const n = Number(mtuS);
        if (!Number.isFinite(n) || n < 68 || n > 65535) throw new Error(t("dcim.equip.if.badMtu"));
        mtu = n;
      }
      return api.createDeviceInterface(id, {
        name: ifName.trim(),
        mac_address: ifMac.trim() === "" ? null : ifMac.trim(),
        speed_mbps,
        mtu,
        description: ifDesc.trim() === "" ? null : ifDesc.trim(),
        sort_order: Number(ifSort) || 0,
      });
    },
    onSuccess: () => {
      setIfName("");
      setIfMac("");
      setIfSpeed("");
      setIfMtu("");
      setIfDesc("");
      setIfSort("0");
      setErr(null);
      void qc.invalidateQueries({ queryKey: ["dcim", "devices", id, "interfaces"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const delIf = useMutation({
    mutationFn: (iid: number) => api.deleteDeviceInterface(id, iid),
    onSuccess: () => {
      setErr(null);
      void qc.invalidateQueries({ queryKey: ["dcim", "devices", id, "interfaces"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const toggleIf = useMutation({
    mutationFn: ({ iid, enabled }: { iid: number; enabled: boolean }) =>
      api.updateDeviceInterface(id, iid, { enabled }),
    onSuccess: () => {
      setErr(null);
      void qc.invalidateQueries({ queryKey: ["dcim", "devices", id, "interfaces"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  if (!Number.isFinite(id) || id < 1) {
    return (
      <Panel title={t("dcim.equip.dev.detailTitle")}>
        <p className={styles.err}>{t("dcim.equip.dev.invalidId")}</p>
        <Link to="/dcim/equipment" className={styles.tableLink}>
          {t("dcim.equip.dev.backToList")}
        </Link>
      </Panel>
    );
  }

  if (deviceQ.isError) {
    return (
      <Panel title={t("dcim.equip.dev.detailTitle")}>
        <p className={styles.err}>{(deviceQ.error as Error).message}</p>
        <Link to="/dcim/equipment" className={styles.tableLink}>
          {t("dcim.equip.dev.backToList")}
        </Link>
      </Panel>
    );
  }

  if (deviceQ.isLoading || !deviceQ.data) {
    return (
      <Panel title={t("dcim.equip.dev.detailTitle")}>
        <p className={styles.muted}>{t("dcim.common.loading")}</p>
      </Panel>
    );
  }

  const dev = deviceQ.data;
  const attrs = dev.attributes;
  const hasAttrs = attrs && Object.keys(attrs).length > 0;

  return (
    <>
      <p className={styles.mfrDetailBack}>
        <Link to="/dcim/equipment" className={styles.tableLink}>
          ← {t("dcim.equip.dev.backToList")}
        </Link>
      </p>

      <Panel title={dev.name}>
        {err ? <p className={styles.err}>{err}</p> : null}
        <dl className={styles.dlInline}>
          <dt>{t("dcim.common.id")}</dt>
          <dd>{dev.id}</dd>
          <dt>{t("dcim.equip.dev.modelCol")}</dt>
          <dd>{modelLabel ?? "—"}</dd>
          <dt>{t("dcim.equip.dev.effectiveTypeCol")}</dt>
          <dd>{typeLabel ?? "—"}</dd>
        </dl>
        {hasAttrs ? (
          <section className={styles.mfrDetailSection}>
            <h3 className={styles.mfrDetailSectionTitle}>{t("dcim.equip.dev.attributesBlock")}</h3>
            <pre className={styles.codeBlock}>{JSON.stringify(attrs, null, 2)}</pre>
          </section>
        ) : null}
      </Panel>

      <Panel title={t("dcim.equip.if.title")}>
        <p className={styles.muted} style={{ marginTop: 0 }}>
          {t("dcim.equip.if.hint")}
        </p>
        <form
          className={styles.formRow}
          onSubmit={(e) => {
            e.preventDefault();
            setErr(null);
            createIf.mutate();
          }}
        >
          <label>
            {t("dcim.equip.if.name")}
            <input value={ifName} onChange={(e) => setIfName(e.target.value)} required />
          </label>
          <label>
            {t("dcim.equip.if.mac")}
            <input value={ifMac} onChange={(e) => setIfMac(e.target.value)} placeholder="aa:bb:cc:dd:ee:ff" />
          </label>
          <label>
            {t("dcim.equip.if.speed")}
            <input
              type="number"
              min={0}
              value={ifSpeed}
              onChange={(e) => setIfSpeed(e.target.value)}
              placeholder="1000"
            />
          </label>
          <label>
            {t("dcim.equip.if.mtu")}
            <input type="number" min={68} max={65535} value={ifMtu} onChange={(e) => setIfMtu(e.target.value)} />
          </label>
          <label>
            {t("dcim.equip.mfr.description")}
            <input value={ifDesc} onChange={(e) => setIfDesc(e.target.value)} />
          </label>
          <label>
            {t("dcim.equip.if.sort")}
            <input type="number" value={ifSort} onChange={(e) => setIfSort(e.target.value)} />
          </label>
          <button type="submit" className={styles.btn} disabled={createIf.isPending}>
            {createIf.isPending ? "…" : t("dcim.common.add")}
          </button>
        </form>

        {interfacesQ.isLoading ? <p className={styles.muted}>{t("dcim.common.loading")}</p> : null}
        {interfacesQ.data && interfacesQ.data.length > 0 ? (
          <table className={styles.table}>
            <thead>
              <tr>
                <th>{t("dcim.common.id")}</th>
                <th>{t("dcim.equip.if.name")}</th>
                <th>{t("dcim.equip.if.mac")}</th>
                <th>{t("dcim.equip.if.speed")}</th>
                <th>{t("dcim.equip.if.mtu")}</th>
                <th>{t("dcim.equip.if.enabled")}</th>
                <th>{t("dcim.equip.mfr.description")}</th>
                <th />
              </tr>
            </thead>
            <tbody>
              {interfacesQ.data.map((x) => (
                <tr key={x.id}>
                  <td>{x.id}</td>
                  <td>{x.name}</td>
                  <td>{x.mac_address ?? "—"}</td>
                  <td>{x.speed_mbps ?? "—"}</td>
                  <td>{x.mtu ?? "—"}</td>
                  <td>
                    <button
                      type="button"
                      className={styles.btn}
                      onClick={() => toggleIf.mutate({ iid: x.id, enabled: !x.enabled })}
                      disabled={toggleIf.isPending}
                    >
                      {x.enabled ? t("dcim.equip.if.disable") : t("dcim.equip.if.enable")}
                    </button>
                  </td>
                  <td>{x.description ?? "—"}</td>
                  <td>
                    <button
                      type="button"
                      className={styles.btnDanger}
                      onClick={() => delIf.mutate(x.id)}
                      disabled={delIf.isPending}
                    >
                      {t("dcim.common.delete")}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          !interfacesQ.isLoading && <p className={styles.muted}>{t("dcim.equip.if.empty")}</p>
        )}
      </Panel>
    </>
  );
}
