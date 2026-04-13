import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useMemo, useRef, useState, type FormEvent, type ReactNode } from "react";
import { Panel } from "@/components/ui/Panel";
import { useI18n } from "@/i18n/I18nProvider";
import type { MessageKey } from "@/i18n/messages/en";
import { ApiError } from "@/lib/api";
import * as api from "./dcimApi";
import baseStyles from "./dcim.module.css";
import { RackElevation, type DragPayload } from "./RackElevation";
import { deviceModelRackFaceSrc } from "./modelImages";
import styles from "./RackPlanner.module.css";
import { canPlaceDeviceAt, deviceUHeight, existingRangesForRack } from "./rackUtils";
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
  const [paletteMount, setPaletteMount] = useState<"front" | "rear">("front");
  const [editorPlacement, setEditorPlacement] = useState<RackPlacement | null>(null);
  const [dragging, setDragging] = useState<DragPayload>(null);
  const [dragOverKey, setDragOverKey] = useState<string | null>(null);
  const [dropErr, setDropErr] = useState<string | null>(null);

  const devicesQ = useQuery({ queryKey: ["dcim", "devices"], queryFn: api.listDevices });
  const modelsQ = useQuery({ queryKey: ["dcim", "device-models"], queryFn: api.listDeviceModels });
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

  const placeDeviceMu = useMutation({
    mutationFn: (body: { rack_id: number; device_id: number; u_position: number }) =>
      api.createPlacement({ ...body, mounting: paletteMount }),
    onSuccess: () => {
      setDropErr(null);
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
        mounting: paletteMount,
      });
    },
    onSuccess: () => {
      setDropErr(null);
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
    onSuccess: () => {
      setDropErr(null);
      void qc.invalidateQueries({ queryKey: ["dcim", "placements"] });
    },
    onError: (e: Error) => setDropErr(e instanceof ApiError ? e.message : e.message),
  });

  const allPlacements = allPlacementsQ.data ?? [];

  const wrap = (body: ReactNode) =>
    embed ? body : <Panel title={t("dcim.racks.plannerTitle")}>{body}</Panel>;

  if (racks.length === 0) {
    return wrap(<p className={baseStyles.muted}>{t("dcim.racks.empty")}</p>);
  }

  return wrap(
    <>
      {dropErr ? (
        <p className={baseStyles.err}>
          {t("dcim.racks.dropError")} {dropErr}
        </p>
      ) : null}

      <p className={styles.hint}>{t("dcim.racks.matrixHint")}</p>

      <div className={styles.planner}>
        <aside className={styles.palette}>
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
          <label className={styles.paletteMountRow}>
            <span className={styles.paletteMountHint}>{t("dcim.racks.paletteMountHint")}</span>
            <select
              value={paletteMount}
              onChange={(e) => setPaletteMount(e.target.value as "front" | "rear")}
              aria-label={t("dcim.racks.paletteMountHint")}
            >
              <option value="front">{t("dcim.equip.mountFront")}</option>
              <option value="rear">{t("dcim.equip.mountRear")}</option>
            </select>
          </label>
          <p className={styles.paletteHint}>
            {paletteTab === "devices" ? t("dcim.racks.paletteHint") : t("dcim.racks.paletteModelsHint")}
          </p>
          <div className={styles.paletteList}>
            {paletteTab === "devices" ? (
              unplacedDevices.length === 0 ? (
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
                        {d.device_model_id != null
                          ? (() => {
                              const m = modelsById.get(d.device_model_id);
                              return m && deviceModelRackFaceSrc(m) ? (
                                <img
                                  src={deviceModelRackFaceSrc(m)!}
                                  alt=""
                                  className={styles.modelThumb}
                                  draggable={false}
                                />
                              ) : null;
                            })()
                          : null}
                        <span>{d.name}</span>
                      </span>
                      <span className={styles.uBadge}>{uh}U</span>
                    </div>
                  );
                })
              )
            ) : (modelsQ.data ?? []).length === 0 ? (
              <p className={baseStyles.muted}>{t("dcim.racks.paletteModelsEmpty")}</p>
            ) : (
              (modelsQ.data ?? []).map((m) => (
                <div
                  key={m.id}
                  className={styles.paletteItem}
                  draggable
                  onDragStart={(e) => {
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
                      <img
                        src={deviceModelRackFaceSrc(m)!}
                        alt=""
                        className={styles.modelThumb}
                        draggable={false}
                      />
                    ) : null}
                    <span>{m.name}</span>
                  </span>
                  <span className={styles.uBadge}>{m.u_height}U</span>
                </div>
              ))
            )}
          </div>
        </aside>

        <div className={styles.rackMatrix}>
          {racks.map((rack) => (
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
    </>,
  );
}
