import { Panel } from "@/components/ui/Panel";
import { useI18n } from "@/i18n/I18nProvider";
import styles from "./dcim.module.css";

export function DcimOverviewPage() {
  const { t } = useI18n();
  return (
    <Panel title={t("dcim.overview.title")}>
      <p className={styles.muted} style={{ marginTop: 0 }}>
        {t("dcim.overview.p1")} <code>/api/v1/dcim</code>.
      </p>
      <p style={{ fontSize: "var(--text-sm)" }}>{t("dcim.overview.p2")}</p>
    </Panel>
  );
}
