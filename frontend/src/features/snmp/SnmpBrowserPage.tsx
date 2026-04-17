import { useMutation, useQuery } from "@tanstack/react-query";
import { useCallback, useEffect, useMemo, useRef, useState, type MouseEvent as ReactMouseEvent } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { SourceCodeEditor } from "@/components/source-editor";
import { useI18n } from "@/i18n/I18nProvider";
import { ApiError } from "@/lib/api";
import * as dcimApi from "@/features/dcim/dcimApi";
import type { DeviceInstance } from "@/features/dcim/types";
import dcimStyles from "@/features/dcim/dcim.module.css";
import { useTheme } from "@/theme/ThemeProvider";
import * as snmpApi from "./snmpApi";
import styles from "./SnmpBrowserPage.module.css";

type TreeItem = snmpApi.SnmpBrowserNode & { depth: number };

function oidAncestorPrefixes(oid: string): string[] {
  const parts = oid.split(".").filter(Boolean);
  if (parts.length <= 1) return [];
  const out: string[] = [];
  for (let i = 1; i < parts.length; i++) {
    out.push(parts.slice(0, i).join("."));
  }
  return out;
}

function nodeMatchesTreeQuery(n: snmpApi.SnmpBrowserNode, q: string): boolean {
  const qf = q.toLowerCase();
  return (
    n.oid.toLowerCase().includes(qf) ||
    n.label.toLowerCase().includes(qf) ||
    (n.module != null && n.module.toLowerCase().includes(qf)) ||
    (n.symbol != null && n.symbol.toLowerCase().includes(qf))
  );
}

function strAttr(obj: Record<string, unknown> | undefined, key: string): string {
  const v = obj?.[key];
  return typeof v === "string" ? v : "";
}

