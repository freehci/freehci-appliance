import { useQuery } from "@tanstack/react-query";
import { Link, useNavigate } from "react-router-dom";
import { useEffect, useId, useMemo, useState } from "react";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { fetchMe } from "@/features/auth/authApi";
import { useAuth } from "@/features/auth/AuthContext";
import * as systemApi from "@/features/system/systemApi";
import { useI18n } from "@/i18n/I18nProvider";
import { useTheme } from "@/theme/ThemeProvider";
import dcimStyles from "@/features/dcim/dcim.module.css";
import styles from "./TopHeader.module.css";

export function TopHeader() {
  const { theme, toggleTheme } = useTheme();
  const { locale, setLocale, t } = useI18n();
  const { token, logout } = useAuth();
  const navigate = useNavigate();
  const updateTitleId = useId();
  const { data: me } = useQuery({
    queryKey: ["auth", "me", token],
    queryFn: () => fetchMe(),
    enabled: Boolean(token),
    staleTime: 60_000,
  });

  const [updateOpen, setUpdateOpen] = useState(false);
  const [updateErr, setUpdateErr] = useState<string | null>(null);
  const updateEnabled = Boolean(token) && updateOpen;

  const updateStatusQ = useQuery({
    queryKey: ["system", "update-status", token],
    queryFn: () => systemApi.updateStatus(),
    enabled: updateEnabled,
    refetchInterval: updateEnabled ? 2_000 : false,
    staleTime: 0,
  });

  const logText = useMemo(() => (updateStatusQ.data?.log_tail ?? []).join("\n"), [updateStatusQ.data?.log_tail]);

  useEffect(() => {
    if (!updateOpen) setUpdateErr(null);
  }, [updateOpen]);

  useEffect(() => {
    if (!updateOpen) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") setUpdateOpen(false);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [updateOpen]);

  return (
    <header className={styles.bar}>
      <div className={styles.brand}>
        <span className={styles.logo} aria-hidden>
          FH
        </span>
        <span>FreeHCI</span>
      </div>

      <form
        className={styles.search}
        onSubmit={(e) => {
          e.preventDefault();
        }}
      >
        <Input
          type="search"
          placeholder={t("header.searchPlaceholder")}
          aria-label={t("header.searchAria")}
          name="q"
        />
        <Button type="submit">{t("header.search")}</Button>
      </form>

      <div className={styles.actions}>
        <div className={styles.lang} role="group" aria-label={t("header.langSwitch")}>
          <button
            type="button"
            className={`${styles.langBtn} ${locale === "nb" ? styles.langBtnActive : ""}`.trim()}
            title={t("header.langNb")}
            onClick={() => setLocale("nb")}
          >
            NB
          </button>
          <button
            type="button"
            className={`${styles.langBtn} ${locale === "en" ? styles.langBtnActive : ""}`.trim()}
            title={t("header.langEn")}
            onClick={() => setLocale("en")}
          >
            EN
          </button>
        </div>
        <button
          type="button"
          className={styles.iconBtn}
          title={theme === "dark" ? t("header.themeToLight") : t("header.themeToDark")}
          onClick={toggleTheme}
        >
          <i className={`fas ${theme === "dark" ? "fa-sun" : "fa-moon"}`} />
        </button>
        {me?.username ? (
          <button
            type="button"
            className={styles.iconBtn}
            title={t("header.updateNow")}
            aria-label={t("header.updateNow")}
            onClick={() => setUpdateOpen(true)}
          >
            <i className="fas fa-arrows-rotate" aria-hidden />
          </button>
        ) : null}
        {me?.username ? (
          <span className={styles.userName} title={me.username}>
            {me.username}
          </span>
        ) : null}
        <Link
          to="/account/password"
          className={styles.iconBtn}
          title={t("header.changePassword")}
          aria-label={t("header.changePassword")}
        >
          <i className="fas fa-key" aria-hidden />
        </Link>
        <button
          type="button"
          className={styles.iconBtn}
          title={t("header.logout")}
          aria-label={t("header.logout")}
          onClick={() => {
            logout();
            navigate("/login", { replace: true });
          }}
        >
          <i className="fas fa-right-from-bracket" aria-hidden />
        </button>
      </div>

      {updateOpen ? (
        <div
          role="presentation"
          style={{
            position: "fixed",
            inset: 0,
            zIndex: 210,
            background: "rgba(0,0,0,0.45)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            padding: "var(--space-3)",
          }}
          onClick={(e) => {
            if (e.target === e.currentTarget) setUpdateOpen(false);
          }}
        >
          <div
            role="dialog"
            aria-modal="true"
            aria-labelledby={updateTitleId}
            style={{
              width: "min(40rem, 100%)",
              maxHeight: "90vh",
              overflow: "auto",
              background: "var(--color-bg-elevated)",
              border: "1px solid var(--shell-border)",
              borderRadius: "var(--radius-md)",
              padding: "var(--space-4)",
              boxShadow: "0 8px 32px rgba(0,0,0,0.2)",
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <h2 id={updateTitleId} style={{ marginTop: 0, marginBottom: "0.25rem" }}>
              {t("system.updateTitle")}
            </h2>
            <p className={dcimStyles.muted} style={{ marginBottom: "var(--space-2)" }}>
              {t("system.updateIntro")}
            </p>

            {updateStatusQ.isError ? (
              <p className={dcimStyles.err}>{(updateStatusQ.error as Error).message}</p>
            ) : null}
            {updateErr ? <p className={dcimStyles.err}>{updateErr}</p> : null}

            <div
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                gap: "var(--space-2)",
                flexWrap: "wrap",
                border: "1px solid var(--shell-border)",
                borderRadius: "var(--radius-sm)",
                padding: "var(--space-2)",
                background: "var(--color-bg-surface)",
              }}
            >
              <div style={{ display: "flex", gap: "0.5rem", alignItems: "center", flexWrap: "wrap" }}>
                <span className={dcimStyles.muted} style={{ margin: 0 }}>
                  {t("system.updateStatus")}
                </span>
                <span style={{ fontFamily: "monospace", fontSize: "var(--text-xs)" }}>
                  {updateStatusQ.data?.running ? t("system.updateRunning") : updateStatusQ.data?.detail ?? "—"}
                  {updateStatusQ.data?.exit_code != null ? ` (exit ${String(updateStatusQ.data.exit_code)})` : ""}
                </span>
              </div>
              <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
                <button
                  type="button"
                  className={dcimStyles.btn}
                  disabled={updateStatusQ.data?.running === true}
                  onClick={async () => {
                    setUpdateErr(null);
                    try {
                      await systemApi.updateNow();
                      void updateStatusQ.refetch();
                    } catch (e) {
                      setUpdateErr(e instanceof Error ? e.message : String(e));
                    }
                  }}
                >
                  {updateStatusQ.data?.running ? "…" : t("system.updateNowBtn")}
                </button>
                <button type="button" className={dcimStyles.btnMuted} onClick={() => setUpdateOpen(false)}>
                  {t("system.close")}
                </button>
              </div>
            </div>

            <div style={{ marginTop: "var(--space-3)" }}>
              <pre
                style={{
                  margin: 0,
                  padding: "0.75rem",
                  border: "1px solid var(--shell-border)",
                  borderRadius: "var(--radius-sm)",
                  maxHeight: "22rem",
                  overflow: "auto",
                  background: "var(--color-bg)",
                  whiteSpace: "pre-wrap",
                  fontFamily: "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, \"Liberation Mono\", \"Courier New\", monospace",
                  fontSize: "0.8rem",
                  lineHeight: 1.35,
                }}
              >
                {logText || "…"}
              </pre>
              <p className={dcimStyles.muted} style={{ marginTop: "var(--space-2)", marginBottom: 0 }}>
                {t("system.updateFallback")}
              </p>
            </div>
          </div>
        </div>
      ) : null}
    </header>
  );
}
