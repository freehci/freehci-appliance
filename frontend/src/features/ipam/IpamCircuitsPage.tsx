import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { Panel } from "@/components/ui/Panel";
import * as dcimApi from "@/features/dcim/dcimApi";
import { DcimInnerTabs } from "@/features/dcim/DcimInnerTabs";
import dcimStyles from "@/features/dcim/dcim.module.css";
import { useI18n } from "@/i18n/I18nProvider";
import type { MessageKey } from "@/i18n/messages/en";
import { ApiError } from "@/lib/api";
import * as ipamApi from "./ipamApi";
import prefixStyles from "./prefixPage.module.css";
import { PrefixDrawer } from "./prefixPageUi";
import type { IpamCircuit } from "./types";

const TABS = new Set(["transport", "overlay", "providers", "groups"]);
const TRANSPORT_TYPES = ["fiber", "radio", "leased_line"] as const;

function isTransportRow(c: IpamCircuit): boolean {
  return c.layer === "transport" || (c.layer == null && TRANSPORT_TYPES.includes(c.circuit_type as (typeof TRANSPORT_TYPES)[number]));
}

function providerLabel(
  c: IpamCircuit,
  providers: { id: number; name: string }[],
): string {
  const named = providers.find((p) => p.id === c.provider_id)?.name;
  return named ?? c.provider_name ?? "—";
}

function contractLabel(c: IpamCircuit, contracts: { id: number; name: string }[]): string {
  return contracts.find((x) => x.id === c.contract_id)?.name ?? "—";
}

function groupLabel(c: IpamCircuit, groups: { id: number; name: string }[]): string {
  return groups.find((x) => x.id === c.group_id)?.name ?? "—";
}

