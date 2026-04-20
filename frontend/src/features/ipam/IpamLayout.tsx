import { NavLink, Outlet } from "react-router-dom";
import dcimTabStyles from "@/features/dcim/DcimInnerTabs.module.css";
import { useI18n } from "@/i18n/I18nProvider";

function tabClass({ isActive }: { isActive: boolean }): string {
  return `${dcimTabStyles.tab} ${isActive ? dcimTabStyles.tabActive : ""}`.trim();
}

export function IpamLayout() {
  const { t } = useI18n();
  return (
    <>
      <nav className={dcimTabStyles.wrap} aria-label={t("ipam.innerNavAria")}>
        <div className={dcimTabStyles.list} role="tablist">
          <NavLink to="/ipam/prefixes" className={tabClass} role="tab" end>
            {t("ipam.tabPrefixes")}
          </NavLink>
          <NavLink to="/ipam/vlans" className={tabClass} role="tab">
            {t("ipam.tabVlans")}
          </NavLink>
          <NavLink to="/ipam/vrfs" className={tabClass} role="tab">
            {t("ipam.tabVrfs")}
          </NavLink>
          <NavLink to="/ipam/circuits" className={tabClass} role="tab">
            {t("ipam.tabCircuits")}
          </NavLink>
        </div>
      </nav>
      <Outlet />
    </>
  );
}
