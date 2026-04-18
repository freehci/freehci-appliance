import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/Button";
import { Panel } from "@/components/ui/Panel";
import { useI18n } from "@/i18n/I18nProvider";
import { ApiError } from "@/lib/api";
import * as api from "./iamApi";
import styles from "./iam.module.css";

export function IamUsersListPage() {
  const { t } = useI18n();
  const qc = useQueryClient();
  const [username, setUsername] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [err, setErr] = useState<string | null>(null);

  const q = useQuery({
    queryKey: ["iam", "directory", "person"],
    queryFn: () => api.listPersons(500, api.IAM_KIND_PERSON),
  });
  const m = useMutation({
    mutationFn: () =>
      api.createPerson({
        username: username.trim(),
        display_name: displayName.trim() || null,
        kind: api.IAM_KIND_PERSON,
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
    <Panel title={t("nav.iamUsers")}>
      <p className={styles.intro}>{t("iam.introUsersList")}</p>
      <div className={styles.rowActions}>
        <div className={styles.field}>
          <label htmlFor="iam-new-username">{t("iam.colUsername")}</label>
          <input
            id="iam-new-username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            autoComplete="off"
          />
        </div>
        <div className={styles.field}>
          <label htmlFor="iam-new-dn">{t("iam.colDisplayName")}</label>
          <input id="iam-new-dn" value={displayName} onChange={(e) => setDisplayName(e.target.value)} />
        </div>
        <Button type="button" onClick={() => m.mutate()} disabled={!username.trim() || m.isPending}>
          {t("iam.createUser")}
        </Button>
      </div>
      {err ? <p className={styles.err}>{err}</p> : null}

      <table className={styles.table}>
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
                <Link className={styles.tableLink} to={`/iam/users/${u.id}/user`}>
                  {u.username}
                </Link>
              </td>
              <td>{u.display_name ?? "—"}</td>
              <td>{u.email ?? "—"}</td>
            </tr>
          ))}
        </tbody>
      </table>
      {!q.isLoading && (q.data?.length ?? 0) === 0 ? <p className={styles.intro}>{t("iam.emptyUsers")}</p> : null}
    </Panel>
  );
}
