import { NavLink } from "react-router-dom";
import styles from "./SidebarNav.module.css";

const mainNav = [
  { to: "/", label: "Dashboard", end: true },
  { to: "/ipam", label: "IPAM" },
  { to: "/jobs", label: "Jobs" },
  { to: "/integrations", label: "Integrasjoner" },
  { to: "/service-catalog", label: "Servicekatalog" },
];

export function SidebarNav() {
  return (
    <nav className={styles.wrap} aria-label="Hovedmeny">
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
          <div className={styles.section}>DCIM</div>
          <ul className={styles.sub}>
            <li>
              <NavLink
                to="/dcim"
                end
                className={({ isActive }) =>
                  `${styles.link} ${isActive ? styles.active : ""}`.trim()
                }
              >
                Oversikt
              </NavLink>
            </li>
            <li>
              <NavLink
                to="/dcim/sites"
                className={({ isActive }) =>
                  `${styles.link} ${isActive ? styles.active : ""}`.trim()
                }
              >
                Sites
              </NavLink>
            </li>
            <li>
              <NavLink
                to="/dcim/rooms"
                className={({ isActive }) =>
                  `${styles.link} ${isActive ? styles.active : ""}`.trim()
                }
              >
                Rom
              </NavLink>
            </li>
            <li>
              <NavLink
                to="/dcim/racks"
                className={({ isActive }) =>
                  `${styles.link} ${isActive ? styles.active : ""}`.trim()
                }
              >
                Racks
              </NavLink>
            </li>
            <li>
              <NavLink
                to="/dcim/equipment"
                className={({ isActive }) =>
                  `${styles.link} ${isActive ? styles.active : ""}`.trim()
                }
              >
                Utstyr
              </NavLink>
            </li>
          </ul>
        </li>
        <li className={styles.item}>
          <div className={styles.section}>Plugins</div>
          <ul className={styles.sub}>
            <li>
              <NavLink
                to="/plugins/freehci.example"
                className={({ isActive }) =>
                  `${styles.link} ${isActive ? styles.active : ""}`.trim()
                }
              >
                Eksempel-plugin
              </NavLink>
            </li>
          </ul>
        </li>
      </ul>
    </nav>
  );
}
