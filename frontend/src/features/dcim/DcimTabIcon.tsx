import type { ReactNode } from "react";

/** Kjente ikoner for DCIM-innfaner (strokelinjer, følger currentColor). */
export type DcimInnerTabIcon =
  | "overview"
  | "sites"
  | "rooms"
  | "floorplan"
  | "rackElevation"
  | "rackAdmin"
  | "manufacturers"
  | "deviceTypes"
  | "deviceModels"
  | "devices"
  | "placements"
  | "deviceNetwork"
  | "deviceHardware"
  | "deviceOs"
  | "accessSurveillance"
  | "powerCooling"
  | "fireSafety";

function Svg({ children }: { children: ReactNode }) {
  return (
    <svg
      width={16}
      height={16}
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

export function DcimTabIcon({ name }: { name: DcimInnerTabIcon }) {
  switch (name) {
    case "overview":
      return (
        <Svg>
          <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
          <polyline points="9 22 9 12 15 12 15 22" />
        </Svg>
      );
    case "sites":
      return (
        <Svg>
          <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" />
          <circle cx="12" cy="10" r="3" />
        </Svg>
      );
    case "rooms":
      return (
        <Svg>
          <path d="M3 21h18" />
          <path d="M5 21V7l8-4v18" />
          <path d="M19 21V11l-6-4" />
        </Svg>
      );
    case "floorplan":
      return (
        <Svg>
          <rect x="3" y="3" width="18" height="18" rx="1" />
          <path d="M3 9h18M9 3v18M15 9v12" />
        </Svg>
      );
    case "rackElevation":
      return (
        <Svg>
          <rect x="4" y="4" width="16" height="16" rx="1" />
          <line x1="9" y1="4" x2="9" y2="20" />
          <line x1="15" y1="4" x2="15" y2="20" />
          <line x1="4" y1="12" x2="20" y2="12" />
        </Svg>
      );
    case "rackAdmin":
      return (
        <Svg>
          <path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2" />
          <rect x="8" y="2" width="8" height="4" rx="1" />
          <line x1="8" y1="12" x2="16" y2="12" />
          <line x1="8" y1="16" x2="16" y2="16" />
        </Svg>
      );
    case "manufacturers":
      return (
        <Svg>
          <path d="M2 20h20" />
          <path d="M4 20V10l8-4v14" />
          <path d="M12 20V6l8 4v10" />
          <path d="M8 10h4" />
          <path d="M16 14h2" />
        </Svg>
      );
    case "deviceTypes":
      return (
        <Svg>
          <polygon points="12 2 2 7 12 12 22 7 12 2" />
          <polyline points="2 17 12 22 22 17" />
          <polyline points="2 12 12 17 22 12" />
        </Svg>
      );
    case "deviceModels":
      return (
        <Svg>
          <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z" />
          <polyline points="3.27 6.96 12 12.01 20.73 6.96" />
          <line x1="12" y1="22.08" x2="12" y2="12" />
        </Svg>
      );
    case "devices":
      return (
        <Svg>
          <rect x="4" y="4" width="16" height="16" rx="2" />
          <rect x="9" y="9" width="6" height="6" />
          <line x1="9" y1="2" x2="9" y2="4" />
          <line x1="15" y1="2" x2="15" y2="4" />
          <line x1="9" y1="20" x2="9" y2="22" />
          <line x1="15" y1="20" x2="15" y2="22" />
        </Svg>
      );
    case "placements":
      return (
        <Svg>
          <rect x="3" y="3" width="7" height="7" rx="1" />
          <rect x="14" y="3" width="7" height="7" rx="1" />
          <rect x="3" y="14" width="7" height="7" rx="1" />
          <rect x="14" y="14" width="7" height="7" rx="1" />
        </Svg>
      );
    case "deviceNetwork":
      return (
        <Svg>
          <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10" />
          <path d="M8 12h8" />
        </Svg>
      );
    case "deviceHardware":
      return (
        <Svg>
          <rect x="4" y="4" width="16" height="16" rx="2" />
          <rect x="9" y="9" width="6" height="6" />
          <line x1="9" y1="2" x2="9" y2="4" />
          <line x1="15" y1="2" x2="15" y2="4" />
          <line x1="9" y1="20" x2="9" y2="22" />
          <line x1="15" y1="20" x2="15" y2="22" />
          <line x1="2" y1="9" x2="4" y2="9" />
          <line x1="2" y1="15" x2="4" y2="15" />
          <line x1="20" y1="9" x2="22" y2="9" />
          <line x1="20" y1="15" x2="22" y2="15" />
        </Svg>
      );
    case "deviceOs":
      return (
        <Svg>
          <rect x="2" y="3" width="20" height="14" rx="2" />
          <line x1="8" y1="21" x2="16" y2="21" />
          <line x1="12" y1="17" x2="12" y2="21" />
        </Svg>
      );
    case "accessSurveillance":
      return (
        <Svg>
          <path d="M3 21h18M5 21V8a2 2 0 012-2h10a2 2 0 012 2v13" />
          <circle cx="12" cy="14" r="1.75" />
          <path d="M17 8h.01" />
          <rect x="15" y="4" width="6" height="4" rx="1" />
          <path d="M17 6h2" />
        </Svg>
      );
    case "powerCooling":
      return (
        <Svg>
          <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z" />
        </Svg>
      );
    case "fireSafety":
      return (
        <Svg>
          <path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.72-2.42 1.4-4 1.4-4S8 4 8 8c0 2 0 3.5-2 4.5" />
          <path d="M12 22c-4.97 0-9-2.69-9-6 0-2.09 1.5-4 4-5" />
        </Svg>
      );
  }
}
