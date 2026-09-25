import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { Outlet } from "react-router-dom";
import { Panel } from "@/components/ui/Panel";
import dcimStyles from "@/features/dcim/dcim.module.css";
import { useI18n } from "@/i18n/I18nProvider";
import { ApiError } from "@/lib/api";
import { IpamFamilyTabs } from "./IpamFamilyTabs";
import * as ipamApi from "./ipamApi";

export function IpamAddressingLayout() {
  const { t } = useI18n();
  const qc = useQueryClient();
  const [name, setName] = useState("");
  const [err, setErr] = useState<string | null>(null);
  const listQ = useQuery({
    queryKey: ["ipam", "dual-stack-groups"],
    queryFn: ipamApi.listDualStackGroups,
  });
  const invalidate = () => {
    void qc.invalidateQueries({ queryKey: ["ipam", "dual-stack-groups"] });
    void qc.invalidateQueries({ queryKey: ["ipam", "ipv4-prefixes"] });
    void qc.invalidateQueries({ queryKey: ["ipam", "ipv6-prefixes"] });
  };
  const createM = useMutation({
    mutationFn: () => ipamApi.createDualStackGroup({ name: name.trim() }),
    onSuccess: () => {
      setName("");
      setErr(null);
      invalidate();
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });
  const delM = useMutation({
    mutationFn: (id: number) => ipamApi.deleteDualStackGroup(id),
    onSuccess: () => {
      setErr(null);
      invalidate();
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });
  const groups = listQ.data ?? [];

  return (
    <Panel>
      <IpamFamilyTabs />
      <section className={dcimStyles.mfrDetailSection} style={{ marginBottom: "var(--space-3)" }}>
        <h3 className={dcimStyles.mfrDetailSectionTitle}>{t("ipam.dualStack.title")}</h3>
        <p className={dcimStyles.muted}>{t("ipam.dualStack.hint")}</p>
        {err ? <p className={dcimStyles.err}>{err}</p> : null}
        {groups.length === 0 && !listQ.isLoading ? <p className={dcimStyles.muted}>{t("ipam.dualStack.empty")}</p> : null}
        {groups.length > 0 ? (
          <ul className={dcimStyles.ipList}>
            {groups.map((g) => (
              <li key={g.id}>
                {g.name} <span className={dcimStyles.muted}>{g.slug}</span>{" "}
                <button type="button" className={dcimStyles.btnLink} onClick={() => delM.mutate(g.id)}>
                  {t("dcim.common.delete")}
                </button>
              </li>
            ))}
          </ul>
        ) : null}
        <form
          className={dcimStyles.formRow}
          style={{ flexWrap: "wrap", marginTop: "var(--space-2)" }}
          onSubmit={(e) => {
            e.preventDefault();
            setErr(null);
            createM.mutate();
          }}
        >
          <label>
            {t("ipam.dualStack.name")}
            <input value={name} onChange={(e) => setName(e.target.value)} required />
          </label>
          <button type="submit" className={dcimStyles.btn} disabled={createM.isPending || name.trim() === ""}>
            {createM.isPending ? "…" : t("ipam.dualStack.add")}
          </button>
        </form>
      </section>
      <Outlet />
    </Panel>
  );
}
