import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { Button } from "@/components/ui/Button";
import { useI18n } from "@/i18n/I18nProvider";
import { ApiError } from "@/lib/api";
import * as api from "./iamApi";
import styles from "./iam.module.css";

export function IamUserProfileTab() {
  const { t } = useI18n();
  const { userId } = useParams<{ userId: string }>();
  const id = Number(userId);
  const qc = useQueryClient();
  const [err, setErr] = useState<string | null>(null);

  const q = useQuery({
    queryKey: ["iam", "person", id],
    queryFn: () => api.getPerson(id),
    enabled: Number.isFinite(id),
  });

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

  if (!Number.isFinite(id)) return <p className={styles.err}>{t("iam.invalidId")}</p>;
  if (q.isLoading) return <p className={styles.intro}>…</p>;
  if (!person) return <p className={styles.err}>{t("iam.notFound")}</p>;

  return (
    <div>
      {err ? <p className={styles.err}>{err}</p> : null}
      <h4 className={styles.userDetailSectionTitle}>{t("iam.sectionProfile")}</h4>
      <dl className={styles.dl}>
        <dt>{t("iam.colUsername")}</dt>
        <dd>{person.username}</dd>
        <dt>{t("iam.colKind")}</dt>
        <dd>{person.kind ?? api.IAM_KIND_PERSON}</dd>
      </dl>
      <div className={styles.userFormGrid}>
        <div className={styles.field}>
          <label htmlFor="pu-dn">{t("iam.colDisplayName")}</label>
          <input id="pu-dn" value={displayName} onChange={(e) => setDisplayName(e.target.value)} />
        </div>
        <div className={styles.field}>
          <label htmlFor="pu-em">{t("iam.colEmail")}</label>
          <input id="pu-em" type="email" value={email} onChange={(e) => setEmail(e.target.value)} />
        </div>
        <div className={styles.field}>
          <label htmlFor="pu-ph">{t("iam.phone")}</label>
          <input id="pu-ph" value={phone} onChange={(e) => setPhone(e.target.value)} />
        </div>
        <div className={`${styles.field} ${styles.fieldSpan2}`}>
          <label htmlFor="pu-no">{t("iam.notes")}</label>
          <textarea id="pu-no" rows={3} value={notes} onChange={(e) => setNotes(e.target.value)} />
        </div>
      </div>

      <h4 className={styles.userDetailSectionTitle}>{t("iam.sectionExternal")}</h4>
      <div className={styles.userFormGrid}>
        <div className={styles.field}>
          <label htmlFor="pu-ext">{t("iam.externalSubjectId")}</label>
          <input id="pu-ext" value={extId} onChange={(e) => setExtId(e.target.value)} />
        </div>
        <div className={styles.field}>
          <label htmlFor="pu-idp">{t("iam.identityProvider")}</label>
          <input id="pu-idp" value={idp} onChange={(e) => setIdp(e.target.value)} placeholder="ldap:ad" />
        </div>
      </div>

      <div className={styles.userDetailFooter}>
        <Link to="/iam/users" className={styles.btnOutline}>
          {t("iam.cancel")}
        </Link>
        <Button type="button" onClick={() => saveM.mutate()} disabled={saveM.isPending}>
          {t("iam.update")}
        </Button>
      </div>
    </div>
  );
}
