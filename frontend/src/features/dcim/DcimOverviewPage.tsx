import { Panel } from "@/components/ui/Panel";
import styles from "./dcim.module.css";

export function DcimOverviewPage() {
  return (
    <Panel title="DCIM">
      <p className={styles.muted} style={{ marginTop: 0 }}>
        Håndter datasentre: sites, rom, racks, enhetsmodeller og plassering i U-posisjoner. Data lagres via{" "}
        <code>/api/v1/dcim</code>.
      </p>
      <p style={{ fontSize: "var(--text-sm)" }}>
        Bruk undermenyen for å opprette og liste ressurser. Sletting av produsenter og plasseringer er tilgjengelig der
        det støttes i API-et.
      </p>
    </Panel>
  );
}
