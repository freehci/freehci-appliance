import { useEffect, useState } from "react";
import { useI18n } from "@/i18n/I18nProvider";
import dcimStyles from "../dcim.module.css";
import demoStyles from "./roomDemo.module.css";

export function RoomFireSafetySection({ roomId }: { roomId: number }) {
  const { t } = useI18n();
  const [pressurePct, setPressurePct] = useState(72);

  useEffect(() => {
    const id = window.setInterval(() => {
      const tt = Date.now() / 2400 + roomId * 0.31;
      setPressurePct(68 + Math.sin(tt) * 14 + Math.cos(tt * 0.7) * 4);
    }, 700);
    return () => window.clearInterval(id);
  }, [roomId]);

  const bar = Math.min(100, Math.max(8, pressurePct));

  return (
    <section className={dcimStyles.mfrDetailSection}>
      <h3 className={dcimStyles.mfrDetailSectionTitle}>{t("dcim.rooms.fireTabTitle")}</h3>
      <p className={demoStyles.demoNotice}>{t("dcim.rooms.demoPluginNotice")}</p>
      <p className={demoStyles.demoMuted}>{t("dcim.rooms.fireTabIntro")}</p>

      <div className={demoStyles.fireGrid} style={{ marginTop: "var(--space-3)" }}>
        <div className={demoStyles.demoCard}>
          <p className={demoStyles.demoCardTitle}>{t("dcim.rooms.fireStatusTitle")}</p>
          <div className={demoStyles.fireRow}>
            <span>{t("dcim.rooms.fireRowDetector")}</span>
            <span className={demoStyles.fireBadge}>{t("dcim.rooms.fireStatusOk")}</span>
          </div>
          <div className={demoStyles.fireRow} style={{ marginTop: "var(--space-2)" }}>
            <span>{t("dcim.rooms.fireRowAlarm")}</span>
            <span className={demoStyles.fireBadge}>{t("dcim.rooms.fireStatusOk")}</span>
          </div>
          <div className={demoStyles.fireRow} style={{ marginTop: "var(--space-2)" }}>
            <span>{t("dcim.rooms.fireRowSuppression")}</span>
            <span className={demoStyles.fireBadge}>{t("dcim.rooms.fireStatusArmed")}</span>
          </div>
        </div>

        <div className={demoStyles.demoCard}>
          <p className={demoStyles.demoCardTitle}>{t("dcim.rooms.firePressureTitle")}</p>
          <p className={demoStyles.demoMuted}>{t("dcim.rooms.firePressureHint")}</p>
          <div className={demoStyles.fireRow} style={{ marginTop: "var(--space-2)" }}>
            <span>{t("dcim.rooms.fireTankLabel")}</span>
            <span className={demoStyles.tempVal} style={{ color: "var(--color-text)" }}>
              {(42 + bar * 0.06).toFixed(1)} bar
            </span>
          </div>
          <div className={demoStyles.pressureBar} aria-hidden>
            <div className={demoStyles.pressureFill} style={{ width: `${bar}%` }} />
          </div>
          <p className={demoStyles.demoMuted} style={{ marginTop: "var(--space-2)", marginBottom: 0 }}>
            {t("dcim.rooms.fireFootnote")}
          </p>
        </div>
      </div>
    </section>
  );
}
