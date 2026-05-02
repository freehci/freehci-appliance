import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { ApiError } from "@/lib/api";
import { useI18n } from "@/i18n/I18nProvider";
import * as api from "./dcimApi";
import {
  DcimComponentSpecEditor,
  componentFieldsForClass,
  specsFromDraft,
} from "./DcimComponentSpecEditor";
import styles from "./dcim.module.css";
import type { DeviceInstanceComponent, DeviceModelComponent } from "./types";

type OwnerComponent = DeviceModelComponent | DeviceInstanceComponent;

type OwnerKind = "model" | "device";

export function DcimOwnerComponentsPanel({
  ownerKind,
  ownerId,
  canCopyFromModel = false,
  onError,
}: {
  ownerKind: OwnerKind;
  ownerId: number;
  canCopyFromModel?: boolean;
  onError: (msg: string | null) => void;
}) {
  const { t } = useI18n();
  const qc = useQueryClient();
  const [componentId, setComponentId] = useState("");
  const [quantity, setQuantity] = useState("1");
  const [slotLabel, setSlotLabel] = useState("");
  const [serial, setSerial] = useState("");
  const [asset, setAsset] = useState("");
  const [notes, setNotes] = useState("");
  const [overrideDraft, setOverrideDraft] = useState<Record<string, string>>({});

  const classesQ = useQuery({ queryKey: ["dcim", "component-classes"], queryFn: api.listComponentClasses });
  const componentsQ = useQuery({ queryKey: ["dcim", "components"], queryFn: () => api.listComponents() });
  const fieldsQueries = useQuery({
    queryKey: ["dcim", "component-class-fields", "all-for-owner-panel", classesQ.data?.map((x) => x.id).join(",") ?? ""],
    queryFn: async () => {
      const rows = await Promise.all((classesQ.data ?? []).map((c) => api.listComponentClassFields(c.id)));
      return rows.flat();
    },
    enabled: (classesQ.data ?? []).length > 0,
  });
  const ownerQ = useQuery<OwnerComponent[]>({
    queryKey: ["dcim", ownerKind, ownerId, "components"],
    queryFn: async () =>
      ownerKind === "model"
        ? ((await api.listDeviceModelComponents(ownerId)) as OwnerComponent[])
        : ((await api.listDeviceInstanceComponents(ownerId)) as OwnerComponent[]),
  });

  const componentById = useMemo(() => new Map((componentsQ.data ?? []).map((c) => [c.id, c])), [componentsQ.data]);
  const classNameById = useMemo(() => new Map((classesQ.data ?? []).map((c) => [c.id, c.name])), [classesQ.data]);
  const selectedComponent = componentById.get(Number(componentId));
  const selectedFields = selectedComponent
    ? componentFieldsForClass(fieldsQueries.data ?? [], selectedComponent.class_id)
    : [];

  const invalidate = () => {
    void qc.invalidateQueries({ queryKey: ["dcim", ownerKind, ownerId, "components"] });
    if (ownerKind === "device") void qc.invalidateQueries({ queryKey: ["dcim", "devices", ownerId] });
    else void qc.invalidateQueries({ queryKey: ["dcim", "device-models", ownerId] });
  };
  const onMutError = (e: Error) => onError(e instanceof ApiError ? e.message : e.message);

  const addM = useMutation<OwnerComponent>({
    mutationFn: async () => {
      const body = {
        component_id: Number(componentId),
        quantity: Number(quantity) || 1,
        slot_label: slotLabel.trim() || null,
        notes: notes.trim() || null,
        overrides_json: specsFromDraft(selectedFields, overrideDraft),
      };
      if (ownerKind === "model") return (await api.createDeviceModelComponent(ownerId, body)) as OwnerComponent;
      return (await api.createDeviceInstanceComponent(ownerId, {
        ...body,
        serial_number: serial.trim() || null,
        asset_tag: asset.trim() || null,
      })) as OwnerComponent;
    },
    onSuccess: () => {
      onError(null);
      setComponentId("");
      setQuantity("1");
      setSlotLabel("");
      setSerial("");
      setAsset("");
      setNotes("");
      setOverrideDraft({});
      invalidate();
    },
    onError: onMutError,
  });
  const delM = useMutation({
    mutationFn: (linkId: number) =>
      ownerKind === "model"
        ? api.deleteDeviceModelComponent(ownerId, linkId)
        : api.deleteDeviceInstanceComponent(ownerId, linkId),
    onSuccess: () => {
      onError(null);
      invalidate();
    },
    onError: onMutError,
  });
  const copyM = useMutation({
    mutationFn: () => api.copyDeviceComponentsFromModel(ownerId),
    onSuccess: () => {
      onError(null);
      invalidate();
    },
    onError: onMutError,
  });
  const materializeM = useMutation({
    mutationFn: (linkId: number) =>
      api.materializeComponentInterfaces(ownerId, { component_link_id: linkId, overwrite_existing: false }),
    onSuccess: () => {
      onError(null);
      invalidate();
      if (ownerKind === "device") void qc.invalidateQueries({ queryKey: ["dcim", "devices", ownerId, "interfaces"] });
    },
    onError: onMutError,
  });

  return (
    <section className={styles.mfrDetailSection} style={{ marginTop: "var(--space-4)" }}>
      <h3 className={styles.mfrDetailSectionTitle}>
        {ownerKind === "model" ? t("dcim.components.modelComponents") : t("dcim.components.deviceComponents")}
      </h3>
      {canCopyFromModel ? (
        <button type="button" className={styles.btnMuted} disabled={copyM.isPending} onClick={() => copyM.mutate()}>
          {t("dcim.components.copyFromModel")}
        </button>
      ) : null}
      <form className={styles.formRow} onSubmit={(e) => { e.preventDefault(); addM.mutate(); }} style={{ marginTop: "var(--space-2)" }}>
        <label>{t("dcim.components.component")}
          <select value={componentId} onChange={(e) => { setComponentId(e.target.value); setOverrideDraft({}); }} required>
            <option value="">{t("dcim.common.choose")}</option>
            {(componentsQ.data ?? []).map((c) => (
              <option key={c.id} value={String(c.id)}>{classNameById.get(c.class_id) ?? "?"}: {c.name}</option>
            ))}
          </select>
        </label>
        <label>{t("dcim.components.quantity")}<input type="number" min={1} value={quantity} onChange={(e) => setQuantity(e.target.value)} /></label>
        <label>{t("dcim.components.slotLabel")}<input value={slotLabel} onChange={(e) => setSlotLabel(e.target.value)} /></label>
        {ownerKind === "device" ? (
          <>
            <label>{t("dcim.components.serialNumber")}<input value={serial} onChange={(e) => setSerial(e.target.value)} /></label>
            <label>{t("dcim.components.assetTag")}<input value={asset} onChange={(e) => setAsset(e.target.value)} /></label>
          </>
        ) : null}
        <label>{t("dcim.components.notes")}<input value={notes} onChange={(e) => setNotes(e.target.value)} /></label>
        <DcimComponentSpecEditor fields={selectedFields} draft={overrideDraft} onChange={setOverrideDraft} compact />
        <button type="submit" className={styles.btn} disabled={addM.isPending}>{t("dcim.components.addComponent")}</button>
      </form>
      {ownerQ.isLoading ? <p className={styles.muted}>{t("dcim.common.loading")}</p> : null}
      <table className={styles.table}>
        <thead>
          <tr><th>{t("dcim.components.className")}</th><th>{t("dcim.components.component")}</th><th>{t("dcim.components.quantity")}</th><th>{t("dcim.components.slotLabel")}</th><th /></tr>
        </thead>
        <tbody>
          {(ownerQ.data ?? []).map((link) => {
            const comp = componentById.get(link.component_id);
            return (
              <tr key={link.id}>
                <td>{comp ? (classNameById.get(comp.class_id) ?? `#${comp.class_id}`) : "—"}</td>
                <td>{comp?.name ?? `#${link.component_id}`}</td>
                <td>{link.quantity}</td>
                <td>{link.slot_label ?? "—"}</td>
                <td>
                  {ownerKind === "device" ? (
                    <button type="button" className={styles.tableIconBtn} title={t("dcim.components.createInterfaces")} aria-label={t("dcim.components.createInterfaces")} onClick={() => materializeM.mutate(link.id)} disabled={materializeM.isPending}>
                      <i className="fas fa-network-wired" aria-hidden />
                    </button>
                  ) : null}
                  <button type="button" className={`${styles.tableIconBtn} ${styles.tableIconBtnDanger}`.trim()} onClick={() => delM.mutate(link.id)}><i className="fas fa-trash-can" aria-hidden /></button>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </section>
  );
}