export function IpamCircuitsPage() {
  const { t } = useI18n();
  const qc = useQueryClient();
  const [searchParams, setSearchParams] = useSearchParams();
  const tabParam = searchParams.get("tab");
  const tab = tabParam != null && TABS.has(tabParam) ? tabParam : "transport";
  const setTab = (next: string) => {
    const n = new URLSearchParams(searchParams);
    if (next === "transport") n.delete("tab");
    else n.set("tab", next);
    setSearchParams(n, { replace: true });
  };

  const [err, setErr] = useState<string | null>(null);
  const [filterTenant, setFilterTenant] = useState("");
  const [tenantId, setTenantId] = useState("");
  const [circuitNumber, setCircuitNumber] = useState("");
  const [name, setName] = useState("");
  const [circuitType, setCircuitType] = useState<string>("fiber");
  const [isLeased, setIsLeased] = useState(false);
  const [providerId, setProviderId] = useState("");
  const [providerName, setProviderName] = useState("");
  const [contractId, setContractId] = useState("");
  const [groupId, setGroupId] = useState("");
  const [providerCircuitId, setProviderCircuitId] = useState("");
  const [capacityMbps, setCapacityMbps] = useState("");
  const [cirMbps, setCirMbps] = useState("");
  const [serviceType, setServiceType] = useState("");
  const [medium, setMedium] = useState("");
  const [operationalStatus, setOperationalStatus] = useState("");
  const [established, setEstablished] = useState("");
  const [contractEnd, setContractEnd] = useState("");
  const [termCircuitId, setTermCircuitId] = useState<number | null>(null);
  const [termEndpoint, setTermEndpoint] = useState<"a" | "z">("a");
  const [termSite, setTermSite] = useState("");
  const [termDevice, setTermDevice] = useState("");
  const [termIface, setTermIface] = useState("");
  const [aSiteId, setASiteId] = useState("");
  const [zSiteId, setZSiteId] = useState("");
  const [drawerOpen, setDrawerOpen] = useState(false);

  const [vpnName, setVpnName] = useState("");
  const [vpnType, setVpnType] = useState("wireguard");
  const [vpnTenant, setVpnTenant] = useState("");
  const [vpnDrawer, setVpnDrawer] = useState(false);
  const [openVpnId, setOpenVpnId] = useState<number | null>(null);
  const [tunnelName, setTunnelName] = useState("");
  const [openTunnelId, setOpenTunnelId] = useState<number | null>(null);
  const [peerName, setPeerName] = useState("");
  const [peerKeyRef, setPeerKeyRef] = useState("");
  const [peerIps, setPeerIps] = useState("");

  const [provName, setProvName] = useState("");
  const [provSlug, setProvSlug] = useState("");
  const [provDrawer, setProvDrawer] = useState(false);
  const [openProvId, setOpenProvId] = useState<number | null>(null);
  const [accName, setAccName] = useState("");
  const [accNumber, setAccNumber] = useState("");
  const [ctrName, setCtrName] = useState("");
  const [ctrSlug, setCtrSlug] = useState("");
  const [ctrRef, setCtrRef] = useState("");
  const [ctrStart, setCtrStart] = useState("");
  const [ctrEnd, setCtrEnd] = useState("");
  const [grpName, setGrpName] = useState("");
  const [grpSlug, setGrpSlug] = useState("");
  const [grpRisk, setGrpRisk] = useState("");
  const [grpDrawer, setGrpDrawer] = useState(false);
  const [openGrpId, setOpenGrpId] = useState<number | null>(null);
  const [assignCircuitId, setAssignCircuitId] = useState("");

  const tenantIdFilter = filterTenant === "" ? undefined : Number(filterTenant);
  const tenantsQ = useQuery({ queryKey: ["tenants"], queryFn: dcimApi.listTenants });
  const sitesQ = useQuery({ queryKey: ["dcim", "sites"], queryFn: dcimApi.listSites });
  const devicesQ = useQuery({ queryKey: ["dcim", "devices"], queryFn: dcimApi.listDevices });
  const circuitsQ = useQuery({
    queryKey: ["ipam", "circuits", tenantIdFilter ?? "all"],
    queryFn: () => ipamApi.listIpamCircuits(tenantIdFilter),
  });
  const providersQ = useQuery({ queryKey: ["ipam", "providers"], queryFn: ipamApi.listIpamProviders });
  const vpnQ = useQuery({
    queryKey: ["ipam", "vpn-services", tenantIdFilter ?? "all"],
    queryFn: () => ipamApi.listVpnServices(tenantIdFilter),
  });
  const termsQ = useQuery({
    queryKey: ["ipam", "circuit-terms", termCircuitId],
    queryFn: () => ipamApi.listCircuitTerminations(termCircuitId!),
    enabled: termCircuitId != null && termCircuitId > 0,
  });
  const termIfacesQ = useQuery({
    queryKey: ["dcim", "device-ifaces", termDevice],
    queryFn: () => dcimApi.listDeviceInterfaces(Number(termDevice)),
    enabled: termDevice !== "",
  });
  const accountsQ = useQuery({
    queryKey: ["ipam", "provider-accounts", openProvId],
    queryFn: () => ipamApi.listProviderAccounts(openProvId!),
    enabled: openProvId != null,
  });
  const contractsQ = useQuery({ queryKey: ["ipam", "contracts"], queryFn: () => ipamApi.listIpamContracts() });
  const groupsQ = useQuery({ queryKey: ["ipam", "circuit-groups"], queryFn: () => ipamApi.listIpamCircuitGroups() });
  const openContractsQ = useQuery({
    queryKey: ["ipam", "contracts", openProvId],
    queryFn: () => ipamApi.listIpamContracts(openProvId!),
    enabled: openProvId != null,
  });
  const tunnelsQ = useQuery({
    queryKey: ["ipam", "vpn-tunnels", openVpnId],
    queryFn: () => ipamApi.listVpnTunnels(openVpnId!),
    enabled: openVpnId != null,
  });
  const peersQ = useQuery({
    queryKey: ["ipam", "tunnel-peers", openTunnelId],
    queryFn: () => ipamApi.listTunnelPeers(openTunnelId!),
    enabled: openTunnelId != null,
  });

  const transportRows = useMemo(
    () => (circuitsQ.data ?? []).filter(isTransportRow),
    [circuitsQ.data],
  );
  const unclassified = useMemo(
    () => (circuitsQ.data ?? []).filter((c) => c.needs_classification),
    [circuitsQ.data],
  );

  const fail = (e: Error) => setErr(e instanceof ApiError ? e.message : e.message);

  const createM = useMutation({
    mutationFn: () =>
      ipamApi.createIpamCircuit({
        tenant_id: tenantId === "" ? null : Number(tenantId),
        circuit_number: circuitNumber.trim(),
        name: name.trim(),
        circuit_type: circuitType,
        layer: TRANSPORT_TYPES.includes(circuitType as (typeof TRANSPORT_TYPES)[number]) ? "transport" : null,
        is_leased: isLeased,
        provider_id: providerId === "" ? null : Number(providerId),
        provider_name: providerName.trim() === "" ? null : providerName.trim(),
        contract_id: contractId === "" ? null : Number(contractId),
        group_id: groupId === "" ? null : Number(groupId),
        provider_circuit_id: providerCircuitId.trim() === "" ? null : providerCircuitId.trim(),
        capacity_mbps: capacityMbps.trim() === "" ? null : Number(capacityMbps),
        cir_mbps: cirMbps.trim() === "" ? null : Number(cirMbps),
        established_on: established.trim() === "" ? null : established.trim(),
        contract_end_on: contractEnd.trim() === "" ? null : contractEnd.trim(),
        a_site_id: aSiteId === "" ? null : Number(aSiteId),
        z_site_id: zSiteId === "" ? null : Number(zSiteId),
        service_type: serviceType === "" ? null : serviceType,
        medium: medium === "" ? null : medium,
        operational_status: operationalStatus === "" ? null : operationalStatus,
      }),
    onSuccess: () => {
      setErr(null);
      setCircuitNumber("");
      setName("");
      setProviderName("");
      setProviderId("");
      setContractId("");
      setGroupId("");
      setProviderCircuitId("");
      setCapacityMbps("");
      setCirMbps("");
      setServiceType("");
      setMedium("");
      setOperationalStatus("");
      setEstablished("");
      setContractEnd("");
      setDrawerOpen(false);
      void qc.invalidateQueries({ queryKey: ["ipam", "circuits"] });
    },
    onError: fail,
  });

  const delM = useMutation({
    mutationFn: (id: number) => ipamApi.deleteIpamCircuit(id),
    onSuccess: () => {
      setErr(null);
      if (termCircuitId != null) setTermCircuitId(null);
      void qc.invalidateQueries({ queryKey: ["ipam", "circuits"] });
    },
    onError: fail,
  });

  const classifyM = useMutation({
    mutationFn: (args: { id: number; layer: "transport" | "overlay" }) =>
      ipamApi.classifyIpamCircuit(args.id, { layer: args.layer, create_vpn: true }),
    onSuccess: () => {
      setErr(null);
      void qc.invalidateQueries({ queryKey: ["ipam", "circuits"] });
      void qc.invalidateQueries({ queryKey: ["ipam", "vpn-services"] });
    },
    onError: fail,
  });

  const termM = useMutation({
    mutationFn: () =>
      ipamApi.upsertCircuitTermination(termCircuitId!, {
        endpoint: termEndpoint,
        device_id: termDevice === "" ? null : Number(termDevice),
        interface_id: termIface === "" ? null : Number(termIface),
        site_id: termSite === "" ? null : Number(termSite),
      }),
    onSuccess: () => {
      setErr(null);
      void qc.invalidateQueries({ queryKey: ["ipam", "circuit-terms", termCircuitId] });
    },
    onError: fail,
  });

  const createVpnM = useMutation({
    mutationFn: () =>
      ipamApi.createVpnService({
        name: vpnName.trim(),
        vpn_type: vpnType,
        tenant_id: vpnTenant === "" ? null : Number(vpnTenant),
      }),
    onSuccess: () => {
      setErr(null);
      setVpnName("");
      setVpnDrawer(false);
      void qc.invalidateQueries({ queryKey: ["ipam", "vpn-services"] });
    },
    onError: fail,
  });

  const delVpnM = useMutation({
    mutationFn: (id: number) => ipamApi.deleteVpnService(id),
    onSuccess: () => {
      setErr(null);
      setOpenVpnId(null);
      void qc.invalidateQueries({ queryKey: ["ipam", "vpn-services"] });
    },
    onError: fail,
  });

  const createTunnelM = useMutation({
    mutationFn: () => ipamApi.createVpnTunnel(openVpnId!, { name: tunnelName.trim() }),
    onSuccess: () => {
      setErr(null);
      setTunnelName("");
      void qc.invalidateQueries({ queryKey: ["ipam", "vpn-tunnels", openVpnId] });
    },
    onError: fail,
  });

  const createPeerM = useMutation({
    mutationFn: () =>
      ipamApi.createTunnelPeer(openTunnelId!, {
        name: peerName.trim(),
        public_key_ref: peerKeyRef.trim() === "" ? null : peerKeyRef.trim(),
        allowed_ips: peerIps.trim() === "" ? null : peerIps.split(/[,\s]+/).map((x) => x.trim()).filter(Boolean),
      }),
    onSuccess: () => {
      setErr(null);
      setPeerName("");
      setPeerKeyRef("");
      setPeerIps("");
      void qc.invalidateQueries({ queryKey: ["ipam", "tunnel-peers", openTunnelId] });
    },
    onError: fail,
  });

  const createProvM = useMutation({
    mutationFn: () => ipamApi.createIpamProvider({ name: provName.trim(), slug: provSlug.trim() || null }),
    onSuccess: () => {
      setErr(null);
      setProvName("");
      setProvSlug("");
      setProvDrawer(false);
      void qc.invalidateQueries({ queryKey: ["ipam", "providers"] });
    },
    onError: fail,
  });

  const delProvM = useMutation({
    mutationFn: (id: number) => ipamApi.deleteIpamProvider(id),
    onSuccess: () => {
      setErr(null);
      setOpenProvId(null);
      void qc.invalidateQueries({ queryKey: ["ipam", "providers"] });
    },
    onError: fail,
  });

  const createAccM = useMutation({
    mutationFn: () =>
      ipamApi.createProviderAccount(openProvId!, {
        name: accName.trim(),
        account_number: accNumber.trim() || null,
      }),
    onSuccess: () => {
      setErr(null);
      setAccName("");
      setAccNumber("");
      void qc.invalidateQueries({ queryKey: ["ipam", "provider-accounts", openProvId] });
    },
    onError: fail,
  });

  const createCtrM = useMutation({
    mutationFn: () =>
      ipamApi.createIpamContract({
        provider_id: openProvId!,
        name: ctrName.trim(),
        slug: ctrSlug.trim() || null,
        reference: ctrRef.trim() || null,
        starts_on: ctrStart.trim() === "" ? null : ctrStart.trim(),
        ends_on: ctrEnd.trim() === "" ? null : ctrEnd.trim(),
      }),
    onSuccess: () => {
      setErr(null);
      setCtrName("");
      setCtrSlug("");
      setCtrRef("");
      setCtrStart("");
      setCtrEnd("");
      void qc.invalidateQueries({ queryKey: ["ipam", "contracts"] });
    },
    onError: fail,
  });

  const delCtrM = useMutation({
    mutationFn: (id: number) => ipamApi.deleteIpamContract(id),
    onSuccess: () => {
      setErr(null);
      void qc.invalidateQueries({ queryKey: ["ipam", "contracts"] });
      void qc.invalidateQueries({ queryKey: ["ipam", "circuits"] });
    },
    onError: fail,
  });

  const createGrpM = useMutation({
    mutationFn: () =>
      ipamApi.createIpamCircuitGroup({
        name: grpName.trim(),
        slug: grpSlug.trim() || null,
        shared_risk: grpRisk.trim() || null,
        tenant_id: filterTenant === "" ? null : Number(filterTenant),
      }),
    onSuccess: () => {
      setErr(null);
      setGrpName("");
      setGrpSlug("");
      setGrpRisk("");
      setGrpDrawer(false);
      void qc.invalidateQueries({ queryKey: ["ipam", "circuit-groups"] });
    },
    onError: fail,
  });

  const delGrpM = useMutation({
    mutationFn: (id: number) => ipamApi.deleteIpamCircuitGroup(id),
    onSuccess: () => {
      setErr(null);
      setOpenGrpId(null);
      void qc.invalidateQueries({ queryKey: ["ipam", "circuit-groups"] });
      void qc.invalidateQueries({ queryKey: ["ipam", "circuits"] });
    },
    onError: fail,
  });

  const assignGrpM = useMutation({
    mutationFn: () => ipamApi.patchIpamCircuit(Number(assignCircuitId), { group_id: openGrpId }),
    onSuccess: () => {
      setErr(null);
      setAssignCircuitId("");
      void qc.invalidateQueries({ queryKey: ["ipam", "circuits"] });
    },
    onError: fail,
  });

  const siteName = (id: number | null | undefined) =>
    (sitesQ.data ?? []).find((s) => s.id === id)?.name ?? "—";
  const devices = devicesQ.data ?? [];
  const termDevices = termSite
    ? devices.filter((d) => (d.effective_site_id ?? d.site_id) === Number(termSite))
    : devices;

  const typeLabel = (type: string) => {
    const keys: Record<string, MessageKey> = {
      fiber: "ipam.circuits.type.fiber",
      vpn: "ipam.circuits.type.vpn",
      wireguard: "ipam.circuits.type.wireguard",
      radio: "ipam.circuits.type.radio",
      leased_line: "ipam.circuits.type.leased_line",
      other: "ipam.circuits.type.other",
    };
    return keys[type] ? t(keys[type]) : type;
  };

  const newLabel =
    tab === "providers"
      ? t("ipam.circuits.newProvider")
      : tab === "overlay"
        ? t("ipam.circuits.newVpn")
        : tab === "groups"
          ? t("ipam.circuits.newGroup")
          : t("ipam.circuits.new");

  return (
    <Panel>
      {err ? <p className={dcimStyles.err}>{err}</p> : null}
      <header className={prefixStyles.pageHead}>
        <div>
          <p className={prefixStyles.crumb}>
            {t("ipam.ipv4.crumbIpam")}
            <span className={prefixStyles.crumbSep}>/</span>
            {t("nav.circuits")}
          </p>
          <h1 className={prefixStyles.title}>{t("ipam.circuits.title")}</h1>
          <p className={prefixStyles.intro}>{t("ipam.circuits.intro")}</p>
          <p className={prefixStyles.intro}>{t("ipam.circuits.placementHint")}</p>
        </div>
        <div className={prefixStyles.headActions}>
          <button
            type="button"
            className={dcimStyles.btn}
            onClick={() => {
              setErr(null);
              if (tab === "providers") setProvDrawer(true);
              else if (tab === "overlay") setVpnDrawer(true);
              else if (tab === "groups") setGrpDrawer(true);
              else {
                if (filterTenant && tenantId === "") setTenantId(filterTenant);
                setDrawerOpen(true);
              }
            }}
          >
            + {newLabel}
          </button>
        </div>
      </header>
      <DcimInnerTabs
        ariaLabel={t("ipam.circuits.tabs")}
        activeId={tab}
        onChange={setTab}
        tabs={[
          { id: "transport", label: t("ipam.circuits.tabTransport") },
          { id: "overlay", label: t("ipam.circuits.tabOverlay") },
          { id: "providers", label: t("ipam.circuits.tabProviders") },
          { id: "groups", label: t("ipam.circuits.tabGroups") },
        ]}
      />
      <div className={prefixStyles.toolbar}>
        <label className={prefixStyles.toolbarField}>
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

      {tab === "transport" ? (
        <div className={prefixStyles.tableCard}>
          {circuitsQ.isLoading ? (
            <p className={dcimStyles.muted} style={{ padding: "var(--space-3)" }}>
              {t("dcim.common.loading")}
            </p>
          ) : null}
          {transportRows.length === 0 && !circuitsQ.isLoading ? (
            <p className={dcimStyles.muted} style={{ padding: "var(--space-3)" }}>
              {t("ipam.circuits.emptyTransport")}
            </p>
          ) : null}
          {transportRows.length > 0 ? (
            <div className={prefixStyles.tableScroll}>
              <table className={dcimStyles.table}>
                <thead>
                  <tr>
                    <th>{t("ipam.circuits.number")}</th>
                    <th>{t("ipam.ipv4.name")}</th>
                    <th>{t("ipam.circuits.type")}</th>
                    <th>{t("ipam.circuits.serviceType")}</th>
                    <th>{t("ipam.circuits.medium")}</th>
                    <th>{t("ipam.circuits.operationalStatus")}</th>
                    <th>{t("ipam.circuits.layer")}</th>
                    <th>{t("ipam.circuits.aSite")}</th>
                    <th>{t("ipam.circuits.zSite")}</th>
                    <th>{t("ipam.circuits.leased")}</th>
                    <th>{t("ipam.circuits.provider")}</th>
                    <th>{t("ipam.circuits.contract")}</th>
                    <th>{t("ipam.circuits.group")}</th>
                    <th>{t("ipam.circuits.providerCircuitId")}</th>
                    <th>{t("ipam.circuits.cirMbps")}</th>
                    <th>{t("ipam.ipv4.actionsCol")}</th>
                  </tr>
                </thead>
                <tbody>
                  {transportRows.map((c) => (
                    <tr key={c.id}>
                      <td>{c.circuit_number}</td>
                      <td>{c.name}</td>
                      <td>{typeLabel(c.circuit_type)}</td>
                      <td>{c.service_type ?? "—"}</td>
                      <td>{c.medium ?? "—"}</td>
                      <td>{c.operational_status ?? "—"}</td>
                      <td>{c.layer ?? t("ipam.circuits.layerUnset")}</td>
                      <td>{siteName(c.a_site_id)}</td>
                      <td>{siteName(c.z_site_id)}</td>
                      <td>{c.is_leased ? t("ipam.circuits.yes") : t("ipam.circuits.no")}</td>
                      <td>{providerLabel(c, providersQ.data ?? [])}</td>
                      <td>{contractLabel(c, contractsQ.data ?? [])}</td>
                      <td>{groupLabel(c, groupsQ.data ?? [])}</td>
                      <td>{c.provider_circuit_id ?? "—"}</td>
                      <td>
                        {c.cir_mbps != null || c.capacity_mbps != null
                          ? `${c.cir_mbps ?? "—"} / ${c.capacity_mbps ?? "—"}`
                          : "—"}
                      </td>
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
            </div>
          ) : null}
        </div>
      ) : null}

      {tab === "overlay" ? (
        <>
          {unclassified.length > 0 ? (
            <div className={prefixStyles.tableCard} style={{ marginBottom: "var(--space-3)" }}>
              <p className={dcimStyles.muted} style={{ padding: "var(--space-3)", paddingBottom: 0 }}>
                {t("ipam.circuits.classifyHint")}
              </p>
              <div className={prefixStyles.tableScroll}>
                <table className={dcimStyles.table}>
                  <thead>
                    <tr>
                      <th>{t("ipam.circuits.number")}</th>
                      <th>{t("ipam.ipv4.name")}</th>
                      <th>{t("ipam.circuits.type")}</th>
                      <th>{t("ipam.ipv4.actionsCol")}</th>
                    </tr>
                  </thead>
                  <tbody>
                    {unclassified.map((c) => (
                      <tr key={c.id}>
                        <td>{c.circuit_number}</td>
                        <td>{c.name}</td>
                        <td>{typeLabel(c.circuit_type)}</td>
                        <td>
                          <button
                            type="button"
                            className={dcimStyles.btnLink}
                            disabled={classifyM.isPending}
                            onClick={() => classifyM.mutate({ id: c.id, layer: "transport" })}
                          >
                            {t("ipam.circuits.classifyTransport")}
                          </button>{" "}
                          <button
                            type="button"
                            className={dcimStyles.btnLink}
                            disabled={classifyM.isPending}
                            onClick={() => classifyM.mutate({ id: c.id, layer: "overlay" })}
                          >
                            {t("ipam.circuits.classifyOverlay")}
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          ) : null}
          <div className={prefixStyles.tableCard}>
            {vpnQ.isLoading ? (
              <p className={dcimStyles.muted} style={{ padding: "var(--space-3)" }}>
                {t("dcim.common.loading")}
              </p>
            ) : null}
            {(vpnQ.data ?? []).length === 0 && !vpnQ.isLoading ? (
              <p className={dcimStyles.muted} style={{ padding: "var(--space-3)" }}>
                {t("ipam.circuits.emptyVpn")}
              </p>
            ) : null}
            {(vpnQ.data ?? []).length > 0 ? (
              <div className={prefixStyles.tableScroll}>
                <table className={dcimStyles.table}>
                  <thead>
                    <tr>
                      <th>{t("ipam.ipv4.name")}</th>
                      <th>{t("ipam.circuits.vpnType")}</th>
                      <th>{t("ipam.circuits.sourceCircuit")}</th>
                      <th>{t("ipam.ipv4.actionsCol")}</th>
                    </tr>
                  </thead>
                  <tbody>
                    {(vpnQ.data ?? []).map((v) => {
                      const src = (circuitsQ.data ?? []).find((c) => c.id === v.source_circuit_id);
                      return (
                        <tr key={v.id}>
                          <td>{v.name}</td>
                          <td>{v.vpn_type}</td>
                          <td>{src?.circuit_number ?? "—"}</td>
                          <td>
                            <button
                              type="button"
                              className={dcimStyles.btnLink}
                              onClick={() => setOpenVpnId(openVpnId === v.id ? null : v.id)}
                            >
                              {openVpnId === v.id ? t("ipam.circuits.hideTunnels") : t("ipam.circuits.showTunnels")}
                            </button>{" "}
                            <button
                              type="button"
                              className={dcimStyles.btnLink}
                              disabled={delVpnM.isPending}
                              onClick={() => delVpnM.mutate(v.id)}
                            >
                              {t("dcim.common.delete")}
                            </button>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            ) : null}
          </div>
          {openVpnId != null ? (
            <section className={dcimStyles.mfrDetailSection} style={{ marginTop: "var(--space-3)" }}>
              <VpnMembersPanel vpnId={openVpnId} onError={setErr} />
              <h3 className={dcimStyles.mfrDetailSectionTitle}>{t("ipam.circuits.tunnels")}</h3>
              <ul className={dcimStyles.ipList}>
                {(tunnelsQ.data ?? []).map((tun) => (
                  <li key={tun.id}>
                    {tun.name} ({tun.status}){" "}
                    <button
                      type="button"
                      className={dcimStyles.btnLink}
                      onClick={() => setOpenTunnelId(openTunnelId === tun.id ? null : tun.id)}
                    >
                      {openTunnelId === tun.id ? t("ipam.circuits.hidePeers") : t("ipam.circuits.showPeers")}
                    </button>
                  </li>
                ))}
              </ul>
              <form
                className={dcimStyles.formRow}
                style={{ flexWrap: "wrap", marginTop: "var(--space-2)" }}
                onSubmit={(e) => {
                  e.preventDefault();
                  setErr(null);
                  createTunnelM.mutate();
                }}
              >
                <label>
                  {t("ipam.ipv4.name")}
                  <input value={tunnelName} onChange={(e) => setTunnelName(e.target.value)} required />
                </label>
                <button type="submit" className={dcimStyles.btn} disabled={createTunnelM.isPending}>
                  {t("ipam.circuits.addTunnel")}
                </button>
              </form>
              {openTunnelId != null ? (
                <>
                  <h4 className={dcimStyles.mfrDetailSectionTitle}>{t("ipam.circuits.peers")}</h4>
                  <p className={dcimStyles.muted}>{t("ipam.circuits.peerHint")}</p>
                  <ul className={dcimStyles.ipList}>
                    {(peersQ.data ?? []).map((p) => (
                      <li key={p.id}>
                        {p.name} {p.public_key_ref ? `(${p.public_key_ref})` : ""}{" "}
                        {(p.allowed_ips ?? []).join(", ")}
                      </li>
                    ))}
                  </ul>
                  <form
                    className={dcimStyles.formRow}
                    style={{ flexWrap: "wrap", marginTop: "var(--space-2)" }}
                    onSubmit={(e) => {
                      e.preventDefault();
                      setErr(null);
                      createPeerM.mutate();
                    }}
                  >
                    <label>
                      {t("ipam.ipv4.name")}
                      <input value={peerName} onChange={(e) => setPeerName(e.target.value)} required />
                    </label>
                    <label>
                      {t("ipam.circuits.publicKeyRef")}
                      <input
                        value={peerKeyRef}
                        onChange={(e) => setPeerKeyRef(e.target.value)}
                        placeholder="secret:wg-peer-…"
                      />
                    </label>
                    <label>
                      {t("ipam.circuits.allowedIps")}
                      <input value={peerIps} onChange={(e) => setPeerIps(e.target.value)} placeholder="10.8.0.2/32" />
                    </label>
                    <button type="submit" className={dcimStyles.btn} disabled={createPeerM.isPending}>
                      {t("ipam.circuits.addPeer")}
                    </button>
                  </form>
                  <TunnelTransportsPanel tunnelId={openTunnelId} onError={setErr} />
                </>
              ) : null}
            </section>
          ) : null}
        </>
      ) : null}

      {tab === "providers" ? (
        <div className={prefixStyles.tableCard}>
          {providersQ.isLoading ? (
            <p className={dcimStyles.muted} style={{ padding: "var(--space-3)" }}>
              {t("dcim.common.loading")}
            </p>
          ) : null}
          {(providersQ.data ?? []).length === 0 && !providersQ.isLoading ? (
            <p className={dcimStyles.muted} style={{ padding: "var(--space-3)" }}>
              {t("ipam.circuits.emptyProviders")}
            </p>
          ) : null}
          {(providersQ.data ?? []).length > 0 ? (
            <div className={prefixStyles.tableScroll}>
              <table className={dcimStyles.table}>
                <thead>
                  <tr>
                    <th>{t("ipam.ipv4.name")}</th>
                    <th>Slug</th>
                    <th>ASN</th>
                    <th>{t("ipam.ipv4.actionsCol")}</th>
                  </tr>
                </thead>
                <tbody>
                  {(providersQ.data ?? []).map((p) => (
                    <tr key={p.id}>
                      <td>{p.name}</td>
                      <td>{p.slug}</td>
                      <td>{p.asn ?? "—"}</td>
                      <td>
                        <button
                          type="button"
                          className={dcimStyles.btnLink}
                          onClick={() => setOpenProvId(openProvId === p.id ? null : p.id)}
                        >
                          {openProvId === p.id ? t("ipam.circuits.hideAccounts") : t("ipam.circuits.showAccounts")}
                        </button>{" "}
                        <button
                          type="button"
                          className={dcimStyles.btnLink}
                          disabled={delProvM.isPending}
                          onClick={() => delProvM.mutate(p.id)}
                        >
                          {t("dcim.common.delete")}
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : null}
          {openProvId != null ? (
            <section className={dcimStyles.mfrDetailSection} style={{ padding: "var(--space-3)" }}>
              <h3 className={dcimStyles.mfrDetailSectionTitle}>{t("ipam.circuits.accounts")}</h3>
              <ul className={dcimStyles.ipList}>
                {(accountsQ.data ?? []).map((a) => (
                  <li key={a.id}>
                    {a.name} {a.account_number ? `(${a.account_number})` : ""}
                  </li>
                ))}
              </ul>
              <form
                className={dcimStyles.formRow}
                style={{ flexWrap: "wrap" }}
                onSubmit={(e) => {
                  e.preventDefault();
                  setErr(null);
                  createAccM.mutate();
                }}
              >
                <label>
                  {t("ipam.ipv4.name")}
                  <input value={accName} onChange={(e) => setAccName(e.target.value)} required />
                </label>
                <label>
                  {t("ipam.circuits.accountNumber")}
                  <input value={accNumber} onChange={(e) => setAccNumber(e.target.value)} />
                </label>
                <button type="submit" className={dcimStyles.btn} disabled={createAccM.isPending}>
                  {t("ipam.circuits.addAccount")}
                </button>
              </form>
              <h3 className={dcimStyles.mfrDetailSectionTitle} style={{ marginTop: "var(--space-3)" }}>
                {t("ipam.circuits.contracts")}
              </h3>
              <p className={dcimStyles.muted}>{t("ipam.circuits.contractHint")}</p>
              {(openContractsQ.data ?? []).length === 0 && !openContractsQ.isLoading ? (
                <p className={dcimStyles.muted}>{t("ipam.circuits.emptyContracts")}</p>
              ) : null}
              <ul className={dcimStyles.ipList}>
                {(openContractsQ.data ?? []).map((ctr) => (
                  <li key={ctr.id}>
                    {ctr.name}
                    {ctr.reference ? ` (${ctr.reference})` : ""}
                    {ctr.ends_on ? ` · ${ctr.ends_on}` : ""}{" "}
                    <button
                      type="button"
                      className={dcimStyles.btnLink}
                      disabled={delCtrM.isPending}
                      onClick={() => delCtrM.mutate(ctr.id)}
                    >
                      {t("dcim.common.delete")}
                    </button>
                  </li>
                ))}
              </ul>
              <form
                className={dcimStyles.formRow}
                style={{ flexWrap: "wrap" }}
                onSubmit={(e) => {
                  e.preventDefault();
                  setErr(null);
                  createCtrM.mutate();
                }}
              >
                <label>
                  {t("ipam.ipv4.name")}
                  <input value={ctrName} onChange={(e) => setCtrName(e.target.value)} required />
                </label>
                <label>
                  Slug
                  <input value={ctrSlug} onChange={(e) => setCtrSlug(e.target.value)} />
                </label>
                <label>
                  {t("ipam.circuits.contractRef")}
                  <input value={ctrRef} onChange={(e) => setCtrRef(e.target.value)} />
                </label>
                <label>
                  {t("ipam.circuits.contractStarts")}
                  <input type="date" value={ctrStart} onChange={(e) => setCtrStart(e.target.value)} />
                </label>
                <label>
                  {t("ipam.circuits.contractEnds")}
                  <input type="date" value={ctrEnd} onChange={(e) => setCtrEnd(e.target.value)} />
                </label>
                <button type="submit" className={dcimStyles.btn} disabled={createCtrM.isPending}>
                  {t("ipam.circuits.addContract")}
                </button>
              </form>
            </section>
          ) : null}
        </div>
      ) : null}

      {tab === "groups" ? (
        <div className={prefixStyles.tableCard}>
          <p className={dcimStyles.muted} style={{ padding: "var(--space-3)", paddingBottom: 0 }}>
            {t("ipam.circuits.groupHint")}
          </p>
          {groupsQ.isLoading ? (
            <p className={dcimStyles.muted} style={{ padding: "var(--space-3)" }}>
              {t("dcim.common.loading")}
            </p>
          ) : null}
          {(groupsQ.data ?? []).length === 0 && !groupsQ.isLoading ? (
            <p className={dcimStyles.muted} style={{ padding: "var(--space-3)" }}>
              {t("ipam.circuits.emptyGroups")}
            </p>
          ) : null}
          {(groupsQ.data ?? []).length > 0 ? (
            <div className={prefixStyles.tableScroll}>
              <table className={dcimStyles.table}>
                <thead>
                  <tr>
                    <th>{t("ipam.ipv4.name")}</th>
                    <th>Slug</th>
                    <th>{t("ipam.circuits.sharedRisk")}</th>
                    <th>{t("ipam.ipv4.actionsCol")}</th>
                  </tr>
                </thead>
                <tbody>
                  {(groupsQ.data ?? []).map((g) => (
                    <tr key={g.id}>
                      <td>{g.name}</td>
                      <td>{g.slug}</td>
                      <td>{g.shared_risk ?? "—"}</td>
                      <td>
                        <button
                          type="button"
                          className={dcimStyles.btnLink}
                          onClick={() => setOpenGrpId(openGrpId === g.id ? null : g.id)}
                        >
                          {openGrpId === g.id ? t("ipam.circuits.hideMembers") : t("ipam.circuits.showMembers")}
                        </button>{" "}
                        <button
                          type="button"
                          className={dcimStyles.btnLink}
                          disabled={delGrpM.isPending}
                          onClick={() => delGrpM.mutate(g.id)}
                        >
                          {t("dcim.common.delete")}
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : null}
          {openGrpId != null ? (
            <section className={dcimStyles.mfrDetailSection} style={{ padding: "var(--space-3)" }}>
              <h3 className={dcimStyles.mfrDetailSectionTitle}>{t("ipam.circuits.members")}</h3>
              <ul className={dcimStyles.ipList}>
                {(circuitsQ.data ?? [])
                  .filter((c) => c.group_id === openGrpId)
                  .map((c) => (
                    <li key={c.id}>
                      {c.circuit_number} · {c.name}
                    </li>
                  ))}
              </ul>
              <form
                className={dcimStyles.formRow}
                style={{ flexWrap: "wrap" }}
                onSubmit={(e) => {
                  e.preventDefault();
                  setErr(null);
                  assignGrpM.mutate();
                }}
              >
                <label>
                  {t("ipam.circuits.number")}
                  <select value={assignCircuitId} onChange={(e) => setAssignCircuitId(e.target.value)} required>
                    <option value="">{t("ipam.circuits.noCircuit")}</option>
                    {(circuitsQ.data ?? [])
                      .filter((c) => c.group_id !== openGrpId)
                      .map((c) => (
                        <option key={c.id} value={String(c.id)}>
                          {c.circuit_number} · {c.name}
                        </option>
                      ))}
                  </select>
                </label>
                <button type="submit" className={dcimStyles.btn} disabled={assignGrpM.isPending || assignCircuitId === ""}>
                  {t("ipam.circuits.addMember")}
                </button>
              </form>
            </section>
          ) : null}
        </div>
      ) : null}

      {termCircuitId != null && tab === "transport" ? (
        <section className={dcimStyles.mfrDetailSection} style={{ marginTop: "var(--space-3)" }}>
          <h3 className={dcimStyles.mfrDetailSectionTitle}>{t("ipam.circuits.termTitle")}</h3>
          <p className={dcimStyles.muted}>{t("ipam.circuits.termHint")}</p>
          {termsQ.isLoading ? <p className={dcimStyles.muted}>{t("dcim.common.loading")}</p> : null}
          <ul className={dcimStyles.ipList}>
            {(termsQ.data ?? []).map((x) => (
              <li key={x.id}>
                {x.endpoint.toUpperCase()}: {x.device_name ?? "—"} / {x.interface_name ?? "—"}
                {x.label ? ` (${x.label})` : ""}
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
              {t("ipam.circuits.termSite")}
              <select
                value={termSite}
                onChange={(e) => {
                  setTermSite(e.target.value);
                  setTermDevice("");
                  setTermIface("");
                }}
              >
                <option value="">{t("ipam.circuits.noSite")}</option>
                {(sitesQ.data ?? []).map((s) => (
                  <option key={s.id} value={String(s.id)}>
                    {s.name}
                  </option>
                ))}
              </select>
            </label>
            <label>
              {t("ipam.circuits.device")}
              <select
                value={termDevice}
                onChange={(e) => {
                  setTermDevice(e.target.value);
                  setTermIface("");
                }}
              >
                <option value="">{t("ipam.circuits.noDevice")}</option>
                {termDevices.map((d) => (
                  <option key={d.id} value={String(d.id)}>
                    {d.name}
                  </option>
                ))}
              </select>
            </label>
            <label>
              {t("ipam.circuits.interface")}
              <select value={termIface} onChange={(e) => setTermIface(e.target.value)} disabled={termDevice === ""}>
                <option value="">{t("ipam.circuits.noInterface")}</option>
                {(termIfacesQ.data ?? []).map((iface) => (
                  <option key={iface.id} value={String(iface.id)}>
                    {iface.name}
                  </option>
                ))}
              </select>
            </label>
            <button type="submit" className={dcimStyles.btn} disabled={termM.isPending}>
              {termM.isPending ? "…" : t("ipam.circuits.saveTerm")}
            </button>
          </form>
          <CircuitStrandsPanel circuitId={termCircuitId} onError={setErr} />
        </section>
      ) : null}

      <PrefixDrawer
        title={t("ipam.circuits.addTitle")}
        open={drawerOpen}
        onClose={() => {
          if (!createM.isPending) setDrawerOpen(false);
        }}
        footer={
          <>
            <button type="button" className={dcimStyles.btn} disabled={createM.isPending} onClick={() => setDrawerOpen(false)}>
              {t("dcim.common.cancel")}
            </button>
            <button
              type="button"
              className={dcimStyles.btn}
              disabled={createM.isPending}
              onClick={() => {
                setErr(null);
                createM.mutate();
              }}
            >
              {createM.isPending ? t("dcim.common.creating") : t("ipam.circuits.create")}
            </button>
          </>
        }
      >
        <div className={prefixStyles.drawerFields}>
          <label>
            {t("ipam.circuits.tenant")}
            <select value={tenantId} onChange={(e) => setTenantId(e.target.value)}>
              <option value="">{t("ipam.circuits.noTenant")}</option>
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
              <option value="radio">{t("ipam.circuits.type.radio")}</option>
              <option value="leased_line">{t("ipam.circuits.type.leased_line")}</option>
              <option value="other">{t("ipam.circuits.type.other")}</option>
            </select>
          </label>
          <label>
            {t("ipam.circuits.aSite")}
            <select value={aSiteId} onChange={(e) => setASiteId(e.target.value)}>
              <option value="">{t("ipam.circuits.noSite")}</option>
              {(sitesQ.data ?? []).map((s) => (
                <option key={s.id} value={String(s.id)}>
                  {s.name}
                </option>
              ))}
            </select>
          </label>
          <label>
            {t("ipam.circuits.zSite")}
            <select value={zSiteId} onChange={(e) => setZSiteId(e.target.value)}>
              <option value="">{t("ipam.circuits.noSite")}</option>
              {(sitesQ.data ?? []).map((s) => (
                <option key={s.id} value={String(s.id)}>
                  {s.name}
                </option>
              ))}
            </select>
          </label>
          <label className={prefixStyles.drawerCheck}>
            <input type="checkbox" checked={isLeased} onChange={(e) => setIsLeased(e.target.checked)} />
            {t("ipam.circuits.leased")}
          </label>
          <label>
            {t("ipam.circuits.provider")}
            <select
              value={providerId}
              onChange={(e) => {
                setProviderId(e.target.value);
                setContractId("");
              }}
            >
              <option value="">{t("ipam.circuits.noProvider")}</option>
              {(providersQ.data ?? []).map((p) => (
                <option key={p.id} value={String(p.id)}>
                  {p.name}
                </option>
              ))}
            </select>
          </label>
          <label>
            {t("ipam.circuits.contract")}
            <select value={contractId} onChange={(e) => setContractId(e.target.value)} disabled={providerId === ""}>
              <option value="">{t("ipam.circuits.noContract")}</option>
              {(contractsQ.data ?? [])
                .filter((ctr) => providerId !== "" && ctr.provider_id === Number(providerId))
                .map((ctr) => (
                  <option key={ctr.id} value={String(ctr.id)}>
                    {ctr.name}
                  </option>
                ))}
            </select>
          </label>
          <label>
            {t("ipam.circuits.group")}
            <select value={groupId} onChange={(e) => setGroupId(e.target.value)}>
              <option value="">{t("ipam.circuits.noGroup")}</option>
              {(groupsQ.data ?? []).map((g) => (
                <option key={g.id} value={String(g.id)}>
                  {g.name}
                </option>
              ))}
            </select>
          </label>
          <label>
            {t("ipam.circuits.providerCircuitId")}
            <input value={providerCircuitId} onChange={(e) => setProviderCircuitId(e.target.value)} />
          </label>
          <p className={dcimStyles.muted}>{t("ipam.circuits.attrHint")}</p>
          <label>
            {t("ipam.circuits.serviceType")}
            <select value={serviceType} onChange={(e) => setServiceType(e.target.value)}>
              <option value="">{t("ipam.circuits.attrUnset")}</option>
              <option value="internet">internet</option>
              <option value="ethernet">ethernet</option>
              <option value="dark-fiber">dark-fiber</option>
              <option value="other">other</option>
            </select>
          </label>
          <label>
            {t("ipam.circuits.medium")}
            <select value={medium} onChange={(e) => setMedium(e.target.value)}>
              <option value="">{t("ipam.circuits.attrUnset")}</option>
              <option value="fiber">fiber</option>
              <option value="copper">copper</option>
              <option value="radio">radio</option>
              <option value="other">other</option>
            </select>
          </label>
          <label>
            {t("ipam.circuits.operationalStatus")}
            <select value={operationalStatus} onChange={(e) => setOperationalStatus(e.target.value)}>
              <option value="">{t("ipam.circuits.attrUnset")}</option>
              <option value="planned">planned</option>
              <option value="active">active</option>
              <option value="offline">offline</option>
              <option value="decommissioned">decommissioned</option>
            </select>
          </label>
          <p className={dcimStyles.muted}>{t("ipam.circuits.rateHint")}</p>
          <label>
            {t("ipam.circuits.capacityMbps")}
            <input type="number" min={1} value={capacityMbps} onChange={(e) => setCapacityMbps(e.target.value)} />
          </label>
          <label>
            {t("ipam.circuits.cirMbps")}
            <input type="number" min={1} value={cirMbps} onChange={(e) => setCirMbps(e.target.value)} />
          </label>
          <label>
            {t("ipam.circuits.providerFreeText")}
            <input value={providerName} onChange={(e) => setProviderName(e.target.value)} />
          </label>
          <label>
            {t("ipam.circuits.established")}
            <input type="date" value={established} onChange={(e) => setEstablished(e.target.value)} />
          </label>
          <label>
            {t("ipam.circuits.contractEnd")}
            <input type="date" value={contractEnd} onChange={(e) => setContractEnd(e.target.value)} />
          </label>
        </div>
      </PrefixDrawer>

      <PrefixDrawer
        title={t("ipam.circuits.addVpn")}
        open={vpnDrawer}
        onClose={() => {
          if (!createVpnM.isPending) setVpnDrawer(false);
        }}
        footer={
          <>
            <button type="button" className={dcimStyles.btn} disabled={createVpnM.isPending} onClick={() => setVpnDrawer(false)}>
              {t("dcim.common.cancel")}
            </button>
            <button
              type="button"
              className={dcimStyles.btn}
              disabled={createVpnM.isPending}
              onClick={() => {
                setErr(null);
                createVpnM.mutate();
              }}
            >
              {createVpnM.isPending ? t("dcim.common.creating") : t("ipam.circuits.createVpn")}
            </button>
          </>
        }
      >
        <div className={prefixStyles.drawerFields}>
          <label>
            {t("ipam.ipv4.name")}
            <input value={vpnName} onChange={(e) => setVpnName(e.target.value)} required />
          </label>
          <label>
            {t("ipam.circuits.vpnType")}
            <select value={vpnType} onChange={(e) => setVpnType(e.target.value)}>
              <option value="wireguard">WireGuard</option>
              <option value="ipsec">IPsec</option>
              <option value="other">{t("ipam.circuits.type.other")}</option>
            </select>
          </label>
          <label>
            {t("ipam.circuits.tenant")}
            <select value={vpnTenant} onChange={(e) => setVpnTenant(e.target.value)}>
              <option value="">{t("ipam.circuits.noTenant")}</option>
              {(tenantsQ.data ?? []).map((tn) => (
                <option key={tn.id} value={String(tn.id)}>
                  {tn.name}
                </option>
              ))}
            </select>
          </label>
        </div>
      </PrefixDrawer>

      <PrefixDrawer
        title={t("ipam.circuits.addProvider")}
        open={provDrawer}
        onClose={() => {
          if (!createProvM.isPending) setProvDrawer(false);
        }}
        footer={
          <>
            <button type="button" className={dcimStyles.btn} disabled={createProvM.isPending} onClick={() => setProvDrawer(false)}>
              {t("dcim.common.cancel")}
            </button>
            <button
              type="button"
              className={dcimStyles.btn}
              disabled={createProvM.isPending}
              onClick={() => {
                setErr(null);
                createProvM.mutate();
              }}
            >
              {createProvM.isPending ? t("dcim.common.creating") : t("ipam.circuits.createProvider")}
            </button>
          </>
        }
      >
        <div className={prefixStyles.drawerFields}>
          <p className={dcimStyles.muted}>{t("ipam.circuits.providerHint")}</p>
          <label>
            {t("ipam.ipv4.name")}
            <input value={provName} onChange={(e) => setProvName(e.target.value)} required />
          </label>
          <label>
            Slug
            <input value={provSlug} onChange={(e) => setProvSlug(e.target.value)} />
          </label>
        </div>
      </PrefixDrawer>

      <PrefixDrawer
        title={t("ipam.circuits.addGroup")}
        open={grpDrawer}
        onClose={() => {
          if (!createGrpM.isPending) setGrpDrawer(false);
        }}
        footer={
          <>
            <button type="button" className={dcimStyles.btn} disabled={createGrpM.isPending} onClick={() => setGrpDrawer(false)}>
              {t("dcim.common.cancel")}
            </button>
            <button
              type="button"
              className={dcimStyles.btn}
              disabled={createGrpM.isPending}
              onClick={() => {
                setErr(null);
                createGrpM.mutate();
              }}
            >
              {createGrpM.isPending ? t("dcim.common.creating") : t("ipam.circuits.createGroup")}
            </button>
          </>
        }
      >
        <div className={prefixStyles.drawerFields}>
          <p className={dcimStyles.muted}>{t("ipam.circuits.groupHint")}</p>
          <label>
            {t("ipam.ipv4.name")}
            <input value={grpName} onChange={(e) => setGrpName(e.target.value)} required />
          </label>
          <label>
            Slug
            <input value={grpSlug} onChange={(e) => setGrpSlug(e.target.value)} />
          </label>
          <label>
            {t("ipam.circuits.sharedRisk")}
            <input value={grpRisk} onChange={(e) => setGrpRisk(e.target.value)} />
          </label>
        </div>
      </PrefixDrawer>
    </Panel>
  );
}

const FIBER_CABLE_TYPES = new Set(["sm-os2", "mm-om4"]);

function CircuitStrandsPanel({
  circuitId,
  onError,
}: {
  circuitId: number;
  onError: (msg: string | null) => void;
}) {
  const { t } = useI18n();
  const qc = useQueryClient();
  const [strandId, setStrandId] = useState("");
  const strandsQ = useQuery({
    queryKey: ["ipam", "circuit-strands", circuitId],
    queryFn: () => ipamApi.listCircuitStrands(circuitId),
  });
  const cablesQ = useQuery({
    queryKey: ["dcim", "cables", "circuit-bind"],
    queryFn: () => dcimApi.listCables(),
  });
  const fiberCables = (cablesQ.data ?? []).filter((c) => FIBER_CABLE_TYPES.has(c.cable_type));
  const firstFiberId = fiberCables[0]?.id;
  const firstStrandsQ = useQuery({
    queryKey: ["dcim", "cables", firstFiberId, "strands"],
    queryFn: () => dcimApi.listFiberStrands(firstFiberId!),
    enabled: firstFiberId != null,
  });
  const extraCables = fiberCables.slice(1);
  const extraStrandsQ = useQuery({
    queryKey: ["dcim", "cables", "extra-strands", extraCables.map((c) => c.id).join(",")],
    queryFn: async () => {
      const rows = await Promise.all(extraCables.map((c) => dcimApi.listFiberStrands(c.id)));
      return extraCables.flatMap((c, i) => rows[i].map((s) => ({ cable: c, strand: s })));
    },
    enabled: extraCables.length > 0,
  });
  const options = [
    ...(firstFiberId != null
      ? (firstStrandsQ.data ?? []).map((s) => ({
          id: s.id,
          label: `${fiberCables[0].slug} #${s.position}${s.label ? ` ${s.label}` : ""}`,
        }))
      : []),
    ...(extraStrandsQ.data ?? []).map((x) => ({
      id: x.strand.id,
      label: `${x.cable.slug} #${x.strand.position}${x.strand.label ? ` ${x.strand.label}` : ""}`,
    })),
  ];
  const bound = strandsQ.data ?? [];
  const bindM = useMutation({
    mutationFn: () => ipamApi.bindCircuitStrand(circuitId, Number(strandId)),
    onSuccess: () => {
      setStrandId("");
      onError(null);
      void qc.invalidateQueries({ queryKey: ["ipam", "circuit-strands", circuitId] });
    },
    onError: (e: Error) => onError(e instanceof ApiError ? e.message : e.message),
  });
  const unbindM = useMutation({
    mutationFn: (id: number) => ipamApi.unbindCircuitStrand(id),
    onSuccess: () => {
      onError(null);
      void qc.invalidateQueries({ queryKey: ["ipam", "circuit-strands", circuitId] });
    },
    onError: (e: Error) => onError(e instanceof ApiError ? e.message : e.message),
  });

  return (
    <div style={{ marginTop: "var(--space-3)" }}>
      <h3 className={dcimStyles.mfrDetailSectionTitle}>{t("ipam.circuits.strands")}</h3>
      <p className={dcimStyles.muted}>{t("ipam.circuits.strandHint")}</p>
      {bound.length === 0 && !strandsQ.isLoading ? <p className={dcimStyles.muted}>{t("ipam.circuits.emptyStrands")}</p> : null}
      {bound.length > 0 ? (
        <ul className={dcimStyles.ipList}>
          {bound.map((s) => (
            <li key={s.id}>
              {s.cable_slug} #{s.position}
              {s.label ? ` ${s.label}` : ""} ({s.status}){" "}
              <button type="button" className={dcimStyles.btnLink} onClick={() => unbindM.mutate(s.id)}>
                {t("dcim.common.delete")}
              </button>
            </li>
          ))}
        </ul>
      ) : null}
      <form
        className={dcimStyles.formRow}
        onSubmit={(e) => {
          e.preventDefault();
          bindM.mutate();
        }}
      >
        <label>
          {t("ipam.circuits.strands")}
          <select value={strandId} onChange={(e) => setStrandId(e.target.value)} required>
            <option value="">{t("ipam.circuits.chooseStrand")}</option>
            {options.map((o) => (
              <option key={o.id} value={String(o.id)}>
                {o.label}
              </option>
            ))}
          </select>
        </label>
        <button type="submit" className={dcimStyles.btn} disabled={bindM.isPending || strandId === ""}>
          {t("ipam.circuits.bindStrand")}
        </button>
      </form>
    </div>
  );
}

function TunnelTransportsPanel({
  tunnelId,
  onError,
}: {
  tunnelId: number;
  onError: (msg: string | null) => void;
}) {
  const { t } = useI18n();
  const qc = useQueryClient();
  const [circuitId, setCircuitId] = useState("");
  const bindsQ = useQuery({
    queryKey: ["ipam", "tunnel-transports", tunnelId],
    queryFn: () => ipamApi.listTunnelTransports(tunnelId),
  });
  const circuitsQ = useQuery({
    queryKey: ["ipam", "circuits", "all"],
    queryFn: () => ipamApi.listIpamCircuits(),
  });
  const binds = bindsQ.data ?? [];
  const bindM = useMutation({
    mutationFn: () => ipamApi.bindTunnelTransport(tunnelId, Number(circuitId)),
    onSuccess: () => {
      setCircuitId("");
      onError(null);
      void qc.invalidateQueries({ queryKey: ["ipam", "tunnel-transports", tunnelId] });
    },
    onError: (e: Error) => onError(e instanceof ApiError ? e.message : e.message),
  });
  const unbindM = useMutation({
    mutationFn: (id: number) => ipamApi.unbindTunnelTransport(id),
    onSuccess: () => {
      onError(null);
      void qc.invalidateQueries({ queryKey: ["ipam", "tunnel-transports", tunnelId] });
    },
    onError: (e: Error) => onError(e instanceof ApiError ? e.message : e.message),
  });

  return (
    <div style={{ marginTop: "var(--space-3)" }}>
      <h4 className={dcimStyles.mfrDetailSectionTitle}>{t("ipam.circuits.transports")}</h4>
      <p className={dcimStyles.muted}>{t("ipam.circuits.transportHint")}</p>
      {binds.length === 0 && !bindsQ.isLoading ? <p className={dcimStyles.muted}>{t("ipam.circuits.emptyTransports")}</p> : null}
      {binds.length > 0 ? (
        <ul className={dcimStyles.ipList}>
          {binds.map((b) => (
            <li key={b.id}>
              {b.circuit_number} {b.circuit_name}{" "}
              <button type="button" className={dcimStyles.btnLink} onClick={() => unbindM.mutate(b.id)}>
                {t("dcim.common.delete")}
              </button>
            </li>
          ))}
        </ul>
      ) : null}
      <form
        className={dcimStyles.formRow}
        onSubmit={(e) => {
          e.preventDefault();
          bindM.mutate();
        }}
      >
        <label>
          {t("ipam.circuits.transports")}
          <select value={circuitId} onChange={(e) => setCircuitId(e.target.value)} required>
            <option value="">{t("ipam.circuits.chooseCircuit")}</option>
            {(circuitsQ.data ?? []).map((c) => (
              <option key={c.id} value={String(c.id)}>
                {c.circuit_number} {c.name}
              </option>
            ))}
          </select>
        </label>
        <button type="submit" className={dcimStyles.btn} disabled={bindM.isPending || circuitId === ""}>
          {t("ipam.circuits.bindTransport")}
        </button>
      </form>
    </div>
  );
}

const VPN_MEMBER_ROLES = ["hub", "spoke", "peer", "client", "other"] as const;

function VpnMembersPanel({ vpnId, onError }: { vpnId: number; onError: (msg: string | null) => void }) {
  const { t } = useI18n();
  const qc = useQueryClient();
  const [siteId, setSiteId] = useState("");
  const [role, setRole] = useState("");
  const membersQ = useQuery({
    queryKey: ["ipam", "vpn-members", vpnId],
    queryFn: () => ipamApi.listVpnMembers(vpnId),
  });
  const sitesQ = useQuery({ queryKey: ["dcim", "sites"], queryFn: dcimApi.listSites });
  const members = membersQ.data ?? [];
  const addM = useMutation({
    mutationFn: () => ipamApi.createVpnMember(vpnId, { site_id: Number(siteId), role: role || null }),
    onSuccess: () => {
      setSiteId("");
      setRole("");
      onError(null);
      void qc.invalidateQueries({ queryKey: ["ipam", "vpn-members", vpnId] });
    },
    onError: (e: Error) => onError(e instanceof ApiError ? e.message : e.message),
  });
  const delM = useMutation({
    mutationFn: (id: number) => ipamApi.deleteVpnMember(id),
    onSuccess: () => {
      onError(null);
      void qc.invalidateQueries({ queryKey: ["ipam", "vpn-members", vpnId] });
    },
    onError: (e: Error) => onError(e instanceof ApiError ? e.message : e.message),
  });

  return (
    <div style={{ marginBottom: "var(--space-3)" }}>
      <h3 className={dcimStyles.mfrDetailSectionTitle}>{t("ipam.circuits.membersVpn")}</h3>
      <p className={dcimStyles.muted}>{t("ipam.circuits.memberHint")}</p>
      {members.length === 0 && !membersQ.isLoading ? <p className={dcimStyles.muted}>{t("ipam.circuits.emptyMembers")}</p> : null}
      {members.length > 0 ? (
        <ul className={dcimStyles.ipList}>
          {members.map((m) => (
            <li key={m.id}>
              {m.site_name}
              {m.role ? ` (${m.role})` : ""}{" "}
              <button type="button" className={dcimStyles.btnLink} onClick={() => delM.mutate(m.id)}>
                {t("dcim.common.delete")}
              </button>
            </li>
          ))}
        </ul>
      ) : null}
      <form
        className={dcimStyles.formRow}
        onSubmit={(e) => {
          e.preventDefault();
          addM.mutate();
        }}
      >
        <label>
          {t("ipam.circuits.termSite")}
          <select value={siteId} onChange={(e) => setSiteId(e.target.value)} required>
            <option value="">{t("ipam.circuits.noSite")}</option>
            {(sitesQ.data ?? []).map((s) => (
              <option key={s.id} value={String(s.id)}>
                {s.name}
              </option>
            ))}
          </select>
        </label>
        <label>
          {t("ipam.circuits.memberRole")}
          <select value={role} onChange={(e) => setRole(e.target.value)}>
            <option value="">{t("ipam.circuits.noGroup")}</option>
            {VPN_MEMBER_ROLES.map((r) => (
              <option key={r} value={r}>
                {r}
              </option>
            ))}
          </select>
        </label>
        <button type="submit" className={dcimStyles.btn} disabled={addM.isPending || siteId === ""}>
          {t("ipam.circuits.addMemberSite")}
        </button>
      </form>
    </div>
  );
}
