import { NavLink, Outlet } from "react-router-dom";
import { Panel } from "@/components/ui/Panel";
import dcimTabStyles from "@/features/dcim/DcimInnerTabs.module.css";
import { useI18n } from "@/i18n/I18nProvider";
import { IamTabIcon } from "./IamTabIcon";
import styles from "./iam.module.css";

function tabClass({ isActive }: { isActive: boolean }): string {
  return `${dcimTabStyles.tab} ${isActive ? dcimTabStyles.tabActive : ""}`.trim();
}

export function IamLayout() {
  const { t } = useI18n();
  return (
    <Panel title={t("iam.title")}>
      <p className={styles.intro}>{t("iam.intro")}</p>
      <nav className={dcimTabStyles.wrap} aria-label={t("iam.innerNavAria")}>
        <div className={dcimTabStyles.list} role="tablist">
          <NavLink to="/iam/persons" className={tabClass} role="tab">
            <span className={dcimTabStyles.iconWrap}>
              <IamTabIcon name="persons" />
            </span>
            <span>{t("iam.tabPersons")}</span>
          </NavLink>
          <NavLink to="/iam/service-accounts" className={tabClass} role="tab">
            <span className={dcimTabStyles.iconWrap}>
              <IamTabIcon name="serviceAccounts" />
            </span>
            <span>{t("iam.tabServiceAccounts")}</span>
          </NavLink>
          <NavLink to="/iam/roles" className={tabClass} role="tab">
            <span className={dcimTabStyles.iconWrap}>
              <IamTabIcon name="roles" />
            </span>
            <span>{t("iam.tabRoles")}</span>
          </NavLink>
          <NavLink to="/iam/groups" className={tabClass} role="tab">
            <span className={dcimTabStyles.iconWrap}>
              <IamTabIcon name="groups" />
            </span>
            <span>{t("iam.tabGroups")}</span>
          </NavLink>
        </div>
      </nav>
      <Outlet />
    </Panel>
  );
}
