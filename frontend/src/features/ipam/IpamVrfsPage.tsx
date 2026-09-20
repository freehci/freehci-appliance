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

const TABS = new Set(["vrfs", "as", "bgp"]);

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
  const [bgpDrawer, setBgpDrawer] = useState(false);

  const siteIdFilter = filterSite === "" ? undefined : Number(filterSite);
  const sitesQ = useQuery({ queryKey: ["dcim", "sites"], queryFn: dcimApi.listSites });
  const tenantsQ = useQuery({ queryKey: ["tenants"], queryFn: dcimApi.listTenants });
  const vrfsQ = useQuery({
    queryKey: ["ipam", "vrfs", siteIdFilter ?? "all"],
    queryFn: () => ipamApi.listIpamVrfs(siteIdFilter),
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
        site_id: Number(bgpSite),
        local_as_id: Number(bgpLocalAs),
        remote_asn: Number(bgpRemoteAsn),
        peer_ip: bgpPeer.trim(),
        vrf_id: bgpVrf === "" ? null : Number(bgpVrf),
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

  const delBgpM = useMutation({
    mutationFn: (id: number) => ipamApi.deleteBgpSession(id),
    onSuccess: () => {
      setErr(null);
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
      </header>
      <DcimInnerTabs
        ariaLabel={t("ipam.routing.tabs")}
        activeId={tab}
        onChange={setTab}
        tabs={[
          { id: "vrfs", label: t("ipam.routing.tabVrfs") },
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
