import { useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { SidebarNavIcon } from "@/components/layout/SidebarNavIcon";
import * as dcimApi from "@/features/dcim/dcimApi";
import type { DeviceInstance, DeviceModel } from "@/features/dcim/types";
import * as ipamApi from "@/features/ipam/ipamApi";
import { prefixUsage } from "@/features/ipam/prefixPageUi";
import * as netscanApi from "@/features/networkScans/networkScanApi";
import * as systemApi from "@/features/system/systemApi";
import { useI18n } from "@/i18n/I18nProvider";
import type { MessageKey } from "@/i18n/messages/en";
import { usePlugins } from "@/plugins/PluginContext";
import styles from "./dashboard.module.css";
import { buildRackUtils, buildSiteCards, ipv4Inventory, siteInitials, topPrefixesByUsage } from "./dashboardUtils";

function barClass(pct: number): string {
  if (pct >= 85) return styles.barHigh;
  if (pct >= 60) return styles.barMid;
  return styles.barOk;
}

function jobStatusKey(status: string): MessageKey {
  if (status === "pending") return "ipam.scan.status.pending";
  if (status === "running") return "ipam.scan.status.running";
  if (status === "completed") return "ipam.scan.status.completed";
  if (status === "failed") return "ipam.scan.status.failed";
  return "dashboard.jobUnknown";
}

function statusTone(status: string): string {
  if (status === "completed") return styles.ok;
  if (status === "failed") return styles.bad;
  if (status === "running" || status === "pending") return styles.warn;
  return "";
}

function formatWhen(iso: string | null | undefined): string {
  if (!iso) return "—";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return iso;
  return d.toLocaleString();
}

export function DashboardHome() {
  const { t } = useI18n();
  const plugins = usePlugins();

  const sitesQ = useQuery({ queryKey: ["dcim", "sites"], queryFn: dcimApi.listSites });
  const roomsQ = useQuery({ queryKey: ["dcim", "rooms"], queryFn: () => dcimApi.listRooms() });
  const racksQ = useQuery({ queryKey: ["dcim", "racks"], queryFn: () => dcimApi.listRacks() });
  const devicesQ = useQuery({ queryKey: ["dcim", "devices"], queryFn: dcimApi.listDevices });
  const modelsQ = useQuery({ queryKey: ["dcim", "device-models"], queryFn: dcimApi.listDeviceModels });
  const placementsQ = useQuery({ queryKey: ["dcim", "placements", "all"], queryFn: () => dcimApi.listPlacements() });
  const prefixesQ = useQuery({ queryKey: ["ipam", "ipv4-prefixes"], queryFn: () => ipamApi.listIpv4Prefixes() });
  const jobsQ = useQuery({
    queryKey: ["network-scans", "jobs", "dashboard"],
    queryFn: () => netscanApi.listNetworkScanJobs({ limit: 12 }),
  });
  const discoveriesQ = useQuery({
    queryKey: ["network-scans", "discoveries", "dashboard"],
    queryFn: () => netscanApi.listDiscoveries({ limit: 12 }),
  });
  const pendingDiscQ = useQuery({
    queryKey: ["network-scans", "discoveries", "pending"],
    queryFn: () => netscanApi.listDiscoveries({ status: "pending", limit: 200 }),
  });
  const systemQ = useQuery({
    queryKey: ["system", "status"],
    queryFn: systemApi.systemStatus,
    refetchInterval: 30_000,
  });

  const sites = sitesQ.data ?? [];
  const rooms = roomsQ.data ?? [];
  const racks = racksQ.data ?? [];
  const devices = devicesQ.data ?? [];
  const prefixes = prefixesQ.data ?? [];
  const jobs = jobsQ.data ?? [];
  const discoveries = discoveriesQ.data ?? [];

  const devicesById = useMemo(() => {
    const m = new Map<number, DeviceInstance>();
    for (const d of devices) m.set(d.id, d);
    return m;
  }, [devices]);
  const modelsById = useMemo(() => {
    const m = new Map<number, DeviceModel>();
    for (const x of modelsQ.data ?? []) m.set(x.id, x);
    return m;
  }, [modelsQ.data]);

  const siteCards = useMemo(() => buildSiteCards(sites, rooms, racks), [sites, rooms, racks]);
  const allRackUtils = useMemo(
    () => buildRackUtils(racks, rooms, sites, placementsQ.data ?? [], devicesById, modelsById),
    [racks, rooms, sites, placementsQ.data, devicesById, modelsById],
  );
  const rackUtils = allRackUtils.slice(0, 6);
  const topPrefixes = useMemo(() => topPrefixesByUsage(prefixes, 5), [prefixes]);
  const ipv4 = useMemo(() => ipv4Inventory(prefixes), [prefixes]);
  const usedU = useMemo(() => allRackUtils.reduce((s, r) => s + r.used, 0), [allRackUtils]);
  const totalU = racks.reduce((s, r) => s + r.u_height, 0);
  const activeJobs = jobs.filter((j) => j.status === "running" || j.status === "pending").length;
  const failedJobs = jobs.filter((j) => j.status === "failed").length;
  const pendingDiscoveries = (pendingDiscQ.data ?? discoveries.filter((d) => d.status === "pending")).length;
  const siteById = useMemo(() => new Map(sites.map((s) => [s.id, s])), [sites]);

  const loadErr =
    sitesQ.error ??
    roomsQ.error ??
    racksQ.error ??
    devicesQ.error ??
    prefixesQ.error ??
    jobsQ.error ??
    discoveriesQ.error ??
    pendingDiscQ.error ??
    modelsQ.error ??
    placementsQ.error ??
    systemQ.error;

  return (
    <div className={styles.page}>
      <header className={styles.head}>
        <div>
          <h1 className={styles.title}>{t("dashboard.title")}</h1>
          <p className={styles.intro}>{t("dashboard.intro")}</p>
        </div>
      </header>

      {loadErr ? <p className={styles.err}>{(loadErr as Error).message}</p> : null}

      <section className={styles.kpiRow}>
        <Link to="/dcim/sites" className={styles.kpi}>
          <span className={styles.kpiIcon}>
            <SidebarNavIcon name="dcimSites" size={18} />
          </span>
          <span>
            <p className={styles.kpiLabel}>{t("dashboard.kpiSites")}</p>
            <p className={styles.kpiValue}>{sites.length}</p>
            <p className={styles.kpiMeta}>{t("dashboard.kpiRooms", { count: String(rooms.length) })}</p>
          </span>
        </Link>
        <Link to="/dcim/racks" className={styles.kpi}>
          <span className={styles.kpiIcon}>
            <SidebarNavIcon name="dcimRacks" size={18} />
          </span>
          <span>
            <p className={styles.kpiLabel}>{t("dashboard.kpiRacks")}</p>
            <p className={styles.kpiValue}>{racks.length}</p>
            <p className={styles.kpiMeta}>
              {t("dashboard.kpiUsedU", { used: String(usedU), total: String(totalU) })}
            </p>
          </span>
        </Link>
        <Link to="/dcim/equipment" className={styles.kpi}>
          <span className={styles.kpiIcon}>
            <SidebarNavIcon name="dcimEquipment" size={18} />
          </span>
          <span>
            <p className={styles.kpiLabel}>{t("dashboard.kpiDevices")}</p>
            <p className={styles.kpiValue}>{devices.length}</p>
            <p className={styles.kpiMeta}>{t("dashboard.kpiPhysical")}</p>
          </span>
        </Link>
        <Link to="/ipam/prefixes" className={styles.kpi}>
          <span className={styles.kpiIcon}>
            <SidebarNavIcon name="ipam" size={18} />
          </span>
          <span>
            <p className={styles.kpiLabel}>{t("dashboard.kpiIpv4")}</p>
            <p className={styles.kpiValue}>{ipv4.used.toLocaleString()}</p>
            <p className={styles.kpiMeta}>
              {t("dashboard.kpiIpv4Meta", { total: String(ipv4.total), pct: String(Math.round(ipv4.pct)) })}
            </p>
          </span>
        </Link>
        <Link to="/jobs" className={styles.kpi}>
          <span className={styles.kpiIcon}>
            <SidebarNavIcon name="jobs" size={18} />
          </span>
          <span>
            <p className={styles.kpiLabel}>{t("dashboard.kpiJobs")}</p>
            <p className={styles.kpiValue}>{activeJobs}</p>
            <p className={styles.kpiMeta}>
              {failedJobs > 0
                ? t("dashboard.kpiJobsFailed", { count: String(failedJobs) })
                : t("dashboard.kpiJobsOk")}
            </p>
          </span>
        </Link>
        <Link to="/jobs" className={styles.kpi}>
          <span className={styles.kpiIcon}>
            <SidebarNavIcon name="snmp" size={18} />
          </span>
          <span>
            <p className={styles.kpiLabel}>{t("dashboard.kpiDiscoveries")}</p>
            <p className={styles.kpiValue}>{pendingDiscoveries}</p>
            <p className={styles.kpiMeta}>{t("dashboard.kpiDiscoveriesMeta")}</p>
          </span>
        </Link>
      </section>

      <section className={styles.grid2}>
        <article className={styles.card}>
          <div className={styles.cardHead}>
            <h2 className={styles.cardTitle}>{t("dashboard.sitesTitle")}</h2>
            <Link to="/dcim/sites" className={styles.cardLink}>
              {t("dashboard.seeAll")}
            </Link>
          </div>
          <div className={styles.cardBody}>
            {siteCards.length === 0 ? (
              <p className={styles.muted}>{t("dashboard.sitesEmpty")}</p>
            ) : (
              <div className={styles.siteGrid}>
                {siteCards.map((row) => (
                  <Link key={row.site.id} to="/dcim/sites" className={styles.siteCard}>
                    <div className={styles.siteThumb}>
                      {row.site.has_banner ? (
                        <img
                          src={dcimApi.siteBannerUrl(row.site.id)}
                          alt=""
                          className={styles.siteThumbImg}
                        />
                      ) : (
                        siteInitials(row.site.name)
                      )}
                    </div>
                    <p className={styles.siteName}>
                      {row.site.name}
                      {row.site.slug ? ` (${row.site.slug.toUpperCase()})` : ""}
                    </p>
                    <p className={styles.siteMeta}>
                      {[row.site.city, row.site.country].filter(Boolean).join(", ") || t("dashboard.noAddress")}
                    </p>
                    <p className={styles.siteMeta}>
                      {t("dashboard.siteStats", { rooms: String(row.rooms), racks: String(row.racks) })}
                    </p>
                  </Link>
                ))}
              </div>
            )}
          </div>
        </article>

        <article className={styles.card}>
          <div className={styles.cardHead}>
            <h2 className={styles.cardTitle}>{t("dashboard.racksTitle")}</h2>
            <Link to="/dcim/racks" className={styles.cardLink}>
              {t("dashboard.seeAll")}
            </Link>
          </div>
          <div className={styles.cardBody}>
            {rackUtils.length === 0 ? (
              <p className={styles.muted}>{t("dashboard.racksEmpty")}</p>
            ) : (
              <div className={styles.list}>
                {rackUtils.map((row) => (
                  <Link
                    key={row.rack.id}
                    to={`/dcim/racks?room=${row.rack.room_id}`}
                    className={styles.listRow}
                  >
                    <span>
                      <span className={styles.listName}>
                        {row.rack.name}
                        {row.siteName ? ` (${row.siteName})` : ""}
                      </span>
                      <span className={styles.listSub}>
                        {row.used} / {row.total} U
                      </span>
                    </span>
                    <span>
                      <div className={styles.bar} aria-hidden>
                        <div
                          className={`${styles.barFill} ${barClass(row.pct)}`}
                          style={{ width: `${Math.min(100, row.pct)}%` }}
                        />
                      </div>
                      <div className={styles.barPct}>{Math.round(row.pct)}%</div>
                    </span>
                  </Link>
                ))}
              </div>
            )}
          </div>
        </article>
      </section>

      <section className={styles.grid3}>
        <article className={styles.card}>
          <div className={styles.cardHead}>
            <h2 className={styles.cardTitle}>{t("dashboard.ipamTitle")}</h2>
            <Link to="/ipam/prefixes" className={styles.cardLink}>
              {t("dashboard.seeAll")}
            </Link>
          </div>
          <div className={styles.cardBody}>
            {topPrefixes.length === 0 ? (
              <p className={styles.muted}>{t("dashboard.ipamEmpty")}</p>
            ) : (
              <div className={styles.list}>
                {topPrefixes.map((p) => {
                  const u = prefixUsage(p);
                  return (
                    <Link key={p.id} to="/ipam/prefixes" className={styles.listRow}>
                      <span>
                        <span className={styles.listName}>{p.cidr}</span>
                        <span className={styles.listSub}>{p.name}</span>
                      </span>
                      <span>
                        <div className={styles.bar} aria-hidden>
                          <div
                            className={`${styles.barFill} ${barClass(u.pct)}`}
                            style={{ width: `${Math.min(100, u.pct)}%` }}
                          />
                        </div>
                        <div className={styles.barPct}>{Math.round(u.pct)}%</div>
                      </span>
                    </Link>
                  );
                })}
              </div>
            )}
          </div>
        </article>

        <article className={styles.card}>
          <div className={styles.cardHead}>
            <h2 className={styles.cardTitle}>{t("dashboard.jobsTitle")}</h2>
            <Link to="/jobs" className={styles.cardLink}>
              {t("dashboard.seeAll")}
            </Link>
          </div>
          <div className={styles.cardBody}>
            {jobs.length === 0 ? (
              <p className={styles.muted}>{t("dashboard.jobsEmpty")}</p>
            ) : (
              <div className={styles.list}>
                {jobs.slice(0, 6).map((job) => (
                  <Link key={job.id} to="/jobs" className={styles.listRow}>
                    <span>
                      <span className={styles.listName}>{job.cidr}</span>
                      <span className={styles.listSub}>{formatWhen(job.completed_at ?? job.started_at)}</span>
                    </span>
                    <span className={`${styles.barPct} ${statusTone(job.status)}`}>{t(jobStatusKey(job.status))}</span>
                  </Link>
                ))}
              </div>
            )}
          </div>
        </article>

        <article className={styles.card}>
          <div className={styles.cardHead}>
            <h2 className={styles.cardTitle}>{t("dashboard.systemTitle")}</h2>
            <Link to="/system" className={styles.cardLink}>
              {t("dashboard.seeAll")}
            </Link>
          </div>
          <div className={styles.cardBody}>
            <div className={styles.statusRow}>
              <span>{t("dashboard.systemApi")}</span>
              <span className={systemQ.isError ? styles.bad : styles.ok}>
                {systemQ.isError ? t("dashboard.systemDown") : t("dashboard.systemOk")}
              </span>
            </div>
            <div className={styles.statusRow}>
              <span>{t("dashboard.systemVersion")}</span>
              <span>{systemQ.data?.update_check.local_version ?? "—"}</span>
            </div>
            <div className={styles.statusRow}>
              <span>{t("dashboard.systemUpdate")}</span>
              <span className={systemQ.data?.update_check.update_available ? styles.warn : styles.ok}>
                {systemQ.data?.update_check.update_available
                  ? t("dashboard.systemUpdateYes")
                  : t("dashboard.systemUpdateNo")}
              </span>
            </div>
            <div className={styles.statusRow}>
              <span>{t("dashboard.systemUpdater")}</span>
              <span className={systemQ.data?.updater_available ? styles.ok : styles.warn}>
                {systemQ.data?.updater_available ? t("dashboard.systemAvailable") : t("dashboard.systemUnavailable")}
              </span>
            </div>
          </div>
        </article>
      </section>

      <section className={styles.grid3}>
        <article className={styles.card}>
          <div className={styles.cardHead}>
            <h2 className={styles.cardTitle}>{t("dashboard.discoveriesTitle")}</h2>
            <Link to="/jobs" className={styles.cardLink}>
              {t("dashboard.seeAll")}
            </Link>
          </div>
          <div className={styles.cardBody}>
            {discoveries.length === 0 ? (
              <p className={styles.muted}>{t("dashboard.discoveriesEmpty")}</p>
            ) : (
              <table className={styles.table}>
                <thead>
                  <tr>
                    <th>{t("dashboard.colName")}</th>
                    <th>{t("dashboard.colSite")}</th>
                    <th>{t("dashboard.colWhen")}</th>
                  </tr>
                </thead>
                <tbody>
                  {discoveries.slice(0, 6).map((d) => (
                    <tr key={d.id}>
                      <td>
                        <Link to="/jobs">{d.chosen_name || d.address}</Link>
                        <span className={styles.listSub}>{d.address}</span>
                      </td>
                      <td>{siteById.get(d.site_id)?.name ?? `#${d.site_id}`}</td>
                      <td>{formatWhen(d.created_at)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </article>

        <article className={styles.card}>
          <div className={styles.cardHead}>
            <h2 className={styles.cardTitle}>{t("dashboard.pluginsTitle")}</h2>
            <Link to="/integrations" className={styles.cardLink}>
              {t("dashboard.manage")}
            </Link>
          </div>
          <div className={styles.cardBody}>
            {plugins.length === 0 ? (
              <p className={styles.muted}>{t("dashboard.pluginsEmpty")}</p>
            ) : (
              <div className={styles.list}>
                {plugins.map((p) => (
                  <div key={p.id} className={styles.listRow}>
                    <span>
                      <span className={styles.listName}>{p.name}</span>
                      <span className={styles.listSub}>{p.id}</span>
                    </span>
                    <span className={styles.ok}>v{p.version}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </article>

        <article className={styles.card}>
          <div className={styles.cardHead}>
            <h2 className={styles.cardTitle}>{t("dashboard.actionsTitle")}</h2>
          </div>
          <div className={styles.cardBody}>
            <div className={styles.actions}>
              <Link to="/ipam/prefixes" className={styles.action}>
                {t("dashboard.actionPrefix")}
                <span>{t("dashboard.actionPrefixHint")}</span>
              </Link>
              <Link to="/dcim/equipment/devices/new" className={styles.action}>
                {t("dashboard.actionDevice")}
                <span>{t("dashboard.actionDeviceHint")}</span>
              </Link>
              <Link to="/dcim/racks" className={styles.action}>
                {t("dashboard.actionRacks")}
                <span>{t("dashboard.actionRacksHint")}</span>
              </Link>
              <Link to="/jobs" className={styles.action}>
                {t("dashboard.actionScan")}
                <span>{t("dashboard.actionScanHint")}</span>
              </Link>
            </div>
          </div>
        </article>
      </section>
    </div>
  );
}
