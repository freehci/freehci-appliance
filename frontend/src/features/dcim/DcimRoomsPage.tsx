import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { Panel } from "@/components/ui/Panel";
import { useI18n } from "@/i18n/I18nProvider";
import { ApiError } from "@/lib/api";
import * as api from "./dcimApi";
import { asList, dcimKeys } from "./dcimQuery";
import { DcimInnerTabs } from "./DcimInnerTabs";
import { DcimRoomLocationFields, optionalId, type RoomLocationValue } from "./DcimRoomLocationFields";
import styles from "./dcim.module.css";

export function DcimRoomsPage() {
  const { t } = useI18n();
  const qc = useQueryClient();
  const [siteFilter, setSiteFilter] = useState<string>("");
  const [loc, setLoc] = useState<RoomLocationValue>({
    siteId: "",
    buildingId: "",
    wingId: "",
    floorId: "",
  });
  const [name, setName] = useState("");
  const [err, setErr] = useState<string | null>(null);
  const [tab, setTab] = useState("main");

  const sitesQ = useQuery({ queryKey: ["dcim", "sites"], queryFn: api.listSites });
  const buildingsQ = useQuery({ queryKey: dcimKeys.buildings(), queryFn: () => api.listBuildings() });
  const wingsQ = useQuery({ queryKey: dcimKeys.wings(), queryFn: () => api.listWings() });
  const filterNum = useMemo(() => {
    const n = Number(siteFilter);
    return Number.isFinite(n) && n > 0 ? n : undefined;
  }, [siteFilter]);

  const sitesById = useMemo(() => {
    const m = new Map<number, string>();
    for (const s of sitesQ.data ?? []) m.set(s.id, s.name);
    return m;
  }, [sitesQ.data]);
  const buildingsById = useMemo(() => {
    const m = new Map<number, string>();
    for (const b of asList(buildingsQ.data)) m.set(b.id, b.name);
    return m;
  }, [buildingsQ.data]);
  const wingsById = useMemo(() => {
    const m = new Map<number, string>();
    for (const w of asList(wingsQ.data)) m.set(w.id, w.name);
    return m;
  }, [wingsQ.data]);

  const roomsQ = useQuery({
    queryKey: dcimKeys.rooms(filterNum),
    queryFn: () => api.listRooms(filterNum),
  });

  const m = useMutation({
    mutationFn: () =>
      api.createRoom({
        site_id: Number(loc.siteId),
        name: name.trim(),
        building_id: optionalId(loc.buildingId),
        wing_id: optionalId(loc.wingId),
        floor_id: optionalId(loc.floorId),
      }),
    onSuccess: () => {
      setErr(null);
      setName("");
      void qc.invalidateQueries({ queryKey: ["dcim", "rooms"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  return (
    <Panel title={t("nav.dcimRooms")}>
      <DcimInnerTabs
        tabs={[{ id: "main", label: t("nav.dcimRooms"), icon: "rooms" }]}
        activeId={tab}
        onChange={setTab}
        ariaLabel={t("dcim.innerNavAria")}
      />
      {tab === "main" ? (
        <>
          {err ? <p className={styles.err}>{err}</p> : null}
          <div className={styles.formRow}>
            <label>
              {t("dcim.rooms.filterSite")}
              <input
                type="number"
                min={1}
                value={siteFilter}
                onChange={(e) => setSiteFilter(e.target.value)}
                placeholder={t("dcim.common.all")}
              />
            </label>
          </div>
          <form
            className={styles.formRow}
            onSubmit={(e) => {
              e.preventDefault();
              setErr(null);
              if (!loc.siteId) {
                setErr(t("dcim.rooms.chooseSite"));
                return;
              }
              m.mutate();
            }}
          >
            <DcimRoomLocationFields value={loc} onChange={setLoc} />
            <label>
              {t("dcim.rooms.roomName")}
              <input value={name} onChange={(e) => setName(e.target.value)} required />
            </label>
            <button type="submit" className={styles.btn} disabled={m.isPending || sitesQ.isLoading}>
              {m.isPending ? t("dcim.common.creating") : t("dcim.rooms.create")}
            </button>
          </form>
          {roomsQ.isError ? (
            <p className={styles.err}>
              {t("dcim.rooms.loadError")} {(roomsQ.error as Error).message}
            </p>
          ) : null}
          {roomsQ.isLoading ? <p className={styles.muted}>{t("dcim.common.loading")}</p> : null}
          {roomsQ.data && asList(roomsQ.data).length === 0 ? <p className={styles.muted}>{t("dcim.rooms.empty")}</p> : null}
          {asList(roomsQ.data).length > 0 ? (
            <table className={styles.table}>
              <thead>
                <tr>
                  <th>{t("dcim.rooms.tableSite")}</th>
                  <th>{t("dcim.rooms.tableBuilding")}</th>
                  <th>{t("dcim.rooms.tableWing")}</th>
                  <th>{t("dcim.rooms.floor")}</th>
                  <th>{t("dcim.common.name")}</th>
                </tr>
              </thead>
              <tbody>
                {asList(roomsQ.data).map((r) => (
                  <tr key={r.id}>
                    <td>{sitesById.get(r.site_id) ?? `#${r.site_id}`}</td>
                    <td>{r.building_id != null ? (buildingsById.get(r.building_id) ?? `#${r.building_id}`) : "—"}</td>
                    <td>{r.wing_id != null ? (wingsById.get(r.wing_id) ?? `#${r.wing_id}`) : "—"}</td>
                    <td>{r.floor ?? "—"}</td>
                    <td>
                      <Link to={`/dcim/rooms/${r.id}`} className={styles.tableLink}>
                        {r.name}
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : null}
        </>
      ) : null}
    </Panel>
  );
}
