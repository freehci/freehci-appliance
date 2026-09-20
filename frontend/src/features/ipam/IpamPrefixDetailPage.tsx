import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useMemo, useState } from "react";
import { Link, useParams, useSearchParams } from "react-router-dom";
import { ConfirmModal } from "@/components/ui/ConfirmModal";
import { DcimInnerTabs } from "@/features/dcim/DcimInnerTabs";
import * as dcimApi from "@/features/dcim/dcimApi";
import dcimStyles from "@/features/dcim/dcim.module.css";
import { useI18n } from "@/i18n/I18nProvider";
import { ApiError } from "@/lib/api";
import * as ipamApi from "./ipamApi";
import { IpamIpRequestModal } from "./IpamIpRequestModal";
import styles from "./prefixDetail.module.css";
import { intToIpv4, parseIpv4Cidr } from "./ipv4PrefixTree";
import {
  PrefixDrawer,
  PrefixStatusBadge,
  prefixUsage,
  readSubnetServices,
} from "./prefixPageUi";
import prefixStyles from "./prefixPage.module.css";
import { PREFIX_ROLES, PREFIX_STATUSES, type PrefixAddressGridRow } from "./types";

const PAGE_SIZES = [25, 50, 100] as const;
const TABS = new Set(["overview", "addresses", "scanning", "services", "history"]);

function isGridRowFree(row: PrefixAddressGridRow): boolean {
  if (row.assignment != null) return false;
  const inv = row.inventory;
  if (inv == null) return true;
  return inv.status === "discovered";
}

function formatWhen(iso: string | null | undefined): string {
  if (!iso) return "—";
  const d = new Date(iso);
  return Number.isNaN(d.getTime()) ? iso : d.toLocaleString();
}

function prefixLenToMask(len: number): string {
  if (len <= 0) return "0.0.0.0";
  if (len >= 32) return "255.255.255.255";
  return intToIpv4((0xffffffff << (32 - len)) >>> 0);
}

function pageWindow(current: number, total: number): number[] {
  if (total <= 7) return Array.from({ length: total }, (_, i) => i);
  const start = Math.max(0, Math.min(current - 2, total - 5));
  const end = Math.min(total, start + 5);
  return Array.from({ length: end - start }, (_, i) => start + i);
}

function isGridTooLarge(err: unknown): boolean {
  return err instanceof ApiError && err.status === 400 && /prefix_too_large|available-ranges/i.test(err.message);
}

