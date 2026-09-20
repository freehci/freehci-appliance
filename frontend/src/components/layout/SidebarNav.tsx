import { useEffect, useState } from "react";
import { NavLink, useLocation } from "react-router-dom";
import { useI18n } from "@/i18n/I18nProvider";
import type { MessageKey } from "@/i18n/messages/en";
import { SidebarNavIcon, type SidebarNavIconName } from "./SidebarNavIcon";
import styles from "./SidebarNav.module.css";

type DomainId = "dcim" | "network" | "platform" | "ops" | "admin";
type NavItem = {
  to: string;
  labelKey: MessageKey;
  icon: SidebarNavIconName;
  end?: boolean;
  isActive?: (pathname: string, search: string) => boolean;
};

const DOMAIN_STORAGE = "freehci.nav.domain";
const LIBRARY_TABS = new Set(["mfr", "dt", "dm", "cmp"]);

function domainForPath(pathname: string): DomainId | null {
  if (pathname.startsWith("/dcim")) return "dcim";
  if (pathname.startsWith("/ipam")) return "network";
  if (pathname.startsWith("/platform")) return "platform";
  if (
    pathname.startsWith("/jobs") ||
    pathname.startsWith("/snmp") ||
    pathname.startsWith("/ops") ||
    pathname.startsWith("/service-catalog")
  ) {
    return "ops";
  }
  if (
    pathname.startsWith("/iam") ||
    pathname.startsWith("/admin") ||
    pathname.startsWith("/system") ||
    pathname.startsWith("/integrations") ||
    pathname.startsWith("/extensions")
  ) {
    return "admin";
  }
  return null;
}

function readStoredDomain(): DomainId | null {
  try {
    const raw = localStorage.getItem(DOMAIN_STORAGE);
    if (raw === "dcim" || raw === "network" || raw === "platform" || raw === "ops" || raw === "admin") return raw;
  } catch {
    /* ignore */
  }
  return null;
}

function persistDomain(id: DomainId | null): void {
  try {
    if (id == null) localStorage.removeItem(DOMAIN_STORAGE);
    else localStorage.setItem(DOMAIN_STORAGE, id);
  } catch {
    /* ignore */
  }
}

function equipmentTab(search: string): string | null {
  return new URLSearchParams(search).get("tab");
}

function devicesActive(pathname: string, search: string): boolean {
  if (!pathname.startsWith("/dcim/equipment") && !pathname.startsWith("/dcim/models")) return false;
  if (pathname.startsWith("/dcim/models")) return false;
  const tab = equipmentTab(search);
  return tab == null || !LIBRARY_TABS.has(tab);
}

function modelsActive(pathname: string, search: string): boolean {
  if (pathname.startsWith("/dcim/models")) return true;
  if (!pathname.startsWith("/dcim/equipment")) return false;
  const tab = equipmentTab(search);
  return tab != null && LIBRARY_TABS.has(tab);
}

function ipamActive(pathname: string): boolean {
  return pathname.startsWith("/ipam/prefixes") || pathname.startsWith("/ipam/ipv6");
}

function SubLink({ item }: { item: NavItem }) {
  const { t } = useI18n();
  const location = useLocation();
  return (
    <li>
      <NavLink
        to={item.to}
        end={item.end}
        className={() => {
          const active = item.isActive
            ? item.isActive(location.pathname, location.search)
            : location.pathname === item.to || (!item.end && location.pathname.startsWith(`${item.to}/`));
          return `${styles.link} ${active ? styles.active : ""}`.trim();
        }}
      >
        <span className={styles.linkInner}>
          <span className={styles.navIconWrap}>
            <SidebarNavIcon name={item.icon} size={16} />
          </span>
          <span>{t(item.labelKey)}</span>
        </span>
      </NavLink>
    </li>
  );
}

function Domain({
  id,
  labelKey,
  open,
  onToggle,
  items,
}: {
  id: DomainId;
  labelKey: MessageKey;
  open: boolean;
  onToggle: () => void;
  items: NavItem[];
}) {
  const { t } = useI18n();
  const label = t(labelKey);
  return (
    <li className={styles.item}>
      <button
        type="button"
        className={`${styles.domainBtn} ${open ? styles.domainOpen : ""}`.trim()}
        aria-expanded={open}
        aria-controls={`nav-domain-${id}`}
        aria-label={open ? t("nav.collapseDomain", { name: label }) : t("nav.expandDomain", { name: label })}
        onClick={onToggle}
      >
        <span>{label}</span>
        <span className={styles.chevron} aria-hidden>
          {open ? "▾" : "▸"}
        </span>
      </button>
      {open ? (
        <ul id={`nav-domain-${id}`} className={styles.sub}>
          {items.map((item) => (
            <SubLink key={item.to} item={item} />
          ))}
        </ul>
      ) : null}
    </li>
  );
}

