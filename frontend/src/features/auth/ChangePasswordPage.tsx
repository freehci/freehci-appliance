import { type FormEvent, useState } from "react";
import { Navigate } from "react-router-dom";
import { ApiError } from "@/lib/api";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Panel } from "@/components/ui/Panel";
import { useI18n } from "@/i18n/I18nProvider";
import { changePassword } from "./authApi";
import { useAuth } from "./AuthContext";
import styles from "./authPages.module.css";

const MIN_LEN = 8;

export function ChangePasswordPage() {
  const { token } = useAuth();
  const { t } = useI18n();

  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [busy, setBusy] = useState(false);

  if (!token) {
    return <Navigate to="/login" replace />;
  }

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setSuccess(false);
    if (newPassword.length < MIN_LEN) {
      setError(t("auth.minLength"));
      return;
    }
    if (newPassword !== confirm) {
      setError(t("auth.mismatch"));
      return;
    }
    setBusy(true);
    try {
      await changePassword(currentPassword, newPassword);
      setSuccess(true);
      setCurrentPassword("");
      setNewPassword("");
      setConfirm("");
    } catch (err) {
      const msg = err instanceof ApiError ? err.message : t("auth.error");
      setError(msg);
    } finally {
      setBusy(false);
    }
  }

  return (
    <Panel title={t("auth.changePasswordTitle")}>
      <form onSubmit={onSubmit} className={styles.form}>
        <label>
          <span className="sr-only">{t("auth.currentPassword")}</span>
          <Input
            type="password"
            autoComplete="current-password"
            value={currentPassword}
            onChange={(e) => setCurrentPassword(e.target.value)}
            placeholder={t("auth.currentPassword")}
            required
          />
        </label>
        <label>
          <span className="sr-only">{t("auth.newPassword")}</span>
          <Input
            type="password"
            autoComplete="new-password"
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
            placeholder={t("auth.newPassword")}
            required
            minLength={MIN_LEN}
          />
        </label>
        <label>
          <span className="sr-only">{t("auth.newPasswordConfirm")}</span>
          <Input
            type="password"
            autoComplete="new-password"
            value={confirm}
            onChange={(e) => setConfirm(e.target.value)}
            placeholder={t("auth.newPasswordConfirm")}
            required
            minLength={MIN_LEN}
          />
        </label>
        <p className={styles.hint}>{t("auth.minLength")}</p>
        {error ? (
          <p className={styles.error} role="alert">
            {error}
          </p>
        ) : null}
        {success ? (
          <p className={styles.success} role="status">
            {t("auth.changePasswordSuccess")}
          </p>
        ) : null}
        <Button type="submit" disabled={busy}>
          {busy ? "…" : t("auth.changePasswordSubmit")}
        </Button>
      </form>
    </Panel>
  );
}
