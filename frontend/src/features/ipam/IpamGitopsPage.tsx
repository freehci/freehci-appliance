import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { Panel } from "@/components/ui/Panel";
import * as dcimApi from "@/features/dcim/dcimApi";
import dcimStyles from "@/features/dcim/dcim.module.css";
import { useI18n } from "@/i18n/I18nProvider";
import { ApiError } from "@/lib/api";
import * as ipamApi from "./ipamApi";

const HOOK_EVENTS = ["prefix.created", "prefix.updated", "address.ensured", "address.released"] as const;

export function IpamGitopsPage() {
  const { t } = useI18n();
  const qc = useQueryClient();
  const [err, setErr] = useState<string | null>(null);
  const [siteId, setSiteId] = useState("");
  const [hookUrl, setHookUrl] = useState("");
  const [hookSecret, setHookSecret] = useState("");
  const [deliveriesFor, setDeliveriesFor] = useState<number | null>(null);

  const sid = siteId === "" ? undefined : Number(siteId);
  const sitesQ = useQuery({ queryKey: ["dcim", "sites"], queryFn: dcimApi.listSites });
  const auditQ = useQuery({
    queryKey: ["ipam", "audit", sid ?? "all"],
    queryFn: () => ipamApi.listIpamAudit({ site_id: sid, limit: 80 }),
  });
  const driftQ = useQuery({
    queryKey: ["ipam", "drift", sid],
    queryFn: () => ipamApi.getSiteDrift(sid!),
    enabled: sid != null,
  });
  const hooksQ = useQuery({ queryKey: ["ipam", "webhooks"], queryFn: ipamApi.listIpamWebhooks });
  const deliveriesQ = useQuery({
    queryKey: ["ipam", "webhook-deliveries", deliveriesFor],
    queryFn: () => ipamApi.listIpamWebhookDeliveries(deliveriesFor!),
    enabled: deliveriesFor != null,
  });

  const siteNameById = useMemo(() => {
    const m = new Map<number, string>();
    for (const s of sitesQ.data ?? []) m.set(s.id, s.name);
    return m;
  }, [sitesQ.data]);

  const exportM = useMutation({
    mutationFn: (format: "yaml" | "json") => ipamApi.exportSiteIpam(sid!, format),
    onSuccess: (text, format) => {
      const blob = new Blob([text], { type: format === "yaml" ? "application/yaml" : "application/json" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `ipam-site-${sid}.${format}`;
      a.click();
      URL.revokeObjectURL(url);
      setErr(null);
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const createHook = useMutation({
    mutationFn: () =>
      ipamApi.createIpamWebhook({
        url: hookUrl.trim(),
        secret: hookSecret.trim() || null,
        events: [...HOOK_EVENTS],
      }),
    onSuccess: () => {
      setHookUrl("");
      setHookSecret("");
      setErr(null);
      void qc.invalidateQueries({ queryKey: ["ipam", "webhooks"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const delHook = useMutation({
    mutationFn: (id: number) => ipamApi.deleteIpamWebhook(id),
    onSuccess: () => {
      setDeliveriesFor(null);
      void qc.invalidateQueries({ queryKey: ["ipam", "webhooks"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  return (
    <Panel title={t("ipam.gitops.title")}>
      <p className={dcimStyles.muted}>{t("ipam.gitops.intro")}</p>
      {err ? <p className={dcimStyles.err}>{err}</p> : null}

      <div className={dcimStyles.formRow}>
        <label>
          {t("ipam.ipv4.filterSite")}
          <select value={siteId} onChange={(e) => setSiteId(e.target.value)}>
            <option value="">{t("ipam.ipv4.allSites")}</option>
            {(sitesQ.data ?? []).map((s) => (
              <option key={s.id} value={String(s.id)}>
                {s.name}
              </option>
            ))}
          </select>
        </label>
      </div>

      <section className={dcimStyles.mfrDetailSection}>
        <h3 className={dcimStyles.mfrDetailSectionTitle}>{t("ipam.gitops.exportTitle")}</h3>
        <p className={dcimStyles.muted}>{t("ipam.gitops.exportHint")}</p>
        <div className={dcimStyles.formRow}>
          <button
            type="button"
            className={dcimStyles.btn}
            disabled={sid == null || exportM.isPending}
            onClick={() => exportM.mutate("yaml")}
          >
            {t("ipam.gitops.exportYaml")}
          </button>
          <button
            type="button"
            className={dcimStyles.btn}
            disabled={sid == null || exportM.isPending}
            onClick={() => exportM.mutate("json")}
          >
            {t("ipam.gitops.exportJson")}
          </button>
        </div>
      </section>

      <section className={dcimStyles.mfrDetailSection}>
        <h3 className={dcimStyles.mfrDetailSectionTitle}>{t("ipam.gitops.driftTitle")}</h3>
        <p className={dcimStyles.muted}>{t("ipam.gitops.driftHint")}</p>
        {sid == null ? <p className={dcimStyles.muted}>{t("ipam.gitops.chooseSite")}</p> : null}
        {driftQ.isError ? <p className={dcimStyles.err}>{(driftQ.error as Error).message}</p> : null}
        {driftQ.data ? (
          driftQ.data.prefixes.length === 0 ? (
            <p className={dcimStyles.muted}>{t("ipam.gitops.driftEmpty")}</p>
          ) : (
            <table className={dcimStyles.table}>
              <thead>
                <tr>
                  <th>{t("ipam.ipv4.cidr")}</th>
                  <th>{t("ipam.gitops.aligned")}</th>
                  <th>{t("ipam.gitops.seenUnmanaged")}</th>
                  <th>{t("ipam.gitops.reservedMissing")}</th>
                </tr>
              </thead>
              <tbody>
                {driftQ.data.prefixes.map((p) => (
                  <tr key={p.prefix_id}>
                    <td>
                      <code>{p.cidr}</code>
                    </td>
                    <td>{p.aligned.length}</td>
                    <td>{p.seen_unmanaged.map((a) => a.address).join(", ") || "—"}</td>
                    <td>{p.reserved_missing.map((a) => a.address).join(", ") || "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )
        ) : null}
      </section>

      <section className={dcimStyles.mfrDetailSection}>
        <h3 className={dcimStyles.mfrDetailSectionTitle}>{t("ipam.gitops.webhooksTitle")}</h3>
        <p className={dcimStyles.muted}>{t("ipam.gitops.webhooksHint")}</p>
        <form
          className={dcimStyles.formRow}
          style={{ flexWrap: "wrap" }}
          onSubmit={(e) => {
            e.preventDefault();
            if (!hookUrl.trim()) return;
            createHook.mutate();
          }}
        >
          <label>
            URL
            <input value={hookUrl} onChange={(e) => setHookUrl(e.target.value)} placeholder="https://…" required />
          </label>
          <label>
            {t("ipam.gitops.webhookSecret")}
            <input value={hookSecret} onChange={(e) => setHookSecret(e.target.value)} />
          </label>
          <button type="submit" className={dcimStyles.btn} disabled={createHook.isPending}>
            {t("dcim.common.add")}
          </button>
        </form>
        {hooksQ.data && hooksQ.data.length > 0 ? (
          <table className={dcimStyles.table}>
            <thead>
              <tr>
                <th>URL</th>
                <th>{t("ipam.gitops.status")}</th>
                <th>{t("ipam.ipv4.actionsCol")}</th>
              </tr>
            </thead>
            <tbody>
              {hooksQ.data.map((h) => (
                <tr key={h.id}>
                  <td>{h.url}</td>
                  <td>{h.enabled ? t("ipam.scan.up") : t("ipam.scan.down")}</td>
                  <td>
                    <button type="button" className={dcimStyles.btnLink} onClick={() => setDeliveriesFor(h.id)}>
                      {t("ipam.gitops.deliveries")}
                    </button>{" "}
                    <button type="button" className={dcimStyles.btnLink} onClick={() => delHook.mutate(h.id)}>
                      {t("dcim.common.delete")}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p className={dcimStyles.muted}>{t("ipam.gitops.webhooksEmpty")}</p>
        )}
        {deliveriesQ.data && deliveriesQ.data.length > 0 ? (
          <table className={dcimStyles.table}>
            <thead>
              <tr>
                <th>{t("ipam.gitops.event")}</th>
                <th>{t("ipam.gitops.status")}</th>
                <th>{t("ipam.gitops.error")}</th>
              </tr>
            </thead>
            <tbody>
              {deliveriesQ.data.map((d) => (
                <tr key={d.id}>
                  <td>{d.event}</td>
                  <td>
                    {d.status}
                    {d.status_code != null ? ` ${d.status_code}` : ""}
                  </td>
                  <td>{d.error ?? "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : null}
      </section>

      <section className={dcimStyles.mfrDetailSection}>
        <h3 className={dcimStyles.mfrDetailSectionTitle}>{t("ipam.gitops.auditTitle")}</h3>
        <p className={dcimStyles.muted}>{t("ipam.gitops.auditHint")}</p>
        {auditQ.data && auditQ.data.length > 0 ? (
          <table className={dcimStyles.table}>
            <thead>
              <tr>
                <th>{t("ipam.gitops.when")}</th>
                <th>{t("ipam.gitops.actor")}</th>
                <th>{t("ipam.gitops.action")}</th>
                <th>{t("ipam.gitops.resource")}</th>
                <th>{t("ipam.ipv4.site")}</th>
              </tr>
            </thead>
            <tbody>
              {auditQ.data.map((e) => (
                <tr key={e.id}>
                  <td>{new Date(e.created_at).toLocaleString()}</td>
                  <td>{e.actor_name ?? e.actor_type}</td>
                  <td>{e.action}</td>
                  <td>
                    {e.resource_type}
                    {e.resource_id != null ? ` #${e.resource_id}` : ""}
                  </td>
                  <td>{e.site_id != null ? (siteNameById.get(e.site_id) ?? `#${e.site_id}`) : "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p className={dcimStyles.muted}>{t("ipam.gitops.auditEmpty")}</p>
        )}
      </section>
    </Panel>
  );
}
