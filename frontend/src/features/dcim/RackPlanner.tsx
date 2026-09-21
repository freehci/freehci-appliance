import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useMemo, useRef, useState, type FormEvent, type ReactNode } from "react";
import { Link } from "react-router-dom";
import { catalogProvisionHref } from "@/features/catalog/catalogHref";
import { Panel } from "@/components/ui/Panel";
import { useI18n } from "@/i18n/I18nProvider";
import type { MessageKey } from "@/i18n/messages/en";
import { ApiError } from "@/lib/api";
import * as api from "./dcimApi";
import baseStyles from "./dcim.module.css";
import { RackElevation, type DragPayload } from "./RackElevation";
import { deviceModelBackSrc, deviceModelRackFaceSrc } from "./modelImages";
import styles from "./RackPlanner.module.css";
import {
  canPlaceDeviceAt,
  deviceUHeight,
  existingRangesForRack,
  findPlacementIssues,
  firstFitU,
  MM_PER_U,
  occupiedUnitsForRack,
  occupiesRange,
  rackColumnU,
  rackMounting,
} from "./rackUtils";
import type { DeviceInstance, DeviceModel, Rack, RackPlacement } from "./types";

/** Unik kort suffiks uten `crypto.randomUUID` (krever ofte sikker kontekst / HTTPS). */
function shortInstanceSuffix(): string {
  const c = globalThis.crypto;
  if (c != null && typeof c.randomUUID === "function") {
    try {
      return c.randomUUID().replace(/-/g, "").slice(0, 8);
    } catch {
      /* ignore */
    }
  }
  return `${Date.now().toString(36)}${Math.random().toString(36).slice(2, 6)}`.slice(-10);
}

type PaletteTab = "devices" | "models";

const CHIP_PREVIEW = 5;

function ChipOverflow({
  items,
  selected,
  onSelect,
  allLabel,
  moreLabel,
  lessLabel,
  searchLabel,
}: {
  items: { id: string; label: string }[];
  selected: string;
  onSelect: (id: string) => void;
  allLabel: string;
  moreLabel: string;
  lessLabel: string;
  searchLabel: string;
}) {
  const [open, setOpen] = useState(false);
  const [q, setQ] = useState("");
  const filtered = useMemo(() => {
    const needle = q.trim().toLowerCase();
    if (!needle) return items;
    return items.filter((x) => x.label.toLowerCase().includes(needle));
  }, [items, q]);
  const shown = useMemo(() => {
    if (open || filtered.length <= CHIP_PREVIEW) return filtered;
    const head = filtered.slice(0, CHIP_PREVIEW);
    if (!selected || head.some((x) => x.id === selected)) return head;
    const extra = filtered.find((x) => x.id === selected);
    return extra ? [extra, ...head.slice(0, CHIP_PREVIEW - 1)] : head;
  }, [filtered, open, selected]);
  const hidden = Math.max(0, filtered.length - shown.length);

  return (
    <div className={styles.chipBlock}>
      {open && items.length > CHIP_PREVIEW ? (
        <input
          className={styles.paletteSearch}
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder={searchLabel}
          aria-label={searchLabel}
        />
      ) : null}
      <div className={styles.chipRow}>
        <button
          type="button"
          className={`${styles.chip} ${selected === "" ? styles.chipOn : ""}`.trim()}
          onClick={() => onSelect("")}
        >
          {allLabel}
        </button>
        {shown.map((item) => (
          <button
            key={item.id}
            type="button"
            className={`${styles.chip} ${selected === item.id ? styles.chipOn : ""}`.trim()}
            onClick={() => onSelect(item.id)}
          >
            {item.label}
          </button>
        ))}
        {filtered.length > CHIP_PREVIEW ? (
          <button type="button" className={styles.chip} onClick={() => setOpen((v) => !v)}>
            {open ? lessLabel : hidden > 0 ? `${moreLabel} (${hidden})` : lessLabel}
          </button>
        ) : null}
      </div>
    </div>
  );
}

type PatchVars = {
  pid: number;
  rack_id?: number;
  u_position?: number;
  mounting?: string;
};

