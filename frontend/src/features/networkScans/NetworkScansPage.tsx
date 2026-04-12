import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { Panel } from "@/components/ui/Panel";
import * as dcimApi from "@/features/dcim/dcimApi";
import * as ipamApi from "@/features/ipam/ipamApi";
import dcimStyles from "@/features/dcim/dcim.module.css";
import { useI18n } from "@/i18n/I18nProvider";
import type { MessageKey } from "@/i18n/messages/en";
import { ApiError } from "@/lib/api";
import type { InventoryMode, NameSource, NetworkScanDiscovery, ParentFilter } from "./networkScanApi";
import * as netscanApi from "./networkScanApi";

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

export function NetworkScansPage() {
  const { t } = useI18n();
  const qc = useQueryClient();
  const [err, setErr] = useState<string | null>(null);

  const [bindPrefix, setBindPrefix] = useState("");
  const [bindTemplate, setBindTemplate] = useState("");

  const [jobPrefix, setJobPrefix] = useState("");
  const [jobTemplate, setJobTemplate] = useState("");
  const [jobParentId, setJobParentId] = useState("");
  const [jobParentFilter, setJobParentFilter] = useState<ParentFilter | "">("");
  const [jobInventory, setJobInventory] = useState<InventoryMode>("none");
  const [jobNamePriority, setJobNamePriority] = useState("snmp_sysname,ptr,ip");
  const [jobModelId, setJobModelId] = useState("");
  const [jobSnmpCommunity, setJobSnmpCommunity] = useState("");
  const [expandedJobId, setExpandedJobId] = useState<number | null>(null);

  const [customSlug, setCustomSlug] = useState("");
  const [customName, setCustomName] = useState("");
  const [customPorts, setCustomPorts] = useState("1883,502,22");

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
  const bindingsQ = useQuery({
    queryKey: ["network-scans", "bindings"],
    queryFn: () => netscanApi.listPrefixBindings(),
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

  const createBinding = useMutation({
    mutationFn: netscanApi.createPrefixBinding,
    onSuccess: () => {
      setErr(null);
      void qc.invalidateQueries({ queryKey: ["network-scans", "bindings"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const delBinding = useMutation({
    mutationFn: netscanApi.deletePrefixBinding,
    onSuccess: () => {
      setErr(null);
      void qc.invalidateQueries({ queryKey: ["network-scans", "bindings"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const createTpl = useMutation({
    mutationFn: netscanApi.createNetworkScanTemplate,
    onSuccess: () => {
      setErr(null);
      setCustomSlug("");
      setCustomName("");
      void qc.invalidateQueries({ queryKey: ["network-scans", "templates"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
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
      <Panel title={t("netscan.title")}>
        <p className={dcimStyles.muted} style={{ marginTop: 0 }}>
          {t("netscan.intro")}
        </p>
        {err ? <p className={dcimStyles.err}>{err}</p> : null}
        <p className={dcimStyles.muted} style={{ fontSize: "var(--text-xs)" }}>
          {t("netscan.schedulesHint")}
        </p>
      </Panel>

      <Panel title={t("netscan.sectionTemplates")}>
        {templatesQ.isLoading ? <p className={dcimStyles.muted}>{t("dcim.common.loading")}</p> : null}
        {templatesQ.data && templatesQ.data.length > 0 ? (
          <table className={dcimStyles.table}>
            <thead>
              <tr>
                <th>{t("netscan.colSlug")}</th>
                <th>{t("netscan.colName")}</th>
                <th>{t("netscan.colKind")}</th>
                <th>{t("netscan.colBuiltin")}</th>
              </tr>
            </thead>
            <tbody>
              {templatesQ.data.map((x) => (
                <tr key={x.id}>
                  <td>
                    <code>{x.slug}</code>
                  </td>
                  <td>{x.name}</td>
                  <td>{x.kind}</td>
                  <td>{x.is_builtin ? t("netscan.yes") : t("netscan.no")}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : null}

        <h4 className={dcimStyles.mfrDetailSectionTitle} style={{ marginTop: "var(--space-3)" }}>
          {t("netscan.customTcpTitle")}
        </h4>
        <p className={dcimStyles.muted}>{t("netscan.customTcpHint")}</p>
        <form
          className={dcimStyles.formRow}
          onSubmit={(e) => {
            e.preventDefault();
            const ports = customPorts
              .split(/[,;\s]+/)
              .map((s) => Number(s.trim()))
              .filter((n) => Number.isFinite(n) && n >= 1 && n <= 65535);
            if (!customSlug.trim() || !customName.trim() || ports.length === 0) {
              setErr(t("netscan.errCustomTcp"));
              return;
            }
            createTpl.mutate({
              slug: customSlug.trim().toLowerCase(),
              name: customName.trim(),
              kind: "tcp_ports",
              default_config: { ports, timeout_sec: 1.0 },
            });
          }}
        >
          <label>
            {t("netscan.customSlug")}
            <input value={customSlug} onChange={(e) => setCustomSlug(e.target.value)} placeholder="iot-discovery" />
          </label>
          <label>
            {t("netscan.customName")}
            <input value={customName} onChange={(e) => setCustomName(e.target.value)} placeholder="IoT Discovery" />
          </label>
          <label>
            {t("netscan.customPorts")}
            <input value={customPorts} onChange={(e) => setCustomPorts(e.target.value)} placeholder="1883,502,22" />
          </label>
          <button type="submit" className={dcimStyles.btn} disabled={createTpl.isPending}>
            {createTpl.isPending ? "…" : t("netscan.createTemplate")}
          </button>
        </form>
      </Panel>

      <Panel title={t("netscan.sectionBindings")}>
        <p className={dcimStyles.muted}>{t("netscan.bindingsHint")}</p>
        <form
          className={dcimStyles.formRow}
          onSubmit={(e) => {
            e.preventDefault();
            const tid = Number(bindTemplate);
            const pid = Number(bindPrefix);
            if (!tid || !pid) {
              setErr(t("netscan.errSelectTplPrefix"));
              return;
            }
            createBinding.mutate({ template_id: tid, ipv4_prefix_id: pid, enabled: true });
          }}
        >
          <label>
            {t("netscan.fieldPrefix")}
            <select value={bindPrefix} onChange={(e) => setBindPrefix(e.target.value)}>
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
            <select value={bindTemplate} onChange={(e) => setBindTemplate(e.target.value)}>
              <option value="">{t("dcim.common.none")}</option>
              {(templatesQ.data ?? []).map((x) => (
                <option key={x.id} value={String(x.id)}>
                  {x.name}
                </option>
              ))}
            </select>
          </label>
          <button type="submit" className={dcimStyles.btn} disabled={createBinding.isPending}>
            {createBinding.isPending ? "…" : t("netscan.addBinding")}
          </button>
        </form>
        {bindingsQ.data && bindingsQ.data.length > 0 ? (
          <table className={dcimStyles.table} style={{ marginTop: "var(--space-2)" }}>
            <thead>
              <tr>
                <th>{t("netscan.colId")}</th>
                <th>{t("netscan.fieldPrefix")}</th>
                <th>{t("netscan.fieldTemplate")}</th>
                <th />
              </tr>
            </thead>
            <tbody>
              {bindingsQ.data.map((b) => (
                <tr key={b.id}>
                  <td>{b.id}</td>
                  <td>{prefixLabel.get(b.ipv4_prefix_id) ?? `#${b.ipv4_prefix_id}`}</td>
                  <td>
                    {(templatesQ.data ?? []).find((t) => t.id === b.template_id)?.name ?? `#${b.template_id}`}
                  </td>
                  <td>
                    <button
                      type="button"
                      className={dcimStyles.btnMuted}
                      onClick={() => delBinding.mutate(b.id)}
                      disabled={delBinding.isPending}
                    >
                      {t("netscan.removeBinding")}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p className={dcimStyles.muted}>{t("netscan.bindingsEmpty")}</p>
        )}
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
            <select
              value={jobInventory}
              onChange={(e) => setJobInventory(e.target.value as InventoryMode)}
            >
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
            styles={dcimStyles}
          />
        ) : (
          <p className={dcimStyles.muted}>{t("netscan.discoveriesEmpty")}</p>
        )}
      </Panel>
    </>
  );
}

function DiscoveryTable({
  rows,
  models,
  onApprove,
  onReject,
  busy,
  t,
  styles,
}: {
  rows: NetworkScanDiscovery[];
  models: Awaited<ReturnType<typeof dcimApi.listDeviceModels>>;
  onApprove: (id: number, body: { chosen_name_source: NameSource; chosen_name?: string; device_model_id: number }) => void;
  onReject: (id: number) => void;
  busy: boolean;
  t: (k: MessageKey) => string;
  styles: typeof dcimStyles;
}) {
  return (
    <table className={styles.table}>
      <thead>
        <tr>
          <th>IP</th>
          <th>{t("netscan.candidates")}</th>
          <th>{t("netscan.approveCol")}</th>
        </tr>
      </thead>
      <tbody>
        {rows.map((d) => (
          <DiscoveryRow key={d.id} d={d} models={models} onApprove={onApprove} onReject={onReject} busy={busy} t={t} styles={styles} />
        ))}
      </tbody>
    </table>
  );
}

function DiscoveryRow({
  d,
  models,
  onApprove,
  onReject,
  busy,
  t,
  styles,
}: {
  d: NetworkScanDiscovery;
  models: Awaited<ReturnType<typeof dcimApi.listDeviceModels>>;
  onApprove: (id: number, body: { chosen_name_source: NameSource; chosen_name?: string; device_model_id: number }) => void;
  onReject: (id: number) => void;
  busy: boolean;
  t: (k: MessageKey) => string;
  styles: typeof dcimStyles;
}) {
  const [src, setSrc] = useState<NameSource>("ip");
  const [custom, setCustom] = useState("");
  const [mid, setMid] = useState("");

  const c = d.name_candidates_json ?? {};

  return (
    <tr>
      <td>
        <code>{d.address}</code>
        <div className={styles.muted} style={{ fontSize: "var(--text-xs)" }}>
          job #{d.job_id}
        </div>
      </td>
      <td style={{ fontSize: "var(--text-xs)" }}>
        <div>
          <strong>IP:</strong> {c.ip ?? d.address}
        </div>
        {c.ptr ? (
          <div>
            <strong>PTR:</strong> {c.ptr}
          </div>
        ) : null}
        {c.snmp_sysname ? (
          <div>
            <strong>sysName:</strong> {c.snmp_sysname}
          </div>
        ) : null}
      </td>
      <td>
        <div className={styles.formRow} style={{ flexWrap: "wrap", alignItems: "flex-end" }}>
          <label>
            {t("netscan.nameSource")}
            <select value={src} onChange={(e) => setSrc(e.target.value as NameSource)}>
              <option value="ip">IP</option>
              <option value="ptr">PTR</option>
              <option value="snmp_sysname">sysName</option>
              <option value="custom">{t("netscan.nameCustom")}</option>
            </select>
          </label>
          {src === "custom" ? (
            <label>
              {t("netscan.customDeviceName")}
              <input value={custom} onChange={(e) => setCustom(e.target.value)} />
            </label>
          ) : null}
          <label>
            {t("netscan.fieldDefaultModel")}
            <select value={mid} onChange={(e) => setMid(e.target.value)}>
              <option value="">{t("dcim.common.none")}</option>
              {models.map((m) => (
                <option key={m.id} value={String(m.id)}>
                  {m.name}
                </option>
              ))}
            </select>
          </label>
          <button
            type="button"
            className={styles.btn}
            disabled={busy || !mid}
            onClick={() => {
              const device_model_id = Number(mid);
              if (!device_model_id) return;
              if (src === "custom") {
                onApprove(d.id, { chosen_name_source: "custom", chosen_name: custom.trim(), device_model_id });
              } else {
                onApprove(d.id, { chosen_name_source: src, device_model_id });
              }
            }}
          >
            {t("netscan.promote")}
          </button>
          <button type="button" className={styles.btnMuted} disabled={busy} onClick={() => onReject(d.id)}>
            {t("netscan.reject")}
          </button>
        </div>
      </td>
    </tr>
  );
}
