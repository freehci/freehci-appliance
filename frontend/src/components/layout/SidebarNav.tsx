import { NavLink } from "react-router-dom";
import { useI18n } from "@/i18n/I18nProvider";
import styles from "./SidebarNav.module.css";

type MainNavItem = { to: string; label: string; end?: boolean };

export function SidebarNav() {
  const { t } = useI18n();

  const mainNav: MainNavItem[] = [
    { to: "/", label: t("nav.dashboard"), end: true },
    { to: "/ipam", label: t("nav.ipam") },
    { to: "/snmp", label: t("nav.snmp") },
    { to: "/jobs", label: t("nav.jobs") },
    { to: "/integrations", label: t("nav.integrations") },
    { to: "/service-catalog", label: t("nav.serviceCatalog") },
  ];

  return (
    <nav className={styles.wrap} aria-label={t("nav.mainAria")}>
      <ul className={styles.list}>
        {mainNav.map(({ to, label, end }) => (
          <li key={to} className={styles.item}>
            <NavLink
              to={to}
              end={end}
              className={({ isActive }) =>
                `${styles.link} ${isActive ? styles.active : ""}`.trim()
              }
            >
              {label}
            </NavLink>
          </li>
        ))}
        <li className={styles.item}>
          <div className={styles.section}>{t("nav.iamSection")}</div>
          <ul className={styles.sub}>
            <li>
              <NavLink
                to="/iam"
                className={({ isActive }) =>
                  `${styles.link} ${isActive ? styles.active : ""}`.trim()
                }
              >
                {t("nav.iam")}
              </NavLink>
            </li>
          </ul>
        </li>
        <li className={styles.item}>
          <div className={styles.section}>{t("nav.dcimSection")}</div>
          <ul className={styles.sub}>
            <li>
              <NavLink
                to="/dcim"
                end
                className={({ isActive }) =>
                  `${styles.link} ${isActive ? styles.active : ""}`.trim()
                }
              >
                {t("nav.dcimOverview")}
              </NavLink>
            </li>
            <li>
              <NavLink
                to="/dcim/sites"
                className={({ isActive }) =>
                  `${styles.link} ${isActive ? styles.active : ""}`.trim()
                }
              >
                {t("nav.dcimSites")}
              </NavLink>
            </li>
            <li>
              <NavLink
                to="/dcim/rooms"
                className={({ isActive }) =>
                  `${styles.link} ${isActive ? styles.active : ""}`.trim()
                }
              >
                {t("nav.dcimRooms")}
              </NavLink>
            </li>
            <li>
              <NavLink
                to="/dcim/racks"
                className={({ isActive }) =>
                  `${styles.link} ${isActive ? styles.active : ""}`.trim()
                }
              >
                {t("nav.dcimRacks")}
              </NavLink>
            </li>
            <li>
              <NavLink
                to="/dcim/equipment"
                className={({ isActive }) =>
                  `${styles.link} ${isActive ? styles.active : ""}`.trim()
                }
              >
                {t("nav.dcimEquipment")}
              </NavLink>
            </li>
          </ul>
        </li>
        <li className={styles.item}>
          <div className={styles.section}>{t("nav.pluginsSection")}</div>
          <ul className={styles.sub}>
            <li>
              <NavLink
                to="/plugins/freehci.example"
                className={({ isActive }) =>
                  `${styles.link} ${isActive ? styles.active : ""}`.trim()
                }
              >
                {t("nav.pluginsExample")}
              </NavLink>
            </li>
          </ul>
        </li>
      </ul>
    </nav>
  );
}
