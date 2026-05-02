import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { ApiError } from "@/lib/api";
import { useI18n } from "@/i18n/I18nProvider";
import * as api from "./dcimApi";
import {
  DcimComponentSpecEditor,
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
  const [parentClassId, setParentClassId] = useState("");
  const [templateComponentId, setTemplateComponentId] = useState("");
  const [templateChildClassId, setTemplateChildClassId] = useState("");
  const [templateChildComponentId, setTemplateChildComponentId] = useState("");
  const [templateQuantity, setTemplateQuantity] = useState("1");
  const [templateNamePattern, setTemplateNamePattern] = useState("eth{n}");
  const [templateSlotLabel, setTemplateSlotLabel] = useState("");
  const [templateMaterialize, setTemplateMaterialize] = useState(true);
  const [templateDraft, setTemplateDraft] = useState<Record<string, string>>({});
  const [seedSummary, setSeedSummary] = useState("");

  const classesQ = useQuery({ queryKey: ["dcim", "component-classes"], queryFn: api.listComponentClasses });
  const fieldsQ = useQuery({
    queryKey: ["dcim", "component-class-fields", selectedClassId],
    queryFn: () => api.listComponentClassFields(Number(selectedClassId)),
    enabled: selectedClassId !== "",
  });
  const effectiveFieldsQ = useQuery({
    queryKey: ["dcim", "component-effective-fields", selectedClassId],
    queryFn: () => api.listComponentEffectiveFields(Number(selectedClassId)),
    enabled: selectedClassId !== "",
  });
  const parentsQ = useQuery({
    queryKey: ["dcim", "component-class-parents", selectedClassId],
    queryFn: () => api.listComponentClassParents(Number(selectedClassId)),
    enabled: selectedClassId !== "",
  });
  const componentsQ = useQuery({ queryKey: ["dcim", "components"], queryFn: () => api.listComponents() });
  const templatesQ = useQuery({
    queryKey: ["dcim", "component-child-templates", templateComponentId],
    queryFn: () => api.listComponentChildTemplates(Number(templateComponentId)),
    enabled: templateComponentId !== "",
  });
  const templateFieldsQ = useQuery({
    queryKey: ["dcim", "component-effective-fields", templateChildClassId],
    queryFn: () => api.listComponentEffectiveFields(Number(templateChildClassId)),
    enabled: templateChildClassId !== "",
  });
  const mfrQ = useQuery({ queryKey: ["dcim", "manufacturers"], queryFn: api.listManufacturers });

  const selectedClass = useMemo(
    () => (classesQ.data ?? []).find((x) => x.id === Number(selectedClassId)),
    [classesQ.data, selectedClassId],
  );
  const selectedFields = useMemo(() => effectiveFieldsQ.data ?? [], [effectiveFieldsQ.data]);
  const ownFields = fieldsQ.data ?? [];
  const displayedFields = selectedFields.length > 0
    ? selectedFields
    : ownFields.map((f) => ({
      ...f,
      inherited: false,
      inherited_from_class_id: null,
      inherited_from_class_name: null,
    }));
  const templateFields = templateFieldsQ.data ?? [];
  const classNameById = useMemo(() => new Map((classesQ.data ?? []).map((x) => [x.id, x.name])), [classesQ.data]);
  const mfrNameById = useMemo(() => new Map((mfrQ.data ?? []).map((x) => [x.id, x.name])), [mfrQ.data]);
  const componentNameById = useMemo(() => new Map((componentsQ.data ?? []).map((x) => [x.id, x.name])), [componentsQ.data]);

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
  const seedCatalogM = useMutation({
    mutationFn: api.seedStandardComponentCatalog,
    onSuccess: (res) => {
      onError(null);
      setSeedSummary(
        t("dcim.components.seedSummary", {
          classes: String(res.classes_created),
          fields: String(res.fields_created),
          parents: String(res.parents_created),
        }),
      );
      void qc.invalidateQueries({ queryKey: ["dcim", "component-classes"] });
      void qc.invalidateQueries({ queryKey: ["dcim", "component-class-fields"] });
      void qc.invalidateQueries({ queryKey: ["dcim", "component-effective-fields"] });
      void qc.invalidateQueries({ queryKey: ["dcim", "component-class-parents"] });
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
  const addParentM = useMutation({
    mutationFn: () =>
      api.createComponentClassParent(Number(selectedClassId), {
        parent_class_id: Number(parentClassId),
        sort_order: (parentsQ.data ?? []).length + 1,
      }),
    onSuccess: () => {
      onError(null);
      setParentClassId("");
      void qc.invalidateQueries({ queryKey: ["dcim", "component-class-parents", selectedClassId] });
      void qc.invalidateQueries({ queryKey: ["dcim", "component-effective-fields", selectedClassId] });
    },
    onError: onMutError,
  });
  const deleteParentM = useMutation({
    mutationFn: (id: number) => api.deleteComponentClassParent(id),
    onSuccess: () => {
      onError(null);
      void qc.invalidateQueries({ queryKey: ["dcim", "component-class-parents", selectedClassId] });
      void qc.invalidateQueries({ queryKey: ["dcim", "component-effective-fields", selectedClassId] });
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
  const createTemplateM = useMutation({
    mutationFn: () =>
      api.createComponentChildTemplate(Number(templateComponentId), {
        child_class_id: Number(templateChildClassId),
        child_component_id: templateChildComponentId === "" ? null : Number(templateChildComponentId),
        quantity: Number(templateQuantity) || 1,
        name_pattern: templateNamePattern.trim() || null,
        slot_label: templateSlotLabel.trim() || null,
        overrides_json: specsFromDraft(templateFields, templateDraft),
        materialize_as: templateMaterialize ? "interface" : null,
        sort_order: (templatesQ.data ?? []).length + 1,
      }),
    onSuccess: () => {
      onError(null);
      setTemplateChildClassId("");
      setTemplateChildComponentId("");
      setTemplateQuantity("1");
      setTemplateNamePattern("eth{n}");
      setTemplateSlotLabel("");
      setTemplateMaterialize(true);
      setTemplateDraft({});
      void qc.invalidateQueries({ queryKey: ["dcim", "component-child-templates", templateComponentId] });
    },
    onError: onMutError,
  });
  const deleteTemplateM = useMutation({
    mutationFn: (id: number) => api.deleteComponentChildTemplate(id),
    onSuccess: () => {
      onError(null);
      void qc.invalidateQueries({ queryKey: ["dcim", "component-child-templates", templateComponentId] });
    },
    onError: onMutError,
  });

  return (
    <>
      <p className={styles.muted} style={{ marginTop: 0 }}>{t("dcim.components.intro")}</p>
      <div className={styles.formRow} style={{ alignItems: "center" }}>
        <button type="button" className={styles.btnMuted} disabled={seedCatalogM.isPending} onClick={() => seedCatalogM.mutate()}>
          {seedCatalogM.isPending ? "…" : t("dcim.components.seedStandard")}
        </button>
        <span className={styles.muted}>{t("dcim.components.seedStandardHint")}</span>
      </div>
      {seedSummary ? <p className={styles.muted}>{seedSummary}</p> : null}
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
          <h3 className={styles.mfrDetailSectionTitle}>{t("dcim.components.inheritsFrom")}</h3>
          <form className={styles.formRow} onSubmit={(e) => { e.preventDefault(); addParentM.mutate(); }}>
            <label>{t("dcim.components.parentClass")}
              <select value={parentClassId} onChange={(e) => setParentClassId(e.target.value)} required>
                <option value="">{t("dcim.common.choose")}</option>
                {(classesQ.data ?? [])
                  .filter((c) => c.id !== selectedClass.id && !(parentsQ.data ?? []).some((p) => p.parent_class_id === c.id))
                  .map((c) => <option key={c.id} value={String(c.id)}>{c.name}</option>)}
              </select>
            </label>
            <button type="submit" className={styles.btn} disabled={addParentM.isPending || parentClassId === ""}>{t("dcim.common.add")}</button>
          </form>
          {(parentsQ.data ?? []).length > 0 ? (
            <ul className={styles.ipList}>
              {(parentsQ.data ?? []).map((p) => (
                <li key={p.id}>
                  {classNameById.get(p.parent_class_id) ?? `#${p.parent_class_id}`}{" "}
                  <button type="button" className={styles.btnDanger} onClick={() => deleteParentM.mutate(p.id)} disabled={deleteParentM.isPending}>
                    {t("dcim.common.remove")}
                  </button>
                </li>
              ))}
            </ul>
          ) : <p className={styles.muted}>{t("dcim.components.noParents")}</p>}

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
            <thead><tr><th>{t("dcim.components.fieldKey")}</th><th>{t("dcim.components.fieldType")}</th><th>{t("dcim.components.unit")}</th><th>{t("dcim.components.required")}</th><th>{t("dcim.components.source")}</th></tr></thead>
            <tbody>{displayedFields.map((f) => <tr key={`${f.class_id}-${f.id}`}><td><code>{f.key}</code></td><td>{f.data_type}</td><td>{f.unit ?? "—"}</td><td>{f.required ? "✓" : "—"}</td><td>{f.inherited ? (f.inherited_from_class_name ?? "—") : t("dcim.components.ownField")}</td></tr>)}</tbody>
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

      <h3 className={styles.mfrDetailSectionTitle}>{t("dcim.components.childTemplates")}</h3>
      <div className={styles.formRow}>
        <label>{t("dcim.components.parentComponent")}
          <select value={templateComponentId} onChange={(e) => { setTemplateComponentId(e.target.value); setTemplateDraft({}); }}>
            <option value="">{t("dcim.common.choose")}</option>
            {(componentsQ.data ?? []).map((c) => <option key={c.id} value={String(c.id)}>{classNameById.get(c.class_id) ?? "?"}: {c.name}</option>)}
          </select>
        </label>
      </div>
      {templateComponentId !== "" ? (
        <>
          <form className={styles.formRow} onSubmit={(e) => { e.preventDefault(); createTemplateM.mutate(); }}>
            <label>{t("dcim.components.childClass")}
              <select value={templateChildClassId} onChange={(e) => { setTemplateChildClassId(e.target.value); setTemplateDraft({}); }} required>
                <option value="">{t("dcim.common.choose")}</option>
                {(classesQ.data ?? []).map((c) => <option key={c.id} value={String(c.id)}>{c.name}</option>)}
              </select>
            </label>
            <label>{t("dcim.components.childComponent")}
              <select value={templateChildComponentId} onChange={(e) => setTemplateChildComponentId(e.target.value)}>
                <option value="">{t("dcim.common.none")}</option>
                {(componentsQ.data ?? [])
                  .filter((c) => templateChildClassId === "" || c.class_id === Number(templateChildClassId))
                  .map((c) => <option key={c.id} value={String(c.id)}>{c.name}</option>)}
              </select>
            </label>
            <label>{t("dcim.components.quantity")}<input type="number" min={1} value={templateQuantity} onChange={(e) => setTemplateQuantity(e.target.value)} /></label>
            <label>{t("dcim.components.namePattern")}<input value={templateNamePattern} onChange={(e) => setTemplateNamePattern(e.target.value)} placeholder="eth{n}" /></label>
            <label>{t("dcim.components.slotLabel")}<input value={templateSlotLabel} onChange={(e) => setTemplateSlotLabel(e.target.value)} /></label>
            <label style={{ flexDirection: "row", alignItems: "center" }}><input type="checkbox" checked={templateMaterialize} onChange={(e) => setTemplateMaterialize(e.target.checked)} /> {t("dcim.components.materializeInterface")}</label>
            <DcimComponentSpecEditor fields={templateFields} draft={templateDraft} onChange={setTemplateDraft} compact />
            <button type="submit" className={styles.btn} disabled={createTemplateM.isPending || templateChildClassId === ""}>{t("dcim.components.addChildTemplate")}</button>
          </form>
          <table className={styles.table}>
            <thead><tr><th>{t("dcim.components.childClass")}</th><th>{t("dcim.components.childComponent")}</th><th>{t("dcim.components.quantity")}</th><th>{t("dcim.components.namePattern")}</th><th>{t("dcim.components.materializeAs")}</th><th /></tr></thead>
            <tbody>
              {(templatesQ.data ?? []).map((tpl) => (
                <tr key={tpl.id}>
                  <td>{classNameById.get(tpl.child_class_id) ?? `#${tpl.child_class_id}`}</td>
                  <td>{tpl.child_component_id ? (componentNameById.get(tpl.child_component_id) ?? `#${tpl.child_component_id}`) : "—"}</td>
                  <td>{tpl.quantity}</td>
                  <td>{tpl.name_pattern ?? "—"}</td>
                  <td>{tpl.materialize_as ?? "—"}</td>
                  <td><button type="button" className={`${styles.tableIconBtn} ${styles.tableIconBtnDanger}`.trim()} onClick={() => deleteTemplateM.mutate(tpl.id)}><i className="fas fa-trash-can" aria-hidden /></button></td>
                </tr>
              ))}
            </tbody>
          </table>
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
