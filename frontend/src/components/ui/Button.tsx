import type { ButtonHTMLAttributes, ReactNode } from "react";
import styles from "./Button.module.css";

type Props = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "default" | "ghost";
  children: ReactNode;
};

export function Button({ variant = "default", className = "", ...rest }: Props) {
  const cls = [styles.btn, variant === "ghost" ? styles.ghost : "", className].join(" ").trim();
  return <button type="button" className={cls} {...rest} />;
}
