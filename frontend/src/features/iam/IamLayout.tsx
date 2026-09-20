import { NavLink, Outlet } from "react-router-dom";
import dcimTabStyles from "@/features/dcim/DcimInnerTabs.module.css";
import { useI18n } from "@/i18n/I18nProvider";
import { IamTabIcon } from "./IamTabIcon";

function iamTabClass({ isActive }: { isActive: boolean }): string {
  return `${dcimTabStyles.tab} ${isActive ? dcimTabStyles.tabActive : ""}`.trim();
}

export function IamLayout() {
  const { t } = useI18n();
  return (
    <div>
      <nav className={dcimTabStyles.wrap} aria-label={t("iam.innerNavAria")}>
        <div className={dcimTabStyles.list} role="tablist">
          <NavLink to="/iam/users" className={iamTabClass} role="tab">
            <span className={dcimTabStyles.iconWrap}>
              <IamTabIcon name="persons" />
            </span>
            <span>{t("nav.iamUsers")}</span>
          </NavLink>
          <NavLink to="/iam/service-accounts" className={iamTabClass} role="tab">
            <span className={dcimTabStyles.iconWrap}>
              <IamTabIcon name="serviceAccounts" />
            </span>
            <span>{t("nav.iamServiceAccountsNav")}</span>
          </NavLink>
          <NavLink to="/iam/roles" className={iamTabClass} role="tab">
            <span className={dcimTabStyles.iconWrap}>
              <IamTabIcon name="roles" />
            </span>
            <span>{t("nav.iamRolesNav")}</span>
          </NavLink>
          <NavLink to="/iam/groups" className={iamTabClass} role="tab">
            <span className={dcimTabStyles.iconWrap}>
              <IamTabIcon name="groups" />
            </span>
            <span>{t("nav.iamGroupsNav")}</span>
          </NavLink>
        </div>
      </nav>
      <Outlet />
    </div>
  );
}
