import type { DragEvent, ReactNode } from "react";
import type { MessageKey } from "@/i18n/messages/en";
import type { DeviceInstance, DeviceModel, Rack, RackPlacement } from "./types";
import {
  canPlaceDeviceAt,
  deviceUHeight,
  existingRangesForRack,
  gridRowStartForPlacement,
  isInsideAnyRange,
  occupiesRange,
} from "./rackUtils";
import styles from "./RackPlanner.module.css";

export type DragPayload =
  | { kind: "device"; id: number }
  | { kind: "model"; id: number }
  | null;

type Props = {
  rack: Rack;
  t: (key: MessageKey) => string;
  allPlacements: RackPlacement[];
  devicesById: Map<number, DeviceInstance>;
  modelsById: Map<number, DeviceModel>;
  dragging: DragPayload;
  setDragging: (d: DragPayload) => void;
  dragOverKey: string | null;
  setDragOverKey: (k: string | null) => void;
  onDropDevice: (rackId: number, deviceId: number, uPosition: number) => void;
  onDropModel: (rackId: number, modelId: number, uPosition: number) => void;
  onRemovePlacement: (placementId: number) => void;
  removePending: boolean;
};

export function RackElevation({
  rack,
  t,
  allPlacements,
  devicesById,
  modelsById,
  dragging,
  setDragging,
  dragOverKey,
  setDragOverKey,
  onDropDevice,
  onDropModel,
  onRemovePlacement,
  removePending,
}: Props) {
  const n = rack.u_height;

  const existingRanges = existingRangesForRack(
    allPlacements,
    rack.id,
    devicesById,
    modelsById,
  );

  const rackPlacements = allPlacements.filter((p) => p.rack_id === rack.id);

  const dragDeviceU = (): number | null => {
    if (!dragging) return null;
    if (dragging.kind === "device") {
      const d = devicesById.get(dragging.id);
      return d ? deviceUHeight(d, modelsById) : null;
    }
    const m = modelsById.get(dragging.id);
    return m?.u_height ?? null;
  };

  const slotAllowsDrop = (u: number): boolean => {
    if (!dragging) return false;
    const h = dragDeviceU();
    if (!h) return false;
    if (isInsideAnyRange(u, existingRanges)) return false;
    return canPlaceDeviceAt(u, h, n, existingRanges);
  };

  const keyFor = (u: number) => `${rack.id}:${u}`;

  const handleDragOverSlot = (e: DragEvent, u: number) => {
    if (!dragging) return;
    if (slotAllowsDrop(u)) {
      e.preventDefault();
      e.dataTransfer.dropEffect = "copy";
      setDragOverKey(keyFor(u));
    } else {
      e.dataTransfer.dropEffect = "none";
      setDragOverKey(null);
    }
  };

  const handleDropSlot = (e: DragEvent, u: number) => {
    e.preventDefault();
    setDragOverKey(null);
    if (!dragging || !slotAllowsDrop(u)) {
      setDragging(null);
      return;
    }
    if (dragging.kind === "device") {
      onDropDevice(rack.id, dragging.id, u);
    } else {
      onDropModel(rack.id, dragging.id, u);
    }
    setDragging(null);
  };

  const slots: ReactNode[] = [];
  for (let u = 1; u <= n; u += 1) {
    const rowFromTop = n - u + 1;
    const occupied = isInsideAnyRange(u, existingRanges);
    const showDrop = Boolean(dragging) && !occupied && slotAllowsDrop(u);
    const dragActive = dragOverKey === keyFor(u);
    slots.push(
      <div
        key={`slot-${u}`}
        className={[
          styles.gridSlot,
          occupied ? styles.slotBlocked : showDrop ? styles.slotDroppable : "",
          dragActive ? styles.slotDragOver : "",
        ]
          .join(" ")
          .trim()}
        style={{ gridRow: rowFromTop, gridColumn: 1 }}
        data-u={u}
        onDragOver={(e) => handleDragOverSlot(e, u)}
        onDragLeave={() => setDragOverKey(null)}
        onDrop={(e) => handleDropSlot(e, u)}
      >
        <span className={styles.slotLabel}>
          {t("dcim.racks.uLabel")}
          {u}
          {occupied ? ` · ${t("dcim.racks.slotBlocked")}` : ""}
        </span>
      </div>,
    );
  }

  const overlays = rackPlacements.map((p) => {
    const dev = devicesById.get(p.device_id);
    if (!dev) return null;
    const h = deviceUHeight(dev, modelsById);
    const rowStart = gridRowStartForPlacement(n, p.u_position, h);
    const { bottom, top } = occupiesRange(p.u_position, h);
    const mod = dev.device_model_id != null ? modelsById.get(dev.device_model_id) : undefined;
    return (
      <div
        key={p.id}
        className={styles.deviceBlockGrid}
        style={{ gridRow: `${rowStart} / span ${h}`, gridColumn: 1 }}
      >
        {mod?.image_front_url ? (
          <img
            src={mod.image_front_url}
            alt=""
            className={styles.deviceThumb}
            draggable={false}
          />
        ) : null}
        <div className={styles.deviceBlockInner}>
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
            disabled={removePending}
            onClick={() => onRemovePlacement(p.id)}
          >
            ×
          </button>
        </div>
      </div>
    );
  });

  return (
    <div className={styles.rackStage}>
      <div className={styles.rackStageTitle}>
        {rack.name} ({n}U)
      </div>
      <div className={styles.rackAspect}>
        <div className={styles.rackGrid} style={{ gridTemplateRows: `repeat(${n}, minmax(0, 1fr))` }}>
          {slots}
          {overlays}
        </div>
      </div>
    </div>
  );
}
