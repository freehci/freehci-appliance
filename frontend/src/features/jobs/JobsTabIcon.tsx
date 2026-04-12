import type { ReactNode } from "react";

export type JobsInnerTabIcon = "jobs" | "scheduler" | "templates";

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

/** Ikoner for Jobber-underfaner (samme stil som SnmpTabIcon). */
export function JobsTabIcon({ name }: { name: JobsInnerTabIcon }) {
  switch (name) {
    case "jobs":
      return (
        <Svg>
          <path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z" />
          <path d="M13 2v7h7" />
          <path d="M8 13h8" />
          <path d="M8 17h5" />
        </Svg>
      );
    case "scheduler":
      return (
        <Svg>
          <circle cx="12" cy="12" r="10" />
          <path d="M12 6v6l4 2" />
        </Svg>
      );
    case "templates":
      return (
        <Svg>
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
          <path d="M14 2v6h6" />
          <path d="M10 12h4" />
          <path d="M10 16h7" />
        </Svg>
      );
  }
}
