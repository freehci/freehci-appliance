import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { Panel } from "@/components/ui/Panel";
import { useI18n } from "@/i18n/I18nProvider";
import { ApiError } from "@/lib/api";
import * as api from "./dcimApi";
import baseStyles from "./dcim.module.css";
import { RackElevation, type DragPayload } from "./RackElevation";
import styles from "./RackPlanner.module.css";
import { deviceUHeight } from "./rackUtils";
import type { DeviceInstance, DeviceModel, Rack } from "./types";

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

export function RackPlanner({ racks }: { racks: Rack[] }) {
  const { t } = useI18n();
  const qc = useQueryClient();
  const [paletteTab, setPaletteTab] = useState<PaletteTab>("devices");
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
      api.createPlacement({ ...body, mounting: "front" }),
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
        mounting: "front",
      });
    },
    onSuccess: () => {
      setDropErr(null);
      void qc.invalidateQueries({ queryKey: ["dcim", "placements"] });
      void qc.invalidateQueries({ queryKey: ["dcim", "devices"] });
    },
    onError: (e: Error) => setDropErr(e instanceof ApiError ? e.message : e.message),
  });

  const movePlacementMu = useMutation({
    mutationFn: (vars: { pid: number; rackId: number; u: number }) =>
      api.updatePlacement(vars.pid, { rack_id: vars.rackId, u_position: vars.u }),
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

  const allPlacements = allPlacementsQ.data ?? [];

  if (racks.length === 0) {
    return (
      <Panel title={t("dcim.racks.plannerTitle")}>
        <p className={baseStyles.muted}>{t("dcim.racks.empty")}</p>
      </Panel>
    );
  }

  return (
    <Panel title={t("dcim.racks.plannerTitle")}>
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
                              return m?.image_front_url ? (
                                <img
                                  src={m.image_front_url}
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
                    {m.image_front_url ? (
                      <img src={m.image_front_url} alt="" className={styles.modelThumb} draggable={false} />
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
              onDropDevice={(rackId, deviceId, u) => {
                placeDeviceMu.mutate({ rack_id: rackId, device_id: deviceId, u_position: u });
              }}
              onDropModel={(rackId, modelId, u) => {
                placeFromModelMu.mutate({ rackId, modelId, u });
              }}
              onMovePlacement={(pid, rackId, u) => {
                movePlacementMu.mutate({ pid, rackId, u });
              }}
              onRemovePlacement={(id) => removeMu.mutate(id)}
              removePending={removeMu.isPending}
            />
          ))}
        </div>
      </div>
    </Panel>
  );
}
