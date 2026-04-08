import { Panel } from "@/components/ui/Panel";

export function PlaceholderPage({
  title,
  description,
}: {
  title: string;
  description: string;
}) {
  return (
    <Panel title={title}>
      <p style={{ marginTop: 0 }}>{description}</p>
      <p style={{ color: "var(--color-text-muted)", fontSize: "var(--text-xs)" }}>
        Placeholder – API og funksjonalitet kommer i senere faser.
      </p>
    </Panel>
  );
}
