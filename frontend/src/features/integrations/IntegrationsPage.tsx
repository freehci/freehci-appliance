import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { useSearchParams } from "react-router-dom";
import { Panel } from "@/components/ui/Panel";
import { DcimInnerTabs } from "@/features/dcim/DcimInnerTabs";
import dcimStyles from "@/features/dcim/dcim.module.css";
import { IpamWebhooksSection } from "@/features/ipam/IpamGitopsPanels";
import { useI18n } from "@/i18n/I18nProvider";
import { ApiError } from "@/lib/api";
import { usePlugins } from "@/plugins/PluginContext";
import * as api from "./integrationsApi";

const TABS = new Set(["connections", "webhooks"]);

export function IntegrationsPage() {
  const { t } = useI18n();
  const qc = useQueryClient();
  const plugins = usePlugins();
  const [searchParams, setSearchParams] = useSearchParams();
  const tabParam = searchParams.get("tab");
  const tab = tabParam != null && TABS.has(tabParam) ? tabParam : "connections";
  const setTab = (next: string) => {
    const n = new URLSearchParams(searchParams);
    if (next === "connections") n.delete("tab");
    else n.set("tab", next);
    setSearchParams(n, { replace: true });
  };

  const [err, setErr] = useState<string | null>(null);
  const [name, setName] = useState("");
  const [pluginId, setPluginId] = useState("");
  const [baseUrl, setBaseUrl] = useState("");
  const [cred, setCred] = useState("");

  const connQ = useQuery({ queryKey: ["integration-connections"], queryFn: api.listConnections });
  const conflictQ = useQuery({ queryKey: ["integration-conflicts"], queryFn: api.listConflicts });

  const fail = (e: Error) => setErr(e instanceof ApiError ? e.message : e.message);

  const createM = useMutation({
    mutationFn: () =>
      api.createConnection({
        name: name.trim(),
        plugin_id: pluginId.trim(),
        base_url: baseUrl.trim() || null,
        credential_ref: cred.trim() || null,
      }),
    onSuccess: () => {
      setErr(null);
      setName("");
      setBaseUrl("");
      setCred("");
      void qc.invalidateQueries({ queryKey: ["integration-connections"] });
    },
    onError: fail,
  });
  const delM = useMutation({
    mutationFn: (id: number) => api.deleteConnection(id),
    onSuccess: () => {
      setErr(null);
      void qc.invalidateQueries({ queryKey: ["integration-connections"] });
    },
    onError: fail,
  });

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "1.25rem" }}>
      <Panel title={t("integrations.title")}>
        <p style={{ marginTop: 0 }}>{t("integrations.intro")}</p>
        <DcimInnerTabs
          ariaLabel={t("integrations.tabs")}
          activeId={tab}
          onChange={setTab}
          tabs={[
            { id: "connections", label: t("integrations.tabConnections") },
            { id: "webhooks", label: t("integrations.tabWebhooks") },
          ]}
        />
        {err ? <p className={dcimStyles.err}>{err}</p> : null}

        {tab === "connections" ? (
          <>
            <p className={dcimStyles.muted}>{t("integrations.connectionsHint")}</p>
            {(conflictQ.data ?? []).length > 0 ? (
              <section className={dcimStyles.mfrDetailSection}>
                <h3 className={dcimStyles.mfrDetailSectionTitle}>{t("integrations.conflictsTitle")}</h3>
                <p className={dcimStyles.muted}>{t("integrations.conflictsHint")}</p>
                <ul className={dcimStyles.ipList}>
                  {(conflictQ.data ?? []).map((c) => (
                    <li key={c.id}>
                      {c.identity_type}:{c.namespace} {c.value} → device #{c.device_a_id} / #{c.device_b_id}
                    </li>
                  ))}
                </ul>
              </section>
            ) : null}
            {(connQ.data ?? []).length === 0 && !connQ.isLoading ? (
              <p className={dcimStyles.muted}>{t("integrations.connectionsEmpty")}</p>
            ) : null}
            {(connQ.data ?? []).length > 0 ? (
              <table className={dcimStyles.table}>
                <thead>
                  <tr>
                    <th>{t("dcim.common.name")}</th>
                    <th>{t("integrations.plugin")}</th>
                    <th>{t("integrations.credential")}</th>
                    <th>{t("dcim.power.status")}</th>
                    <th>{t("integrations.lastSync")}</th>
                    <th>{t("dcim.equip.actionsCol")}</th>
                  </tr>
                </thead>
                <tbody>
                  {(connQ.data ?? []).map((c) => (
                    <tr key={c.id}>
                      <td>{c.name}</td>
                      <td>{c.plugin_id}</td>
                      <td>{c.credential_ref ?? "—"}</td>
                      <td>{c.status}</td>
                      <td>{c.last_sync_at ?? t("integrations.neverSynced")}</td>
                      <td>
                        <button type="button" className={dcimStyles.btnLink} onClick={() => delM.mutate(c.id)}>
                          {t("dcim.common.delete")}
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : null}
            <form
              className={dcimStyles.formRow}
              onSubmit={(e) => {
                e.preventDefault();
                createM.mutate();
              }}
            >
              <label>
                {t("dcim.common.name")}
                <input value={name} onChange={(e) => setName(e.target.value)} required />
              </label>
              <label>
                {t("integrations.plugin")}
                <input
                  list="plugin-ids"
                  value={pluginId}
                  onChange={(e) => setPluginId(e.target.value)}
                  placeholder={t("integrations.choosePlugin")}
                  required
                />
                <datalist id="plugin-ids">
                  {plugins.map((p) => (
                    <option key={p.id} value={p.id}>
                      {p.name}
                    </option>
                  ))}
                </datalist>
              </label>
              <label>
                {t("integrations.baseUrl")}
                <input value={baseUrl} onChange={(e) => setBaseUrl(e.target.value)} />
              </label>
              <label>
                {t("integrations.credential")}
                <input
                  value={cred}
                  onChange={(e) => setCred(e.target.value)}
                  placeholder="secret:…"
                />
              </label>
              <button type="submit" className={dcimStyles.btn} disabled={createM.isPending}>
                {t("integrations.addConnection")}
              </button>
            </form>
            <p className={dcimStyles.muted}>{t("integrations.idracHint")}</p>
          </>
        ) : (
          <IpamWebhooksSection />
        )}
      </Panel>
    </div>
  );
}
