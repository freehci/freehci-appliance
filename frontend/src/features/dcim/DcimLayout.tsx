import { NavLink, Outlet } from "react-router-dom";
import { useI18n } from "@/i18n/I18nProvider";
import layoutStyles from "./DcimLayout.module.css";

type SubNav = { to: string; label: string; end?: boolean };

export function DcimLayout() {
  const { t } = useI18n();

  const links: SubNav[] = [
    { to: "/dcim", label: t("nav.dcimOverview"), end: true },
    { to: "/dcim/sites", label: t("nav.dcimSites") },
    { to: "/dcim/rooms", label: t("nav.dcimRooms") },
    { to: "/dcim/racks", label: t("nav.dcimRacks") },
    { to: "/dcim/equipment", label: t("nav.dcimEquipment") },
  ];

  return (
    <div>
      <nav className={layoutStyles.subnav} aria-label={t("nav.dcimSection")}>
        {links.map(({ to, label, end }) => (
          <NavLink
            key={to}
            to={to}
            end={Boolean(end)}
            className={({ isActive }) =>
              [layoutStyles.subLink, isActive ? layoutStyles.subLinkActive : ""].join(" ").trim()
            }
          >
            {label}
          </NavLink>
        ))}
      </nav>
      <Outlet />
    </div>
  );
}