export function IpamPrefixDetailPage() {
  const { t } = useI18n();
  const qc = useQueryClient();
  const { prefixId } = useParams<{ prefixId: string }>();
  const id = Number(prefixId);
  const [searchParams, setSearchParams] = useSearchParams();
  const tabParam = searchParams.get("tab");
  const tab = tabParam != null && TABS.has(tabParam) ? tabParam : "addresses";
  const setTab = (next: string) => {
    setSearchParams(
      (prev) => {
        const n = new URLSearchParams(prev);
        if (next === "addresses") n.delete("tab");
        else n.set("tab", next);
        return n;
      },
      { replace: true },
    );
  };

  const [err, setErr] = useState<string | null>(null);
  const [q, setQ] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [roleFilter, setRoleFilter] = useState("");
  const [page, setPage] = useState(0);
  const [pageSize, setPageSize] = useState(50);
  const [editOpen, setEditOpen] = useState(false);
  const [editName, setEditName] = useState("");
  const [editRole, setEditRole] = useState("active");
  const [editStatus, setEditStatus] = useState("active");
  const [editVlan, setEditVlan] = useState("");
  const [editVrf, setEditVrf] = useState("");
  const [svcGateway, setSvcGateway] = useState("");
  const [svcDns, setSvcDns] = useState("");
  const [svcDhcp, setSvcDhcp] = useState("");
  const [requestOpen, setRequestOpen] = useState(false);
  const [requestPreferred, setRequestPreferred] = useState<string | undefined>(undefined);
  const [releaseRow, setReleaseRow] = useState<PrefixAddressGridRow | null>(null);

  const exploreQ = useQuery({
    queryKey: ["ipam", "explore", id],
    queryFn: () => ipamApi.getIpv4PrefixExplore(id),
    enabled: Number.isFinite(id) && id > 0,
  });
  const gridQ = useQuery({
    queryKey: ["ipam", "address-grid", id],
    queryFn: () => ipamApi.getPrefixAddressGrid(id),
    enabled: Number.isFinite(id) && id > 0,
    retry: false,
    refetchInterval: (query) => {
      const st = query.state.data?.active_scan?.status;
      return st === "pending" || st === "running" ? 1500 : false;
    },
  });
  const rangesQ = useQuery({
    queryKey: ["ipam", "available-ranges", id],
    queryFn: () => ipamApi.getAvailableRanges(id),
    enabled: Number.isFinite(id) && id > 0 && isGridTooLarge(gridQ.error),
  });
  const scansQ = useQuery({
    queryKey: ["ipam", "subnet-scans", id],
    queryFn: () => ipamApi.listSubnetScans({ ipv4_prefix_id: id, limit: 25 }),
    enabled: Number.isFinite(id) && id > 0,
  });
  const driftQ = useQuery({
    queryKey: ["ipam", "prefix-drift", id],
    queryFn: () => ipamApi.getPrefixDrift(id),
    enabled: Number.isFinite(id) && id > 0,
  });
  const sitesQ = useQuery({ queryKey: ["dcim", "sites"], queryFn: dcimApi.listSites });
  const vlansQ = useQuery({ queryKey: ["ipam", "vlans", "all-for-prefixes"], queryFn: () => ipamApi.listIpamVlans() });
  const vrfsQ = useQuery({ queryKey: ["ipam", "vrfs", "all-for-prefixes"], queryFn: () => ipamApi.listIpamVrfs() });
  const usersQ = useQuery({ queryKey: ["ipam", "users"], queryFn: () => ipamApi.listUsers() });
  const devicesQ = useQuery({ queryKey: ["dcim", "devices"], queryFn: dcimApi.listDevices });
  const prefix = exploreQ.data?.prefix;
  const auditQ = useQuery({
    queryKey: ["ipam", "audit", prefix?.site_id],
    queryFn: () => ipamApi.listIpamAudit({ site_id: prefix!.site_id, limit: 80 }),
    enabled: prefix != null,
  });

  useEffect(() => {
    setPage(0);
  }, [q, statusFilter, roleFilter, pageSize, id]);

  useEffect(() => {
    if (!prefix) return;
    setEditName(prefix.name);
    setEditRole(prefix.role || "active");
    setEditStatus(prefix.status || "active");
    setEditVlan(prefix.vlan_id != null ? String(prefix.vlan_id) : "");
    setEditVrf(prefix.vrf_id != null ? String(prefix.vrf_id) : "");
    const svc = readSubnetServices(prefix.subnet_services);
    setSvcGateway(svc.gateway ?? "");
    setSvcDns(svc.dns.join(", "));
    setSvcDhcp(svc.dhcp ?? "");
  }, [prefix]);

  const site = (sitesQ.data ?? []).find((s) => s.id === prefix?.site_id);
  const vlan = (vlansQ.data ?? []).find((v) => v.id === prefix?.vlan_id);
  const vrf = (vrfsQ.data ?? []).find((v) => v.id === prefix?.vrf_id);
  const svc = readSubnetServices(prefix?.subnet_services);
  const usage = prefix ? prefixUsage(prefix) : { used: 0, total: 0, pct: 0 };
  const parsed = prefix ? parseIpv4Cidr(prefix.cidr) : null;
  const network = parsed ? intToIpv4(parsed.first) : null;
  const broadcast = parsed && parsed.prefixLen < 31 ? intToIpv4(parsed.last) : null;
  const mask = parsed ? `${prefixLenToMask(parsed.prefixLen)} · /${parsed.prefixLen}` : null;
  const deviceNameById = useMemo(() => {
    const m = new Map<number, string>();
    for (const d of devicesQ.data ?? []) m.set(d.id, d.name);
    return m;
  }, [devicesQ.data]);
  const lastScan = scansQ.data?.[0] ?? gridQ.data?.active_scan ?? null;
  const scanRunning = lastScan?.status === "pending" || lastScan?.status === "running";
  const rows = gridQ.data?.rows ?? [];
  const filtered = useMemo(() => {
    const needle = q.trim().toLowerCase();
    return rows.filter((row) => {
      const inv = row.inventory;
      if (statusFilter) {
        const live = row.scan_ping_responded === true ? "up" : row.scan_ping_responded === false ? "down" : inv?.status ?? "";
        if (statusFilter === "up" && live !== "up") return false;
        if (statusFilter === "down" && live !== "down") return false;
        if (statusFilter !== "up" && statusFilter !== "down" && inv?.status !== statusFilter) return false;
      }
      if (roleFilter) {
        const role = inv?.role || row.address_role || "";
        if (role !== roleFilter) return false;
      }
      if (!needle) return true;
      const hay = [
        row.address,
        row.scan_mac,
        inv?.mac_address,
        inv?.note,
        inv?.role,
        inv?.hostname,
        row.assignment?.device_name,
        row.assignment?.interface_name,
      ]
        .filter(Boolean)
        .join(" ")
        .toLowerCase();
      return hay.includes(needle);
    });
  }, [rows, q, statusFilter, roleFilter]);
  const pageCount = Math.max(1, Math.ceil(filtered.length / pageSize));
  const safePage = Math.min(page, pageCount - 1);
  const pageRows = filtered.slice(safePage * pageSize, safePage * pageSize + pageSize);

  const invalidate = () => {
    void qc.invalidateQueries({ queryKey: ["ipam", "explore", id] });
    void qc.invalidateQueries({ queryKey: ["ipam", "address-grid", id] });
    void qc.invalidateQueries({ queryKey: ["ipam", "ipv4-prefixes"] });
    void qc.invalidateQueries({ queryKey: ["ipam", "subnet-scans", id] });
    void qc.invalidateQueries({ queryKey: ["ipam", "prefix-drift", id] });
  };

  const scanM = useMutation({
    mutationFn: () => ipamApi.createSubnetScan(id),
    onSuccess: () => {
      setErr(null);
      invalidate();
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });
  const saveEdit = useMutation({
    mutationFn: () =>
      ipamApi.updateIpv4Prefix(id, {
        name: editName.trim(),
        role: editRole,
        status: editStatus,
        vlan_id: editVlan === "" ? null : Number(editVlan),
        vrf_id: editVrf === "" ? null : Number(editVrf),
      }),
    onSuccess: () => {
      setEditOpen(false);
      invalidate();
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });
  const saveSvc = useMutation({
    mutationFn: () =>
      ipamApi.updateIpv4Prefix(id, {
        subnet_services: {
          gateway: svcGateway.trim() || null,
          dns: svcDns.trim() || null,
          dhcp_server: svcDhcp.trim() || null,
        },
      }),
    onSuccess: invalidate,
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });
  const patchAddr = useMutation({
    mutationFn: (args: { id: number; body: { owner_user_id?: number | null; note?: string | null; status?: string } }) =>
      ipamApi.patchIpv4Address(args.id, args.body),
    onSuccess: invalidate,
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });
  const reserveOne = useMutation({
    mutationFn: async (address: string) => {
      const row = rows.find((r) => r.address === address);
      if (row?.inventory) {
        await ipamApi.patchIpv4Address(row.inventory.id, { status: "reserved" });
        return;
      }
      const inv = await ipamApi.ensureIpv4Address({ ipv4_prefix_id: id, address });
      await ipamApi.patchIpv4Address(inv.id, { status: "reserved" });
    },
    onSuccess: invalidate,
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });
  const releaseM = useMutation({
    mutationFn: (addrId: number) => ipamApi.releaseIpv4Address(addrId),
    onSuccess: () => {
      setReleaseRow(null);
      invalidate();
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const exportYaml = () => {
    if (!prefix) return;
    void ipamApi.exportSiteIpam(prefix.site_id, "yaml").then((text) => {
      const blob = new Blob([text], { type: "text/yaml" });
      const a = document.createElement("a");
      a.href = URL.createObjectURL(blob);
      a.download = `${site?.slug ?? "site"}-ipam.yaml`;
      a.click();
      URL.revokeObjectURL(a.href);
    });
  };

  if (!Number.isFinite(id) || id < 1) {
    return <p className={styles.err}>{t("ipam.detail.notFound")}</p>;
  }

  const freeCount = Math.max(0, usage.total - usage.used);
  const scanDenom = Math.max(usage.total, lastScan?.hosts_scanned ?? 0);
  const scanPct =
    lastScan?.status === "completed"
      ? 100
      : scanRunning && scanDenom > 0
        ? Math.min(99, Math.round((100 * (lastScan?.hosts_scanned ?? 0)) / scanDenom))
        : 0;
  const vlanOptions = (vlansQ.data ?? []).filter((v) => v.site_id === prefix?.site_id);
  const vrfOptions = (vrfsQ.data ?? []).filter((v) => v.site_id === prefix?.site_id);
  const history = (auditQ.data ?? []).filter((ev) => {
    if (ev.resource_id === id) return true;
    const cidr = prefix?.cidr;
    return cidr != null && JSON.stringify(ev.detail ?? {}).includes(cidr);
  });

  return (
    <div className={styles.page}>
      <p className={styles.crumb}>
        <Link to="/ipam/prefixes">{t("ipam.ipv4.crumbIpam")}</Link>
        <span className={styles.crumbSep}>/</span>
        <Link to="/ipam/prefixes">{t("ipam.ipv4.title")}</Link>
        <span className={styles.crumbSep}>/</span>
        <span>{prefix?.cidr ?? `#${id}`}</span>
      </p>

      <header className={styles.head}>
        <div>
          <h1 className={styles.title}>{t("ipam.detail.title")}</h1>
          <p className={styles.intro}>{t("ipam.detail.intro")}</p>
        </div>
        <div className={styles.actions}>
          <button type="button" className={styles.toolBtn} onClick={() => setEditOpen(true)} disabled={!prefix}>
            <i className="fas fa-pen" aria-hidden />
            {t("ipam.ipv4.edit")}
          </button>
          <button type="button" className={styles.toolBtn} onClick={exportYaml} disabled={!prefix}>
            <i className="fas fa-download" aria-hidden />
            {t("ipam.ipv4.export")}
          </button>
          <button type="button" className={styles.toolBtn} onClick={() => scanM.mutate()} disabled={scanM.isPending || scanRunning}>
            <i className="fas fa-satellite-dish" aria-hidden />
            {t("ipam.detail.scanAction")}
          </button>
          <button
            type="button"
            className={styles.btnPrimary}
            onClick={() => {
              setRequestPreferred(undefined);
              setRequestOpen(true);
            }}
          >
            <i className="fas fa-plus" aria-hidden />
            {t("ipam.detail.newObject")}
          </button>
        </div>
      </header>

      {err ? <p className={styles.err}>{err}</p> : null}
      {exploreQ.isError ? <p className={styles.err}>{(exploreQ.error as Error).message}</p> : null}

      {prefix ? (
        <section className={styles.identity}>
          <div className={styles.identityMain}>
            <span className={styles.identityIcon} aria-hidden>
              <i className="fas fa-sitemap" />
            </span>
            <div>
              <div className={styles.cidrRow}>
                <p className={styles.cidr}>{prefix.cidr}</p>
                <PrefixStatusBadge status={prefix.status || "active"} />
              </div>
              <p className={styles.identityMeta}>
                {prefix.name}
                {site ? ` · ${site.name}` : ""}
                {prefix.overlap_policy ? ` · ${prefix.overlap_policy}` : ""}
              </p>
            </div>
          </div>
          <div className={styles.identityRight}>
            <div>
              {t("ipam.detail.utilLine", { used: String(usage.used), free: String(freeCount), missing: String(driftQ.data?.reserved_missing.length ?? 0) })}
            </div>
            <div>
              {t("ipam.detail.created")}: {formatWhen(prefix.created_at)}
            </div>
            <div>
              {t("ipam.detail.updated")}: {formatWhen(prefix.updated_at)}
            </div>
          </div>
        </section>
      ) : exploreQ.isLoading ? (
        <p className={styles.muted}>{t("dcim.common.loading")}</p>
      ) : null}

      {prefix ? (
        <section className={styles.kpis}>
          <div className={styles.kpi}>
            <i className={`fas fa-chart-pie ${styles.kpiIcon}`} aria-hidden />
            <div>
              <p className={styles.kpiLabel}>{t("ipam.detail.kpiAddresses")}</p>
              <p className={styles.kpiValue}>{usage.total}</p>
              <p className={styles.kpiMeta}>
                {usage.used} {t("ipam.detail.used")} ({Math.round(usage.pct)}%)
              </p>
              <div className={styles.kpiBar} aria-hidden>
                <div className={styles.kpiBarFill} style={{ width: `${Math.max(0, Math.min(100, usage.pct))}%` }} />
              </div>
            </div>
          </div>
          <div className={styles.kpi}>
            <i className={`fas fa-location-dot ${styles.kpiIcon}`} aria-hidden />
            <div>
              <p className={styles.kpiLabel}>{t("ipam.ipv4.site")}</p>
              <p className={styles.kpiValue}>{site?.name ?? `#${prefix.site_id}`}</p>
              <p className={styles.kpiMeta}>{prefix.overlap_policy || "—"}</p>
            </div>
          </div>
          <div className={styles.kpi}>
            <i className={`fas fa-layer-group ${styles.kpiIcon}`} aria-hidden />
            <div>
              <p className={styles.kpiLabel}>VRF</p>
              <p className={styles.kpiValue}>{vrf?.name ?? "—"}</p>
              <p className={styles.kpiMeta}>{vrf ? vrf.slug : t("ipam.detail.notSet")}</p>
            </div>
          </div>
          <div className={styles.kpi}>
            <i className={`fas fa-network-wired ${styles.kpiIcon}`} aria-hidden />
            <div>
              <p className={styles.kpiLabel}>VLAN</p>
              <p className={styles.kpiValue}>{vlan ? `${vlan.vid}` : "—"}</p>
              <p className={styles.kpiMeta}>{vlan?.name ?? t("ipam.detail.notSet")}</p>
            </div>
          </div>
          <div className={styles.kpi}>
            <i className={`fas fa-route ${styles.kpiIcon}`} aria-hidden />
            <div>
              <p className={styles.kpiLabel}>{t("ipam.detail.kpiGateway")}</p>
              <p className={styles.kpiValue}>{svc.gateway ?? "—"}</p>
              <p className={styles.kpiMeta}>
                {svc.gateway ? (
                  <>
                    <span className={`${styles.dot} ${styles.dotOk}`} />
                    {t("ipam.detail.configured")}
                  </>
                ) : (
                  t("ipam.detail.notSet")
                )}
              </p>
            </div>
          </div>
          <div className={styles.kpi}>
            <i className={`fas fa-server ${styles.kpiIcon}`} aria-hidden />
            <div>
              <p className={styles.kpiLabel}>DHCP</p>
              <p className={styles.kpiValue}>{svc.dhcp ?? "—"}</p>
              <p className={styles.kpiMeta}>
                {svc.dhcp ? (
                  <>
                    <span className={`${styles.dot} ${styles.dotOk}`} />
                    {t("ipam.detail.configured")}
                  </>
                ) : (
                  t("ipam.detail.notSet")
                )}
              </p>
            </div>
          </div>
          <div className={styles.kpi}>
            <i className={`fas fa-globe ${styles.kpiIcon}`} aria-hidden />
            <div>
              <p className={styles.kpiLabel}>DNS</p>
              <p className={styles.kpiValue}>{svc.dns[0] ?? "—"}</p>
              <p className={styles.kpiMeta}>
                {svc.dns.length > 1 ? svc.dns.slice(1).join(", ") : svc.dns.length ? t("ipam.detail.configured") : t("ipam.detail.notSet")}
              </p>
            </div>
          </div>
        </section>
      ) : null}

      <DcimInnerTabs
        ariaLabel={t("ipam.detail.tabs")}
        activeId={tab}
        onChange={setTab}
        tabs={[
          { id: "overview", label: t("ipam.detail.tabOverview") },
          { id: "addresses", label: t("ipam.detail.tabAddresses") },
          { id: "scanning", label: t("ipam.detail.tabScanning") },
          { id: "services", label: t("ipam.detail.tabServices") },
          { id: "history", label: t("ipam.detail.tabHistory") },
        ]}
      />

      <div className={styles.body}>
        <section className={styles.main}>
          {tab === "overview" ? (
            <div className={styles.panelPad}>
              {prefix?.description ? <p>{prefix.description}</p> : null}
              <h2 className={styles.mainTitle}>{t("ipam.ipv4.childPrefixes")}</h2>
              {(exploreQ.data?.child_prefixes ?? []).length ? (
                <ul>
                  {(exploreQ.data?.child_prefixes ?? []).map((c) => (
                    <li key={c.id}>
                      <Link to={`/ipam/prefixes/${c.id}`}>
                        {c.name} <code>{c.cidr}</code>
                      </Link>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className={styles.muted}>{t("ipam.ipv4.noChildPrefixes")}</p>
              )}
              <h2 className={styles.mainTitle} style={{ marginTop: "1.25rem" }}>
                {t("ipam.detail.assignments")}
              </h2>
              {(exploreQ.data?.assignments ?? []).length ? (
                <table className={styles.table}>
                  <thead>
                    <tr>
                      <th>{t("ipam.ipv4.colAddress")}</th>
                      <th>{t("ipam.ipv4.colDevice")}</th>
                      <th>{t("ipam.ipv4.colInterface")}</th>
                    </tr>
                  </thead>
                  <tbody>
                    {(exploreQ.data?.assignments ?? []).map((a) => (
                      <tr key={a.assignment_id}>
                        <td>
                          <code>{a.address}</code>
                        </td>
                        <td>
                          <Link to={`/dcim/equipment/devices/${a.device_id}`}>{a.device_name}</Link>
                        </td>
                        <td>{a.interface_name}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              ) : (
                <p className={styles.muted}>{t("ipam.detail.noAssignments")}</p>
              )}
            </div>
          ) : null}

          {tab === "addresses" ? (
            <>
              <div className={styles.mainHead}>
                <div>
                  <h2 className={styles.mainTitle}>
                    {t("ipam.detail.addressTitle")} ({filtered.length}/{usage.total || rows.length})
                  </h2>
                  <p className={styles.mainHint}>{t("ipam.detail.addressHint")}</p>
                </div>
              </div>
              <div className={styles.filters}>
                <input
                  value={q}
                  onChange={(e) => setQ(e.target.value)}
                  placeholder={t("ipam.detail.searchAddresses")}
                />
                <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
                  <option value="">{t("ipam.detail.filterAllStatus")}</option>
                  <option value="up">{t("ipam.detail.statusUp")}</option>
                  <option value="down">{t("ipam.detail.statusDown")}</option>
                  <option value="reserved">reserved</option>
                  <option value="assigned">assigned</option>
                  <option value="discovered">discovered</option>
                </select>
                <select value={roleFilter} onChange={(e) => setRoleFilter(e.target.value)}>
                  <option value="">{t("ipam.detail.filterAllRoles")}</option>
                  <option value="gateway">gateway</option>
                  <option value="host">host</option>
                  <option value="dhcp">dhcp</option>
                  <option value="vip">vip</option>
                  <option value="network">network</option>
                  <option value="broadcast">broadcast</option>
                </select>
                <select value={String(pageSize)} onChange={(e) => setPageSize(Number(e.target.value))}>
                  {PAGE_SIZES.map((n) => (
                    <option key={n} value={n}>
                      {n} {t("ipam.grid.pagination.perPage")}
                    </option>
                  ))}
                </select>
                <button
                  type="button"
                  className={dcimStyles.btn}
                  onClick={() => {
                    setQ("");
                    setStatusFilter("");
                    setRoleFilter("");
                  }}
                >
                  {t("ipam.ipv4.resetFilters")}
                </button>
              </div>
              {gridQ.isLoading ? <p className={styles.muted} style={{ padding: "0 var(--space-4)" }}>{t("dcim.common.loading")}</p> : null}
              {isGridTooLarge(gridQ.error) ? (
                <p className={styles.muted} style={{ padding: "0 var(--space-4) var(--space-3)" }}>
                  {t("ipam.detail.gridTooLarge")}
                  {rangesQ.data ? ` ${rangesQ.data.used_count} ${t("ipam.detail.used")}.` : ""}
                </p>
              ) : gridQ.isError ? (
                <p className={styles.err} style={{ padding: "0 var(--space-4) var(--space-3)" }}>
                  {(gridQ.error as Error).message}
                </p>
              ) : (
                <div className={styles.tableWrap}>
                  <table className={styles.table}>
                    <thead>
                      <tr>
                        <th>{t("ipam.ipv4.colAddress")}</th>
                        <th>{t("ipam.grid.colRole")}</th>
                        <th>{t("ipam.grid.reachCol")}</th>
                        <th>{t("ipam.scan.colMac")}</th>
                        <th>{t("ipam.ipv4.colDevice")}</th>
                        <th>{t("ipam.ipv4.colInterface")}</th>
                        <th>{t("ipam.addr.colStatus")}</th>
                        <th>{t("ipam.addr.colOwner")}</th>
                        <th>{t("ipam.addr.colNote")}</th>
                        <th />
                      </tr>
                    </thead>
                    <tbody>
                      {pageRows.map((row) => {
                        const inv = row.inventory;
                        const ping = row.scan_ping_responded;
                        const role = inv?.role || (row.address_role === "network" || row.address_role === "broadcast" ? row.address_role : "—");
                        const devId = row.assignment?.device_id ?? inv?.device_id ?? null;
                        const devName =
                          row.assignment?.device_name ?? (devId != null ? (deviceNameById.get(devId) ?? `#${devId}`) : null);
                        const ifLabel = row.assignment?.interface_name ?? inv?.interface_name ?? "—";
                        const liveLabel =
                          ping === true
                            ? t("ipam.detail.statusUp")
                            : ping === false
                              ? t("ipam.detail.statusDown")
                              : inv?.status ?? "—";
                        return (
                          <tr key={row.address}>
                            <td>
                              <code>{row.address}</code>
                            </td>
                            <td>
                              {role !== "—" ? <span className={styles.roleChip}>{role}</span> : <span className={styles.muted}>—</span>}
                            </td>
                            <td>
                              {ping === true ? (
                                <span className={`${styles.dot} ${styles.dotOk}`} title={t("ipam.grid.reach.alive")} />
                              ) : ping === false ? (
                                <span className={`${styles.dot} ${styles.dotOff}`} title={t("ipam.grid.reach.dead")} />
                              ) : (
                                <span className={styles.muted}>—</span>
                              )}
                            </td>
                            <td>{row.scan_mac ?? inv?.mac_address ?? "—"}</td>
                            <td>
                              {devId != null ? (
                                <Link to={`/dcim/equipment/devices/${devId}`}>{devName}</Link>
                              ) : (
                                <span className={styles.muted}>—</span>
                              )}
                            </td>
                            <td>{ifLabel}</td>
                            <td className={ping === true ? styles.statusOk : ping === false ? styles.statusDown : undefined}>
                              {inv != null ? (
                                <select
                                  className={styles.compactSelect}
                                  value={inv.status}
                                  onChange={(e) => patchAddr.mutate({ id: inv.id, body: { status: e.target.value } })}
                                >
                                  <option value="discovered">discovered</option>
                                  <option value="reserved">reserved</option>
                                  <option value="assigned">assigned</option>
                                </select>
                              ) : (
                                liveLabel
                              )}
                            </td>
                            <td>
                              {inv != null ? (
                                <select
                                  className={styles.compactSelect}
                                  value={inv.owner_user_id ?? ""}
                                  onChange={(e) =>
                                    patchAddr.mutate({
                                      id: inv.id,
                                      body: { owner_user_id: e.target.value === "" ? null : Number(e.target.value) },
                                    })
                                  }
                                >
                                  <option value="">{t("dcim.common.choose")}</option>
                                  {(usersQ.data ?? []).map((u) => (
                                    <option key={u.id} value={String(u.id)}>
                                      {u.display_name ?? u.username}
                                    </option>
                                  ))}
                                </select>
                              ) : (
                                <span className={styles.muted}>—</span>
                              )}
                            </td>
                            <td>
                              {inv != null ? (
                                <input
                                  className={styles.compactInput}
                                  defaultValue={inv.note ?? ""}
                                  key={`${inv.id}-${inv.updated_at}`}
                                  onBlur={(e) => {
                                    const v = e.target.value.trim();
                                    if ((inv.note ?? "") !== v) patchAddr.mutate({ id: inv.id, body: { note: v || null } });
                                  }}
                                />
                              ) : (
                                <span className={styles.muted}>—</span>
                              )}
                            </td>
                            <td>
                              <div className={styles.rowActions}>
                                <button
                                  type="button"
                                  className={styles.toolBtn}
                                  disabled={!isGridRowFree(row) || reserveOne.isPending}
                                  onClick={() => reserveOne.mutate(row.address)}
                                >
                                  {t("ipam.grid.action.reserve")}
                                </button>
                                {inv && (inv.status === "reserved" || inv.status === "assigned") ? (
                                  <button type="button" className={styles.toolBtn} onClick={() => setReleaseRow(row)}>
                                    {t("ipam.addr.release")}
                                  </button>
                                ) : (
                                  <button
                                    type="button"
                                    className={styles.toolBtn}
                                    onClick={() => {
                                      setRequestPreferred(row.address);
                                      setRequestOpen(true);
                                    }}
                                  >
                                    {t("ipam.detail.request")}
                                  </button>
                                )}
                              </div>
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              )}
              {!gridQ.isError && !gridQ.isLoading ? (
                <div className={styles.pager}>
                  <span>
                    {t("ipam.grid.pagination.showing")} {filtered.length ? safePage * pageSize + 1 : 0}–
                    {Math.min(filtered.length, (safePage + 1) * pageSize)} {t("ipam.grid.pagination.of")} {filtered.length}
                  </span>
                  <span style={{ display: "inline-flex", gap: "0.3rem", alignItems: "center" }}>
                    <button type="button" className={styles.pageBtn} disabled={safePage <= 0} onClick={() => setPage((p) => p - 1)}>
                      ‹
                    </button>
                    {pageWindow(safePage, pageCount).map((n) => (
                      <button
                        key={n}
                        type="button"
                        className={`${styles.pageBtn} ${n === safePage ? styles.pageBtnActive : ""}`}
                        onClick={() => setPage(n)}
                      >
                        {n + 1}
                      </button>
                    ))}
                    <button
                      type="button"
                      className={styles.pageBtn}
                      disabled={safePage >= pageCount - 1}
                      onClick={() => setPage((p) => p + 1)}
                    >
                      ›
                    </button>
                  </span>
                </div>
              ) : null}
            </>
          ) : null}

          {tab === "scanning" ? (
            <div className={styles.panelPad}>
              <button type="button" className={styles.toolBtn} onClick={() => scanM.mutate()} disabled={scanM.isPending || scanRunning}>
                {t("ipam.scan.start")}
              </button>
              {(scansQ.data ?? []).length ? (
                <table className={styles.table}>
                  <thead>
                    <tr>
                      <th>{t("ipam.scan.last")}</th>
                      <th>{t("ipam.detail.colScanStatus")}</th>
                      <th>{t("ipam.detail.scanned")}</th>
                      <th>{t("ipam.detail.responding")}</th>
                    </tr>
                  </thead>
                  <tbody>
                    {(scansQ.data ?? []).map((s) => (
                      <tr key={s.id}>
                        <td>{formatWhen(s.completed_at ?? s.started_at)}</td>
                        <td>{s.status}</td>
                        <td>{s.hosts_scanned}</td>
                        <td>{s.hosts_responding}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              ) : (
                <p className={styles.muted}>{t("ipam.detail.noScans")}</p>
              )}
              {driftQ.data ? (
                <p className={styles.muted}>
                  {t("ipam.detail.driftLine", {
                    unmanaged: String(driftQ.data.seen_unmanaged.length),
                    missing: String(driftQ.data.reserved_missing.length),
                  })}
                </p>
              ) : null}
            </div>
          ) : null}

          {tab === "services" ? (
            <form
              className={styles.panelPad}
              style={{ display: "grid", gap: "0.75rem", maxWidth: "28rem" }}
              onSubmit={(e) => {
                e.preventDefault();
                saveSvc.mutate();
              }}
            >
              <label>
                {t("ipam.detail.kpiGateway")}
                <input value={svcGateway} onChange={(e) => setSvcGateway(e.target.value)} />
              </label>
              <label>
                DNS
                <input value={svcDns} onChange={(e) => setSvcDns(e.target.value)} placeholder="1.1.1.1, 8.8.8.8" />
              </label>
              <label>
                DHCP
                <input value={svcDhcp} onChange={(e) => setSvcDhcp(e.target.value)} />
              </label>
              <button type="submit" className={dcimStyles.btn} disabled={saveSvc.isPending}>
                {t("dcim.common.save")}
              </button>
            </form>
          ) : null}

          {tab === "history" ? (
            <div className={styles.panelPad}>
              {history.length ? (
                <table className={styles.table}>
                  <thead>
                    <tr>
                      <th>{t("ipam.detail.when")}</th>
                      <th>{t("ipam.detail.actor")}</th>
                      <th>{t("ipam.detail.action")}</th>
                    </tr>
                  </thead>
                  <tbody>
                    {history.map((ev) => (
                      <tr key={ev.id}>
                        <td>{formatWhen(ev.created_at)}</td>
                        <td>{ev.actor_name ?? ev.actor_type}</td>
                        <td>
                          {ev.action} {ev.resource_type}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              ) : (
                <p className={styles.muted}>{t("ipam.detail.noHistory")}</p>
              )}
            </div>
          ) : null}
        </section>

        <aside className={styles.side}>
          <section className={styles.sideCard}>
            <h2 className={styles.sideTitle}>{t("ipam.detail.scanStatus")}</h2>
            <dl>
              <div className={styles.sideRow}>
                <dt>{t("ipam.scan.last")}</dt>
                <dd>
                  {lastScan ? formatWhen(lastScan.completed_at ?? lastScan.started_at) : "—"}
                  {lastScan?.status === "completed" ? ` (${t("ipam.detail.scanComplete")})` : ""}
                </dd>
              </div>
            </dl>
            <div className={styles.bar} aria-hidden>
              <div className={styles.barFill} style={{ width: `${scanPct}%` }} />
            </div>
            <p className={styles.muted} style={{ margin: "0 0 0.5rem" }}>
              {scanPct}%
              {lastScan ? ` · ${lastScan.hosts_scanned} ${t("ipam.detail.scanned").toLowerCase()}` : ""}
            </p>
            <div className={styles.legend}>
              <span>
                <span className={`${styles.dot} ${styles.dotOk}`} />
                {lastScan?.hosts_responding ?? 0} {t("ipam.detail.responding")}
              </span>
              <span>
                <span className={`${styles.dot} ${styles.dotWarn}`} />
                {driftQ.data?.seen_unmanaged.length ?? 0} {t("ipam.detail.newHosts")}
              </span>
              <span>
                <span className={`${styles.dot} ${styles.dotOff}`} />
                {Math.max(0, (lastScan?.hosts_scanned ?? 0) - (lastScan?.hosts_responding ?? 0))} {t("ipam.detail.noReply")}
              </span>
            </div>
            <div className={styles.rowActions}>
              <button type="button" className={styles.btnPrimary} onClick={() => scanM.mutate()} disabled={scanM.isPending || scanRunning}>
                {t("ipam.scan.start")}
              </button>
              <button type="button" className={styles.toolBtn} onClick={() => setTab("scanning")}>
                {t("ipam.detail.viewScanLog")}
              </button>
            </div>
          </section>

          <section className={styles.sideCard}>
            <h2 className={styles.sideTitle}>{t("ipam.detail.services")}</h2>
            <div className={styles.svcLine}>
              <span>{t("ipam.detail.kpiGateway")}</span>
              <span>
                {svc.gateway ? (
                  <>
                    <span className={`${styles.dot} ${styles.dotOk}`} />
                    {svc.gateway}
                  </>
                ) : (
                  "—"
                )}
              </span>
            </div>
            <div className={styles.svcLine}>
              <span>DNS</span>
              <span>{svc.dns.length ? svc.dns.join(", ") : "—"}</span>
            </div>
            <div className={styles.svcLine}>
              <span>DHCP</span>
              <span>{svc.dhcp ?? "—"}</span>
            </div>
          </section>

          <section className={styles.sideCard}>
            <h2 className={styles.sideTitle}>{t("ipam.detail.info")}</h2>
            <dl>
              <div className={styles.sideRow}>
                <dt>{t("ipam.detail.network")}</dt>
                <dd>{network ?? "—"}</dd>
              </div>
              <div className={styles.sideRow}>
                <dt>{t("ipam.detail.broadcast")}</dt>
                <dd>{broadcast ?? "—"}</dd>
              </div>
              <div className={styles.sideRow}>
                <dt>{t("ipam.detail.mask")}</dt>
                <dd>{mask ?? "—"}</dd>
              </div>
              <div className={styles.sideRow}>
                <dt>{t("ipam.detail.kpiAddresses")}</dt>
                <dd>{usage.total}</dd>
              </div>
              <div className={styles.sideRow}>
                <dt>{t("ipam.detail.used")}</dt>
                <dd>
                  {usage.used}/{usage.total} ({Math.round(usage.pct)}%)
                </dd>
              </div>
              <div className={styles.sideRow}>
                <dt>{t("ipam.detail.free")}</dt>
                <dd>
                  {freeCount} ({usage.total ? Math.round((100 * freeCount) / usage.total) : 0}%)
                </dd>
              </div>
            </dl>
          </section>
        </aside>
      </div>

      <PrefixDrawer title={t("ipam.ipv4.editTitle")} open={editOpen} onClose={() => setEditOpen(false)}>
        <label className={dcimStyles.wideField}>
          {t("ipam.ipv4.name")}
          <input value={editName} onChange={(e) => setEditName(e.target.value)} />
        </label>
        <label className={dcimStyles.wideField}>
          {t("ipam.ipv4.filterRole")}
          <select value={editRole} onChange={(e) => setEditRole(e.target.value)}>
            {PREFIX_ROLES.map((r) => (
              <option key={r} value={r}>
                {r}
              </option>
            ))}
          </select>
        </label>
        <label className={dcimStyles.wideField}>
          {t("ipam.ipv4.filterStatus")}
          <select value={editStatus} onChange={(e) => setEditStatus(e.target.value)}>
            {PREFIX_STATUSES.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
        </label>
        <label className={dcimStyles.wideField}>
          VLAN
          <select value={editVlan} onChange={(e) => setEditVlan(e.target.value)}>
            <option value="">{t("ipam.detail.notSet")}</option>
            {vlanOptions.map((v) => (
              <option key={v.id} value={String(v.id)}>
                {v.vid} {v.name}
              </option>
            ))}
          </select>
        </label>
        <label className={dcimStyles.wideField}>
          VRF
          <select value={editVrf} onChange={(e) => setEditVrf(e.target.value)}>
            <option value="">{t("ipam.detail.notSet")}</option>
            {vrfOptions.map((v) => (
              <option key={v.id} value={String(v.id)}>
                {v.name}
              </option>
            ))}
          </select>
        </label>
        <div className={prefixStyles.drawerFoot} style={{ padding: 0, border: "none" }}>
          <button type="button" className={dcimStyles.btn} onClick={() => saveEdit.mutate()} disabled={saveEdit.isPending}>
            {t("dcim.common.save")}
          </button>
        </div>
      </PrefixDrawer>

      <IpamIpRequestModal
        open={requestOpen}
        onClose={() => setRequestOpen(false)}
        prefixId={id}
        prefixCidr={prefix?.cidr ?? ""}
        initialPreferred={requestPreferred ?? ""}
        onAllocated={invalidate}
      />
      <ConfirmModal
        open={releaseRow?.inventory != null}
        onClose={() => setReleaseRow(null)}
        title={t("ipam.addr.release")}
        message={
          releaseRow ? (
            <>
              <code>{releaseRow.address}</code>
              <br />
              {t("ipam.addr.releaseConfirm")}
            </>
          ) : null
        }
        confirmLabel={t("ipam.addr.release")}
        cancelLabel={t("dcim.common.cancel")}
        danger
        pending={releaseM.isPending}
        onConfirm={() => {
          if (releaseRow?.inventory) releaseM.mutate(releaseRow.inventory.id);
        }}
      />
    </div>
  );
}
