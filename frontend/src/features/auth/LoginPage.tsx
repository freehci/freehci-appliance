import { type FormEvent, useState } from "react";
import { Navigate, useLocation, useNavigate } from "react-router-dom";
import { ApiError } from "@/lib/api";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Panel } from "@/components/ui/Panel";
import { useI18n } from "@/i18n/I18nProvider";
import { login } from "./authApi";
import { useAuth } from "./AuthContext";
import styles from "./authPages.module.css";

export function LoginPage() {
  const { token, setToken } = useAuth();
  const { t } = useI18n();
  const navigate = useNavigate();
  const location = useLocation();
  const fromRaw = (location.state as { from?: string } | null)?.from ?? "/";
  const from = fromRaw.startsWith("/login") ? "/" : fromRaw;

  const [username, setUsername] = useState("admin");
  const [password, setPassword] = useState("admin");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  if (token) {
    return <Navigate to={from} replace />;
  }

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setBusy(true);
    try {
      const data = await login(username, password);
      setToken(data.access_token);
      navigate(from, { replace: true });
    } catch (err) {
      const msg = err instanceof ApiError ? err.message : t("auth.error");
      setError(msg);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className={styles.center}>
      <Panel title={t("auth.loginTitle")}>
        <form onSubmit={onSubmit} className={styles.form}>
          <label>
            <span className="sr-only">{t("auth.username")}</span>
            <Input
              name="username"
              autoComplete="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder={t("auth.username")}
              required
            />
          </label>
          <label>
            <span className="sr-only">{t("auth.password")}</span>
            <Input
              type="password"
              name="password"
              autoComplete="current-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder={t("auth.password")}
              required
            />
          </label>
          {error ? (
            <p className={styles.error} role="alert">
              {error}
            </p>
          ) : null}
          <Button type="submit" disabled={busy}>
            {busy ? "…" : t("auth.submit")}
          </Button>
        </form>
        <p className={styles.hint}>{t("auth.defaultCredsHint")}</p>
      </Panel>
    </div>
  );
}