export function SidebarNav() {
  const { t } = useI18n();
  const location = useLocation();
  const [openDomain, setOpenDomain] = useState<DomainId | null>(() => domainForPath(location.pathname) ?? readStoredDomain());

  useEffect(() => {
    const next = domainForPath(location.pathname);
    if (next == null) return;
    setOpenDomain(next);
    persistDomain(next);
  }, [location.pathname]);

  const toggle = (id: DomainId) => {
    setOpenDomain((cur) => {
      const next = cur === id ? null : id;
      persistDomain(next);
      return next;
    });
  };

  return (
    <nav className={styles.wrap} aria-label={t("nav.mainAria")}>
      <ul className={styles.list}>
        <li className={styles.item}>
          <NavLink
            to="/"
            end
            className={({ isActive }) => `${styles.link} ${isActive ? styles.active : ""}`.trim()}
          >
            <span className={styles.linkInner}>
              <span className={styles.navIconWrap}>
                <SidebarNavIcon name="dashboard" />
              </span>
              <span>{t("nav.dashboard")}</span>
            </span>
          </NavLink>
        </li>
        <Domain
          id="dcim"
          labelKey="nav.domainDcim"
          open={openDomain === "dcim"}
          onToggle={() => toggle("dcim")}
          items={[
            {
              to: "/dcim/locations",
              labelKey: "nav.locations",
              icon: "locations",
              isActive: (p) =>
                p.startsWith("/dcim/locations") || p.startsWith("/dcim/sites") || /^\/dcim\/rooms(\/|$)/.test(p),
            },
            { to: "/dcim/racks", labelKey: "nav.dcimRacks", icon: "dcimRacks" },
            { to: "/dcim/equipment", labelKey: "nav.devices", icon: "devices", isActive: devicesActive },
            { to: "/dcim/models", labelKey: "nav.modelLibrary", icon: "models", isActive: modelsActive },
          ]}
        />
        <Domain
          id="network"
          labelKey="nav.domainNetwork"
          open={openDomain === "network"}
          onToggle={() => toggle("network")}
          items={[
            { to: "/ipam/prefixes", labelKey: "nav.ipam", icon: "ipam", isActive: (p) => ipamActive(p) },
            { to: "/ipam/vlans", labelKey: "nav.segments", icon: "ipam" },
            { to: "/ipam/vrfs", labelKey: "nav.routing", icon: "ipam" },
            { to: "/ipam/circuits", labelKey: "nav.circuits", icon: "ipam" },
          ]}
        />
        <Domain
          id="platform"
          labelKey="nav.domainPlatform"
          open={openDomain === "platform"}
          onToggle={() => toggle("platform")}
          items={[{ to: "/platform/clusters", labelKey: "nav.clusters", icon: "clusters" }]}
        />
        <Domain
          id="ops"
          labelKey="nav.domainOps"
          open={openDomain === "ops"}
          onToggle={() => toggle("ops")}
          items={[
            { to: "/jobs/templates", labelKey: "nav.discovery", icon: "discovery" },
            {
              to: "/jobs",
              labelKey: "nav.jobs",
              icon: "jobs",
              isActive: (p) => p === "/jobs" || p.startsWith("/jobs/scheduler"),
            },
            { to: "/snmp", labelKey: "nav.snmp", icon: "snmp" },
            { to: "/service-catalog", labelKey: "nav.serviceCatalog", icon: "serviceCatalog" },
          ]}
        />
        <Domain
          id="admin"
          labelKey="nav.domainAdmin"
          open={openDomain === "admin"}
          onToggle={() => toggle("admin")}
          items={[
            { to: "/iam/users", labelKey: "nav.access", icon: "access", isActive: (p) => p.startsWith("/iam") },
            { to: "/admin/organizations", labelKey: "nav.organizations", icon: "orgs" },
            { to: "/system", labelKey: "nav.systemStatus", icon: "system" },
            { to: "/integrations", labelKey: "nav.integrations", icon: "integrations" },
            { to: "/extensions", labelKey: "nav.extensions", icon: "extensions" },
          ]}
        />
      </ul>
    </nav>
  );
}