export function SnmpBrowserPage() {
  const { t } = useI18n();
  const { theme } = useTheme();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [err, setErr] = useState<string | null>(null);

  const [selectedOid, setSelectedOid] = useState<string>("1.3.6.1.2.1");
  const [expanded, setExpanded] = useState<Set<string>>(() => new Set(["1", "1.3", "1.3.6", "1.3.6.1"]));
  const [childrenByOid, setChildrenByOid] = useState<Map<string, snmpApi.SnmpBrowserNode[]>>(
    () => new Map(),
  );
  const childrenRef = useRef(childrenByOid);
  childrenRef.current = childrenByOid;

  const [col1Px, setCol1Px] = useState(280);
  const [col3Px, setCol3Px] = useState(320);
  const dragRef = useRef<{ which: "left" | "right"; startX: number; c1: number; c3: number } | null>(null);
  const [splitterActive, setSplitterActive] = useState<"left" | "right" | null>(null);
  const [compact, setCompact] = useState(false);
  const [treeFilterInput, setTreeFilterInput] = useState("");
  const [treeFilterDebounced, setTreeFilterDebounced] = useState("");

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
  const [indexSuffix, setIndexSuffix] = useState("");

  useEffect(() => {
    if (device == null) return;
    setHost(defaultHost);
    setCommunity(defaultCommunity);
  }, [device?.id, defaultHost, defaultCommunity]);

  useEffect(() => {
    const mq = window.matchMedia("(max-width: 1120px)");
    const apply = () => setCompact(mq.matches);
    apply();
    mq.addEventListener("change", apply);
    return () => mq.removeEventListener("change", apply);
  }, []);

  useEffect(() => {
    const id = window.setTimeout(() => setTreeFilterDebounced(treeFilterInput.trim()), 320);
    return () => window.clearTimeout(id);
  }, [treeFilterInput]);

  useEffect(() => {
    const onMove = (e: MouseEvent) => {
      const d = dragRef.current;
      if (!d) return;
      const dx = e.clientX - d.startX;
      if (d.which === "left") {
        setCol1Px(Math.max(160, Math.min(520, d.c1 + dx)));
      } else {
        setCol3Px(Math.max(200, Math.min(620, d.c3 - dx)));
      }
    };
    const onUp = () => {
      dragRef.current = null;
      setSplitterActive(null);
      document.body.style.removeProperty("cursor");
    };
    window.addEventListener("mousemove", onMove);
    window.addEventListener("mouseup", onUp);
    return () => {
      window.removeEventListener("mousemove", onMove);
      window.removeEventListener("mouseup", onUp);
    };
  }, []);

  const onSplitterDown =
    (which: "left" | "right") =>
    (e: ReactMouseEvent): void => {
      e.preventDefault();
      dragRef.current = { which, startX: e.clientX, c1: col1Px, c3: col3Px };
      setSplitterActive(which);
      document.body.style.cursor = "col-resize";
    };

  const loadChildren = useCallback(async (oid: string) => {
    if (childrenRef.current.has(oid)) return;
    const rows = await snmpApi.snmpBrowserChildren({ oid });
    setChildrenByOid((m) => new Map(m).set(oid, rows));
  }, []);

  const rootChildrenQ = useQuery({
    queryKey: ["snmp", "browser", "children", "1"],
    queryFn: () => snmpApi.snmpBrowserChildren({ oid: "1" }),
  });

  const allRoots = rootChildrenQ.data ?? [];

  useEffect(() => {
    if (!treeFilterDebounced) return;
    const q = treeFilterDebounced;
    let cancelled = false;
    const collectNodes = (): snmpApi.SnmpBrowserNode[] => {
      const o: snmpApi.SnmpBrowserNode[] = [...(rootChildrenQ.data ?? [])];
      for (const kids of childrenRef.current.values()) {
        o.push(...kids);
      }
      return o;
    };
    void (async () => {
      for (let round = 0; round < 5 && !cancelled; round++) {
        const expandOids = new Set<string>(["1"]);
        const rawOid = q.replace(/\s/g, "");
        if (/^[\d.]+$/.test(rawOid)) {
          const parts = rawOid.split(".").filter(Boolean);
          for (let i = 1; i < parts.length; i++) {
            expandOids.add(parts.slice(0, i).join("."));
          }
        }
        for (const n of collectNodes()) {
          if (nodeMatchesTreeQuery(n, q)) {
            for (const a of oidAncestorPrefixes(n.oid)) expandOids.add(a);
          }
        }
        const ordered = [...expandOids].sort(
          (a, b) => a.split(".").length - b.split(".").length || a.localeCompare(b),
        );
        for (const o of ordered) {
          if (cancelled) return;
          await loadChildren(o);
        }
        if (cancelled) return;
        setExpanded((prev) => new Set([...prev, ...expandOids]));
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [treeFilterDebounced, loadChildren, rootChildrenQ.data]);

  const mibQ = searchParams.get("mib")?.trim() ?? "";
  const modQ = searchParams.get("module")?.trim() ?? "";

  useEffect(() => {
    if (!mibQ && !modQ) return;
    let cancelled = false;
    void (async () => {
      try {
        setErr(null);
        const r = await snmpApi.snmpBrowserLocate({ mib: mibQ || undefined, module: modQ || undefined });
        if (cancelled) return;
        if (!r.found || !r.oid) {
          setErr(r.error ?? t("snmp.browser.locateFail"));
          setSelectedOid("1");
          setExpanded(new Set(["1"]));
          return;
        }
        setSelectedOid(r.oid);
        const anc = r.ancestor_oids ?? [];
        setExpanded(new Set<string>(["1", ...anc]));
        const ordered = ["1", ...anc];
        for (const o of ordered) {
          await loadChildren(o);
        }
        const parts = r.oid.split(".").filter((x) => x !== "");
        if (parts.length > 1) {
          const parentOid = parts.slice(0, -1).join(".");
          await loadChildren(parentOid);
        }
      } catch (e) {
        if (!cancelled) {
          setErr(e instanceof ApiError ? e.message : String(e));
        }
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [mibQ, modQ, loadChildren, t]);

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

  const directMatchOids = useMemo(() => {
    if (!treeFilterDebounced) return null;
    const q = treeFilterDebounced;
    return new Set(flatTree.filter((n) => nodeMatchesTreeQuery(n, q)).map((n) => n.oid));
  }, [flatTree, treeFilterDebounced]);

  const displayTree = useMemo(() => {
    if (!treeFilterDebounced) return flatTree;
    const direct = new Set(flatTree.filter((n) => nodeMatchesTreeQuery(n, treeFilterDebounced)).map((n) => n.oid));
    const show = new Set<string>();
    for (const oid of direct) {
      show.add(oid);
      for (const a of oidAncestorPrefixes(oid)) show.add(a);
    }
    return flatTree.filter((n) => show.has(n.oid));
  }, [flatTree, treeFilterDebounced]);

  const defQ = useQuery({
    queryKey: ["snmp", "browser", "definition", selectedOid],
    queryFn: () => snmpApi.snmpBrowserDefinition({ oid: selectedOid }),
  });

  const defHighlightRange = useMemo(() => {
    const d = defQ.data;
    const a = d?.highlight_start_line;
    const b = d?.highlight_end_line;
    if (a == null || b == null || a < 1 || b < a) return null;
    return { start: a, end: b };
  }, [defQ.data]);

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

  const onClose = useCallback(() => {
    navigate("/snmp/tools", { replace: true });
  }, [navigate]);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  const themeClass = theme === "dark" ? styles.themeMonacoDark : styles.themeMonacoLight;
  const gridCols = compact
    ? `${col1Px}px 6px minmax(200px, 1fr)`
    : `${col1Px}px 6px minmax(200px, 1fr) 6px ${col3Px}px`;

  const treePane = (
    <section className={styles.pane}>
      <div className={`${styles.paneHeader} ${styles.paneHeaderWithSearch}`.trim()}>
        <span className={styles.paneHeaderTitle}>{t("snmp.browser.treeTitle")}</span>
        <div className={styles.treeSearchWrap}>
          <input
            type="search"
            className={styles.treeSearchInput}
            value={treeFilterInput}
            onChange={(e) => setTreeFilterInput(e.target.value)}
            placeholder={t("snmp.browser.treeSearchPlaceholder")}
            aria-label={t("snmp.browser.treeSearchLabel")}
            autoComplete="off"
            spellCheck={false}
          />
        </div>
      </div>
      <div className={styles.paneBody}>
        {rootChildrenQ.isLoading ? <p className={dcimStyles.muted}>{t("dcim.common.loading")}</p> : null}
        {rootChildrenQ.isError ? (
          <p className={dcimStyles.err}>{(rootChildrenQ.error as Error).message}</p>
        ) : null}
        <div className={styles.tree}>
          {displayTree.map((n) => {
            const isActive = n.oid === selectedOid;
            const pad = `${n.depth * 0.9}rem`;
            const isMatch = Boolean(treeFilterDebounced && directMatchOids?.has(n.oid));
            return (
              <div
                key={n.oid}
                className={`${styles.treeRow} ${isActive ? styles.treeRowActive : ""} ${
                  isMatch ? styles.treeRowMatch : ""
                }`.trim()}
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
  );

  const editorPane = (
    <section className={styles.pane}>
      <div className={styles.paneHeader}>{t("snmp.browser.editorTitle")}</div>
      <div className={`${styles.paneBody} ${styles.editorBody}`.trim()}>
        {defQ.isLoading ? <p className={dcimStyles.muted}>{t("dcim.common.loading")}</p> : null}
        {defQ.isError ? <p className={dcimStyles.err}>{(defQ.error as Error).message}</p> : null}
        <div className={styles.editorBox}>
          <SourceCodeEditor
            value={defQ.data?.text ?? ""}
            filename={defQ.data?.source_filename ?? `${defQ.data?.module ?? "mib"}.mib`}
            path={`inmemory://snmp-mib/${encodeURIComponent(selectedOid)}.mib`}
            highlightLineRange={defHighlightRange}
            readOnly
          />
        </div>
      </div>
    </section>
  );

  const inspectorPane = (
    <section className={`${styles.pane} ${styles.paneInspector}`.trim()}>
      <div className={styles.paneHeader}>{t("snmp.browser.inspectorTitle")}</div>
      <div className={styles.paneBody}>
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
  );

  return (
    <div
      className={styles.backdrop}
      role="presentation"
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div
        className={styles.dialog}
        role="dialog"
        aria-modal="true"
        aria-label={t("snmp.tabBrowser")}
        onClick={(e) => e.stopPropagation()}
      >
        <div className={styles.header}>
          <h2 className={styles.title}>{t("snmp.tabBrowser")}</h2>
          <button
            type="button"
            className={dcimStyles.btnMuted}
            onClick={onClose}
            aria-label={t("snmp.mibSourceCloseAria")}
          >
            ×
          </button>
        </div>

        <div className={`${styles.bodyWrap} ${styles.bodyWrapThemed} ${themeClass}`.trim()}>
          <div
            className={styles.splitGrid}
            style={{
              gridTemplateColumns: gridCols,
            }}
          >
            {treePane}
            <div
              className={`${styles.splitter} ${splitterActive === "left" ? styles.splitterDragging : ""}`.trim()}
              onMouseDown={onSplitterDown("left")}
              role="separator"
              aria-orientation="vertical"
              aria-label={t("snmp.browser.splitterLeft")}
            />
            {editorPane}
            {compact ? null : (
              <>
                <div
                  className={`${styles.splitter} ${splitterActive === "right" ? styles.splitterDragging : ""}`.trim()}
                  onMouseDown={onSplitterDown("right")}
                  role="separator"
                  aria-orientation="vertical"
                  aria-label={t("snmp.browser.splitterRight")}
                />
                {inspectorPane}
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
