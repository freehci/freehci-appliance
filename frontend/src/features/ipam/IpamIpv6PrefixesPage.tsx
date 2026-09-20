import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useId, useMemo, useState } from "react";
import { ConfirmModal } from "@/components/ui/ConfirmModal";
import { Panel } from "@/components/ui/Panel";
import * as dcimApi from "@/features/dcim/dcimApi";
import dcimStyles from "@/features/dcim/dcim.module.css";
import { useI18n } from "@/i18n/I18nProvider";
import { ApiError } from "@/lib/api";
import { IpamFamilyTabs } from "./IpamFamilyTabs";
import * as ipamApi from "./ipamApi";
import type { Ipv6Prefix } from "./types";
import { OVERLAP_POLICIES, PREFIX_ROLES, PREFIX_STATUSES } from "./types";
import { buildIpv6ChildrenByParent, flattenIpv6Tree, ipv6EqualSplitOptions, parseIpv6PrefixLen } from "./ipv6PrefixTree";

const SPLIT_PREVIEW_MAX = 48;

export function IpamIpv6PrefixesPage() {
  const { t } = useI18n();
  const qc = useQueryClient();
  const splitTitleId = useId();
  const [err, setErr] = useState<string | null>(null);
  const [filterSite, setFilterSite] = useState("");
  const [newSite, setNewSite] = useState("");
  const [newName, setNewName] = useState("");
  const [newCidr, setNewCidr] = useState("");
  const [newRole, setNewRole] = useState("active");
  const [newStatus, setNewStatus] = useState("active");
  const [newOverlap, setNewOverlap] = useState("");
  const [newDualStack, setNewDualStack] = useState("");
  const [newVrf, setNewVrf] = useState("");
  const [explore, setExplore] = useState<Ipv6Prefix | null>(null);
  const [expanded, setExpanded] = useState<Set<number>>(() => new Set());
  const [splitTarget, setSplitTarget] = useState<Ipv6Prefix | null>(null);
  const [splitLen, setSplitLen] = useState<number | null>(null);
  const [splitMigrate, setSplitMigrate] = useState(true);
  const [splitErr, setSplitErr] = useState<string | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<Ipv6Prefix | null>(null);
  const [reqNote, setReqNote] = useState("");

  const siteIdFilter = filterSite === "" ? undefined : Number(filterSite);
  const sitesQ = useQuery({ queryKey: ["dcim", "sites"], queryFn: dcimApi.listSites });
  const vrfsQ = useQuery({ queryKey: ["ipam", "vrfs", "all-for-prefixes"], queryFn: () => ipamApi.listIpamVrfs() });
  const prefixesQ = useQuery({
    queryKey: ["ipam", "ipv6-prefixes", siteIdFilter ?? "all"],
    queryFn: () => ipamApi.listIpv6Prefixes(siteIdFilter),
  });

  const gridEnabled = explore != null && (parseIpv6PrefixLen(explore.cidr) ?? 0) >= 118;
  const gridQ = useQuery({
    queryKey: ["ipam", "ipv6-grid", explore?.id],
    queryFn: () => ipamApi.getIpv6PrefixAddressGrid(explore!.id),
    enabled: gridEnabled,
    refetchInterval: (q) => {
      const st = q.state.data?.active_scan?.status;
      return st === "pending" || st === "running" ? 1500 : false;
    },
  });
  const rangesQ = useQuery({
    queryKey: ["ipam", "ipv6-ranges", explore?.id],
    queryFn: () => ipamApi.getIpv6AvailableRanges(explore!.id),
    enabled: explore != null && !gridEnabled,
  });
  const addrsQ = useQuery({
    queryKey: ["ipam", "ipv6-addresses", explore?.id],
    queryFn: () => ipamApi.listIpv6Addresses({ ipv6_prefix_id: explore!.id, limit: 200 }),
    enabled: explore != null,
  });
  const scansQ = useQuery({
    queryKey: ["ipam", "ipv6-scans", explore?.id],
    queryFn: () => ipamApi.listSubnetScans({ ipv6_prefix_id: explore!.id, limit: 20 }),
    enabled: explore != null,
  });

  const splitOpts = useMemo(() => (splitTarget ? ipv6EqualSplitOptions(splitTarget.cidr) : []), [splitTarget]);
  useEffect(() => {
    setSplitLen(splitOpts[0]?.newPrefixLen ?? null);
    setSplitErr(null);
  }, [splitTarget, splitOpts]);

  const splitPreviewQ = useQuery({
    queryKey: ["ipam", "ipv6-split-preview", splitTarget?.id, splitLen, splitMigrate],
    queryFn: () =>
      ipamApi.ipv6PrefixSplitEqual(splitTarget!.id, {
        new_prefix_len: splitLen!,
        migrate_inventory: splitMigrate,
        dry_run: true,
      }),
    enabled: splitTarget != null && splitLen != null,
  });

  const tree = useMemo(() => buildIpv6ChildrenByParent(prefixesQ.data ?? []), [prefixesQ.data]);
  const visible = useMemo(
    () => flattenIpv6Tree(tree.roots, tree.childrenByParentId, expanded),
    [tree, expanded],
  );
  const childrenOfExplore = explore ? (tree.childrenByParentId.get(explore.id) ?? []) : [];

  const siteNameById = useMemo(() => {
    const m = new Map<number, string>();
    for (const s of sitesQ.data ?? []) m.set(s.id, s.name);
    return m;
  }, [sitesQ.data]);

  const invalidate = () => {
    void qc.invalidateQueries({ queryKey: ["ipam", "ipv6-prefixes"] });
    void qc.invalidateQueries({ queryKey: ["ipam", "ipv6-addresses"] });
    void qc.invalidateQueries({ queryKey: ["ipam", "ipv6-grid"] });
    void qc.invalidateQueries({ queryKey: ["ipam", "ipv6-ranges"] });
    void qc.invalidateQueries({ queryKey: ["ipam", "ipv6-scans"] });
  };

  const createM = useMutation({
    mutationFn: () =>
      ipamApi.createIpv6Prefix({
        site_id: Number(newSite),
        name: newName.trim(),
        cidr: newCidr.trim(),
        role: newRole,
        status: newStatus,
        overlap_policy: newOverlap || undefined,
        dual_stack_group_id: newDualStack.trim() === "" ? undefined : Number(newDualStack),
        vrf_id: newVrf === "" ? undefined : Number(newVrf),
      }),
    onSuccess: () => {
      setNewName("");
      setNewCidr("");
      setNewDualStack("");
      setErr(null);
      invalidate();
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const delM = useMutation({
    mutationFn: (id: number) => ipamApi.deleteIpv6Prefix(id, true),
    onSuccess: () => {
      setExplore(null);
      setErr(null);
      invalidate();
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const scanM = useMutation({
    mutationFn: (id: number) => ipamApi.createIpv6SubnetScan(id),
    onSuccess: () => {
      setErr(null);
      invalidate();
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const reqM = useMutation({
    mutationFn: () =>
      ipamApi.requestIpv6Address({
        ipv6_prefix_id: explore!.id,
        mode: "reserve",
        note: reqNote.trim() || null,
      }),
    onSuccess: () => {
      setReqNote("");
      setErr(null);
      invalidate();
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const relM = useMutation({
    mutationFn: (id: number) => ipamApi.releaseIpv6Address(id),
    onSuccess: () => {
      setErr(null);
      invalidate();
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const splitM = useMutation({
    mutationFn: () =>
      ipamApi.ipv6PrefixSplitEqual(splitTarget!.id, {
        new_prefix_len: splitLen!,
        migrate_inventory: splitMigrate,
        dry_run: false,
      }),
    onSuccess: () => {
      setSplitTarget(null);
      setErr(null);
      invalidate();
    },
    onError: (e: Error) => setSplitErr(e instanceof ApiError ? e.message : e.message),
  });

  const vrfOptions = useMemo(() => {
    const sid = newSite.trim() ? Number(newSite) : null;
    if (sid == null) return [];
    return (vrfsQ.data ?? []).filter((v) => v.site_id === sid);
  }, [vrfsQ.data, newSite]);

  return (
    <Panel title={t("ipam.ipv6.title")}>
      <IpamFamilyTabs />
      <p className={dcimStyles.muted}>{t("ipam.ipv6.intro")}</p>
      {err ? <p className={dcimStyles.err}>{err}</p> : null}

      <div className={dcimStyles.formRow} style={{ flexWrap: "wrap" }}>
        <label>
          {t("ipam.ipv4.filterSite")}
          <select value={filterSite} onChange={(e) => setFilterSite(e.target.value)}>
            <option value="">{t("ipam.ipv4.allSites")}</option>
            {(sitesQ.data ?? []).map((s) => (
              <option key={s.id} value={String(s.id)}>
                {s.name}
              </option>
            ))}
          </select>
        </label>
      </div>

      {explore ? (
        <section
          className={dcimStyles.mfrDetailSection}
          style={{ border: "1px solid var(--shell-border)", borderRadius: "var(--radius-md)", padding: "var(--space-3)" }}
        >
          <button type="button" className={dcimStyles.btnLink} onClick={() => setExplore(null)}>
            {t("ipam.ipv4.breadcrumbRoot")}
          </button>
          <h3 className={dcimStyles.mfrDetailSectionTitle} style={{ marginTop: "var(--space-2)" }}>
            {explore.name} <code>{explore.cidr}</code>
            <span className={dcimStyles.muted} style={{ fontWeight: 400 }}>
              {" "}
              · {siteNameById.get(explore.site_id) ?? `#${explore.site_id}`} · {explore.role} · {explore.status} ·{" "}
              {explore.overlap_policy}
              {explore.dual_stack_group_id != null ? ` · dual-stack #${explore.dual_stack_group_id}` : ""}
            </span>
          </h3>

          <h4 className={dcimStyles.mfrDetailSectionTitle}>{t("ipam.ipv4.childPrefixes")}</h4>
          {childrenOfExplore.length === 0 ? (
            <p className={dcimStyles.muted}>{t("ipam.ipv6.noChildren")}</p>
          ) : (
            <table className={dcimStyles.table}>
              <thead>
                <tr>
                  <th>{t("ipam.ipv4.name")}</th>
                  <th>{t("ipam.ipv4.cidr")}</th>
                  <th />
                </tr>
              </thead>
              <tbody>
                {childrenOfExplore.map((ch) => (
                  <tr key={ch.id}>
                    <td>{ch.name}</td>
                    <td>
                      <code>{ch.cidr}</code>
                    </td>
                    <td>
                      <button type="button" className={dcimStyles.btnLink} onClick={() => setExplore(ch)}>
                        {t("ipam.ipv4.openExplore")}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}

          <h4 className={dcimStyles.mfrDetailSectionTitle}>{t("ipam.ipv6.inventory")}</h4>
          <form
            className={dcimStyles.formRow}
            onSubmit={(e) => {
              e.preventDefault();
              reqM.mutate();
            }}
          >
            <label>
              {t("ipam.addr.note")}
              <input value={reqNote} onChange={(e) => setReqNote(e.target.value)} />
            </label>
            <button type="submit" className={dcimStyles.btn} disabled={reqM.isPending}>
              {t("ipam.ipv6.request")}
            </button>
          </form>
          {addrsQ.data && addrsQ.data.length > 0 ? (
            <table className={dcimStyles.table}>
              <thead>
                <tr>
                  <th>{t("ipam.ipv4.cidr")}</th>
                  <th>{t("ipam.gitops.status")}</th>
                  <th>{t("ipam.ipv4.actionsCol")}</th>
                </tr>
              </thead>
              <tbody>
                {addrsQ.data.map((a) => (
                  <tr key={a.id}>
                    <td>
                      <code>{a.address}</code>
                    </td>
                    <td>{a.status}</td>
                    <td>
                      {a.status === "reserved" || a.status === "assigned" ? (
                        <button type="button" className={dcimStyles.btnLink} onClick={() => relM.mutate(a.id)}>
                          {t("ipam.addr.release")}
                        </button>
                      ) : (
                        "—"
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <p className={dcimStyles.muted}>{t("ipam.ipv6.noAddresses")}</p>
          )}

          {gridEnabled ? (
            <>
              <h4 className={dcimStyles.mfrDetailSectionTitle}>{t("ipam.ipv6.gridTitle")}</h4>
              <button
                type="button"
                className={dcimStyles.btn}
                disabled={scanM.isPending}
                onClick={() => scanM.mutate(explore.id)}
              >
                {t("ipam.scan.start")}
              </button>
              {gridQ.isError ? <p className={dcimStyles.err}>{(gridQ.error as Error).message}</p> : null}
              {gridQ.data ? (
                <p className={dcimStyles.muted}>
                  {gridQ.data.rows.length} {t("ipam.ipv6.gridRows")}
                  {gridQ.data.active_scan
                    ? ` · ${gridQ.data.active_scan.status} ${gridQ.data.active_scan.hosts_responding}/${gridQ.data.active_scan.hosts_scanned}`
                    : ""}
                </p>
              ) : null}
              {gridQ.data && gridQ.data.rows.length > 0 ? (
                <table className={dcimStyles.table}>
                  <thead>
                    <tr>
                      <th>{t("ipam.ipv4.cidr")}</th>
                      <th>{t("ipam.gitops.status")}</th>
                      <th>{t("ipam.scan.ping")}</th>
                    </tr>
                  </thead>
                  <tbody>
                    {gridQ.data.rows.slice(0, 64).map((r) => (
                      <tr key={r.address}>
                        <td>
                          <code>{r.address}</code>
                        </td>
                        <td>{r.inventory?.status ?? r.address_role ?? "—"}</td>
                        <td>
                          {r.scan_ping_responded == null
                            ? "—"
                            : r.scan_ping_responded
                              ? t("ipam.scan.up")
                              : t("ipam.scan.down")}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              ) : null}
            </>
          ) : (
            <>
              <h4 className={dcimStyles.mfrDetailSectionTitle}>{t("ipam.ipv6.rangesTitle")}</h4>
              <p className={dcimStyles.muted}>{t("ipam.ipv6.rangesHint")}</p>
              {rangesQ.isError ? <p className={dcimStyles.err}>{(rangesQ.error as Error).message}</p> : null}
              {rangesQ.data ? (
                <>
                  <p>
                    {t("ipam.ipv6.usedCount")}: {rangesQ.data.used_count}
                  </p>
                  <p className={dcimStyles.muted}>
                    {t("ipam.ipv6.freeCidrs")}: {rangesQ.data.free_cidrs.slice(0, 12).join(", ")}
                    {rangesQ.data.free_cidrs.length > 12 ? " …" : ""}
                  </p>
                </>
              ) : null}
            </>
          )}

          {scansQ.data && scansQ.data.length > 0 ? (
            <p className={dcimStyles.muted}>
              {t("ipam.scan.last")}: {scansQ.data[0].status} · {scansQ.data[0].cidr}
            </p>
          ) : null}
        </section>
      ) : null}

      <section className={dcimStyles.mfrDetailSection}>
        <h3 className={dcimStyles.mfrDetailSectionTitle}>{t("ipam.ipv6.addTitle")}</h3>
        <form
          className={dcimStyles.formRow}
          style={{ flexWrap: "wrap" }}
          onSubmit={(e) => {
            e.preventDefault();
            if (!newSite || !newName.trim() || !newCidr.trim()) {
              setErr(t("ipam.ipv4.addMissing"));
              return;
            }
            createM.mutate();
          }}
        >
          <label>
            {t("ipam.ipv4.site")}
            <select value={newSite} onChange={(e) => setNewSite(e.target.value)} required>
              <option value="">{t("dcim.common.choose")}</option>
              {(sitesQ.data ?? []).map((s) => (
                <option key={s.id} value={String(s.id)}>
                  {s.name}
                </option>
              ))}
            </select>
          </label>
          <label>
            {t("ipam.ipv4.name")}
            <input value={newName} onChange={(e) => setNewName(e.target.value)} required />
          </label>
          <label>
            {t("ipam.ipv4.cidr")}
            <input value={newCidr} onChange={(e) => setNewCidr(e.target.value)} placeholder="fd00:1::/64" required />
          </label>
          <label>
            {t("ipam.gitops.role")}
            <select value={newRole} onChange={(e) => setNewRole(e.target.value)}>
              {PREFIX_ROLES.map((r) => (
                <option key={r} value={r}>
                  {r}
                </option>
              ))}
            </select>
          </label>
          <label>
            {t("ipam.gitops.status")}
            <select value={newStatus} onChange={(e) => setNewStatus(e.target.value)}>
              {PREFIX_STATUSES.map((s) => (
                <option key={s} value={s}>
                  {s}
                </option>
              ))}
            </select>
          </label>
          <label>
            {t("ipam.gitops.overlap")}
            <select value={newOverlap} onChange={(e) => setNewOverlap(e.target.value)}>
              <option value="">{t("ipam.gitops.overlapDefault")}</option>
              {OVERLAP_POLICIES.map((p) => (
                <option key={p} value={p}>
                  {p}
                </option>
              ))}
            </select>
          </label>
          <label>
            {t("ipam.gitops.dualStack")}
            <input value={newDualStack} onChange={(e) => setNewDualStack(e.target.value)} placeholder="80" />
          </label>
          <label>
            VRF
            <select value={newVrf} onChange={(e) => setNewVrf(e.target.value)}>
              <option value="">{t("dcim.common.none")}</option>
              {vrfOptions.map((v) => (
                <option key={v.id} value={String(v.id)}>
                  {v.name}
                </option>
              ))}
            </select>
          </label>
          <button type="submit" className={dcimStyles.btn} disabled={createM.isPending}>
            {t("dcim.common.add")}
          </button>
        </form>
      </section>

      <h3 className={dcimStyles.mfrDetailSectionTitle}>{t("ipam.ipv6.allTitle")}</h3>
      {prefixesQ.isLoading ? <p className={dcimStyles.muted}>{t("dcim.common.loading")}</p> : null}
      {prefixesQ.data && prefixesQ.data.length > 0 ? (
        <table className={dcimStyles.table}>
          <thead>
            <tr>
              <th />
              <th>{t("ipam.ipv4.site")}</th>
              <th>{t("ipam.ipv4.name")}</th>
              <th>{t("ipam.ipv4.cidr")}</th>
              <th>{t("ipam.gitops.role")}</th>
              <th>{t("ipam.gitops.status")}</th>
              <th>{t("ipam.gitops.overlap")}</th>
              <th>{t("ipam.ipv4.actionsCol")}</th>
            </tr>
          </thead>
          <tbody>
            {visible.map((row) => {
              const x = row.prefix;
              const plen = parseIpv6PrefixLen(x.cidr);
              const childCount = tree.childrenByParentId.get(x.id)?.length ?? 0;
              return (
                <tr key={x.id}>
                  <td style={{ paddingLeft: `calc(${row.depth} * 0.65rem)` }}>
                    {row.hasChildren ? (
                      <button
                        type="button"
                        className={dcimStyles.btnLink}
                        onClick={() => {
                          setExpanded((prev) => {
                            const n = new Set(prev);
                            if (n.has(x.id)) n.delete(x.id);
                            else n.add(x.id);
                            return n;
                          });
                        }}
                      >
                        {expanded.has(x.id) ? "▼" : "▶"}
                      </button>
                    ) : (
                      "·"
                    )}
                  </td>
                  <td>{siteNameById.get(x.site_id) ?? `#${x.site_id}`}</td>
                  <td>{x.name}</td>
                  <td>
                    <code>{x.cidr}</code>
                  </td>
                  <td>{x.role}</td>
                  <td>{x.status}</td>
                  <td>{x.overlap_policy}</td>
                  <td>
                    <div className={dcimStyles.tableIconActions}>
                      <button type="button" className={dcimStyles.btnLink} onClick={() => setExplore(x)}>
                        {t("ipam.ipv4.openExplore")}
                      </button>
                      {plen != null && plen < 128 && childCount === 0 ? (
                        <button type="button" className={dcimStyles.btnLink} onClick={() => setSplitTarget(x)}>
                          {t("ipam.ipv4.splitSubnet")}
                        </button>
                      ) : null}
                      <button type="button" className={dcimStyles.btnLink} onClick={() => setDeleteTarget(x)}>
                        {t("dcim.common.delete")}
                      </button>
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      ) : !prefixesQ.isLoading ? (
        <p className={dcimStyles.muted}>{t("ipam.ipv6.empty")}</p>
      ) : null}

      {splitTarget ? (
        <div
          role="presentation"
          style={{
            position: "fixed",
            inset: 0,
            background: "rgba(0,0,0,0.35)",
            zIndex: 40,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
          onClick={() => {
            if (!splitM.isPending) setSplitTarget(null);
          }}
        >
          <div
            role="dialog"
            aria-labelledby={splitTitleId}
            className={dcimStyles.mfrDetailSection}
            style={{
              background: "var(--shell-surface)",
              padding: "var(--space-4)",
              maxWidth: "36rem",
              width: "90%",
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <h2 id={splitTitleId}>{t("ipam.ipv4.splitTitle")}</h2>
            <p className={dcimStyles.muted}>{t("ipam.ipv4.splitIntro", { cidr: splitTarget.cidr })}</p>
            {splitOpts.length === 0 ? (
              <p className={dcimStyles.err}>{t("ipam.ipv6.splitNoOptions")}</p>
            ) : (
              <label>
                {t("ipam.ipv4.splitEqualSelect")}
                <select value={splitLen ?? ""} onChange={(e) => setSplitLen(Number(e.target.value))}>
                  {splitOpts.map((o) => (
                    <option key={o.newPrefixLen} value={o.newPrefixLen}>
                      {o.label}
                    </option>
                  ))}
                </select>
              </label>
            )}
            <label style={{ display: "flex", gap: "0.4rem", marginTop: "var(--space-2)" }}>
              <input type="checkbox" checked={splitMigrate} onChange={(e) => setSplitMigrate(e.target.checked)} />
              {t("ipam.ipv6.splitMigrate")}
            </label>
            {splitPreviewQ.data?.has_child_prefixes ? (
              <p className={dcimStyles.err}>{t("ipam.ipv4.splitHasChildren")}</p>
            ) : null}
            {splitPreviewQ.data?.planned?.length ? (
              <ul>
                {splitPreviewQ.data.planned.slice(0, SPLIT_PREVIEW_MAX).map((p) => (
                  <li key={p.cidr}>
                    <code>{p.cidr}</code>
                  </li>
                ))}
              </ul>
            ) : null}
            {splitErr ? <p className={dcimStyles.err}>{splitErr}</p> : null}
            <div className={dcimStyles.formRow} style={{ marginTop: "var(--space-3)" }}>
              <button
                type="button"
                className={dcimStyles.btn}
                disabled={
                  splitLen == null ||
                  splitM.isPending ||
                  splitPreviewQ.data?.has_child_prefixes === true ||
                  splitPreviewQ.data?.partition_ok === false
                }
                onClick={() => splitM.mutate()}
              >
                {t("ipam.ipv4.splitExecute", {
                  count: String(splitPreviewQ.data?.subnet_count ?? splitOpts.find((o) => o.newPrefixLen === splitLen)?.subnetCount ?? 0),
                })}
              </button>
              <button type="button" className={dcimStyles.btn} onClick={() => setSplitTarget(null)}>
                {t("ipam.ipv4.splitCancel")}
              </button>
            </div>
          </div>
        </div>
      ) : null}

      <ConfirmModal
        open={deleteTarget != null}
        onClose={() => {
          if (!delM.isPending) setDeleteTarget(null);
        }}
        title={t("dcim.common.delete")}
        message={
          deleteTarget
            ? t("ipam.ipv6.deleteConfirm", { name: deleteTarget.name, cidr: deleteTarget.cidr })
            : null
        }
        confirmLabel={t("dcim.common.delete")}
        cancelLabel={t("dcim.common.cancel")}
        danger
        pending={delM.isPending}
        onConfirm={() => {
          if (!deleteTarget) return;
          delM.mutate(deleteTarget.id, { onSettled: () => setDeleteTarget(null) });
        }}
      />
    </Panel>
  );
}
