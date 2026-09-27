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
  const [spaceName, setSpaceName] = useState("");
  const [err, setErr] = useState<string | null>(null);
  const [spaceErr, setSpaceErr] = useState<string | null>(null);
  const listQ = useQuery({
    queryKey: ["ipam", "dual-stack-groups"],
    queryFn: ipamApi.listDualStackGroups,
  });
  const spacesQ = useQuery({
    queryKey: ["ipam", "address-spaces"],
    queryFn: ipamApi.listAddressSpaces,
  });
  const invalidate = () => {
    void qc.invalidateQueries({ queryKey: ["ipam", "dual-stack-groups"] });
    void qc.invalidateQueries({ queryKey: ["ipam", "address-spaces"] });
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
  const createSpaceM = useMutation({
    mutationFn: () => ipamApi.createAddressSpace({ name: spaceName.trim() }),
    onSuccess: () => {
      setSpaceName("");
      setSpaceErr(null);
      invalidate();
    },
    onError: (e: Error) => setSpaceErr(e instanceof ApiError ? e.message : e.message),
  });
  const delSpaceM = useMutation({
    mutationFn: (id: number) => ipamApi.deleteAddressSpace(id),
    onSuccess: () => {
      setSpaceErr(null);
      invalidate();
    },
    onError: (e: Error) => setSpaceErr(e instanceof ApiError ? e.message : e.message),
  });
  const groups = listQ.data ?? [];
  const spaces = spacesQ.data ?? [];

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
      <section className={dcimStyles.mfrDetailSection} style={{ marginBottom: "var(--space-3)" }}>
        <h3 className={dcimStyles.mfrDetailSectionTitle}>{t("ipam.addressSpace.title")}</h3>
        <p className={dcimStyles.muted}>{t("ipam.addressSpace.hint")}</p>
        {spaceErr ? <p className={dcimStyles.err}>{spaceErr}</p> : null}
        {spaces.length === 0 && !spacesQ.isLoading ? <p className={dcimStyles.muted}>{t("ipam.addressSpace.empty")}</p> : null}
        {spaces.length > 0 ? (
          <ul className={dcimStyles.ipList}>
            {spaces.map((s) => (
              <li key={s.id}>
                {s.name} <span className={dcimStyles.muted}>{s.slug}</span>{" "}
                <button type="button" className={dcimStyles.btnLink} onClick={() => delSpaceM.mutate(s.id)}>
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
            setSpaceErr(null);
            createSpaceM.mutate();
          }}
        >
          <label>
            {t("ipam.addressSpace.name")}
            <input value={spaceName} onChange={(e) => setSpaceName(e.target.value)} required />
          </label>
          <button type="submit" className={dcimStyles.btn} disabled={createSpaceM.isPending || spaceName.trim() === ""}>
            {createSpaceM.isPending ? "…" : t("ipam.addressSpace.add")}
          </button>
        </form>
      </section>
      <Outlet />
    </Panel>
  );
}
