import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { Panel } from "@/components/ui/Panel";
import { useI18n } from "@/i18n/I18nProvider";
import { ApiError } from "@/lib/api";
import * as api from "./dcimApi";
import { DcimInnerTabs } from "./DcimInnerTabs";
import styles from "./dcim.module.css";

export function DcimSitesPage() {
  const { t } = useI18n();
  const qc = useQueryClient();
  const [name, setName] = useState("");
  const [slug, setSlug] = useState("");
  const [err, setErr] = useState<string | null>(null);
  const [tab, setTab] = useState("main");

  const q = useQuery({ queryKey: ["dcim", "sites"], queryFn: api.listSites });
  const m = useMutation({
    mutationFn: () => api.createSite({ name: name.trim(), slug: slug.trim().toLowerCase() }),
    onSuccess: () => {
      setErr(null);
      setName("");
      setSlug("");
      void qc.invalidateQueries({ queryKey: ["dcim", "sites"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  return (
    <Panel title={t("nav.dcimSites")}>
      <DcimInnerTabs
        tabs={[{ id: "main", label: t("nav.dcimSites") }]}
        activeId={tab}
        onChange={setTab}
        ariaLabel={t("dcim.innerNavAria")}
      />
      {tab === "main" ? (
        <>
      {err ? <p className={styles.err}>{err}</p> : null}
      <form
        className={styles.formRow}
        onSubmit={(e) => {
          e.preventDefault();
          setErr(null);
          m.mutate();
        }}
      >
        <label>
          {t("dcim.common.name")}
          <input value={name} onChange={(e) => setName(e.target.value)} required />
        </label>
        <label>
          {t("dcim.common.slug")}
          <input
            value={slug}
            onChange={(e) => setSlug(e.target.value)}
            placeholder={t("dcim.sites.slugPh")}
            required
            pattern="[a-z0-9]+(?:-[a-z0-9]+)*"
            title={t("dcim.sites.slugPatternTitle")}
          />
        </label>
        <button type="submit" className={styles.btn} disabled={m.isPending}>
          {m.isPending ? t("dcim.common.creating") : t("dcim.common.create")}
        </button>
      </form>
      {q.isError ? (
        <p className={styles.err}>
          {t("dcim.sites.loadError")} {(q.error as Error).message}
        </p>
      ) : null}
      {q.isLoading ? <p className={styles.muted}>{t("dcim.common.loading")}</p> : null}
      {q.data && q.data.length === 0 ? <p className={styles.muted}>{t("dcim.sites.empty")}</p> : null}
      {q.data && q.data.length > 0 ? (
        <table className={styles.table}>
          <thead>
            <tr>
              <th>{t("dcim.common.id")}</th>
              <th>{t("dcim.common.name")}</th>
              <th>{t("dcim.common.slug")}</th>
            </tr>
          </thead>
          <tbody>
            {q.data.map((s) => (
              <tr key={s.id}>
                <td>{s.id}</td>
                <td>{s.name}</td>
                <td>{s.slug}</td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : null}
        </>
      ) : null}
    </Panel>
  );
}
