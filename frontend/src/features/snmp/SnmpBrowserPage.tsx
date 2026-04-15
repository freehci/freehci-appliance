import { useMutation, useQuery } from "@tanstack/react-query";
import { useCallback, useEffect, useMemo, useState } from "react";
import { SourceCodeEditor } from "@/components/source-editor";
import { useI18n } from "@/i18n/I18nProvider";
import { ApiError } from "@/lib/api";
import * as dcimApi from "@/features/dcim/dcimApi";
import type { DeviceInstance } from "@/features/dcim/types";
import dcimStyles from "@/features/dcim/dcim.module.css";
import * as snmpApi from "./snmpApi";
import styles from "./SnmpBrowserPage.module.css";

type TreeItem = snmpApi.SnmpBrowserNode & { depth: number };

function strAttr(obj: Record<string, unknown> | undefined, key: string): string {
  const v = obj?.[key];
  return typeof v === "string" ? v : "";
}

export function SnmpBrowserPage() {
  const { t } = useI18n();
  const [err, setErr] = useState<string | null>(null);

  const [selectedOid, setSelectedOid] = useState<string>("1.3.6.1.2.1"); // mgmt
  const [expanded, setExpanded] = useState<Set<string>>(() => new Set(["1", "1.3", "1.3.6", "1.3.6.1"]));
  const [childrenByOid, setChildrenByOid] = useState<Map<string, snmpApi.SnmpBrowserNode[]>>(
    () => new Map(),
  );

  const devicesQ = useQuery({ queryKey: ["dcim", "devices"], queryFn: dcimApi.listDevices });
  const [deviceId, setDeviceId] = useState<string>("");
  const device: DeviceInstance | null = useMemo(() => {
    const rows = devicesQ.data ?? [];
    const id = Number(deviceId);
    if (!Number.isFinite(id) || id < 1) return null;
    return rows.find((d) => d.id === id) ?? null;
  }, [devicesQ.data, deviceId]);

  const defaultHost = useMemo(() => {
    const a = (device?.attributes ?? {}) as Record<string, unknown>;
    return strAttr(a, "snmp_host");
  }, [device?.attributes]);

  const defaultCommunity = useMemo(() => {
    const a = (device?.attributes ?? {}) as Record<string, unknown>;
    return strAttr(a, "snmp_community_read") || strAttr(a, "snmp_community") || "public";
  }, [device?.attributes]);

  const [host, setHost] = useState("");
  const [community, setCommunity] = useState("public");
  const [port, setPort] = useState("161");
  const [indexSuffix, setIndexSuffix] = useState(""); // f.eks. ifIndex

  // Sync defaults when device changes.
  useEffect(() => {
    if (device == null) return;
    setHost(defaultHost);
    setCommunity(defaultCommunity);
  }, [device?.id, defaultHost, defaultCommunity]);

  const loadChildren = useCallback(
    async (oid: string) => {
      if (childrenByOid.has(oid)) return;
      const rows = await snmpApi.snmpBrowserChildren({ oid });
      setChildrenByOid((m) => new Map(m).set(oid, rows));
    },
    [childrenByOid],
  );

  const rootChildrenQ = useQuery({
    queryKey: ["snmp", "browser", "children", "1"],
    queryFn: () => snmpApi.snmpBrowserChildren({ oid: "1" }),
  });

  const allRoots = rootChildrenQ.data ?? [];

  const flatTree = useMemo(() => {
    const out: TreeItem[] = [];
    const visit = (oid: string, depth: number, node: snmpApi.SnmpBrowserNode) => {
      out.push({ ...node, depth });
      if (!expanded.has(oid)) return;
      const kids = childrenByOid.get(oid) ?? [];
      for (const k of kids) visit(k.oid, depth + 1, k);
    };
    for (const n of allRoots) visit(n.oid, 0, n);
    return out;
  }, [allRoots, expanded, childrenByOid]);

  const defQ = useQuery({
    queryKey: ["snmp", "browser", "definition", selectedOid],
    queryFn: () => snmpApi.snmpBrowserDefinition({ oid: selectedOid }),
  });

  const effectiveOid = useMemo(() => {
    const idx = indexSuffix.trim();
    if (idx === "") return selectedOid;
    if (/^\d+$/.test(idx)) return `${selectedOid}.${idx}`;
    return selectedOid;
  }, [selectedOid, indexSuffix]);

  const probeMut = useMutation({
    mutationFn: () =>
      snmpApi.snmpProbe({
        host: host.trim(),
        port: Number(port) || 161,
        community: community.trim() || "public",
        oid: effectiveOid,
        operation: "get",
      }),
    onSuccess: () => setErr(null),
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const invMut = useMutation({
    mutationFn: () =>
      snmpApi.snmpInventory({
        host: host.trim(),
        port: Number(port) || 161,
        community: community.trim() || "public",
      }),
    onSuccess: () => setErr(null),
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const inventoryIfaces = invMut.data?.interfaces ?? [];

  const handleToggle = useCallback(
    async (n: snmpApi.SnmpBrowserNode) => {
      if (!n.has_children) return;
      await loadChildren(n.oid);
      setExpanded((prev) => {
        const next = new Set(prev);
        if (next.has(n.oid)) next.delete(n.oid);
        else next.add(n.oid);
        return next;
      });
    },
    [loadChildren],
  );

  const handleRowClick = useCallback(
    async (n: snmpApi.SnmpBrowserNode) => {
      setSelectedOid(n.oid);
      if (n.has_children) await loadChildren(n.oid);
    },
    [loadChildren],
  );

  return (
    <div className={styles.layout}>
      <section className={styles.panel}>
        <h3 className={styles.panelTitle}>{t("snmp.browser.treeTitle")}</h3>
        <div className={styles.panelBody}>
          {rootChildrenQ.isLoading ? <p className={dcimStyles.muted}>{t("dcim.common.loading")}</p> : null}
          {rootChildrenQ.isError ? (
            <p className={dcimStyles.err}>{(rootChildrenQ.error as Error).message}</p>
          ) : null}
          <div className={styles.tree}>
            {flatTree.map((n) => {
              const isActive = n.oid === selectedOid;
              const pad = `${n.depth * 0.9}rem`;
              return (
                <div
                  key={n.oid}
                  className={`${styles.treeRow} ${isActive ? styles.treeRowActive : ""}`.trim()}
                  style={{ paddingLeft: pad }}
                  onClick={() => void handleRowClick(n)}
                  title={n.oid}
                  role="button"
                  tabIndex={0}
                >
                  <span
                    className={styles.twisty}
                    onClick={(e) => {
                      e.stopPropagation();
                      void handleToggle(n);
                    }}
                    title={n.has_children ? t("snmp.browser.toggle") : ""}
                  >
                    {n.has_children ? (expanded.has(n.oid) ? "▾" : "▸") : "·"}
                  </span>
                  <span>{n.label}</span>
                  <span className={styles.oidMuted}>{n.oid}</span>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      <section className={styles.panel}>
        <h3 className={styles.panelTitle}>{t("snmp.browser.editorTitle")}</h3>
        <div className={styles.panelBody}>
          {defQ.isLoading ? <p className={dcimStyles.muted}>{t("dcim.common.loading")}</p> : null}
          {defQ.isError ? <p className={dcimStyles.err}>{(defQ.error as Error).message}</p> : null}
          <div className={styles.editorBox}>
            <SourceCodeEditor
              value={defQ.data?.text ?? ""}
              filename={(defQ.data?.module ?? "mib") + ".mib"}
              path={`inmemory://snmp-mib/${encodeURIComponent(selectedOid)}.mib`}
              readOnly
            />
          </div>
        </div>
      </section>

      <section className={styles.panel}>
        <h3 className={styles.panelTitle}>{t("snmp.browser.inspectorTitle")}</h3>
        <div className={styles.panelBody}>
          {err ? <p className={dcimStyles.err}>{err}</p> : null}

          <dl className={styles.kv}>
            <dt>{t("snmp.browser.selected")}</dt>
            <dd>
              <code>{selectedOid}</code>
            </dd>
            <dt>{t("snmp.browser.module")}</dt>
            <dd>{defQ.data?.module ?? "—"}</dd>
            <dt>{t("snmp.browser.symbol")}</dt>
            <dd>{defQ.data?.symbol ?? "—"}</dd>
          </dl>

          <div className={dcimStyles.formRow} style={{ alignItems: "flex-end" }}>
            <label style={{ minWidth: "12rem" }}>
              {t("snmp.browser.device")}
              <select
                className={dcimStyles.controlSelect}
                value={deviceId}
                onChange={(e) => setDeviceId(e.target.value)}
              >
                <option value="">{t("snmp.browser.deviceNone")}</option>
                {(devicesQ.data ?? []).map((d) => (
                  <option key={d.id} value={String(d.id)}>
                    {d.name} (#{d.id})
                  </option>
                ))}
              </select>
            </label>
            <label style={{ minWidth: "12rem" }}>
              {t("snmp.probeHost")}
              <input value={host} onChange={(e) => setHost(e.target.value)} placeholder="192.0.2.10" />
            </label>
            <label style={{ minWidth: "10rem" }}>
              {t("snmp.probeCommunity")}
              <input value={community} onChange={(e) => setCommunity(e.target.value)} />
            </label>
            <label style={{ minWidth: "7rem" }}>
              {t("snmp.probePort")}
              <input value={port} onChange={(e) => setPort(e.target.value)} />
            </label>
          </div>

          <div className={dcimStyles.formRow} style={{ alignItems: "flex-end" }}>
            <label style={{ minWidth: "10rem" }}>
              {t("snmp.browser.indexSuffix")}
              <input
                value={indexSuffix}
                onChange={(e) => setIndexSuffix(e.target.value)}
                placeholder={t("snmp.browser.indexSuffixPlaceholder")}
              />
            </label>
            <button
              type="button"
              className={dcimStyles.btnMuted}
              disabled={invMut.isPending || host.trim() === ""}
              onClick={() => invMut.mutate()}
              title={t("snmp.browser.fetchIfacesHint")}
            >
              {invMut.isPending ? "…" : t("snmp.browser.fetchIfaces")}
            </button>
            <label style={{ minWidth: "14rem" }}>
              {t("snmp.browser.iface")}
              <select
                className={dcimStyles.controlSelect}
                value={indexSuffix}
                onChange={(e) => setIndexSuffix(e.target.value)}
                disabled={!inventoryIfaces.length}
              >
                <option value="">{t("snmp.browser.ifaceNone")}</option>
                {inventoryIfaces.map((x) => (
                  <option key={x.if_index} value={String(x.if_index)}>
                    {x.name} (ifIndex {x.if_index})
                  </option>
                ))}
              </select>
            </label>
          </div>

          <div className={dcimStyles.formRow} style={{ alignItems: "center" }}>
            <button
              type="button"
              className={dcimStyles.btn}
              disabled={probeMut.isPending || host.trim() === "" || selectedOid.trim() === ""}
              onClick={() => probeMut.mutate()}
            >
              {probeMut.isPending ? "…" : t("snmp.browser.pollNow")}
            </button>
            <span className={dcimStyles.muted}>
              {t("snmp.browser.effectiveOid")} <code>{effectiveOid}</code>
            </span>
          </div>

          {probeMut.data ? (
            probeMut.data.ok ? (
              <div className={dcimStyles.codeBlock} style={{ maxWidth: "100%" }}>
                {(probeMut.data.varbinds ?? []).slice(0, 1).map((vb) => (
                  <div key={vb.oid}>
                    <div className={dcimStyles.muted}>{vb.oid}</div>
                    <div>{vb.value}</div>
                  </div>
                ))}
              </div>
            ) : (
              <p className={dcimStyles.err}>{probeMut.data.error ?? t("snmp.probeFail")}</p>
            )
          ) : null}
        </div>
      </section>
    </div>
  );
}

