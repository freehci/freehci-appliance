import type { DragEvent, ReactNode } from "react";
import { useEffect, useRef } from "react";
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
import { deviceModelBackSrc, deviceModelRackFaceSrc } from "./modelImages";
import styles from "./RackPlanner.module.css";

export type DragPayload =
  | { kind: "device"; id: number }
  | { kind: "model"; id: number }
  | { kind: "placement"; placementId: number; sourceRackId: number }
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
  onMovePlacement: (placementId: number, rackId: number, uPosition: number) => void;
  onEditPlacement: (placement: RackPlacement) => void;
  onPlacementMountingChange: (placementId: number, mounting: string) => void;
  onRemovePlacement: (placementId: number) => void;
  removePending: boolean;
  highlightPlacementId?: number;
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
  onMovePlacement,
  onEditPlacement,
  onPlacementMountingChange,
  onRemovePlacement,
  removePending,
  highlightPlacementId,
}: Props) {
  const n = rack.u_height;
  const stageRef = useRef<HTMLDivElement | null>(null);

  const rackPlacements = allPlacements.filter((p) => p.rack_id === rack.id);
  const isHighlightedRack =
    highlightPlacementId != null && rackPlacements.some((p) => p.id === highlightPlacementId);

  useEffect(() => {
    if (!isHighlightedRack) return;
    stageRef.current?.scrollIntoView({ behavior: "smooth", block: "center" });
  }, [isHighlightedRack, highlightPlacementId, rack.id]);

  const excludePlacementId =
    dragging?.kind === "placement" && dragging.sourceRackId === rack.id
      ? dragging.placementId
      : undefined;

  const existingRanges = existingRangesForRack(
    allPlacements,
    rack.id,
    devicesById,
    modelsById,
    excludePlacementId,
  );

  const dragDeviceU = (): number | null => {
    if (!dragging) return null;
    if (dragging.kind === "placement") {
      const pl = allPlacements.find((x) => x.id === dragging.placementId);
      if (!pl) return null;
      const d = devicesById.get(pl.device_id);
      return d ? deviceUHeight(d, modelsById) : null;
    }
    if (dragging.kind === "device") {
      const d = devicesById.get(dragging.id);
      return d ? deviceUHeight(d, modelsById) : null;
    }
    const m = modelsById.get(dragging.id);
    return m !== undefined ? m.u_height : null;
  };

  const slotAllowsDrop = (u: number): boolean => {
    if (!dragging) return false;
    const h = dragDeviceU();
    if (h === null) return false;
    if (h === 0) return false;
    if (isInsideAnyRange(u, existingRanges)) return false;
    return canPlaceDeviceAt(u, h, n, existingRanges);
  };

  const keyFor = (u: number) => `${rack.id}:${u}`;
  const zeroKey = `${rack.id}:0u`;

  const zeroSlotAllowsDrop = (): boolean => {
    if (!dragging) return false;
    const h = dragDeviceU();
    return h === 0;
  };

  const handleZeroDragOver = (e: DragEvent) => {
    if (!dragging) return;
    if (zeroSlotAllowsDrop()) {
      e.preventDefault();
      e.dataTransfer.dropEffect = dragging.kind === "placement" ? "move" : "copy";
      setDragOverKey(zeroKey);
    } else {
      e.dataTransfer.dropEffect = "none";
      setDragOverKey(null);
    }
  };

  const handleZeroDrop = (e: DragEvent) => {
    e.preventDefault();
    setDragOverKey(null);
    if (!dragging || !zeroSlotAllowsDrop()) {
      setDragging(null);
      return;
    }
    if (dragging.kind === "device") {
      onDropDevice(rack.id, dragging.id, 0);
    } else if (dragging.kind === "model") {
      onDropModel(rack.id, dragging.id, 0);
    } else {
      onMovePlacement(dragging.placementId, rack.id, 0);
    }
    setDragging(null);
  };

  const zeroPlacements = rackPlacements.filter((p) => {
    const dev = devicesById.get(p.device_id);
    if (!dev) return false;
    return deviceUHeight(dev, modelsById) === 0;
  });

  const showZeroStrip = zeroPlacements.length > 0 || zeroSlotAllowsDrop();

  const handleDragOverSlot = (e: DragEvent, u: number) => {
    if (!dragging) return;
    if (slotAllowsDrop(u)) {
      e.preventDefault();
      e.dataTransfer.dropEffect = dragging.kind === "placement" ? "move" : "copy";
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
    } else if (dragging.kind === "model") {
      onDropModel(rack.id, dragging.id, u);
    } else {
      onMovePlacement(dragging.placementId, rack.id, u);
    }
    setDragging(null);
  };

  const slots: ReactNode[] = [];
  for (let u = 1; u <= n; u += 1) {
    const rowFromTop = n - u + 1;
    const occupied = isInsideAnyRange(u, existingRanges);
    const showDrop = Boolean(dragging) && !occupied && slotAllowsDrop(u);
    const dragActive = dragOverKey === keyFor(u);
    const placementDrag = dragging?.kind === "placement";
    slots.push(
      <div
        key={`slot-${u}`}
        className={[
          styles.gridSlot,
          occupied ? styles.slotBlocked : showDrop ? styles.slotDroppable : "",
          showDrop && placementDrag ? styles.slotDroppableMove : "",
          dragActive ? styles.slotDragOver : "",
          dragActive && placementDrag ? styles.slotDragOverMove : "",
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
    if (h === 0) return null;
    const rowStart = gridRowStartForPlacement(n, p.u_position, h);
    const { bottom, top } = occupiesRange(p.u_position, h);
    const mod = dev.device_model_id != null ? modelsById.get(dev.device_model_id) : undefined;
    const isRear = p.mounting === "rear";
    const thumbSrc = mod
      ? isRear
        ? deviceModelBackSrc(mod) ?? deviceModelRackFaceSrc(mod)
        : deviceModelRackFaceSrc(mod)
      : null;
    return (
      <div
        key={p.id}
        className={[
          styles.deviceBlockGrid,
          isRear ? styles.deviceBlockRear : styles.deviceBlockFront,
          dragging?.kind === "placement" && dragging.placementId === p.id
            ? styles.deviceBlockDragging
            : "",
          highlightPlacementId === p.id ? styles.deviceBlockHighlight : "",
        ]
          .join(" ")
          .trim()}
        style={{ gridRow: `${rowStart} / span ${h}`, gridColumn: 1 }}
        draggable
        onDragStart={(e) => {
          const el = e.target as HTMLElement;
          if (el.closest("button, select, [data-rack-no-drag]")) {
            e.preventDefault();
            return;
          }
          setDragging({ kind: "placement", placementId: p.id, sourceRackId: rack.id });
          e.dataTransfer.effectAllowed = "move";
          e.dataTransfer.setData("text/plain", `placement:${p.id}`);
        }}
        onDragEnd={() => {
          setDragging(null);
          setDragOverKey(null);
        }}
      >
        <span
          className={isRear ? styles.mountBadgeRear : styles.mountBadgeFront}
          title={isRear ? t("dcim.equip.mountRear") : t("dcim.equip.mountFront")}
          aria-hidden
        >
          {isRear ? "R" : "F"}
        </span>
        {thumbSrc ? (
          <img
            src={thumbSrc}
            alt=""
            className={[styles.deviceThumb, isRear ? styles.deviceThumbRear : ""].join(" ").trim()}
            draggable={false}
          />
        ) : null}
        <div className={styles.deviceBlockInner}>
          <div className={styles.deviceBlockText}>
            <div className={styles.deviceName}>{dev.name}</div>
            <div className={styles.deviceMeta}>
              U{bottom}–{top} · {h}U · {p.mounting}
            </div>
            <label className={styles.deviceMountLabel}>
              <span className={styles.srOnly}>{t("dcim.racks.editorMount")}</span>
              <select
                value={p.mounting === "rear" ? "rear" : "front"}
                onChange={(e) => onPlacementMountingChange(p.id, e.target.value)}
                className={styles.deviceMountSelect}
                data-rack-no-drag=""
                aria-label={t("dcim.racks.editorMount")}
              >
                <option value="front">{t("dcim.equip.mountFront")}</option>
                <option value="rear">{t("dcim.equip.mountRear")}</option>
              </select>
            </label>
          </div>
          <div className={styles.deviceActions} data-rack-no-drag="">
            <button
              type="button"
              className={styles.adjustBtn}
              title={t("dcim.racks.adjustPlacementAria")}
              aria-label={t("dcim.racks.adjustPlacementAria")}
              draggable={false}
              onClick={() => onEditPlacement(p)}
            >
              {t("dcim.racks.adjustPlacement")}
            </button>
            <button
              type="button"
              className={styles.removeBtn}
              title={t("dcim.racks.removePlacementAria")}
              aria-label={t("dcim.racks.removePlacementAria")}
              disabled={removePending}
              draggable={false}
              onClick={() => onRemovePlacement(p.id)}
            >
              ×
            </button>
          </div>
        </div>
      </div>
    );
  });

  const zeroOverlays: ReactNode[] = [];
  for (const p of zeroPlacements) {
    const dev = devicesById.get(p.device_id);
    if (!dev) continue;
    const mod = dev.device_model_id != null ? modelsById.get(dev.device_model_id) : undefined;
    const isRear = p.mounting === "rear";
    const thumbSrc = mod
      ? isRear
        ? deviceModelBackSrc(mod) ?? deviceModelRackFaceSrc(mod)
        : deviceModelRackFaceSrc(mod)
      : null;
    zeroOverlays.push(
      <div
        key={`zero-${p.id}`}
        className={[
          styles.deviceBlockZeroU,
          styles.deviceBlockGrid,
          isRear ? styles.deviceBlockRear : styles.deviceBlockFront,
          dragging?.kind === "placement" && dragging.placementId === p.id ? styles.deviceBlockDragging : "",
          highlightPlacementId === p.id ? styles.deviceBlockHighlight : "",
        ]
          .join(" ")
          .trim()}
        draggable
        onDragStart={(e) => {
          const el = e.target as HTMLElement;
          if (el.closest("button, select, [data-rack-no-drag]")) {
            e.preventDefault();
            return;
          }
          setDragging({ kind: "placement", placementId: p.id, sourceRackId: rack.id });
          e.dataTransfer.effectAllowed = "move";
          e.dataTransfer.setData("text/plain", `placement:${p.id}`);
        }}
        onDragEnd={() => {
          setDragging(null);
          setDragOverKey(null);
        }}
      >
        <span
          className={isRear ? styles.mountBadgeRear : styles.mountBadgeFront}
          title={isRear ? t("dcim.equip.mountRear") : t("dcim.equip.mountFront")}
          aria-hidden
        >
          {isRear ? "R" : "F"}
        </span>
        {thumbSrc ? (
          <img
            src={thumbSrc}
            alt=""
            className={[styles.deviceThumb, isRear ? styles.deviceThumbRear : ""].join(" ").trim()}
            draggable={false}
          />
        ) : null}
        <div className={styles.deviceBlockInner}>
          <div className={styles.deviceBlockText}>
            <div className={styles.deviceName}>{dev.name}</div>
            <div className={styles.deviceMeta}>
              {t("dcim.racks.zeroUDeviceMeta").replace(/\{mount\}/g, p.mounting)}
            </div>
            <label className={styles.deviceMountLabel}>
              <span className={styles.srOnly}>{t("dcim.racks.editorMount")}</span>
              <select
                value={p.mounting === "rear" ? "rear" : "front"}
                onChange={(e) => onPlacementMountingChange(p.id, e.target.value)}
                className={styles.deviceMountSelect}
                data-rack-no-drag=""
                aria-label={t("dcim.racks.editorMount")}
              >
                <option value="front">{t("dcim.equip.mountFront")}</option>
                <option value="rear">{t("dcim.equip.mountRear")}</option>
              </select>
            </label>
          </div>
          <div className={styles.deviceActions} data-rack-no-drag="">
            <button
              type="button"
              className={styles.adjustBtn}
              title={t("dcim.racks.adjustPlacementAria")}
              aria-label={t("dcim.racks.adjustPlacementAria")}
              draggable={false}
              onClick={() => onEditPlacement(p)}
            >
              {t("dcim.racks.adjustPlacement")}
            </button>
            <button
              type="button"
              className={styles.removeBtn}
              title={t("dcim.racks.removePlacementAria")}
              aria-label={t("dcim.racks.removePlacementAria")}
              disabled={removePending}
              draggable={false}
              onClick={() => onRemovePlacement(p.id)}
            >
              ×
            </button>
          </div>
        </div>
      </div>,
    );
  }

  const zeroStripDroppable = Boolean(dragging) && zeroSlotAllowsDrop();
  const zeroStripActive = dragOverKey === zeroKey;

  return (
    <div
      ref={stageRef}
      className={[styles.rackStage, isHighlightedRack ? styles.rackStageHighlight : ""].join(" ").trim()}
    >
      <div className={styles.rackStageTitle}>
        {rack.name} ({n}U)
      </div>
      <div className={styles.rackAspect}>
        <div
          className={styles.rackGrid}
          style={{ gridTemplateRows: `repeat(${n}, minmax(0, 1fr))` }}
          role="group"
          aria-label={`${rack.name}, ${n}U`}
        >
          {slots}
          {overlays}
        </div>
        {showZeroStrip ? (
          <div
            className={[
              styles.rackZeroStrip,
              zeroStripDroppable ? styles.rackZeroStripDroppable : "",
              zeroStripActive ? styles.rackZeroStripActive : "",
            ]
              .join(" ")
              .trim()}
            onDragOver={handleZeroDragOver}
            onDragLeave={() => setDragOverKey(null)}
            onDrop={handleZeroDrop}
          >
            <div className={styles.rackZeroStripTitle}>{t("dcim.racks.zeroStripTitle")}</div>
            <p className={styles.rackZeroStripHint}>{t("dcim.racks.zeroStripHint")}</p>
            {zeroOverlays.length > 0 ? (
              <div className={styles.rackZeroStripList}>{zeroOverlays}</div>
            ) : null}
          </div>
        ) : null}
      </div>
    </div>
  );
}
