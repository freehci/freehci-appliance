import { Link, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { useAuth } from "@/features/auth/AuthContext";
import { useI18n } from "@/i18n/I18nProvider";
import { useTheme } from "@/theme/ThemeProvider";
import styles from "./TopHeader.module.css";

export function TopHeader() {
  const { theme, toggleTheme } = useTheme();
  const { locale, setLocale, t } = useI18n();
  const { logout } = useAuth();
  const navigate = useNavigate();

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
    </header>
  );
}
