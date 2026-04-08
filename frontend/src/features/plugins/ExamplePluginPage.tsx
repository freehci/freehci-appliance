import { useQuery } from "@tanstack/react-query";
import { Panel } from "@/components/ui/Panel";
import { apiGet } from "@/lib/api";

type Hello = { message: string };

export default function ExamplePluginPage() {
  const { data, error, isLoading } = useQuery({
    queryKey: ["plugin-example-hello"],
    queryFn: () => apiGet<Hello>("/api/v1/plugins/freehci/example/hello"),
  });

  return (
    <Panel title="Eksempel-plugin">
      <p style={{ marginTop: 0 }}>
        Dette er en innebygd frontend-modul som hører til backend-plugin{" "}
        <code>freehci.example</code>.
      </p>
      {isLoading ? <p>Laster svar fra API …</p> : null}
      {error ? (
        <p style={{ color: "var(--color-status-down)" }}>
          Klarte ikke hente API: {String(error)}
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
