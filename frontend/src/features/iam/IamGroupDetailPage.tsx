import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useMemo, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { Button } from "@/components/ui/Button";
import { useI18n } from "@/i18n/I18nProvider";
import { ApiError } from "@/lib/api";
import * as api from "./iamApi";
import styles from "./iam.module.css";

export function IamGroupDetailPage() {
  const { t } = useI18n();
  const nav = useNavigate();
  const { groupId } = useParams<{ groupId: string }>();
  const id = Number(groupId);
  const qc = useQueryClient();
  const [err, setErr] = useState<string | null>(null);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [userPick, setUserPick] = useState("");
  const [subPick, setSubPick] = useState("");

  const q = useQuery({
    queryKey: ["iam", "group", id],
    queryFn: () => api.getGroup(id),
    enabled: Number.isFinite(id),
  });

  const personsQ = useQuery({
    queryKey: ["iam", "directory", "all"],
    queryFn: () => api.listPersons(500),
  });
  const groupsQ = useQuery({ queryKey: ["iam", "groups"], queryFn: api.listGroups });

  const group = q.data;
  useEffect(() => {
    if (!group) return;
    setName(group.name);
    setDescription(group.description ?? "");
  }, [group]);

  const subgroupOptions = useMemo(() => {
    if (!group || !groupsQ.data) return [];
    const childIds = new Set(group.direct_subgroups.map((s) => s.child_group_id));
    return groupsQ.data.filter((g) => g.id !== group.id && !childIds.has(g.id));
  }, [group, groupsQ.data]);

  const userOptions = useMemo(() => {
    if (!group || !personsQ.data) return [];
    const memberIds = new Set(group.direct_users.map((u) => u.user_id));
    return personsQ.data.filter((u) => !memberIds.has(u.id));
  }, [group, personsQ.data]);

  const saveM = useMutation({
    mutationFn: () => api.patchGroup(id, { name: name.trim(), description: description.trim() || null }),
    onSuccess: () => {
      setErr(null);
      void qc.invalidateQueries({ queryKey: ["iam", "group", id] });
      void qc.invalidateQueries({ queryKey: ["iam", "groups"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const delM = useMutation({
    mutationFn: () => api.deleteGroup(id),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ["iam", "groups"] });
      void nav("/iam/groups");
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const addUserM = useMutation({
    mutationFn: () => api.addGroupUserMember(id, Number(userPick)),
    onSuccess: () => {
      setErr(null);
      setUserPick("");
      void qc.invalidateQueries({ queryKey: ["iam", "group", id] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const addSubM = useMutation({
    mutationFn: () => api.addGroupSubgroupMember(id, Number(subPick)),
    onSuccess: () => {
      setErr(null);
      setSubPick("");
      void qc.invalidateQueries({ queryKey: ["iam", "group", id] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const remUserM = useMutation({
    mutationFn: (userId: number) => api.removeGroupUserMember(id, userId),
    onSuccess: () => void qc.invalidateQueries({ queryKey: ["iam", "group", id] }),
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const remSubM = useMutation({
    mutationFn: (childId: number) => api.removeGroupSubgroupMember(id, childId),
    onSuccess: () => void qc.invalidateQueries({ queryKey: ["iam", "group", id] }),
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  if (!Number.isFinite(id)) {
    return <p className={styles.err}>{t("iam.invalidId")}</p>;
  }

  return (
    <div>
      <Link className={styles.back} to="/iam/groups">
        ← {t("iam.backToList")}
      </Link>
      <h3 className={styles.sectionTitle}>
        {t("iam.detailGroup")}: {group?.name ?? "…"}
      </h3>
      {err ? <p className={styles.err}>{err}</p> : null}

      {q.isLoading ? (
        <p className={styles.intro}>…</p>
      ) : group ? (
        <>
          <dl className={styles.dl}>
            <dt>{t("iam.colSlug")}</dt>
            <dd>{group.slug}</dd>
            <dt>{t("iam.externalSubjectId")}</dt>
            <dd>{group.external_subject_id ?? "—"}</dd>
            <dt>{t("iam.identityProvider")}</dt>
            <dd>{group.identity_provider ?? "—"}</dd>
          </dl>
          <div className={styles.rowActions}>
            <div className={styles.field}>
              <label htmlFor="g-name">{t("iam.colName")}</label>
              <input id="g-name" value={name} onChange={(e) => setName(e.target.value)} />
            </div>
            <div className={styles.field} style={{ minWidth: "18rem" }}>
              <label htmlFor="g-desc">{t("iam.roleDescription")}</label>
              <textarea id="g-desc" rows={3} value={description} onChange={(e) => setDescription(e.target.value)} />
            </div>
            <Button type="button" onClick={() => saveM.mutate()} disabled={saveM.isPending}>
              {t("iam.save")}
            </Button>
          </div>
          <Button type="button" onClick={() => delM.mutate()} disabled={delM.isPending}>
            {t("iam.deleteGroup")}
          </Button>

          <h4 className={styles.sectionTitle}>{t("iam.groupDirectUsers")}</h4>
          <ul className={styles.pillList}>
            {group.direct_users.map((u) => (
              <li key={u.user_id}>
                <Link className={styles.tableLink} to={`/iam/users/${u.user_id}/user`}>
                  {u.display_name ?? u.username}
                </Link>{" "}
                <button type="button" className={styles.tableLink} onClick={() => remUserM.mutate(u.user_id)}>
                  {t("iam.remove")}
                </button>
              </li>
            ))}
          </ul>
          <div className={styles.rowActions}>
            <div className={styles.field}>
              <label htmlFor="g-user">{t("iam.choosePerson")}</label>
              <select id="g-user" value={userPick} onChange={(e) => setUserPick(e.target.value)}>
                <option value="">—</option>
                {userOptions.map((u) => (
                  <option key={u.id} value={String(u.id)}>
                    {u.username}
                  </option>
                ))}
              </select>
            </div>
            <Button type="button" onClick={() => addUserM.mutate()} disabled={!userPick || addUserM.isPending}>
              {t("iam.addUserMember")}
            </Button>
          </div>

          <h4 className={styles.sectionTitle}>{t("iam.groupDirectSubgroups")}</h4>
          <ul className={styles.pillList}>
            {group.direct_subgroups.map((s) => (
              <li key={s.child_group_id}>
                <Link className={styles.tableLink} to={`/iam/groups/${s.child_group_id}`}>
                  {s.name}
                </Link>{" "}
                <button type="button" className={styles.tableLink} onClick={() => remSubM.mutate(s.child_group_id)}>
                  {t("iam.remove")}
                </button>
              </li>
            ))}
          </ul>
          <div className={styles.rowActions}>
            <div className={styles.field}>
              <label htmlFor="g-sub">{t("iam.chooseSubgroup")}</label>
              <select id="g-sub" value={subPick} onChange={(e) => setSubPick(e.target.value)}>
                <option value="">—</option>
                {subgroupOptions.map((g) => (
                  <option key={g.id} value={String(g.id)}>
                    {g.name}
                  </option>
                ))}
              </select>
            </div>
            <Button type="button" onClick={() => addSubM.mutate()} disabled={!subPick || addSubM.isPending}>
              {t("iam.addSubgroup")}
            </Button>
          </div>

          <h4 className={styles.sectionTitle}>{t("iam.groupEffectiveUsers")}</h4>
          <pre className={styles.mono}>{group.effective_user_ids.join(", ") || "—"}</pre>
        </>
      ) : (
        <p className={styles.err}>{t("iam.notFound")}</p>
      )}
    </div>
  );
}
