import { NavLink } from "react-router-dom";
import { useI18n } from "@/i18n/I18nProvider";
import { SidebarNavIcon, type SidebarNavIconName } from "./SidebarNavIcon";
import styles from "./SidebarNav.module.css";

type MainNavItem = { to: string; label: string; end?: boolean; icon: SidebarNavIconName };

export function SidebarNav() {
  const { t } = useI18n();

  const mainNav: MainNavItem[] = [
    { to: "/", label: t("nav.dashboard"), end: true, icon: "dashboard" },
    { to: "/snmp", label: t("nav.snmp"), icon: "snmp" },
    { to: "/jobs", label: t("nav.jobs"), icon: "jobs" },
    { to: "/system", label: t("nav.systemStatus"), icon: "system" },
    { to: "/integrations", label: t("nav.integrations"), icon: "integrations" },
    { to: "/service-catalog", label: t("nav.serviceCatalog"), icon: "serviceCatalog" },
  ];

  return (
    <nav className={styles.wrap} aria-label={t("nav.mainAria")}>
      <ul className={styles.list}>
        {mainNav.map(({ to, label, end, icon }) => (
          <li key={to} className={styles.item}>
            <NavLink
              to={to}
              end={end}
              className={({ isActive }) =>
                `${styles.link} ${isActive ? styles.active : ""}`.trim()
              }
            >
              <span className={styles.linkInner}>
                <span className={styles.navIconWrap}>
                  <SidebarNavIcon name={icon} />
                </span>
                <span>{label}</span>
              </span>
            </NavLink>
          </li>
        ))}
        <li className={styles.item}>
          <div className={styles.section}>{t("nav.ipamSection")}</div>
          <ul className={styles.sub}>
            <li>
              <NavLink
                to="/ipam/prefixes"
                className={({ isActive }) =>
                  `${styles.link} ${isActive ? styles.active : ""}`.trim()
                }
              >
                <span className={styles.linkInner}>
                  <span className={styles.navIconWrap}>
                    <SidebarNavIcon name="ipam" size={16} />
                  </span>
                  <span>{t("ipam.tabPrefixes")}</span>
                </span>
              </NavLink>
            </li>
            <li>
              <NavLink
                to="/ipam/vlans"
                className={({ isActive }) =>
                  `${styles.link} ${isActive ? styles.active : ""}`.trim()
                }
              >
                <span className={styles.linkInner}>
                  <span className={styles.navIconWrap}>
                    <SidebarNavIcon name="ipam" size={16} />
                  </span>
                  <span>{t("ipam.tabVlans")}</span>
                </span>
              </NavLink>
            </li>
            <li>
              <NavLink
                to="/ipam/vrfs"
                className={({ isActive }) =>
                  `${styles.link} ${isActive ? styles.active : ""}`.trim()
                }
              >
                <span className={styles.linkInner}>
                  <span className={styles.navIconWrap}>
                    <SidebarNavIcon name="ipam" size={16} />
                  </span>
                  <span>{t("ipam.tabVrfs")}</span>
                </span>
              </NavLink>
            </li>
            <li>
              <NavLink
                to="/ipam/circuits"
                className={({ isActive }) =>
                  `${styles.link} ${isActive ? styles.active : ""}`.trim()
                }
              >
                <span className={styles.linkInner}>
                  <span className={styles.navIconWrap}>
                    <SidebarNavIcon name="ipam" size={16} />
                  </span>
                  <span>{t("ipam.tabCircuits")}</span>
                </span>
              </NavLink>
            </li>
          </ul>
        </li>
        <li className={styles.item}>
          <div className={styles.section}>{t("nav.iamSection")}</div>
          <ul className={styles.sub}>
            <li>
              <NavLink
                to="/iam/users"
                className={({ isActive }) =>
                  `${styles.link} ${isActive ? styles.active : ""}`.trim()
                }
              >
                <span className={styles.linkInner}>
                  <span className={styles.navIconWrap}>
                    <SidebarNavIcon name="iam" size={16} />
                  </span>
                  <span>{t("nav.iamUsers")}</span>
                </span>
              </NavLink>
            </li>
            <li>
              <NavLink
                to="/iam/service-accounts"
                className={({ isActive }) =>
                  `${styles.link} ${isActive ? styles.active : ""}`.trim()
                }
              >
                <span className={styles.linkInner}>
                  <span className={styles.navIconWrap}>
                    <SidebarNavIcon name="iam" size={16} />
                  </span>
                  <span>{t("nav.iamServiceAccountsNav")}</span>
                </span>
              </NavLink>
            </li>
            <li>
              <NavLink
                to="/iam/roles"
                className={({ isActive }) =>
                  `${styles.link} ${isActive ? styles.active : ""}`.trim()
                }
              >
                <span className={styles.linkInner}>
                  <span className={styles.navIconWrap}>
                    <SidebarNavIcon name="iam" size={16} />
                  </span>
                  <span>{t("nav.iamRolesNav")}</span>
                </span>
              </NavLink>
            </li>
            <li>
              <NavLink
                to="/iam/groups"
                className={({ isActive }) =>
                  `${styles.link} ${isActive ? styles.active : ""}`.trim()
                }
              >
                <span className={styles.linkInner}>
                  <span className={styles.navIconWrap}>
                    <SidebarNavIcon name="iam" size={16} />
                  </span>
                  <span>{t("nav.iamGroupsNav")}</span>
                </span>
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
                <span className={styles.linkInner}>
                  <span className={styles.navIconWrap}>
                    <SidebarNavIcon name="dcimOverview" size={16} />
                  </span>
                  <span>{t("nav.dcimOverview")}</span>
                </span>
              </NavLink>
            </li>
            <li>
              <NavLink
                to="/dcim/sites"
                className={({ isActive }) =>
                  `${styles.link} ${isActive ? styles.active : ""}`.trim()
                }
              >
                <span className={styles.linkInner}>
                  <span className={styles.navIconWrap}>
                    <SidebarNavIcon name="dcimSites" size={16} />
                  </span>
                  <span>{t("nav.dcimSites")}</span>
                </span>
              </NavLink>
            </li>
            <li>
              <NavLink
                to="/dcim/tenants"
                className={({ isActive }) =>
                  `${styles.link} ${isActive ? styles.active : ""}`.trim()
                }
              >
                <span className={styles.linkInner}>
                  <span className={styles.navIconWrap}>
                    <SidebarNavIcon name="dcimTenants" size={16} />
                  </span>
                  <span>{t("nav.dcimTenants")}</span>
                </span>
              </NavLink>
            </li>
            <li>
              <NavLink
                to="/dcim/rooms"
                className={({ isActive }) =>
                  `${styles.link} ${isActive ? styles.active : ""}`.trim()
                }
              >
                <span className={styles.linkInner}>
                  <span className={styles.navIconWrap}>
                    <SidebarNavIcon name="dcimRooms" size={16} />
                  </span>
                  <span>{t("nav.dcimRooms")}</span>
                </span>
              </NavLink>
            </li>
            <li>
              <NavLink
                to="/dcim/racks"
                className={({ isActive }) =>
                  `${styles.link} ${isActive ? styles.active : ""}`.trim()
                }
              >
                <span className={styles.linkInner}>
                  <span className={styles.navIconWrap}>
                    <SidebarNavIcon name="dcimRacks" size={16} />
                  </span>
                  <span>{t("nav.dcimRacks")}</span>
                </span>
              </NavLink>
            </li>
            <li>
              <NavLink
                to="/dcim/equipment"
                className={({ isActive }) =>
                  `${styles.link} ${isActive ? styles.active : ""}`.trim()
                }
              >
                <span className={styles.linkInner}>
                  <span className={styles.navIconWrap}>
                    <SidebarNavIcon name="dcimEquipment" size={16} />
                  </span>
                  <span>{t("nav.dcimEquipment")}</span>
                </span>
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
                <span className={styles.linkInner}>
                  <span className={styles.navIconWrap}>
                    <SidebarNavIcon name="plugins" size={16} />
                  </span>
                  <span>{t("nav.pluginsExample")}</span>
                </span>
              </NavLink>
            </li>
          </ul>
        </li>
      </ul>
    </nav>
  );
}
