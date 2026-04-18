import { useI18n } from "@/i18n/I18nProvider";
import styles from "./iam.module.css";

export function IamUserComingSoonTab() {
  const { t } = useI18n();
  return <p className={styles.comingSoon}>{t("iam.comingSoonBody")}</p>;
}
