import { Panel } from "@/components/ui/Panel";
import dcimStyles from "@/features/dcim/dcim.module.css";
import { useI18n } from "@/i18n/I18nProvider";

export function JobsSchedulerPage() {
  const { t } = useI18n();
  return (
    <Panel title={t("jobs.schedulerPanelTitle")}>
      <p className={dcimStyles.muted} style={{ marginTop: 0 }}>
        {t("jobs.schedulerIntro")}
      </p>
      <p className={dcimStyles.muted}>{t("netscan.schedulesHint")}</p>
      <p className={dcimStyles.muted} style={{ fontSize: "var(--text-xs)" }}>
        {t("jobs.schedulerFooter")}
      </p>
    </Panel>
  );
}
