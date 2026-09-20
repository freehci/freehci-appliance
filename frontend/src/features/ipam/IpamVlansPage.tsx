import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Fragment, useEffect, useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { Panel } from "@/components/ui/Panel";
import * as dcimApi from "@/features/dcim/dcimApi";
import dcimStyles from "@/features/dcim/dcim.module.css";
import { useI18n } from "@/i18n/I18nProvider";
import { ApiError } from "@/lib/api";
import * as ipamApi from "./ipamApi";
import prefixStyles from "./prefixPage.module.css";
import { PrefixDrawer } from "./prefixPageUi";

export function IpamVlansPage() {
  const { t } = useI18n();
  const qc = useQueryClient();
  const [searchParams, setSearchParams] = useSearchParams();
  const [err, setErr] = useState<string | null>(null);
  const [expandVlanId, setExpandVlanId] = useState<number | null>(null);
  const [filterSite, setFilterSite] = useState("");
  const [siteId, setSiteId] = useState("");
  const [vid, setVid] = useState("");
  const [name, setName] = useState("");
  const [vrfId, setVrfId] = useState("");
  const [vlanTenantId, setVlanTenantId] = useState("");
  const [drawerOpen, setDrawerOpen] = useState(false);

  const siteIdFilter = filterSite === "" ? undefined : Number(filterSite);
  const sitesQ = useQuery({ queryKey: ["dcim", "sites"], queryFn: dcimApi.listSites });
  const tenantsQ = useQuery({ queryKey: ["tenants"], queryFn: dcimApi.listTenants });
  const vlansQ = useQuery({
    queryKey: ["ipam", "vlans", siteIdFilter ?? "all"],
    queryFn: () => ipamApi.listIpamVlans(siteIdFilter),
  });
  const prefixesQ = useQuery({
    queryKey: ["ipam", "ipv4-prefixes", "for-vlans", siteIdFilter ?? "all"],
    queryFn: () => ipamApi.listIpv4Prefixes(siteIdFilter),
  });
  const expandedPrefixesQ = useQuery({
    queryKey: ["ipam", "ipv4-prefixes", "by-vlan", expandVlanId ?? "none", siteIdFilter ?? "all"],
    queryFn: () => ipamApi.listIpv4Prefixes(siteIdFilter, undefined, expandVlanId!),
    enabled: expandVlanId != null && expandVlanId > 0,
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

  const prefixesByVlanId = useMemo(() => {
    const m = new Map<number, number>();
    for (const p of prefixesQ.data ?? []) {
      const vid = p.vlan_id;
      if (vid != null && vid > 0) m.set(vid, (m.get(vid) ?? 0) + 1);
    }
    return m;
  }, [prefixesQ.data]);

  useEffect(() => {
    const rawVlan = searchParams.get("vlan");
    const rawSite = searchParams.get("site");
    const v = rawVlan != null && rawVlan !== "" ? Number(rawVlan) : null;
    const s = rawSite != null && rawSite !== "" ? Number(rawSite) : null;
    if (s != null && Number.isFinite(s) && s > 0) setFilterSite(String(s));
    if (v != null && Number.isFinite(v) && v > 0) setExpandVlanId(v);
  }, []); // kun init fra URL

  const toggleExpand = (id: number, siteId: number) => {
    setExpandVlanId((cur) => {
      const next = cur === id ? null : id;
      const sp = new URLSearchParams(searchParams);
      if (next == null) sp.delete("vlan");
      else sp.set("vlan", String(next));
      sp.set("site", String(siteId));
      setSearchParams(sp, { replace: true });
      return next;
    });
  };

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
      setDrawerOpen(false);
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

  const openCreate = () => {
    setErr(null);
    if (filterSite && siteId === "") setSiteId(filterSite);
    setDrawerOpen(true);
  };

  return (
    <Panel>
      {err ? <p className={dcimStyles.err}>{err}</p> : null}
      <header className={prefixStyles.pageHead}>
        <div>
          <p className={prefixStyles.crumb}>
            {t("ipam.ipv4.crumbIpam")}
            <span className={prefixStyles.crumbSep}>/</span>
            {t("nav.segments")}
          </p>
          <h1 className={prefixStyles.title}>{t("ipam.vlan.title")}</h1>
          <p className={prefixStyles.intro}>{t("ipam.vlan.intro")}</p>
        </div>
        <div className={prefixStyles.headActions}>
          <button type="button" className={dcimStyles.btn} onClick={openCreate}>
            + {t("ipam.vlan.new")}
          </button>
        </div>
      </header>
      <div className={prefixStyles.toolbar}>
        <label className={prefixStyles.toolbarField}>
          {t("ipam.ipv4.filterSite")}
          <select
            value={filterSite}
            onChange={(e) => {
              setFilterSite(e.target.value);
              setExpandVlanId(null);
              const sp = new URLSearchParams(searchParams);
              if (e.target.value === "") sp.delete("site");
              else sp.set("site", e.target.value);
              sp.delete("vlan");
              setSearchParams(sp, { replace: true });
            }}
          >
            <option value="">{t("ipam.ipv4.allSites")}</option>
            {(sitesQ.data ?? []).map((s) => (
              <option key={s.id} value={String(s.id)}>
                {s.name}
              </option>
            ))}
          </select>
        </label>
      </div>
      {vlansQ.isLoading ? <p className={dcimStyles.muted}>{t("dcim.common.loading")}</p> : null}
      <div className={prefixStyles.tableCard}>
      {vlansQ.data && vlansQ.data.length === 0 && !vlansQ.isLoading ? (
        <p className={dcimStyles.muted} style={{ padding: "var(--space-3)" }}>{t("ipam.vlan.empty")}</p>
      ) : null}
      {vlansQ.data && vlansQ.data.length > 0 ? (
        <div className={prefixStyles.tableScroll}>
        <table className={dcimStyles.table}>
          <thead>
            <tr>
              <th>{t("ipam.ipv4.site")}</th>
              <th>{t("ipam.ipv4.tenantCol")}</th>
              <th>VLAN</th>
              <th>{t("ipam.ipv4.name")}</th>
              <th>Subnets</th>
              <th>VRF</th>
              <th>{t("ipam.ipv4.actionsCol")}</th>
            </tr>
          </thead>
          <tbody>
            {vlansQ.data.map((v) => (
              <Fragment key={v.id}>
                <tr key={v.id}>
                  <td>{siteNameById.get(v.site_id) ?? v.site_id}</td>
                  <td>
                    {v.tenant_id != null && v.tenant_id > 0
                      ? tenantNameById.get(v.tenant_id) ?? `#${v.tenant_id}`
                      : "—"}
                  </td>
                  <td>{v.vid}</td>
                  <td>{v.name}</td>
                  <td className={dcimStyles.muted}>
                    <button
                      type="button"
                      className={dcimStyles.btnLink}
                      onClick={() => toggleExpand(v.id, v.site_id)}
                    >
                      {prefixesByVlanId.get(v.id) ?? 0}
                    </button>
                  </td>
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
                {expandVlanId === v.id ? (
                  <tr key={`${v.id}-subnets`}>
                    <td colSpan={7} style={{ paddingTop: "0.25rem" }}>
                      <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                        <strong>{t("ipam.vlan.showSubnets")}</strong>
                        <button type="button" className={dcimStyles.btnLink} onClick={() => setExpandVlanId(null)}>
                          {t("ipam.vlan.hideSubnets")}
                        </button>
                      </div>
                      {expandedPrefixesQ.isLoading ? <p className={dcimStyles.muted}>{t("dcim.common.loading")}</p> : null}
                      {expandedPrefixesQ.isError ? (
                        <p className={dcimStyles.err}>{(expandedPrefixesQ.error as Error).message}</p>
                      ) : null}
                      {expandedPrefixesQ.data && expandedPrefixesQ.data.length > 0 ? (
                        <table className={dcimStyles.table} style={{ marginTop: "0.5rem" }}>
                          <thead>
                            <tr>
                              <th>{t("ipam.ipv4.name")}</th>
                              <th>{t("ipam.ipv4.cidr")}</th>
                              <th>{t("ipam.ipv4.site")}</th>
                            </tr>
                          </thead>
                          <tbody>
                            {expandedPrefixesQ.data.map((p) => (
                              <tr key={p.id}>
                                <td>{p.name}</td>
                                <td>
                                  <code>{p.cidr}</code>
                                </td>
                                <td className={dcimStyles.muted}>
                                  {siteNameById.get(p.site_id) ?? `#${p.site_id}`}
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      ) : (
                        !expandedPrefixesQ.isLoading && <p className={dcimStyles.muted}>—</p>
                      )}
                    </td>
                  </tr>
                ) : null}
              </Fragment>
            ))}
          </tbody>
        </table>
        </div>
      ) : null}
      </div>
      <PrefixDrawer
        title={t("ipam.vlan.addTitle")}
        open={drawerOpen}
        onClose={() => {
          if (!createM.isPending) setDrawerOpen(false);
        }}
        footer={
          <>
            <button type="button" className={dcimStyles.btn} disabled={createM.isPending} onClick={() => setDrawerOpen(false)}>
              {t("dcim.common.cancel")}
            </button>
            <button
              type="button"
              className={dcimStyles.btn}
              disabled={createM.isPending}
              onClick={() => {
                setErr(null);
                createM.mutate();
              }}
            >
              {createM.isPending ? t("dcim.common.creating") : t("ipam.vlan.create")}
            </button>
          </>
        }
      >
        <div className={prefixStyles.drawerFields}>
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
            <input type="number" min={1} max={4094} value={vid} onChange={(e) => setVid(e.target.value)} required />
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
        </div>
      </PrefixDrawer>
    </Panel>
  );
}
