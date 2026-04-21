import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useId, useMemo, useRef, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { ConfirmModal } from "@/components/ui/ConfirmModal";
import { Panel } from "@/components/ui/Panel";
import { useI18n } from "@/i18n/I18nProvider";
import { ApiError } from "@/lib/api";
import * as dcimApi from "@/features/dcim/dcimApi";
import dcimStyles from "@/features/dcim/dcim.module.css";
import { interfaceDepthByInterfaceList, interfaceIndentedName } from "@/features/dcim/interfaceTreeLabels";
import type { Ipv4Prefix, PrefixAddressGridRow } from "./types";
import {
  buildPrefixTreeIndex,
  flattenVisiblePrefixTree,
  ipv4EqualSplitOptions,
  parseIpv4Cidr,
} from "./ipv4PrefixTree";
import * as ipamApi from "./ipamApi";
import { IpamIpRequestModal } from "./IpamIpRequestModal";

type ExploreCrumb = { id: number; name: string; cidr: string };

const GRID_PAGE_SIZE_OPTIONS = [25, 50, 100, 0] as const;
const SPLIT_PLANNED_PREVIEW_MAX = 48;

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

export function IpamPrefixesPage() {
  const { t } = useI18n();
  const splitDialogTitleId = useId();
  const qc = useQueryClient();
  const nav = useNavigate();
  const [err, setErr] = useState<string | null>(null);
  const [filterSite, setFilterSite] = useState<string>("");
  const [filterTenant, setFilterTenant] = useState<string>("");
  const [newSite, setNewSite] = useState("");
  const [newName, setNewName] = useState("");
  const [newCidr, setNewCidr] = useState("");
  const [newPrefixTenant, setNewPrefixTenant] = useState("");
  const [newPrefixVlan, setNewPrefixVlan] = useState("");
  const [newPrefixVrf, setNewPrefixVrf] = useState("");
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editName, setEditName] = useState("");
  const [editCidr, setEditCidr] = useState("");
  const [editTenantId, setEditTenantId] = useState("");
  const [editVlanId, setEditVlanId] = useState("");
  const [editVrfId, setEditVrfId] = useState("");
  const [exploreStack, setExploreStack] = useState<ExploreCrumb[]>([]);
  const [showScanHistory, setShowScanHistory] = useState(false);
  const [linkFor, setLinkFor] = useState<string | null>(null);
  const [linkDeviceId, setLinkDeviceId] = useState("");
  const [linkInterfaceId, setLinkInterfaceId] = useState("");
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
  const [ipRequestCtx, setIpRequestCtx] = useState<{
    prefixId: number;
    cidr: string;
    preferred: string;
  } | null>(null);
  const [gridReleaseRow, setGridReleaseRow] = useState<PrefixAddressGridRow | null>(null);
  const [deletePrefixTarget, setDeletePrefixTarget] = useState<{
    id: number;
    name: string;
    cidr: string;
  } | null>(null);
  const [svcGateway, setSvcGateway] = useState("");
  const [svcDns, setSvcDns] = useState("");
  const [svcDhcp, setSvcDhcp] = useState("");
  const [expandedPrefixIds, setExpandedPrefixIds] = useState<Set<number>>(() => new Set());
  const rootIdsKeyRef = useRef<string>("");
  const [splitTarget, setSplitTarget] = useState<Ipv4Prefix | null>(null);
  const [splitNewPrefixLen, setSplitNewPrefixLen] = useState<number | null>(null);
  const [splitMigrateInventory, setSplitMigrateInventory] = useState(true);
  const [splitAckBroadcast, setSplitAckBroadcast] = useState(false);
  const [splitErr, setSplitErr] = useState<string | null>(null);

  const sitesQ = useQuery({ queryKey: ["dcim", "sites"], queryFn: dcimApi.listSites });
  const tenantsQ = useQuery({ queryKey: ["tenants"], queryFn: dcimApi.listTenants });
  const vlansQ = useQuery({
    queryKey: ["ipam", "vlans", "all-for-prefixes"],
    queryFn: () => ipamApi.listIpamVlans(),
  });
  const vrfsQ = useQuery({ queryKey: ["ipam", "vrfs", "all-for-prefixes"], queryFn: () => ipamApi.listIpamVrfs() });
  const siteIdFilter = filterSite === "" ? undefined : Number(filterSite);
  const tenantIdFilter = filterTenant === "" ? undefined : Number(filterTenant);

  const prefixesQ = useQuery({
    queryKey: ["ipam", "ipv4-prefixes", siteIdFilter ?? "all", tenantIdFilter ?? "all"],
    queryFn: () => ipamApi.listIpv4Prefixes(siteIdFilter, tenantIdFilter),
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
  }, [tenantIdFilter]);

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

  const tenantNameById = useMemo(() => {
    const m = new Map<number, string>();
    for (const tn of tenantsQ.data ?? []) m.set(tn.id, tn.name);
    return m;
  }, [tenantsQ.data]);

  const vlanLabelById = useMemo(() => {
    const m = new Map<number, string>();
    for (const v of vlansQ.data ?? []) m.set(v.id, `VLAN ${v.vid} — ${v.name} (site ${v.site_id})`);
    return m;
  }, [vlansQ.data]);

  const vrfLabelById = useMemo(() => {
    const m = new Map<number, string>();
    for (const v of vrfsQ.data ?? []) m.set(v.id, `${v.name} (site ${v.site_id})`);
    return m;
  }, [vrfsQ.data]);

  const vlanOptionsForNewSite = useMemo(() => {
    const all = vlansQ.data ?? [];
    const siteNum = newSite.trim() ? Number(newSite) : null;
    if (siteNum == null || !Number.isFinite(siteNum) || siteNum < 1) return [];
    return all.filter((v) => v.site_id === siteNum);
  }, [vlansQ.data, newSite]);

  const vrfOptionsForNewSite = useMemo(() => {
    const all = vrfsQ.data ?? [];
    const siteNum = newSite.trim() ? Number(newSite) : null;
    if (siteNum == null || !Number.isFinite(siteNum) || siteNum < 1) return [];
    return all.filter((v) => v.site_id === siteNum);
  }, [vrfsQ.data, newSite]);

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
        tenant_id: newPrefixTenant === "" ? undefined : Number(newPrefixTenant),
        vlan_id: newPrefixVlan === "" ? undefined : Number(newPrefixVlan),
        vrf_id: newPrefixVrf === "" ? undefined : Number(newPrefixVrf),
      }),
    onSuccess: () => {
      setNewName("");
      setNewCidr("");
      setNewPrefixTenant("");
      setNewPrefixVlan("");
      setNewPrefixVrf("");
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
    mutationFn: ({
      id,
      body,
    }: {
      id: number;
      body: { name: string; cidr: string; tenant_id: number | null; vlan_id: number | null; vrf_id: number | null };
    }) => ipamApi.updateIpv4Prefix(id, body),
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

  const prefixTreeIndex = useMemo(() => buildPrefixTreeIndex(prefixesQ.data ?? []), [prefixesQ.data]);

  const prefixRootsSlice = useMemo(() => {
    const roots = prefixTreeIndex.roots;
    const total = roots.length;
    const size = prefixListPageSize === 0 ? Math.max(total, 1) : prefixListPageSize;
    const pageCount = Math.max(1, Math.ceil(total / size));
    const safePage = Math.min(Math.max(0, prefixListPage), pageCount - 1);
    const start = safePage * size;
    const end = prefixListPageSize === 0 ? total : Math.min(start + size, total);
    return {
      rows: roots.slice(start, end),
      total,
      size,
      pageCount,
      safePage,
      rangeStart: total === 0 ? 0 : start + 1,
      rangeEnd: end,
    };
  }, [prefixTreeIndex.roots, prefixListPage, prefixListPageSize]);

  const visiblePrefixRows = useMemo(
    () =>
      flattenVisiblePrefixTree(
        prefixRootsSlice.rows,
        prefixTreeIndex.childrenByParentId,
        expandedPrefixIds,
      ),
    [prefixRootsSlice.rows, prefixTreeIndex.childrenByParentId, expandedPrefixIds],
  );

  const splitEqualOptions = useMemo(
    () => (splitTarget ? ipv4EqualSplitOptions(splitTarget.cidr) : []),
    [splitTarget?.cidr, splitTarget?.id],
  );

  useEffect(() => {
    const key = prefixTreeIndex.roots
      .map((r) => r.id)
      .sort((a, b) => a - b)
      .join(",");
    if (key === rootIdsKeyRef.current) return;
    rootIdsKeyRef.current = key;
    setExpandedPrefixIds(new Set(prefixTreeIndex.roots.map((r) => r.id)));
  }, [prefixTreeIndex.roots]);

  useEffect(() => {
    const total = prefixTreeIndex.roots.length;
    const size = prefixListPageSize === 0 ? Math.max(total, 1) : prefixListPageSize;
    const pageCount = Math.max(1, Math.ceil(total / size));
    setPrefixListPage((p) => Math.min(Math.max(0, p), pageCount - 1));
  }, [prefixTreeIndex.roots.length, prefixListPageSize]);

  useEffect(() => {
    if (!splitTarget) {
      setSplitNewPrefixLen(null);
      setSplitMigrateInventory(true);
      setSplitAckBroadcast(false);
      setSplitErr(null);
      return;
    }
    setSplitNewPrefixLen(splitEqualOptions[0]?.newPrefixLen ?? null);
    setSplitMigrateInventory(true);
    setSplitAckBroadcast(false);
    setSplitErr(null);
  }, [splitTarget, splitEqualOptions]);

  useEffect(() => {
    setSplitAckBroadcast(false);
  }, [splitNewPrefixLen, splitMigrateInventory]);

  const splitPreviewEnabled = splitTarget != null && splitNewPrefixLen != null;

  const splitPreviewQ = useQuery({
    queryKey: [
      "ipam",
      "split-equal-preview",
      splitTarget?.id,
      splitNewPrefixLen,
      splitMigrateInventory,
    ],
    queryFn: () =>
      ipamApi.ipv4PrefixSplitEqual(splitTarget!.id, {
        new_prefix_len: splitNewPrefixLen!,
        dry_run: true,
        migrate_inventory: splitMigrateInventory,
        acknowledge_network_broadcast: false,
      }),
    enabled: splitPreviewEnabled,
    staleTime: 3_000,
  });

  const executeSplitMutation = useMutation({
    mutationFn: () =>
      ipamApi.ipv4PrefixSplitEqual(splitTarget!.id, {
        new_prefix_len: splitNewPrefixLen!,
        dry_run: false,
        migrate_inventory: splitMigrateInventory,
        acknowledge_network_broadcast: splitAckBroadcast,
      }),
    onMutate: () => setSplitErr(null),
    onSuccess: () => {
      setSplitTarget(null);
      setSplitErr(null);
      void qc.invalidateQueries({ queryKey: ["ipam", "split-equal-preview"] });
      invalidateIpam();
    },
    onError: (e: Error) => setSplitErr(e instanceof ApiError ? e.message : e.message),
  });

  const splitPv = splitPreviewQ.data;
  const splitNeedsAck = (splitPv?.conflicts?.length ?? 0) > 0;
  const splitBlockingCount =
    (splitPv?.ipam_inventory_on_parent ?? 0) +
    (splitPv?.dcim_iface_on_parent ?? 0) +
    (splitPv?.dcim_device_on_parent ?? 0);
  const splitMustMigrate = splitBlockingCount > 0 && !splitMigrateInventory;
  const splitCanExecute =
    splitPreviewEnabled &&
    splitPv != null &&
    !splitPv.has_child_prefixes &&
    splitPv.partition_ok &&
    !splitMustMigrate &&
    (!splitNeedsAck || splitAckBroadcast) &&
    !executeSplitMutation.isPending;

  const splitExecuteSubnetCount =
    splitPv?.subnet_count ??
    splitEqualOptions.find((o) => o.newPrefixLen === splitNewPrefixLen)?.subnetCount ??
    0;

  useEffect(() => {
    if (!splitTarget) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape" && !executeSplitMutation.isPending) setSplitTarget(null);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [splitTarget, executeSplitMutation.isPending]);

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

  const patchSubnetSvc = useMutation({
    mutationFn: () =>
      ipamApi.updateIpv4Prefix(exploreId!, {
        subnet_services: {
          gateway: svcGateway.trim() || null,
          dns: svcDns.trim() || null,
          dhcp_server: svcDhcp.trim() || null,
        },
      }),
    onSuccess: () => {
      setErr(null);
      void qc.invalidateQueries({ queryKey: ["ipam", "explore", exploreId] });
      void qc.invalidateQueries({ queryKey: ["ipam", "ipv4-prefixes"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const reserveOne = useMutation({
    mutationFn: async (address: string) => {
      const row = (gridQ.data?.rows ?? []).find((r) => r.address === address);
      if (row?.inventory) {
        await ipamApi.patchIpv4Address(row.inventory.id, { status: "reserved" });
        return;
      }
      const inv = await ipamApi.ensureIpv4Address({ ipv4_prefix_id: exploreId!, address });
      await ipamApi.patchIpv4Address(inv.id, { status: "reserved" });
    },
    onSuccess: () => {
      setErr(null);
      void qc.invalidateQueries({ queryKey: ["ipam", "explore", exploreId] });
      void qc.invalidateQueries({ queryKey: ["ipam", "address-grid", exploreId] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  useEffect(() => {
    const p = exploreQ.data?.prefix;
    if (!p) return;
    const s = p.subnet_services;
    setSvcGateway(typeof s?.gateway === "string" ? s.gateway : "");
    setSvcDns(typeof s?.dns === "string" ? s.dns : "");
    setSvcDhcp(typeof s?.dhcp_server === "string" ? s.dhcp_server : "");
  }, [exploreQ.data?.prefix?.id, exploreQ.data?.prefix?.subnet_services]);

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
      {ipRequestCtx ? (
        <IpamIpRequestModal
          open
          onClose={() => setIpRequestCtx(null)}
          prefixId={ipRequestCtx.prefixId}
          prefixCidr={ipRequestCtx.cidr}
          initialPreferred={ipRequestCtx.preferred}
          onAllocated={() => {
            void qc.invalidateQueries({ queryKey: ["ipam", "ipv4-prefixes"] });
            void qc.invalidateQueries({ queryKey: ["ipam", "explore"] });
            void qc.invalidateQueries({ queryKey: ["ipam", "address-grid"] });
          }}
        />
      ) : null}
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
          <label>
            {t("ipam.ipv4.filterTenant")}
            <select value={filterTenant} onChange={(e) => setFilterTenant(e.target.value)}>
              <option value="">{t("ipam.ipv4.allTenants")}</option>
              {(tenantsQ.data ?? []).map((tn) => (
                <option key={tn.id} value={String(tn.id)}>
                  {tn.name}
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
                {t("ipam.subnetSvc.title")}
              </h5>
              <p className={dcimStyles.muted} style={{ marginTop: 0 }}>
                {t("ipam.subnetSvc.intro")}
              </p>
              <form
                className={dcimStyles.formRow}
                style={{ marginBottom: "var(--space-3)", flexWrap: "wrap" }}
                onSubmit={(e) => {
                  e.preventDefault();
                  patchSubnetSvc.mutate();
                }}
              >
                <label>
                  {t("ipam.subnetSvc.gateway")}
                  <input value={svcGateway} onChange={(e) => setSvcGateway(e.target.value)} placeholder="192.168.1.1" />
                </label>
                <label>
                  {t("ipam.subnetSvc.dns")}
                  <input value={svcDns} onChange={(e) => setSvcDns(e.target.value)} placeholder="192.168.1.2, 192.168.1.3" />
                </label>
                <label>
                  {t("ipam.subnetSvc.dhcp")}
                  <input value={svcDhcp} onChange={(e) => setSvcDhcp(e.target.value)} placeholder="192.168.1.4" />
                </label>
                <button type="submit" className={dcimStyles.btn} disabled={patchSubnetSvc.isPending}>
                  {patchSubnetSvc.isPending ? "…" : t("ipam.subnetSvc.save")}
                </button>
              </form>

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
                        <th>{t("ipam.grid.colRole")}</th>
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
                                  to={`/snmp/tools?host=${encodeURIComponent(row.address)}`}
                                  className={dcimStyles.tableLink}
                                  title={t("ipam.grid.addressOpenSnmpDiscovery")}
                                >
                                  <code>{row.address}</code>
                                </Link>
                              )}
                            </td>
                            <td className={dcimStyles.muted}>
                              {row.address_role === "network"
                                ? t("ipam.grid.role.network")
                                : row.address_role === "broadcast"
                                  ? t("ipam.grid.role.broadcast")
                                  : "—"}
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
                                  disabled={!isGridRowFree(row) || reserveOne.isPending}
                                  title={t("ipam.grid.action.reserve")}
                                  onClick={() => reserveOne.mutate(row.address)}
                                >
                                  <i className="fas fa-bookmark" aria-hidden />
                                </button>
                                <button
                                  type="button"
                                  className={dcimStyles.btn}
                                  style={{ padding: "0.2rem 0.45rem" }}
                                  disabled={row.assignment != null}
                                  title={t("ipam.addr.openRequestModal")}
                                  onClick={() => {
                                    setErr(null);
                                    const c = exploreStack[exploreStack.length - 1];
                                    if (c)
                                      setIpRequestCtx({
                                        prefixId: c.id,
                                        cidr: c.cidr,
                                        preferred: row.address,
                                      });
                                  }}
                                >
                                  <i className="fas fa-inbox" aria-hidden />
                                </button>
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
                                  onClick={() => setGridReleaseRow(row)}
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

          <div style={{ marginTop: "var(--space-2)" }}>
            <button
              type="button"
              className={dcimStyles.btn}
              onClick={() => {
                setErr(null);
                const c = exploreStack[exploreStack.length - 1];
                if (c) setIpRequestCtx({ prefixId: c.id, cidr: c.cidr, preferred: "" });
              }}
            >
              {t("ipam.addr.openRequestModal")}
            </button>
          </div>
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
          <label>
            {t("ipam.ipv4.coloTenant")}
            <select value={newPrefixTenant} onChange={(e) => setNewPrefixTenant(e.target.value)}>
              <option value="">{t("dcim.common.none")}</option>
              {(tenantsQ.data ?? []).map((tn) => (
                <option key={tn.id} value={String(tn.id)}>
                  {tn.name}
                </option>
              ))}
            </select>
          </label>
          <label>
            VLAN (valgfritt)
            <select value={newPrefixVlan} onChange={(e) => setNewPrefixVlan(e.target.value)}>
              <option value="">{t("dcim.common.none")}</option>
              {vlanOptionsForNewSite.map((v) => (
                <option key={v.id} value={String(v.id)}>
                  VLAN {v.vid} — {v.name}
                </option>
              ))}
            </select>
          </label>
          <label>
            VRF (valgfritt)
            <select value={newPrefixVrf} onChange={(e) => setNewPrefixVrf(e.target.value)}>
              <option value="">{t("dcim.common.none")}</option>
              {vrfOptionsForNewSite.map((v) => (
                <option key={v.id} value={String(v.id)}>
                  {v.name}
                </option>
              ))}
            </select>
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
                {prefixRootsSlice.rangeStart}–{prefixRootsSlice.rangeEnd}
              </strong>{" "}
              {t("ipam.grid.pagination.of")}{" "}
              <strong>{prefixRootsSlice.total}</strong>
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
                disabled={prefixRootsSlice.safePage <= 0}
                onClick={() => setPrefixListPage((p) => Math.max(0, p - 1))}
              >
                {t("ipam.grid.pagination.prev")}
              </button>
              <button
                type="button"
                className={dcimStyles.btn}
                disabled={prefixRootsSlice.safePage >= prefixRootsSlice.pageCount - 1}
                onClick={() =>
                  setPrefixListPage((p) => Math.min(p + 1, prefixRootsSlice.pageCount - 1))
                }
              >
                {t("ipam.grid.pagination.next")}
              </button>
            </span>
          </div>
          <p className={dcimStyles.muted} style={{ marginTop: "-0.25rem", marginBottom: "var(--space-2)" }}>
            {t("ipam.ipv4.paginationRootsHint")}
          </p>
          <table className={dcimStyles.table}>
          <thead>
            <tr>
              <th style={{ width: "2.25rem" }} aria-label={t("ipam.ipv4.treeColAria")} />
              <th>{t("dcim.common.id")}</th>
              <th>{t("ipam.ipv4.site")}</th>
              <th>VRF</th>
              <th>VLAN</th>
              <th>{t("ipam.ipv4.tenantCol")}</th>
              <th>{t("ipam.ipv4.name")}</th>
              <th>{t("ipam.ipv4.cidr")}</th>
              <th>{t("ipam.ipv4.usageCol")}</th>
              <th>{t("ipam.ipv4.exploreCol")}</th>
              <th>{t("ipam.ipv4.actionsCol")}</th>
            </tr>
          </thead>
          <tbody>
            {visiblePrefixRows.map((row) => {
              const x = row.prefix;
              const plen = parseIpv4Cidr(x.cidr)?.prefixLen;
              const childCount = prefixTreeIndex.childrenByParentId.get(x.id)?.length ?? 0;
              const canSplit = plen != null && plen < 32 && childCount === 0;
              return (
              <tr key={x.id}>
                <td
                  style={{
                    paddingLeft: `calc(${row.depth} * 0.65rem)`,
                    verticalAlign: "middle",
                    whiteSpace: "nowrap",
                  }}
                >
                  {row.hasChildren ? (
                    <button
                      type="button"
                      className={dcimStyles.btnLink}
                      style={{ padding: "0 0.15rem", minWidth: "1.25rem" }}
                      aria-expanded={expandedPrefixIds.has(x.id)}
                      title={expandedPrefixIds.has(x.id) ? t("ipam.ipv4.treeCollapse") : t("ipam.ipv4.treeExpand")}
                      onClick={() => {
                        setExpandedPrefixIds((prev) => {
                          const n = new Set(prev);
                          if (n.has(x.id)) n.delete(x.id);
                          else n.add(x.id);
                          return n;
                        });
                      }}
                    >
                      {expandedPrefixIds.has(x.id) ? "▼" : "▶"}
                    </button>
                  ) : (
                    <span style={{ display: "inline-block", width: "1.25rem" }} aria-hidden />
                  )}
                </td>
                <td>{x.id}</td>
                <td>{siteNameById.get(x.site_id) ?? `#${x.site_id}`}</td>
                <td>
                  {editingId === x.id ? (
                    <select value={editVrfId} onChange={(e) => setEditVrfId(e.target.value)} aria-label="VRF">
                      <option value="">{t("dcim.common.none")}</option>
                      {(vrfsQ.data ?? [])
                        .filter((v) => v.site_id === x.site_id)
                        .map((v) => (
                          <option key={v.id} value={String(v.id)}>
                            {v.name}
                          </option>
                        ))}
                    </select>
                  ) : x.vrf_id != null && x.vrf_id > 0 ? (
                    vrfLabelById.get(x.vrf_id) ?? `#${x.vrf_id}`
                  ) : (
                    "—"
                  )}
                </td>
                <td>
                  {editingId === x.id ? (
                    <select value={editVlanId} onChange={(e) => setEditVlanId(e.target.value)} aria-label="VLAN">
                      <option value="">{t("dcim.common.none")}</option>
                      {(vlansQ.data ?? [])
                        .filter((v) => v.site_id === x.site_id)
                        .map((v) => (
                          <option key={v.id} value={String(v.id)}>
                            VLAN {v.vid} — {v.name}
                          </option>
                        ))}
                    </select>
                  ) : x.vlan_id != null && x.vlan_id > 0 ? (
                    <button
                      type="button"
                      className={dcimStyles.btnLink}
                      title="Åpne VLAN"
                      onClick={() => nav(`/ipam/vlans?site=${encodeURIComponent(String(x.site_id))}&vlan=${encodeURIComponent(String(x.vlan_id))}`)}
                    >
                      {vlanLabelById.get(x.vlan_id) ?? `#${x.vlan_id}`}
                    </button>
                  ) : (
                    "—"
                  )}
                </td>
                <td>
                  {editingId === x.id ? (
                    <select
                      value={editTenantId}
                      onChange={(e) => setEditTenantId(e.target.value)}
                      aria-label={t("ipam.ipv4.tenantCol")}
                    >
                      <option value="">{t("dcim.common.none")}</option>
                      {(tenantsQ.data ?? []).map((tn) => (
                        <option key={tn.id} value={String(tn.id)}>
                          {tn.name}
                        </option>
                      ))}
                    </select>
                  ) : x.tenant_id != null && x.tenant_id > 0 ? (
                    tenantNameById.get(x.tenant_id) ?? `#${x.tenant_id}`
                  ) : (
                    "—"
                  )}
                </td>
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
                  <div className={dcimStyles.tableIconActions}>
                    <button
                      type="button"
                      className={dcimStyles.tableIconBtn}
                      disabled={editingId === x.id}
                      title={t("ipam.ipv4.openExplore")}
                      aria-label={t("ipam.ipv4.openExplore")}
                      onClick={() => openExplore(x)}
                    >
                      <i className="fas fa-sitemap" aria-hidden />
                    </button>
                  </div>
                </td>
                <td>
                  {editingId === x.id ? (
                    <span className={dcimStyles.tableIconActions}>
                      <button
                        type="button"
                        className={dcimStyles.tableIconBtn}
                        disabled={patchPfx.isPending}
                        title={t("dcim.common.save")}
                        aria-label={t("dcim.common.save")}
                        onClick={() => {
                          const nm = editName.trim();
                          const cd = editCidr.trim();
                          if (!nm || !cd) {
                            setErr(t("ipam.ipv4.addMissing"));
                            return;
                          }
                          const tid =
                            editTenantId === "" ? null : Number(editTenantId);
                          if (editTenantId !== "" && (!Number.isFinite(tid) || (tid as number) < 1)) {
                            setErr(t("ipam.ipv4.addMissing"));
                            return;
                          }
                          const vid = editVlanId === "" ? null : Number(editVlanId);
                          if (editVlanId !== "" && (!Number.isFinite(vid) || (vid as number) < 1)) {
                            setErr(t("ipam.ipv4.addMissing"));
                            return;
                          }
                          const vrfId = editVrfId === "" ? null : Number(editVrfId);
                          if (editVrfId !== "" && (!Number.isFinite(vrfId) || (vrfId as number) < 1)) {
                            setErr(t("ipam.ipv4.addMissing"));
                            return;
                          }
                          patchPfx.mutate({
                            id: x.id,
                            body: {
                              name: nm,
                              cidr: cd,
                              tenant_id: tid,
                              vlan_id: vid,
                              vrf_id: vrfId,
                            },
                          });
                        }}
                      >
                        {patchPfx.isPending ? (
                          "…"
                        ) : (
                          <i className="fas fa-floppy-disk" aria-hidden />
                        )}
                      </button>
                      <button
                        type="button"
                        className={dcimStyles.tableIconBtn}
                        title={t("ipam.ipv4.cancel")}
                        aria-label={t("ipam.ipv4.cancel")}
                        onClick={() => {
                          setEditingId(null);
                          setErr(null);
                        }}
                      >
                        <i className="fas fa-xmark" aria-hidden />
                      </button>
                    </span>
                  ) : (
                    <span className={dcimStyles.tableIconActions}>
                      {canSplit ? (
                        <button
                          type="button"
                          className={dcimStyles.tableIconBtn}
                          title={t("ipam.ipv4.splitSubnet")}
                          aria-label={t("ipam.ipv4.splitSubnet")}
                          onClick={() => {
                            setErr(null);
                            setSplitTarget(x);
                          }}
                        >
                          <i className="fas fa-scissors" aria-hidden />
                        </button>
                      ) : null}
                      <button
                        type="button"
                        className={dcimStyles.tableIconBtn}
                        title={t("ipam.ipv4.requestIps")}
                        aria-label={t("ipam.ipv4.requestIps")}
                        onClick={() => {
                          setErr(null);
                          setIpRequestCtx({ prefixId: x.id, cidr: x.cidr, preferred: "" });
                        }}
                      >
                        <i className="fas fa-inbox" aria-hidden />
                      </button>
                      <button
                        type="button"
                        className={dcimStyles.tableIconBtn}
                        title={t("ipam.ipv4.edit")}
                        aria-label={t("ipam.ipv4.edit")}
                        onClick={() => {
                          setEditingId(x.id);
                          setEditName(x.name);
                          setEditCidr(x.cidr);
                          setEditTenantId(
                            x.tenant_id != null && x.tenant_id > 0 ? String(x.tenant_id) : "",
                          );
                          setEditVlanId(x.vlan_id != null && x.vlan_id > 0 ? String(x.vlan_id) : "");
                          setEditVrfId(x.vrf_id != null && x.vrf_id > 0 ? String(x.vrf_id) : "");
                          setErr(null);
                        }}
                      >
                        <i className="fas fa-pen-to-square" aria-hidden />
                      </button>
                      <button
                        type="button"
                        className={`${dcimStyles.tableIconBtn} ${dcimStyles.tableIconBtnDanger}`.trim()}
                        title={t("dcim.common.delete")}
                        aria-label={t("dcim.common.delete")}
                        disabled={delPfx.isPending}
                        onClick={() => setDeletePrefixTarget({ id: x.id, name: x.name, cidr: x.cidr })}
                      >
                        <i className="fas fa-trash-can" aria-hidden />
                      </button>
                    </span>
                  )}
                </td>
              </tr>
            );
            })}
          </tbody>
        </table>
        </>
      ) : (
        !prefixesQ.isLoading && <p className={dcimStyles.muted}>{t("ipam.ipv4.empty")}</p>
      )}
      {splitTarget != null ? (
        <div
          role="presentation"
          style={{
            position: "fixed",
            inset: 0,
            zIndex: 200,
            background: "rgba(0,0,0,0.45)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            padding: "var(--space-3)",
          }}
          onClick={(e) => {
            if (e.target === e.currentTarget && !executeSplitMutation.isPending) setSplitTarget(null);
          }}
        >
          <div
            role="dialog"
            aria-modal="true"
            aria-labelledby={splitDialogTitleId}
            style={{
              width: "min(32rem, 100%)",
              maxHeight: "90vh",
              overflow: "auto",
              background: "var(--color-bg-elevated)",
              border: "1px solid var(--shell-border)",
              borderRadius: "var(--radius-md)",
              padding: "var(--space-4)",
              boxShadow: "0 8px 32px rgba(0,0,0,0.2)",
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <h2 id={splitDialogTitleId} style={{ marginTop: 0 }}>
              {t("ipam.ipv4.splitTitle")}
            </h2>
            <p className={dcimStyles.muted}>{t("ipam.ipv4.splitIntro", { cidr: splitTarget.cidr })}</p>
            <p className={dcimStyles.muted}>{t("ipam.ipv4.splitEqualHint")}</p>
            {splitEqualOptions.length === 0 ? (
              <p className={dcimStyles.err}>{t("ipam.ipv4.splitEqualNoOptions")}</p>
            ) : (
              <label style={{ display: "block", marginTop: "var(--space-2)" }}>
                {t("ipam.ipv4.splitEqualSelect")}
                <select
                  value={splitNewPrefixLen ?? ""}
                  onChange={(e) => {
                    const v = e.target.value;
                    setSplitNewPrefixLen(v === "" ? null : Number(v));
                  }}
                  style={{ display: "block", width: "100%", marginTop: "0.25rem" }}
                >
                  {splitEqualOptions.map((o) => (
                    <option key={o.newPrefixLen} value={o.newPrefixLen}>
                      {o.label}
                    </option>
                  ))}
                </select>
              </label>
            )}
            <label style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginTop: "var(--space-3)" }}>
              <input
                type="checkbox"
                checked={splitMigrateInventory}
                onChange={(e) => setSplitMigrateInventory(e.target.checked)}
              />
              <span>{t("ipam.ipv4.splitMigrateLabel")}</span>
            </label>
            {splitPreviewQ.isFetching ? <p className={dcimStyles.muted}>{t("ipam.ipv4.splitPreviewLoading")}</p> : null}
            {splitPreviewQ.isError ? (
              <p className={dcimStyles.err}>{(splitPreviewQ.error as Error).message}</p>
            ) : null}
            {splitPv != null ? (
              <div style={{ marginTop: "var(--space-2)" }}>
                {splitPv.has_child_prefixes ? (
                  <p className={dcimStyles.err}>{splitPv.detail ?? t("ipam.ipv4.splitHasChildren")}</p>
                ) : null}
                {!splitPv.partition_ok && splitPv.detail ? (
                  <p className={dcimStyles.err}>{splitPv.detail}</p>
                ) : null}
                {splitPv.partition_ok && !splitPv.has_child_prefixes ? (
                  <p className={dcimStyles.muted}>
                    {t("ipam.ipv4.splitSummary", {
                      inv: String(splitPv.ipam_inventory_on_parent),
                      iface: String(splitPv.dcim_iface_on_parent),
                      dev: String(splitPv.dcim_device_on_parent),
                    })}
                  </p>
                ) : null}
                {splitPv.partition_ok && !splitPv.has_child_prefixes && splitPv.planned.length > 0 ? (
                  <div style={{ marginTop: "var(--space-2)" }}>
                    <p className={dcimStyles.muted}>{t("ipam.ipv4.splitPlannedHint")}</p>
                    <ul
                      className={dcimStyles.muted}
                      style={{
                        marginTop: "0.25rem",
                        paddingLeft: "1.25rem",
                        maxHeight: "14rem",
                        overflow: "auto",
                        fontFamily: "monospace",
                        fontSize: "0.85rem",
                      }}
                    >
                      {splitPv.planned.slice(0, SPLIT_PLANNED_PREVIEW_MAX).map((row) => (
                        <li key={row.cidr}>
                          <code>{row.cidr}</code>
                          {row.suggested_name !== row.cidr ? <> → {row.suggested_name}</> : null}
                        </li>
                      ))}
                    </ul>
                    {splitPv.planned.length > SPLIT_PLANNED_PREVIEW_MAX ? (
                      <p className={dcimStyles.muted}>
                        {t("ipam.ipv4.splitPlannedTruncated", {
                          shown: String(SPLIT_PLANNED_PREVIEW_MAX),
                          total: String(splitPv.planned.length),
                        })}
                      </p>
                    ) : null}
                  </div>
                ) : null}
                {splitPv.conflicts.length > 0 ? (
                  <div style={{ marginTop: "var(--space-2)" }}>
                    <p className={dcimStyles.err}>{t("ipam.ipv4.splitConflictsTitle")}</p>
                    <ul className={dcimStyles.muted} style={{ marginTop: 0 }}>
                      {splitPv.conflicts.map((c, i) => (
                        <li key={`${c.address}-${c.subnet_cidr}-${i}`}>
                          <code>{c.address}</code> — {c.message}
                        </li>
                      ))}
                    </ul>
                    <label style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginTop: "var(--space-2)" }}>
                      <input
                        type="checkbox"
                        checked={splitAckBroadcast}
                        onChange={(e) => setSplitAckBroadcast(e.target.checked)}
                      />
                      <span>{t("ipam.ipv4.splitAckBroadcast")}</span>
                    </label>
                  </div>
                ) : null}
                {splitMustMigrate ? <p className={dcimStyles.err}>{t("ipam.ipv4.splitMustMigrate")}</p> : null}
              </div>
            ) : null}
            {splitErr ? <p className={dcimStyles.err}>{splitErr}</p> : null}
            <div style={{ display: "flex", gap: "var(--space-2)", marginTop: "var(--space-3)", flexWrap: "wrap" }}>
              <button
                type="button"
                className={dcimStyles.btn}
                disabled={!splitCanExecute}
                onClick={() => executeSplitMutation.mutate()}
              >
                {executeSplitMutation.isPending
                  ? "…"
                  : t("ipam.ipv4.splitExecute", { count: String(splitExecuteSubnetCount) })}
              </button>
              <button
                type="button"
                className={dcimStyles.btn}
                disabled={executeSplitMutation.isPending}
                onClick={() => setSplitTarget(null)}
              >
                {t("ipam.ipv4.splitCancel")}
              </button>
            </div>
          </div>
        </div>
      ) : null}
      <ConfirmModal
        open={gridReleaseRow != null}
        onClose={() => {
          if (!releaseGridRow.isPending) setGridReleaseRow(null);
        }}
        title={t("ipam.addr.release")}
        message={
          gridReleaseRow ? (
            <>
              <code>{gridReleaseRow.address}</code>
              <br />
              {t("ipam.addr.releaseConfirm")}
            </>
          ) : null
        }
        confirmLabel={t("ipam.addr.release")}
        cancelLabel={t("dcim.common.cancel")}
        danger
        pending={releaseGridRow.isPending}
        onConfirm={() => {
          if (!gridReleaseRow) return;
          releaseGridRow.mutate(gridReleaseRow, { onSettled: () => setGridReleaseRow(null) });
        }}
      />
      <ConfirmModal
        open={deletePrefixTarget != null}
        onClose={() => {
          if (!delPfx.isPending) setDeletePrefixTarget(null);
        }}
        title={t("ui.confirmTitle")}
        message={
          deletePrefixTarget
            ? t("ipam.ipv4.deletePrefixConfirm", {
                name: deletePrefixTarget.name,
                cidr: deletePrefixTarget.cidr,
              })
            : null
        }
        confirmLabel={t("dcim.common.delete")}
        cancelLabel={t("dcim.common.cancel")}
        danger
        pending={delPfx.isPending}
        onConfirm={() => {
          if (!deletePrefixTarget) return;
          delPfx.mutate(deletePrefixTarget.id, { onSettled: () => setDeletePrefixTarget(null) });
        }}
      />
    </Panel>
  );
}
