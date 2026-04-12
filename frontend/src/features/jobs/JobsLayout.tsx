import { NavLink, Outlet } from "react-router-dom";
import { Panel } from "@/components/ui/Panel";
import dcimTabStyles from "@/features/dcim/DcimInnerTabs.module.css";
import { useI18n } from "@/i18n/I18nProvider";
import { JobsTabIcon } from "./JobsTabIcon";

function jobsTabClass({ isActive }: { isActive: boolean }): string {
  return `${dcimTabStyles.tab} ${isActive ? dcimTabStyles.tabActive : ""}`.trim();
}

export function JobsLayout() {
  const { t } = useI18n();
  return (
    <Panel title={t("nav.jobs")}>
      <nav className={dcimTabStyles.wrap} aria-label={t("jobs.innerNavAria")}>
        <div className={dcimTabStyles.list} role="tablist">
          <NavLink to="/jobs" className={jobsTabClass} role="tab" end>
            <span className={dcimTabStyles.iconWrap}>
              <JobsTabIcon name="jobs" />
            </span>
            <span>{t("jobs.tabJobs")}</span>
          </NavLink>
          <NavLink to="/jobs/scheduler" className={jobsTabClass} role="tab">
            <span className={dcimTabStyles.iconWrap}>
              <JobsTabIcon name="scheduler" />
            </span>
            <span>{t("jobs.tabScheduler")}</span>
          </NavLink>
          <NavLink to="/jobs/templates" className={jobsTabClass} role="tab">
            <span className={dcimTabStyles.iconWrap}>
              <JobsTabIcon name="templates" />
            </span>
            <span>{t("jobs.tabTemplates")}</span>
          </NavLink>
        </div>
      </nav>
      <Outlet />
    </Panel>
  );
}
