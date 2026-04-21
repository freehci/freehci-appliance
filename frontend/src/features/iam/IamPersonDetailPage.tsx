import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { Link, useLocation, useParams } from "react-router-dom";
import { Button } from "@/components/ui/Button";
import { Panel } from "@/components/ui/Panel";
import { useI18n } from "@/i18n/I18nProvider";
import { ApiError } from "@/lib/api";
import * as api from "./iamApi";
import styles from "./iam.module.css";

export function IamPersonDetailPage() {
  const { t } = useI18n();
  const loc = useLocation();
  const { personId } = useParams<{ personId: string }>();
  const id = Number(personId);
  const qc = useQueryClient();
  const fromServiceAccounts = loc.pathname.includes("/iam/service-accounts/");
  const backTo = fromServiceAccounts ? "/iam/service-accounts" : "/iam/users";
  const [err, setErr] = useState<string | null>(null);
  const [rolePick, setRolePick] = useState("");

  const q = useQuery({
    queryKey: ["iam", "person", id],
    queryFn: () => api.getPerson(id),
    enabled: Number.isFinite(id),
  });

  const rolesQ = useQuery({ queryKey: ["iam", "roles"], queryFn: api.listRoles });

  const [displayName, setDisplayName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [notes, setNotes] = useState("");
  const [extId, setExtId] = useState("");
  const [idp, setIdp] = useState("");

  const person = q.data;
  useEffect(() => {
    if (!person) return;
    setDisplayName(person.display_name ?? "");
    setEmail(person.email ?? "");
    setPhone(person.phone ?? "");
    setNotes(person.notes ?? "");
    setExtId(person.external_subject_id ?? "");
    setIdp(person.identity_provider ?? "");
  }, [person]);

  const saveM = useMutation({
    mutationFn: () =>
      api.patchPerson(id, {
        display_name: displayName.trim() || null,
        email: email.trim() || null,
        phone: phone.trim() || null,
        notes: notes.trim() || null,
        external_subject_id: extId.trim() || null,
        identity_provider: idp.trim() || null,
      }),
    onSuccess: () => {
      setErr(null);
      void qc.invalidateQueries({ queryKey: ["iam", "person", id] });
      void qc.invalidateQueries({ queryKey: ["iam", "directory"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

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

  if (!Number.isFinite(id)) {
    return (
      <Panel title={t("iam.invalidId")}>
        <p className={styles.err}>{t("iam.invalidId")}</p>
      </Panel>
    );
  }

  const detailKindLabel =
    person?.kind === api.IAM_KIND_SERVICE_ACCOUNT ? t("iam.detailServiceAccount") : t("iam.detailPerson");
  const panelTitle = `${detailKindLabel}: ${person?.username ?? "…"}`;

  return (
    <Panel title={panelTitle}>
      <Link className={styles.back} to={backTo}>
        ← {t("iam.backToList")}
      </Link>
      {err ? <p className={styles.err}>{err}</p> : null}

      {q.isLoading ? (
        <p className={styles.intro}>…</p>
      ) : person ? (
        <>
          <h4 className={styles.sectionTitle}>{t("iam.sectionProfile")}</h4>
          <dl className={styles.dl}>
            <dt>{t("iam.colUsername")}</dt>
            <dd>{person.username}</dd>
            <dt>{t("iam.colKind")}</dt>
            <dd>{person.kind ?? api.IAM_KIND_PERSON}</dd>
          </dl>
          <div className={styles.rowActions}>
            <div className={styles.field}>
              <label htmlFor="p-dn">{t("iam.colDisplayName")}</label>
              <input id="p-dn" value={displayName} onChange={(e) => setDisplayName(e.target.value)} />
            </div>
            <div className={styles.field}>
              <label htmlFor="p-em">{t("iam.colEmail")}</label>
              <input id="p-em" type="email" value={email} onChange={(e) => setEmail(e.target.value)} />
            </div>
            <div className={styles.field}>
              <label htmlFor="p-ph">{t("iam.phone")}</label>
              <input id="p-ph" value={phone} onChange={(e) => setPhone(e.target.value)} />
            </div>
            <div className={styles.field} style={{ minWidth: "16rem" }}>
              <label htmlFor="p-no">{t("iam.notes")}</label>
              <textarea id="p-no" rows={2} value={notes} onChange={(e) => setNotes(e.target.value)} />
            </div>
          </div>
          <h4 className={styles.sectionTitle}>{t("iam.sectionExternal")}</h4>
          <div className={styles.rowActions}>
            <div className={styles.field}>
              <label htmlFor="p-ext">{t("iam.externalSubjectId")}</label>
              <input id="p-ext" value={extId} onChange={(e) => setExtId(e.target.value)} />
            </div>
            <div className={styles.field}>
              <label htmlFor="p-idp">{t("iam.identityProvider")}</label>
              <input id="p-idp" value={idp} onChange={(e) => setIdp(e.target.value)} placeholder="ldap:ad" />
            </div>
            <Button type="button" onClick={() => saveM.mutate()} disabled={saveM.isPending}>
              {t("iam.save")}
            </Button>
          </div>

          <h4 className={styles.sectionTitle}>{t("iam.rolesAssigned")}</h4>
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
              <label htmlFor="p-role">{t("iam.chooseRole")}</label>
              <select id="p-role" value={rolePick} onChange={(e) => setRolePick(e.target.value)}>
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

          <h4 className={styles.sectionTitle}>{t("iam.groupsDirect")}</h4>
          <ul className={styles.pillList}>
            {person.groups_direct.map((g) => (
              <li key={g.id}>
                <Link className={styles.tableLink} to={`/iam/groups/${g.id}`}>
                  {g.name}
                </Link>
              </li>
            ))}
          </ul>
          {person.groups_direct.length === 0 ? <p className={styles.intro}>—</p> : null}

          <h4 className={styles.sectionTitle}>{t("iam.groupsEffective")}</h4>
          <ul className={styles.pillList}>
            {person.groups_effective.map((g) => (
              <li key={g.id}>
                <Link className={styles.tableLink} to={`/iam/groups/${g.id}`}>
                  {g.name}
                </Link>
              </li>
            ))}
          </ul>
        </>
      ) : (
        <p className={styles.err}>{t("iam.notFound")}</p>
      )}
    </Panel>
  );
}
