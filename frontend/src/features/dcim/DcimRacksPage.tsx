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
import type { Rack } from "./types";

function formatDimsMm(k: Rack): string {
  const h = k.height_mm;
  const w = k.width_mm;
  const d = k.depth_mm;
  if (h == null && w == null && d == null) return "—";
  return `${h ?? "—"}×${w ?? "—"}×${d ?? "—"}`;
}

function parseMmInput(s: string): "empty" | "invalid" | number {
  const t = s.trim();
  if (!t) return "empty";
  const n = Number(t);
  if (!Number.isFinite(n) || n < 1 || n > 100_000) return "invalid";
  return Math.trunc(n);
}

function parseDateInput(s: string): "empty" | string {
  const t = s.trim();
  if (!t) return "empty";
  return t;
}

/** JSON-objekt til create (undefined = utelat) eller patch (undefined = ikke endre). */
function parseAttributesJson(
  raw: string,
  forPatch: boolean,
): { ok: true; value: Record<string, unknown> | null | undefined } | { ok: false } {
  const t = raw.trim();
  if (!t) return { ok: true, value: forPatch ? undefined : undefined };
  try {
    const v = JSON.parse(t) as unknown;
    if (v === null) return { ok: true, value: forPatch ? null : undefined };
    if (typeof v !== "object" || v === null || Array.isArray(v)) return { ok: false };
    return { ok: true, value: v as Record<string, unknown> };
  } catch {
    return { ok: false };
  }
}

type RackExtraForm = {
  heightMm: string;
  widthMm: string;
  depthMm: string;
  brand: string;
  purchaseDate: string;
  commissionedDate: string;
  notes: string;
  attributesJson: string;
};

const emptyExtra = (): RackExtraForm => ({
  heightMm: "",
  widthMm: "",
  depthMm: "",
  brand: "",
  purchaseDate: "",
  commissionedDate: "",
  notes: "",
  attributesJson: "",
});