function PlacementEditorDialog({
  placement,
  racks,
  allPlacements,
  devicesById,
  modelsById,
  t,
  saving,
  onClose,
  onApply,
}: {
  placement: RackPlacement;
  racks: Rack[];
  allPlacements: RackPlacement[];
  devicesById: Map<number, DeviceInstance>;
  modelsById: Map<number, DeviceModel>;
  t: (key: MessageKey) => string;
  saving: boolean;
  onClose: () => void;
  onApply: (rack_id: number, u_position: number, mounting: string) => void;
}) {
  const ref = useRef<HTMLDialogElement>(null);
  const [rackId, setRackId] = useState(String(placement.rack_id));
  const [uStr, setUStr] = useState(String(placement.u_position));
  const [mount, setMount] = useState(placement.mounting);

  useEffect(() => {
    const d = ref.current;
    if (!d) return;
    d.showModal();
    return () => d.close();
  }, []);

  const dev = devicesById.get(placement.device_id);
  const h = dev ? deviceUHeight(dev, modelsById) : 1;
  const rackNum = Number(rackId);
  const selectedRack = racks.find((r) => r.id === rackNum);

  const clientErr = useMemo(() => {
    if (!selectedRack) return t("dcim.racks.editorInvalidU");
    const u = Number(uStr);
    if (h === 0) {
      if (!Number.isFinite(u) || u !== 0) return t("dcim.racks.editorInvalidU");
      return null;
    }
    if (!Number.isFinite(u) || u < 1) return t("dcim.racks.editorInvalidU");
    const ranges = existingRangesForRack(
      allPlacements,
      rackNum,
      devicesById,
      modelsById,
      placement.id,
    );
    if (!canPlaceDeviceAt(u, h, selectedRack.u_height, ranges)) return t("dcim.racks.editorNoFit");
    return null;
  }, [uStr, rackNum, h, selectedRack, allPlacements, devicesById, modelsById, placement.id, t]);

  const submit = (e: FormEvent) => {
    e.preventDefault();
    if (clientErr || !selectedRack) return;
    onApply(rackNum, Number(uStr), mount);
  };

  return (
    <dialog
      ref={ref}
      className={styles.placementDialog}
      aria-labelledby="placement-editor-title"
      onCancel={(e) => {
        e.preventDefault();
        onClose();
      }}
    >
      <form className={styles.placementDialogForm} onSubmit={submit}>
        <h2 id="placement-editor-title" className={styles.placementDialogTitle}>
          {t("dcim.racks.editorTitle")}
        </h2>
        <div className={styles.placementDialogFields}>
          <label className={styles.placementDialogLabel}>
            {t("dcim.racks.editorRack")}
            <select
              value={rackId}
              onChange={(e) => setRackId(e.target.value)}
              data-rack-no-drag=""
            >
              {racks.map((r) => (
                <option key={r.id} value={String(r.id)}>
                  #{r.id} {r.name} ({r.u_height}U)
                </option>
              ))}
            </select>
          </label>
          <label className={styles.placementDialogLabel}>
            {t("dcim.racks.editorU")}
            <input
              type="number"
              min={h === 0 ? 0 : 1}
              max={h === 0 ? 0 : selectedRack?.u_height ?? 64}
              value={uStr}
              onChange={(e) => setUStr(e.target.value)}
              readOnly={h === 0}
              aria-invalid={clientErr != null}
            />
          </label>
          {h === 0 ? (
            <p className={baseStyles.muted} style={{ gridColumn: "1 / -1", margin: 0, fontSize: "var(--text-xs)" }}>
              {t("dcim.racks.editorUZeroHint")}
            </p>
          ) : null}
          <label className={styles.placementDialogLabel}>
            {t("dcim.racks.editorMount")}
            <select value={mount} onChange={(e) => setMount(e.target.value)} data-rack-no-drag="">
              <option value="front">{t("dcim.equip.mountFront")}</option>
              <option value="rear">{t("dcim.equip.mountRear")}</option>
            </select>
          </label>
        </div>
        {clientErr ? <p className={styles.placementDialogErr}>{clientErr}</p> : null}
        <div className={styles.placementDialogActions}>
          <button type="button" className={baseStyles.btn} onClick={onClose}>
            {t("dcim.racks.editorCancel")}
          </button>
          <button type="submit" className={baseStyles.btn} disabled={clientErr != null || saving}>
            {t("dcim.racks.editorApply")}
          </button>
        </div>
      </form>
    </dialog>
  );
}

