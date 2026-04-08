import { useQuery } from "@tanstack/react-query";
import { Panel } from "@/components/ui/Panel";
import { useI18n } from "@/i18n/I18nProvider";
import { apiGet } from "@/lib/api";

type Hello = { message: string };

export default function ExamplePluginPage() {
  const { t } = useI18n();
  const { data, error, isLoading } = useQuery({
    queryKey: ["plugin-example-hello"],
    queryFn: () => apiGet<Hello>("/api/v1/plugins/freehci/example/hello"),
  });

  return (
    <Panel title={t("plugin.example.title")}>
      <p style={{ marginTop: 0 }}>
        {t("plugin.example.intro")}
      </p>
      {isLoading ? <p>{t("plugin.example.loading")}</p> : null}
      {error ? (
        <p style={{ color: "var(--color-status-down)" }}>
          {t("plugin.example.errorPrefix")} {String(error)}
        </p>
      ) : null}
      {data ? (
        <pre
          style={{
            padding: "var(--space-3)",
            background: "var(--color-bg-elevated)",
            border: "1px solid var(--color-border)",
            borderRadius: "var(--radius-sm)",
            fontSize: "var(--text-sm)",
          }}
        >
          {JSON.stringify(data, null, 2)}
        </pre>
      ) : null}
    </Panel>
  );
}
