import type { ReactNode } from "react";

/** Ikoner for hoved- og undermeny (strokelinjer, følger currentColor). */
export type SidebarNavIconName =
  | "dashboard"
  | "ipam"
  | "snmp"
  | "jobs"
  | "integrations"
  | "serviceCatalog"
  | "iam"
  | "dcimOverview"
  | "dcimSites"
  | "dcimRooms"
  | "dcimRacks"
  | "dcimEquipment"
  | "plugins";

function Svg({ size, children }: { size: 16 | 18; children: ReactNode }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={1.75}
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden
    >
      {children}
    </svg>
  );
}

export function SidebarNavIcon({ name, size = 18 }: { name: SidebarNavIconName; size?: 16 | 18 }) {
  const S = ({ children }: { children: ReactNode }) => <Svg size={size}>{children}</Svg>;
  switch (name) {
    case "dashboard":
      return (
        <S>
          <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
          <polyline points="9 22 9 12 15 12 15 22" />
        </S>
      );
    case "ipam":
      return (
        <S>
          <rect x="2" y="2" width="20" height="8" rx="2" />
          <rect x="2" y="14" width="20" height="8" rx="2" />
          <line x1="6" y1="6" x2="6.01" y2="6" />
          <line x1="6" y1="18" x2="6.01" y2="18" />
        </S>
      );
    case "snmp":
      return (
        <S>
          <path d="M5 12.55a11 11 0 0 1 14.08 0" />
          <path d="M1.42 9a16 16 0 0 1 21.16 0" />
          <path d="M8.53 16.11a6 6 0 0 1 6.95 0" />
          <line x1="12" y1="20" x2="12.01" y2="20" />
        </S>
      );
    case "jobs":
      return (
        <S>
          <rect x="2" y="7" width="20" height="14" rx="2" />
          <path d="M16 7V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v2" />
          <line x1="8" y1="12" x2="16" y2="12" />
        </S>
      );
    case "integrations":
      return (
        <S>
          <path d="M12 22v-6" />
          <path d="M9 12V8a3 3 0 0 1 6 0v4" />
          <rect x="5" y="12" width="14" height="6" rx="1" />
        </S>
      );
    case "serviceCatalog":
      return (
        <S>
          <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" />
          <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z" />
          <line x1="8" y1="7" x2="16" y2="7" />
          <line x1="8" y1="11" x2="14" y2="11" />
        </S>
      );
    case "iam":
      return (
        <S>
          <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10" />
          <circle cx="12" cy="11" r="2" />
        </S>
      );
    case "dcimOverview":
      return (
        <S>
          <rect x="3" y="3" width="7" height="9" rx="1" />
          <rect x="14" y="3" width="7" height="5" rx="1" />
          <rect x="14" y="12" width="7" height="9" rx="1" />
          <rect x="3" y="16" width="7" height="5" rx="1" />
        </S>
      );
    case "dcimSites":
      return (
        <S>
          <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" />
          <circle cx="12" cy="10" r="3" />
        </S>
      );
    case "dcimRooms":
      return (
        <S>
          <path d="M3 21h18" />
          <path d="M5 21V7l8-4v18" />
          <path d="M19 21V11l-6-4" />
        </S>
      );
    case "dcimRacks":
      return (
        <S>
          <rect x="4" y="4" width="16" height="16" rx="1" />
          <line x1="9" y1="4" x2="9" y2="20" />
          <line x1="15" y1="4" x2="15" y2="20" />
        </S>
      );
    case "dcimEquipment":
      return (
        <S>
          <rect x="4" y="4" width="16" height="16" rx="2" />
          <rect x="9" y="9" width="6" height="6" />
          <line x1="9" y1="2" x2="9" y2="4" />
          <line x1="15" y1="2" x2="15" y2="4" />
        </S>
      );
    case "plugins":
      return (
        <S>
          <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z" />
          <polyline points="3.27 6.96 12 12.01 20.73 6.96" />
          <line x1="12" y1="22.08" x2="12" y2="12" />
        </S>
      );
  }
}
