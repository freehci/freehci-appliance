import { Badge } from "@/components/ui/Badge";
import { Panel } from "@/components/ui/Panel";
import { useI18n } from "@/i18n/I18nProvider";

export function DashboardPage() {
  const { t } = useI18n();
  return (
    <Panel title={t("dashboard.title")}>
      <p style={{ marginTop: 0 }}>{t("dashboard.welcome")}</p>
      <p>
        <Badge tone="ok">{t("dashboard.apiBadge")}</Badge>{" "}
        <span style={{ fontSize: "var(--text-xs)", color: "var(--color-text-muted)" }}>
          {t("dashboard.apiHint")} <code>/api/v1</code>
        </span>
      </p>
    </Panel>
  );
}
