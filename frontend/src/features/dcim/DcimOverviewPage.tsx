import { useState } from "react";
import { Panel } from "@/components/ui/Panel";
import { useI18n } from "@/i18n/I18nProvider";
import { DcimInnerTabs } from "./DcimInnerTabs";
import styles from "./dcim.module.css";

export function DcimOverviewPage() {
  const { t } = useI18n();
  const [tab, setTab] = useState("main");
  return (
    <Panel title={t("nav.dcimOverview")}>
      <DcimInnerTabs
        tabs={[{ id: "main", label: t("nav.dcimOverview") }]}
        activeId={tab}
        onChange={setTab}
        ariaLabel={t("dcim.innerNavAria")}
      />
      {tab === "main" ? (
        <>
          <p className={styles.muted} style={{ marginTop: 0 }}>
            {t("dcim.overview.p1")} <code>/api/v1/dcim</code>.
          </p>
          <p style={{ fontSize: "var(--text-sm)" }}>{t("dcim.overview.p2")}</p>
        </>
      ) : null}
    </Panel>
  );
}
