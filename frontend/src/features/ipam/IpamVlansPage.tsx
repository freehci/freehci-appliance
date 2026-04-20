import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { Panel } from "@/components/ui/Panel";
import * as dcimApi from "@/features/dcim/dcimApi";
import dcimStyles from "@/features/dcim/dcim.module.css";
import { useI18n } from "@/i18n/I18nProvider";
import { ApiError } from "@/lib/api";
import * as ipamApi from "./ipamApi";

export function IpamVlansPage() {
  const { t } = useI18n();
  const qc = useQueryClient();
  const [err, setErr] = useState<string | null>(null);
  const [filterSite, setFilterSite] = useState("");
  const [siteId, setSiteId] = useState("");
  const [vid, setVid] = useState("");
  const [name, setName] = useState("");
  const [vrfId, setVrfId] = useState("");
  const [vlanTenantId, setVlanTenantId] = useState("");

  const siteIdFilter = filterSite === "" ? undefined : Number(filterSite);
  const sitesQ = useQuery({ queryKey: ["dcim", "sites"], queryFn: dcimApi.listSites });
  const tenantsQ = useQuery({ queryKey: ["tenants"], queryFn: dcimApi.listTenants });
  const vlansQ = useQuery({
    queryKey: ["ipam", "vlans", siteIdFilter ?? "all"],
    queryFn: () => ipamApi.listIpamVlans(siteIdFilter),
  });
  const vrfsQ = useQuery({
    queryKey: ["ipam", "vrfs", siteId === "" ? "all" : Number(siteId)],
    queryFn: () => ipamApi.listIpamVrfs(siteId === "" ? undefined : Number(siteId)),
    enabled: siteId !== "",
  });
  const siteNameById = useMemo(() => {
    const m = new Map<number, string>();
    for (const s of sitesQ.data ?? []) m.set(s.id, s.name);
    return m;
  }, [sitesQ.data]);

  const tenantNameById = useMemo(() => {
    const m = new Map<number, string>();
    for (const tn of tenantsQ.data ?? []) m.set(tn.id, tn.name);
    return m;
  }, [tenantsQ.data]);

  const allVrfsQ = useQuery({
    queryKey: ["ipam", "vrfs", "all-names"],
    queryFn: () => ipamApi.listIpamVrfs(),
  });

  const vrfNameById = useMemo(() => {
    const m = new Map<number, string>();
    for (const v of allVrfsQ.data ?? []) m.set(v.id, v.name);
    return m;
  }, [allVrfsQ.data]);

  const createM = useMutation({
    mutationFn: () =>
      ipamApi.createIpamVlan({
        site_id: Number(siteId),
        vid: Number(vid),
        name: name.trim(),
        vrf_id: vrfId === "" ? null : Number(vrfId),
        tenant_id: vlanTenantId === "" ? undefined : Number(vlanTenantId),
      }),
    onSuccess: () => {
      setErr(null);
      setVid("");
      setName("");
      setVrfId("");
      setVlanTenantId("");
      void qc.invalidateQueries({ queryKey: ["ipam", "vlans"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const delM = useMutation({
    mutationFn: (id: number) => ipamApi.deleteIpamVlan(id),
    onSuccess: () => {
      setErr(null);
      void qc.invalidateQueries({ queryKey: ["ipam", "vlans"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  return (
    <Panel title={t("ipam.vlan.title")}>
      <p className={dcimStyles.muted}>{t("ipam.vlan.intro")}</p>
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
        {t("ipam.vlan.addTitle")}
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
          <select
            value={siteId}
            onChange={(e) => {
              setSiteId(e.target.value);
              setVrfId("");
            }}
            required
          >
            <option value="">{t("ipam.vrf.chooseSite")}</option>
            {(sitesQ.data ?? []).map((s) => (
              <option key={s.id} value={String(s.id)}>
                {s.name}
              </option>
            ))}
          </select>
        </label>
        <label>
          VLAN ID
          <input
            type="number"
            min={1}
            max={4094}
            value={vid}
            onChange={(e) => setVid(e.target.value)}
            required
          />
        </label>
        <label>
          {t("ipam.ipv4.name")}
          <input value={name} onChange={(e) => setName(e.target.value)} required />
        </label>
        <label>
          {t("ipam.vlan.vrfOptional")}
          <select value={vrfId} onChange={(e) => setVrfId(e.target.value)} disabled={siteId === ""}>
            <option value="">{t("ipam.vlan.noVrf")}</option>
            {(vrfsQ.data ?? []).map((v) => (
              <option key={v.id} value={String(v.id)}>
                {v.name}
              </option>
            ))}
          </select>
        </label>
        <label>
          {t("ipam.vlan.tenantOptional")}
          <select value={vlanTenantId} onChange={(e) => setVlanTenantId(e.target.value)}>
            <option value="">{t("dcim.common.none")}</option>
            {(tenantsQ.data ?? []).map((tn) => (
              <option key={tn.id} value={String(tn.id)}>
                {tn.name}
              </option>
            ))}
          </select>
        </label>
        <button type="submit" className={dcimStyles.btn} disabled={createM.isPending}>
          {createM.isPending ? "…" : t("ipam.vlan.create")}
        </button>
      </form>
      {vlansQ.isLoading ? <p className={dcimStyles.muted}>{t("dcim.common.loading")}</p> : null}
      {vlansQ.data && vlansQ.data.length === 0 && !vlansQ.isLoading ? (
        <p className={dcimStyles.muted}>{t("ipam.vlan.empty")}</p>
      ) : null}
      {vlansQ.data && vlansQ.data.length > 0 ? (
        <table className={dcimStyles.table} style={{ marginTop: "var(--space-3)" }}>
          <thead>
            <tr>
              <th>{t("ipam.ipv4.site")}</th>
              <th>{t("ipam.ipv4.tenantCol")}</th>
              <th>VLAN</th>
              <th>{t("ipam.ipv4.name")}</th>
              <th>VRF</th>
              <th>{t("ipam.ipv4.actionsCol")}</th>
            </tr>
          </thead>
          <tbody>
            {vlansQ.data.map((v) => (
              <tr key={v.id}>
                <td>{siteNameById.get(v.site_id) ?? v.site_id}</td>
                <td>
                  {v.tenant_id != null && v.tenant_id > 0
                    ? tenantNameById.get(v.tenant_id) ?? `#${v.tenant_id}`
                    : "—"}
                </td>
                <td>{v.vid}</td>
                <td>{v.name}</td>
                <td>{v.vrf_id != null ? vrfNameById.get(v.vrf_id) ?? `#${v.vrf_id}` : "—"}</td>
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