export function RackPlanner({
  racks,
  highlightPlacementId,
  embed,
}: {
  racks: Rack[];
  highlightPlacementId?: number;
  /** When true, omit outer Panel (parent provides section chrome). */
  embed?: boolean;
}) {
  const { t } = useI18n();
  const qc = useQueryClient();
  const [paletteTab, setPaletteTab] = useState<PaletteTab>("devices");
  const [editorPlacement, setEditorPlacement] = useState<RackPlacement | null>(null);
  const [dragging, setDragging] = useState<DragPayload>(null);
  const [dragOverKey, setDragOverKey] = useState<string | null>(null);
  const [dropErr, setDropErr] = useState<string | null>(null);
  const [paletteQuery, setPaletteQuery] = useState("");
  const [layoutQuery, setLayoutQuery] = useState("");
  const [sizeFilter, setSizeFilter] = useState<"" | "1" | "2" | "4+">("");
  const [vendorFilter, setVendorFilter] = useState("");
  const [typeFilter, setTypeFilter] = useState("");
  const [compact, setCompact] = useState(false);
  const [zoom, setZoom] = useState(100);
  const [paletteCollapsed, setPaletteCollapsed] = useState(false);
  const [selectedPlacementId, setSelectedPlacementId] = useState<number | null>(null);
  const [selectedRackId, setSelectedRackId] = useState<number | null>(null);
  const [elevDraft, setElevDraft] = useState("");
  const [armed, setArmed] = useState<{ kind: "device" | "model"; id: number } | null>(null);

  const devicesQ = useQuery({ queryKey: ["dcim", "devices"], queryFn: api.listDevices });
  const modelsQ = useQuery({ queryKey: ["dcim", "device-models"], queryFn: api.listDeviceModels });
  const mfrQ = useQuery({ queryKey: ["dcim", "manufacturers"], queryFn: api.listManufacturers });
  const typesQ = useQuery({ queryKey: ["dcim", "device-types"], queryFn: api.listDeviceTypes });
  const roomsQ = useQuery({ queryKey: ["dcim", "rooms"], queryFn: () => api.listRooms() });
  const sitesQ = useQuery({ queryKey: ["dcim", "sites"], queryFn: api.listSites });
  const allPlacementsQ = useQuery({
    queryKey: ["dcim", "placements", "all"],
    queryFn: () => api.listPlacements(),
  });

  const devicesById = useMemo(() => {
    const m = new Map<number, DeviceInstance>();
    for (const d of devicesQ.data ?? []) m.set(d.id, d);
    return m;
  }, [devicesQ.data]);

  const modelsById = useMemo(() => {
    const m = new Map<number, DeviceModel>();
    for (const x of modelsQ.data ?? []) m.set(x.id, x);
    return m;
  }, [modelsQ.data]);

  const placedDeviceIds = useMemo(() => {
    const s = new Set<number>();
    for (const p of allPlacementsQ.data ?? []) s.add(p.device_id);
    return s;
  }, [allPlacementsQ.data]);

  const unplacedDevices = useMemo(
    () => (devicesQ.data ?? []).filter((d) => !placedDeviceIds.has(d.id)),
    [devicesQ.data, placedDeviceIds],
  );

  const mfrById = useMemo(() => {
    const m = new Map<number, string>();
    for (const x of mfrQ.data ?? []) m.set(x.id, x.name);
    return m;
  }, [mfrQ.data]);

  const typeById = useMemo(() => {
    const m = new Map<number, string>();
    for (const x of typesQ.data ?? []) m.set(x.id, x.name);
    return m;
  }, [typesQ.data]);

  const roomById = useMemo(() => {
    const m = new Map<number, { name: string; site_id: number }>();
    for (const r of roomsQ.data ?? []) m.set(r.id, { name: r.name, site_id: r.site_id });
    return m;
  }, [roomsQ.data]);

  const siteById = useMemo(() => {
    const m = new Map<number, string>();
    for (const s of sitesQ.data ?? []) m.set(s.id, s.name);
    return m;
  }, [sitesQ.data]);

  const roomLabelForRack = (rack: Rack) => {
    const room = roomById.get(rack.room_id);
    if (!room) return undefined;
    const site = siteById.get(room.site_id);
    return site ? `${site} › ${room.name}` : room.name;
  };

  const matchesSize = (u: number) => {
    if (sizeFilter === "1") return u === 1;
    if (sizeFilter === "2") return u === 2;
    if (sizeFilter === "4+") return u >= 4;
    return true;
  };

  const allPlacements = allPlacementsQ.data ?? [];

  const visibleRacks = useMemo(() => {
    const q = layoutQuery.trim().toLowerCase();
    if (!q) return racks;
    return racks.filter((r) => {
      const room = roomById.get(r.room_id);
      const site = room ? siteById.get(room.site_id) : undefined;
      const loc = room ? (site ? `${site} › ${room.name}` : room.name) : "";
      if (`${r.name} ${loc}`.toLowerCase().includes(q)) return true;
      return allPlacements.some((p) => {
        if (p.rack_id !== r.id) return false;
        const d = devicesById.get(p.device_id);
        if (!d) return false;
        const mod = d.device_model_id != null ? modelsById.get(d.device_model_id) : undefined;
        return `${d.name} ${mod?.name ?? ""}`.toLowerCase().includes(q);
      });
    });
  }, [racks, layoutQuery, roomById, siteById, allPlacements, devicesById, modelsById]);

  const filteredUnplaced = useMemo(() => {
    const q = paletteQuery.trim().toLowerCase();
    return unplacedDevices.filter((d) => {
      const uh = deviceUHeight(d, modelsById);
      if (!matchesSize(uh)) return false;
      const mod = d.device_model_id != null ? modelsById.get(d.device_model_id) : undefined;
      if (vendorFilter && String(mod?.manufacturer_id ?? "") !== vendorFilter) return false;
      const typeId = d.effective_device_type_id ?? mod?.device_type_id ?? null;
      if (typeFilter && String(typeId ?? "") !== typeFilter) return false;
      if (q) {
        const blob = `${d.name} ${mod?.name ?? ""} ${d.serial_number ?? ""} ${d.asset_tag ?? ""}`.toLowerCase();
        if (!blob.includes(q)) return false;
      }
      return true;
    });
  }, [unplacedDevices, modelsById, paletteQuery, sizeFilter, vendorFilter, typeFilter]);

  const vendorItems = useMemo(
    () =>
      [...(mfrQ.data ?? [])]
        .sort((a, b) => a.name.localeCompare(b.name))
        .map((m) => ({ id: String(m.id), label: m.name })),
    [mfrQ.data],
  );
  const typeItems = useMemo(
    () =>
      [...(typesQ.data ?? [])]
        .sort((a, b) => a.name.localeCompare(b.name))
        .map((tp) => ({ id: String(tp.id), label: tp.name })),
    [typesQ.data],
  );

  const filteredModels = useMemo(() => {
    const q = paletteQuery.trim().toLowerCase();
    return (modelsQ.data ?? []).filter((m) => {
      if (!matchesSize(m.u_height)) return false;
      if (vendorFilter && String(m.manufacturer_id ?? "") !== vendorFilter) return false;
      if (typeFilter && String(m.device_type_id ?? "") !== typeFilter) return false;
      if (q) {
        const blob = `${m.name} ${mfrById.get(m.manufacturer_id ?? -1) ?? ""}`.toLowerCase();
        if (!blob.includes(q)) return false;
      }
      return true;
    });
  }, [modelsQ.data, paletteQuery, sizeFilter, vendorFilter, typeFilter, mfrById]);

  const placeDeviceMu = useMutation({
    mutationFn: (body: { rack_id: number; device_id: number; u_position: number }) =>
      api.createPlacement({ ...body, mounting: "front" }),
    onSuccess: (p) => {
      setDropErr(null);
      setSelectedPlacementId(p.id);
      setArmed(null);
      void qc.invalidateQueries({ queryKey: ["dcim", "placements"] });
    },
    onError: (e: Error) => setDropErr(e instanceof ApiError ? e.message : e.message),
  });

  const placeFromModelMu = useMutation({
    mutationFn: async (vars: { rackId: number; modelId: number; u: number }) => {
      const model = modelsById.get(vars.modelId);
      const base = model?.name ?? "device";
      const dev = await api.createDevice({
        device_model_id: vars.modelId,
        name: `${base}-${shortInstanceSuffix()}`,
      });
      return api.createPlacement({
        rack_id: vars.rackId,
        device_id: dev.id,
        u_position: vars.u,
        mounting: "front",
      });
    },
    onSuccess: (p) => {
      setDropErr(null);
      setSelectedPlacementId(p.id);
      setArmed(null);
      void qc.invalidateQueries({ queryKey: ["dcim", "placements"] });
      void qc.invalidateQueries({ queryKey: ["dcim", "devices"] });
    },
    onError: (e: Error) => setDropErr(e instanceof ApiError ? e.message : e.message),
  });

  const patchPlacementMu = useMutation({
    mutationFn: (vars: PatchVars) => {
      const body: { rack_id?: number; u_position?: number; mounting?: string } = {};
      if (vars.rack_id !== undefined) body.rack_id = vars.rack_id;
      if (vars.u_position !== undefined) body.u_position = vars.u_position;
      if (vars.mounting !== undefined) body.mounting = vars.mounting;
      return api.updatePlacement(vars.pid, body);
    },
    onMutate: async (vars) => {
      setDropErr(null);
      await qc.cancelQueries({ queryKey: ["dcim", "placements", "all"] });
      const previous = qc.getQueryData<RackPlacement[]>(["dcim", "placements", "all"]);
      qc.setQueryData<RackPlacement[]>(["dcim", "placements", "all"], (old) => {
        if (!old) return old;
        return old.map((p) =>
          p.id === vars.pid
            ? {
                ...p,
                ...(vars.rack_id !== undefined ? { rack_id: vars.rack_id } : {}),
                ...(vars.u_position !== undefined ? { u_position: vars.u_position } : {}),
                ...(vars.mounting !== undefined ? { mounting: vars.mounting } : {}),
              }
            : p,
        );
      });
      return { previous };
    },
    onError: (e: Error, _vars, ctx) => {
      if (ctx?.previous !== undefined) {
        qc.setQueryData(["dcim", "placements", "all"], ctx.previous);
      }
      setDropErr(e instanceof ApiError ? e.message : e.message);
    },
    onSettled: () => {
      void qc.invalidateQueries({ queryKey: ["dcim", "placements"] });
    },
  });

  const removeMu = useMutation({
    mutationFn: (id: number) => api.deletePlacement(id),
    onSuccess: (_void, id) => {
      setDropErr(null);
      setSelectedPlacementId((cur) => (cur === id ? null : cur));
      void qc.invalidateQueries({ queryKey: ["dcim", "placements"] });
    },
    onError: (e: Error) => setDropErr(e instanceof ApiError ? e.message : e.message),
  });

  const patchRackMu = useMutation({
    mutationFn: (vars: { id: number; mounting?: "floor" | "wall"; elevation_mm?: number | null }) =>
      api.updateRack(vars.id, { mounting: vars.mounting, elevation_mm: vars.elevation_mm }),
    onSuccess: () => {
      setDropErr(null);
      void qc.invalidateQueries({ queryKey: ["dcim", "racks"] });
    },
    onError: (e: Error) => setDropErr(e instanceof ApiError ? e.message : e.message),
  });

  useEffect(() => {
    if (highlightPlacementId != null) setSelectedPlacementId(highlightPlacementId);
  }, [highlightPlacementId]);

  const issues = useMemo(
    () => findPlacementIssues(allPlacements, visibleRacks, devicesById, modelsById),
    [allPlacements, visibleRacks, devicesById, modelsById],
  );
  const conflictIds = useMemo(() => new Set(issues.map((i) => i.placementId)), [issues]);

  const usedU = useMemo(() => {
    let used = 0;
    let total = 0;
    for (const r of visibleRacks) {
      total += r.u_height;
      used += occupiedUnitsForRack(allPlacements, r.id, devicesById, modelsById).size;
    }
    return { used, total, free: Math.max(0, total - used) };
  }, [visibleRacks, allPlacements, devicesById, modelsById]);

  const columnU = useMemo(() => rackColumnU(visibleRacks), [visibleRacks]);
  const selectedDetailRack = selectedRackId != null ? (racks.find((r) => r.id === selectedRackId) ?? null) : null;
  const rackFeedsQ = useQuery({
    queryKey: ["dcim", "power-feeds", "rack", selectedDetailRack?.id ?? "none"],
    queryFn: () => api.listPowerFeeds({ rackId: selectedDetailRack!.id }),
    enabled: selectedDetailRack != null,
  });

  useEffect(() => {
    if (!selectedDetailRack) return;
    setElevDraft(selectedDetailRack.elevation_mm != null ? String(selectedDetailRack.elevation_mm) : "");
  }, [selectedDetailRack?.id, selectedDetailRack?.elevation_mm]);

  const selectedPlacement =
    selectedPlacementId != null ? (allPlacements.find((p) => p.id === selectedPlacementId) ?? null) : null;
  const selectedDevice = selectedPlacement ? devicesById.get(selectedPlacement.device_id) : undefined;
  const selectedRack = selectedPlacement ? racks.find((r) => r.id === selectedPlacement.rack_id) : undefined;
  const selectedModel =
    selectedDevice?.device_model_id != null ? modelsById.get(selectedDevice.device_model_id) : undefined;
  const selectedUHeight = selectedDevice ? deviceUHeight(selectedDevice, modelsById) : 0;
  const selectedRange =
    selectedPlacement == null
      ? ""
      : selectedUHeight === 0
        ? "U0"
        : (() => {
            const { bottom, top } = occupiesRange(selectedPlacement.u_position, selectedUHeight);
            return `U${bottom}–U${top}`;
          })();
  const selectedTypeId = selectedDevice?.effective_device_type_id ?? selectedModel?.device_type_id ?? null;
  const selectedThumb = selectedModel
    ? selectedPlacement?.mounting === "rear"
      ? (deviceModelBackSrc(selectedModel) ?? deviceModelRackFaceSrc(selectedModel))
      : deviceModelRackFaceSrc(selectedModel)
    : null;
  const colMin = Math.round((compact ? 110 : 160) * (zoom / 100));
  const dash = (v: string | null | undefined) => (v && v.trim() ? v : "—");

  const autoPlace = () => {
    if (!armed) {
      setDropErr(t("dcim.racks.autoPlaceNeedPick"));
      return;
    }
    let h = 1;
    if (armed.kind === "device") {
      const d = devicesById.get(armed.id);
      if (!d) return;
      h = deviceUHeight(d, modelsById);
    } else {
      h = modelsById.get(armed.id)?.u_height ?? 1;
    }
    for (const rack of visibleRacks) {
      const ranges = existingRangesForRack(allPlacements, rack.id, devicesById, modelsById);
      const u = firstFitU(rack.u_height, h, ranges);
      if (u != null) {
        if (armed.kind === "device") {
          placeDeviceMu.mutate({ rack_id: rack.id, device_id: armed.id, u_position: u });
        } else {
          placeFromModelMu.mutate({ rackId: rack.id, modelId: armed.id, u });
        }
        return;
      }
    }
    setDropErr(t("dcim.racks.autoPlaceNoFit"));
  };

  const wrap = (body: ReactNode) =>
    embed ? body : <Panel title={t("dcim.racks.designerTitle")}>{body}</Panel>;

  if (racks.length === 0) {
    return wrap(<p className={baseStyles.muted}>{t("dcim.racks.empty")}</p>);
  }

  return wrap(
    <div className={styles.designer}>
      {dropErr ? (
        <p className={baseStyles.err}>
          {t("dcim.racks.dropError")} {dropErr}
        </p>
      ) : null}

      <p className={styles.hint}>{t("dcim.racks.designerIntro")}</p>

      <div className={styles.toolbar}>
        <input
          className={styles.toolbarSearch}
          value={layoutQuery}
          onChange={(e) => setLayoutQuery(e.target.value)}
          placeholder={t("dcim.racks.searchPlaceholder")}
          aria-label={t("dcim.racks.searchPlaceholder")}
        />
        <div className={styles.toolbarGroup} role="group" aria-label={t("dcim.racks.zoom")}>
          {[75, 100, 125].map((z) => (
            <button
              key={z}
              type="button"
              className={`${styles.toolbarBtn} ${zoom === z ? styles.toolbarBtnOn : ""}`.trim()}
              onClick={() => setZoom(z)}
            >
              {z}%
            </button>
          ))}
        </div>
        <button type="button" className={`${styles.toolbarBtn} ${styles.toolbarBtnOn}`} disabled>
          {t("dcim.racks.snapOn")}
        </button>
        <button type="button" className={styles.toolbarBtn} onClick={autoPlace}>
          {t("dcim.racks.autoPlace")}
        </button>
        <button
          type="button"
          className={styles.toolbarBtn}
          onClick={() => {
            const first = issues[0];
            if (first) setSelectedPlacementId(first.placementId);
          }}
        >
          {t("dcim.racks.validate")}
        </button>
        <span className={styles.paletteItemMeta}>{t("dcim.racks.savedAuto")}</span>
        {paletteCollapsed ? (
          <button type="button" className={styles.toolbarBtn} onClick={() => setPaletteCollapsed(false)}>
            {t("dcim.racks.expandPalette")}
          </button>
        ) : null}
      </div>

      <div className={styles.legend} aria-label={t("dcim.racks.rackView")}>
        <span className={styles.legendItem}>
          <span className={`${styles.swatch} ${styles.swatchFront}`} />
          {t("dcim.racks.legendFront")}
        </span>
        <span className={styles.legendItem}>
          <span className={`${styles.swatch} ${styles.swatchRear}`} />
          {t("dcim.racks.legendRear")}
        </span>
        <span className={styles.legendItem}>
          <span className={`${styles.swatch} ${styles.swatchSelected}`} />
          {t("dcim.racks.legendSelected")}
        </span>
        <span className={styles.legendItem}>
          <span className={`${styles.swatch} ${styles.swatchEmpty}`} />
          {t("dcim.racks.legendEmpty")}
        </span>
        <span className={styles.legendItem}>
          <span className={`${styles.swatch} ${styles.swatchConflict}`} />
          {t("dcim.racks.legendConflict")}
        </span>
      </div>

      <div className={`${styles.planner} ${paletteCollapsed ? styles.plannerPaletteCollapsed : ""}`.trim()}>
        {paletteCollapsed ? null : (
          <aside className={styles.palette}>
            <button
              type="button"
              className={`${styles.toolbarBtn} ${styles.paletteCollapse}`}
              onClick={() => setPaletteCollapsed(true)}
            >
              {t("dcim.racks.collapsePalette")}
            </button>
            <h3 className={styles.paletteTitle}>{t("dcim.racks.paletteTitle")}</h3>
            <div className={styles.paletteTabs} role="tablist">
              <button
                type="button"
                role="tab"
                aria-selected={paletteTab === "devices"}
                className={`${styles.paletteTab} ${paletteTab === "devices" ? styles.paletteTabActive : ""}`.trim()}
                onClick={() => setPaletteTab("devices")}
              >
                {t("dcim.racks.paletteTabDevices")}
              </button>
              <button
                type="button"
                role="tab"
                aria-selected={paletteTab === "models"}
                className={`${styles.paletteTab} ${paletteTab === "models" ? styles.paletteTabActive : ""}`.trim()}
                onClick={() => setPaletteTab("models")}
              >
                {t("dcim.racks.paletteTabModels")}
              </button>
            </div>
            <div className={styles.paletteFilters}>
              <input
                className={styles.paletteSearch}
                value={paletteQuery}
                onChange={(e) => setPaletteQuery(e.target.value)}
                placeholder={t("dcim.racks.paletteSearch")}
                aria-label={t("dcim.racks.paletteSearch")}
              />
              <p className={styles.filterLabel}>{t("dcim.racks.filterSize")}</p>
              <div className={styles.chipRow}>
                {(["", "1", "2", "4+"] as const).map((sz) => (
                  <button
                    key={sz || "all"}
                    type="button"
                    className={`${styles.chip} ${sizeFilter === sz ? styles.chipOn : ""}`.trim()}
                    onClick={() => setSizeFilter(sz)}
                  >
                    {sz === "" ? t("dcim.racks.filterAll") : sz === "4+" ? t("dcim.racks.size4plus") : `${sz}U`}
                  </button>
                ))}
              </div>
              {vendorItems.length > 0 ? (
                <>
                  <p className={styles.filterLabel}>{t("dcim.racks.filterVendor")}</p>
                  <ChipOverflow
                    items={vendorItems}
                    selected={vendorFilter}
                    onSelect={setVendorFilter}
                    allLabel={t("dcim.racks.filterAll")}
                    moreLabel={t("dcim.racks.filterMore")}
                    lessLabel={t("dcim.racks.filterLess")}
                    searchLabel={t("dcim.racks.filterChipSearch")}
                  />
                </>
              ) : null}
              {typeItems.length > 0 ? (
                <>
                  <p className={styles.filterLabel}>{t("dcim.racks.filterCategory")}</p>
                  <ChipOverflow
                    items={typeItems}
                    selected={typeFilter}
                    onSelect={setTypeFilter}
                    allLabel={t("dcim.racks.filterAll")}
                    moreLabel={t("dcim.racks.filterMore")}
                    lessLabel={t("dcim.racks.filterLess")}
                    searchLabel={t("dcim.racks.filterChipSearch")}
                  />
                </>
              ) : null}
            </div>
            <div className={styles.paletteList}>
              {paletteTab === "devices" ? (
                unplacedDevices.length === 0 ? (
                  <p className={baseStyles.muted}>{t("dcim.racks.paletteEmpty")}</p>
                ) : filteredUnplaced.length === 0 ? (
                  <p className={baseStyles.muted}>{t("dcim.racks.paletteFilterEmpty")}</p>
                ) : (
                  filteredUnplaced.map((d) => {
                    const uh = deviceUHeight(d, modelsById);
                    const mod = d.device_model_id != null ? modelsById.get(d.device_model_id) : undefined;
                    const vendor = mod?.manufacturer_id != null ? mfrById.get(mod.manufacturer_id) : undefined;
                    const typeName = typeById.get(d.effective_device_type_id ?? mod?.device_type_id ?? -1);
                    return (
                      <div
                        key={d.id}
                        className={`${styles.paletteItem} ${armed?.kind === "device" && armed.id === d.id ? styles.paletteItemArmed : ""}`.trim()}
                        draggable
                        onClick={() => setArmed({ kind: "device", id: d.id })}
                        onDragStart={(e) => {
                          setArmed({ kind: "device", id: d.id });
                          setDragging({ kind: "device", id: d.id });
                          e.dataTransfer.effectAllowed = "copy";
                          e.dataTransfer.setData("text/plain", `device:${d.id}`);
                        }}
                        onDragEnd={() => {
                          setDragging(null);
                          setDragOverKey(null);
                        }}
                      >
                        <span className={styles.paletteItemRow}>
                          {mod && deviceModelRackFaceSrc(mod) ? (
                            <img src={deviceModelRackFaceSrc(mod)!} alt="" className={styles.modelThumb} draggable={false} />
                          ) : null}
                          <span>
                            <span className={styles.paletteItemName}>{d.name}</span>
                            <span className={styles.paletteItemMeta}>
                              {[vendor, typeName].filter(Boolean).join(" · ")}
                            </span>
                          </span>
                        </span>
                        <span className={styles.uBadge}>{uh}U</span>
                      </div>
                    );
                  })
                )
              ) : (modelsQ.data ?? []).length === 0 ? (
                <p className={baseStyles.muted}>{t("dcim.racks.paletteModelsEmpty")}</p>
              ) : filteredModels.length === 0 ? (
                <p className={baseStyles.muted}>{t("dcim.racks.paletteFilterEmpty")}</p>
              ) : (
                filteredModels.map((m) => (
                  <div
                    key={m.id}
                    className={`${styles.paletteItem} ${armed?.kind === "model" && armed.id === m.id ? styles.paletteItemArmed : ""}`.trim()}
                    draggable
                    onClick={() => setArmed({ kind: "model", id: m.id })}
                    onDragStart={(e) => {
                      setArmed({ kind: "model", id: m.id });
                      setDragging({ kind: "model", id: m.id });
                      e.dataTransfer.effectAllowed = "copy";
                      e.dataTransfer.setData("text/plain", `model:${m.id}`);
                    }}
                    onDragEnd={() => {
                      setDragging(null);
                      setDragOverKey(null);
                    }}
                  >
                    <span className={styles.paletteItemRow}>
                      {deviceModelRackFaceSrc(m) ? (
                        <img src={deviceModelRackFaceSrc(m)!} alt="" className={styles.modelThumb} draggable={false} />
                      ) : null}
                      <span>
                        <span className={styles.paletteItemName}>{m.name}</span>
                        <span className={styles.paletteItemMeta}>
                          {[mfrById.get(m.manufacturer_id ?? -1), typeById.get(m.device_type_id ?? -1)]
                            .filter(Boolean)
                            .join(" · ")}
                        </span>
                      </span>
                    </span>
                    <span className={styles.uBadge}>{m.u_height}U</span>
                  </div>
                ))
              )}
            </div>
          </aside>
        )}

        <div className={styles.rackWorkspace}>
          <div className={styles.rackWorkspaceHead}>
            <strong>{t("dcim.racks.rackView")}</strong>
            <div className={styles.toolbarGroup} role="group">
              <button
                type="button"
                className={`${styles.toolbarBtn} ${!compact ? styles.toolbarBtnOn : ""}`.trim()}
                onClick={() => setCompact(false)}
              >
                {t("dcim.racks.viewNormal")}
              </button>
              <button
                type="button"
                className={`${styles.toolbarBtn} ${compact ? styles.toolbarBtnOn : ""}`.trim()}
                onClick={() => setCompact(true)}
              >
                {t("dcim.racks.viewCompact")}
              </button>
            </div>
          </div>
          <div
            className={`${styles.rackMatrix} ${compact ? styles.rackMatrixCompact : ""}`.trim()}
            style={{
              gridTemplateColumns:
                visibleRacks.length <= 3
                  ? `repeat(${Math.max(visibleRacks.length, 1)}, minmax(0, 1fr))`
                  : `repeat(auto-fill, minmax(${colMin}px, 1fr))`,
            }}
          >
            {visibleRacks.map((rack) => (
              <RackElevation
                key={rack.id}
                rack={rack}
                t={t}
                allPlacements={allPlacements}
                devicesById={devicesById}
                modelsById={modelsById}
                dragging={dragging}
                setDragging={setDragging}
                dragOverKey={dragOverKey}
                setDragOverKey={setDragOverKey}
                highlightPlacementId={highlightPlacementId}
                selectedPlacementId={selectedPlacementId}
                onSelectPlacement={(p) => {
                  setSelectedPlacementId(p?.id ?? null);
                  setSelectedRackId(null);
                }}
                selectedRackId={selectedRackId}
                onSelectRack={(id) => {
                  setSelectedRackId(id);
                  setSelectedPlacementId(null);
                }}
                columnU={columnU}
                compact={compact}
                roomLabel={roomLabelForRack(rack)}
                conflictIds={conflictIds}
                onDropDevice={(rackId, deviceId, u) => {
                  placeDeviceMu.mutate({ rack_id: rackId, device_id: deviceId, u_position: u });
                }}
                onDropModel={(rackId, modelId, u) => {
                  placeFromModelMu.mutate({ rackId, modelId, u });
                }}
                onMovePlacement={(pid, rackId, u) => {
                  patchPlacementMu.mutate({ pid, rack_id: rackId, u_position: u });
                }}
                onEditPlacement={setEditorPlacement}
                onPlacementMountingChange={(pid, mounting) => {
                  patchPlacementMu.mutate({ pid, mounting });
                }}
                onRemovePlacement={(id) => removeMu.mutate(id)}
                removePending={removeMu.isPending}
              />
            ))}
          </div>
        </div>

        <aside className={styles.details}>
          <div className={styles.detailsHead}>
            <h3 className={styles.detailsTitle}>
              {selectedDetailRack ? t("dcim.racks.detailsRackTitle") : t("dcim.racks.detailsTitle")}
            </h3>
            {selectedPlacement || selectedDetailRack ? (
              <button
                type="button"
                className={styles.toolbarBtn}
                onClick={() => {
                  setSelectedPlacementId(null);
                  setSelectedRackId(null);
                }}
              >
                {t("dcim.racks.closeDetails")}
              </button>
            ) : null}
          </div>
          {selectedDetailRack ? (
            <>
              <div className={styles.detailsHero}>
                <div>
                  <strong>{selectedDetailRack.name}</strong>
                  <div className={styles.paletteItemMeta}>{dash(roomLabelForRack(selectedDetailRack))}</div>
                </div>
              </div>
              <dl className={styles.detailsDl}>
                <dt>{t("dcim.racks.detailRack")}</dt>
                <dd>
                  {selectedDetailRack.name} ({selectedDetailRack.u_height}U)
                </dd>
                <dt>{t("dcim.racks.detailLocation")}</dt>
                <dd>{dash(roomLabelForRack(selectedDetailRack))}</dd>
                <dt>{t("dcim.racks.powerFeeds")}</dt>
                <dd>
                  {(rackFeedsQ.data ?? []).length === 0
                    ? t("dcim.racks.noFeeds")
                    : (rackFeedsQ.data ?? []).map((f) => `${f.name} (${f.status})`).join(", ")}
                </dd>
                <dt>{t("dcim.racks.brand")}</dt>
                <dd>{dash(selectedDetailRack.brand)}</dd>
                <dt>{t("dcim.racks.tableDims")}</dt>
                <dd>
                  {selectedDetailRack.height_mm ?? "—"}×{selectedDetailRack.width_mm ?? "—"}×
                  {selectedDetailRack.depth_mm ?? "—"}
                </dd>
                <dt>{t("dcim.racks.mounting")}</dt>
                <dd>
                  <div className={styles.toolbarGroup} role="group" aria-label={t("dcim.racks.mounting")}>
                    <button
                      type="button"
                      className={`${styles.toolbarBtn} ${rackMounting(selectedDetailRack) === "floor" ? styles.toolbarBtnOn : ""}`.trim()}
                      onClick={() => {
                        if (rackMounting(selectedDetailRack) !== "floor") {
                          patchRackMu.mutate({ id: selectedDetailRack.id, mounting: "floor", elevation_mm: null });
                        }
                      }}
                    >
                      {t("dcim.racks.mountFloor")}
                    </button>
                    <button
                      type="button"
                      className={`${styles.toolbarBtn} ${rackMounting(selectedDetailRack) === "wall" ? styles.toolbarBtnOn : ""}`.trim()}
                      onClick={() => {
                        if (rackMounting(selectedDetailRack) !== "wall") {
                          patchRackMu.mutate({ id: selectedDetailRack.id, mounting: "wall" });
                        }
                      }}
                    >
                      {t("dcim.racks.mountWall")}
                    </button>
                  </div>
                </dd>
                {rackMounting(selectedDetailRack) === "wall" ? (
                  <>
                    <dt>{t("dcim.racks.elevationMm")}</dt>
                    <dd>
                      <input
                        className={styles.paletteSearch}
                        type="number"
                        min={0}
                        max={100000}
                        value={elevDraft}
                        onChange={(e) => setElevDraft(e.target.value)}
                        onBlur={() => {
                          const raw = elevDraft.trim();
                          if (raw === "") {
                            patchRackMu.mutate({ id: selectedDetailRack.id, elevation_mm: null });
                            return;
                          }
                          const n = Number(raw);
                          if (!Number.isFinite(n) || n < 0) return;
                          const mm = Math.trunc(n);
                          if (mm === (selectedDetailRack.elevation_mm ?? null)) return;
                          patchRackMu.mutate({ id: selectedDetailRack.id, elevation_mm: mm });
                        }}
                        aria-label={t("dcim.racks.elevationMm")}
                      />
                      <span className={styles.paletteItemMeta}>
                        {t("dcim.racks.elevationHint")}
                        {elevDraft.trim() !== "" && Number.isFinite(Number(elevDraft))
                          ? ` ${t("dcim.racks.elevationApproxU", { u: String(Math.round(Number(elevDraft) / MM_PER_U)) })}`
                          : ""}
                      </span>
                    </dd>
                  </>
                ) : null}
                <dt>{t("dcim.racks.notes")}</dt>
                <dd>{dash(selectedDetailRack.notes)}</dd>
              </dl>
            </>
          ) : selectedPlacement && selectedDevice && selectedRack ? (
            <>
              <div className={styles.detailsHero}>
                {selectedThumb ? <img src={selectedThumb} alt="" /> : null}
                <div>
                  <strong>{selectedDevice.name}</strong>
                  <div className={styles.paletteItemMeta}>{dash(selectedModel?.name)}</div>
                </div>
              </div>
              <dl className={styles.detailsDl}>
                <dt>{t("dcim.equip.dev.hostname")}</dt>
                <dd>{selectedDevice.name}</dd>
                <dt>{t("dcim.racks.detailModel")}</dt>
                <dd>{dash(selectedModel?.name)}</dd>
                <dt>{t("dcim.racks.detailVendor")}</dt>
                <dd>{dash(selectedModel?.manufacturer_id != null ? mfrById.get(selectedModel.manufacturer_id) : undefined)}</dd>
                <dt>{t("dcim.racks.detailType")}</dt>
                <dd>{dash(selectedTypeId != null ? typeById.get(selectedTypeId) : undefined)}</dd>
                <dt>{t("dcim.racks.detailU")}</dt>
                <dd>
                  {selectedRange} · {selectedUHeight}U
                </dd>
                <dt>{t("dcim.racks.detailSide")}</dt>
                <dd>
                  <div className={styles.toolbarGroup} role="group" aria-label={t("dcim.racks.detailSide")}>
                    <button
                      type="button"
                      className={`${styles.toolbarBtn} ${selectedPlacement.mounting !== "rear" ? styles.toolbarBtnOn : ""}`.trim()}
                      onClick={() => {
                        if (selectedPlacement.mounting !== "front") {
                          patchPlacementMu.mutate({ pid: selectedPlacement.id, mounting: "front" });
                        }
                      }}
                    >
                      {t("dcim.racks.viewFront")}
                    </button>
                    <button
                      type="button"
                      className={`${styles.toolbarBtn} ${selectedPlacement.mounting === "rear" ? styles.toolbarBtnOn : ""}`.trim()}
                      onClick={() => {
                        if (selectedPlacement.mounting !== "rear") {
                          patchPlacementMu.mutate({ pid: selectedPlacement.id, mounting: "rear" });
                        }
                      }}
                    >
                      {t("dcim.racks.viewRear")}
                    </button>
                  </div>
                </dd>
                <dt>{t("dcim.racks.detailRack")}</dt>
                <dd>
                  {selectedRack.name} ({selectedRack.u_height}U)
                </dd>
                <dt>{t("dcim.racks.detailLocation")}</dt>
                <dd>{dash(roomLabelForRack(selectedRack))}</dd>
                <dt>{t("dcim.equip.dev.serial")}</dt>
                <dd>{dash(selectedDevice.serial_number)}</dd>
                <dt>{t("dcim.equip.dev.assetTag")}</dt>
                <dd>{dash(selectedDevice.asset_tag)}</dd>
              </dl>
              <div className={styles.detailsActions}>
                <button type="button" className={baseStyles.btn} onClick={() => setEditorPlacement(selectedPlacement)}>
                  {t("dcim.racks.movePlacement")}
                </button>
                <button
                  type="button"
                  className={baseStyles.btnDanger}
                  disabled={removeMu.isPending}
                  onClick={() => removeMu.mutate(selectedPlacement.id)}
                >
                  {t("dcim.common.remove")}
                </button>
                <Link to={`/dcim/equipment/devices/${selectedDevice.id}`} className={baseStyles.btn}>
                  {t("dcim.racks.openDevice")}
                </Link>
                <Link
                  to={catalogProvisionHref(selectedDevice.id)}
                  className={baseStyles.btn}
                  title={t("catalog.provisionHint")}
                >
                  {t("catalog.provision")}
                </Link>
              </div>
            </>
          ) : (
            <p className={baseStyles.muted}>{t("dcim.racks.detailsEmpty")}</p>
          )}
        </aside>
      </div>

      <div className={styles.statusBar}>
        <span>{t("dcim.racks.statusBarRacks", { count: String(visibleRacks.length) })}</span>
        <span>
          {t("dcim.racks.statusBarUsed", { used: String(usedU.used), total: String(usedU.total) })}
        </span>
        <span>{t("dcim.racks.statusBarFree", { free: String(usedU.free) })}</span>
        <span className={issues.length === 0 ? styles.statusOk : styles.statusWarn}>
          {issues.length === 0
            ? t("dcim.racks.validationOk")
            : t("dcim.racks.validationIssues", { count: String(issues.length) })}
        </span>
      </div>

      {editorPlacement ? (
        <PlacementEditorDialog
          key={editorPlacement.id}
          placement={editorPlacement}
          racks={racks}
          allPlacements={allPlacements}
          devicesById={devicesById}
          modelsById={modelsById}
          t={t}
          saving={patchPlacementMu.isPending}
          onClose={() => setEditorPlacement(null)}
          onApply={(rack_id, u_position, mounting) => {
            patchPlacementMu.mutate(
              { pid: editorPlacement.id, rack_id, u_position, mounting },
              { onSuccess: () => setEditorPlacement(null) },
            );
          }}
        />
      ) : null}
    </div>,
  );
}
