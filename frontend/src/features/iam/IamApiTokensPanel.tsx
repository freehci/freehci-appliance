import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { ConfirmModal } from "@/components/ui/ConfirmModal";
import { Button } from "@/components/ui/Button";
import { useI18n } from "@/i18n/I18nProvider";
import { ApiError } from "@/lib/api";
import dcimStyles from "@/features/dcim/dcim.module.css";
import authStyles from "@/features/auth/authPages.module.css";
import * as api from "./iamApi";
import styles from "./iam.module.css";

function fmtDate(v: string | null | undefined): string {
  if (!v) return "—";
  const d = new Date(v);
  if (Number.isNaN(d.getTime())) return v;
  return d.toLocaleString();
}

export function IamApiTokensPanel({ personId }: { personId: number }) {
  const { t } = useI18n();
  const qc = useQueryClient();
  const [err, setErr] = useState<string | null>(null);
  const [name, setName] = useState("");
  const [created, setCreated] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);
  const [revoke, setRevoke] = useState<api.IamApiToken | null>(null);
  const [scopes, setScopes] = useState<string[]>([]);

  function toggleScope(scope: string) {
    setScopes((cur) => (cur.includes(scope) ? cur.filter((s) => s !== scope) : [...cur, scope]));
  }

  const q = useQuery({
    queryKey: ["iam", "person", personId, "tokens"],
    queryFn: () => api.listPersonTokens(personId),
  });

  const createM = useMutation({
    mutationFn: () => api.createPersonToken(personId, name.trim(), scopes.length ? scopes : null),
    onSuccess: (row) => {
      setErr(null);
      setName("");
      setScopes([]);
      setCreated(row.token);
      setCopied(false);
      void qc.invalidateQueries({ queryKey: ["iam", "person", personId, "tokens"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const delM = useMutation({
    mutationFn: (tokenId: number) => api.deletePersonToken(personId, tokenId),
    onSuccess: () => {
      setErr(null);
      setRevoke(null);
      void qc.invalidateQueries({ queryKey: ["iam", "person", personId, "tokens"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  return (
    <div>
      <h4 className={styles.sectionTitle}>{t("iam.sectionApiTokens")}</h4>
      <p className={styles.intro}>{t("iam.apiTokensHint")}</p>
      {err ? <p className={styles.err}>{err}</p> : null}
      <div className={styles.rowActions}>
        <div className={styles.field}>
          <label htmlFor={`sa-tok-${personId}`}>{t("auth.tokenName")}</label>
          <input
            id={`sa-tok-${personId}`}
            value={name}
            onChange={(e) => setName(e.target.value)}
            autoComplete="off"
          />
        </div>
        <Button type="button" onClick={() => createM.mutate()} disabled={!name.trim() || createM.isPending}>
          {t("auth.createToken")}
        </Button>
      </div>
      <p className={styles.intro}>{t("auth.tokenScopesHint")}</p>
      <div className={styles.rowActions}>
        {(["ipam:read", "ipam:alloc", "ipam:admin"] as const).map((scope) => (
          <label key={scope} className={styles.field} style={{ display: "flex", gap: "0.4rem", alignItems: "center" }}>
            <input type="checkbox" checked={scopes.includes(scope)} onChange={() => toggleScope(scope)} />
            {scope}
          </label>
        ))}
      </div>
      {created ? (
        <div className={authStyles.tokenBox}>
          <p className={authStyles.success}>{t("auth.tokenCreatedOnce")}</p>
          <code className={authStyles.tokenValue}>{created}</code>
          <div className={styles.rowActions}>
            <Button
              type="button"
              onClick={() => {
                void navigator.clipboard.writeText(created).then(() => setCopied(true));
              }}
            >
              {copied ? t("auth.tokenCopied") : t("auth.copyToken")}
            </Button>
          </div>
        </div>
      ) : null}
      <table className={dcimStyles.table}>
        <thead>
          <tr>
            <th>{t("iam.colName")}</th>
            <th>{t("auth.colPrefix")}</th>
            <th>{t("auth.colCreated")}</th>
            <th>{t("auth.colLastUsed")}</th>
            <th>{t("auth.colScopes")}</th>
            <th />
          </tr>
        </thead>
        <tbody>
          {(q.data ?? []).map((tok) => (
            <tr key={tok.id}>
              <td>{tok.name}</td>
              <td>
                <code>{tok.token_prefix}…</code>
              </td>
              <td>{fmtDate(tok.created_at)}</td>
              <td>{fmtDate(tok.last_used_at)}</td>
              <td>{tok.scopes?.length ? tok.scopes.join(", ") : t("auth.scopeUnrestricted")}</td>
              <td>
                <button type="button" className={styles.tableLink} onClick={() => setRevoke(tok)}>
                  {t("auth.revokeToken")}
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {!q.isLoading && (q.data?.length ?? 0) === 0 ? <p className={styles.intro}>{t("auth.emptyTokens")}</p> : null}
      <ConfirmModal
        open={revoke != null}
        onClose={() => {
          if (!delM.isPending) setRevoke(null);
        }}
        title={t("ui.confirmTitle")}
        message={revoke ? t("auth.revokeTokenConfirm", { name: revoke.name }) : null}
        confirmLabel={t("auth.revokeToken")}
        cancelLabel={t("iam.cancel")}
        danger
        pending={delM.isPending}
        onConfirm={() => {
          if (revoke == null) return;
          delM.mutate(revoke.id);
        }}
      />
    </div>
  );
}
