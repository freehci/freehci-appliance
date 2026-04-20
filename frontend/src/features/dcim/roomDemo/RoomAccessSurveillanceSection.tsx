import { useI18n } from "@/i18n/I18nProvider";
import dcimStyles from "../dcim.module.css";
import demoStyles from "./roomDemo.module.css";

const READER_IDS = ["A-DIN-01", "A-DIN-02", "B-LOK-03"];
const CAM_KEYS = ["dcim.rooms.demoCam1", "dcim.rooms.demoCam2", "dcim.rooms.demoCam3", "dcim.rooms.demoCam4", "dcim.rooms.demoCam5", "dcim.rooms.demoCam6"] as const;

export function RoomAccessSurveillanceSection() {
  const { t } = useI18n();

  return (
    <section className={dcimStyles.mfrDetailSection}>
      <h3 className={dcimStyles.mfrDetailSectionTitle}>{t("dcim.rooms.accessTabTitle")}</h3>
      <p className={demoStyles.demoNotice}>{t("dcim.rooms.demoPluginNotice")}</p>
      <p className={demoStyles.demoMuted}>{t("dcim.rooms.accessTabIntro")}</p>

      <div className={demoStyles.accessSplit} style={{ marginTop: "var(--space-3)" }}>
        <div className={demoStyles.demoCard}>
          <p className={demoStyles.demoCardTitle}>{t("dcim.rooms.accessReadersTitle")}</p>
          <p className={demoStyles.demoMuted}>{t("dcim.rooms.accessReadersHint")}</p>
          <ul className={demoStyles.demoList}>
            {READER_IDS.map((id) => (
              <li key={id}>
                {t("dcim.rooms.accessReaderItem", { id })}
              </li>
            ))}
          </ul>
          <p className={demoStyles.demoMuted} style={{ marginTop: "var(--space-2)", marginBottom: 0 }}>
            {t("dcim.rooms.accessVendorFootnote")}
          </p>
        </div>

        <div className={demoStyles.demoCard}>
          <p className={demoStyles.demoCardTitle}>{t("dcim.rooms.accessCamerasTitle")}</p>
          <p className={demoStyles.demoMuted}>{t("dcim.rooms.accessCamerasHint")}</p>
          <div className={demoStyles.camGrid} style={{ marginTop: "var(--space-2)" }}>
            {CAM_KEYS.map((key) => (
              <div key={key} className={demoStyles.camTile}>
                <span className={demoStyles.camIcon} aria-hidden>
                  <i className="fas fa-video" />
                </span>
                <span>{t(key)}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
