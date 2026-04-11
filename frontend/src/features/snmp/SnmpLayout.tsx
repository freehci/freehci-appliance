import { NavLink, Outlet } from "react-router-dom";
import { Panel } from "@/components/ui/Panel";
import dcimTabStyles from "@/features/dcim/DcimInnerTabs.module.css";
import { useI18n } from "@/i18n/I18nProvider";

function snmpTabClass({ isActive }: { isActive: boolean }): string {
  return `${dcimTabStyles.tab} ${isActive ? dcimTabStyles.tabActive : ""}`.trim();
}

export function SnmpLayout() {
  const { t } = useI18n();
  return (
    <Panel title={t("nav.snmp")}>
      <nav className={dcimTabStyles.wrap} aria-label={t("snmp.innerNavAria")}>
        <div className={dcimTabStyles.list} role="tablist">
          <NavLink to="/snmp/tools" className={snmpTabClass} role="tab" end>
            {t("snmp.tabTools")}
          </NavLink>
          <NavLink to="/snmp/mibs" className={snmpTabClass} role="tab">
            {t("snmp.tabMibs")}
          </NavLink>
          <NavLink to="/snmp/enterprises" className={snmpTabClass} role="tab">
            {t("snmp.tabEnterprises")}
          </NavLink>
        </div>
      </nav>
      <Outlet />
    </Panel>
  );
}
