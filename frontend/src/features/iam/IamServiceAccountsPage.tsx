import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/Button";
import { useI18n } from "@/i18n/I18nProvider";
import { ApiError } from "@/lib/api";
import * as api from "./iamApi";
import dcimStyles from "@/features/dcim/dcim.module.css";
import styles from "./iam.module.css";

export function IamServiceAccountsPage() {
  const { t } = useI18n();
  const qc = useQueryClient();
  const [username, setUsername] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [err, setErr] = useState<string | null>(null);

  const q = useQuery({
    queryKey: ["iam", "directory", "service_account"],
    queryFn: () => api.listPersons(500, api.IAM_KIND_SERVICE_ACCOUNT),
  });
  const m = useMutation({
    mutationFn: () =>
      api.createPerson({
        username: username.trim(),
        display_name: displayName.trim() || null,
        kind: api.IAM_KIND_SERVICE_ACCOUNT,
      }),
    onSuccess: () => {
      setErr(null);
      setUsername("");
      setDisplayName("");
      void qc.invalidateQueries({ queryKey: ["iam", "directory"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  return (
    <div>
      <h3 className={styles.sectionTitle}>{t("iam.tabServiceAccounts")}</h3>
      <p className={styles.intro}>{t("iam.serviceAccountsHint")}</p>
      <div className={styles.rowActions}>
        <div className={styles.field}>
          <label htmlFor="iam-sa-user">{t("iam.colUsername")}</label>
          <input
            id="iam-sa-user"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            autoComplete="off"
          />
        </div>
        <div className={styles.field}>
          <label htmlFor="iam-sa-dn">{t("iam.colDisplayName")}</label>
          <input id="iam-sa-dn" value={displayName} onChange={(e) => setDisplayName(e.target.value)} />
        </div>
        <Button type="button" onClick={() => m.mutate()} disabled={!username.trim() || m.isPending}>
          {t("iam.createServiceAccount")}
        </Button>
      </div>
      {err ? <p className={styles.err}>{err}</p> : null}

      <table className={dcimStyles.table}>
        <thead>
          <tr>
            <th>{t("iam.colUsername")}</th>
            <th>{t("iam.colDisplayName")}</th>
            <th>{t("iam.colEmail")}</th>
          </tr>
        </thead>
        <tbody>
          {(q.data ?? []).map((u) => (
            <tr key={u.id}>
              <td>
                <Link className={styles.tableLink} to={`/iam/service-accounts/${u.id}`}>
                  {u.username}
                </Link>
              </td>
              <td>{u.display_name ?? "—"}</td>
              <td>{u.email ?? "—"}</td>
            </tr>
          ))}
        </tbody>
      </table>
      {!q.isLoading && (q.data?.length ?? 0) === 0 ? (
        <p className={styles.intro}>{t("iam.emptyServiceAccounts")}</p>
      ) : null}
    </div>
  );
}
