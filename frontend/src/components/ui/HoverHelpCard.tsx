import { useId, type ReactNode } from "react";
import styles from "./HoverHelpCard.module.css";

export type HoverHelpCardProps = {
  /** Screen reader label for the help icon button. */
  ariaLabel: string;
  children: ReactNode;
};

export function HoverHelpCard({ ariaLabel, children }: HoverHelpCardProps) {
  const tipId = useId();
  return (
    <span className={styles.wrap}>
      <button
        type="button"
        className={styles.trigger}
        aria-label={ariaLabel}
        aria-describedby={tipId}
      >
        <i className="fas fa-circle-question" aria-hidden />
      </button>
      <div className={styles.card} id={tipId} role="tooltip">
        <div className={styles.cardInner}>{children}</div>
      </div>
    </span>
  );
}
