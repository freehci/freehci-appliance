import { NavLink } from "react-router-dom";
import dcimTabStyles from "@/features/dcim/DcimInnerTabs.module.css";
import { useI18n } from "@/i18n/I18nProvider";

function familyClass({ isActive }: { isActive: boolean }): string {
  return `${dcimTabStyles.tab} ${isActive ? dcimTabStyles.tabActive : ""}`.trim();
}

export function IpamFamilyTabs() {
  const { t } = useI18n();
  return (
    <nav className={dcimTabStyles.wrap} aria-label={t("ipam.family.aria")}>
      <div className={dcimTabStyles.list} role="tablist">
        <NavLink to="/ipam/prefixes" className={familyClass} role="tab" end>
          {t("ipam.family.ipv4")}
        </NavLink>
        <NavLink to="/ipam/ipv6" className={familyClass} role="tab">
          {t("ipam.family.ipv6")}
        </NavLink>
      </div>
    </nav>
  );
}
