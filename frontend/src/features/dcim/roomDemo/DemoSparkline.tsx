import styles from "./roomDemo.module.css";

type DemoSparklineProps = {
  title: string;
  values: number[];
  unit: string;
  decimals?: number;
  stroke: string;
};

export function DemoSparkline({ title, values, unit, decimals = 1, stroke }: DemoSparklineProps) {
  const w = 300;
  const h = 64;
  const padX = 4;
  const padY = 6;
  if (values.length < 2) return null;

  const vmin = Math.min(...values);
  const vmax = Math.max(...values);
  const span = Math.max(vmax - vmin, 1e-6);
  const last = values[values.length - 1]!;
  const lastStr = decimals > 0 ? last.toFixed(decimals) : String(Math.round(last));

  const pts = values
    .map((v, i) => {
      const x = padX + (i / (values.length - 1)) * (w - 2 * padX);
      const y = padY + (1 - (v - vmin) / span) * (h - 2 * padY);
      return `${x},${y}`;
    })
    .join(" ");

  const under = `${pts} ${w - padX},${h} ${padX},${h}`;

  return (
    <div className={styles.sparkBlock}>
      <div className={styles.sparkHead}>
        <p className={styles.sparkTitle}>{title}</p>
        <span className={styles.sparkValue}>
          {lastStr}
          {unit ? ` ${unit}` : ""}
        </span>
      </div>
      <svg className={styles.sparkSvg} viewBox={`0 0 ${w} ${h}`} preserveAspectRatio="none" aria-hidden>
        <polygon fill={`${stroke}22`} points={under} />
        <polyline fill="none" stroke={stroke} strokeWidth={2} strokeLinejoin="round" strokeLinecap="round" points={pts} />
      </svg>
    </div>
  );
}
