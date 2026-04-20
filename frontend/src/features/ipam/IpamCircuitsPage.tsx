import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { Panel } from "@/components/ui/Panel";
import * as dcimApi from "@/features/dcim/dcimApi";
import dcimStyles from "@/features/dcim/dcim.module.css";
import { useI18n } from "@/i18n/I18nProvider";
import { ApiError } from "@/lib/api";
import * as ipamApi from "./ipamApi";

export function IpamCircuitsPage() {
  const { t } = useI18n();
  const qc = useQueryClient();
  const [err, setErr] = useState<string | null>(null);
  const [filterTenant, setFilterTenant] = useState("");
  const [tenantId, setTenantId] = useState("");
  const [circuitNumber, setCircuitNumber] = useState("");
  const [name, setName] = useState("");
  const [circuitType, setCircuitType] = useState<string>("fiber");
  const [isLeased, setIsLeased] = useState(false);
  const [provider, setProvider] = useState("");
  const [established, setEstablished] = useState("");
  const [contractEnd, setContractEnd] = useState("");
  const [termCircuitId, setTermCircuitId] = useState<number | null>(null);
  const [termEndpoint, setTermEndpoint] = useState<"a" | "z">("a");
  const [termIface, setTermIface] = useState("");

  const tenantIdFilter = filterTenant === "" ? undefined : Number(filterTenant);
  const tenantsQ = useQuery({ queryKey: ["tenants"], queryFn: dcimApi.listTenants });
  const circuitsQ = useQuery({
    queryKey: ["ipam", "circuits", tenantIdFilter ?? "all"],
    queryFn: () => ipamApi.listIpamCircuits(tenantIdFilter),
  });

  const termsQ = useQuery({
    queryKey: ["ipam", "circuit-terms", termCircuitId],
    queryFn: () => ipamApi.listCircuitTerminations(termCircuitId!),
    enabled: termCircuitId != null && termCircuitId > 0,
  });

  const createM = useMutation({
    mutationFn: () =>
      ipamApi.createIpamCircuit({
        tenant_id: Number(tenantId),
        circuit_number: circuitNumber.trim(),
        name: name.trim(),
        circuit_type: circuitType,
        is_leased: isLeased,
        provider_name: provider.trim() === "" ? null : provider.trim(),
        established_on: established.trim() === "" ? null : established.trim(),
        contract_end_on: contractEnd.trim() === "" ? null : contractEnd.trim(),
      }),
    onSuccess: () => {
      setErr(null);
      setCircuitNumber("");
      setName("");
      setProvider("");
      setEstablished("");
      setContractEnd("");
      void qc.invalidateQueries({ queryKey: ["ipam", "circuits"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const delM = useMutation({
    mutationFn: (id: number) => ipamApi.deleteIpamCircuit(id),
    onSuccess: () => {
      setErr(null);
      if (termCircuitId != null) setTermCircuitId(null);
      void qc.invalidateQueries({ queryKey: ["ipam", "circuits"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const termM = useMutation({
    mutationFn: () =>
      ipamApi.upsertCircuitTermination(termCircuitId!, {
        endpoint: termEndpoint,
        interface_id: termIface.trim() === "" ? null : Number(termIface),
      }),
    onSuccess: () => {
      setErr(null);
      setTermIface("");
      void qc.invalidateQueries({ queryKey: ["ipam", "circuit-terms", termCircuitId] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  return (
    <Panel title={t("ipam.circuits.title")}>
      <p className={dcimStyles.muted}>{t("ipam.circuits.intro")}</p>
      <p className={dcimStyles.muted}>{t("ipam.circuits.placementHint")}</p>
      {err ? <p className={dcimStyles.err}>{err}</p> : null}
      <div className={dcimStyles.formRow} style={{ marginTop: "var(--space-2)", flexWrap: "wrap" }}>
        <label>
          {t("ipam.circuits.filterTenant")}
          <select value={filterTenant} onChange={(e) => setFilterTenant(e.target.value)}>
            <option value="">{t("ipam.circuits.allTenants")}</option>
            {(tenantsQ.data ?? []).map((tn) => (
              <option key={tn.id} value={String(tn.id)}>
                {tn.name}
              </option>
            ))}
          </select>
        </label>
      </div>
      <h3 className={dcimStyles.mfrDetailSectionTitle} style={{ marginTop: "var(--space-3)" }}>
        {t("ipam.circuits.addTitle")}
      </h3>
      <form
        className={dcimStyles.formRow}
        style={{ flexDirection: "column", alignItems: "stretch", maxWidth: "32rem", gap: "var(--space-2)" }}
        onSubmit={(e) => {
          e.preventDefault();
          setErr(null);
          createM.mutate();
        }}
      >
        <label>
          {t("ipam.circuits.tenant")}
          <select value={tenantId} onChange={(e) => setTenantId(e.target.value)} required>
            <option value="">{t("ipam.circuits.chooseTenant")}</option>
            {(tenantsQ.data ?? []).map((tn) => (
              <option key={tn.id} value={String(tn.id)}>
                {tn.name}
              </option>
            ))}
          </select>
        </label>
        <label>
          {t("ipam.circuits.number")}
          <input value={circuitNumber} onChange={(e) => setCircuitNumber(e.target.value)} required />
        </label>
        <label>
          {t("ipam.ipv4.name")}
          <input value={name} onChange={(e) => setName(e.target.value)} required />
        </label>
        <label>
          {t("ipam.circuits.type")}
          <select value={circuitType} onChange={(e) => setCircuitType(e.target.value)}>
            <option value="fiber">{t("ipam.circuits.type.fiber")}</option>
            <option value="vpn">{t("ipam.circuits.type.vpn")}</option>
            <option value="radio">{t("ipam.circuits.type.radio")}</option>
            <option value="leased_line">{t("ipam.circuits.type.leased_line")}</option>
            <option value="other">{t("ipam.circuits.type.other")}</option>
          </select>
        </label>
        <label style={{ display: "flex", gap: "var(--space-2)", alignItems: "center" }}>
          <input type="checkbox" checked={isLeased} onChange={(e) => setIsLeased(e.target.checked)} />
          {t("ipam.circuits.leased")}
        </label>
        <label>
          {t("ipam.circuits.provider")}
          <input value={provider} onChange={(e) => setProvider(e.target.value)} />
        </label>
        <label>
          {t("ipam.circuits.established")}
          <input type="date" value={established} onChange={(e) => setEstablished(e.target.value)} />
        </label>
        <label>
          {t("ipam.circuits.contractEnd")}
          <input type="date" value={contractEnd} onChange={(e) => setContractEnd(e.target.value)} />
        </label>
        <button type="submit" className={dcimStyles.btn} disabled={createM.isPending}>
          {createM.isPending ? "…" : t("ipam.circuits.create")}
        </button>
      </form>
      {circuitsQ.isLoading ? <p className={dcimStyles.muted}>{t("dcim.common.loading")}</p> : null}
      {circuitsQ.data && circuitsQ.data.length === 0 && !circuitsQ.isLoading ? (
        <p className={dcimStyles.muted}>{t("ipam.circuits.empty")}</p>
      ) : null}
      {circuitsQ.data && circuitsQ.data.length > 0 ? (
        <table className={dcimStyles.table} style={{ marginTop: "var(--space-3)" }}>
          <thead>
            <tr>
              <th>{t("ipam.circuits.number")}</th>
              <th>{t("ipam.ipv4.name")}</th>
              <th>{t("ipam.circuits.type")}</th>
              <th>{t("ipam.circuits.leased")}</th>
              <th>{t("ipam.circuits.provider")}</th>
              <th>{t("ipam.ipv4.actionsCol")}</th>
            </tr>
          </thead>
          <tbody>
            {circuitsQ.data.map((c) => (
              <tr key={c.id}>
                <td>{c.circuit_number}</td>
                <td>{c.name}</td>
                <td>{c.circuit_type}</td>
                <td>{c.is_leased ? t("ipam.circuits.yes") : t("ipam.circuits.no")}</td>
                <td>{c.provider_name ?? "—"}</td>
                <td>
                  <button
                    type="button"
                    className={dcimStyles.btnLink}
                    onClick={() => setTermCircuitId(termCircuitId === c.id ? null : c.id)}
                  >
                    {termCircuitId === c.id ? t("ipam.circuits.hideTerms") : t("ipam.circuits.showTerms")}
                  </button>{" "}
                  <button
                    type="button"
                    className={dcimStyles.btnLink}
                    disabled={delM.isPending}
                    onClick={() => delM.mutate(c.id)}
                  >
                    {t("dcim.common.delete")}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : null}
      {termCircuitId != null ? (
        <section className={dcimStyles.mfrDetailSection} style={{ marginTop: "var(--space-3)" }}>
          <h3 className={dcimStyles.mfrDetailSectionTitle}>{t("ipam.circuits.termTitle")}</h3>
          <p className={dcimStyles.muted}>{t("ipam.circuits.termHint")}</p>
          {termsQ.isLoading ? <p className={dcimStyles.muted}>{t("dcim.common.loading")}</p> : null}
          <ul className={dcimStyles.ipList}>
            {(termsQ.data ?? []).map((x) => (
              <li key={x.id}>
                {x.endpoint.toUpperCase()}: iface #{x.interface_id ?? "—"} {x.label ? `(${x.label})` : ""}
              </li>
            ))}
          </ul>
          <form
            className={dcimStyles.formRow}
            style={{ flexWrap: "wrap", marginTop: "var(--space-2)" }}
            onSubmit={(e) => {
              e.preventDefault();
              setErr(null);
              termM.mutate();
            }}
          >
            <label>
              {t("ipam.circuits.endpoint")}
              <select value={termEndpoint} onChange={(e) => setTermEndpoint(e.target.value as "a" | "z")}>
                <option value="a">A</option>
                <option value="z">Z</option>
              </select>
            </label>
            <label>
              {t("ipam.circuits.interfaceId")}
              <input type="number" min={1} value={termIface} onChange={(e) => setTermIface(e.target.value)} />
            </label>
            <button type="submit" className={dcimStyles.btn} disabled={termM.isPending}>
              {termM.isPending ? "…" : t("ipam.circuits.saveTerm")}
            </button>
          </form>
        </section>
      ) : null}
    </Panel>
  );
}
