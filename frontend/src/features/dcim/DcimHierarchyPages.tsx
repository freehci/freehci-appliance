import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { ConfirmModal } from "@/components/ui/ConfirmModal";
import { Panel } from "@/components/ui/Panel";
import { useI18n } from "@/i18n/I18nProvider";
import { ApiError } from "@/lib/api";
import * as api from "./dcimApi";
import { asList, dcimKeys } from "./dcimQuery";
import type { Room } from "./types";
import styles from "./dcim.module.css";

function crumb(to: string, label: string) {
  return (
    <Link to={to} className={styles.tableLink}>
      {label}
    </Link>
  );
}

function RoomTable({
  rooms,
  empty,
}: {
  rooms: Room[] | Room | undefined;
  empty: string;
}) {
  const { t } = useI18n();
  const rows = asList(rooms);
  if (rooms == null) return <p className={styles.muted}>{t("dcim.common.loading")}</p>;
  if (rows.length === 0) return <p className={styles.muted}>{empty}</p>;
  return (
    <table className={styles.table}>
      <thead>
        <tr>
          <th>{t("dcim.common.name")}</th>
          <th>{t("dcim.rooms.floor")}</th>
        </tr>
      </thead>
      <tbody>
        {rows.map((r) => (
          <tr key={r.id}>
            <td>
              <Link to={`/dcim/rooms/${r.id}`} className={styles.tableLink}>
                {r.name}
              </Link>
            </td>
            <td>{r.floor ?? "—"}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export function DcimBuildingDetailPage() {
  const { t } = useI18n();
  const qc = useQueryClient();
  const navigate = useNavigate();
  const { siteId: siteParam, buildingId: buildingParam } = useParams<{
    siteId: string;
    buildingId: string;
  }>();
  const siteId = Number(siteParam);
  const buildingId = Number(buildingParam);
  const [err, setErr] = useState<string | null>(null);
  const [wingName, setWingName] = useState("");
  const [wingSlug, setWingSlug] = useState("");
  const [floorName, setFloorName] = useState("");
  const [floorSlug, setFloorSlug] = useState("");
  const [floorLevel, setFloorLevel] = useState("0");
  const [floorWingId, setFloorWingId] = useState("");
  const [deleteOpen, setDeleteOpen] = useState(false);

  const ok = Number.isFinite(siteId) && siteId > 0 && Number.isFinite(buildingId) && buildingId > 0;
  const siteQ = useQuery({ queryKey: dcimKeys.site(siteId), queryFn: () => api.getSite(siteId), enabled: ok });
  const buildingQ = useQuery({
    queryKey: dcimKeys.building(buildingId),
    queryFn: () => api.getBuilding(buildingId),
    enabled: ok,
  });
  const wingsQ = useQuery({
    queryKey: dcimKeys.wings(buildingId),
    queryFn: () => api.listWings(buildingId),
    enabled: ok,
  });
  const floorsQ = useQuery({
    queryKey: dcimKeys.floors({ buildingId }),
    queryFn: () => api.listFloors({ buildingId }),
    enabled: ok,
  });
  const roomsQ = useQuery({
    queryKey: dcimKeys.roomsByBuilding(buildingId),
    queryFn: () => api.listRooms(undefined, { buildingId }),
    enabled: ok,
  });

  const roomsWithoutFloor = useMemo(
    () => asList(roomsQ.data).filter((r) => r.floor_id == null),
    [roomsQ.data],
  );

  const createWing = useMutation({
    mutationFn: () =>
      api.createWing({
        building_id: buildingId,
        name: wingName.trim(),
        slug: wingSlug.trim().toLowerCase(),
      }),
    onSuccess: () => {
      setErr(null);
      setWingName("");
      setWingSlug("");
      void qc.invalidateQueries({ queryKey: ["dcim", "wings"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const createFloor = useMutation({
    mutationFn: () =>
      api.createFloor({
        building_id: buildingId,
        name: floorName.trim(),
        slug: floorSlug.trim().toLowerCase(),
        level: Number(floorLevel) || 0,
        wing_id: floorWingId === "" ? null : Number(floorWingId),
      }),
    onSuccess: () => {
      setErr(null);
      setFloorName("");
      setFloorSlug("");
      setFloorLevel("0");
      setFloorWingId("");
      void qc.invalidateQueries({ queryKey: ["dcim", "floors"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const del = useMutation({
    mutationFn: () => api.deleteBuilding(buildingId),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ["dcim", "buildings"] });
      void navigate(`/dcim/sites/${siteId}`);
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  if (!ok) {
    return (
      <Panel title={t("dcim.common.building")}>
        <p className={styles.err}>{t("dcim.buildings.invalidId")}</p>
      </Panel>
    );
  }
  if (buildingQ.isError || siteQ.isError) {
    return (
      <Panel title={t("dcim.common.building")}>
        <p className={styles.err}>{(buildingQ.error as Error | undefined)?.message ?? (siteQ.error as Error).message}</p>
      </Panel>
    );
  }
  if (buildingQ.isLoading || !buildingQ.data || !siteQ.data) {
    return (
      <Panel title={t("dcim.common.building")}>
        <p className={styles.muted}>{t("dcim.common.loading")}</p>
      </Panel>
    );
  }

  const b = buildingQ.data;
  const site = siteQ.data;

  return (
    <>
      <p className={styles.mfrDetailBack}>
        {crumb("/dcim/sites", t("nav.dcimSites"))}
        {" / "}
        {crumb(`/dcim/sites/${site.id}`, site.name)}
        {" / "}
        <span>{b.name}</span>
      </p>
      <Panel title={b.name}>
        {err ? <p className={styles.err}>{err}</p> : null}

        <section className={styles.mfrDetailSection}>
          <h3 className={styles.mfrDetailSectionTitle}>{t("dcim.buildings.wingsTitle")}</h3>
          <form
            className={styles.formRow}
            onSubmit={(e) => {
              e.preventDefault();
              setErr(null);
              createWing.mutate();
            }}
          >
            <label>
              {t("dcim.common.name")}
              <input value={wingName} onChange={(e) => setWingName(e.target.value)} required />
            </label>
            <label>
              {t("dcim.common.slug")}
              <input
                value={wingSlug}
                onChange={(e) => setWingSlug(e.target.value)}
                placeholder={t("dcim.wings.slugPh")}
                required
                pattern="[a-z0-9]+(?:-[a-z0-9]+)*"
              />
            </label>
            <button type="submit" className={styles.btn} disabled={createWing.isPending}>
              {createWing.isPending ? t("dcim.common.creating") : t("dcim.wings.create")}
            </button>
          </form>
          {asList(wingsQ.data).length === 0 ? <p className={styles.muted}>{t("dcim.wings.empty")}</p> : null}
          {asList(wingsQ.data).length > 0 ? (
            <table className={styles.table}>
              <thead>
                <tr>
                  <th>{t("dcim.common.name")}</th>
                  <th>{t("dcim.common.slug")}</th>
                </tr>
              </thead>
              <tbody>
                {asList(wingsQ.data).map((w) => (
                  <tr key={w.id}>
                    <td>
                      <Link
                        to={`/dcim/sites/${site.id}/buildings/${b.id}/wings/${w.id}`}
                        className={styles.tableLink}
                      >
                        {w.name}
                      </Link>
                    </td>
                    <td>{w.slug}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : null}
        </section>

        <section className={styles.mfrDetailSection}>
          <h3 className={styles.mfrDetailSectionTitle}>{t("dcim.buildings.floorsTitle")}</h3>
          <form
            className={styles.formRow}
            onSubmit={(e) => {
              e.preventDefault();
              setErr(null);
              createFloor.mutate();
            }}
          >
            <label>
              {t("dcim.common.name")}
              <input value={floorName} onChange={(e) => setFloorName(e.target.value)} required />
            </label>
            <label>
              {t("dcim.common.slug")}
              <input
                value={floorSlug}
                onChange={(e) => setFloorSlug(e.target.value)}
                placeholder={t("dcim.floors.slugPh")}
                required
                pattern="[a-z0-9]+(?:-[a-z0-9]+)*"
              />
            </label>
            <label>
              {t("dcim.common.level")}
              <input value={floorLevel} onChange={(e) => setFloorLevel(e.target.value)} placeholder={t("dcim.floors.levelPh")} />
            </label>
            <label>
              {t("dcim.floors.optionalWing")}
              <select value={floorWingId} onChange={(e) => setFloorWingId(e.target.value)}>
                <option value="">{t("dcim.common.skip")}</option>
                {asList(wingsQ.data).map((w) => (
                  <option key={w.id} value={String(w.id)}>
                    {w.name}
                  </option>
                ))}
              </select>
            </label>
            <button type="submit" className={styles.btn} disabled={createFloor.isPending}>
              {createFloor.isPending ? t("dcim.common.creating") : t("dcim.floors.create")}
            </button>
          </form>
          {asList(floorsQ.data).length === 0 ? <p className={styles.muted}>{t("dcim.floors.empty")}</p> : null}
          {asList(floorsQ.data).length > 0 ? (
            <table className={styles.table}>
              <thead>
                <tr>
                  <th>{t("dcim.common.level")}</th>
                  <th>{t("dcim.common.name")}</th>
                  <th>{t("dcim.common.wing")}</th>
                </tr>
              </thead>
              <tbody>
                {asList(floorsQ.data).map((f) => (
                  <tr key={f.id}>
                    <td>{f.level}</td>
                    <td>
                      <Link
                        to={`/dcim/sites/${site.id}/buildings/${b.id}/floors/${f.id}`}
                        className={styles.tableLink}
                      >
                        {f.name}
                      </Link>
                    </td>
                    <td>{asList(wingsQ.data).find((w) => w.id === f.wing_id)?.name ?? "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : null}
        </section>

        <section className={styles.mfrDetailSection}>
          <h3 className={styles.mfrDetailSectionTitle}>{t("dcim.buildings.roomsWithoutFloor")}</h3>
          <RoomTable rooms={roomsWithoutFloor} empty={t("dcim.rooms.empty")} />
        </section>

        <p className={styles.muted}>{t("dcim.buildings.deleteHint")}</p>
        <button type="button" className={styles.btnMuted} onClick={() => setDeleteOpen(true)}>
          {t("dcim.common.delete")}
        </button>
      </Panel>
      <ConfirmModal
        open={deleteOpen}
        onClose={() => {
          if (!del.isPending) setDeleteOpen(false);
        }}
        title={t("dcim.buildings.deleteModalTitle", { name: b.name })}
        message={t("dcim.buildings.deleteModalHint")}
        confirmLabel={t("dcim.common.delete")}
        cancelLabel={t("dcim.common.cancel")}
        danger
        pending={del.isPending}
        onConfirm={() => del.mutate()}
      />
    </>
  );
}

export function DcimWingDetailPage() {
  const { t } = useI18n();
  const qc = useQueryClient();
  const navigate = useNavigate();
  const { siteId: siteParam, buildingId: buildingParam, wingId: wingParam } = useParams<{
    siteId: string;
    buildingId: string;
    wingId: string;
  }>();
  const siteId = Number(siteParam);
  const buildingId = Number(buildingParam);
  const wingId = Number(wingParam);
  const [err, setErr] = useState<string | null>(null);
  const [floorName, setFloorName] = useState("");
  const [floorSlug, setFloorSlug] = useState("");
  const [floorLevel, setFloorLevel] = useState("0");
  const [deleteOpen, setDeleteOpen] = useState(false);
  const ok =
    Number.isFinite(siteId) &&
    siteId > 0 &&
    Number.isFinite(buildingId) &&
    buildingId > 0 &&
    Number.isFinite(wingId) &&
    wingId > 0;

  const siteQ = useQuery({ queryKey: dcimKeys.site(siteId), queryFn: () => api.getSite(siteId), enabled: ok });
  const buildingQ = useQuery({
    queryKey: dcimKeys.building(buildingId),
    queryFn: () => api.getBuilding(buildingId),
    enabled: ok,
  });
  const wingQ = useQuery({ queryKey: dcimKeys.wing(wingId), queryFn: () => api.getWing(wingId), enabled: ok });
  const floorsQ = useQuery({
    queryKey: dcimKeys.floors({ buildingId, wingId }),
    queryFn: () => api.listFloors({ buildingId, wingId }),
    enabled: ok,
  });
  const roomsQ = useQuery({
    queryKey: dcimKeys.roomsByWing(wingId),
    queryFn: () => api.listRooms(undefined, { wingId }),
    enabled: ok,
  });
  const roomsWithoutFloor = useMemo(
    () => asList(roomsQ.data).filter((r) => r.floor_id == null),
    [roomsQ.data],
  );

  const createFloor = useMutation({
    mutationFn: () =>
      api.createFloor({
        building_id: buildingId,
        wing_id: wingId,
        name: floorName.trim(),
        slug: floorSlug.trim().toLowerCase(),
        level: Number(floorLevel) || 0,
      }),
    onSuccess: () => {
      setErr(null);
      setFloorName("");
      setFloorSlug("");
      setFloorLevel("0");
      void qc.invalidateQueries({ queryKey: ["dcim", "floors"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const del = useMutation({
    mutationFn: () => api.deleteWing(wingId),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ["dcim", "wings"] });
      void navigate(`/dcim/sites/${siteId}/buildings/${buildingId}`);
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  if (!ok) {
    return (
      <Panel title={t("dcim.common.wing")}>
        <p className={styles.err}>{t("dcim.wings.invalidId")}</p>
      </Panel>
    );
  }
  if (wingQ.isLoading || !wingQ.data || !siteQ.data || !buildingQ.data) {
    return (
      <Panel title={t("dcim.common.wing")}>
        <p className={styles.muted}>{t("dcim.common.loading")}</p>
      </Panel>
    );
  }
  if (wingQ.isError) {
    return (
      <Panel title={t("dcim.common.wing")}>
        <p className={styles.err}>{(wingQ.error as Error).message}</p>
      </Panel>
    );
  }

  const w = wingQ.data;
  const b = buildingQ.data;
  const site = siteQ.data;

  return (
    <>
      <p className={styles.mfrDetailBack}>
        {crumb("/dcim/sites", t("nav.dcimSites"))}
        {" / "}
        {crumb(`/dcim/sites/${site.id}`, site.name)}
        {" / "}
        {crumb(`/dcim/sites/${site.id}/buildings/${b.id}`, b.name)}
        {" / "}
        <span>{w.name}</span>
      </p>
      <Panel title={w.name}>
        {err ? <p className={styles.err}>{err}</p> : null}
        <section className={styles.mfrDetailSection}>
          <h3 className={styles.mfrDetailSectionTitle}>{t("dcim.wings.floorsTitle")}</h3>
          <form
            className={styles.formRow}
            onSubmit={(e) => {
              e.preventDefault();
              setErr(null);
              createFloor.mutate();
            }}
          >
            <label>
              {t("dcim.common.name")}
              <input value={floorName} onChange={(e) => setFloorName(e.target.value)} required />
            </label>
            <label>
              {t("dcim.common.slug")}
              <input
                value={floorSlug}
                onChange={(e) => setFloorSlug(e.target.value)}
                placeholder={t("dcim.floors.slugPh")}
                required
                pattern="[a-z0-9]+(?:-[a-z0-9]+)*"
              />
            </label>
            <label>
              {t("dcim.common.level")}
              <input value={floorLevel} onChange={(e) => setFloorLevel(e.target.value)} />
            </label>
            <button type="submit" className={styles.btn} disabled={createFloor.isPending}>
              {createFloor.isPending ? t("dcim.common.creating") : t("dcim.floors.create")}
            </button>
          </form>
          {asList(floorsQ.data).length === 0 ? <p className={styles.muted}>{t("dcim.floors.empty")}</p> : null}
          {asList(floorsQ.data).length > 0 ? (
            <table className={styles.table}>
              <thead>
                <tr>
                  <th>{t("dcim.common.level")}</th>
                  <th>{t("dcim.common.name")}</th>
                </tr>
              </thead>
              <tbody>
                {asList(floorsQ.data).map((f) => (
                  <tr key={f.id}>
                    <td>{f.level}</td>
                    <td>
                      <Link
                        to={`/dcim/sites/${site.id}/buildings/${b.id}/floors/${f.id}`}
                        className={styles.tableLink}
                      >
                        {f.name}
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : null}
        </section>
        <section className={styles.mfrDetailSection}>
          <h3 className={styles.mfrDetailSectionTitle}>{t("dcim.wings.roomsWithoutFloor")}</h3>
          <RoomTable rooms={roomsWithoutFloor} empty={t("dcim.rooms.empty")} />
        </section>
        <p className={styles.muted}>{t("dcim.wings.deleteHint")}</p>
        <button type="button" className={styles.btnMuted} onClick={() => setDeleteOpen(true)}>
          {t("dcim.common.delete")}
        </button>
      </Panel>
      <ConfirmModal
        open={deleteOpen}
        onClose={() => {
          if (!del.isPending) setDeleteOpen(false);
        }}
        title={t("dcim.wings.deleteModalTitle", { name: w.name })}
        message={t("dcim.wings.deleteModalHint")}
        confirmLabel={t("dcim.common.delete")}
        cancelLabel={t("dcim.common.cancel")}
        danger
        pending={del.isPending}
        onConfirm={() => del.mutate()}
      />
    </>
  );
}

export function DcimFloorDetailPage() {
  const { t } = useI18n();
  const qc = useQueryClient();
  const navigate = useNavigate();
  const { siteId: siteParam, buildingId: buildingParam, floorId: floorParam } = useParams<{
    siteId: string;
    buildingId: string;
    floorId: string;
  }>();
  const siteId = Number(siteParam);
  const buildingId = Number(buildingParam);
  const floorId = Number(floorParam);
  const [err, setErr] = useState<string | null>(null);
  const [roomName, setRoomName] = useState("");
  const [deleteOpen, setDeleteOpen] = useState(false);
  const ok =
    Number.isFinite(siteId) &&
    siteId > 0 &&
    Number.isFinite(buildingId) &&
    buildingId > 0 &&
    Number.isFinite(floorId) &&
    floorId > 0;

  const siteQ = useQuery({ queryKey: dcimKeys.site(siteId), queryFn: () => api.getSite(siteId), enabled: ok });
  const buildingQ = useQuery({
    queryKey: dcimKeys.building(buildingId),
    queryFn: () => api.getBuilding(buildingId),
    enabled: ok,
  });
  const floorQ = useQuery({ queryKey: dcimKeys.floor(floorId), queryFn: () => api.getFloor(floorId), enabled: ok });
  const roomsQ = useQuery({
    queryKey: dcimKeys.roomsByFloor(floorId),
    queryFn: () => api.listRooms(undefined, { floorId }),
    enabled: ok,
  });

  const createRoom = useMutation({
    mutationFn: () =>
      api.createRoom({
        site_id: siteId,
        name: roomName.trim(),
        floor_id: floorId,
      }),
    onSuccess: () => {
      setErr(null);
      setRoomName("");
      void qc.invalidateQueries({ queryKey: ["dcim", "rooms"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const del = useMutation({
    mutationFn: () => api.deleteFloor(floorId),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ["dcim", "floors"] });
      void navigate(`/dcim/sites/${siteId}/buildings/${buildingId}`);
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  if (!ok) {
    return (
      <Panel title={t("dcim.common.floor")}>
        <p className={styles.err}>{t("dcim.floors.invalidId")}</p>
      </Panel>
    );
  }
  if (floorQ.isLoading || !floorQ.data || !siteQ.data || !buildingQ.data) {
    return (
      <Panel title={t("dcim.common.floor")}>
        <p className={styles.muted}>{t("dcim.common.loading")}</p>
      </Panel>
    );
  }
  if (floorQ.isError) {
    return (
      <Panel title={t("dcim.common.floor")}>
        <p className={styles.err}>{(floorQ.error as Error).message}</p>
      </Panel>
    );
  }

  const f = floorQ.data;
  const b = buildingQ.data;
  const site = siteQ.data;

  return (
    <>
      <p className={styles.mfrDetailBack}>
        {crumb("/dcim/sites", t("nav.dcimSites"))}
        {" / "}
        {crumb(`/dcim/sites/${site.id}`, site.name)}
        {" / "}
        {crumb(`/dcim/sites/${site.id}/buildings/${b.id}`, b.name)}
        {" / "}
        <span>{f.name}</span>
      </p>
      <Panel title={f.name}>
        {err ? <p className={styles.err}>{err}</p> : null}
        <section className={styles.mfrDetailSection}>
          <h3 className={styles.mfrDetailSectionTitle}>{t("dcim.floors.roomsTitle")}</h3>
          <form
            className={styles.formRow}
            onSubmit={(e) => {
              e.preventDefault();
              setErr(null);
              createRoom.mutate();
            }}
          >
            <label>
              {t("dcim.rooms.roomName")}
              <input value={roomName} onChange={(e) => setRoomName(e.target.value)} required />
            </label>
            <button type="submit" className={styles.btn} disabled={createRoom.isPending}>
              {createRoom.isPending ? t("dcim.common.creating") : t("dcim.rooms.create")}
            </button>
          </form>
          <RoomTable rooms={roomsQ.data} empty={t("dcim.rooms.empty")} />
        </section>
        <p className={styles.muted}>{t("dcim.floors.deleteHint")}</p>
        <button type="button" className={styles.btnMuted} onClick={() => setDeleteOpen(true)}>
          {t("dcim.common.delete")}
        </button>
      </Panel>
      <ConfirmModal
        open={deleteOpen}
        onClose={() => {
          if (!del.isPending) setDeleteOpen(false);
        }}
        title={t("dcim.floors.deleteModalTitle", { name: f.name })}
        message={t("dcim.floors.deleteModalHint")}
        confirmLabel={t("dcim.common.delete")}
        cancelLabel={t("dcim.common.cancel")}
        danger
        pending={del.isPending}
        onConfirm={() => del.mutate()}
      />
    </>
  );
}
