import { useId, useState } from "react";
import type { MessageKey } from "@/i18n/messages/en";
import { MibCompileMessage } from "./MibCompileMessage";
import {
  mibCompileErrorHintsForExpanded,
  mibCompileErrorNeedsToggle,
  mibCompileErrorPreview,
} from "./compileErrorHints";
import mibsTableStyles from "./snmpMibs.module.css";
import type { SnmpMibDetail } from "./snmpApi";

type TFn = (key: MessageKey, vars?: Record<string, string>) => string;

export function MibCompileErrorBlock({
  raw,
  rows,
  t,
  onMibRefNavigate,
}: {
  raw: string;
  rows: SnmpMibDetail[];
  t: TFn;
  onMibRefNavigate: (filename: string) => void;
}) {
  const panelId = useId();
  const [open, setOpen] = useState(false);
  const needsToggle = mibCompileErrorNeedsToggle(raw);
  const preview = mibCompileErrorPreview(raw);
  const hintKeys = mibCompileErrorHintsForExpanded(raw);

  if (!needsToggle) {
    return (
      <div className={mibsTableStyles.compileErrorWrap}>
        <MibCompileMessage raw={raw} rows={rows} t={t} onMibRefNavigate={onMibRefNavigate} />
      </div>
    );
  }

  return (
    <div className={mibsTableStyles.compileErrorWrap}>
      <div
        id={panelId}
        className={open ? mibsTableStyles.compileErrorExpanded : mibsTableStyles.compileErrorPreview}
        title={open ? undefined : raw}
      >
        {open ? (
          <>
            <MibCompileMessage raw={raw} rows={rows} t={t} onMibRefNavigate={onMibRefNavigate} />
            <div className={mibsTableStyles.compileHints} role="note">
              <strong className={mibsTableStyles.compileHintsTitle}>{t("snmp.compileErrorHintsTitle")}</strong>
              <ul className={mibsTableStyles.compileHintsList}>
                {hintKeys.map((k) => (
                  <li key={k}>{t(k)}</li>
                ))}
              </ul>
            </div>
          </>
        ) : (
          preview
        )}
      </div>
      <button
        type="button"
        className={mibsTableStyles.compileErrorToggle}
        aria-expanded={open}
        aria-controls={panelId}
        onClick={() => setOpen((v) => !v)}
      >
        {open ? t("snmp.compileErrorLess") : t("snmp.compileErrorMore")}
      </button>
    </div>
  );
}
