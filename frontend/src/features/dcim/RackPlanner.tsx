import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useCallback, useMemo, useState } from "react";
import { Panel } from "@/components/ui/Panel";
import { useI18n } from "@/i18n/I18nProvider";
import { ApiError } from "@/lib/api";
import * as api from "./dcimApi";
import baseStyles from "./dcim.module.css";
import {
  canPlaceDeviceAt,
  deviceUHeight,
  existingRangesForRack,
  occupiesRange,
} from "./rackUtils";
import styles from "./RackPlanner.module.css";
import type { DeviceInstance, DeviceModel, Rack } from "./types";

function isInsideAnyRange(u: number, ranges: { bottom: number; top: number }[]): boolean {
  for (const r of ranges) {
    if (u >= r.bottom && u <= r.top) return true;
  }
  return false;
}

export function RackPlanner({ racks }: { racks: Rack[] }) {
  const { t } = useI18n();
  const qc = useQueryClient();
  const [rackId, setRackId] = useState<string>("");
  const [draggingDeviceId, setDraggingDeviceId] = useState<number | null>(null);
  const [dragOverU, setDragOverU] = useState<number | null>(null);
  const [dropErr, setDropErr] = useState<string | null>(null);

  const devicesQ = useQuery({ queryKey: ["dcim", "devices"], queryFn: api.listDevices });
  const modelsQ = useQuery({ queryKey: ["dcim", "device-models"], queryFn: api.listDeviceModels });
  const allPlacementsQ = useQuery({
    queryKey: ["dcim", "placements", "all"],
    queryFn: () => api.listPlacements(),
  });

  const selectedRackId = rackId === "" ? undefined : Number(rackId);

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

  const rack: Rack | undefined = useMemo(
    () => racks.find((k) => k.id === selectedRackId),
    [racks, selectedRackId],
  );

  const rackPlacements = useMemo(() => {
    if (!rack) return [];
    return (allPlacementsQ.data ?? []).filter((p) => p.rack_id === rack.id);
  }, [rack, allPlacementsQ.data]);

  const existingRanges = useMemo(() => {
    if (!rack || !allPlacementsQ.data) return [];
    return existingRangesForRack(allPlacementsQ.data, rack.id, devicesById, modelsById);
  }, [rack, allPlacementsQ.data, devicesById, modelsById]);

  const placeMu = useMutation({
    mutationFn: (body: { rack_id: number; device_id: number; u_position: number }) =>
      api.createPlacement({ ...body, mounting: "front" }),
    onSuccess: () => {
      setDropErr(null);
      void qc.invalidateQueries({ queryKey: ["dcim", "placements"] });
    },
    onError: (e: Error) => setDropErr(e instanceof ApiError ? e.message : e.message),
  });

  const removeMu = useMutation({
    mutationFn: (id: number) => api.deletePlacement(id),
    onSuccess: () => {
      setDropErr(null);
      void qc.invalidateQueries({ queryKey: ["dcim", "placements"] });
    },
    onError: (e: Error) => setDropErr(e instanceof ApiError ? e.message : e.message),
  });

  const resolveDragDevice = useCallback((): DeviceInstance | null => {
    if (draggingDeviceId == null) return null;
    return devicesById.get(draggingDeviceId) ?? null;
  }, [draggingDeviceId, devicesById]);

  const slotAllowsDrop = useCallback(
    (u: number): boolean => {
      const dev = resolveDragDevice();
      if (!rack || !dev) return false;
      if (isInsideAnyRange(u, existingRanges)) return false;
      const h = deviceUHeight(dev, modelsById);
      return canPlaceDeviceAt(u, h, rack.u_height, existingRanges);
    },
    [rack, resolveDragDevice, modelsById, existingRanges],
  );

  const handleDragOverSlot = (e: React.DragEvent, u: number) => {
    if (!draggingDeviceId || !rack) return;
    if (slotAllowsDrop(u)) {
      e.preventDefault();
      e.dataTransfer.dropEffect = "copy";
      setDragOverU(u);
    } else {
      e.dataTransfer.dropEffect = "none";
      setDragOverU(null);
    }
  };

  const handleDropSlot = (e: React.DragEvent, u: number) => {
    e.preventDefault();
    setDragOverU(null);
    if (!rack || draggingDeviceId == null) return;
    const dev = devicesById.get(draggingDeviceId);
    if (!dev) return;
    if (!slotAllowsDrop(u)) return;
    setDropErr(null);
    placeMu.mutate({ rack_id: rack.id, device_id: dev.id, u_position: u });
    setDraggingDeviceId(null);
  };

  const renderSlots = () => {
    if (!rack) return null;
    const slots: React.ReactNode[] = [];
    for (let u = 1; u <= rack.u_height; u += 1) {
      const occupied = isInsideAnyRange(u, existingRanges);
      const showDrop =
        Boolean(draggingDeviceId) && !occupied && slotAllowsDrop(u);
      const dragActive = dragOverU === u;
      slots.push(
        <div
          key={u}
          className={[
            styles.slot,
            occupied ? styles.blocked : showDrop ? styles.droppable : "",
            dragActive ? styles.dragOver : "",
          ]
            .join(" ")
            .trim()}
          data-u={u}
          onDragOver={(e) => handleDragOverSlot(e, u)}
          onDragLeave={() => setDragOverU(null)}
          onDrop={(e) => handleDropSlot(e, u)}
        >
          {t("dcim.racks.uLabel")}
          {u}
          {occupied ? ` · ${t("dcim.racks.slotBlocked")}` : ""}
        </div>,
      );
    }
    return slots;
  };

  const renderOverlays = () => {
    if (!rack || rackPlacements.length === 0) return null;
    const n = rack.u_height;
    return rackPlacements.map((p) => {
      const dev = devicesById.get(p.device_id);
      if (!dev) return null;
      const h = deviceUHeight(dev, modelsById);
      const { bottom, top } = occupiesRange(p.u_position, h);
      const heightPct = (h / n) * 100;
      const bottomPct = ((bottom - 1) / n) * 100;
      return (
        <div
          key={p.id}
          className={styles.deviceBlock}
          style={{
            height: `${heightPct}%`,
            bottom: `${bottomPct}%`,
          }}
        >
          <div>
            <div className={styles.deviceName}>{dev.name}</div>
            <div className={styles.deviceMeta}>
              U{bottom}–{top} · {h}U
            </div>
          </div>
          <button
            type="button"
            className={styles.removeBtn}
            title={t("dcim.racks.removePlacementAria")}
            aria-label={t("dcim.racks.removePlacementAria")}
            disabled={removeMu.isPending}
            onClick={() => removeMu.mutate(p.id)}
          >
            ×
          </button>
        </div>
      );
    });
  };

  return (
    <Panel title={t("dcim.racks.plannerTitle")}>
      {dropErr ? <p className={baseStyles.err}>{t("dcim.racks.dropError")} {dropErr}</p> : null}

      <div className={styles.selectRow}>
        <label className={baseStyles.muted} style={{ display: "block", marginBottom: "var(--space-1)" }}>
          {t("dcim.racks.selectRack")}
        </label>
        <select
          value={rackId}
          onChange={(e) => {
            setRackId(e.target.value);
            setDropErr(null);
          }}
          aria-label={t("dcim.racks.selectRack")}
        >
          <option value="">{t("dcim.common.choose")}</option>
          {racks.map((k) => (
            <option key={k.id} value={String(k.id)}>
              #{k.id} {k.name} ({k.u_height}U)
            </option>
          ))}
        </select>
        {!rackId ? <p className={styles.hint}>{t("dcim.racks.selectRackHint")}</p> : null}
      </div>

      {rack ? (
        <div className={styles.planner}>
          <aside className={styles.palette}>
            <h3 className={styles.paletteTitle}>{t("dcim.racks.paletteTitle")}</h3>
            <p className={styles.paletteHint}>{t("dcim.racks.paletteHint")}</p>
            <div className={styles.paletteList}>
              {unplacedDevices.length === 0 ? (
                <p className={baseStyles.muted}>{t("dcim.racks.paletteEmpty")}</p>
              ) : (
                unplacedDevices.map((d) => {
                  const uh = deviceUHeight(d, modelsById);
                  return (
                    <div
                      key={d.id}
                      className={styles.paletteItem}
                      draggable
                      onDragStart={(e) => {
                        setDraggingDeviceId(d.id);
                        e.dataTransfer.effectAllowed = "copy";
                        e.dataTransfer.setData("text/plain", String(d.id));
                      }}
                      onDragEnd={() => {
                        setDraggingDeviceId(null);
                        setDragOverU(null);
                      }}
                    >
                      <span>{d.name}</span>
                      <span className={styles.uBadge}>{uh}U</span>
                    </div>
                  );
                })
              )}
            </div>
          </aside>

          <div className={styles.rackColumn}>
            <h3 className={styles.rackHeader}>
              {rack.name}
              {" · "}
              {t("dcim.racks.frontView")}
            </h3>
            <div className={styles.rackFrame}>
              <div className={styles.rackSlots}>{renderSlots()}</div>
              <div className={styles.overlays}>{renderOverlays()}</div>
            </div>
          </div>
        </div>
      ) : null}
    </Panel>
  );
}
