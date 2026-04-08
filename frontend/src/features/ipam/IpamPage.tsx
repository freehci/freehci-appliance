import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { Panel } from "@/components/ui/Panel";
import { useI18n } from "@/i18n/I18nProvider";
import { ApiError } from "@/lib/api";
import * as dcimApi from "@/features/dcim/dcimApi";
import dcimStyles from "@/features/dcim/dcim.module.css";
import type { Ipv4Prefix } from "./types";
import * as ipamApi from "./ipamApi";

type ExploreCrumb = { id: number; name: string; cidr: string };

export function IpamPage() {
  const { t } = useI18n();
  const qc = useQueryClient();
  const [err, setErr] = useState<string | null>(null);
  const [filterSite, setFilterSite] = useState<string>("");
  const [newSite, setNewSite] = useState("");
  const [newName, setNewName] = useState("");
  const [newCidr, setNewCidr] = useState("");
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editName, setEditName] = useState("");
  const [editCidr, setEditCidr] = useState("");
  const [exploreStack, setExploreStack] = useState<ExploreCrumb[]>([]);

  const sitesQ = useQuery({ queryKey: ["dcim", "sites"], queryFn: dcimApi.listSites });
  const siteIdFilter = filterSite === "" ? undefined : Number(filterSite);

  const prefixesQ = useQuery({
    queryKey: ["ipam", "ipv4-prefixes", siteIdFilter ?? "all"],
    queryFn: () => ipamApi.listIpv4Prefixes(siteIdFilter),
  });

  const exploreId = exploreStack.length > 0 ? exploreStack[exploreStack.length - 1].id : null;

  const exploreQ = useQuery({
    queryKey: ["ipam", "explore", exploreId],
    queryFn: () => ipamApi.getIpv4PrefixExplore(exploreId!),
    enabled: exploreId != null && exploreId > 0,
  });

  const siteNameById = useMemo(() => {
    const m = new Map<number, string>();
    for (const s of sitesQ.data ?? []) m.set(s.id, s.name);
    return m;
  }, [sitesQ.data]);

  const invalidateIpam = () => {
    void qc.invalidateQueries({ queryKey: ["ipam", "ipv4-prefixes"] });
    void qc.invalidateQueries({ queryKey: ["ipam", "explore"] });
  };

  const openExplore = (p: Pick<Ipv4Prefix, "id" | "name" | "cidr">) => {
    setEditingId(null);
    setExploreStack([{ id: p.id, name: p.name, cidr: p.cidr }]);
    setErr(null);
  };

  const drillChild = (p: Ipv4Prefix) => {
    setExploreStack((s) => [...s, { id: p.id, name: p.name, cidr: p.cidr }]);
    setErr(null);
  };

  const createPfx = useMutation({
    mutationFn: () =>
      ipamApi.createIpv4Prefix({
        site_id: Number(newSite),
        name: newName.trim(),
        cidr: newCidr.trim(),
      }),
    onSuccess: () => {
      setNewName("");
      setNewCidr("");
      setErr(null);
      invalidateIpam();
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const delPfx = useMutation({
    mutationFn: (id: number) => ipamApi.deleteIpv4Prefix(id),
    onSuccess: () => {
      setEditingId(null);
      setExploreStack([]);
      setErr(null);
      invalidateIpam();
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const patchPfx = useMutation({
    mutationFn: ({ id, body }: { id: number; body: { name: string; cidr: string } }) =>
      ipamApi.updateIpv4Prefix(id, body),
    onSuccess: () => {
      setEditingId(null);
      setErr(null);
      invalidateIpam();
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  return (
    <Panel title={t("ipam.ipv4.title")}>
      {err ? <p className={dcimStyles.err}>{err}</p> : null}
      <p className={dcimStyles.muted} style={{ marginTop: 0 }}>
        {t("ipam.ipv4.intro")}
      </p>

      <section className={dcimStyles.mfrDetailSection}>
        <h3 className={dcimStyles.mfrDetailSectionTitle}>{t("ipam.ipv4.filterTitle")}</h3>
        <div className={dcimStyles.formRow}>
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
      </section>

      {exploreStack.length > 0 && exploreId != null ? (
        <section
          className={dcimStyles.mfrDetailSection}
          style={{
            border: "1px solid var(--shell-border)",
            borderRadius: "var(--radius-md)",
            padding: "var(--space-3)",
          }}
        >
          <nav className={dcimStyles.muted} style={{ marginBottom: "var(--space-2)", fontSize: "var(--text-sm)" }}>
            <button
              type="button"
              className={dcimStyles.btnLink}
              onClick={() => {
                setExploreStack([]);
                setErr(null);
              }}
            >
              {t("ipam.ipv4.breadcrumbRoot")}
            </button>
            {exploreStack.map((c, i) => (
              <span key={c.id}>
                {" "}
                ›{" "}
                <button
                  type="button"
                  className={dcimStyles.btnLink}
                  onClick={() => setExploreStack((s) => s.slice(0, i + 1))}
                >
                  <code>{c.cidr}</code>
                </button>
              </span>
            ))}
          </nav>

          {exploreQ.isLoading ? <p className={dcimStyles.muted}>{t("dcim.common.loading")}</p> : null}
          {exploreQ.isError ? (
            <p className={dcimStyles.err}>{(exploreQ.error as Error).message}</p>
          ) : null}
          {exploreQ.data ? (
            <>
              <h3 className={dcimStyles.mfrDetailSectionTitle} style={{ marginTop: 0 }}>
                {exploreQ.data.prefix.name}{" "}
                <code>{exploreQ.data.prefix.cidr}</code>
                <span className={dcimStyles.muted} style={{ fontWeight: 400 }}>
                  {" "}
                  · {siteNameById.get(exploreQ.data.prefix.site_id) ?? `#${exploreQ.data.prefix.site_id}`}
                </span>
              </h3>

              <h4 className={dcimStyles.mfrDetailSectionTitle}>{t("ipam.ipv4.childPrefixes")}</h4>
              {exploreQ.data.child_prefixes.length > 0 ? (
                <table className={dcimStyles.table}>
                  <thead>
                    <tr>
                      <th>{t("dcim.common.id")}</th>
                      <th>{t("ipam.ipv4.name")}</th>
                      <th>{t("ipam.ipv4.cidr")}</th>
                      <th>{t("ipam.ipv4.usageCol")}</th>
                      <th />
                    </tr>
                  </thead>
                  <tbody>
                    {exploreQ.data.child_prefixes.map((ch) => (
                      <tr key={ch.id}>
                        <td>{ch.id}</td>
                        <td>{ch.name}</td>
                        <td>
                          <code>{ch.cidr}</code>
                        </td>
                        <td>
                          {ch.address_total > 0 ? (
                            <>
                              {ch.used_count} / {ch.address_total}
                              <span className={dcimStyles.muted}>
                                {" "}
                                ({Math.round((100 * ch.used_count) / ch.address_total)}%)
                              </span>
                            </>
                          ) : (
                            "—"
                          )}
                        </td>
                        <td>
                          <button type="button" className={dcimStyles.btn} onClick={() => drillChild(ch)}>
                            {t("ipam.ipv4.drillDown")}
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              ) : (
                <p className={dcimStyles.muted}>{t("ipam.ipv4.noChildPrefixes")}</p>
              )}

              <h4 className={dcimStyles.mfrDetailSectionTitle}>{t("ipam.ipv4.assignmentsHere")}</h4>
              {exploreQ.data.assignments.length > 0 ? (
                <table className={dcimStyles.table}>
                  <thead>
                    <tr>
                      <th>{t("ipam.ipv4.colAddress")}</th>
                      <th>{t("ipam.ipv4.colDevice")}</th>
                      <th>{t("ipam.ipv4.colInterface")}</th>
                      <th>{t("ipam.ipv4.colLinkedPrefix")}</th>
                    </tr>
                  </thead>
                  <tbody>
                    {exploreQ.data.assignments.map((a) => (
                      <tr key={a.assignment_id}>
                        <td>
                          <code>{a.address}</code>
                        </td>
                        <td>
                          <Link to={`/dcim/equipment/devices/${a.device_id}`} className={dcimStyles.tableLink}>
                            {a.device_name}
                          </Link>
                        </td>
                        <td>{a.interface_name}</td>
                        <td className={dcimStyles.muted}>
                          {a.ipv4_prefix_id != null ? `#${a.ipv4_prefix_id}` : "—"}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              ) : (
                <p className={dcimStyles.muted}>{t("ipam.ipv4.noAssignmentsInPrefix")}</p>
              )}
            </>
          ) : null}
        </section>
      ) : null}

      <section className={dcimStyles.mfrDetailSection}>
        <h3 className={dcimStyles.mfrDetailSectionTitle}>{t("ipam.ipv4.addTitle")}</h3>
        <form
          className={dcimStyles.formRow}
          onSubmit={(e) => {
            e.preventDefault();
            setErr(null);
            if (!newSite || !newName.trim() || !newCidr.trim()) {
              setErr(t("ipam.ipv4.addMissing"));
              return;
            }
            createPfx.mutate();
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
            <input value={newCidr} onChange={(e) => setNewCidr(e.target.value)} placeholder="192.168.1.0/24" required />
          </label>
          <button type="submit" className={dcimStyles.btn} disabled={createPfx.isPending}>
            {createPfx.isPending ? "…" : t("dcim.common.add")}
          </button>
        </form>
      </section>

      <h3 className={dcimStyles.mfrDetailSectionTitle}>{t("ipam.ipv4.allPrefixesTitle")}</h3>
      <p className={dcimStyles.muted} style={{ marginTop: 0 }}>
        {t("ipam.ipv4.allPrefixesHint")}
      </p>

      {prefixesQ.isLoading ? <p className={dcimStyles.muted}>{t("dcim.common.loading")}</p> : null}
      {prefixesQ.data && prefixesQ.data.length > 0 ? (
        <table className={dcimStyles.table}>
          <thead>
            <tr>
              <th>{t("dcim.common.id")}</th>
              <th>{t("ipam.ipv4.site")}</th>
              <th>{t("ipam.ipv4.name")}</th>
              <th>{t("ipam.ipv4.cidr")}</th>
              <th>{t("ipam.ipv4.usageCol")}</th>
              <th>{t("ipam.ipv4.exploreCol")}</th>
              <th>{t("ipam.ipv4.actionsCol")}</th>
            </tr>
          </thead>
          <tbody>
            {prefixesQ.data.map((x) => (
              <tr key={x.id}>
                <td>{x.id}</td>
                <td>{siteNameById.get(x.site_id) ?? `#${x.site_id}`}</td>
                <td>
                  {editingId === x.id ? (
                    <input
                      value={editName}
                      onChange={(e) => setEditName(e.target.value)}
                      aria-label={t("ipam.ipv4.name")}
                    />
                  ) : (
                    x.name
                  )}
                </td>
                <td>
                  {editingId === x.id ? (
                    <input
                      value={editCidr}
                      onChange={(e) => setEditCidr(e.target.value)}
                      aria-label={t("ipam.ipv4.cidr")}
                    />
                  ) : (
                    <code>{x.cidr}</code>
                  )}
                </td>
                <td>
                  {x.address_total > 0 ? (
                    <>
                      {x.used_count} / {x.address_total}
                      <span className={dcimStyles.muted}>
                        {" "}
                        ({Math.round((100 * x.used_count) / x.address_total)}%)
                      </span>
                    </>
                  ) : (
                    "—"
                  )}
                </td>
                <td>
                  <button
                    type="button"
                    className={dcimStyles.btn}
                    disabled={editingId === x.id}
                    onClick={() => openExplore(x)}
                  >
                    {t("ipam.ipv4.openExplore")}
                  </button>
                </td>
                <td>
                  {editingId === x.id ? (
                    <span style={{ display: "inline-flex", flexWrap: "wrap", gap: "0.35rem" }}>
                      <button
                        type="button"
                        className={dcimStyles.btn}
                        disabled={patchPfx.isPending}
                        onClick={() => {
                          const nm = editName.trim();
                          const cd = editCidr.trim();
                          if (!nm || !cd) {
                            setErr(t("ipam.ipv4.addMissing"));
                            return;
                          }
                          patchPfx.mutate({ id: x.id, body: { name: nm, cidr: cd } });
                        }}
                      >
                        {patchPfx.isPending ? "…" : t("dcim.common.save")}
                      </button>
                      <button
                        type="button"
                        className={dcimStyles.btn}
                        onClick={() => {
                          setEditingId(null);
                          setErr(null);
                        }}
                      >
                        {t("ipam.ipv4.cancel")}
                      </button>
                    </span>
                  ) : (
                    <span style={{ display: "inline-flex", flexWrap: "wrap", gap: "0.35rem" }}>
                      <button
                        type="button"
                        className={dcimStyles.btn}
                        onClick={() => {
                          setEditingId(x.id);
                          setEditName(x.name);
                          setEditCidr(x.cidr);
                          setErr(null);
                        }}
                      >
                        {t("ipam.ipv4.edit")}
                      </button>
                      <button
                        type="button"
                        className={dcimStyles.btnDanger}
                        onClick={() => delPfx.mutate(x.id)}
                        disabled={delPfx.isPending}
                      >
                        {t("dcim.common.delete")}
                      </button>
                    </span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        !prefixesQ.isLoading && <p className={dcimStyles.muted}>{t("ipam.ipv4.empty")}</p>
      )}
    </Panel>
  );
}
