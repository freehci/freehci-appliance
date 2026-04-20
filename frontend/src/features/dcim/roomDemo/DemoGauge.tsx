import styles from "./demoGauge.module.css";

const R = 44;
const CX = 60;
const CY = 56;
/** Halvbue nederst: venstre → høyre */
const ARC_D = `M ${CX - R} ${CY} A ${R} ${R} 0 0 1 ${CX + R} ${CY}`;
const ARC_LEN = Math.PI * R;

type DemoGaugeProps = {
  value: number;
  min: number;
  max: number;
  label: string;
  unit: string;
  decimals?: number;
  /** 0–360 for stroke-farge (HSL) */
  hue?: number;
};

export function DemoGauge({ value, min, max, label, unit, decimals = 0, hue = 195 }: DemoGaugeProps) {
  const clamped = Math.min(max, Math.max(min, value));
  const pct = (clamped - min) / (max - min || 1);
  const dash = ARC_LEN * pct;

  const shown =
    decimals > 0 ? clamped.toFixed(decimals) : Math.round(clamped).toString();

  return (
    <div className={styles.wrap}>
      <p className={styles.label}>{label}</p>
      <div className={styles.svgWrap}>
        <svg className={styles.svg} viewBox="0 0 120 78" aria-hidden>
          <path d={ARC_D} fill="none" stroke="rgba(255,255,255,0.08)" strokeWidth={9} strokeLinecap="round" />
          <path
            d={ARC_D}
            fill="none"
            stroke={`hsl(${hue} 70% 52%)`}
            strokeWidth={9}
            strokeLinecap="round"
            strokeDasharray={`${dash} ${ARC_LEN}`}
          />
        </svg>
        <div className={styles.valueBlock}>
          <span className={styles.value}>{shown}</span>
          <span className={styles.unit}>{unit}</span>
        </div>
      </div>
    </div>
  );
}
