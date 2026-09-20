import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { useI18n } from "@/i18n/I18nProvider";
import { ApiError } from "@/lib/api";
import * as api from "./dcimApi";
import styles from "./dcim.module.css";

export function RoomPowerInventorySection({ roomId, siteId }: { roomId: number; siteId: number }) {
  const { t } = useI18n();
  const qc = useQueryClient();
  const [err, setErr] = useState<string | null>(null);
  const [panelName, setPanelName] = useState("");
  const [circuitPanel, setCircuitPanel] = useState("");
  const [circuitName, setCircuitName] = useState("");
  const [circuitAmps, setCircuitAmps] = useState("");
  const [feedCircuit, setFeedCircuit] = useState("");
  const [feedName, setFeedName] = useState("");
  const [feedRack, setFeedRack] = useState("");

  const panelsQ = useQuery({
    queryKey: ["dcim", "power-panels", siteId],
    queryFn: () => api.listPowerPanels(siteId),
  });
  const circuitsQ = useQuery({
    queryKey: ["dcim", "power-circuits", siteId],
    queryFn: () => api.listPowerCircuits(undefined, siteId),
  });
  const feedsQ = useQuery({
    queryKey: ["dcim", "power-feeds", siteId],
    queryFn: () => api.listPowerFeeds({ siteId }),
  });
  const racksQ = useQuery({
    queryKey: ["dcim", "racks", "room", roomId],
    queryFn: () => api.listRacks(roomId),
  });

  const fail = (e: Error) => setErr(e instanceof ApiError ? e.message : e.message);
  const invalidate = () => {
    void qc.invalidateQueries({ queryKey: ["dcim", "power-panels"] });
    void qc.invalidateQueries({ queryKey: ["dcim", "power-circuits"] });
    void qc.invalidateQueries({ queryKey: ["dcim", "power-feeds"] });
  };

  const createPanel = useMutation({
    mutationFn: () => api.createPowerPanel({ site_id: siteId, room_id: roomId, name: panelName.trim() }),
    onSuccess: () => {
      setPanelName("");
      setErr(null);
      invalidate();
    },
    onError: fail,
  });
  const createCircuit = useMutation({
    mutationFn: () =>
      api.createPowerCircuit({
        panel_id: Number(circuitPanel),
        name: circuitName.trim(),
        rating_amps: circuitAmps === "" ? null : Number(circuitAmps),
      }),
    onSuccess: () => {
      setCircuitName("");
      setCircuitAmps("");
      setErr(null);
      invalidate();
    },
    onError: fail,
  });
  const createFeed = useMutation({
    mutationFn: () =>
      api.createPowerFeed({
        circuit_id: Number(feedCircuit),
        name: feedName.trim(),
        rack_id: feedRack === "" ? null : Number(feedRack),
        status: "planned",
      }),
    onSuccess: () => {
      setFeedName("");
      setErr(null);
      invalidate();
    },
    onError: fail,
  });

  const rackIds = new Set((racksQ.data ?? []).map((r) => r.id));
  const panels = (panelsQ.data ?? []).filter((p) => p.room_id == null || p.room_id === roomId);
  const panelIds = new Set(panels.map((p) => p.id));
  const circuits = (circuitsQ.data ?? []).filter((c) => panelIds.has(c.panel_id));
  const feeds = (feedsQ.data ?? []).filter((f) => (f.rack_id != null && rackIds.has(f.rack_id)) || panelIds.has(
    circuits.find((c) => c.id === f.circuit_id)?.panel_id ?? -1,
  ));

  return (
    <section className={styles.mfrDetailSection}>
      <h3 className={styles.mfrDetailSectionTitle}>{t("dcim.rooms.powerTabTitle")}</h3>
      <p className={styles.muted}>{t("dcim.rooms.powerTabIntro")}</p>
      <p className={styles.muted}>{t("dcim.power.noMeasurements")}</p>
      {err ? <p className={styles.err}>{err}</p> : null}

      <h4 className={styles.mfrDetailSectionTitle}>{t("dcim.power.panels")}</h4>
      {panels.length === 0 && !panelsQ.isLoading ? <p className={styles.muted}>{t("dcim.power.emptyPanels")}</p> : null}
      {panels.length > 0 ? (
        <table className={styles.table}>
          <thead>
            <tr>
              <th>{t("dcim.common.name")}</th>
              <th>Slug</th>
            </tr>
          </thead>
          <tbody>
            {panels.map((p) => (
              <tr key={p.id}>
                <td>{p.name}</td>
                <td>{p.slug}</td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : null}
      <form
        className={styles.formRow}
        onSubmit={(e) => {
          e.preventDefault();
          createPanel.mutate();
        }}
      >
        <label>
          {t("dcim.common.name")}
          <input value={panelName} onChange={(e) => setPanelName(e.target.value)} required />
        </label>
        <button type="submit" className={styles.btn} disabled={createPanel.isPending}>
          {t("dcim.power.addPanel")}
        </button>
      </form>

      <h4 className={styles.mfrDetailSectionTitle}>{t("dcim.power.circuits")}</h4>
      {circuits.length > 0 ? (
        <table className={styles.table}>
          <thead>
            <tr>
              <th>{t("dcim.common.name")}</th>
              <th>{t("dcim.power.rating")}</th>
              <th>{t("dcim.power.voltage")}</th>
            </tr>
          </thead>
          <tbody>
            {circuits.map((c) => (
              <tr key={c.id}>
                <td>{c.name}</td>
                <td>{c.rating_amps != null ? `${c.rating_amps} A` : "—"}</td>
                <td>{c.voltage != null ? `${c.voltage} V` : "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : null}
      <form
        className={styles.formRow}
        onSubmit={(e) => {
          e.preventDefault();
          createCircuit.mutate();
        }}
      >
        <label>
          {t("dcim.power.panels")}
          <select value={circuitPanel} onChange={(e) => setCircuitPanel(e.target.value)} required>
            <option value="">{t("dcim.power.choosePanel")}</option>
            {panels.map((p) => (
              <option key={p.id} value={String(p.id)}>
                {p.name}
              </option>
            ))}
          </select>
        </label>
        <label>
          {t("dcim.common.name")}
          <input value={circuitName} onChange={(e) => setCircuitName(e.target.value)} required />
        </label>
        <label>
          {t("dcim.power.rating")}
          <input type="number" min={1} value={circuitAmps} onChange={(e) => setCircuitAmps(e.target.value)} />
        </label>
        <button type="submit" className={styles.btn} disabled={createCircuit.isPending}>
          {t("dcim.power.addCircuit")}
        </button>
      </form>

      <h4 className={styles.mfrDetailSectionTitle}>{t("dcim.power.feeds")}</h4>
      {feeds.length === 0 && !feedsQ.isLoading ? <p className={styles.muted}>{t("dcim.power.emptyFeeds")}</p> : null}
      {feeds.length > 0 ? (
        <table className={styles.table}>
          <thead>
            <tr>
              <th>{t("dcim.common.name")}</th>
              <th>{t("dcim.power.circuits")}</th>
              <th>{t("dcim.racks.detailRack")}</th>
              <th>{t("dcim.power.status")}</th>
            </tr>
          </thead>
          <tbody>
            {feeds.map((f) => (
              <tr key={f.id}>
                <td>{f.name}</td>
                <td>
                  {f.panel_name ?? "—"} / {f.circuit_name ?? "—"}
                </td>
                <td>{f.rack_name ?? "—"}</td>
                <td>{f.status}</td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : null}
      <form
        className={styles.formRow}
        onSubmit={(e) => {
          e.preventDefault();
          createFeed.mutate();
        }}
      >
        <label>
          {t("dcim.power.circuits")}
          <select value={feedCircuit} onChange={(e) => setFeedCircuit(e.target.value)} required>
            <option value="">{t("dcim.power.chooseCircuit")}</option>
            {circuits.map((c) => (
              <option key={c.id} value={String(c.id)}>
                {c.name}
              </option>
            ))}
          </select>
        </label>
        <label>
          {t("dcim.common.name")}
          <input value={feedName} onChange={(e) => setFeedName(e.target.value)} required />
        </label>
        <label>
          {t("dcim.racks.detailRack")}
          <select value={feedRack} onChange={(e) => setFeedRack(e.target.value)}>
            <option value="">{t("dcim.power.chooseRack")}</option>
            {(racksQ.data ?? []).map((r) => (
              <option key={r.id} value={String(r.id)}>
                {r.name}
              </option>
            ))}
          </select>
        </label>
        <button type="submit" className={styles.btn} disabled={createFeed.isPending}>
          {t("dcim.power.addFeed")}
        </button>
      </form>
    </section>
  );
}
