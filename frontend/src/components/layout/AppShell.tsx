import type { ReactNode } from "react";
import { SidebarNav } from "./SidebarNav";
import { TopHeader } from "./TopHeader";
import styles from "./AppShell.module.css";

export function AppShell({ children }: { children: ReactNode }) {
  return (
    <div className={styles.shell}>
      <TopHeader />
      <div className={styles.grid}>
        <SidebarNav />
        <main className={styles.main}>{children}</main>
      </div>
    </div>
  );
}
