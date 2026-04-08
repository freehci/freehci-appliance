import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { Panel } from "@/components/ui/Panel";
import { useI18n } from "@/i18n/I18nProvider";
import { ApiError } from "@/lib/api";
import * as dcimApi from "@/features/dcim/dcimApi";
import dcimStyles from "@/features/dcim/dcim.module.css";
import * as ipamApi from "./ipamApi";

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

  const sitesQ = useQuery({ queryKey: ["dcim", "sites"], queryFn: dcimApi.listSites });
  const siteIdFilter = filterSite === "" ? undefined : Number(filterSite);

  const prefixesQ = useQuery({
    queryKey: ["ipam", "ipv4-prefixes", siteIdFilter ?? "all"],
    queryFn: () => ipamApi.listIpv4Prefixes(siteIdFilter),
  });

  const siteNameById = useMemo(() => {
    const m = new Map<number, string>();
    for (const s of sitesQ.data ?? []) m.set(s.id, s.name);
    return m;
  }, [sitesQ.data]);

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
      void qc.invalidateQueries({ queryKey: ["ipam", "ipv4-prefixes"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const delPfx = useMutation({
    mutationFn: (id: number) => ipamApi.deleteIpv4Prefix(id),
    onSuccess: () => {
      setEditingId(null);
      setErr(null);
      void qc.invalidateQueries({ queryKey: ["ipam", "ipv4-prefixes"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const patchPfx = useMutation({
    mutationFn: ({ id, body }: { id: number; body: { name: string; cidr: string } }) =>
      ipamApi.updateIpv4Prefix(id, body),
    onSuccess: () => {
      setEditingId(null);
      setErr(null);
      void qc.invalidateQueries({ queryKey: ["ipam", "ipv4-prefixes"] });
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

      {prefixesQ.isLoading ? <p className={dcimStyles.muted}>{t("dcim.common.loading")}</p> : null}
      {prefixesQ.data && prefixesQ.data.length > 0 ? (
        <table className={dcimStyles.table}>
          <thead>
            <tr>
              <th>{t("dcim.common.id")}</th>
              <th>{t("ipam.ipv4.site")}</th>
              <th>{t("ipam.ipv4.name")}</th>
              <th>{t("ipam.ipv4.cidr")}</th>
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
