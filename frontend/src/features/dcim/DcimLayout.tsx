import { NavLink, Outlet } from "react-router-dom";
import layoutStyles from "./DcimLayout.module.css";

type DcimSubNav = { to: string; label: string; end?: boolean };

const links: DcimSubNav[] = [
  { to: "/dcim", label: "Oversikt", end: true },
  { to: "/dcim/sites", label: "Sites" },
  { to: "/dcim/rooms", label: "Rom" },
  { to: "/dcim/racks", label: "Racks" },
  { to: "/dcim/equipment", label: "Utstyr" },
];

export function DcimLayout() {
  return (
    <div>
      <nav className={layoutStyles.subnav} aria-label="DCIM">
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
