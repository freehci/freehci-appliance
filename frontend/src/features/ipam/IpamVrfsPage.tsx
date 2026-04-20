import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { Panel } from "@/components/ui/Panel";
import * as dcimApi from "@/features/dcim/dcimApi";
import dcimStyles from "@/features/dcim/dcim.module.css";
import { useI18n } from "@/i18n/I18nProvider";
import { ApiError } from "@/lib/api";
import * as ipamApi from "./ipamApi";

export function IpamVrfsPage() {
  const { t } = useI18n();
  const qc = useQueryClient();
  const [err, setErr] = useState<string | null>(null);
  const [filterSite, setFilterSite] = useState("");
  const [siteId, setSiteId] = useState("");
  const [name, setName] = useState("");
  const [rd, setRd] = useState("");

  const siteIdFilter = filterSite === "" ? undefined : Number(filterSite);
  const sitesQ = useQuery({ queryKey: ["dcim", "sites"], queryFn: dcimApi.listSites });
  const vrfsQ = useQuery({
    queryKey: ["ipam", "vrfs", siteIdFilter ?? "all"],
    queryFn: () => ipamApi.listIpamVrfs(siteIdFilter),
  });

  const createM = useMutation({
    mutationFn: () =>
      ipamApi.createIpamVrf({
        site_id: Number(siteId),
        name: name.trim(),
        route_distinguisher: rd.trim() === "" ? null : rd.trim(),
      }),
    onSuccess: () => {
      setErr(null);
      setName("");
      setRd("");
      void qc.invalidateQueries({ queryKey: ["ipam", "vrfs"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const siteNameById = useMemo(() => {
    const m = new Map<number, string>();
    for (const s of sitesQ.data ?? []) m.set(s.id, s.name);
    return m;
  }, [sitesQ.data]);

  const delM = useMutation({
    mutationFn: (id: number) => ipamApi.deleteIpamVrf(id),
    onSuccess: () => {
      setErr(null);
      void qc.invalidateQueries({ queryKey: ["ipam", "vrfs"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  return (
    <Panel title={t("ipam.vrf.title")}>
      <p className={dcimStyles.muted}>{t("ipam.vrf.intro")}</p>
      {err ? <p className={dcimStyles.err}>{err}</p> : null}
      <div className={dcimStyles.formRow} style={{ marginTop: "var(--space-2)", flexWrap: "wrap" }}>
        <label>
          {t("ipam.ipv4.filterSite")}
          <select value={filterSite} onChange={(e) => setFilterSite(e.target.value)}>
            <option value="">{t("ipam.ipv4.allSites")}</option>
            {(sitesQ.data ?? []).map((s) => (
              <option key={s.id} value={String(s.id)}>
                {s.name}
              </option>
            ))}
          </select>
        </label>
      </div>
      <h3 className={dcimStyles.mfrDetailSectionTitle} style={{ marginTop: "var(--space-3)" }}>
        {t("ipam.vrf.addTitle")}
      </h3>
      <form
        className={dcimStyles.formRow}
        style={{ flexWrap: "wrap", alignItems: "flex-end" }}
        onSubmit={(e) => {
          e.preventDefault();
          setErr(null);
          createM.mutate();
        }}
      >
        <label>
          {t("ipam.ipv4.site")}
          <select value={siteId} onChange={(e) => setSiteId(e.target.value)} required>
            <option value="">{t("ipam.vrf.chooseSite")}</option>
            {(sitesQ.data ?? []).map((s) => (
              <option key={s.id} value={String(s.id)}>
                {s.name}
              </option>
            ))}
          </select>
        </label>
        <label>
          {t("ipam.vrf.name")}
          <input value={name} onChange={(e) => setName(e.target.value)} required />
        </label>
        <label>
          {t("ipam.vrf.rd")}
          <input value={rd} onChange={(e) => setRd(e.target.value)} placeholder={t("ipam.vrf.rdPlaceholder")} />
        </label>
        <button type="submit" className={dcimStyles.btn} disabled={createM.isPending}>
          {createM.isPending ? "…" : t("ipam.vrf.create")}
        </button>
      </form>
      {vrfsQ.isLoading ? <p className={dcimStyles.muted}>{t("dcim.common.loading")}</p> : null}
      {vrfsQ.data && vrfsQ.data.length === 0 && !vrfsQ.isLoading ? (
        <p className={dcimStyles.muted}>{t("ipam.vrf.empty")}</p>
      ) : null}
      {vrfsQ.data && vrfsQ.data.length > 0 ? (
        <table className={dcimStyles.table} style={{ marginTop: "var(--space-3)" }}>
          <thead>
            <tr>
              <th>{t("ipam.ipv4.site")}</th>
              <th>{t("ipam.vrf.name")}</th>
              <th>{t("ipam.vrf.rd")}</th>
              <th>{t("ipam.ipv4.actionsCol")}</th>
            </tr>
          </thead>
          <tbody>
            {vrfsQ.data.map((v) => (
              <tr key={v.id}>
                <td>{siteNameById.get(v.site_id) ?? v.site_id}</td>
                <td>{v.name}</td>
                <td>{v.route_distinguisher ?? "—"}</td>
                <td>
                  <button
                    type="button"
                    className={dcimStyles.btnLink}
                    disabled={delM.isPending}
                    onClick={() => delM.mutate(v.id)}
                  >
                    {t("dcim.common.delete")}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : null}
    </Panel>
  );
}