function rackToExtra(k: Rack): RackExtraForm {
  return {
    heightMm: k.height_mm != null ? String(k.height_mm) : "",
    widthMm: k.width_mm != null ? String(k.width_mm) : "",
    depthMm: k.depth_mm != null ? String(k.depth_mm) : "",
    brand: k.brand ?? "",
    purchaseDate: k.purchase_date ?? "",
    commissionedDate: k.commissioned_date ?? "",
    notes: k.notes ?? "",
    attributesJson: k.attributes != null ? JSON.stringify(k.attributes, null, 2) : "",
  };
}

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
  const [sortOrderCreate, setSortOrderCreate] = useState("0");
  const [createExtra, setCreateExtra] = useState<RackExtraForm>(emptyExtra);
  const [err, setErr] = useState<string | null>(null);
  const [rackTab, setRackTab] = useState<"elevation" | "admin">("elevation");

  const [editId, setEditId] = useState<number | null>(null);
  const [editName, setEditName] = useState("");
  const [editUHeight, setEditUHeight] = useState("42");
  const [editSortOrder, setEditSortOrder] = useState("0");
  const [editExtra, setEditExtra] = useState<RackExtraForm>(emptyExtra());

  const roomsQ = useQuery({ queryKey: ["dcim", "rooms", "all"], queryFn: () => api.listRooms() });
  const filterNum = useMemo(() => {
    const n = Number(roomFilter);
    return Number.isFinite(n) && n > 0 ? n : undefined;
  }, [roomFilter]);

  const racksQ = useQuery({
    queryKey: ["dcim", "racks", filterNum ?? "all"],
    queryFn: () => api.listRacks(filterNum),
  });

  function beginEdit(k: Rack) {
    setEditId(k.id);
    setEditName(k.name);
    setEditUHeight(String(k.u_height));
    setEditSortOrder(String(k.sort_order));
    setEditExtra(rackToExtra(k));
    setErr(null);
  }

  function cancelEdit() {
    setEditId(null);
    setErr(null);
  }

  const m = useMutation({
    mutationFn: () => {
      const dims: Array<{ key: "height_mm" | "width_mm" | "depth_mm"; raw: string }> = [
        { key: "height_mm", raw: createExtra.heightMm },
        { key: "width_mm", raw: createExtra.widthMm },
        { key: "depth_mm", raw: createExtra.depthMm },
      ];
      for (const { raw } of dims) {
        const p = parseMmInput(raw);
        if (p === "invalid") throw new Error(t("dcim.racks.invalidMm"));
      }
      const attr = parseAttributesJson(createExtra.attributesJson, false);
      if (!attr.ok) throw new Error(t("dcim.racks.invalidAttributesJson"));

      const body: Parameters<typeof api.createRack>[0] = {
        room_id: Number(roomId),
        name: name.trim(),
        u_height: Number(uHeight) || 42,
        sort_order: Number(sortOrderCreate) || 0,
      };
      for (const { key, raw } of dims) {
        const p = parseMmInput(raw);
        if (typeof p === "number") body[key] = p;
      }
      if (createExtra.brand.trim()) body.brand = createExtra.brand.trim();
      const pd = parseDateInput(createExtra.purchaseDate);
      if (pd !== "empty") body.purchase_date = pd;
      const cd = parseDateInput(createExtra.commissionedDate);
      if (cd !== "empty") body.commissioned_date = cd;
      if (createExtra.notes.trim()) body.notes = createExtra.notes.trim();
      if (attr.value !== undefined) body.attributes = attr.value;

      return api.createRack(body);
    },
    onSuccess: () => {
      setErr(null);
      setName("");
      setCreateExtra(emptyExtra());
      void qc.invalidateQueries({ queryKey: ["dcim", "racks"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const saveEdit = useMutation({
    mutationFn: () => {
      if (editId == null) throw new Error("id");
      const dims: Array<{ key: "height_mm" | "width_mm" | "depth_mm"; raw: string }> = [
        { key: "height_mm", raw: editExtra.heightMm },
        { key: "width_mm", raw: editExtra.widthMm },
        { key: "depth_mm", raw: editExtra.depthMm },
      ];
      for (const { raw } of dims) {
        const p = parseMmInput(raw);
        if (p === "invalid") throw new Error(t("dcim.racks.invalidMm"));
      }
      const attr = parseAttributesJson(editExtra.attributesJson, true);
      if (!attr.ok) throw new Error(t("dcim.racks.invalidAttributesJson"));

      const body: Parameters<typeof api.updateRack>[1] = {
        name: editName.trim(),
        u_height: Number(editUHeight) || 42,
        sort_order: Number(editSortOrder) || 0,
      };
      for (const { key, raw } of dims) {
        const p = parseMmInput(raw);
        if (p === "empty") body[key] = null;
        else if (typeof p === "number") body[key] = p;
      }
      body.brand = editExtra.brand.trim() ? editExtra.brand.trim() : null;
      const pd = parseDateInput(editExtra.purchaseDate);
      body.purchase_date = pd === "empty" ? null : pd;
      const cd = parseDateInput(editExtra.commissionedDate);
      body.commissioned_date = cd === "empty" ? null : cd;
      body.notes = editExtra.notes.trim() ? editExtra.notes.trim() : null;
      if (attr.value !== undefined) body.attributes = attr.value;

      return api.updateRack(editId, body);
    },
    onSuccess: () => {
      setErr(null);
      setEditId(null);
      void qc.invalidateQueries({ queryKey: ["dcim", "racks"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const racks = racksQ.data ?? [];

  return (
    <Panel title={t("nav.dcimRacks")}>
      <DcimInnerTabs
        tabs={[
          { id: "elevation", label: t("dcim.racks.tabElevation"), icon: "rackElevation" },
          { id: "admin", label: t("dcim.racks.tabAdmin"), icon: "rackAdmin" },
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
            <label>
              {t("dcim.racks.sortOrder")}
              <input
                type="number"
                value={sortOrderCreate}
                onChange={(e) => setSortOrderCreate(e.target.value)}
              />
            </label>
            <label>
              {t("dcim.racks.heightMm")}
              <input
                type="number"
                min={1}
                value={createExtra.heightMm}
                onChange={(e) => setCreateExtra((x) => ({ ...x, heightMm: e.target.value }))}
              />
            </label>
            <label>
              {t("dcim.racks.widthMm")}
              <input
                type="number"
                min={1}
                value={createExtra.widthMm}
                onChange={(e) => setCreateExtra((x) => ({ ...x, widthMm: e.target.value }))}
              />
            </label>
            <label>
              {t("dcim.racks.depthMm")}
              <input
                type="number"
                min={1}
                value={createExtra.depthMm}
                onChange={(e) => setCreateExtra((x) => ({ ...x, depthMm: e.target.value }))}
              />
            </label>
            <label>
              {t("dcim.racks.brand")}
              <input
                value={createExtra.brand}
                onChange={(e) => setCreateExtra((x) => ({ ...x, brand: e.target.value }))}
              />
            </label>
            <label>
              {t("dcim.racks.purchaseDate")}
              <input
                type="date"
                value={createExtra.purchaseDate}
                onChange={(e) => setCreateExtra((x) => ({ ...x, purchaseDate: e.target.value }))}
              />
            </label>
            <label>
              {t("dcim.racks.commissionedDate")}
              <input
                type="date"
                value={createExtra.commissionedDate}
                onChange={(e) => setCreateExtra((x) => ({ ...x, commissionedDate: e.target.value }))}
              />
            </label>
            <label className={styles.formFullWidth}>
              {t("dcim.racks.notes")}
              <textarea
                rows={2}
                value={createExtra.notes}
                onChange={(e) => setCreateExtra((x) => ({ ...x, notes: e.target.value }))}
              />
            </label>
            <label className={styles.formFullWidth}>
              {t("dcim.racks.attributesJson")}
              <textarea
                rows={3}
                value={createExtra.attributesJson}
                onChange={(e) => setCreateExtra((x) => ({ ...x, attributesJson: e.target.value }))}
                placeholder="{}"
              />
              <span className={styles.muted}>{t("dcim.racks.attributesHint")}</span>
            </label>
            <button type="submit" className={styles.btn} disabled={m.isPending || roomsQ.isLoading}>
              {m.isPending ? t("dcim.common.creating") : t("dcim.racks.create")}
            </button>
          </form>

          {editId != null ? (
            <section className={styles.formRow} aria-labelledby="rack-edit-heading">
              <h3 id="rack-edit-heading">{t("dcim.racks.editTitle")}</h3>
              <label>
                {t("dcim.common.name")}
                <input value={editName} onChange={(e) => setEditName(e.target.value)} required />
              </label>
              <label>
                {t("dcim.racks.uHeight")}
                <input
                  type="number"
                  min={1}
                  max={64}
                  value={editUHeight}
                  onChange={(e) => setEditUHeight(e.target.value)}
                />
              </label>
              <label>
                {t("dcim.racks.sortOrder")}
                <input
                  type="number"
                  value={editSortOrder}
                  onChange={(e) => setEditSortOrder(e.target.value)}
                />
              </label>
              <label>
                {t("dcim.racks.heightMm")}
                <input
                  type="number"
                  min={1}
                  value={editExtra.heightMm}
                  onChange={(e) => setEditExtra((x) => ({ ...x, heightMm: e.target.value }))}
                />
              </label>
              <label>
                {t("dcim.racks.widthMm")}
                <input
                  type="number"
                  min={1}
                  value={editExtra.widthMm}
                  onChange={(e) => setEditExtra((x) => ({ ...x, widthMm: e.target.value }))}
                />
              </label>
              <label>
                {t("dcim.racks.depthMm")}
                <input
                  type="number"
                  min={1}
                  value={editExtra.depthMm}
                  onChange={(e) => setEditExtra((x) => ({ ...x, depthMm: e.target.value }))}
                />
              </label>
              <label>
                {t("dcim.racks.brand")}
                <input
                  value={editExtra.brand}
                  onChange={(e) => setEditExtra((x) => ({ ...x, brand: e.target.value }))}
                />
              </label>
              <label>
                {t("dcim.racks.purchaseDate")}
                <input
                  type="date"
                  value={editExtra.purchaseDate}
                  onChange={(e) => setEditExtra((x) => ({ ...x, purchaseDate: e.target.value }))}
                />
              </label>
              <label>
                {t("dcim.racks.commissionedDate")}
                <input
                  type="date"
                  value={editExtra.commissionedDate}
                  onChange={(e) => setEditExtra((x) => ({ ...x, commissionedDate: e.target.value }))}
                />
              </label>
              <label className={styles.formFullWidth}>
                {t("dcim.racks.notes")}
                <textarea
                  rows={2}
                  value={editExtra.notes}
                  onChange={(e) => setEditExtra((x) => ({ ...x, notes: e.target.value }))}
                />
              </label>
              <label className={styles.formFullWidth}>
                {t("dcim.racks.attributesJson")}
                <textarea
                  rows={4}
                  value={editExtra.attributesJson}
                  onChange={(e) => setEditExtra((x) => ({ ...x, attributesJson: e.target.value }))}
                />
                <span className={styles.muted}>{t("dcim.racks.attributesHint")}</span>
              </label>
              <div className={styles.formRow}>
                <button
                  type="button"
                  className={styles.btn}
                  disabled={saveEdit.isPending}
                  onClick={() => saveEdit.mutate()}
                >
                  {saveEdit.isPending ? t("dcim.common.loading") : t("dcim.racks.save")}
                </button>
                <button type="button" className={styles.btnMuted} onClick={cancelEdit}>
                  {t("dcim.racks.cancelEdit")}
                </button>
              </div>
            </section>
          ) : null}

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
                  <th>{t("dcim.racks.tableBrand")}</th>
                  <th>{t("dcim.racks.tableDims")}</th>
                  <th>{t("dcim.racks.edit")}</th>
                </tr>
              </thead>
              <tbody>
                {racksQ.data.map((k) => (
                  <tr key={k.id}>
                    <td>{k.id}</td>
                    <td>{k.room_id}</td>
                    <td>{k.name}</td>
                    <td>{k.u_height}</td>
                    <td>{k.brand ?? "—"}</td>
                    <td>{formatDimsMm(k)}</td>
                    <td>
                      <button type="button" className={styles.btnLink} onClick={() => beginEdit(k)}>
                        {t("dcim.racks.edit")}
                      </button>
                    </td>
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
