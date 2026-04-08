import { Panel } from "@/components/ui/Panel";
import { useI18n } from "@/i18n/I18nProvider";
import type { MessageKey } from "@/i18n/messages/en";

export function PlaceholderPage({
  titleKey,
  descriptionKey,
}: {
  titleKey: MessageKey;
  descriptionKey: MessageKey;
}) {
  const { t } = useI18n();
  return (
    <Panel title={t(titleKey)}>
      <p style={{ marginTop: 0 }}>{t(descriptionKey)}</p>
      <p style={{ color: "var(--color-text-muted)", fontSize: "var(--text-xs)" }}>
        {t("placeholders.footer")}
      </p>
    </Panel>
  );
}
