import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { Panel } from "@/components/ui/Panel";
import { useI18n } from "@/i18n/I18nProvider";
import { ApiError } from "@/lib/api";
import * as api from "./dcimApi";
import { DcimInnerTabs } from "./DcimInnerTabs";
import styles from "./dcim.module.css";

export function DcimRoomsPage() {
  const { t } = useI18n();
  const qc = useQueryClient();
  const [siteFilter, setSiteFilter] = useState<string>("");
  const [siteId, setSiteId] = useState<string>("");
  const [name, setName] = useState("");
  const [floorNew, setFloorNew] = useState("");
  const [err, setErr] = useState<string | null>(null);
  const [tab, setTab] = useState("main");

  const sitesQ = useQuery({ queryKey: ["dcim", "sites"], queryFn: api.listSites });
  const filterNum = useMemo(() => {
    const n = Number(siteFilter);
    return Number.isFinite(n) && n > 0 ? n : undefined;
  }, [siteFilter]);

  const sitesById = useMemo(() => {
    const m = new Map<number, string>();
    for (const s of sitesQ.data ?? []) m.set(s.id, s.name);
    return m;
  }, [sitesQ.data]);

  const roomsQ = useQuery({
    queryKey: ["dcim", "rooms", filterNum ?? "all"],
    queryFn: () => api.listRooms(filterNum),
  });

  const m = useMutation({
    mutationFn: () =>
      api.createRoom({
        site_id: Number(siteId),
        name: name.trim(),
        floor: floorNew.trim() === "" ? undefined : floorNew.trim(),
      }),
    onSuccess: () => {
      setErr(null);
      setName("");
      setFloorNew("");
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
              if (!siteId) {
                setErr(t("dcim.rooms.chooseSite"));
                return;
              }
              m.mutate();
            }}
          >
            <label>
              {t("dcim.common.site")}
              <select value={siteId} onChange={(e) => setSiteId(e.target.value)} required>
                <option value="">{t("dcim.common.choose")}</option>
                {(sitesQ.data ?? []).map((s) => (
                  <option key={s.id} value={String(s.id)}>
                    {s.name} ({s.slug})
                  </option>
                ))}
              </select>
            </label>
            <label>
              {t("dcim.rooms.roomName")}
              <input value={name} onChange={(e) => setName(e.target.value)} required />
            </label>
            <label>
              {t("dcim.rooms.floor")}
              <input value={floorNew} onChange={(e) => setFloorNew(e.target.value)} placeholder={t("dcim.rooms.floorPlaceholder")} />
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
          {roomsQ.data && roomsQ.data.length === 0 ? <p className={styles.muted}>{t("dcim.rooms.empty")}</p> : null}
          {roomsQ.data && roomsQ.data.length > 0 ? (
            <table className={styles.table}>
              <thead>
                <tr>
                  <th>{t("dcim.rooms.tableSite")}</th>
                  <th>{t("dcim.rooms.floor")}</th>
                  <th>{t("dcim.common.name")}</th>
                </tr>
              </thead>
              <tbody>
                {roomsQ.data.map((r) => (
                  <tr key={r.id}>
                    <td>{sitesById.get(r.site_id) ?? `#${r.site_id}`}</td>
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
