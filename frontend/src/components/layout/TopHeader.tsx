import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { useI18n } from "@/i18n/I18nProvider";
import { useTheme } from "@/theme/ThemeProvider";
import styles from "./TopHeader.module.css";

export function TopHeader() {
  const { theme, toggleTheme } = useTheme();
  const { locale, setLocale, t } = useI18n();

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
        <button type="button" className={styles.iconBtn} title={t("header.user")}>
          <i className="fas fa-user" />
        </button>
      </div>
    </header>
  );
}
