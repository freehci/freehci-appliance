import type { ReactNode } from "react";

/** Ikoner for IAM-faner (strokelinjer, følger currentColor). */
export type IamTabIconName = "persons" | "serviceAccounts" | "roles" | "groups";

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

export function IamTabIcon({ name }: { name: IamTabIconName }) {
  switch (name) {
    case "persons":
      return (
        <Svg>
          <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
          <circle cx="12" cy="7" r="4" />
        </Svg>
      );
    case "serviceAccounts":
      return (
        <Svg>
          <circle cx="9" cy="7" r="3" />
          <path d="M4 19.5A3.5 3.5 0 0 1 7.5 16h3" />
          <circle cx="17" cy="17" r="2" />
          <path d="M17 14.5V12.5M17 21.5V19.5M14.5 17H12.5M21.5 17H19.5" />
        </Svg>
      );
    case "roles":
      return (
        <Svg>
          <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10" />
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
  }
}
