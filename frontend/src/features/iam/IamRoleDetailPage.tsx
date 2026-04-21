import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { Button } from "@/components/ui/Button";
import { Panel } from "@/components/ui/Panel";
import { useI18n } from "@/i18n/I18nProvider";
import { ApiError } from "@/lib/api";
import * as api from "./iamApi";
import styles from "./iam.module.css";

export function IamRoleDetailPage() {
  const { t } = useI18n();
  const nav = useNavigate();
  const { roleId } = useParams<{ roleId: string }>();
  const id = Number(roleId);
  const qc = useQueryClient();
  const [err, setErr] = useState<string | null>(null);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");

  const q = useQuery({
    queryKey: ["iam", "role", id],
    queryFn: () => api.getRole(id),
    enabled: Number.isFinite(id),
  });

  const role = q.data;
  useEffect(() => {
    if (!role) return;
    setName(role.name);
    setDescription(role.description ?? "");
  }, [role]);

  const saveM = useMutation({
    mutationFn: () => api.patchRole(id, { name: name.trim(), description: description.trim() || null }),
    onSuccess: () => {
      setErr(null);
      void qc.invalidateQueries({ queryKey: ["iam", "role", id] });
      void qc.invalidateQueries({ queryKey: ["iam", "roles"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const delM = useMutation({
    mutationFn: () => api.deleteRole(id),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ["iam", "roles"] });
      void nav("/iam/roles");
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  if (!Number.isFinite(id)) {
    return (
      <Panel title={t("iam.invalidId")}>
        <p className={styles.err}>{t("iam.invalidId")}</p>
      </Panel>
    );
  }

  const panelTitle = `${t("iam.detailRole")}: ${role?.name ?? "…"}`;

  return (
    <Panel title={panelTitle}>
      <Link className={styles.back} to="/iam/roles">
        ← {t("iam.backToList")}
      </Link>
      {err ? <p className={styles.err}>{err}</p> : null}

      {q.isLoading ? (
        <p className={styles.intro}>…</p>
      ) : role ? (
        <>
          <dl className={styles.dl}>
            <dt>{t("iam.colSlug")}</dt>
            <dd>{role.slug}</dd>
            <dt>{t("iam.colMembers")}</dt>
            <dd>{role.member_count}</dd>
          </dl>
          <div className={styles.rowActions}>
            <div className={styles.field}>
              <label htmlFor="r-name">{t("iam.colName")}</label>
              <input id="r-name" value={name} onChange={(e) => setName(e.target.value)} disabled={role.system} />
            </div>
            <div className={styles.field} style={{ minWidth: "18rem" }}>
              <label htmlFor="r-desc">{t("iam.roleDescription")}</label>
              <textarea id="r-desc" rows={3} value={description} onChange={(e) => setDescription(e.target.value)} />
            </div>
            <Button type="button" onClick={() => saveM.mutate()} disabled={saveM.isPending}>
              {t("iam.save")}
            </Button>
          </div>
          {!role.system ? (
            <Button type="button" onClick={() => delM.mutate()} disabled={delM.isPending}>
              {t("iam.deleteRole")}
            </Button>
          ) : null}

          <h4 className={styles.sectionTitle}>{t("iam.roleAssignees")}</h4>
          <ul className={styles.pillList}>
            {role.assignees.map((a) => (
              <li key={a.id}>
                <Link className={styles.tableLink} to={`/iam/users/${a.id}/user`}>
                  {a.display_name ?? a.username}
                </Link>
              </li>
            ))}
          </ul>
          {role.assignees.length === 0 ? <p className={styles.intro}>—</p> : null}
        </>
      ) : (
        <p className={styles.err}>{t("iam.notFound")}</p>
      )}
    </Panel>
  );
}
