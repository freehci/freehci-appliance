import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { Link, useParams } from "react-router-dom";
import { Button } from "@/components/ui/Button";
import { useI18n } from "@/i18n/I18nProvider";
import { ApiError } from "@/lib/api";
import * as api from "./iamApi";
import styles from "./iam.module.css";

export function IamUserRolesTab() {
  const { t } = useI18n();
  const { userId } = useParams<{ userId: string }>();
  const id = Number(userId);
  const qc = useQueryClient();
  const [err, setErr] = useState<string | null>(null);
  const [rolePick, setRolePick] = useState("");

  const q = useQuery({
    queryKey: ["iam", "person", id],
    queryFn: () => api.getPerson(id),
    enabled: Number.isFinite(id),
  });

  const rolesQ = useQuery({ queryKey: ["iam", "roles"], queryFn: api.listRoles });

  const assignM = useMutation({
    mutationFn: () => api.assignPersonRole(id, Number(rolePick)),
    onSuccess: () => {
      setErr(null);
      setRolePick("");
      void qc.invalidateQueries({ queryKey: ["iam", "person", id] });
      void qc.invalidateQueries({ queryKey: ["iam", "directory"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const revokeM = useMutation({
    mutationFn: (roleId: number) => api.revokePersonRole(id, roleId),
    onSuccess: () => {
      setErr(null);
      void qc.invalidateQueries({ queryKey: ["iam", "person", id] });
      void qc.invalidateQueries({ queryKey: ["iam", "directory"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const person = q.data;
  if (!Number.isFinite(id)) return <p className={styles.err}>{t("iam.invalidId")}</p>;
  if (q.isLoading) return <p className={styles.intro}>…</p>;
  if (!person) return <p className={styles.err}>{t("iam.notFound")}</p>;

  return (
    <div>
      {err ? <p className={styles.err}>{err}</p> : null}
      <h4 className={styles.userDetailSectionTitle}>{t("iam.rolesAssigned")}</h4>
      <ul className={styles.pillList}>
        {person.roles.map((r) => (
          <li key={r.id}>
            <Link className={styles.tableLink} to={`/iam/roles/${r.id}`}>
              {r.name}
            </Link>{" "}
            <button type="button" className={styles.tableLink} onClick={() => revokeM.mutate(r.id)}>
              {t("iam.remove")}
            </button>
          </li>
        ))}
      </ul>
      <div className={styles.rowActions}>
        <div className={styles.field}>
          <label htmlFor="ur-role">{t("iam.chooseRole")}</label>
          <select id="ur-role" value={rolePick} onChange={(e) => setRolePick(e.target.value)}>
            <option value="">—</option>
            {(rolesQ.data ?? [])
              .filter((r) => !person.roles.some((x) => x.id === r.id))
              .map((r) => (
                <option key={r.id} value={String(r.id)}>
                  {r.name}
                </option>
              ))}
          </select>
        </div>
        <Button type="button" onClick={() => assignM.mutate()} disabled={!rolePick || assignM.isPending}>
          {t("iam.assignRole")}
        </Button>
      </div>
    </div>
  );
}
