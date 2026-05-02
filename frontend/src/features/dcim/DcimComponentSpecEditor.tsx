import type { ChangeEvent } from "react";
import type { ComponentClassField } from "./types";
import styles from "./dcim.module.css";

export function componentFieldsForClass(fields: ComponentClassField[], classId: number): ComponentClassField[] {
  return fields
    .filter((f) => f.class_id === classId && f.active)
    .sort((a, b) => a.sort_order - b.sort_order || a.id - b.id);
}

export function specsFromDraft(fields: ComponentClassField[], draft: Record<string, string>): Record<string, unknown> {
  const out: Record<string, unknown> = {};
  for (const f of fields) {
    const raw = draft[f.key]?.trim() ?? "";
    if (raw === "") continue;
    if (f.data_type === "number") out[f.key] = Number(raw);
    else if (f.data_type === "integer") out[f.key] = Number.parseInt(raw, 10);
    else if (f.data_type === "boolean") out[f.key] = raw === "true";
    else out[f.key] = raw;
  }
  return out;
}

export function draftFromSpecs(fields: ComponentClassField[], specs: Record<string, unknown> | null | undefined) {
  const src = specs ?? {};
  const out: Record<string, string> = {};
  for (const f of fields) {
    const v = src[f.key];
    if (v == null) out[f.key] = "";
    else if (typeof v === "boolean") out[f.key] = v ? "true" : "false";
    else out[f.key] = String(v);
  }
  return out;
}

export function DcimComponentSpecEditor({
  fields,
  draft,
  onChange,
  compact = false,
}: {
  fields: ComponentClassField[];
  draft: Record<string, string>;
  onChange: (next: Record<string, string>) => void;
  compact?: boolean;
}) {
  if (fields.length === 0) return <p className={styles.muted}>Ingen egendefinerte felt for valgt klasse.</p>;
  return (
    <div className={styles.formRow} style={{ alignItems: "flex-end" }}>
      {fields.map((f) => {
        const label = `${f.label}${f.unit ? ` (${f.unit})` : ""}${f.required ? " *" : ""}`;
        const common = {
          value: draft[f.key] ?? "",
          required: f.required && !compact,
          onChange: (e: ChangeEvent<HTMLInputElement | HTMLSelectElement>) =>
            onChange({ ...draft, [f.key]: e.target.value }),
        };
        return (
          <label key={f.id} title={f.description ?? undefined}>
            {label}
            {f.data_type === "choice" ? (
              <select {...common}>
                <option value="">—</option>
                {(f.choices_json ?? []).map((c) => (
                  <option key={c} value={c}>
                    {c}
                  </option>
                ))}
              </select>
            ) : f.data_type === "boolean" ? (
              <select {...common}>
                <option value="">—</option>
                <option value="true">Ja</option>
                <option value="false">Nei</option>
              </select>
            ) : (
              <input
                {...common}
                type={f.data_type === "date" ? "date" : f.data_type === "text" ? "text" : "number"}
                min={f.min_number ?? undefined}
                max={f.max_number ?? undefined}
                step={f.data_type === "integer" ? 1 : undefined}
              />
            )}
          </label>
        );
      })}
    </div>
  );
}
