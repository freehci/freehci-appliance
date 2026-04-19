import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useRef, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { ConfirmModal } from "@/components/ui/ConfirmModal";
import { Panel } from "@/components/ui/Panel";
import { useI18n } from "@/i18n/I18nProvider";
import { ApiError } from "@/lib/api";
import * as api from "./dcimApi";
import { DcimInnerTabs } from "./DcimInnerTabs";
import styles from "./dcim.module.css";

type RoomTab = "overview" | "floorplan";

export function DcimRoomDetailPage() {
  const { t } = useI18n();
  const qc = useQueryClient();
  const navigate = useNavigate();
  const { roomId: roomIdParam } = useParams<{ roomId: string }>();
  const id = Number(roomIdParam);
  const fileRef = useRef<HTMLInputElement | null>(null);

  const [err, setErr] = useState<string | null>(null);
  const [tab, setTab] = useState<RoomTab>("overview");
  const [name, setName] = useState("");
  const [siteId, setSiteId] = useState("");
  const [floor, setFloor] = useState("");
  const [description, setDescription] = useState("");
  const [planVersion, setPlanVersion] = useState("");
  const [floorplanImgUrl, setFloorplanImgUrl] = useState<string | null>(null);
  const [deleteOpen, setDeleteOpen] = useState(false);
  const hydrated = useRef(false);

  const roomQ = useQuery({
    queryKey: ["dcim", "rooms", id],
    queryFn: () => api.getRoom(id),
    enabled: Number.isFinite(id) && id > 0,
  });
  const sitesQ = useQuery({ queryKey: ["dcim", "sites"], queryFn: api.listSites });
  const racksQ = useQuery({
    queryKey: ["dcim", "racks", "room", id],
    queryFn: () => api.listRacks(id),
    enabled: Number.isFinite(id) && id > 0,
  });

  const ro = roomQ.data;

  useEffect(() => {
    hydrated.current = false;
  }, [id]);

  useEffect(() => {
    if (!ro || hydrated.current) return;
    setName(ro.name);
    setSiteId(String(ro.site_id));
    setFloor(ro.floor ?? "");
    setDescription(ro.description ?? "");
    if (ro.has_floorplan) setPlanVersion(String(Date.now()));
    hydrated.current = true;
  }, [ro]);

  useEffect(() => {
    if (!ro?.has_floorplan) {
      setFloorplanImgUrl((prev) => {
        if (prev) URL.revokeObjectURL(prev);
        return null;
      });
      return;
    }
    let cancelled = false;
    void api
      .fetchRoomFloorplanBlobUrl(id, planVersion)
      .then((url) => {
        if (cancelled) {
          URL.revokeObjectURL(url);
          return;
        }
        setFloorplanImgUrl((prev) => {
          if (prev) URL.revokeObjectURL(prev);
          return url;
        });
      })
      .catch((e: unknown) => {
        if (!cancelled) {
          setErr(e instanceof ApiError ? e.message : e instanceof Error ? e.message : String(e));
          setFloorplanImgUrl((prev) => {
            if (prev) URL.revokeObjectURL(prev);
            return null;
          });
        }
      });
    return () => {
      cancelled = true;
      setFloorplanImgUrl((prev) => {
        if (prev) URL.revokeObjectURL(prev);
        return null;
      });
    };
  }, [id, ro?.has_floorplan, planVersion]);

  const saveMu = useMutation({
    mutationFn: () =>
      api.updateRoom(id, {
        site_id: siteId === "" ? undefined : Number(siteId),
        name: name.trim(),
        floor: floor.trim() === "" ? null : floor.trim(),
        description: description.trim() === "" ? null : description.trim(),
      }),
    onSuccess: () => {
      setErr(null);
      void qc.invalidateQueries({ queryKey: ["dcim", "rooms"] });
      void qc.invalidateQueries({ queryKey: ["dcim", "rooms", id] });
      void qc.invalidateQueries({ queryKey: ["dcim", "racks"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const uploadPlanMu = useMutation({
    mutationFn: (file: File) => api.uploadRoomFloorplan(id, file),
    onSuccess: () => {
      setErr(null);
      setPlanVersion(String(Date.now()));
      void qc.invalidateQueries({ queryKey: ["dcim", "rooms"] });
      void qc.invalidateQueries({ queryKey: ["dcim", "rooms", id] });
      if (fileRef.current) fileRef.current.value = "";
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const removePlanMu = useMutation({
    mutationFn: () => api.deleteRoomFloorplan(id),
    onSuccess: () => {
      setErr(null);
      setPlanVersion("");
      void qc.invalidateQueries({ queryKey: ["dcim", "rooms"] });
      void qc.invalidateQueries({ queryKey: ["dcim", "rooms", id] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const deleteMu = useMutation({
    mutationFn: () => api.deleteRoom(id),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ["dcim", "rooms"] });
      void qc.invalidateQueries({ queryKey: ["dcim", "racks"] });
      void navigate("/dcim/rooms");
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  if (!Number.isFinite(id) || id < 1) {
    return (
      <Panel title={t("dcim.rooms.detailTitle")}>
        <p className={styles.err}>{t("dcim.rooms.invalidId")}</p>
        <Link to="/dcim/rooms" className={styles.tableLink}>
          {t("dcim.rooms.backToList")}
        </Link>
      </Panel>
    );
  }

  if (roomQ.isError) {
    return (
      <Panel title={t("dcim.rooms.detailTitle")}>
        <p className={styles.err}>{(roomQ.error as Error).message}</p>
        <Link to="/dcim/rooms" className={styles.tableLink}>
          {t("dcim.rooms.backToList")}
        </Link>
      </Panel>
    );
  }

  if (roomQ.isLoading || !ro) {
    return (
      <Panel title={t("dcim.rooms.detailTitle")}>
        <p className={styles.muted}>{t("dcim.common.loading")}</p>
      </Panel>
    );
  }

  return (
    <>
      <p className={styles.mfrDetailBack}>
        <Link to="/dcim/rooms" className={styles.tableLink}>
          ← {t("dcim.rooms.backToList")}
        </Link>
      </p>
      <Panel title={ro.name}>
        {err ? <p className={styles.err}>{err}</p> : null}
        <DcimInnerTabs
          tabs={[
            { id: "overview", label: t("dcim.rooms.tabOverview"), icon: "overview" },
            { id: "floorplan", label: t("dcim.rooms.tabFloorplan"), icon: "floorplan" },
          ]}
          activeId={tab}
          onChange={(tid) => setTab(tid as RoomTab)}
          ariaLabel={t("dcim.rooms.detailTabsAria")}
        />

        {tab === "overview" ? (
          <>
            <section className={styles.mfrDetailSection}>
              <h3 className={styles.mfrDetailSectionTitle}>{t("dcim.rooms.sectionProfile")}</h3>
              <form
                className={styles.formRow}
                style={{ flexDirection: "column", alignItems: "stretch", maxWidth: "40rem" }}
                onSubmit={(e) => {
                  e.preventDefault();
                  saveMu.mutate();
                }}
              >
                <label>
                  {t("dcim.common.site")}
                  <select value={siteId} onChange={(e) => setSiteId(e.target.value)} required>
                    {(sitesQ.data ?? []).map((s) => (
                      <option key={s.id} value={String(s.id)}>
                        {s.name} ({s.slug})
                      </option>
                    ))}
                  </select>
                </label>
                <label>
                  {t("dcim.common.name")}
                  <input value={name} onChange={(e) => setName(e.target.value)} required />
                </label>
                <label>
                  {t("dcim.rooms.floor")}
                  <input value={floor} onChange={(e) => setFloor(e.target.value)} placeholder={t("dcim.rooms.floorPlaceholder")} />
                </label>
                <label>
                  {t("dcim.equip.mfr.description")}
                  <textarea
                    rows={4}
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    className={styles.mfrTextarea}
                  />
                </label>
                <div>
                  <button type="submit" className={styles.btn} disabled={saveMu.isPending}>
                    {saveMu.isPending ? "…" : t("dcim.equip.mfr.save")}
                  </button>
                </div>
              </form>
            </section>

            <section className={styles.mfrDetailSection}>
              <h3 className={styles.mfrDetailSectionTitle}>{t("dcim.rooms.racksInRoom")}</h3>
              <p className={styles.muted} style={{ marginTop: 0 }}>
                <Link to={`/dcim/racks?room=${id}`} className={styles.tableLink}>
                  {t("dcim.rooms.openRacksView")}
                </Link>
              </p>
              {racksQ.isLoading ? <p className={styles.muted}>{t("dcim.common.loading")}</p> : null}
              {racksQ.data && racksQ.data.length > 0 ? (
                <table className={styles.table}>
                  <thead>
                    <tr>
                      <th>{t("dcim.common.name")}</th>
                      <th>{t("dcim.racks.uHeight")}</th>
                    </tr>
                  </thead>
                  <tbody>
                    {(racksQ.data ?? []).map((k) => (
                      <tr key={k.id}>
                        <td>
                          <Link to={`/dcim/racks?room=${id}`} className={styles.tableLink}>
                            {k.name}
                          </Link>
                        </td>
                        <td>{k.u_height}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              ) : !racksQ.isLoading ? (
                <p className={styles.muted}>{t("dcim.rooms.noRacks")}</p>
              ) : null}
            </section>

            <section className={styles.mfrDetailSection}>
              <h3 className={styles.mfrDetailSectionTitle}>{t("dcim.equip.mfr.dangerZone")}</h3>
              <p className={styles.muted} style={{ marginTop: 0 }}>
                {t("dcim.rooms.deleteHint")}
              </p>
              <button
                type="button"
                className={`${styles.tableIconBtn} ${styles.tableIconBtnDanger}`.trim()}
                title={t("dcim.common.delete")}
                aria-label={t("dcim.common.delete")}
                disabled={deleteMu.isPending}
                onClick={() => setDeleteOpen(true)}
              >
                <i className="fas fa-trash-can" aria-hidden />
              </button>
            </section>
          </>
        ) : null}

        {tab === "floorplan" ? (
          <section className={styles.mfrDetailSection}>
            <h3 className={styles.mfrDetailSectionTitle}>{t("dcim.rooms.floorplanTitle")}</h3>
            <p className={styles.muted} style={{ marginTop: 0 }}>
              {t("dcim.rooms.floorplanIntro")}
            </p>
            {ro.has_floorplan ? (
              floorplanImgUrl ? (
                <p style={{ marginTop: "var(--space-2)" }}>
                  <img
                    src={floorplanImgUrl}
                    alt=""
                    className={styles.mfrLogoThumb}
                    style={{ maxWidth: "100%", width: "auto", height: "auto", maxHeight: "28rem" }}
                  />
                </p>
              ) : (
                <p className={styles.muted} style={{ marginTop: "var(--space-2)" }}>
                  {t("dcim.common.loading")}
                </p>
              )
            ) : (
              <p className={styles.muted}>{t("dcim.rooms.floorplanEmpty")}</p>
            )}
            <div className={styles.formRow} style={{ marginTop: "var(--space-3)", flexWrap: "wrap" }}>
              <label>
                {t("dcim.rooms.floorplanUpload")}
                <input
                  ref={fileRef}
                  type="file"
                  accept="image/png,image/jpeg,image/webp,image/svg+xml"
                  onChange={(e) => {
                    const f = e.target.files?.[0];
                    if (f) {
                      setErr(null);
                      uploadPlanMu.mutate(f);
                    }
                  }}
                />
              </label>
              {ro.has_floorplan ? (
                <button
                  type="button"
                  className={styles.btn}
                  disabled={removePlanMu.isPending}
                  onClick={() => {
                    setErr(null);
                    removePlanMu.mutate();
                  }}
                >
                  {removePlanMu.isPending ? "…" : t("dcim.rooms.floorplanRemove")}
                </button>
              ) : null}
            </div>
            <p className={styles.muted} style={{ marginTop: "var(--space-2)" }}>
              {t("dcim.rooms.floorplanFuture")}
            </p>
          </section>
        ) : null}
      </Panel>

      <ConfirmModal
        open={deleteOpen}
        onClose={() => {
          if (!deleteMu.isPending) setDeleteOpen(false);
        }}
        title={t("dcim.rooms.deleteModalTitle", { name: ro.name })}
        message={t("dcim.rooms.deleteModalHint")}
        confirmLabel={t("dcim.common.delete")}
        cancelLabel={t("dcim.common.cancel")}
        danger
        pending={deleteMu.isPending}
        onConfirm={() => {
          deleteMu.mutate(undefined as void, { onSettled: () => setDeleteOpen(false) });
        }}
      />
    </>
  );
}
