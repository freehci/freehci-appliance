import type { ReactNode } from "react";

export type IamUserTabIconName =
  | "user"
  | "loginDevices"
  | "groups"
  | "roles"
  | "applications"
  | "company"
  | "log";

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

export function IamUserTabIcon({ name }: { name: IamUserTabIconName }) {
  switch (name) {
    case "user":
      return (
        <Svg>
          <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
          <circle cx="12" cy="7" r="4" />
        </Svg>
      );
    case "loginDevices":
      return (
        <Svg>
          <rect x="5" y="2" width="14" height="20" rx="2" />
          <line x1="12" y1="18" x2="12.01" y2="18" />
        </Svg>
      );
    case "groups":
      return (
        <Svg>
          <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
          <circle cx="9" cy="7" r="4" />
          <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
          <path d="M16 3.13a4 4 0 0 1 0 7.75" />
        </Svg>
      );
    case "roles":
      return (
        <Svg>
          <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10" />
        </Svg>
      );
    case "applications":
      return (
        <Svg>
          <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z" />
          <polyline points="3.27 6.96 12 12.01 20.73 6.96" />
          <line x1="12" y1="22.08" x2="12" y2="12" />
        </Svg>
      );
    case "company":
      return (
        <Svg>
          <path d="M3 21h18" />
          <path d="M5 21V7l8-4v18" />
          <path d="M19 21V11l-6-4" />
          <path d="M9 9h1" />
          <path d="M9 13h1" />
          <path d="M9 17h1" />
        </Svg>
      );
    case "log":
      return (
        <Svg>
          <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" />
          <path d="M3 3v5h5" />
          <path d="M12 7v6l4 2" />
        </Svg>
      );
  }
}
