import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { ConfirmModal } from "@/components/ui/ConfirmModal";
import { Panel } from "@/components/ui/Panel";
import * as dcimApi from "@/features/dcim/dcimApi";
import * as ipamApi from "@/features/ipam/ipamApi";
import dcimStyles from "@/features/dcim/dcim.module.css";
import { useI18n } from "@/i18n/I18nProvider";
import { ApiError } from "@/lib/api";
import * as netscanApi from "@/features/networkScans/networkScanApi";

export function JobsTemplatesPage() {
  const { t } = useI18n();
  const qc = useQueryClient();
  const [err, setErr] = useState<string | null>(null);

  const [bindPrefix, setBindPrefix] = useState("");
  const [bindTemplate, setBindTemplate] = useState("");
  const [customSlug, setCustomSlug] = useState("");
  const [customName, setCustomName] = useState("");
  const [customPorts, setCustomPorts] = useState("1883,502,22");
  const [bindingDeleteId, setBindingDeleteId] = useState<number | null>(null);

  const sitesQ = useQuery({ queryKey: ["dcim", "sites"], queryFn: dcimApi.listSites });
  const prefixesQ = useQuery({
    queryKey: ["ipam", "ipv4-prefixes", "all-netscan"],
    queryFn: () => ipamApi.listIpv4Prefixes(),
  });
  const templatesQ = useQuery({
    queryKey: ["network-scans", "templates"],
    queryFn: netscanApi.listNetworkScanTemplates,
  });
  const bindingsQ = useQuery({
    queryKey: ["network-scans", "bindings"],
    queryFn: () => netscanApi.listPrefixBindings(),
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

  const prefixLabel = useMemo(() => {
    const m = new Map<number, string>();
    for (const p of prefixesQ.data ?? []) {
      const site = sitesQ.data?.find((s) => s.id === p.site_id);
      m.set(p.id, `${p.name} (${p.cidr})${site ? ` · ${site.name}` : ""}`);
    }
    return m;
  }, [prefixesQ.data, sitesQ.data]);

  return (
    <>
      <Panel title={t("jobs.templatesPanelTitle")}>
        <p className={dcimStyles.muted} style={{ marginTop: 0 }}>
          {t("jobs.templatesIntro")}
        </p>
        {err ? <p className={dcimStyles.err}>{err}</p> : null}
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
                    {(templatesQ.data ?? []).find((tpl) => tpl.id === b.template_id)?.name ?? `#${b.template_id}`}
                  </td>
                  <td>
                    <div className={dcimStyles.tableIconActions}>
                      <button
                        type="button"
                        className={`${dcimStyles.tableIconBtn} ${dcimStyles.tableIconBtnDanger}`.trim()}
                        title={t("netscan.removeBinding")}
                        aria-label={t("netscan.removeBinding")}
                        disabled={delBinding.isPending}
                        onClick={() => setBindingDeleteId(b.id)}
                      >
                        <i className="fas fa-link-slash" aria-hidden />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p className={dcimStyles.muted}>{t("netscan.bindingsEmpty")}</p>
        )}
      </Panel>
      <ConfirmModal
        open={bindingDeleteId != null}
        onClose={() => {
          if (!delBinding.isPending) setBindingDeleteId(null);
        }}
        title={t("ui.confirmTitle")}
        message={t("netscan.removeBindingConfirm")}
        confirmLabel={t("netscan.removeBinding")}
        cancelLabel={t("dcim.common.cancel")}
        danger
        pending={delBinding.isPending}
        onConfirm={() => {
          if (bindingDeleteId == null) return;
          delBinding.mutate(bindingDeleteId, { onSettled: () => setBindingDeleteId(null) });
        }}
      />
    </>
  );
}
