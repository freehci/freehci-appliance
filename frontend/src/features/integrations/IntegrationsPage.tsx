import { Panel } from "@/components/ui/Panel";
import { IpamWebhooksSection } from "@/features/ipam/IpamGitopsPanels";
import { useI18n } from "@/i18n/I18nProvider";

export function IntegrationsPage() {
  const { t } = useI18n();
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "1.25rem" }}>
      <Panel title={t("integrations.title")}>
        <p style={{ marginTop: 0 }}>{t("integrations.intro")}</p>
        <IpamWebhooksSection />
      </Panel>
      <Panel title={t("integrations.idracTitle")}>
        <p style={{ marginTop: 0, fontSize: "var(--text-sm)", color: "var(--color-text-muted)" }}>
          {t("integrations.idracHint")}
        </p>
      </Panel>
    </div>
  );
}
