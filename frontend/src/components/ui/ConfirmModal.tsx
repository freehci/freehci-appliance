import { useEffect, useId, type ReactNode } from "react";
import dcimStyles from "@/features/dcim/dcim.module.css";

export type ConfirmModalProps = {
  open: boolean;
  onClose: () => void;
  title: ReactNode;
  message?: ReactNode;
  confirmLabel: string;
  cancelLabel: string;
  onConfirm: () => void;
  danger?: boolean;
  pending?: boolean;
};

export function ConfirmModal({
  open,
  onClose,
  title,
  message,
  confirmLabel,
  cancelLabel,
  onConfirm,
  danger = false,
  pending = false,
}: ConfirmModalProps) {
  const titleId = useId();
  const descId = useId();

  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  if (!open) return null;

  const confirmClass = danger ? dcimStyles.btnDanger : dcimStyles.btn;

  return (
    <div
      role="presentation"
      style={{
        position: "fixed",
        inset: 0,
        zIndex: 200,
        background: "rgba(0,0,0,0.45)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: "var(--space-3)",
      }}
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
        {...(message != null ? { "aria-describedby": descId } : {})}
        style={{
          width: "min(28rem, 100%)",
          maxHeight: "90vh",
          overflow: "auto",
          background: "var(--color-bg-elevated)",
          border: "1px solid var(--shell-border)",
          borderRadius: "var(--radius-md)",
          padding: "var(--space-4)",
          boxShadow: "0 8px 32px rgba(0,0,0,0.2)",
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <h2 id={titleId} style={{ marginTop: 0 }}>
          {title}
        </h2>
        {message != null ? (
          <div id={descId} className={dcimStyles.muted} style={{ marginTop: 0 }}>
            {message}
          </div>
        ) : null}
        <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem", marginTop: "var(--space-3)" }}>
          <button type="button" className={confirmClass} disabled={pending} onClick={() => onConfirm()}>
            {pending ? "…" : confirmLabel}
          </button>
          <button type="button" className={dcimStyles.btnMuted} onClick={onClose} disabled={pending}>
            {cancelLabel}
          </button>
        </div>
      </div>
    </div>
  );
}
