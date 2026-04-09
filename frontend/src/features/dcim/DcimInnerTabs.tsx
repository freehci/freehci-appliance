import type { DcimInnerTabIcon } from "./DcimTabIcon";
import { DcimTabIcon } from "./DcimTabIcon";
import styles from "./DcimInnerTabs.module.css";

export type DcimInnerTabDef = { id: string; label: string; icon?: DcimInnerTabIcon };

export type { DcimInnerTabIcon };

export function DcimInnerTabs({
  tabs,
  activeId,
  onChange,
  ariaLabel,
}: {
  tabs: DcimInnerTabDef[];
  activeId: string;
  onChange: (id: string) => void;
  ariaLabel: string;
}) {
  return (
    <nav className={styles.wrap} aria-label={ariaLabel}>
      <div className={styles.list} role="tablist">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            type="button"
            role="tab"
            aria-selected={activeId === tab.id}
            className={`${styles.tab} ${activeId === tab.id ? styles.tabActive : ""}`.trim()}
            onClick={() => onChange(tab.id)}
          >
            {tab.icon ? (
              <span className={styles.iconWrap}>
                <DcimTabIcon name={tab.icon} />
              </span>
            ) : null}
            <span>{tab.label}</span>
          </button>
        ))}
      </div>
    </nav>
  );
}
