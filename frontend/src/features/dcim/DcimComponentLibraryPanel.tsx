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

function slugify(s: string): string {
  return s.trim().toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "");
}

export function DcimComponentLibraryPanel({ onError }: { onError: (msg: string | null) => void }) {
  const { t } = useI18n();
  const qc = useQueryClient();
  const [className, setClassName] = useState("");
  const [classSlug, setClassSlug] = useState("");
  const [selectedClassId, setSelectedClassId] = useState("");
  const [fieldKey, setFieldKey] = useState("");
  const [fieldLabel, setFieldLabel] = useState("");
  const [fieldType, setFieldType] = useState("text");
  const [fieldUnit, setFieldUnit] = useState("");
  const [fieldRequired, setFieldRequired] = useState(false);
  const [fieldChoices, setFieldChoices] = useState("");
  const [componentName, setComponentName] = useState("");
  const [componentMfr, setComponentMfr] = useState("");
  const [componentPart, setComponentPart] = useState("");
  const [specDraft, setSpecDraft] = useState<Record<string, string>>({});

  const classesQ = useQuery({ queryKey: ["dcim", "component-classes"], queryFn: api.listComponentClasses });
  const fieldsQ = useQuery({
    queryKey: ["dcim", "component-class-fields", selectedClassId],
    queryFn: () => api.listComponentClassFields(Number(selectedClassId)),
    enabled: selectedClassId !== "",
  });
  const componentsQ = useQuery({ queryKey: ["dcim", "components"], queryFn: () => api.listComponents() });
  const mfrQ = useQuery({ queryKey: ["dcim", "manufacturers"], queryFn: api.listManufacturers });

  const selectedClass = useMemo(
    () => (classesQ.data ?? []).find((x) => x.id === Number(selectedClassId)),
    [classesQ.data, selectedClassId],
  );
  const selectedFields = useMemo(
    () => componentFieldsForClass(fieldsQ.data ?? [], Number(selectedClassId)),
    [fieldsQ.data, selectedClassId],
  );
  const classNameById = useMemo(() => new Map((classesQ.data ?? []).map((x) => [x.id, x.name])), [classesQ.data]);
  const mfrNameById = useMemo(() => new Map((mfrQ.data ?? []).map((x) => [x.id, x.name])), [mfrQ.data]);

  const onMutError = (e: Error) => onError(e instanceof ApiError ? e.message : e.message);

  const createClassM = useMutation({
    mutationFn: () => api.createComponentClass({ name: className.trim(), slug: classSlug.trim() || slugify(className) }),
    onSuccess: (created) => {
      onError(null);
      setClassName("");
      setClassSlug("");
      setSelectedClassId(String(created.id));
      void qc.invalidateQueries({ queryKey: ["dcim", "component-classes"] });
    },
    onError: onMutError,
  });
  const createFieldM = useMutation({
    mutationFn: () =>
      api.createComponentClassField(Number(selectedClassId), {
        key: fieldKey,
        label: fieldLabel,
        data_type: fieldType as never,
        unit: fieldUnit.trim() || null,
        required: fieldRequired,
        sort_order: (fieldsQ.data ?? []).length + 1,
        min_number: null,
        max_number: null,
        choices_json: fieldType === "choice" ? fieldChoices.split(",").map((x) => x.trim()).filter(Boolean) : null,
        default_value: null,
        description: null,
        active: true,
      }),
    onSuccess: () => {
      onError(null);
      setFieldKey("");
      setFieldLabel("");
      setFieldType("text");
      setFieldUnit("");
      setFieldRequired(false);
      setFieldChoices("");
      void qc.invalidateQueries({ queryKey: ["dcim", "component-class-fields", selectedClassId] });
    },
    onError: onMutError,
  });
  const createComponentM = useMutation({
    mutationFn: () =>
      api.createComponent({
        class_id: Number(selectedClassId),
        manufacturer_id: componentMfr === "" ? null : Number(componentMfr),
        name: componentName.trim(),
        part_number: componentPart.trim() || null,
        specs_json: specsFromDraft(selectedFields, specDraft),
      }),
    onSuccess: () => {
      onError(null);
      setComponentName("");
      setComponentMfr("");
      setComponentPart("");
      setSpecDraft({});
      void qc.invalidateQueries({ queryKey: ["dcim", "components"] });
    },
    onError: onMutError,
  });
  const deleteComponentM = useMutation({
    mutationFn: (id: number) => api.deleteComponent(id),
    onSuccess: () => {
      onError(null);
      void qc.invalidateQueries({ queryKey: ["dcim", "components"] });
    },
    onError: onMutError,
  });

  return (
    <>
      <p className={styles.muted} style={{ marginTop: 0 }}>{t("dcim.components.intro")}</p>
      <form className={styles.formRow} onSubmit={(e) => { e.preventDefault(); createClassM.mutate(); }}>
        <label>{t("dcim.components.className")}<input value={className} onChange={(e) => { setClassName(e.target.value); setClassSlug(slugify(e.target.value)); }} required /></label>
        <label>{t("dcim.components.classSlug")}<input value={classSlug} onChange={(e) => setClassSlug(e.target.value)} required /></label>
        <button type="submit" className={styles.btn} disabled={createClassM.isPending}>{t("dcim.common.add")}</button>
      </form>

      <div className={styles.formRow}>
        <label>{t("dcim.components.selectedClass")}
          <select value={selectedClassId} onChange={(e) => { setSelectedClassId(e.target.value); setSpecDraft({}); }}>
            <option value="">{t("dcim.common.choose")}</option>
            {(classesQ.data ?? []).map((c) => <option key={c.id} value={String(c.id)}>{c.name}</option>)}
          </select>
        </label>
      </div>

      {selectedClass ? (
        <>
          <h3 className={styles.mfrDetailSectionTitle}>{t("dcim.components.fields")}</h3>
          <form className={styles.formRow} onSubmit={(e) => { e.preventDefault(); createFieldM.mutate(); }}>
            <label>{t("dcim.components.fieldKey")}<input value={fieldKey} onChange={(e) => setFieldKey(e.target.value)} required /></label>
            <label>{t("dcim.components.fieldLabel")}<input value={fieldLabel} onChange={(e) => setFieldLabel(e.target.value)} required /></label>
            <label>{t("dcim.components.fieldType")}
              <select value={fieldType} onChange={(e) => setFieldType(e.target.value)}>
                {["text", "number", "integer", "boolean", "choice", "date"].map((x) => <option key={x} value={x}>{x}</option>)}
              </select>
            </label>
            <label>{t("dcim.components.unit")}<input value={fieldUnit} onChange={(e) => setFieldUnit(e.target.value)} /></label>
            {fieldType === "choice" ? <label>{t("dcim.components.choices")}<input value={fieldChoices} onChange={(e) => setFieldChoices(e.target.value)} placeholder="DDR4,DDR5" /></label> : null}
            <label style={{ flexDirection: "row", alignItems: "center" }}><input type="checkbox" checked={fieldRequired} onChange={(e) => setFieldRequired(e.target.checked)} /> {t("dcim.components.required")}</label>
            <button type="submit" className={styles.btn} disabled={createFieldM.isPending}>{t("dcim.common.add")}</button>
          </form>
          <table className={styles.table} style={{ marginBottom: "var(--space-3)" }}>
            <thead><tr><th>{t("dcim.components.fieldKey")}</th><th>{t("dcim.components.fieldType")}</th><th>{t("dcim.components.unit")}</th><th>{t("dcim.components.required")}</th></tr></thead>
            <tbody>{selectedFields.map((f) => <tr key={f.id}><td><code>{f.key}</code></td><td>{f.data_type}</td><td>{f.unit ?? "—"}</td><td>{f.required ? "✓" : "—"}</td></tr>)}</tbody>
          </table>

          <h3 className={styles.mfrDetailSectionTitle}>{t("dcim.components.library")}</h3>
          <form className={styles.formRow} onSubmit={(e) => { e.preventDefault(); createComponentM.mutate(); }}>
            <label>{t("dcim.common.name")}<input value={componentName} onChange={(e) => setComponentName(e.target.value)} required /></label>
            <label>{t("dcim.equip.dm.mfr")}<select value={componentMfr} onChange={(e) => setComponentMfr(e.target.value)}><option value="">{t("dcim.common.none")}</option>{(mfrQ.data ?? []).map((m) => <option key={m.id} value={String(m.id)}>{m.name}</option>)}</select></label>
            <label>{t("dcim.components.partNumber")}<input value={componentPart} onChange={(e) => setComponentPart(e.target.value)} /></label>
            <DcimComponentSpecEditor fields={selectedFields} draft={specDraft} onChange={setSpecDraft} />
            <button type="submit" className={styles.btn} disabled={createComponentM.isPending}>{t("dcim.components.createComponent")}</button>
          </form>
        </>
      ) : null}

      <table className={styles.table}>
        <thead><tr><th>{t("dcim.components.className")}</th><th>{t("dcim.common.name")}</th><th>{t("dcim.equip.dm.mfr")}</th><th>{t("dcim.components.partNumber")}</th><th /></tr></thead>
        <tbody>
          {(componentsQ.data ?? []).map((c) => (
            <tr key={c.id}>
              <td>{classNameById.get(c.class_id) ?? `#${c.class_id}`}</td>
              <td>{c.name}</td>
              <td>{c.manufacturer_id ? (mfrNameById.get(c.manufacturer_id) ?? `#${c.manufacturer_id}`) : "—"}</td>
              <td>{c.part_number ?? "—"}</td>
              <td><button type="button" className={`${styles.tableIconBtn} ${styles.tableIconBtnDanger}`.trim()} onClick={() => deleteComponentM.mutate(c.id)}><i className="fas fa-trash-can" aria-hidden /></button></td>
            </tr>
          ))}
        </tbody>
      </table>
    </>
  );
}
