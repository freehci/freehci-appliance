import { Badge } from "@/components/ui/Badge";
import { Panel } from "@/components/ui/Panel";

export function DashboardPage() {
  return (
    <Panel title="Dashboard">
      <p style={{ marginTop: 0 }}>
        Velkommen til FreeHCI. Dette er det nye skallet med tema og plugin-støtte.
      </p>
      <p>
        <Badge tone="ok">API</Badge>{" "}
        <span style={{ fontSize: "var(--text-xs)", color: "var(--color-text-muted)" }}>
          Koble til backend via <code>/api/v1</code>
        </span>
      </p>
    </Panel>
  );
}
