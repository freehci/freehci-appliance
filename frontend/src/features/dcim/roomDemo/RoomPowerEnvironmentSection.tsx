import { useI18n } from "@/i18n/I18nProvider";
import dcimStyles from "../dcim.module.css";
import { DemoGauge } from "./DemoGauge";
import { DemoSparkline } from "./DemoSparkline";
import demoStyles from "./roomDemo.module.css";
import { useRoomPowerDemo } from "./useRoomPowerDemo";

export function RoomPowerEnvironmentSection({ roomId }: { roomId: number }) {
  const { t } = useI18n();
  const d = useRoomPowerDemo(roomId);

  return (
    <section className={dcimStyles.mfrDetailSection}>
      <h3 className={dcimStyles.mfrDetailSectionTitle}>{t("dcim.rooms.powerTabTitle")}</h3>
      <p className={demoStyles.demoNotice}>{t("dcim.rooms.demoPluginNotice")}</p>
      <p className={demoStyles.demoMuted}>{t("dcim.rooms.powerTabIntro")}</p>

      <div className={`${demoStyles.demoGrid} ${demoStyles.demoGrid3}`.trim()} style={{ marginTop: "var(--space-3)" }}>
        <div className={demoStyles.demoCard}>
          <DemoGauge
            value={d.upsSoc}
            min={0}
            max={100}
            label={t("dcim.rooms.demoGaugeUpsCharge")}
            unit="%"
            decimals={0}
            hue={142}
          />
          <p className={demoStyles.demoMuted} style={{ marginTop: "var(--space-2)", marginBottom: 0 }}>
            {t("dcim.rooms.demoUpsRuntimeHint")}
          </p>
        </div>
        <div className={demoStyles.demoCard}>
          <DemoGauge
            value={d.itLoadKw}
            min={0}
            max={24}
            label={t("dcim.rooms.demoGaugeItLoad")}
            unit="kW"
            decimals={1}
            hue={38}
          />
        </div>
        <div className={demoStyles.demoCard}>
          <DemoGauge
            value={d.coolingKw}
            min={0}
            max={10}
            label={t("dcim.rooms.demoGaugeCooling")}
            unit="kW"
            decimals={1}
            hue={210}
          />
        </div>
      </div>

      <div className={`${demoStyles.demoGrid}`.trim()} style={{ marginTop: "var(--space-3)" }}>
        <div className={demoStyles.demoCard}>
          <p className={demoStyles.demoCardTitle}>{t("dcim.rooms.demoTempsTitle")}</p>
          <div className={demoStyles.tempRow}>
            <div>
              <span className={demoStyles.tempLabel}>{t("dcim.rooms.demoTempSupply")}</span>
              <span className={demoStyles.tempVal}>{d.tempSupplyC.toFixed(1)} °C</span>
            </div>
            <div>
              <span className={demoStyles.tempLabel}>{t("dcim.rooms.demoTempReturn")}</span>
              <span className={demoStyles.tempVal}>{d.tempReturnC.toFixed(1)} °C</span>
            </div>
            <div>
              <span className={demoStyles.tempLabel}>{t("dcim.rooms.demoHumidity")}</span>
              <span className={demoStyles.tempVal}>{d.humidityPct.toFixed(0)} %</span>
            </div>
          </div>
          <DemoGauge
            value={d.tempReturnC}
            min={14}
            max={32}
            label={t("dcim.rooms.demoGaugeReturnAir")}
            unit="°C"
            decimals={1}
            hue={28}
          />
        </div>
        <div className={demoStyles.demoCard}>
          <p className={demoStyles.demoCardTitle}>{t("dcim.rooms.demoSparkTitleBlock")}</p>
          <DemoSparkline
            title={t("dcim.rooms.demoSparkIt")}
            values={d.itKwHistory}
            unit="kW"
            decimals={1}
            stroke="hsl(38 85% 55%)"
          />
          <DemoSparkline
            title={t("dcim.rooms.demoSparkCool")}
            values={d.coolingKwHistory}
            unit="kW"
            decimals={1}
            stroke="hsl(210 80% 55%)"
          />
          <DemoSparkline
            title={t("dcim.rooms.demoSparkPue")}
            values={d.pueHistory}
            unit=""
            decimals={2}
            stroke="hsl(265 70% 58%)"
          />
        </div>
      </div>
    </section>
  );
}
