import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { useTheme } from "@/theme/ThemeProvider";
import styles from "./TopHeader.module.css";

export function TopHeader() {
  const { theme, toggleTheme } = useTheme();

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
        <Input type="search" placeholder="Søk" aria-label="Søk" name="q" />
        <Button type="submit">Søk</Button>
      </form>

      <div className={styles.actions}>
        <button
          type="button"
          className={styles.iconBtn}
          title={theme === "dark" ? "Bytt til lys modus" : "Bytt til mørk modus"}
          onClick={toggleTheme}
        >
          <i className={`fas ${theme === "dark" ? "fa-sun" : "fa-moon"}`} />
        </button>
        <button type="button" className={styles.iconBtn} title="Bruker">
          <i className="fas fa-user" />
        </button>
      </div>
    </header>
  );
}
