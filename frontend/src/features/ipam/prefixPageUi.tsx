import { useEffect, useRef, type ReactNode } from "react";
import type { Ipv4Prefix } from "./types";
import styles from "./prefixPage.module.css";

export function prefixUsage(p: Ipv4Prefix): { used: number; total: number; pct: number } {
  const used = p.used_count ?? 0;
  const total = p.usable_hosts && p.usable_hosts > 0 ? p.usable_hosts : p.address_total;
  const raw = p.utilization;
  const pct =
    raw != null ? (raw <= 1 ? raw * 100 : raw) : total > 0 ? (100 * used) / total : 0;
  return { used, total, pct };
}

export function UtilizationBar({ used, total, pct }: { used: number; total: number; pct: number }) {
  const fill =
    pct >= 85 ? styles.barHigh : pct >= 60 ? styles.barWarn : pct >= 20 ? styles.barMid : styles.barLow;
  const width = Math.max(0, Math.min(100, pct));
  return (
    <div className={styles.usage}>
      <span className={styles.usageNums}>
        {used} / {total}
        <span style={{ opacity: 0.7 }}> ({Math.round(pct)}%)</span>
      </span>
      <div className={styles.bar} aria-hidden>
        <div className={`${styles.barFill} ${fill}`} style={{ width: `${width}%` }} />
      </div>
    </div>
  );
}

export function PrefixRoleBadge({ role }: { role: string }) {
  const r = role || "active";
  const cls =
    r === "active"
      ? styles.pillActive
      : r === "container"
        ? styles.pillContainer
        : r === "reserved"
          ? styles.pillReserved
          : r === "overlay-pod" || r === "overlay-service" || r === "lb-pool"
            ? styles.pillOverlay
            : r === "p2p"
              ? styles.pillPlanned
              : styles.pill;
  return <span className={`${styles.pill} ${cls}`}>{r}</span>;
}

export function PrefixStatusBadge({ status }: { status: string }) {
  const s = status || "active";
  const cls =
    s === "active"
      ? styles.pillActive
      : s === "planned"
        ? styles.pillPlanned
        : s === "reserved"
          ? styles.pillReserved
          : s === "deprecated"
            ? styles.pillWarn
            : styles.pill;
  return <span className={`${styles.pill} ${cls}`}>{s}</span>;
}

export function PrefixDrawer({
  title,
  open,
  onClose,
  children,
  footer,
}: {
  title: string;
  open: boolean;
  onClose: () => void;
  children: ReactNode;
  footer?: ReactNode;
}) {
  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, onClose]);
  if (!open) return null;
  return (
    <>
      <div className={styles.drawerBackdrop} onClick={onClose} role="presentation" />
      <aside className={styles.drawer} role="dialog" aria-modal="true" aria-label={title}>
        <div className={styles.drawerHead}>
          <h2 className={styles.drawerTitle}>{title}</h2>
          <button type="button" className={styles.treeToggle} onClick={onClose} aria-label={title}>
            <i className="fas fa-xmark" aria-hidden />
          </button>
        </div>
        <div className={styles.drawerBody}>{children}</div>
        {footer ? <div className={styles.drawerFoot}>{footer}</div> : null}
      </aside>
    </>
  );
}

export function RowOverflowMenu({
  open,
  onOpen,
  onClose,
  label,
  children,
}: {
  open: boolean;
  onOpen: () => void;
  onClose: () => void;
  label?: string;
  children: ReactNode;
}) {
  const ref = useRef<HTMLDivElement | null>(null);
  useEffect(() => {
    if (!open) return;
    const onDown = (e: MouseEvent) => {
      if (ref.current && e.target instanceof Node && !ref.current.contains(e.target)) onClose();
    };
    document.addEventListener("mousedown", onDown);
    return () => document.removeEventListener("mousedown", onDown);
  }, [open, onClose]);
  return (
    <div className={styles.menuWrap} ref={ref}>
      <button
        type="button"
        className={styles.treeToggle}
        aria-label={label}
        aria-expanded={open}
        aria-haspopup="menu"
        onClick={(e) => {
          e.stopPropagation();
          if (open) onClose();
          else onOpen();
        }}
      >
        <i className="fas fa-ellipsis" aria-hidden />
      </button>
      {open ? (
        <div className={styles.menuPop} role="menu" onClick={(e) => e.stopPropagation()}>
          {children}
        </div>
      ) : null}
    </div>
  );
}

export function SummaryCards({
  total,
  active,
  container,
  reserved,
  labels,
}: {
  total: number;
  active: number;
  container: number;
  reserved: number;
  labels: { total: string; active: string; container: string; reserved: string };
}) {
  const pct = (n: number) => (total > 0 ? `${Math.round((100 * n) / total)}%` : "—");
  const items = [
    { icon: "fa-layer-group", label: labels.total, value: total, meta: null as string | null },
    { icon: "fa-diagram-project", label: labels.active, value: active, meta: pct(active) },
    { icon: "fa-cube", label: labels.container, value: container, meta: pct(container) },
    { icon: "fa-bookmark", label: labels.reserved, value: reserved, meta: pct(reserved) },
  ];
  return (
    <div className={styles.cards}>
      {items.map((it) => (
        <div key={it.label} className={styles.card}>
          <span className={styles.cardIcon}>
            <i className={`fas ${it.icon}`} aria-hidden />
          </span>
          <div>
            <p className={styles.cardLabel}>{it.label}</p>
            <p className={styles.cardValue}>{it.value}</p>
            {it.meta ? <p className={styles.cardMeta}>{it.meta}</p> : null}
          </div>
        </div>
      ))}
    </div>
  );
}
