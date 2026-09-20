import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { Panel } from "@/components/ui/Panel";
import { listDevices } from "@/features/dcim/dcimApi";
import { DcimInnerTabs } from "@/features/dcim/DcimInnerTabs";
import dcimStyles from "@/features/dcim/dcim.module.css";
import { listIpv4Prefixes } from "@/features/ipam/ipamApi";
import { useI18n } from "@/i18n/I18nProvider";
import { ApiError } from "@/lib/api";
import * as api from "./catalogApi";

const TABS = new Set(["templates", "deploy", "instances"]);

export function ServiceCatalogPage() {
  const { t } = useI18n();
  const qc = useQueryClient();
  const [searchParams, setSearchParams] = useSearchParams();
  const tabParam = searchParams.get("tab");
  const tab = tabParam != null && TABS.has(tabParam) ? tabParam : "templates";
  const setTab = (next: string) => {
    const n = new URLSearchParams(searchParams);
    if (next === "templates") n.delete("tab");
    else n.set("tab", next);
    setSearchParams(n, { replace: true });
  };

  const [err, setErr] = useState<string | null>(null);
  const [name, setName] = useState("");
  const [kind, setKind] = useState<api.ServiceTemplateSpec["kind"]>("device_instance");
  const [reserve, setReserve] = useState(false);
  const [versionId, setVersionId] = useState("");
  const [deviceId, setDeviceId] = useState("");
  const [deviceIds, setDeviceIds] = useState<number[]>([]);
  const [clusterName, setClusterName] = useState("");
  const [clusterKind, setClusterKind] = useState("other");
  const [prefixId, setPrefixId] = useState("");
  const [selectedId, setSelectedId] = useState<number | null>(null);

  const tmplQ = useQuery({ queryKey: ["service-templates"], queryFn: api.listTemplates });
  const depQ = useQuery({ queryKey: ["service-deployments"], queryFn: api.listDeployments });
  const instQ = useQuery({ queryKey: ["service-instances"], queryFn: api.listInstances });
  const devQ = useQuery({ queryKey: ["dcim-devices"], queryFn: listDevices });
  const pfxQ = useQuery({ queryKey: ["ipam-ipv4-prefixes"], queryFn: () => listIpv4Prefixes() });

  const versions = useMemo(
    () => (tmplQ.data ?? []).flatMap((tmpl) => tmpl.versions.map((v) => ({ tmpl, v }))),
    [tmplQ.data],
  );
  const selected = (depQ.data ?? []).find((d) => d.id === selectedId) ?? null;
  const selectedVersion = versions.find(({ v }) => String(v.id) === versionId);
  const isCluster = selectedVersion?.v.spec.kind === "cluster";
  const fail = (e: Error) => setErr(e instanceof ApiError ? e.message : e.message);

  const createTmpl = useMutation({
    mutationFn: () =>
      api.createTemplate({
        name: name.trim(),
        spec: { kind, reserve_ipv4: kind === "cluster" ? false : reserve },
      }),
    onSuccess: () => {
      setErr(null);
      setName("");
      void qc.invalidateQueries({ queryKey: ["service-templates"] });
    },
    onError: fail,
  });

  const planM = useMutation({
    mutationFn: () =>
      isCluster
        ? api.createDeployment({
            template_version_id: Number(versionId),
            device_ids: deviceIds,
            name: clusterName.trim(),
            cluster_kind: clusterKind,
          })
        : api.createDeployment({
            template_version_id: Number(versionId),
            device_id: Number(deviceId),
            ipv4_prefix_id: prefixId ? Number(prefixId) : null,
          }),
    onSuccess: (row) => {
      setErr(null);
      setSelectedId(row.id);
      void qc.invalidateQueries({ queryKey: ["service-deployments"] });
    },
    onError: fail,
  });

  const runM = useMutation({
    mutationFn: (id: number) => api.runDeployment(id),
    onSuccess: (row) => {
      setErr(null);
      setSelectedId(row.id);
      void qc.invalidateQueries({ queryKey: ["service-deployments"] });
      void qc.invalidateQueries({ queryKey: ["service-instances"] });
      void qc.invalidateQueries({ queryKey: ["platform-clusters"] });
    },
    onError: fail,
  });

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "1.25rem" }}>
      <Panel title={t("catalog.title")}>
        <p style={{ marginTop: 0 }}>{t("catalog.intro")}</p>
        <DcimInnerTabs
          ariaLabel={t("catalog.tabs")}
          activeId={tab}
          onChange={setTab}
          tabs={[
            { id: "templates", label: t("catalog.tabTemplates") },
            { id: "deploy", label: t("catalog.tabDeploy") },
            { id: "instances", label: t("catalog.tabInstances") },
          ]}
        />
        {err ? <p className={dcimStyles.err}>{err}</p> : null}

        {tab === "templates" ? (
          <>
            <p className={dcimStyles.muted}>{t("catalog.templatesHint")}</p>
            <form
              className={dcimStyles.formRow}
              onSubmit={(e) => {
                e.preventDefault();
                if (name.trim()) createTmpl.mutate();
              }}
            >
              <label>
                {t("dcim.common.name")}
                <input value={name} onChange={(e) => setName(e.target.value)} />
              </label>
              <label>
                {t("catalog.kind")}
                <select value={kind} onChange={(e) => setKind(e.target.value as api.ServiceTemplateSpec["kind"])}>
                  <option value="device_instance">{t("catalog.kindDevice")}</option>
                  <option value="cluster">{t("catalog.kindCluster")}</option>
                </select>
              </label>
              {kind === "device_instance" ? (
                <label>
                  {t("catalog.reserveIpv4")}
                  <input type="checkbox" checked={reserve} onChange={(e) => setReserve(e.target.checked)} />
                </label>
              ) : null}
              <button type="submit" className={dcimStyles.btn} disabled={createTmpl.isPending || !name.trim()}>
                {t("catalog.addTemplate")}
              </button>
            </form>
            {(tmplQ.data ?? []).length === 0 && !tmplQ.isLoading ? (
              <p className={dcimStyles.muted}>{t("catalog.templatesEmpty")}</p>
            ) : null}
            {(tmplQ.data ?? []).length > 0 ? (
              <table className={dcimStyles.table}>
                <thead>
                  <tr>
                    <th>{t("dcim.common.name")}</th>
                    <th>{t("dcim.common.slug")}</th>
                    <th>{t("catalog.versions")}</th>
                    <th>{t("catalog.kind")}</th>
                    <th>{t("catalog.reserveIpv4")}</th>
                  </tr>
                </thead>
                <tbody>
                  {(tmplQ.data ?? []).map((tmpl) => {
                    const latest = tmpl.versions[tmpl.versions.length - 1];
                    return (
                      <tr key={tmpl.id}>
                        <td>{tmpl.name}</td>
                        <td>{tmpl.slug}</td>
                        <td>{tmpl.versions.map((v) => v.version).join(", ")}</td>
                        <td>{latest?.spec.kind ?? "—"}</td>
                        <td>{latest?.spec.reserve_ipv4 ? t("catalog.yes") : t("catalog.no")}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            ) : null}
          </>
        ) : null}

        {tab === "deploy" ? (
          <>
            <p className={dcimStyles.muted}>{t("catalog.deployHint")}</p>
            <form
              className={dcimStyles.formRow}
              onSubmit={(e) => {
                e.preventDefault();
                if (versionId && (isCluster ? deviceIds.length > 0 : deviceId)) planM.mutate();
              }}
            >
              <label>
                {t("catalog.templateVersion")}
                <select value={versionId} onChange={(e) => setVersionId(e.target.value)}>
                  <option value="">{t("dcim.common.choose")}</option>
                  {versions.map(({ tmpl, v }) => (
                    <option key={v.id} value={v.id}>
                      {tmpl.name} {v.version}
                    </option>
                  ))}
                </select>
              </label>
              {isCluster ? (
                <>
                  <label>
                    {t("platform.cluster")}
                    <input value={clusterName} onChange={(e) => setClusterName(e.target.value)} />
                  </label>
                  <label>
                    {t("platform.kind")}
                    <select value={clusterKind} onChange={(e) => setClusterKind(e.target.value)}>
                      <option value="other">{t("platform.kindOther")}</option>
                      <option value="proxmox">Proxmox</option>
                      <option value="talos">Talos</option>
                    </select>
                  </label>
                  <label>
                    {t("catalog.devices")}
                    <select
                      multiple
                      value={deviceIds.map(String)}
                      onChange={(e) =>
                        setDeviceIds([...e.target.selectedOptions].map((o) => Number(o.value)).filter((n) => n > 0))
                      }
                    >
                      {(devQ.data ?? []).map((d) => (
                        <option key={d.id} value={d.id}>
                          {d.name}
                        </option>
                      ))}
                    </select>
                  </label>
                </>
              ) : (
                <>
                  <label>
                    {t("catalog.device")}
                    <select value={deviceId} onChange={(e) => setDeviceId(e.target.value)}>
                      <option value="">{t("dcim.common.choose")}</option>
                      {(devQ.data ?? []).map((d) => (
                        <option key={d.id} value={d.id}>
                          {d.name}
                        </option>
                      ))}
                    </select>
                  </label>
                  <label>
                    {t("catalog.prefixOptional")}
                    <select value={prefixId} onChange={(e) => setPrefixId(e.target.value)}>
                      <option value="">{t("dcim.common.none")}</option>
                      {(pfxQ.data ?? []).map((p) => (
                        <option key={p.id} value={p.id}>
                          {p.cidr} {p.name}
                        </option>
                      ))}
                    </select>
                  </label>
                </>
              )}
              <button
                type="submit"
                className={dcimStyles.btn}
                disabled={planM.isPending || !versionId || (isCluster ? deviceIds.length === 0 : !deviceId)}
              >
                {t("catalog.plan")}
              </button>
            </form>
            {selected?.plan_json ? (
              <section className={dcimStyles.mfrDetailSection}>
                <h3 className={dcimStyles.mfrDetailSectionTitle}>
                  {t("catalog.planTitle")} #{selected.id} — {selected.status}
                </h3>
                <p>
                  {selected.plan_json.template.name} {selected.plan_json.template.version}
                  {selected.plan_json.cluster?.name
                    ? ` → ${selected.plan_json.cluster.name} (${selected.plan_json.cluster.kind})`
                    : selected.plan_json.device
                      ? ` → ${selected.plan_json.device.name}`
                      : ""}
                </p>
                {selected.plan_json.devices && selected.plan_json.devices.length > 0 ? (
                  <p>{selected.plan_json.devices.map((d) => d.name).join(", ")}</p>
                ) : null}
                {selected.plan_json.prefix ? (
                  <p>
                    {selected.plan_json.prefix.cidr} ({selected.plan_json.prefix.used_count}/
                    {selected.plan_json.prefix.usable_hosts})
                  </p>
                ) : null}
                {selected.plan_json.blockers.length > 0 ? (
                  <p className={dcimStyles.err}>{selected.plan_json.blockers.join(", ")}</p>
                ) : null}
                <ul className={dcimStyles.ipList}>
                  {selected.plan_json.notes.map((n) => (
                    <li key={n}>{n}</li>
                  ))}
                </ul>
                {selected.status === "planned" ? (
                  <button
                    type="button"
                    className={dcimStyles.btn}
                    disabled={!selected.plan_json.can_run || runM.isPending}
                    onClick={() => runM.mutate(selected.id)}
                  >
                    {t("catalog.run")}
                  </button>
                ) : null}
                {selected.steps.length > 0 ? (
                  <ul className={dcimStyles.ipList}>
                    {selected.steps.map((s) => (
                      <li key={s.id}>
                        {s.name}: {s.status}
                        {s.detail ? ` — ${s.detail}` : ""}
                      </li>
                    ))}
                  </ul>
                ) : null}
                {selected.instance ? (
                  <p>
                    {t("catalog.instance")}: {selected.instance.name}
                    {selected.instance.cluster_id != null ? ` (cluster #${selected.instance.cluster_id})` : ""}
                    {selected.instance.ipv4_address_id != null
                      ? ` (IPv4 #${selected.instance.ipv4_address_id})`
                      : ""}
                  </p>
                ) : null}
              </section>
            ) : null}
            {(depQ.data ?? []).length > 0 ? (
              <table className={dcimStyles.table}>
                <thead>
                  <tr>
                    <th>{t("dcim.common.id")}</th>
                    <th>{t("dcim.power.status")}</th>
                    <th>{t("catalog.device")}</th>
                    <th>{t("catalog.canRun")}</th>
                  </tr>
                </thead>
                <tbody>
                  {(depQ.data ?? []).map((d) => (
                    <tr key={d.id}>
                      <td>
                        <button type="button" className={dcimStyles.btnLink} onClick={() => setSelectedId(d.id)}>
                          #{d.id}
                        </button>
                      </td>
                      <td>{d.status}</td>
                      <td>
                        {d.plan_json?.cluster?.name ??
                          d.plan_json?.device?.name ??
                          d.device_id}
                      </td>
                      <td>{d.plan_json?.can_run ? t("catalog.yes") : t("catalog.no")}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : null}
          </>
        ) : null}

        {tab === "instances" ? (
          <>
            <p className={dcimStyles.muted}>{t("catalog.instancesHint")}</p>
            {(instQ.data ?? []).length === 0 && !instQ.isLoading ? (
              <p className={dcimStyles.muted}>{t("catalog.instancesEmpty")}</p>
            ) : null}
            {(instQ.data ?? []).length > 0 ? (
              <table className={dcimStyles.table}>
                <thead>
                  <tr>
                    <th>{t("dcim.common.name")}</th>
                    <th>{t("dcim.common.slug")}</th>
                    <th>{t("catalog.device")}</th>
                    <th>{t("dcim.power.status")}</th>
                    <th>{t("catalog.ipv4")}</th>
                  </tr>
                </thead>
                <tbody>
                  {(instQ.data ?? []).map((i) => (
                    <tr key={i.id}>
                      <td>{i.name}</td>
                      <td>{i.slug}</td>
                      <td>#{i.device_id}</td>
                      <td>{i.status}</td>
                      <td>{i.ipv4_address_id != null ? `#${i.ipv4_address_id}` : "—"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : null}
          </>
        ) : null}
      </Panel>
    </div>
  );
}
