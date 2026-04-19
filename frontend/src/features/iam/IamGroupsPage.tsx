import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/Button";
import { useI18n } from "@/i18n/I18nProvider";
import { ApiError } from "@/lib/api";
import * as api from "./iamApi";
import dcimStyles from "@/features/dcim/dcim.module.css";
import styles from "./iam.module.css";

export function IamGroupsPage() {
  const { t } = useI18n();
  const qc = useQueryClient();
  const [name, setName] = useState("");
  const [slug, setSlug] = useState("");
  const [err, setErr] = useState<string | null>(null);

  const q = useQuery({ queryKey: ["iam", "groups"], queryFn: api.listGroups });
  const m = useMutation({
    mutationFn: () => api.createGroup({ name: name.trim(), slug: slug.trim().toLowerCase(), description: null }),
    onSuccess: () => {
      setErr(null);
      setName("");
      setSlug("");
      void qc.invalidateQueries({ queryKey: ["iam", "groups"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  return (
    <div>
      <h3 className={styles.sectionTitle}>{t("iam.tabGroups")}</h3>
      <p className={styles.intro}>{t("iam.slugHint")}</p>
      <div className={styles.rowActions}>
        <div className={styles.field}>
          <label htmlFor="iam-g-name">{t("iam.colName")}</label>
          <input id="iam-g-name" value={name} onChange={(e) => setName(e.target.value)} />
        </div>
        <div className={styles.field}>
          <label htmlFor="iam-g-slug">{t("iam.colSlug")}</label>
          <input id="iam-g-slug" value={slug} onChange={(e) => setSlug(e.target.value)} />
        </div>
        <Button type="button" onClick={() => m.mutate()} disabled={!name.trim() || !slug.trim() || m.isPending}>
          {t("iam.createGroup")}
        </Button>
      </div>
      {err ? <p className={styles.err}>{err}</p> : null}

      <table className={dcimStyles.table}>
        <thead>
          <tr>
            <th>{t("iam.colName")}</th>
            <th>{t("iam.colSlug")}</th>
            <th>{t("iam.identityProvider")}</th>
          </tr>
        </thead>
        <tbody>
          {(q.data ?? []).map((g) => (
            <tr key={g.id}>
              <td>
                <Link className={styles.tableLink} to={`/iam/groups/${g.id}`}>
                  {g.name}
                </Link>
              </td>
              <td>{g.slug}</td>
              <td>{g.identity_provider ?? "—"}</td>
            </tr>
          ))}
        </tbody>
      </table>
      {!q.isLoading && (q.data?.length ?? 0) === 0 ? <p className={styles.intro}>{t("iam.emptyGroups")}</p> : null}
    </div>
  );
}
