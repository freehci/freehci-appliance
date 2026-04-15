import { NavLink, Outlet } from "react-router-dom";
import { Panel } from "@/components/ui/Panel";
import dcimTabStyles from "@/features/dcim/DcimInnerTabs.module.css";
import { useI18n } from "@/i18n/I18nProvider";
import { SnmpTabIcon } from "./SnmpTabIcon";

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
            <span className={dcimTabStyles.iconWrap}>
              <SnmpTabIcon name="tools" />
            </span>
            <span>{t("snmp.tabTools")}</span>
          </NavLink>
          <NavLink to="/snmp/mibs" className={snmpTabClass} role="tab">
            <span className={dcimTabStyles.iconWrap}>
              <SnmpTabIcon name="mibs" />
            </span>
            <span>{t("snmp.tabMibs")}</span>
          </NavLink>
          <NavLink to="/snmp/enterprises" className={snmpTabClass} role="tab">
            <span className={dcimTabStyles.iconWrap}>
              <SnmpTabIcon name="enterprises" />
            </span>
            <span>{t("snmp.tabEnterprises")}</span>
          </NavLink>
          <NavLink to="/snmp/browser" className={snmpTabClass} role="tab">
            <span className={dcimTabStyles.iconWrap}>
              <SnmpTabIcon name="browser" />
            </span>
            <span>{t("snmp.tabBrowser")}</span>
          </NavLink>
        </div>
      </nav>
      <Outlet />
    </Panel>
  );
}
