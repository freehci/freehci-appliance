import { useQuery } from "@tanstack/react-query";
import { Link, useParams } from "react-router-dom";
import { useI18n } from "@/i18n/I18nProvider";
import * as api from "./iamApi";
import styles from "./iam.module.css";

export function IamUserGroupsTab() {
  const { t } = useI18n();
  const { userId } = useParams<{ userId: string }>();
  const id = Number(userId);

  const q = useQuery({
    queryKey: ["iam", "person", id],
    queryFn: () => api.getPerson(id),
    enabled: Number.isFinite(id),
  });

  const person = q.data;
  if (!Number.isFinite(id)) return <p className={styles.err}>{t("iam.invalidId")}</p>;
  if (q.isLoading) return <p className={styles.intro}>…</p>;
  if (!person) return <p className={styles.err}>{t("iam.notFound")}</p>;

  return (
    <div>
      <h4 className={styles.userDetailSectionTitle}>{t("iam.groupsDirect")}</h4>
      <ul className={styles.pillList}>
        {person.groups_direct.map((g) => (
          <li key={g.id}>
            <Link className={styles.tableLink} to={`/iam/groups/${g.id}`}>
              {g.name}
            </Link>
          </li>
        ))}
      </ul>
      {person.groups_direct.length === 0 ? <p className={styles.intro}>—</p> : null}

      <h4 className={styles.userDetailSectionTitle}>{t("iam.groupsEffective")}</h4>
      <ul className={styles.pillList}>
        {person.groups_effective.map((g) => (
          <li key={g.id}>
            <Link className={styles.tableLink} to={`/iam/groups/${g.id}`}>
              {g.name}
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}
