import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/Button";
import { useI18n } from "@/i18n/I18nProvider";
import { ApiError } from "@/lib/api";
import * as api from "./iamApi";
import styles from "./iam.module.css";

export function IamRolesPage() {
  const { t } = useI18n();
  const qc = useQueryClient();
  const [name, setName] = useState("");
  const [slug, setSlug] = useState("");
  const [err, setErr] = useState<string | null>(null);

  const q = useQuery({ queryKey: ["iam", "roles"], queryFn: api.listRoles });
  const m = useMutation({
    mutationFn: () => api.createRole({ name: name.trim(), slug: slug.trim().toLowerCase(), description: null }),
    onSuccess: () => {
      setErr(null);
      setName("");
      setSlug("");
      void qc.invalidateQueries({ queryKey: ["iam", "roles"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  return (
    <div>
      <h3 className={styles.sectionTitle}>{t("iam.tabRoles")}</h3>
      <p className={styles.intro}>{t("iam.slugHint")}</p>
      <div className={styles.rowActions}>
        <div className={styles.field}>
          <label htmlFor="iam-r-name">{t("iam.colName")}</label>
          <input id="iam-r-name" value={name} onChange={(e) => setName(e.target.value)} />
        </div>
        <div className={styles.field}>
          <label htmlFor="iam-r-slug">{t("iam.colSlug")}</label>
          <input id="iam-r-slug" value={slug} onChange={(e) => setSlug(e.target.value)} />
        </div>
        <Button type="button" onClick={() => m.mutate()} disabled={!name.trim() || !slug.trim() || m.isPending}>
          {t("iam.createRole")}
        </Button>
      </div>
      {err ? <p className={styles.err}>{err}</p> : null}

      <table className={styles.table}>
        <thead>
          <tr>
            <th>{t("iam.colName")}</th>
            <th>{t("iam.colSlug")}</th>
            <th>{t("iam.roleDescription")}</th>
          </tr>
        </thead>
        <tbody>
          {(q.data ?? []).map((r) => (
            <tr key={r.id}>
              <td>
                <Link className={styles.tableLink} to={`/iam/roles/${r.id}`}>
                  {r.name}
                </Link>
              </td>
              <td>{r.slug}</td>
              <td>{r.description ?? "—"}</td>
            </tr>
          ))}
        </tbody>
      </table>
      {!q.isLoading && (q.data?.length ?? 0) === 0 ? <p className={styles.intro}>{t("iam.emptyRoles")}</p> : null}
    </div>
  );
}
