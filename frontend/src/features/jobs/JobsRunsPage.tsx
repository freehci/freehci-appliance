import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { Panel } from "@/components/ui/Panel";
import * as dcimApi from "@/features/dcim/dcimApi";
import * as ipamApi from "@/features/ipam/ipamApi";
import dcimStyles from "@/features/dcim/dcim.module.css";
import { useI18n } from "@/i18n/I18nProvider";
import { ApiError } from "@/lib/api";
import type { InventoryMode, NameSource, ParentFilter } from "@/features/networkScans/networkScanApi";
import * as netscanApi from "@/features/networkScans/networkScanApi";
import { DiscoveryTable } from "./JobsDiscoveryTable";

const DEFAULT_PRIORITY: NameSource[] = ["snmp_sysname", "ptr", "ip"];

function parseNamePriority(raw: string): NameSource[] {
  const allowed = new Set<string>(["snmp_sysname", "ptr", "ip"]);
  const out: NameSource[] = [];
  for (const part of raw.split(/[,;\s]+/).filter(Boolean)) {
    const p = part.trim() as NameSource;
    if (allowed.has(p) && !out.includes(p)) out.push(p);
  }
  return out.length > 0 ? out : [...DEFAULT_PRIORITY];
}

export function JobsRunsPage() {
  const { t } = useI18n();
  const qc = useQueryClient();
  const [err, setErr] = useState<string | null>(null);

  const [jobPrefix, setJobPrefix] = useState("");
  const [jobTemplate, setJobTemplate] = useState("");
  const [jobParentId, setJobParentId] = useState("");
  const [jobParentFilter, setJobParentFilter] = useState<ParentFilter | "">("");
  const [jobInventory, setJobInventory] = useState<InventoryMode>("none");
  const [jobNamePriority, setJobNamePriority] = useState("snmp_sysname,ptr,ip");
  const [jobModelId, setJobModelId] = useState("");
  const [jobSnmpCommunity, setJobSnmpCommunity] = useState("");
  const [expandedJobId, setExpandedJobId] = useState<number | null>(null);

  const sitesQ = useQuery({ queryKey: ["dcim", "sites"], queryFn: dcimApi.listSites });
  const prefixesQ = useQuery({
    queryKey: ["ipam", "ipv4-prefixes", "all-netscan"],
    queryFn: () => ipamApi.listIpv4Prefixes(),
  });
  const templatesQ = useQuery({
    queryKey: ["network-scans", "templates"],
    queryFn: netscanApi.listNetworkScanTemplates,
  });
  const jobsQ = useQuery({
    queryKey: ["network-scans", "jobs"],
    queryFn: () => netscanApi.listNetworkScanJobs({ limit: 80 }),
  });
  const discoveriesQ = useQuery({
    queryKey: ["network-scans", "discoveries", "pending"],
    queryFn: () => netscanApi.listDiscoveries({ status: "pending", limit: 200 }),
  });
  const modelsQ = useQuery({ queryKey: ["dcim", "device-models"], queryFn: dcimApi.listDeviceModels });

  const jobDetailQ = useQuery({
    queryKey: ["network-scans", "job", expandedJobId],
    queryFn: () => netscanApi.getNetworkScanJob(expandedJobId!),
    enabled: expandedJobId != null,
  });

  const createJob = useMutation({
    mutationFn: netscanApi.createNetworkScanJob,
    onSuccess: () => {
      setErr(null);
      void qc.invalidateQueries({ queryKey: ["network-scans", "jobs"] });
      void qc.invalidateQueries({ queryKey: ["network-scans", "discoveries"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const delJob = useMutation({
    mutationFn: netscanApi.deleteNetworkScanJob,
    onSuccess: () => {
      setErr(null);
      setExpandedJobId(null);
      void qc.invalidateQueries({ queryKey: ["network-scans", "jobs"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const approveDisc = useMutation({
    mutationFn: ({ id, body }: { id: number; body: Parameters<typeof netscanApi.approveDiscovery>[1] }) =>
      netscanApi.approveDiscovery(id, body),
    onSuccess: () => {
      setErr(null);
      void qc.invalidateQueries({ queryKey: ["network-scans", "discoveries"] });
      void qc.invalidateQueries({ queryKey: ["dcim", "devices"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const rejectDisc = useMutation({
    mutationFn: netscanApi.rejectDiscovery,
    onSuccess: () => {
      setErr(null);
      void qc.invalidateQueries({ queryKey: ["network-scans", "discoveries"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const prefixLabel = useMemo(() => {
    const m = new Map<number, string>();
    for (const p of prefixesQ.data ?? []) {
      const site = sitesQ.data?.find((s) => s.id === p.site_id);
      m.set(p.id, `${p.name} (${p.cidr})${site ? ` · ${site.name}` : ""}`);
    }
    return m;
  }, [prefixesQ.data, sitesQ.data]);

  const submitJob = () => {
    const tid = Number(jobTemplate);
    const pid = Number(jobPrefix);
    if (!tid || !pid) {
      setErr(t("netscan.errSelectTplPrefix"));
      return;
    }
    const parentRaw = jobParentId.trim();
    const options: Parameters<typeof netscanApi.createNetworkScanJob>[0]["options"] = {
      inventory_mode: jobInventory,
      name_priority: parseNamePriority(jobNamePriority),
    };
    if (parentRaw !== "") {
      options.parent_job_id = Number(parentRaw);
      if (!jobParentFilter) {
        setErr(t("netscan.errParentFilter"));
        return;
      }
      options.parent_filter = jobParentFilter;
    }
    if (jobInventory === "auto") {
      const mid = Number(jobModelId);
      if (!mid) {
        setErr(t("netscan.errModelAuto"));
        return;
      }
      options.default_device_model_id = mid;
    }
    const comm = jobSnmpCommunity.trim();
    if (comm !== "") options.snmp_community = comm;

    createJob.mutate({ template_id: tid, ipv4_prefix_id: pid, options });
  };

  return (
    <>
      <Panel title={t("jobs.runsPanelTitle")}>
        <p className={dcimStyles.muted} style={{ marginTop: 0 }}>
          {t("netscan.intro")}
        </p>
        {err ? <p className={dcimStyles.err}>{err}</p> : null}
      </Panel>

      <Panel title={t("netscan.sectionRunJob")}>
        <p className={dcimStyles.muted}>{t("netscan.runHint")}</p>
        <form
          className={dcimStyles.formRow}
          onSubmit={(e) => {
            e.preventDefault();
            submitJob();
          }}
        >
          <label>
            {t("netscan.fieldPrefix")}
            <select value={jobPrefix} onChange={(e) => setJobPrefix(e.target.value)}>
              <option value="">{t("dcim.common.none")}</option>
              {(prefixesQ.data ?? []).map((p) => (
                <option key={p.id} value={String(p.id)}>
                  {prefixLabel.get(p.id) ?? `${p.name} (${p.cidr})`}
                </option>
              ))}
            </select>
          </label>
          <label>
            {t("netscan.fieldTemplate")}
            <select value={jobTemplate} onChange={(e) => setJobTemplate(e.target.value)}>
              <option value="">{t("dcim.common.none")}</option>
              {(templatesQ.data ?? []).map((x) => (
                <option key={x.id} value={String(x.id)}>
                  {x.name}
                </option>
              ))}
            </select>
          </label>
          <label>
            {t("netscan.fieldParentJob")}
            <input value={jobParentId} onChange={(e) => setJobParentId(e.target.value)} placeholder="123" />
          </label>
          <label>
            {t("netscan.fieldParentFilter")}
            <select
              value={jobParentFilter}
              onChange={(e) => setJobParentFilter((e.target.value || "") as ParentFilter | "")}
            >
              <option value="">{t("dcim.common.none")}</option>
              <option value="alive">{t("netscan.filterAlive")}</option>
              <option value="snmp_ok">{t("netscan.filterSnmpOk")}</option>
            </select>
          </label>
          <label>
            {t("netscan.fieldInventory")}
            <select value={jobInventory} onChange={(e) => setJobInventory(e.target.value as InventoryMode)}>
              <option value="none">{t("netscan.invNone")}</option>
              <option value="discovered_queue">{t("netscan.invQueue")}</option>
              <option value="auto">{t("netscan.invAuto")}</option>
            </select>
          </label>
          <label style={{ minWidth: "14rem" }}>
            {t("netscan.fieldNamePriority")}
            <input
              value={jobNamePriority}
              onChange={(e) => setJobNamePriority(e.target.value)}
              spellCheck={false}
              placeholder="snmp_sysname,ptr,ip"
            />
          </label>
          {jobInventory === "auto" ? (
            <label>
              {t("netscan.fieldDefaultModel")}
              <select value={jobModelId} onChange={(e) => setJobModelId(e.target.value)}>
                <option value="">{t("dcim.common.none")}</option>
                {(modelsQ.data ?? []).map((m) => (
                  <option key={m.id} value={String(m.id)}>
                    {m.name}
                  </option>
                ))}
              </select>
            </label>
          ) : null}
          <label>
            {t("netscan.fieldSnmpCommunity")}
            <input
              value={jobSnmpCommunity}
              onChange={(e) => setJobSnmpCommunity(e.target.value)}
              placeholder="public"
            />
          </label>
          <button type="submit" className={dcimStyles.btn} disabled={createJob.isPending}>
            {createJob.isPending ? "…" : t("netscan.runJob")}
          </button>
        </form>
      </Panel>

      <Panel title={t("netscan.sectionJobs")}>
        {jobsQ.data && jobsQ.data.length > 0 ? (
          <table className={dcimStyles.table}>
            <thead>
              <tr>
                <th>{t("netscan.colId")}</th>
                <th>{t("netscan.colStatus")}</th>
                <th>CIDR</th>
                <th>{t("netscan.colMatched")}</th>
                <th />
              </tr>
            </thead>
            <tbody>
              {jobsQ.data.map((j) => (
                <tr key={j.id}>
                  <td>{j.id}</td>
                  <td>{j.status}</td>
                  <td>
                    <code>{j.cidr}</code>
                  </td>
                  <td>
                    {j.hosts_matched}/{j.hosts_scanned}
                  </td>
                  <td style={{ whiteSpace: "nowrap" }}>
                    <button
                      type="button"
                      className={dcimStyles.btnMuted}
                      onClick={() => setExpandedJobId((x) => (x === j.id ? null : j.id))}
                    >
                      {expandedJobId === j.id ? t("netscan.hideResults") : t("netscan.showResults")}
                    </button>{" "}
                    <button
                      type="button"
                      className={dcimStyles.btnMuted}
                      onClick={() => delJob.mutate(j.id)}
                      disabled={delJob.isPending}
                    >
                      {t("netscan.deleteJob")}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p className={dcimStyles.muted}>{t("netscan.jobsEmpty")}</p>
        )}
        {expandedJobId != null && jobDetailQ.data ? (
          <div style={{ marginTop: "var(--space-2)", maxHeight: "40vh", overflow: "auto" }}>
            <pre
              className={dcimStyles.muted}
              style={{ fontSize: "var(--text-xs)", margin: 0, whiteSpace: "pre-wrap" }}
            >
              {JSON.stringify(jobDetailQ.data.host_results, null, 2)}
            </pre>
          </div>
        ) : null}
      </Panel>

      <Panel title={t("netscan.sectionDiscoveries")}>
        <p className={dcimStyles.muted}>{t("netscan.discoveriesHint")}</p>
        {discoveriesQ.data && discoveriesQ.data.length > 0 ? (
          <DiscoveryTable
            rows={discoveriesQ.data}
            models={modelsQ.data ?? []}
            onApprove={(id, body) => approveDisc.mutate({ id, body })}
            onReject={(id) => rejectDisc.mutate(id)}
            busy={approveDisc.isPending || rejectDisc.isPending}
            t={t}
          />
        ) : (
          <p className={dcimStyles.muted}>{t("netscan.discoveriesEmpty")}</p>
        )}
      </Panel>
    </>
  );
}
