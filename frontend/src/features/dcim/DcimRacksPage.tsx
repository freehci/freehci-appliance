import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { Panel } from "@/components/ui/Panel";
import { useI18n } from "@/i18n/I18nProvider";
import { ApiError } from "@/lib/api";
import * as api from "./dcimApi";
import { DcimInnerTabs } from "./DcimInnerTabs";
import styles from "./dcim.module.css";
import { RackPlanner } from "./RackPlanner";

export function DcimRacksPage() {
  const { t } = useI18n();
  const qc = useQueryClient();
  const [searchParams] = useSearchParams();
  const [roomFilter, setRoomFilter] = useState<string>(() => searchParams.get("room") ?? "");

  const highlightPlacementId = useMemo(() => {
    const raw = searchParams.get("highlightPlacement");
    if (raw == null || raw === "") return undefined;
    const n = Number(raw);
    return Number.isFinite(n) && n > 0 ? n : undefined;
  }, [searchParams]);

  useEffect(() => {
    const r = searchParams.get("room");
    if (r != null && r !== "") setRoomFilter(r);
  }, [searchParams]);

  const placementsForHighlight = useQuery({
    queryKey: ["dcim", "placements", "all"],
    queryFn: () => api.listPlacements(),
    enabled: highlightPlacementId != null && (searchParams.get("room") == null || searchParams.get("room") === ""),
  });

  const allRacksForHighlight = useQuery({
    queryKey: ["dcim", "racks", "all-for-highlight"],
    queryFn: () => api.listRacks(),
    enabled: highlightPlacementId != null && (searchParams.get("room") == null || searchParams.get("room") === ""),
  });

  useEffect(() => {
    if (highlightPlacementId == null) return;
    if (searchParams.get("room")) return;
    const p = placementsForHighlight.data?.find((x) => x.id === highlightPlacementId);
    if (!p || !allRacksForHighlight.data) return;
    const rk = allRacksForHighlight.data.find((r) => r.id === p.rack_id);
    if (rk) setRoomFilter(String(rk.room_id));
  }, [
    highlightPlacementId,
    placementsForHighlight.data,
    allRacksForHighlight.data,
    searchParams,
  ]);

  useEffect(() => {
    if (highlightPlacementId != null) setRackTab("elevation");
  }, [highlightPlacementId]);

  const [roomId, setRoomId] = useState<string>("");
  const [name, setName] = useState("");
  const [uHeight, setUHeight] = useState("42");
  const [err, setErr] = useState<string | null>(null);
  const [rackTab, setRackTab] = useState<"elevation" | "admin">("elevation");

  const roomsQ = useQuery({ queryKey: ["dcim", "rooms", "all"], queryFn: () => api.listRooms() });
  const filterNum = useMemo(() => {
    const n = Number(roomFilter);
    return Number.isFinite(n) && n > 0 ? n : undefined;
  }, [roomFilter]);

  const racksQ = useQuery({
    queryKey: ["dcim", "racks", filterNum ?? "all"],
    queryFn: () => api.listRacks(filterNum),
  });

  const m = useMutation({
    mutationFn: () =>
      api.createRack({
        room_id: Number(roomId),
        name: name.trim(),
        u_height: Number(uHeight) || 42,
      }),
    onSuccess: () => {
      setErr(null);
      setName("");
      void qc.invalidateQueries({ queryKey: ["dcim", "racks"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const racks = racksQ.data ?? [];

  return (
    <Panel title={t("nav.dcimRacks")}>
      <DcimInnerTabs
        tabs={[
          { id: "elevation", label: t("dcim.racks.tabElevation") },
          { id: "admin", label: t("dcim.racks.tabAdmin") },
        ]}
        activeId={rackTab}
        onChange={(id) => setRackTab(id as "elevation" | "admin")}
        ariaLabel={t("dcim.innerNavAria")}
      />
      {rackTab === "elevation" ? (
        <RackPlanner racks={racks} highlightPlacementId={highlightPlacementId} embed />
      ) : (
        <div className={styles.adminBody}>
          <h2 className={styles.srOnly}>{t("dcim.racks.adminSummary")}</h2>
          {err ? <p className={styles.err}>{err}</p> : null}
          <div className={styles.formRow}>
            <label>
              {t("dcim.racks.filterRoom")}
              <input
                type="number"
                min={1}
                value={roomFilter}
                onChange={(e) => setRoomFilter(e.target.value)}
                placeholder={t("dcim.common.all")}
              />
            </label>
          </div>
          <form
            className={styles.formRow}
            onSubmit={(e) => {
              e.preventDefault();
              setErr(null);
              if (!roomId) {
                setErr(t("dcim.racks.chooseRoom"));
                return;
              }
              m.mutate();
            }}
          >
            <label>
              {t("dcim.common.room")}
              <select value={roomId} onChange={(e) => setRoomId(e.target.value)} required>
                <option value="">{t("dcim.common.choose")}</option>
                {(roomsQ.data ?? []).map((r) => (
                  <option key={r.id} value={String(r.id)}>
                    #{r.id} — {r.name} (site {r.site_id})
                  </option>
                ))}
              </select>
            </label>
            <label>
              {t("dcim.racks.rackName")}
              <input value={name} onChange={(e) => setName(e.target.value)} required />
            </label>
            <label>
              {t("dcim.racks.uHeight")}
              <input
                type="number"
                min={1}
                max={64}
                value={uHeight}
                onChange={(e) => setUHeight(e.target.value)}
              />
            </label>
            <button type="submit" className={styles.btn} disabled={m.isPending || roomsQ.isLoading}>
              {m.isPending ? t("dcim.common.creating") : t("dcim.racks.create")}
            </button>
          </form>
          {racksQ.isError ? (
            <p className={styles.err}>
              {t("dcim.racks.loadError")} {(racksQ.error as Error).message}
            </p>
          ) : null}
          {racksQ.isLoading ? <p className={styles.muted}>{t("dcim.common.loading")}</p> : null}
          {racksQ.data && racksQ.data.length === 0 ? <p className={styles.muted}>{t("dcim.racks.empty")}</p> : null}
          {racksQ.data && racksQ.data.length > 0 ? (
            <table className={styles.table}>
              <thead>
                <tr>
                  <th>{t("dcim.common.id")}</th>
                  <th>{t("dcim.racks.tableRoom")}</th>
                  <th>{t("dcim.common.name")}</th>
                  <th>{t("dcim.racks.uHeight")}</th>
                </tr>
              </thead>
              <tbody>
                {racksQ.data.map((k) => (
                  <tr key={k.id}>
                    <td>{k.id}</td>
                    <td>{k.room_id}</td>
                    <td>{k.name}</td>
                    <td>{k.u_height}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : null}
        </div>
      )}
    </Panel>
  );
}
