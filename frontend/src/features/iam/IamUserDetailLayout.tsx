import { useQuery } from "@tanstack/react-query";
import { NavLink, Outlet, useParams } from "react-router-dom";
import { Panel } from "@/components/ui/Panel";
import dcimTabStyles from "@/features/dcim/DcimInnerTabs.module.css";
import { useI18n } from "@/i18n/I18nProvider";
import * as api from "./iamApi";
import styles from "./iam.module.css";

function initials(displayName: string | null | undefined, username: string): string {
  const s = (displayName ?? "").trim() || username.trim();
  const parts = s.split(/\s+/).filter(Boolean);
  if (parts.length >= 2) return (parts[0]![0]! + parts[1]![0]!).toUpperCase();
  if (parts.length === 1 && parts[0]!.length >= 2) return parts[0]!.slice(0, 2).toUpperCase();
  return (s.slice(0, 2) || "??").toUpperCase();
}

function tabClass({ isActive }: { isActive: boolean }): string {
  return `${dcimTabStyles.tab} ${isActive ? dcimTabStyles.tabActive : ""}`.trim();
}

export function IamUserDetailLayout() {
  const { t } = useI18n();
  const { userId } = useParams<{ userId: string }>();
  const id = Number(userId);

  const q = useQuery({
    queryKey: ["iam", "person", id],
    queryFn: () => api.getPerson(id),
    enabled: Number.isFinite(id),
  });

  const person = q.data;
  const title =
    q.isLoading || !person ? t("iam.userDetailLoading") : person.display_name?.trim() || person.username;

  if (!Number.isFinite(id)) {
    return (
      <Panel title={t("iam.invalidId")}>
        <p className={styles.err}>{t("iam.invalidId")}</p>
      </Panel>
    );
  }

  const about = person?.notes?.trim() || "";

  return (
    <Panel title={title}>
      {q.isError ? <p className={styles.err}>{(q.error as Error).message}</p> : null}
      {!q.isLoading && !person ? <p className={styles.err}>{t("iam.notFound")}</p> : null}
      {person ? (
        <div className={styles.userDetailGrid}>
          <aside className={styles.userDetailSidebar}>
            <div className={styles.userDetailAvatar} aria-hidden>
              {initials(person.display_name, person.username)}
            </div>
            <h2 className={styles.userDetailName}>{person.display_name?.trim() || person.username}</h2>
            {person.email ? (
              <p className={styles.userDetailMeta}>
                <a href={`mailto:${person.email}`}>{person.email}</a>
              </p>
            ) : null}
            <p className={styles.userDetailMeta}>{person.username}</p>
            <h3 className={styles.userDetailAboutTitle}>{t("iam.about")}</h3>
            <p className={styles.userDetailAbout}>{about || "—"}</p>
          </aside>
          <div className={styles.userDetailMain}>
            <nav className={`${dcimTabStyles.wrap} ${styles.userDetailTabs}`} aria-label={t("iam.userInnerNavAria")}>
              <div className={dcimTabStyles.list} role="tablist">
                <NavLink to="user" className={tabClass} role="tab" end>
                  {t("iam.userTabUser")}
                </NavLink>
                <NavLink to="login-devices" className={tabClass} role="tab">
                  {t("iam.userTabLoginDevices")}
                </NavLink>
                <NavLink to="groups" className={tabClass} role="tab">
                  {t("iam.userTabGroups")}
                </NavLink>
                <NavLink to="roles" className={tabClass} role="tab">
                  {t("iam.userTabRoles")}
                </NavLink>
                <NavLink to="applications" className={tabClass} role="tab">
                  {t("iam.userTabApplications")}
                </NavLink>
                <NavLink to="company" className={tabClass} role="tab">
                  {t("iam.userTabCompany")}
                </NavLink>
                <NavLink to="log" className={tabClass} role="tab">
                  {t("iam.userTabLog")}
                </NavLink>
              </div>
            </nav>
            <Outlet />
          </div>
        </div>
      ) : q.isLoading ? (
        <p className={styles.intro}>…</p>
      ) : null}
    </Panel>
  );
}
