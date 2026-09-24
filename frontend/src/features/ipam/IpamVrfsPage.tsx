import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { Panel } from "@/components/ui/Panel";
import * as dcimApi from "@/features/dcim/dcimApi";
import { DcimInnerTabs } from "@/features/dcim/DcimInnerTabs";
import dcimStyles from "@/features/dcim/dcim.module.css";
import { useI18n } from "@/i18n/I18nProvider";
import { ApiError } from "@/lib/api";
import * as ipamApi from "./ipamApi";
import prefixStyles from "./prefixPage.module.css";
import { PrefixDrawer } from "./prefixPageUi";

const TABS = new Set(["vrfs", "instances", "targets", "as", "bgp"]);

export function IpamVrfsPage() {
  const { t } = useI18n();
  const qc = useQueryClient();
  const [searchParams, setSearchParams] = useSearchParams();
  const tabParam = searchParams.get("tab");
  const tab = tabParam != null && TABS.has(tabParam) ? tabParam : "vrfs";
  const setTab = (next: string) => {
    const n = new URLSearchParams(searchParams);
    if (next === "vrfs") n.delete("tab");
    else n.set("tab", next);
    setSearchParams(n, { replace: true });
  };

  const [err, setErr] = useState<string | null>(null);
  const [filterSite, setFilterSite] = useState("");
  const [siteId, setSiteId] = useState("");
  const [name, setName] = useState("");
  const [rd, setRd] = useState("");
  const [drawerOpen, setDrawerOpen] = useState(false);

  const [asAsn, setAsAsn] = useState("");
  const [asName, setAsName] = useState("");
  const [asTenant, setAsTenant] = useState("");
  const [asDrawer, setAsDrawer] = useState(false);
  const [assignAsId, setAssignAsId] = useState("");
  const [assignSite, setAssignSite] = useState("");
  const [assignVrf, setAssignVrf] = useState("");

  const [bgpName, setBgpName] = useState("");
  const [bgpLocalAs, setBgpLocalAs] = useState("");
  const [bgpRemoteAsn, setBgpRemoteAsn] = useState("");
  const [bgpPeer, setBgpPeer] = useState("");
  const [bgpSite, setBgpSite] = useState("");
  const [bgpVrf, setBgpVrf] = useState("");
  const [bgpV6, setBgpV6] = useState(false);
  const [bgpInst, setBgpInst] = useState("");
  const [bgpDrawer, setBgpDrawer] = useState(false);
  const [biName, setBiName] = useState("");
  const [biDevice, setBiDevice] = useState("");
  const [biAs, setBiAs] = useState("");
  const [biVrf, setBiVrf] = useState("");
  const [biIntent, setBiIntent] = useState("recorded");
  const [biRouterId, setBiRouterId] = useState("");
  const [instVrf, setInstVrf] = useState("");
  const [instDevice, setInstDevice] = useState("");
  const [instRd, setInstRd] = useState("");
  const [instIntent, setInstIntent] = useState("recorded");
  const [rtName, setRtName] = useState("");
  const [rtValue, setRtValue] = useState("");
  const [rtSlug, setRtSlug] = useState("");
  const [bindVrf, setBindVrf] = useState("");
  const [bindRt, setBindRt] = useState("");
  const [bindDir, setBindDir] = useState("import");
  const [stName, setStName] = useState("");
  const [stVrfA, setStVrfA] = useState("");
  const [stVrfB, setStVrfB] = useState("");

  const siteIdFilter = filterSite === "" ? undefined : Number(filterSite);
  const sitesQ = useQuery({ queryKey: ["dcim", "sites"], queryFn: dcimApi.listSites });
  const tenantsQ = useQuery({ queryKey: ["tenants"], queryFn: dcimApi.listTenants });
  const vrfsQ = useQuery({
    queryKey: ["ipam", "vrfs", siteIdFilter ?? "all"],
    queryFn: () => ipamApi.listIpamVrfs(siteIdFilter),
  });
  const allVrfsQ = useQuery({
    queryKey: ["ipam", "vrfs", "all-for-stretch"],
    queryFn: () => ipamApi.listIpamVrfs(),
  });
  const stretchesQ = useQuery({
    queryKey: ["ipam", "vrf-stretches", siteIdFilter ?? "all"],
    queryFn: () => ipamApi.listVrfStretches(siteIdFilter),
  });
  const asQ = useQuery({ queryKey: ["ipam", "autonomous-systems"], queryFn: () => ipamApi.listAutonomousSystems() });
  const assignQ = useQuery({
    queryKey: ["ipam", "as-assignments", siteIdFilter ?? "all"],
    queryFn: () => ipamApi.listAsAssignments(siteIdFilter),
  });
  const bgpQ = useQuery({
    queryKey: ["ipam", "bgp-sessions", siteIdFilter ?? "all"],
    queryFn: () => ipamApi.listBgpSessions(siteIdFilter),
  });
  const bgpInstQ = useQuery({
    queryKey: ["ipam", "bgp-instances", siteIdFilter ?? "all"],
    queryFn: () => ipamApi.listBgpInstances(siteIdFilter),
  });
  const devicesQ = useQuery({ queryKey: ["dcim", "devices"], queryFn: dcimApi.listDevices });
  const instQ = useQuery({
    queryKey: ["ipam", "vrf-instances", siteIdFilter ?? "all"],
    queryFn: () => ipamApi.listVrfInstances({ siteId: siteIdFilter }),
  });
  const rtQ = useQuery({ queryKey: ["ipam", "route-targets"], queryFn: () => ipamApi.listRouteTargets() });
  const rtBindQ = useQuery({
    queryKey: ["ipam", "vrf-route-targets", siteIdFilter ?? "all"],
    queryFn: () => ipamApi.listVrfRouteTargets({ siteId: siteIdFilter }),
  });

  const fail = (e: Error) => setErr(e instanceof ApiError ? e.message : e.message);

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
      setDrawerOpen(false);
      void qc.invalidateQueries({ queryKey: ["ipam", "vrfs"] });
    },
    onError: fail,
  });

  const siteNameById = useMemo(() => {
    const m = new Map<number, string>();
    for (const s of sitesQ.data ?? []) m.set(s.id, s.name);
    return m;
  }, [sitesQ.data]);

  const asNameById = useMemo(() => {
    const m = new Map<number, string>();
    for (const a of asQ.data ?? []) m.set(a.id, `AS${a.asn} ${a.name}`);
    return m;
  }, [asQ.data]);

  const delM = useMutation({
    mutationFn: (id: number) => ipamApi.deleteIpamVrf(id),
    onSuccess: () => {
      setErr(null);
      void qc.invalidateQueries({ queryKey: ["ipam", "vrfs"] });
      void qc.invalidateQueries({ queryKey: ["ipam", "vrf-stretches"] });
    },
    onError: fail,
  });
  const createStM = useMutation({
    mutationFn: () =>
      ipamApi.createVrfStretch({
        vrf_a_id: Number(stVrfA),
        vrf_b_id: Number(stVrfB),
        name: stName.trim(),
      }),
    onSuccess: () => {
      setErr(null);
      setStName("");
      setStVrfA("");
      setStVrfB("");
      void qc.invalidateQueries({ queryKey: ["ipam", "vrf-stretches"] });
    },
    onError: fail,
  });
  const delStM = useMutation({
    mutationFn: (id: number) => ipamApi.deleteVrfStretch(id),
    onSuccess: () => {
      setErr(null);
      void qc.invalidateQueries({ queryKey: ["ipam", "vrf-stretches"] });
    },
    onError: fail,
  });

  const createAsM = useMutation({
    mutationFn: () =>
      ipamApi.createAutonomousSystem({
        asn: Number(asAsn),
        name: asName.trim(),
        tenant_id: asTenant === "" ? null : Number(asTenant),
      }),
    onSuccess: () => {
      setErr(null);
      setAsAsn("");
      setAsName("");
      setAsDrawer(false);
      void qc.invalidateQueries({ queryKey: ["ipam", "autonomous-systems"] });
    },
    onError: fail,
  });

  const delAsM = useMutation({
    mutationFn: (id: number) => ipamApi.deleteAutonomousSystem(id),
    onSuccess: () => {
      setErr(null);
      void qc.invalidateQueries({ queryKey: ["ipam", "autonomous-systems"] });
    },
    onError: fail,
  });

  const createAssignM = useMutation({
    mutationFn: () =>
      ipamApi.createAsAssignment({
        autonomous_system_id: Number(assignAsId),
        site_id: Number(assignSite),
        vrf_id: assignVrf === "" ? null : Number(assignVrf),
      }),
    onSuccess: () => {
      setErr(null);
      setAssignAsId("");
      void qc.invalidateQueries({ queryKey: ["ipam", "as-assignments"] });
    },
    onError: fail,
  });

  const delAssignM = useMutation({
    mutationFn: (id: number) => ipamApi.deleteAsAssignment(id),
    onSuccess: () => {
      setErr(null);
      void qc.invalidateQueries({ queryKey: ["ipam", "as-assignments"] });
    },
    onError: fail,
  });

  const createBgpM = useMutation({
    mutationFn: () =>
      ipamApi.createBgpSession({
        site_id: bgpInst === "" ? Number(bgpSite) : undefined,
        bgp_instance_id: bgpInst === "" ? null : Number(bgpInst),
        local_as_id: bgpInst === "" ? Number(bgpLocalAs) : undefined,
        remote_asn: Number(bgpRemoteAsn),
        peer_ip: bgpPeer.trim(),
        vrf_id: bgpInst === "" && bgpVrf !== "" ? Number(bgpVrf) : undefined,
        name: bgpName.trim() || null,
        address_families: bgpV6 ? ["ipv4-unicast", "ipv6-unicast"] : ["ipv4-unicast"],
      }),
    onSuccess: () => {
      setErr(null);
      setBgpName("");
      setBgpPeer("");
      setBgpRemoteAsn("");
      setBgpDrawer(false);
      void qc.invalidateQueries({ queryKey: ["ipam", "bgp-sessions"] });
    },
    onError: fail,
  });

  const createInstM = useMutation({
    mutationFn: () =>
      ipamApi.createVrfInstance(Number(instVrf), {
        device_id: Number(instDevice),
        intent: instIntent,
        route_distinguisher: instRd.trim() === "" ? null : instRd.trim(),
      }),
    onSuccess: () => {
      setErr(null);
      setInstVrf("");
      setInstDevice("");
      setInstRd("");
      setInstIntent("recorded");
      void qc.invalidateQueries({ queryKey: ["ipam", "vrf-instances"] });
    },
    onError: fail,
  });
  const createRtM = useMutation({
    mutationFn: () =>
      ipamApi.createRouteTarget({
        name: rtName.trim(),
        slug: rtSlug.trim() || null,
        value: rtValue.trim(),
      }),
    onSuccess: () => {
      setErr(null);
      setRtName("");
      setRtSlug("");
      setRtValue("");
      void qc.invalidateQueries({ queryKey: ["ipam", "route-targets"] });
    },
    onError: fail,
  });
  const delRtM = useMutation({
    mutationFn: (id: number) => ipamApi.deleteRouteTarget(id),
    onSuccess: () => {
      setErr(null);
      void qc.invalidateQueries({ queryKey: ["ipam", "route-targets"] });
      void qc.invalidateQueries({ queryKey: ["ipam", "vrf-route-targets"] });
    },
    onError: fail,
  });
  const bindRtM = useMutation({
    mutationFn: () =>
      ipamApi.bindVrfRouteTarget(Number(bindVrf), {
        route_target_id: Number(bindRt),
        direction: bindDir,
      }),
    onSuccess: () => {
      setErr(null);
      setBindVrf("");
      setBindRt("");
      setBindDir("import");
      void qc.invalidateQueries({ queryKey: ["ipam", "vrf-route-targets"] });
    },
    onError: fail,
  });
  const unbindRtM = useMutation({
    mutationFn: (id: number) => ipamApi.unbindVrfRouteTarget(id),
    onSuccess: () => {
      setErr(null);
      void qc.invalidateQueries({ queryKey: ["ipam", "vrf-route-targets"] });
    },
    onError: fail,
  });
  const delInstM = useMutation({
    mutationFn: (id: number) => ipamApi.deleteVrfInstance(id),
    onSuccess: () => {
      setErr(null);
      void qc.invalidateQueries({ queryKey: ["ipam", "vrf-instances"] });
    },
    onError: fail,
  });
  const delBgpM = useMutation({
    mutationFn: (id: number) => ipamApi.deleteBgpSession(id),
    onSuccess: () => {
      setErr(null);
      void qc.invalidateQueries({ queryKey: ["ipam", "bgp-sessions"] });
    },
    onError: fail,
  });
  const createBiM = useMutation({
    mutationFn: () =>
      ipamApi.createBgpInstance({
        device_id: Number(biDevice),
        local_as_id: Number(biAs),
        vrf_id: biVrf === "" ? null : Number(biVrf),
        name: biName.trim() || null,
        intent: biIntent,
        router_id: biRouterId.trim() === "" ? null : biRouterId.trim(),
      }),
    onSuccess: () => {
      setErr(null);
      setBiName("");
      setBiDevice("");
      setBiAs("");
      setBiVrf("");
      setBiIntent("recorded");
      setBiRouterId("");
      void qc.invalidateQueries({ queryKey: ["ipam", "bgp-instances"] });
    },
    onError: fail,
  });
  const delBiM = useMutation({
    mutationFn: (id: number) => ipamApi.deleteBgpInstance(id),
    onSuccess: () => {
      setErr(null);
      void qc.invalidateQueries({ queryKey: ["ipam", "bgp-instances"] });
      void qc.invalidateQueries({ queryKey: ["ipam", "bgp-sessions"] });
    },
    onError: fail,
  });

  const newLabel = tab === "as" ? t("ipam.as.new") : tab === "bgp" ? t("ipam.bgp.new") : t("ipam.vrf.new");
  const assignVrfs = (vrfsQ.data ?? []).filter((v) => assignSite === "" || v.site_id === Number(assignSite));
  const bgpVrfs = (vrfsQ.data ?? []).filter((v) => bgpSite === "" || v.site_id === Number(bgpSite));

  return (
    <Panel>
      {err ? <p className={dcimStyles.err}>{err}</p> : null}
      <header className={prefixStyles.pageHead}>
        <div>
          <p className={prefixStyles.crumb}>
            {t("ipam.ipv4.crumbIpam")}
            <span className={prefixStyles.crumbSep}>/</span>
            {t("nav.routing")}
          </p>
          <h1 className={prefixStyles.title}>{t("ipam.vrf.title")}</h1>
          <p className={prefixStyles.intro}>{t("ipam.vrf.intro")}</p>
        </div>
        {tab !== "instances" && tab !== "targets" ? (
          <div className={prefixStyles.headActions}>
            <button
              type="button"
              className={dcimStyles.btn}
              onClick={() => {
                setErr(null);
                if (tab === "as") setAsDrawer(true);
                else if (tab === "bgp") {
                  if (filterSite && bgpSite === "") setBgpSite(filterSite);
                  setBgpDrawer(true);
                } else {
                  if (filterSite && siteId === "") setSiteId(filterSite);
                  setDrawerOpen(true);
                }
              }}
            >
              + {newLabel}
            </button>
          </div>
        ) : null}
      </header>
      <DcimInnerTabs
        ariaLabel={t("ipam.routing.tabs")}
        activeId={tab}
        onChange={setTab}
        tabs={[
          { id: "vrfs", label: t("ipam.routing.tabVrfs") },
          { id: "instances", label: t("ipam.routing.tabInstances") },
          { id: "targets", label: t("ipam.routing.tabTargets") },
          { id: "as", label: t("ipam.routing.tabAs") },
          { id: "bgp", label: t("ipam.routing.tabBgp") },
        ]}
      />
      <div className={prefixStyles.toolbar}>
        <label className={prefixStyles.toolbarField}>
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

      {tab === "vrfs" ? (
        <>
        <div className={prefixStyles.tableCard}>
          {vrfsQ.isLoading ? (
            <p className={dcimStyles.muted} style={{ padding: "var(--space-3)" }}>
              {t("dcim.common.loading")}
            </p>
          ) : null}
          {vrfsQ.data && vrfsQ.data.length === 0 && !vrfsQ.isLoading ? (
            <p className={dcimStyles.muted} style={{ padding: "var(--space-3)" }}>
              {t("ipam.vrf.empty")}
            </p>
          ) : null}
          {vrfsQ.data && vrfsQ.data.length > 0 ? (
            <div className={prefixStyles.tableScroll}>
              <table className={dcimStyles.table}>
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
                        <button type="button" className={dcimStyles.btnLink} disabled={delM.isPending} onClick={() => delM.mutate(v.id)}>
                          {t("dcim.common.delete")}
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : null}
        </div>
        <section className={dcimStyles.mfrDetailSection}>
          <h3 className={dcimStyles.mfrDetailSectionTitle}>{t("ipam.vrfStretch.title")}</h3>
          <p className={dcimStyles.muted}>{t("ipam.vrfStretch.hint")}</p>
          <form
            className={dcimStyles.formRow}
            onSubmit={(e) => {
              e.preventDefault();
              setErr(null);
              createStM.mutate();
            }}
          >
            <label>
              {t("ipam.ipv4.name")}
              <input value={stName} onChange={(e) => setStName(e.target.value)} required />
            </label>
            <label>
              {t("ipam.vrfStretch.vrfA")}
              <select value={stVrfA} onChange={(e) => setStVrfA(e.target.value)} required>
                <option value="">{t("ipam.vrfStretch.choose")}</option>
                {(allVrfsQ.data ?? []).map((v) => (
                  <option key={v.id} value={String(v.id)}>
                    {siteNameById.get(v.site_id) ?? v.site_id} · {v.name}
                  </option>
                ))}
              </select>
            </label>
            <label>
              {t("ipam.vrfStretch.vrfB")}
              <select value={stVrfB} onChange={(e) => setStVrfB(e.target.value)} required>
                <option value="">{t("ipam.vrfStretch.choose")}</option>
                {(allVrfsQ.data ?? []).map((v) => (
                  <option key={`b-${v.id}`} value={String(v.id)}>
                    {siteNameById.get(v.site_id) ?? v.site_id} · {v.name}
                  </option>
                ))}
              </select>
            </label>
            <button
              type="submit"
              className={dcimStyles.btn}
              disabled={createStM.isPending || stName.trim() === "" || stVrfA === "" || stVrfB === "" || stVrfA === stVrfB}
            >
              {t("ipam.vrfStretch.add")}
            </button>
          </form>
          {(stretchesQ.data ?? []).length > 0 ? (
            <ul className={dcimStyles.ipList}>
              {(stretchesQ.data ?? []).map((s) => (
                <li key={s.id}>
                  {s.name} <code>{s.slug}</code>
                  {` · ${siteNameById.get(s.site_a_id ?? 0) ?? s.site_a_id} ${s.vrf_a_name ?? "—"}`}
                  {` ↔ ${siteNameById.get(s.site_b_id ?? 0) ?? s.site_b_id} ${s.vrf_b_name ?? "—"}`}{" "}
                  <button
                    type="button"
                    className={dcimStyles.btnLink}
                    disabled={delStM.isPending}
                    onClick={() => delStM.mutate(s.id)}
                  >
                    {t("dcim.common.delete")}
                  </button>
                </li>
              ))}
            </ul>
          ) : (
            !stretchesQ.isLoading && <p className={dcimStyles.muted}>{t("ipam.vrfStretch.empty")}</p>
          )}
        </section>
        </>
      ) : null}

      {tab === "instances" ? (
        <div className={prefixStyles.tableCard}>
          <p className={dcimStyles.muted} style={{ padding: "var(--space-3)", paddingBottom: 0 }}>
            {t("ipam.vrf.instanceIntro")}
          </p>
          {instQ.data && instQ.data.length > 0 ? (
            <div className={prefixStyles.tableScroll}>
              <table className={dcimStyles.table}>
                <thead>
                  <tr>
                    <th>{t("ipam.vrf.name")}</th>
                    <th>{t("ipam.vrf.instanceDevice")}</th>
                    <th>{t("ipam.vrf.instanceIntent")}</th>
                    <th>{t("ipam.vrf.effectiveRd")}</th>
                    <th>{t("ipam.ipv4.actionsCol")}</th>
                  </tr>
                </thead>
                <tbody>
                  {instQ.data.map((x) => (
                    <tr key={x.id}>
                      <td>{x.vrf_name}</td>
                      <td>{x.device_name}</td>
                      <td>
                        {x.intent === "intended" ? t("ipam.vrf.intentIntended") : t("ipam.vrf.intentRecorded")}
                      </td>
                      <td>{x.effective_rd ?? "—"}</td>
                      <td>
                        <button type="button" className={dcimStyles.btnLink} onClick={() => delInstM.mutate(x.id)}>
                          {t("dcim.common.delete")}
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className={dcimStyles.muted} style={{ padding: "var(--space-3)" }}>
              {t("ipam.vrf.instanceEmpty")}
            </p>
          )}
          <form
            className={dcimStyles.formRow}
            style={{ flexWrap: "wrap", padding: "var(--space-3)" }}
            onSubmit={(e) => {
              e.preventDefault();
              setErr(null);
              createInstM.mutate();
            }}
          >
            <label>
              VRF
              <select value={instVrf} onChange={(e) => setInstVrf(e.target.value)} required>
                <option value="">{t("ipam.vrf.chooseVrf")}</option>
                {(vrfsQ.data ?? []).map((v) => (
                  <option key={v.id} value={String(v.id)}>
                    {v.name}
                  </option>
                ))}
              </select>
            </label>
            <label>
              {t("ipam.vrf.instanceDevice")}
              <select value={instDevice} onChange={(e) => setInstDevice(e.target.value)} required>
                <option value="">{t("ipam.vrf.chooseDevice")}</option>
                {(devicesQ.data ?? [])
                  .filter((d) => {
                    if (!instVrf) return true;
                    const vrf = (vrfsQ.data ?? []).find((v) => v.id === Number(instVrf));
                    if (!vrf) return true;
                    const site = d.effective_site_id ?? d.site_id;
                    return site === vrf.site_id;
                  })
                  .map((d) => (
                    <option key={d.id} value={String(d.id)}>
                      {d.name}
                    </option>
                  ))}
              </select>
            </label>
            <label>
              {t("ipam.vrf.instanceIntent")}
              <select value={instIntent} onChange={(e) => setInstIntent(e.target.value)}>
                <option value="recorded">{t("ipam.vrf.intentRecorded")}</option>
                <option value="intended">{t("ipam.vrf.intentIntended")}</option>
              </select>
            </label>
            <label>
              {t("ipam.vrf.instanceRdOverride")}
              <input value={instRd} onChange={(e) => setInstRd(e.target.value)} placeholder={t("ipam.vrf.rdPlaceholder")} />
            </label>
            <button type="submit" className={dcimStyles.btn} disabled={createInstM.isPending || !instVrf || !instDevice}>
              {t("ipam.vrf.instanceAdd")}
            </button>
          </form>
        </div>
      ) : null}

      {tab === "targets" ? (
        <div className={prefixStyles.tableCard}>
          <p className={dcimStyles.muted} style={{ padding: "var(--space-3)", paddingBottom: 0 }}>
            {t("ipam.rt.intro")}
          </p>
          {rtQ.data && rtQ.data.length > 0 ? (
            <div className={prefixStyles.tableScroll}>
              <table className={dcimStyles.table}>
                <thead>
                  <tr>
                    <th>{t("ipam.rt.name")}</th>
                    <th>{t("ipam.rt.value")}</th>
                    <th>{t("ipam.ipv4.actionsCol")}</th>
                  </tr>
                </thead>
                <tbody>
                  {rtQ.data.map((x) => (
                    <tr key={x.id}>
                      <td>
                        {x.name}
                        <div className={dcimStyles.muted}>{x.slug}</div>
                      </td>
                      <td>{x.value}</td>
                      <td>
                        <button type="button" className={dcimStyles.btnLink} onClick={() => delRtM.mutate(x.id)}>
                          {t("dcim.common.delete")}
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className={dcimStyles.muted} style={{ padding: "var(--space-3)" }}>
              {t("ipam.rt.empty")}
            </p>
          )}
          <form
            className={dcimStyles.formRow}
            style={{ flexWrap: "wrap", padding: "var(--space-3)" }}
            onSubmit={(e) => {
              e.preventDefault();
              setErr(null);
              createRtM.mutate();
            }}
          >
            <label>
              {t("ipam.rt.name")}
              <input value={rtName} onChange={(e) => setRtName(e.target.value)} required />
            </label>
            <label>
              {t("ipam.detail.rangeSlug")}
              <input value={rtSlug} onChange={(e) => setRtSlug(e.target.value)} />
            </label>
            <label>
              {t("ipam.rt.value")}
              <input value={rtValue} onChange={(e) => setRtValue(e.target.value)} placeholder={t("ipam.vrf.rdPlaceholder")} required />
            </label>
            <button type="submit" className={dcimStyles.btn} disabled={createRtM.isPending || !rtName.trim() || !rtValue.trim()}>
              {t("ipam.rt.add")}
            </button>
          </form>
          <p className={dcimStyles.muted} style={{ padding: "0 var(--space-3)" }}>
            {t("ipam.rt.valueHelp")}
          </p>
          {(rtBindQ.data ?? []).length > 0 ? (
            <div className={prefixStyles.tableScroll}>
              <table className={dcimStyles.table}>
                <thead>
                  <tr>
                    <th>{t("ipam.vrf.name")}</th>
                    <th>{t("ipam.rt.value")}</th>
                    <th>{t("ipam.rt.direction")}</th>
                    <th>{t("ipam.ipv4.actionsCol")}</th>
                  </tr>
                </thead>
                <tbody>
                  {(rtBindQ.data ?? []).map((x) => (
                    <tr key={x.id}>
                      <td>{x.vrf_name}</td>
                      <td>
                        {x.value} ({x.route_target_name})
                      </td>
                      <td>{x.direction === "export" ? t("ipam.rt.export") : t("ipam.rt.import")}</td>
                      <td>
                        <button type="button" className={dcimStyles.btnLink} onClick={() => unbindRtM.mutate(x.id)}>
                          {t("dcim.common.delete")}
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className={dcimStyles.muted} style={{ padding: "var(--space-3)" }}>
              {t("ipam.rt.bindEmpty")}
            </p>
          )}
          <form
            className={dcimStyles.formRow}
            style={{ flexWrap: "wrap", padding: "var(--space-3)" }}
            onSubmit={(e) => {
              e.preventDefault();
              setErr(null);
              bindRtM.mutate();
            }}
          >
            <label>
              VRF
              <select value={bindVrf} onChange={(e) => setBindVrf(e.target.value)} required>
                <option value="">{t("ipam.vrf.chooseVrf")}</option>
                {(vrfsQ.data ?? []).map((v) => (
                  <option key={v.id} value={String(v.id)}>
                    {v.name}
                  </option>
                ))}
              </select>
            </label>
            <label>
              RT
              <select value={bindRt} onChange={(e) => setBindRt(e.target.value)} required>
                <option value="">{t("ipam.rt.choose")}</option>
                {(rtQ.data ?? []).map((r) => (
                  <option key={r.id} value={String(r.id)}>
                    {r.name} ({r.value})
                  </option>
                ))}
              </select>
            </label>
            <label>
              {t("ipam.rt.direction")}
              <select value={bindDir} onChange={(e) => setBindDir(e.target.value)}>
                <option value="import">{t("ipam.rt.import")}</option>
                <option value="export">{t("ipam.rt.export")}</option>
              </select>
            </label>
            <button type="submit" className={dcimStyles.btn} disabled={bindRtM.isPending || !bindVrf || !bindRt}>
              {t("ipam.rt.bind")}
            </button>
          </form>
        </div>
      ) : null}

      {tab === "as" ? (
        <>
          <div className={prefixStyles.tableCard}>
            {asQ.isLoading ? (
              <p className={dcimStyles.muted} style={{ padding: "var(--space-3)" }}>
                {t("dcim.common.loading")}
              </p>
            ) : null}
            {(asQ.data ?? []).length === 0 && !asQ.isLoading ? (
              <p className={dcimStyles.muted} style={{ padding: "var(--space-3)" }}>
                {t("ipam.as.empty")}
              </p>
            ) : null}
            {(asQ.data ?? []).length > 0 ? (
              <div className={prefixStyles.tableScroll}>
                <table className={dcimStyles.table}>
                  <thead>
                    <tr>
                      <th>ASN</th>
                      <th>{t("ipam.ipv4.name")}</th>
                      <th>{t("ipam.as.scope")}</th>
                      <th>{t("ipam.ipv4.actionsCol")}</th>
                    </tr>
                  </thead>
                  <tbody>
                    {(asQ.data ?? []).map((a) => (
                      <tr key={a.id}>
                        <td>{a.asn}</td>
                        <td>{a.name}</td>
                        <td>{a.is_private ? t("ipam.as.private") : t("ipam.as.public")}</td>
                        <td>
                          <button type="button" className={dcimStyles.btnLink} disabled={delAsM.isPending} onClick={() => delAsM.mutate(a.id)}>
                            {t("dcim.common.delete")}
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : null}
          </div>
          <section className={dcimStyles.mfrDetailSection} style={{ marginTop: "var(--space-3)" }}>
            <h3 className={dcimStyles.mfrDetailSectionTitle}>{t("ipam.as.assignments")}</h3>
            <p className={dcimStyles.muted}>{t("ipam.as.assignHint")}</p>
            <ul className={dcimStyles.ipList}>
              {(assignQ.data ?? []).map((x) => (
                <li key={x.id}>
                  AS{x.asn} {x.as_name} → {x.site_name}
                  {x.vrf_name ? ` / ${x.vrf_name}` : ""}{" "}
                  <button type="button" className={dcimStyles.btnLink} onClick={() => delAssignM.mutate(x.id)}>
                    {t("dcim.common.delete")}
                  </button>
                </li>
              ))}
            </ul>
            <form
              className={dcimStyles.formRow}
              style={{ flexWrap: "wrap" }}
              onSubmit={(e) => {
                e.preventDefault();
                setErr(null);
                createAssignM.mutate();
              }}
            >
              <label>
                AS
                <select value={assignAsId} onChange={(e) => setAssignAsId(e.target.value)} required>
                  <option value="">{t("ipam.as.chooseAs")}</option>
                  {(asQ.data ?? []).map((a) => (
                    <option key={a.id} value={String(a.id)}>
                      AS{a.asn} {a.name}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                {t("ipam.ipv4.site")}
                <select value={assignSite} onChange={(e) => setAssignSite(e.target.value)} required>
                  <option value="">{t("ipam.vrf.chooseSite")}</option>
                  {(sitesQ.data ?? []).map((s) => (
                    <option key={s.id} value={String(s.id)}>
                      {s.name}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                VRF
                <select value={assignVrf} onChange={(e) => setAssignVrf(e.target.value)}>
                  <option value="">{t("ipam.vlan.noVrf")}</option>
                  {assignVrfs.map((v) => (
                    <option key={v.id} value={String(v.id)}>
                      {v.name}
                    </option>
                  ))}
                </select>
              </label>
              <button type="submit" className={dcimStyles.btn} disabled={createAssignM.isPending}>
                {t("ipam.as.assign")}
              </button>
            </form>
          </section>
        </>
      ) : null}

      {tab === "bgp" ? (
        <>
        <section className={dcimStyles.mfrDetailSection} style={{ marginTop: 0 }}>
          <h3 className={dcimStyles.mfrDetailSectionTitle}>{t("ipam.bgp.instanceTitle")}</h3>
          <p className={dcimStyles.muted}>{t("ipam.bgp.instanceHint")}</p>
          <form
            className={dcimStyles.formRow}
            onSubmit={(e) => {
              e.preventDefault();
              setErr(null);
              createBiM.mutate();
            }}
          >
            <label>
              {t("dcim.common.name")}
              <input value={biName} onChange={(e) => setBiName(e.target.value)} />
            </label>
            <label>
              {t("ipam.vrf.chooseDevice")}
              <select value={biDevice} onChange={(e) => setBiDevice(e.target.value)} required>
                <option value="">{t("ipam.vrf.chooseDevice")}</option>
                {(devicesQ.data ?? []).map((d) => (
                  <option key={d.id} value={String(d.id)}>
                    {d.name}
                  </option>
                ))}
              </select>
            </label>
            <label>
              {t("ipam.bgp.localAs")}
              <select value={biAs} onChange={(e) => setBiAs(e.target.value)} required>
                <option value="">{t("ipam.as.chooseAs")}</option>
                {(asQ.data ?? []).map((a) => (
                  <option key={a.id} value={String(a.id)}>
                    AS{a.asn} {a.name}
                  </option>
                ))}
              </select>
            </label>
            <label>
              VRF
              <select value={biVrf} onChange={(e) => setBiVrf(e.target.value)}>
                <option value="">{t("ipam.vlan.noVrf")}</option>
                {(vrfsQ.data ?? []).map((v) => (
                  <option key={v.id} value={String(v.id)}>
                    {v.name}
                  </option>
                ))}
              </select>
            </label>
            <label>
              {t("ipam.vrf.instanceIntent")}
              <select value={biIntent} onChange={(e) => setBiIntent(e.target.value)}>
                <option value="recorded">{t("ipam.vrf.intentRecorded")}</option>
                <option value="intended">{t("ipam.vrf.intentIntended")}</option>
              </select>
            </label>
            <label>
              {t("ipam.bgp.routerId")}
              <input value={biRouterId} onChange={(e) => setBiRouterId(e.target.value)} placeholder="192.0.2.1" />
            </label>
            <button type="submit" className={dcimStyles.btn} disabled={createBiM.isPending || biDevice === "" || biAs === ""}>
              {t("ipam.bgp.instanceAdd")}
            </button>
          </form>
          <p className={dcimStyles.muted}>{t("ipam.bgp.routerIdHelp")}</p>
          {(bgpInstQ.data ?? []).length > 0 ? (
            <ul className={dcimStyles.ipList}>
              {(bgpInstQ.data ?? []).map((i) => (
                <li key={i.id}>
                  {i.name} <code>{i.slug}</code>
                  {i.device_name ? ` · ${i.device_name}` : ""}
                  {i.local_asn != null ? ` · AS${i.local_asn}` : ""}
                  {i.vrf_name ? ` · ${i.vrf_name}` : ""}
                  {i.router_id ? ` · ${i.router_id}` : ""}{" "}
                  <button type="button" className={dcimStyles.btnLink} disabled={delBiM.isPending} onClick={() => delBiM.mutate(i.id)}>
                    {t("dcim.common.delete")}
                  </button>
                </li>
              ))}
            </ul>
          ) : (
            !bgpInstQ.isLoading && <p className={dcimStyles.muted}>{t("ipam.bgp.instanceEmpty")}</p>
          )}
        </section>
        <div className={prefixStyles.tableCard}>
          {bgpQ.isLoading ? (
            <p className={dcimStyles.muted} style={{ padding: "var(--space-3)" }}>
              {t("dcim.common.loading")}
            </p>
          ) : null}
          {(bgpQ.data ?? []).length === 0 && !bgpQ.isLoading ? (
            <p className={dcimStyles.muted} style={{ padding: "var(--space-3)" }}>
              {t("ipam.bgp.empty")}
            </p>
          ) : null}
          {(bgpQ.data ?? []).length > 0 ? (
            <div className={prefixStyles.tableScroll}>
              <table className={dcimStyles.table}>
                <thead>
                  <tr>
                    <th>{t("ipam.ipv4.name")}</th>
                    <th>{t("ipam.ipv4.site")}</th>
                    <th>{t("ipam.bgp.localAs")}</th>
                    <th>{t("ipam.bgp.remoteAs")}</th>
                    <th>{t("ipam.bgp.peerIp")}</th>
                    <th>{t("ipam.bgp.families")}</th>
                    <th>{t("ipam.bgp.desired")}</th>
                    <th>{t("ipam.bgp.observed")}</th>
                    <th>{t("ipam.ipv4.actionsCol")}</th>
                  </tr>
                </thead>
                <tbody>
                  {(bgpQ.data ?? []).map((s) => (
                    <tr key={s.id}>
                      <td>{s.name}</td>
                      <td>{siteNameById.get(s.site_id) ?? s.site_id}</td>
                      <td>{asNameById.get(s.local_as_id) ?? s.local_as_id}</td>
                      <td>{s.remote_asn}</td>
                      <td>{s.peer_ip}</td>
                      <td>{(s.address_families ?? []).join(", ")}</td>
                      <td>{s.desired_status}</td>
                      <td>{s.observed_status ?? t("ipam.bgp.unobserved")}</td>
                      <td>
                        <button type="button" className={dcimStyles.btnLink} disabled={delBgpM.isPending} onClick={() => delBgpM.mutate(s.id)}>
                          {t("dcim.common.delete")}
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : null}
        </div>
        </>
      ) : null}

      <PrefixDrawer
        title={t("ipam.vrf.addTitle")}
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
              {createM.isPending ? t("dcim.common.creating") : t("ipam.vrf.create")}
            </button>
          </>
        }
      >
        <div className={prefixStyles.drawerFields}>
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
            <span className={dcimStyles.muted}>{t("ipam.vrf.rdHelp")}</span>
          </label>
        </div>
      </PrefixDrawer>

      <PrefixDrawer
        title={t("ipam.as.addTitle")}
        open={asDrawer}
        onClose={() => {
          if (!createAsM.isPending) setAsDrawer(false);
        }}
        footer={
          <>
            <button type="button" className={dcimStyles.btn} disabled={createAsM.isPending} onClick={() => setAsDrawer(false)}>
              {t("dcim.common.cancel")}
            </button>
            <button
              type="button"
              className={dcimStyles.btn}
              disabled={createAsM.isPending}
              onClick={() => {
                setErr(null);
                createAsM.mutate();
              }}
            >
              {createAsM.isPending ? t("dcim.common.creating") : t("ipam.as.create")}
            </button>
          </>
        }
      >
        <div className={prefixStyles.drawerFields}>
          <p className={dcimStyles.muted}>{t("ipam.as.hint")}</p>
          <label>
            ASN
            <input type="number" min={1} value={asAsn} onChange={(e) => setAsAsn(e.target.value)} required />
          </label>
          <label>
            {t("ipam.ipv4.name")}
            <input value={asName} onChange={(e) => setAsName(e.target.value)} required />
          </label>
          <label>
            {t("ipam.circuits.tenant")}
            <select value={asTenant} onChange={(e) => setAsTenant(e.target.value)}>
              <option value="">{t("ipam.circuits.noTenant")}</option>
              {(tenantsQ.data ?? []).map((tn) => (
                <option key={tn.id} value={String(tn.id)}>
                  {tn.name}
                </option>
              ))}
            </select>
          </label>
        </div>
      </PrefixDrawer>

      <PrefixDrawer
        title={t("ipam.bgp.addTitle")}
        open={bgpDrawer}
        onClose={() => {
          if (!createBgpM.isPending) setBgpDrawer(false);
        }}
        footer={
          <>
            <button type="button" className={dcimStyles.btn} disabled={createBgpM.isPending} onClick={() => setBgpDrawer(false)}>
              {t("dcim.common.cancel")}
            </button>
            <button
              type="button"
              className={dcimStyles.btn}
              disabled={createBgpM.isPending}
              onClick={() => {
                setErr(null);
                createBgpM.mutate();
              }}
            >
              {createBgpM.isPending ? t("dcim.common.creating") : t("ipam.bgp.create")}
            </button>
          </>
        }
      >
        <div className={prefixStyles.drawerFields}>
          <p className={dcimStyles.muted}>{t("ipam.bgp.hint")}</p>
          <label>
            {t("ipam.bgp.instancePick")}
            <select
              value={bgpInst}
              onChange={(e) => {
                setBgpInst(e.target.value);
              }}
            >
              <option value="">{t("ipam.bgp.instanceChoose")}</option>
              {(bgpInstQ.data ?? []).map((i) => (
                <option key={i.id} value={String(i.id)}>
                  {i.name}
                </option>
              ))}
            </select>
          </label>
          <label>
            {t("ipam.ipv4.site")}
            <select value={bgpSite} onChange={(e) => setBgpSite(e.target.value)} required>
              <option value="">{t("ipam.vrf.chooseSite")}</option>
              {(sitesQ.data ?? []).map((s) => (
                <option key={s.id} value={String(s.id)}>
                  {s.name}
                </option>
              ))}
            </select>
          </label>
          <label>
            {t("ipam.bgp.localAs")}
            <select value={bgpLocalAs} onChange={(e) => setBgpLocalAs(e.target.value)} required>
              <option value="">{t("ipam.as.chooseAs")}</option>
              {(asQ.data ?? []).map((a) => (
                <option key={a.id} value={String(a.id)}>
                  AS{a.asn} {a.name}
                </option>
              ))}
            </select>
          </label>
          <label>
            {t("ipam.bgp.remoteAs")}
            <input type="number" min={1} value={bgpRemoteAsn} onChange={(e) => setBgpRemoteAsn(e.target.value)} required />
          </label>
          <label>
            {t("ipam.bgp.peerIp")}
            <input value={bgpPeer} onChange={(e) => setBgpPeer(e.target.value)} required />
          </label>
          <label>
            VRF
            <select value={bgpVrf} onChange={(e) => setBgpVrf(e.target.value)}>
              <option value="">{t("ipam.vlan.noVrf")}</option>
              {bgpVrfs.map((v) => (
                <option key={v.id} value={String(v.id)}>
                  {v.name}
                </option>
              ))}
            </select>
          </label>
          <label>
            {t("ipam.ipv4.name")}
            <input value={bgpName} onChange={(e) => setBgpName(e.target.value)} />
          </label>
          <label className={prefixStyles.drawerCheck}>
            <input type="checkbox" checked={bgpV6} onChange={(e) => setBgpV6(e.target.checked)} />
            {t("ipam.bgp.alsoV6")}
          </label>
        </div>
      </PrefixDrawer>
    </Panel>
  );
}
