import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { Link } from "react-router-dom";
import { ConfirmModal } from "@/components/ui/ConfirmModal";
import { Button } from "@/components/ui/Button";
import { Panel } from "@/components/ui/Panel";
import { useI18n } from "@/i18n/I18nProvider";
import { ApiError } from "@/lib/api";
import dcimStyles from "@/features/dcim/dcim.module.css";
import iamStyles from "@/features/iam/iam.module.css";
import * as api from "./authApi";
import styles from "./authPages.module.css";

function fmtDate(v: string | null | undefined): string {
  if (!v) return "—";
  const d = new Date(v);
  if (Number.isNaN(d.getTime())) return v;
  return d.toLocaleString();
}

export function AccountAccessPage() {
  const { t } = useI18n();
  const qc = useQueryClient();
  const [err, setErr] = useState<string | null>(null);

  const [newUser, setNewUser] = useState("");
  const [newPw, setNewPw] = useState("");
  const [resetId, setResetId] = useState<number | null>(null);
  const [resetPw, setResetPw] = useState("");
  const [resetPw2, setResetPw2] = useState("");
  const [deleteAccount, setDeleteAccount] = useState<api.AdminAccount | null>(null);
  const [resetOk, setResetOk] = useState<string | null>(null);

  const [tokenName, setTokenName] = useState("");
  const [createdToken, setCreatedToken] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);
  const [revokeToken, setRevokeToken] = useState<api.ApiToken | null>(null);
  const [tokenScopes, setTokenScopes] = useState<string[]>([]);

  function toggleTokenScope(scope: string) {
    setTokenScopes((cur) => (cur.includes(scope) ? cur.filter((s) => s !== scope) : [...cur, scope]));
  }

  const accountsQ = useQuery({ queryKey: ["auth", "accounts"], queryFn: api.listAccounts });
  const tokensQ = useQuery({ queryKey: ["auth", "tokens"], queryFn: api.listApiTokens });
  const agentQ = useQuery({ queryKey: ["auth", "agent"], queryFn: api.fetchAgentInfo });

  const createAccM = useMutation({
    mutationFn: () => api.createAccount(newUser.trim(), newPw),
    onSuccess: () => {
      setErr(null);
      setNewUser("");
      setNewPw("");
      void qc.invalidateQueries({ queryKey: ["auth", "accounts"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const resetM = useMutation({
    mutationFn: () => api.resetAccountPassword(resetId as number, resetPw),
    onSuccess: () => {
      const row = (accountsQ.data ?? []).find((a) => a.id === resetId);
      setErr(null);
      setResetOk(row?.username ?? "");
      setResetId(null);
      setResetPw("");
      setResetPw2("");
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const delAccM = useMutation({
    mutationFn: (id: number) => api.deleteAccount(id),
    onSuccess: () => {
      setErr(null);
      setDeleteAccount(null);
      void qc.invalidateQueries({ queryKey: ["auth", "accounts"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const createTokM = useMutation({
    mutationFn: () => api.createApiToken(tokenName.trim(), tokenScopes.length ? tokenScopes : null),
    onSuccess: (row) => {
      setErr(null);
      setTokenName("");
      setTokenScopes([]);
      setCreatedToken(row.token);
      setCopied(false);
      void qc.invalidateQueries({ queryKey: ["auth", "tokens"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const delTokM = useMutation({
    mutationFn: (id: number) => api.deleteApiToken(id),
    onSuccess: () => {
      setErr(null);
      setRevokeToken(null);
      void qc.invalidateQueries({ queryKey: ["auth", "tokens"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const resetTarget = (accountsQ.data ?? []).find((a) => a.id === resetId);
  const canCreate = newUser.trim().length > 0 && newPw.length >= 8;
  const canReset = resetPw.length >= 8 && resetPw === resetPw2;

  return (
    <>
      <Panel title={t("auth.accountsTitle")}>
        <p className={iamStyles.intro}>{t("auth.accountsIntro")}</p>
        <p className={iamStyles.intro}>
          <Link className={iamStyles.tableLink} to="/account/password">
            {t("auth.changePasswordTitle")}
          </Link>
        </p>
        {err ? (
          <p className={styles.error} role="alert">
            {err}
          </p>
        ) : null}
        {resetOk ? (
          <p className={styles.success} role="status">
            {t("auth.resetPasswordSuccess", { username: resetOk })}
          </p>
        ) : null}

        <div className={iamStyles.rowActions}>
          <div className={iamStyles.field}>
            <label htmlFor="acc-user">{t("auth.username")}</label>
            <input
              id="acc-user"
              value={newUser}
              onChange={(e) => setNewUser(e.target.value)}
              autoComplete="off"
            />
          </div>
          <div className={iamStyles.field}>
            <label htmlFor="acc-pw">{t("auth.password")}</label>
            <input
              id="acc-pw"
              type="password"
              value={newPw}
              onChange={(e) => setNewPw(e.target.value)}
              autoComplete="new-password"
              minLength={8}
            />
          </div>
          <Button type="button" onClick={() => createAccM.mutate()} disabled={!canCreate || createAccM.isPending}>
            {t("auth.createAccount")}
          </Button>
        </div>
        <p className={styles.hint}>{t("auth.minLength")}</p>

        <table className={dcimStyles.table}>
          <thead>
            <tr>
              <th>{t("auth.username")}</th>
              <th>{t("auth.colUpdated")}</th>
              <th />
            </tr>
          </thead>
          <tbody>
            {(accountsQ.data ?? []).map((a) => (
              <tr key={a.id}>
                <td>
                  {a.username}
                  {a.is_self ? ` (${t("auth.you")})` : ""}
                </td>
                <td>{fmtDate(a.updated_at)}</td>
                <td>
                  <button type="button" className={iamStyles.tableLink} onClick={() => setResetId(a.id)}>
                    {t("auth.resetPassword")}
                  </button>
                  {!a.is_self ? (
                    <>
                      {" · "}
                      <button type="button" className={iamStyles.tableLink} onClick={() => setDeleteAccount(a)}>
                        {t("auth.deleteAccount")}
                      </button>
                    </>
                  ) : null}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {!accountsQ.isLoading && (accountsQ.data?.length ?? 0) === 0 ? (
          <p className={iamStyles.intro}>{t("auth.emptyAccounts")}</p>
        ) : null}

        {resetId != null && resetTarget ? (
          <div className={iamStyles.rowActions}>
            <p className={iamStyles.intro} style={{ width: "100%", marginBottom: 0 }}>
              {t("auth.resetPassword")} — {resetTarget.username}
            </p>
            <div className={iamStyles.field}>
              <label htmlFor="acc-reset-pw">{t("auth.newPassword")}</label>
              <input
                id="acc-reset-pw"
                type="password"
                value={resetPw}
                onChange={(e) => setResetPw(e.target.value)}
                autoComplete="new-password"
                minLength={8}
              />
            </div>
            <div className={iamStyles.field}>
              <label htmlFor="acc-reset-pw2">{t("auth.newPasswordConfirm")}</label>
              <input
                id="acc-reset-pw2"
                type="password"
                value={resetPw2}
                onChange={(e) => setResetPw2(e.target.value)}
                autoComplete="new-password"
                minLength={8}
              />
            </div>
            <Button
              type="button"
              onClick={() => {
                if (resetPw !== resetPw2) {
                  setErr(t("auth.mismatch"));
                  return;
                }
                resetM.mutate();
              }}
              disabled={!canReset || resetM.isPending}
            >
              {t("auth.resetPasswordSubmit")}
            </Button>
            <Button type="button" variant="ghost" onClick={() => setResetId(null)}>
              {t("iam.cancel")}
            </Button>
          </div>
        ) : null}
      </Panel>

      <Panel title={t("auth.tokensTitle")}>
        <p className={iamStyles.intro}>{t("auth.tokensIntro")}</p>
        {agentQ.data ? (
          <p className={iamStyles.intro}>
            <a className={iamStyles.tableLink} href={agentQ.data.docs_url} target="_blank" rel="noreferrer">
              {t("auth.agentDocs")}
            </a>
            {" · "}
            <a className={iamStyles.tableLink} href={agentQ.data.openapi_url} target="_blank" rel="noreferrer">
              {t("auth.agentOpenapi")}
            </a>
            {" · "}
            <code>{agentQ.data.auth.header}</code>
          </p>
        ) : null}

        <div className={iamStyles.rowActions}>
          <div className={iamStyles.field}>
            <label htmlFor="tok-name">{t("auth.tokenName")}</label>
            <input
              id="tok-name"
              value={tokenName}
              onChange={(e) => setTokenName(e.target.value)}
              autoComplete="off"
            />
          </div>
          <Button
            type="button"
            onClick={() => createTokM.mutate()}
            disabled={!tokenName.trim() || createTokM.isPending}
          >
            {t("auth.createToken")}
          </Button>
        </div>
        <p className={iamStyles.intro}>{t("auth.tokenScopesHint")}</p>
        <div className={iamStyles.rowActions}>
          {(["ipam:read", "ipam:alloc", "ipam:admin"] as const).map((scope) => (
            <label key={scope} className={iamStyles.field} style={{ display: "flex", gap: "0.4rem", alignItems: "center" }}>
              <input
                type="checkbox"
                checked={tokenScopes.includes(scope)}
                onChange={() => toggleTokenScope(scope)}
              />
              {scope}
            </label>
          ))}
        </div>

        {createdToken ? (
          <div className={styles.tokenBox}>
            <p className={styles.success}>{t("auth.tokenCreatedOnce")}</p>
            <code className={styles.tokenValue}>{createdToken}</code>
            <div className={iamStyles.rowActions}>
              <Button
                type="button"
                onClick={() => {
                  void navigator.clipboard.writeText(createdToken).then(() => setCopied(true));
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
            {(tokensQ.data ?? []).map((tok) => (
              <tr key={tok.id}>
                <td>{tok.name}</td>
                <td>
                  <code>{tok.token_prefix}…</code>
                </td>
                <td>{fmtDate(tok.created_at)}</td>
                <td>{fmtDate(tok.last_used_at)}</td>
                <td>{tok.scopes?.length ? tok.scopes.join(", ") : t("auth.scopeUnrestricted")}</td>
                <td>
                  <button type="button" className={iamStyles.tableLink} onClick={() => setRevokeToken(tok)}>
                    {t("auth.revokeToken")}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {!tokensQ.isLoading && (tokensQ.data?.length ?? 0) === 0 ? (
          <p className={iamStyles.intro}>{t("auth.emptyTokens")}</p>
        ) : null}
      </Panel>

      <ConfirmModal
        open={deleteAccount != null}
        onClose={() => {
          if (!delAccM.isPending) setDeleteAccount(null);
        }}
        title={t("ui.confirmTitle")}
        message={deleteAccount ? t("auth.deleteAccountConfirm", { username: deleteAccount.username }) : null}
        confirmLabel={t("auth.deleteAccount")}
        cancelLabel={t("iam.cancel")}
        danger
        pending={delAccM.isPending}
        onConfirm={() => {
          if (deleteAccount == null) return;
          delAccM.mutate(deleteAccount.id);
        }}
      />
      <ConfirmModal
        open={revokeToken != null}
        onClose={() => {
          if (!delTokM.isPending) setRevokeToken(null);
        }}
        title={t("ui.confirmTitle")}
        message={revokeToken ? t("auth.revokeTokenConfirm", { name: revokeToken.name }) : null}
        confirmLabel={t("auth.revokeToken")}
        cancelLabel={t("iam.cancel")}
        danger
        pending={delTokM.isPending}
        onConfirm={() => {
          if (revokeToken == null) return;
          delTokM.mutate(revokeToken.id);
        }}
      />
    </>
  );
}
