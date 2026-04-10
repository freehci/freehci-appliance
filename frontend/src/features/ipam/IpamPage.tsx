import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useMemo, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { Panel } from "@/components/ui/Panel";
import { useI18n } from "@/i18n/I18nProvider";
import { ApiError } from "@/lib/api";
import * as dcimApi from "@/features/dcim/dcimApi";
import dcimStyles from "@/features/dcim/dcim.module.css";
import { interfaceDepthByInterfaceList, interfaceIndentedName } from "@/features/dcim/interfaceTreeLabels";
import type { Ipv4Prefix, PrefixAddressGridRow } from "./types";
import * as ipamApi from "./ipamApi";

type ExploreCrumb = { id: number; name: string; cidr: string };

const GRID_PAGE_SIZE_OPTIONS = [25, 50, 100, 0] as const;

function isGridRowFree(row: PrefixAddressGridRow): boolean {
  if (row.assignment != null) return false;
  const inv = row.inventory;
  if (inv == null) return true;
  return inv.status === "discovered";
}

function formatInventoryTimestamp(iso: string | null | undefined): string {
  if (iso == null || iso === "") return "";
  const d = new Date(iso);
  return Number.isNaN(d.getTime()) ? iso : d.toLocaleString();
}

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
  const [showScanHistory, setShowScanHistory] = useState(false);
  const [linkFor, setLinkFor] = useState<string | null>(null);
  const [linkDeviceId, setLinkDeviceId] = useState("");
  const [linkInterfaceId, setLinkInterfaceId] = useState("");
  const [reqMode, setReqMode] = useState<"reserve" | "assign">("reserve");
  const [reqOwnerUserId, setReqOwnerUserId] = useState("");
  const [reqOwnerNewUsername, setReqOwnerNewUsername] = useState("");
  const [reqOwnerNewDisplay, setReqOwnerNewDisplay] = useState("");
  const [reqNote, setReqNote] = useState("");
  const [reqDeviceId, setReqDeviceId] = useState("");
  const [reqInterfaceId, setReqInterfaceId] = useState("");
  const [addrFilterText, setAddrFilterText] = useState("");
  const [addrFilterStatus, setAddrFilterStatus] = useState("");
  const [addrFilterFreeOnly, setAddrFilterFreeOnly] = useState(false);
  const [addrFilterOwnerUserId, setAddrFilterOwnerUserId] = useState("");
  const [gridFilterOpen, setGridFilterOpen] = useState(false);
  const gridFilterRef = useRef<HTMLDivElement | null>(null);
  const [gridPage, setGridPage] = useState(0);
  const [gridPageSize, setGridPageSize] = useState<number>(50);
  const [prefixListPage, setPrefixListPage] = useState(0);
  const [prefixListPageSize, setPrefixListPageSize] = useState<number>(25);

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

  const scansQ = useQuery({
    queryKey: ["ipam", "subnet-scans", exploreId],
    queryFn: () => ipamApi.listSubnetScans({ ipv4_prefix_id: exploreId!, limit: 25 }),
    enabled: exploreId != null && exploreId > 0,
  });

  const gridQ = useQuery({
    queryKey: ["ipam", "address-grid", exploreId],
    queryFn: () => ipamApi.getPrefixAddressGrid(exploreId!),
    enabled: exploreId != null && exploreId > 0,
    refetchInterval: (query) => {
      const st = query.state.data?.active_scan?.status;
      return st === "pending" || st === "running" ? 1500 : false;
    },
  });

  useEffect(() => {
    setShowScanHistory(false);
    setLinkFor(null);
    setLinkDeviceId("");
    setLinkInterfaceId("");
    setReqOwnerUserId("");
    setReqOwnerNewUsername("");
    setReqOwnerNewDisplay("");
    setReqNote("");
    setReqDeviceId("");
    setReqInterfaceId("");
    setReqMode("reserve");
    setAddrFilterFreeOnly(false);
    setAddrFilterOwnerUserId("");
    setGridFilterOpen(false);
    setGridPage(0);
  }, [exploreId]);

  useEffect(() => {
    setPrefixListPage(0);
  }, [siteIdFilter]);

  useEffect(() => {
    setPrefixListPage(0);
  }, [prefixListPageSize]);

  useEffect(() => {
    setGridPage(0);
  }, [addrFilterText, addrFilterStatus, addrFilterFreeOnly, addrFilterOwnerUserId]);

  useEffect(() => {
    setGridPage(0);
  }, [gridPageSize]);

  useEffect(() => {
    if (!gridFilterOpen) return;
    const onDown = (e: MouseEvent) => {
      const el = gridFilterRef.current;
      if (el && e.target instanceof Node && !el.contains(e.target)) setGridFilterOpen(false);
    };
    document.addEventListener("mousedown", onDown);
    return () => document.removeEventListener("mousedown", onDown);
  }, [gridFilterOpen]);

  useEffect(() => {
    const st = gridQ.data?.active_scan?.status;
    if (st === "completed" || st === "failed") {
      void qc.invalidateQueries({ queryKey: ["ipam", "subnet-scans", exploreId] });
    }
  }, [gridQ.data?.active_scan?.status, qc, exploreId]);

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

  const startScan = useMutation({
    mutationFn: (prefixId: number) => ipamApi.createSubnetScan(prefixId),
    onSuccess: () => {
      setErr(null);
      void qc.invalidateQueries({ queryKey: ["ipam", "subnet-scans", exploreId] });
      void qc.invalidateQueries({ queryKey: ["ipam", "address-grid", exploreId] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const scanStatusLabel = (status: string) => {
    const key =
      status === "pending"
        ? "ipam.scan.status.pending"
        : status === "running"
          ? "ipam.scan.status.running"
          : status === "completed"
            ? "ipam.scan.status.completed"
            : status === "failed"
              ? "ipam.scan.status.failed"
              : null;
    return key ? t(key) : status;
  };

  const usersQ = useQuery({ queryKey: ["ipam", "users"], queryFn: () => ipamApi.listUsers(500) });

  const devicesQ = useQuery({ queryKey: ["dcim", "devices"], queryFn: dcimApi.listDevices });
  const deviceNameById = useMemo(() => {
    const m = new Map<number, string>();
    for (const d of devicesQ.data ?? []) m.set(d.id, d.name);
    return m;
  }, [devicesQ.data]);

  const userLabelById = useMemo(() => {
    const m = new Map<number, string>();
    for (const u of usersQ.data ?? []) m.set(u.id, u.display_name ?? u.username);
    return m;
  }, [usersQ.data]);

  const filteredGridRows = useMemo(() => {
    const rows = gridQ.data?.rows ?? [];
    const q = addrFilterText.trim().toLowerCase();
    const ownerF = addrFilterOwnerUserId === "" ? null : Number(addrFilterOwnerUserId);
    return rows.filter((row) => {
      const inv = row.inventory;
      const st = inv?.status ?? "";
      if (addrFilterStatus !== "" && st !== addrFilterStatus) return false;
      if (addrFilterFreeOnly && !isGridRowFree(row)) return false;
      if (ownerF != null && !Number.isNaN(ownerF)) {
        if (inv?.owner_user_id !== ownerF) return false;
      }
      if (q === "") return true;
      const devName =
        row.assignment != null
          ? row.assignment.device_name.toLowerCase()
          : inv?.device_id != null
            ? (deviceNameById.get(inv.device_id) ?? "").toLowerCase()
            : "";
      const ifStr =
        row.assignment != null
          ? `${row.assignment.interface_id} ${row.assignment.interface_name}`.toLowerCase()
          : `${inv?.interface_id ?? ""} ${inv?.interface_name ?? ""}`.toLowerCase();
      const note = (inv?.note ?? "").toLowerCase();
      const ownerStr =
        inv?.owner_user_id != null
          ? `${inv.owner_user_id} ${userLabelById.get(inv.owner_user_id) ?? ""}`.toLowerCase()
          : "";
      const mac = `${row.scan_mac ?? ""} ${inv?.mac_address ?? ""}`.toLowerCase();
      return (
        row.address.toLowerCase().includes(q) ||
        st.toLowerCase().includes(q) ||
        note.includes(q) ||
        devName.includes(q) ||
        ifStr.includes(q) ||
        ownerStr.includes(q) ||
        mac.includes(q)
      );
    });
  }, [
    gridQ.data?.rows,
    addrFilterText,
    addrFilterStatus,
    addrFilterFreeOnly,
    addrFilterOwnerUserId,
    deviceNameById,
    userLabelById,
  ]);

  useEffect(() => {
    const total = filteredGridRows.length;
    const size = gridPageSize === 0 ? Math.max(total, 1) : gridPageSize;
    const pageCount = Math.max(1, Math.ceil(total / size));
    setGridPage((p) => Math.min(Math.max(0, p), pageCount - 1));
  }, [filteredGridRows.length, gridPageSize]);

  const gridFilterActiveCount = useMemo(() => {
    let n = 0;
    if (addrFilterStatus !== "") n += 1;
    if (addrFilterFreeOnly) n += 1;
    if (addrFilterOwnerUserId !== "") n += 1;
    return n;
  }, [addrFilterStatus, addrFilterFreeOnly, addrFilterOwnerUserId]);

  const gridPageSlice = useMemo(() => {
    const total = filteredGridRows.length;
    const size = gridPageSize === 0 ? Math.max(total, 1) : gridPageSize;
    const pageCount = Math.max(1, Math.ceil(total / size));
    const safePage = Math.min(Math.max(0, gridPage), pageCount - 1);
    const start = safePage * size;
    const end = gridPageSize === 0 ? total : Math.min(start + size, total);
    return {
      rows: filteredGridRows.slice(start, end),
      total,
      size,
      pageCount,
      safePage,
      rangeStart: total === 0 ? 0 : start + 1,
      rangeEnd: end,
    };
  }, [filteredGridRows, gridPage, gridPageSize]);

  const prefixListSlice = useMemo(() => {
    const all = prefixesQ.data ?? [];
    const total = all.length;
    const size = prefixListPageSize === 0 ? Math.max(total, 1) : prefixListPageSize;
    const pageCount = Math.max(1, Math.ceil(total / size));
    const safePage = Math.min(Math.max(0, prefixListPage), pageCount - 1);
    const start = safePage * size;
    const end = prefixListPageSize === 0 ? total : Math.min(start + size, total);
    return {
      rows: all.slice(start, end),
      total,
      size,
      pageCount,
      safePage,
      rangeStart: total === 0 ? 0 : start + 1,
      rangeEnd: end,
    };
  }, [prefixesQ.data, prefixListPage, prefixListPageSize]);

  useEffect(() => {
    const total = prefixesQ.data?.length ?? 0;
    const size = prefixListPageSize === 0 ? Math.max(total, 1) : prefixListPageSize;
    const pageCount = Math.max(1, Math.ceil(total / size));
    setPrefixListPage((p) => Math.min(Math.max(0, p), pageCount - 1));
  }, [prefixesQ.data?.length, prefixListPageSize]);

  const deviceIdNum = reqDeviceId === "" ? null : Number(reqDeviceId);
  const interfacesQ = useQuery({
    queryKey: ["dcim", "devices", deviceIdNum, "interfaces"],
    queryFn: () => dcimApi.listDeviceInterfaces(deviceIdNum!),
    enabled: deviceIdNum != null && deviceIdNum > 0,
  });

  const reqIfaceDepthById = useMemo(
    () => interfaceDepthByInterfaceList(interfacesQ.data ?? []),
    [interfacesQ.data],
  );

  useEffect(() => {
    setReqInterfaceId("");
  }, [reqDeviceId]);

  const linkDeviceNum = linkDeviceId === "" ? null : Number(linkDeviceId);
  const interfacesLinkQ = useQuery({
    queryKey: ["dcim", "devices", linkDeviceNum, "interfaces", "ipam-link"],
    queryFn: () => dcimApi.listDeviceInterfaces(linkDeviceNum!),
    enabled: linkFor != null && linkDeviceNum != null && linkDeviceNum > 0,
  });

  const linkIfaceDepthById = useMemo(
    () => interfaceDepthByInterfaceList(interfacesLinkQ.data ?? []),
    [interfacesLinkQ.data],
  );

  useEffect(() => {
    setLinkInterfaceId("");
  }, [linkDeviceId]);

  const createOwner = useMutation({
    mutationFn: () =>
      ipamApi.createUser({
        username: reqOwnerNewUsername.trim(),
        display_name: reqOwnerNewDisplay.trim() !== "" ? reqOwnerNewDisplay.trim() : null,
      }),
    onSuccess: (u) => {
      setReqOwnerUserId(String(u.id));
      setReqOwnerNewUsername("");
      setReqOwnerNewDisplay("");
      setErr(null);
      void qc.invalidateQueries({ queryKey: ["ipam", "users"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const requestAddr = useMutation({
    mutationFn: () =>
      ipamApi.requestIpv4Address({
        ipv4_prefix_id: exploreId!,
        mode: reqMode,
        interface_id: reqMode === "assign" && reqInterfaceId.trim() !== "" ? Number(reqInterfaceId) : null,
        device_id: reqMode === "assign" && reqDeviceId.trim() !== "" ? Number(reqDeviceId) : null,
        owner_user_id: reqOwnerUserId.trim() !== "" ? Number(reqOwnerUserId) : null,
        note: reqNote.trim() !== "" ? reqNote.trim() : null,
      }),
    onSuccess: () => {
      setErr(null);
      setReqNote("");
      void qc.invalidateQueries({ queryKey: ["ipam", "explore", exploreId] });
      void qc.invalidateQueries({ queryKey: ["ipam", "address-grid", exploreId] });
      void qc.invalidateQueries({ queryKey: ["dcim", "devices"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const patchAddr = useMutation({
    mutationFn: (args: { id: number; body: { owner_user_id?: number | null; note?: string | null; status?: string } }) =>
      ipamApi.patchIpv4Address(args.id, args.body),
    onSuccess: () => {
      setErr(null);
      void qc.invalidateQueries({ queryKey: ["ipam", "explore", exploreId] });
      void qc.invalidateQueries({ queryKey: ["ipam", "address-grid", exploreId] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const linkAssign = useMutation({
    mutationFn: async (args: { address: string; deviceId: number; interfaceId: number }) => {
      await dcimApi.createIfaceIpAssignment(args.deviceId, args.interfaceId, {
        address: args.address,
        ipv4_prefix_id: exploreId!,
      });
    },
    onSuccess: () => {
      setLinkFor(null);
      setErr(null);
      void qc.invalidateQueries({ queryKey: ["ipam", "explore", exploreId] });
      void qc.invalidateQueries({ queryKey: ["ipam", "address-grid", exploreId] });
      void qc.invalidateQueries({ queryKey: ["dcim", "devices"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const releaseGridRow = useMutation({
    mutationFn: async (row: PrefixAddressGridRow) => {
      const inv = row.inventory;
      if (inv != null && inv.interface_ip_assignment_id != null) {
        await ipamApi.releaseIpv4Address(inv.id);
        return;
      }
      const asn = row.assignment;
      if (asn != null) {
        await dcimApi.deleteIfaceIpAssignment(asn.device_id, asn.interface_id, asn.assignment_id);
        return;
      }
      if (inv != null && (inv.status === "reserved" || inv.status === "assigned")) {
        await ipamApi.releaseIpv4Address(inv.id);
        return;
      }
      throw new Error("release");
    },
    onSuccess: () => {
      setErr(null);
      void qc.invalidateQueries({ queryKey: ["ipam", "explore", exploreId] });
      void qc.invalidateQueries({ queryKey: ["ipam", "address-grid", exploreId] });
      void qc.invalidateQueries({ queryKey: ["dcim", "devices"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const canReleaseGridRow = (row: PrefixAddressGridRow): boolean => {
    const inv = row.inventory;
    if (inv?.interface_ip_assignment_id != null) return true;
    if (row.assignment != null) return true;
    if (inv != null && (inv.status === "reserved" || inv.status === "assigned")) return true;
    return false;
  };

  const scanRunning =
    gridQ.data?.active_scan?.status === "pending" || gridQ.data?.active_scan?.status === "running";
  const activeSc = gridQ.data?.active_scan;

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

              <h4 className={dcimStyles.mfrDetailSectionTitle}>{t("ipam.addr.title")}</h4>
              <p className={dcimStyles.muted} style={{ marginTop: 0 }}>
                {t("ipam.grid.hint")}
              </p>

              <h5 className={dcimStyles.mfrDetailSectionTitle} style={{ marginTop: "var(--space-3)" }}>
                {t("ipam.scan.title")}
              </h5>
              <p className={dcimStyles.muted} style={{ marginTop: 0 }}>
                {t("ipam.scan.intro")}
              </p>
              <div style={{ marginBottom: "var(--space-2)" }}>
                <button
                  type="button"
                  className={dcimStyles.btn}
                  disabled={startScan.isPending}
                  onClick={() => startScan.mutate(exploreQ.data.prefix.id)}
                >
                  {startScan.isPending ? t("ipam.scan.running") : t("ipam.scan.start")}
                </button>
              </div>
              {activeSc != null ? (
                <p className={dcimStyles.muted} style={{ marginTop: 0 }}>
                  {scanStatusLabel(activeSc.status)} · {activeSc.hosts_responding} / {activeSc.hosts_scanned}
                  {activeSc.status === "failed" && activeSc.error_message ? (
                    <>
                      {" "}
                      · <span className={dcimStyles.err}>{activeSc.error_message}</span>
                    </>
                  ) : null}
                </p>
              ) : null}

              <label className={dcimStyles.muted} style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "var(--space-2)" }}>
                <input
                  type="checkbox"
                  checked={showScanHistory}
                  onChange={(e) => setShowScanHistory(e.target.checked)}
                />
                {t("ipam.scan.showHistory")}
              </label>

              {showScanHistory ? (
                <>
                  <h5 className={dcimStyles.mfrDetailSectionTitle} style={{ marginTop: "var(--space-2)" }}>
                    {t("ipam.scan.history")}
                  </h5>
                  {scansQ.isLoading ? <p className={dcimStyles.muted}>{t("dcim.common.loading")}</p> : null}
                  {scansQ.data && scansQ.data.length > 0 ? (
                    <table className={dcimStyles.table}>
                      <thead>
                        <tr>
                          <th>{t("ipam.scan.colId")}</th>
                          <th>{t("ipam.scan.colStatus")}</th>
                          <th>{t("ipam.scan.colHosts")}</th>
                          <th>{t("ipam.scan.colStarted")}</th>
                        </tr>
                      </thead>
                      <tbody>
                        {scansQ.data.map((s) => (
                          <tr key={s.id}>
                            <td>{s.id}</td>
                            <td>{scanStatusLabel(s.status)}</td>
                            <td>
                              {s.hosts_responding} / {s.hosts_scanned}
                            </td>
                            <td className={dcimStyles.muted}>{new Date(s.started_at).toLocaleString()}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  ) : scansQ.data && scansQ.data.length === 0 ? (
                    <p className={dcimStyles.muted}>{t("ipam.scan.noScans")}</p>
                  ) : null}
                </>
              ) : null}

              {linkFor != null ? (
                <div
                  style={{
                    border: "1px solid var(--shell-border)",
                    borderRadius: "var(--radius-md)",
                    padding: "var(--space-2)",
                    marginBottom: "var(--space-2)",
                  }}
                >
                  <p style={{ marginTop: 0 }}>
                    <strong>{t("ipam.grid.linkTitle")}</strong> <code>{linkFor}</code>
                  </p>
                  <div className={dcimStyles.formRow}>
                    <label>
                      {t("ipam.addr.device")}
                      <select value={linkDeviceId} onChange={(e) => setLinkDeviceId(e.target.value)}>
                        <option value="">{t("dcim.common.choose")}</option>
                        {(devicesQ.data ?? []).map((d) => (
                          <option key={d.id} value={String(d.id)}>
                            #{d.id} · {d.name}
                          </option>
                        ))}
                      </select>
                    </label>
                    <label>
                      {t("ipam.addr.interfaceId")}
                      <select value={linkInterfaceId} onChange={(e) => setLinkInterfaceId(e.target.value)}>
                        <option value="">{t("dcim.common.choose")}</option>
                        {(interfacesLinkQ.data ?? []).map((x) => (
                          <option key={x.id} value={String(x.id)}>
                            #{x.id} · {interfaceIndentedName(x, linkIfaceDepthById)}
                          </option>
                        ))}
                      </select>
                    </label>
                    <button
                      type="button"
                      className={dcimStyles.btn}
                      disabled={
                        linkAssign.isPending || linkDeviceId === "" || linkInterfaceId === "" || exploreId == null
                      }
                      onClick={() => {
                        const did = Number(linkDeviceId);
                        const iid = Number(linkInterfaceId);
                        if (!did || !iid) return;
                        linkAssign.mutate({ address: linkFor, deviceId: did, interfaceId: iid });
                      }}
                    >
                      {linkAssign.isPending ? "…" : t("ipam.grid.linkSubmit")}
                    </button>
                    <button type="button" className={dcimStyles.btn} onClick={() => setLinkFor(null)}>
                      {t("ipam.ipv4.cancel")}
                    </button>
                  </div>
                </div>
              ) : null}

              <div
                className={dcimStyles.formRow}
                style={{ marginTop: "var(--space-2)", alignItems: "flex-end", flexWrap: "wrap" }}
              >
                <label style={{ flex: "1 1 14rem", minWidth: "10rem" }}>
                  {t("ipam.addr.filterText")}
                  <input
                    value={addrFilterText}
                    onChange={(e) => setAddrFilterText(e.target.value)}
                    placeholder={t("ipam.addr.filterTextPlaceholder")}
                  />
                </label>
                <div ref={gridFilterRef} style={{ position: "relative" }}>
                  <button
                    type="button"
                    className={dcimStyles.btn}
                    aria-expanded={gridFilterOpen}
                    aria-label={
                      gridFilterActiveCount > 0
                        ? `${t("ipam.grid.filter.aria")} (${gridFilterActiveCount})`
                        : t("ipam.grid.filter.aria")
                    }
                    onClick={() => setGridFilterOpen((o) => !o)}
                    style={{ display: "inline-flex", alignItems: "center", gap: "0.35rem" }}
                  >
                    <i className="fas fa-filter" aria-hidden />
                    {gridFilterActiveCount > 0 ? (
                      <span
                        style={{
                          fontSize: "var(--text-xs)",
                          fontWeight: 600,
                          minWidth: "1.1rem",
                          textAlign: "center",
                        }}
                        aria-hidden
                      >
                        {gridFilterActiveCount}
                      </span>
                    ) : null}
                  </button>
                  {gridFilterOpen ? (
                    <div
                      role="dialog"
                      aria-label={t("ipam.grid.filter.title")}
                      style={{
                        position: "absolute",
                        right: 0,
                        top: "100%",
                        marginTop: 6,
                        zIndex: 30,
                        minWidth: "min(100vw - 2rem, 20rem)",
                        padding: "var(--space-2)",
                        background: "var(--color-bg-elevated)",
                        border: "1px solid var(--shell-border)",
                        borderRadius: "var(--radius-md)",
                        boxShadow: "0 4px 16px rgba(0,0,0,0.12)",
                      }}
                    >
                      <p style={{ marginTop: 0, marginBottom: "var(--space-2)", fontWeight: 600 }}>
                        {t("ipam.grid.filter.title")}
                      </p>
                      <label style={{ display: "block", marginBottom: "var(--space-2)" }}>
                        {t("ipam.addr.filterStatus")}
                        <select
                          value={addrFilterStatus}
                          onChange={(e) => setAddrFilterStatus(e.target.value)}
                          style={{ width: "100%", marginTop: 4 }}
                        >
                          <option value="">{t("ipam.addr.filterStatusAll")}</option>
                          <option value="discovered">discovered</option>
                          <option value="reserved">reserved</option>
                          <option value="assigned">assigned</option>
                        </select>
                      </label>
                      <label
                        style={{
                          display: "flex",
                          alignItems: "center",
                          gap: "0.5rem",
                          marginBottom: "var(--space-2)",
                          cursor: "pointer",
                        }}
                      >
                        <input
                          type="checkbox"
                          checked={addrFilterFreeOnly}
                          onChange={(e) => setAddrFilterFreeOnly(e.target.checked)}
                        />
                        {t("ipam.grid.filter.freeOnly")}
                      </label>
                      <label style={{ display: "block", marginBottom: "var(--space-2)" }}>
                        {t("ipam.grid.filter.owner")}
                        <select
                          value={addrFilterOwnerUserId}
                          onChange={(e) => setAddrFilterOwnerUserId(e.target.value)}
                          style={{ width: "100%", marginTop: 4 }}
                        >
                          <option value="">{t("ipam.grid.filter.ownerAll")}</option>
                          {(usersQ.data ?? []).map((u) => (
                            <option key={u.id} value={String(u.id)}>
                              #{u.id} · {u.display_name ?? u.username}
                            </option>
                          ))}
                        </select>
                      </label>
                      <button
                        type="button"
                        className={dcimStyles.btn}
                        style={{ width: "100%" }}
                        onClick={() => {
                          setAddrFilterStatus("");
                          setAddrFilterFreeOnly(false);
                          setAddrFilterOwnerUserId("");
                        }}
                      >
                        {t("ipam.grid.filter.reset")}
                      </button>
                    </div>
                  ) : null}
                </div>
              </div>

              {gridQ.isLoading ? <p className={dcimStyles.muted}>{t("dcim.common.loading")}</p> : null}
              {gridQ.isError ? <p className={dcimStyles.err}>{(gridQ.error as Error).message}</p> : null}
              {filteredGridRows.length > 0 ? (
                <>
                  <div
                    className={dcimStyles.muted}
                    style={{
                      display: "flex",
                      flexWrap: "wrap",
                      alignItems: "center",
                      gap: "0.75rem",
                      marginTop: "var(--space-2)",
                      marginBottom: "var(--space-1)",
                    }}
                  >
                    <span>
                      {t("ipam.grid.pagination.showing")}{" "}
                      <strong>
                        {gridPageSlice.rangeStart}–{gridPageSlice.rangeEnd}
                      </strong>{" "}
                      {t("ipam.grid.pagination.of")}{" "}
                      <strong>{gridPageSlice.total}</strong>
                    </span>
                    <label style={{ display: "inline-flex", alignItems: "center", gap: "0.35rem" }}>
                      {t("ipam.grid.pagination.perPage")}
                      <select
                        value={String(gridPageSize)}
                        onChange={(e) => setGridPageSize(Number(e.target.value))}
                      >
                        {GRID_PAGE_SIZE_OPTIONS.map((n) => (
                          <option key={n} value={String(n)}>
                            {n === 0 ? t("ipam.grid.pagination.all") : n}
                          </option>
                        ))}
                      </select>
                    </label>
                    <span style={{ display: "inline-flex", gap: "0.35rem" }}>
                      <button
                        type="button"
                        className={dcimStyles.btn}
                        disabled={gridPageSlice.safePage <= 0}
                        onClick={() => setGridPage((p) => Math.max(0, p - 1))}
                      >
                        {t("ipam.grid.pagination.prev")}
                      </button>
                      <button
                        type="button"
                        className={dcimStyles.btn}
                        disabled={gridPageSlice.safePage >= gridPageSlice.pageCount - 1}
                        onClick={() =>
                          setGridPage((p) => Math.min(p + 1, gridPageSlice.pageCount - 1))
                        }
                      >
                        {t("ipam.grid.pagination.next")}
                      </button>
                    </span>
                  </div>
                  <div style={{ maxHeight: "70vh", overflow: "auto" }}>
                    <table className={dcimStyles.table}>
                    <thead>
                      <tr>
                        <th>{t("ipam.ipv4.colAddress")}</th>
                        <th title={t("ipam.grid.reachColHint")}>{t("ipam.grid.reachCol")}</th>
                        <th title={t("ipam.grid.lastSeenColHint")}>{t("ipam.grid.lastSeenCol")}</th>
                        <th>{t("ipam.scan.colMac")}</th>
                        <th>{t("ipam.ipv4.colDevice")}</th>
                        <th>{t("ipam.ipv4.colInterface")}</th>
                        <th>{t("ipam.addr.colStatus")}</th>
                        <th>{t("ipam.addr.colOwner")}</th>
                        <th>{t("ipam.addr.colNote")}</th>
                        <th>{t("ipam.addr.colActions")}</th>
                      </tr>
                    </thead>
                    <tbody>
                      {gridPageSlice.rows.map((row) => {
                        const inv = row.inventory;
                        const ping = row.scan_ping_responded;
                        const lastSeenRaw = inv?.last_seen_at ?? null;
                        const lastSeenLabel = formatInventoryTimestamp(lastSeenRaw);
                        const reach =
                          scanRunning && ping === null ? (
                            <span title={t("ipam.grid.reach.scanning")}>
                              <i
                                className="fas fa-spinner fa-spin"
                                style={{ color: "#ca8a04" }}
                                aria-hidden
                              />
                            </span>
                          ) : ping === true ? (
                            <span title={t("ipam.grid.reach.alive")}>
                              <i
                                className="fas fa-circle"
                                style={{ color: "#22c55e", fontSize: "0.65rem" }}
                                aria-hidden
                              />
                            </span>
                          ) : ping === false ? (
                            lastSeenRaw ? (
                              <span
                                title={`${t("ipam.grid.reach.staleHint")}${lastSeenLabel ? ` ${lastSeenLabel}` : ""}`}
                              >
                                <i
                                  className="fas fa-skull"
                                  style={{
                                    color: "var(--color-text-muted, #8fa8d4)",
                                    fontSize: "0.85rem",
                                  }}
                                  aria-hidden
                                />
                              </span>
                            ) : (
                              <span title={t("ipam.grid.reach.dead")}>
                                <i
                                  className="fas fa-circle"
                                  style={{ color: "var(--shell-muted-fg, #737373)", fontSize: "0.65rem" }}
                                  aria-hidden
                                />
                              </span>
                            )
                          ) : lastSeenRaw ? (
                            <span
                              title={`${t("ipam.grid.reach.noScanHint")}${lastSeenLabel ? ` ${lastSeenLabel}` : ""}`}
                            >
                              <i
                                className="fas fa-clock"
                                style={{
                                  color: "var(--color-text-muted, #8fa8d4)",
                                  fontSize: "0.85rem",
                                }}
                                aria-hidden
                              />
                            </span>
                          ) : (
                            <span className={dcimStyles.muted}>—</span>
                          );
                        const mac = row.scan_mac ?? inv?.mac_address ?? "—";
                        const devId = row.assignment?.device_id ?? inv?.device_id ?? null;
                        const devName =
                          row.assignment?.device_name ??
                          (devId != null ? (deviceNameById.get(devId) ?? `#${devId}`) : null);
                        const ifLabel =
                          row.assignment != null
                            ? row.assignment.interface_name
                            : inv?.interface_id != null
                              ? `${inv.interface_name ?? ""}${inv.interface_name ? " · " : ""}#${inv.interface_id}`
                              : null;
                        return (
                          <tr key={row.address}>
                            <td>
                              {devId != null ? (
                                <Link
                                  to={`/dcim/equipment/devices/${devId}?tab=network&snmpHost=${encodeURIComponent(row.address)}`}
                                  className={dcimStyles.tableLink}
                                  title={t("ipam.grid.addressOpenDeviceSnmp")}
                                >
                                  <code>{row.address}</code>
                                </Link>
                              ) : (
                                <Link
                                  to={`/snmp?host=${encodeURIComponent(row.address)}`}
                                  className={dcimStyles.tableLink}
                                  title={t("ipam.grid.addressOpenSnmpDiscovery")}
                                >
                                  <code>{row.address}</code>
                                </Link>
                              )}
                            </td>
                            <td>{reach}</td>
                            <td className={dcimStyles.muted} title={lastSeenLabel || undefined}>
                              {lastSeenLabel || "—"}
                            </td>
                            <td>{mac}</td>
                            <td>
                              {devId != null ? (
                                <Link
                                  to={`/dcim/equipment/devices/${row.assignment?.device_id ?? devId}?tab=network`}
                                  className={dcimStyles.tableLink}
                                >
                                  {devName ?? `#${devId}`}
                                </Link>
                              ) : (
                                <span className={dcimStyles.muted}>—</span>
                              )}
                            </td>
                            <td className={dcimStyles.muted}>{ifLabel ?? "—"}</td>
                            <td>
                              {inv != null ? (
                                <select
                                  value={inv.status}
                                  onChange={(e) =>
                                    patchAddr.mutate({ id: inv.id, body: { status: e.target.value } })
                                  }
                                >
                                  <option value="discovered">discovered</option>
                                  <option value="reserved">reserved</option>
                                  <option value="assigned">assigned</option>
                                </select>
                              ) : (
                                <span className={dcimStyles.muted}>—</span>
                              )}
                            </td>
                            <td>
                              {inv != null ? (
                                <select
                                  value={inv.owner_user_id ?? ""}
                                  onChange={(e) =>
                                    patchAddr.mutate({
                                      id: inv.id,
                                      body: { owner_user_id: e.target.value === "" ? null : Number(e.target.value) },
                                    })
                                  }
                                >
                                  <option value="">{t("dcim.common.choose")}</option>
                                  {(usersQ.data ?? []).map((u) => (
                                    <option key={u.id} value={String(u.id)}>
                                      #{u.id} · {u.display_name ?? u.username}
                                    </option>
                                  ))}
                                </select>
                              ) : (
                                <span className={dcimStyles.muted}>—</span>
                              )}
                            </td>
                            <td>
                              {inv != null ? (
                                <input
                                  defaultValue={inv.note ?? ""}
                                  key={`${inv.id}-${inv.updated_at}`}
                                  onBlur={(e) => {
                                    const v = e.target.value.trim();
                                    if ((inv.note ?? "") !== v)
                                      patchAddr.mutate({ id: inv.id, body: { note: v === "" ? null : v } });
                                  }}
                                />
                              ) : (
                                <span className={dcimStyles.muted}>—</span>
                              )}
                            </td>
                            <td>
                              <div style={{ display: "flex", flexWrap: "wrap", gap: "0.35rem", alignItems: "center" }}>
                                <button
                                  type="button"
                                  className={dcimStyles.btn}
                                  style={{ padding: "0.2rem 0.45rem" }}
                                  disabled={row.assignment != null}
                                  title={t("ipam.grid.action.link")}
                                  onClick={() => {
                                    setLinkFor(row.address);
                                    setLinkDeviceId("");
                                    setLinkInterfaceId("");
                                  }}
                                >
                                  <i className="fas fa-link" aria-hidden />
                                </button>
                                <button
                                  type="button"
                                  className={dcimStyles.btnDanger}
                                  style={{ padding: "0.2rem 0.45rem" }}
                                  disabled={!canReleaseGridRow(row) || releaseGridRow.isPending}
                                  title={t("ipam.grid.action.release")}
                                  onClick={() => {
                                    if (!window.confirm(t("ipam.addr.releaseConfirm"))) return;
                                    releaseGridRow.mutate(row);
                                  }}
                                >
                                  <i className="fas fa-unlink" aria-hidden />
                                </button>
                              </div>
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                  </div>
                </>
              ) : gridQ.data != null && gridQ.data.rows.length > 0 && !gridQ.isLoading ? (
                <p className={dcimStyles.muted}>{t("ipam.addr.filterNoResults")}</p>
              ) : null}

            </>
          ) : null}

          <h5 className={dcimStyles.mfrDetailSectionTitle} style={{ marginTop: "var(--space-2)" }}>
            {t("ipam.addr.requestTitle")}
          </h5>
          <form
            className={dcimStyles.formRow}
            onSubmit={(e) => {
              e.preventDefault();
              setErr(null);
              if (reqMode === "assign" && reqDeviceId.trim() === "") {
                setErr(t("ipam.addr.assignNeedsDevice"));
                return;
              }
              if (reqMode === "assign" && reqInterfaceId.trim() === "") {
                setErr(t("dcim.equip.ip.chooseIface"));
                return;
              }
              requestAddr.mutate();
            }}
          >
            <label>
              {t("ipam.addr.mode")}
              <select value={reqMode} onChange={(e) => setReqMode(e.target.value as "reserve" | "assign")}>
                <option value="reserve">{t("ipam.addr.mode.reserve")}</option>
                <option value="assign">{t("ipam.addr.mode.assign")}</option>
              </select>
            </label>
            <label>
              {t("ipam.addr.interfaceId")}
              <select
                value={reqInterfaceId}
                onChange={(e) => setReqInterfaceId(e.target.value)}
                disabled={reqMode !== "assign"}
              >
                <option value="">{t("dcim.common.choose")}</option>
                {(interfacesQ.data ?? []).map((x) => (
                  <option key={x.id} value={String(x.id)}>
                    #{x.id} · {interfaceIndentedName(x, reqIfaceDepthById)}
                  </option>
                ))}
              </select>
            </label>
            <label>
              {t("ipam.addr.device")}
              <select value={reqDeviceId} onChange={(e) => setReqDeviceId(e.target.value)} disabled={reqMode !== "assign"}>
                <option value="">{t("dcim.common.choose")}</option>
                {(devicesQ.data ?? []).map((d) => (
                  <option key={d.id} value={String(d.id)}>
                    #{d.id} · {d.name}
                  </option>
                ))}
              </select>
            </label>
            <label>
              {t("ipam.addr.ownerUserId")}
              <select value={reqOwnerUserId} onChange={(e) => setReqOwnerUserId(e.target.value)}>
                <option value="">{t("dcim.common.choose")}</option>
                {(usersQ.data ?? []).map((u) => (
                  <option key={u.id} value={String(u.id)}>
                    #{u.id} · {u.display_name ?? u.username}
                  </option>
                ))}
              </select>
            </label>
            <label>
              {t("ipam.addr.ownerNew")}
              <input
                value={reqOwnerNewUsername}
                onChange={(e) => setReqOwnerNewUsername(e.target.value)}
                placeholder="username"
              />
            </label>
            <label>
              {t("ipam.addr.ownerNewDisplay")}
              <input value={reqOwnerNewDisplay} onChange={(e) => setReqOwnerNewDisplay(e.target.value)} />
            </label>
            <button
              type="button"
              className={dcimStyles.btn}
              disabled={createOwner.isPending || reqOwnerNewUsername.trim() === ""}
              onClick={() => createOwner.mutate()}
            >
              {createOwner.isPending ? "…" : t("ipam.addr.ownerNewBtn")}
            </button>
            <label>
              {t("ipam.addr.note")}
              <input value={reqNote} onChange={(e) => setReqNote(e.target.value)} />
            </label>
            <button type="submit" className={dcimStyles.btn} disabled={requestAddr.isPending}>
              {requestAddr.isPending ? "…" : t("ipam.addr.requestBtn")}
            </button>
          </form>
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
        <>
          <div
            className={dcimStyles.muted}
            style={{
              display: "flex",
              flexWrap: "wrap",
              alignItems: "center",
              gap: "0.75rem",
              marginBottom: "var(--space-2)",
            }}
          >
            <span>
              {t("ipam.grid.pagination.showing")}{" "}
              <strong>
                {prefixListSlice.rangeStart}–{prefixListSlice.rangeEnd}
              </strong>{" "}
              {t("ipam.grid.pagination.of")}{" "}
              <strong>{prefixListSlice.total}</strong>
            </span>
            <label style={{ display: "inline-flex", alignItems: "center", gap: "0.35rem" }}>
              {t("ipam.grid.pagination.perPage")}
              <select
                value={String(prefixListPageSize)}
                onChange={(e) => setPrefixListPageSize(Number(e.target.value))}
              >
                {GRID_PAGE_SIZE_OPTIONS.map((n) => (
                  <option key={n} value={String(n)}>
                    {n === 0 ? t("ipam.grid.pagination.all") : n}
                  </option>
                ))}
              </select>
            </label>
            <span style={{ display: "inline-flex", gap: "0.35rem" }}>
              <button
                type="button"
                className={dcimStyles.btn}
                disabled={prefixListSlice.safePage <= 0}
                onClick={() => setPrefixListPage((p) => Math.max(0, p - 1))}
              >
                {t("ipam.grid.pagination.prev")}
              </button>
              <button
                type="button"
                className={dcimStyles.btn}
                disabled={prefixListSlice.safePage >= prefixListSlice.pageCount - 1}
                onClick={() =>
                  setPrefixListPage((p) => Math.min(p + 1, prefixListSlice.pageCount - 1))
                }
              >
                {t("ipam.grid.pagination.next")}
              </button>
            </span>
          </div>
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
            {prefixListSlice.rows.map((x) => (
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
        </>
      ) : (
        !prefixesQ.isLoading && <p className={dcimStyles.muted}>{t("ipam.ipv4.empty")}</p>
      )}
    </Panel>
  );
}
