import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useMemo, useState } from "react";
import { Link, useParams, useSearchParams } from "react-router-dom";
import { catalogProvisionHref } from "@/features/catalog/catalogHref";
import { ConfirmModal } from "@/components/ui/ConfirmModal";
import { Panel } from "@/components/ui/Panel";
import { useI18n } from "@/i18n/I18nProvider";
import { ApiError, apiGet } from "@/lib/api";
import * as ipamApi from "@/features/ipam/ipamApi";
import * as api from "./dcimApi";
import { DcimOwnerComponentsPanel } from "./DcimOwnerComponentsPanel";
import { DevicePortsCablesPanel } from "./DevicePortsCablesPanel";
import { DCIM_DEVICE_ICON_URL_ATTR } from "./modelImages";
import { interfaceDepthByInterfaceList, interfaceIndentedName } from "./interfaceTreeLabels";
import type { IpamWireGuardInterface } from "@/features/ipam/types";
import type { DeviceInterface, DeviceInterfaceLag, DeviceInterfaceVlanMember, DeviceIpAssignment } from "./types";
import { CAP_DCIM_DEVICE_HARDWARE_VIEW, CAP_DCIM_DEVICE_OS_VIEW } from "@/plugins/capabilities";
import { pluginsWithCapability } from "@/plugins/devicePluginSupport";
import { usePlugins } from "@/plugins/PluginContext";
import { SnmpInventoryPanel } from "@/features/snmp/SnmpInventoryPanel";
import { DcimInnerTabs } from "./DcimInnerTabs";
import styles from "./dcim.module.css";

function strAttr(v: unknown): string {
  return typeof v === "string" ? v : "";
}

function looksIpv6(addr: string): boolean {
  return addr.includes(":");
}

function formatSnmpExtra(attrs: Record<string, unknown>): string {
  const x = attrs.snmp_communities;
  if (Array.isArray(x)) return x.map(String).join(", ");
  if (typeof x === "string") return x;
  return "";
}

const DEVICE_DETAIL_TABS = new Set(["overview", "network", "hardware", "os"]);
type DeviceDetailTab = "overview" | "network" | "hardware" | "os";

type DeviceNetDeleteConfirm =
  | { kind: "interface"; iid: number; name: string }
  | { kind: "ip"; iid: number; aid: number; address: string }
  | { kind: "lag"; lid: number; name: string }
  | { kind: "lag-member"; mid: number; name: string }
  | { kind: "wg"; wid: number; name: string }
  | { kind: "wg-peer"; pid: number; name: string }
  | { kind: "vlan-member"; mid: number; name: string };

export function DcimDeviceDetailPage() {
  const { t } = useI18n();
  const qc = useQueryClient();
  const plugins = usePlugins();
  const { deviceId } = useParams<{ deviceId: string }>();
  const [searchParams, setSearchParams] = useSearchParams();
  const id = Number(deviceId);
  const backToDevices = "/dcim/equipment?tab=dev";

  const tabParam = searchParams.get("tab");
  const detailTab: DeviceDetailTab =
    tabParam != null && DEVICE_DETAIL_TABS.has(tabParam) ? (tabParam as DeviceDetailTab) : "overview";

  const setDetailTab = (next: string) => {
    if (!DEVICE_DETAIL_TABS.has(next)) return;
    setSearchParams(
      (prev) => {
        const n = new URLSearchParams(prev);
        if (next === "overview") n.delete("tab");
        else n.set("tab", next);
        return n;
      },
      { replace: true },
    );
  };

  const [err, setErr] = useState<string | null>(null);
  const [ifName, setIfName] = useState("");
  const [ifMac, setIfMac] = useState("");
  const [ifSpeed, setIfSpeed] = useState("");
  const [ifMtu, setIfMtu] = useState("");
  const [ifDesc, setIfDesc] = useState("");
  const [ifSort, setIfSort] = useState("0");
  const [ifVlan, setIfVlan] = useState("");
  const [ifIpamVlan, setIfIpamVlan] = useState("");
  const [ifIpamVrf, setIfIpamVrf] = useState("");
  const [ifParent, setIfParent] = useState("");
  const [vlanDraft, setVlanDraft] = useState<Record<number, string>>({});
  const [parentDraft, setParentDraft] = useState<Record<number, string>>({});
  const [ipIface, setIpIface] = useState("");
  const [ipAddr, setIpAddr] = useState("");
  const [ipPrimary, setIpPrimary] = useState(false);
  const [ipPrefix, setIpPrefix] = useState("");
  const [ipPrefix6, setIpPrefix6] = useState("");
  const [ipPrefixDraft, setIpPrefixDraft] = useState<Record<number, string>>({});
  const [ipPrefix6Draft, setIpPrefix6Draft] = useState<Record<number, string>>({});
  const [typeEdit, setTypeEdit] = useState("");
  const [roleEdit, setRoleEdit] = useState("");
  const [artPick, setArtPick] = useState("");
  const [artIntent, setArtIntent] = useState<"recorded" | "intended">("recorded");
  const [blPick, setBlPick] = useState("");
  const [blIntent, setBlIntent] = useState<"recorded" | "intended">("recorded");
  const [vrfPick, setVrfPick] = useState("");
  const [vrfIntent, setVrfIntent] = useState<"recorded" | "intended">("recorded");
  const [serialDraft, setSerialDraft] = useState("");
  const [assetDraft, setAssetDraft] = useState("");
  const [iconUrlDraft, setIconUrlDraft] = useState("");
  const [snmpReadDraft, setSnmpReadDraft] = useState("public");
  const [snmpWriteDraft, setSnmpWriteDraft] = useState("");
  const [snmpExtraDraft, setSnmpExtraDraft] = useState("");
  const [devIpAddr, setDevIpAddr] = useState("");
  const [devIpPrimary, setDevIpPrimary] = useState(false);
  const [devIpPrefix, setDevIpPrefix] = useState("");
  const [devIpPrefix6, setDevIpPrefix6] = useState("");
  const [devIpPrefixDraft, setDevIpPrefixDraft] = useState<Record<number, string>>({});
  const [devIpPrefix6Draft, setDevIpPrefix6Draft] = useState<Record<number, string>>({});
  const [netDeleteConfirm, setNetDeleteConfirm] = useState<DeviceNetDeleteConfirm | null>(null);
  const [lagName, setLagName] = useState("");
  const [lagId, setLagId] = useState("");
  const [lagIfaceId, setLagIfaceId] = useState("");
  const [vlanMemIfaceId, setVlanMemIfaceId] = useState("");
  const [vlanMemVlanId, setVlanMemVlanId] = useState("");
  const [vlanMemRole, setVlanMemRole] = useState("");
  const [wgName, setWgName] = useState("");
  const [wgListen, setWgListen] = useState("");
  const [wgAddr, setWgAddr] = useState("");
  const [wgPriv, setWgPriv] = useState("");
  const [wgDcimIface, setWgDcimIface] = useState("");
  const [wgVpnId, setWgVpnId] = useState("");
  const [wgTunnelId, setWgTunnelId] = useState("");
  const [wgPeerIface, setWgPeerIface] = useState("");
  const [wgPeerName, setWgPeerName] = useState("");
  const [wgPeerKey, setWgPeerKey] = useState("");
  const [wgPeerPsk, setWgPeerPsk] = useState("");
  const [wgPeerHost, setWgPeerHost] = useState("");
  const [wgPeerPort, setWgPeerPort] = useState("");
  const [wgPeerAllowed, setWgPeerAllowed] = useState("");

  const deviceQ = useQuery({
    queryKey: ["dcim", "devices", id],
    queryFn: () => api.getDevice(id),
    enabled: Number.isFinite(id) && id > 0,
  });

  const interfacesQ = useQuery({
    queryKey: ["dcim", "devices", id, "interfaces"],
    queryFn: () => api.listDeviceInterfaces(id),
    enabled: Number.isFinite(id) && id > 0,
  });

  const lagsQ = useQuery({
    queryKey: ["dcim", "devices", id, "interface-lags"],
    queryFn: () => api.listDeviceInterfaceLags(id),
    enabled: Number.isFinite(id) && id > 0,
  });
  const vlanMemQ = useQuery({
    queryKey: ["dcim", "devices", id, "interface-vlans"],
    queryFn: () => api.listDeviceInterfaceVlans(id),
    enabled: Number.isFinite(id) && id > 0,
  });
  const wgQ = useQuery({
    queryKey: ["ipam", "wireguard-interfaces", id],
    queryFn: () => ipamApi.listWireGuardInterfaces(id),
    enabled: Number.isFinite(id) && id > 0,
  });
  const wgVpnsQ = useQuery({
    queryKey: ["ipam", "vpn-services"],
    queryFn: () => ipamApi.listVpnServices(),
  });
  const wgTunnelsQ = useQuery({
    queryKey: ["ipam", "vpn-tunnels", wgVpnId],
    queryFn: () => ipamApi.listVpnTunnels(Number(wgVpnId)),
    enabled: wgVpnId !== "",
  });

  const deviceIpsQ = useQuery({
    queryKey: ["dcim", "devices", id, "device-ip-assignments"],
    queryFn: () => api.listDeviceIpAssignments(id),
    enabled: Number.isFinite(id) && id > 0,
  });

  const typesQ = useQuery({
    queryKey: ["dcim", "device-types"],
    queryFn: api.listDeviceTypes,
  });

  const rolesQ = useQuery({
    queryKey: ["dcim", "device-roles"],
    queryFn: api.listDeviceRoles,
  });
  const artifactsQ = useQuery({
    queryKey: ["dcim", "device-artifacts"],
    queryFn: api.listDeviceArtifacts,
  });
  const artifactRecQ = useQuery({
    queryKey: ["dcim", "devices", id, "artifacts"],
    queryFn: () => api.listDeviceArtifactRecords(id),
    enabled: Number.isFinite(id),
  });
  const baselinesQ = useQuery({
    queryKey: ["dcim", "device-artifact-baselines"],
    queryFn: api.listDeviceArtifactBaselines,
  });
  const blAssignQ = useQuery({
    queryKey: ["dcim", "devices", id, "artifact-baselines"],
    queryFn: () => api.listDeviceArtifactBaselineAssignments(id),
    enabled: Number.isFinite(id),
  });

  const modelsQ = useQuery({
    queryKey: ["dcim", "device-models"],
    queryFn: api.listDeviceModels,
  });

  const sitesQ = useQuery({ queryKey: ["dcim", "sites"], queryFn: api.listSites });

  const deviceSiteId = deviceQ.data?.effective_site_id ?? null;

  const vrfsQ = useQuery({
    queryKey: ["ipam", "vrfs", deviceSiteId ?? "none"],
    queryFn: () => ipamApi.listIpamVrfs(deviceSiteId!),
    enabled: deviceSiteId != null && deviceSiteId > 0,
  });
  const vrfInstQ = useQuery({
    queryKey: ["ipam", "vrf-instances", "device", id],
    queryFn: () => ipamApi.listVrfInstances({ deviceId: id }),
    enabled: Number.isFinite(id) && id > 0,
  });
  const prefixesQ = useQuery({
    queryKey: ["ipam", "ipv4-prefixes", deviceSiteId ?? "none"],
    queryFn: () => ipamApi.listIpv4Prefixes(deviceSiteId!),
    enabled: deviceSiteId != null && deviceSiteId > 0,
  });
  const prefixes6Q = useQuery({
    queryKey: ["ipam", "ipv6-prefixes", deviceSiteId ?? "none"],
    queryFn: () => ipamApi.listIpv6Prefixes(deviceSiteId!),
    enabled: deviceSiteId != null && deviceSiteId > 0,
  });
  const vlansQ = useQuery({
    queryKey: ["ipam", "vlans", deviceSiteId ?? "none"],
    queryFn: () => ipamApi.listIpamVlans(deviceSiteId!),
    enabled: deviceSiteId != null && deviceSiteId > 0,
  });

  const prefixById = useMemo(() => {
    const m = new Map<number, string>();
    for (const p of prefixesQ.data ?? []) m.set(p.id, p.cidr);
    return m;
  }, [prefixesQ.data]);
  const prefix6ById = useMemo(() => {
    const m = new Map<number, string>();
    for (const p of prefixes6Q.data ?? []) m.set(p.id, p.cidr);
    return m;
  }, [prefixes6Q.data]);

  const ifaceDepthById = useMemo(
    () => interfaceDepthByInterfaceList(interfacesQ.data ?? []),
    [interfacesQ.data],
  );

  const ifaceDescendantIds = useMemo(() => {
    const rows = interfacesQ.data ?? [];
    const byParent = new Map<number | null, number[]>();
    for (const r of rows) {
      const p = r.parent_interface_id ?? null;
      const arr = byParent.get(p) ?? [];
      arr.push(r.id);
      byParent.set(p, arr);
    }
    const desc = new Map<number, Set<number>>();
    function collect(root: number): Set<number> {
      const s = new Set<number>();
      for (const c of byParent.get(root) ?? []) {
        s.add(c);
        for (const x of collect(c)) s.add(x);
      }
      return s;
    }
    for (const r of rows) {
      desc.set(r.id, collect(r.id));
    }
    return desc;
  }, [interfacesQ.data]);

  const ifaceIndentedLabel = (x: DeviceInterface) => interfaceIndentedName(x, ifaceDepthById);

  const typeLabel = useMemo(() => {
    const tid = deviceQ.data?.effective_device_type_id;
    if (tid == null) return null;
    const row = (typesQ.data ?? []).find((x) => x.id === tid);
    return row ? `${row.name} (${row.slug})` : `#${tid}`;
  }, [deviceQ.data?.effective_device_type_id, typesQ.data]);

  const modelLabel = useMemo(() => {
    const mid = deviceQ.data?.device_model_id;
    if (mid == null) return null;
    const row = (modelsQ.data ?? []).find((x) => x.id === mid);
    return row ? row.name : `#${mid}`;
  }, [deviceQ.data?.device_model_id, modelsQ.data]);

  const roleLabel = useMemo(() => {
    const rid = deviceQ.data?.device_role_id;
    if (rid == null) return null;
    const row = (rolesQ.data ?? []).find((x) => x.id === rid);
    return row ? `${row.name} (${row.kind})` : `#${rid}`;
  }, [deviceQ.data?.device_role_id, rolesQ.data]);

  const siteLabel = useMemo(() => {
    const sid = deviceQ.data?.effective_site_id;
    if (sid == null) return null;
    const row = (sitesQ.data ?? []).find((x) => x.id === sid);
    return row ? `${row.name} (#${sid})` : `#${sid}`;
  }, [deviceQ.data?.effective_site_id, sitesQ.data]);

  const snmpHostParam = searchParams.get("snmpHost")?.trim() ?? "";

  const defaultSnmpHost = useMemo(() => {
    if (snmpHostParam !== "") return snmpHostParam;
    const v4: { addr: string; primary: boolean }[] = [];
    for (const dip of deviceIpsQ.data ?? []) {
      if (dip.family === "ipv4") v4.push({ addr: dip.address, primary: dip.is_primary });
    }
    const rows = interfacesQ.data ?? [];
    for (const iface of rows) {
      for (const ip of iface.ip_assignments ?? []) {
        if (ip.family === "ipv4") v4.push({ addr: ip.address, primary: ip.is_primary });
      }
    }
    const prim = v4.find((x) => x.primary);
    return prim?.addr ?? v4[0]?.addr ?? "";
  }, [snmpHostParam, interfacesQ.data, deviceIpsQ.data]);

  const snmpHostSyncKey = useMemo(() => {
    const a = deviceQ.data?.attributes ?? {};
    return `${snmpHostParam}\u0000${interfacesQ.dataUpdatedAt}\u0000${deviceIpsQ.dataUpdatedAt}\u0000${strAttr(a.snmp_community_read)}\u0000${strAttr(a.snmp_community)}\u0000${strAttr(a.snmp_community_write)}`;
  }, [
    snmpHostParam,
    interfacesQ.dataUpdatedAt,
    deviceIpsQ.dataUpdatedAt,
    deviceQ.data?.attributes,
  ]);

  const snmpProbeRead = useMemo(() => {
    const a = deviceQ.data?.attributes ?? {};
    return strAttr(a.snmp_community_read) || strAttr(a.snmp_community) || "public";
  }, [deviceQ.data?.attributes]);

  const snmpProbeWrite = useMemo(() => {
    const a = deviceQ.data?.attributes ?? {};
    return strAttr(a.snmp_community_write);
  }, [deviceQ.data?.attributes]);

  const deviceTypeSlug = useMemo(() => {
    const tid = deviceQ.data?.effective_device_type_id;
    if (tid == null) return null;
    return (typesQ.data ?? []).find((x) => x.id === tid)?.slug ?? null;
  }, [deviceQ.data?.effective_device_type_id, typesQ.data]);

  const hwPlugins = useMemo(
    () => pluginsWithCapability(plugins, CAP_DCIM_DEVICE_HARDWARE_VIEW, deviceTypeSlug),
    [plugins, deviceTypeSlug],
  );

  const osPlugins = useMemo(
    () => pluginsWithCapability(plugins, CAP_DCIM_DEVICE_OS_VIEW, deviceTypeSlug),
    [plugins, deviceTypeSlug],
  );

  const primaryHwPlugin = hwPlugins[0];
  const primaryOsPlugin = osPlugins[0];

  const pluginHwPath =
    primaryHwPlugin?.api_route_prefix != null
      ? `${primaryHwPlugin.api_route_prefix}/devices/${id}/hardware`
      : null;
  const pluginOsPath =
    primaryOsPlugin?.api_route_prefix != null
      ? `${primaryOsPlugin.api_route_prefix}/devices/${id}/os`
      : null;

  const pluginHardwareQ = useQuery({
    queryKey: ["plugin", "device-hardware", primaryHwPlugin?.id, id],
    queryFn: () => apiGet<unknown>(pluginHwPath!),
    enabled:
      detailTab === "hardware" &&
      pluginHwPath != null &&
      Number.isFinite(id) &&
      id > 0,
  });

  const pluginOsQ = useQuery({
    queryKey: ["plugin", "device-os", primaryOsPlugin?.id, id],
    queryFn: () => apiGet<unknown>(pluginOsPath!),
    enabled: detailTab === "os" && pluginOsPath != null && Number.isFinite(id) && id > 0,
  });

  useEffect(() => {
    const d = deviceQ.data;
    if (!d) return;
    setTypeEdit(d.device_type_id != null ? String(d.device_type_id) : "");
    setRoleEdit(d.device_role_id != null ? String(d.device_role_id) : "");
    setSerialDraft(d.serial_number ?? "");
    setAssetDraft(d.asset_tag ?? "");
    const a = d.attributes ?? {};
    setIconUrlDraft(strAttr(a[DCIM_DEVICE_ICON_URL_ATTR]));
    const read = strAttr(a.snmp_community_read) || strAttr(a.snmp_community);
    setSnmpReadDraft(read !== "" ? read : "public");
    setSnmpWriteDraft(strAttr(a.snmp_community_write));
    setSnmpExtraDraft(formatSnmpExtra(a as Record<string, unknown>));
  }, [
    deviceQ.data?.id,
    deviceQ.data?.device_type_id,
    deviceQ.data?.device_role_id,
    deviceQ.data?.serial_number,
    deviceQ.data?.asset_tag,
    deviceQ.data?.attributes,
  ]);

  const typeDirty = useMemo(() => {
    const d = deviceQ.data;
    if (!d) return false;
    const next = typeEdit === "" ? null : Number(typeEdit);
    return d.device_type_id !== next;
  }, [deviceQ.data, typeEdit]);

  const patchDeviceType = useMutation({
    mutationFn: (device_type_id: number | null) => api.updateDevice(id, { device_type_id }),
    onSuccess: () => {
      setErr(null);
      void qc.invalidateQueries({ queryKey: ["dcim", "devices", id] });
      void qc.invalidateQueries({ queryKey: ["dcim", "devices"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const roleDirty = useMemo(() => {
    const d = deviceQ.data;
    if (!d) return false;
    const next = roleEdit === "" ? null : Number(roleEdit);
    return d.device_role_id !== next;
  }, [deviceQ.data, roleEdit]);

  const patchDeviceRole = useMutation({
    mutationFn: (device_role_id: number | null) => api.updateDevice(id, { device_role_id }),
    onSuccess: () => {
      setErr(null);
      void qc.invalidateQueries({ queryKey: ["dcim", "devices", id] });
      void qc.invalidateQueries({ queryKey: ["dcim", "devices"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });
  const recordArt = useMutation({
    mutationFn: () =>
      api.recordDeviceArtifact(id, { artifact_id: Number(artPick), intent: artIntent }),
    onSuccess: () => {
      setErr(null);
      setArtPick("");
      void qc.invalidateQueries({ queryKey: ["dcim", "devices", id, "artifacts"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });
  const delArtRec = useMutation({
    mutationFn: (rid: number) => api.deleteDeviceArtifactRecord(id, rid),
    onSuccess: () => {
      setErr(null);
      void qc.invalidateQueries({ queryKey: ["dcim", "devices", id, "artifacts"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });
  const assignBl = useMutation({
    mutationFn: () =>
      api.assignDeviceArtifactBaseline(id, { baseline_id: Number(blPick), intent: blIntent }),
    onSuccess: () => {
      setErr(null);
      setBlPick("");
      void qc.invalidateQueries({ queryKey: ["dcim", "devices", id, "artifact-baselines"] });
      void qc.invalidateQueries({ queryKey: ["dcim", "devices", id, "artifacts"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });
  const delBlAssign = useMutation({
    mutationFn: (aid: number) => api.deleteDeviceArtifactBaselineAssignment(id, aid),
    onSuccess: () => {
      setErr(null);
      void qc.invalidateQueries({ queryKey: ["dcim", "devices", id, "artifact-baselines"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });
  const recordVrf = useMutation({
    mutationFn: () =>
      ipamApi.createVrfInstance(Number(vrfPick), { device_id: id, intent: vrfIntent }),
    onSuccess: () => {
      setErr(null);
      setVrfPick("");
      void qc.invalidateQueries({ queryKey: ["ipam", "vrf-instances"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });
  const delVrfInst = useMutation({
    mutationFn: (instanceId: number) => ipamApi.deleteVrfInstance(instanceId),
    onSuccess: () => {
      setErr(null);
      void qc.invalidateQueries({ queryKey: ["ipam", "vrf-instances"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const patchIdentity = useMutation({
    mutationFn: () => {
      const prev = deviceQ.data?.attributes ?? {};
      const next: Record<string, unknown> = { ...prev };
      const u = iconUrlDraft.trim();
      if (u !== "") next[DCIM_DEVICE_ICON_URL_ATTR] = u;
      else delete next[DCIM_DEVICE_ICON_URL_ATTR];
      return api.updateDevice(id, {
        serial_number: serialDraft.trim() === "" ? null : serialDraft.trim(),
        asset_tag: assetDraft.trim() === "" ? null : assetDraft.trim(),
        attributes: next,
      });
    },
    onSuccess: () => {
      setErr(null);
      void qc.invalidateQueries({ queryKey: ["dcim", "devices", id] });
      void qc.invalidateQueries({ queryKey: ["dcim", "devices"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const patchSnmpAttrs = useMutation({
    mutationFn: () => {
      const prev = deviceQ.data?.attributes ?? {};
      const next: Record<string, unknown> = { ...prev };
      const r = snmpReadDraft.trim();
      if (r !== "") {
        next.snmp_community_read = r;
        next.snmp_community = r;
      } else {
        delete next.snmp_community_read;
        delete next.snmp_community;
      }
      const w = snmpWriteDraft.trim();
      if (w !== "") next.snmp_community_write = w;
      else delete next.snmp_community_write;
      const extras = snmpExtraDraft
        .split(",")
        .map((s) => s.trim())
        .filter((s) => s !== "");
      if (extras.length > 0) next.snmp_communities = extras;
      else delete next.snmp_communities;
      return api.updateDevice(id, { attributes: next });
    },
    onSuccess: () => {
      setErr(null);
      void qc.invalidateQueries({ queryKey: ["dcim", "devices", id] });
      void qc.invalidateQueries({ queryKey: ["dcim", "devices"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  useEffect(() => {
    const rows = interfacesQ.data;
    if (!rows?.length || ipIface !== "") return;
    setIpIface(String(rows[0].id));
  }, [interfacesQ.data, ipIface]);

  const createIf = useMutation({
    mutationFn: () => {
      const sp = ifSpeed.trim();
      const mtuS = ifMtu.trim();
      let speed_mbps: number | null = null;
      let mtu: number | null = null;
      if (sp !== "") {
        const n = Number(sp);
        if (!Number.isFinite(n) || n < 0) throw new Error(t("dcim.equip.if.badNumber"));
        speed_mbps = n;
      }
      if (mtuS !== "") {
        const n = Number(mtuS);
        if (!Number.isFinite(n) || n < 68 || n > 65535) throw new Error(t("dcim.equip.if.badMtu"));
        mtu = n;
      }
      const vlanS = ifVlan.trim();
      let vlan_id: number | null = null;
      if (vlanS !== "") {
        const n = Number(vlanS);
        if (!Number.isFinite(n) || !Number.isInteger(n) || n < 1 || n > 4094) {
          throw new Error(t("dcim.equip.if.badVlan"));
        }
        vlan_id = n;
      }
      return api.createDeviceInterface(id, {
        name: ifName.trim(),
        mac_address: ifMac.trim() === "" ? null : ifMac.trim(),
        speed_mbps,
        mtu,
        vlan_id,
        ipam_vlan_id: ifIpamVlan === "" ? null : Number(ifIpamVlan),
        ipam_vrf_id: ifIpamVrf === "" ? null : Number(ifIpamVrf),
        description: ifDesc.trim() === "" ? null : ifDesc.trim(),
        sort_order: Number(ifSort) || 0,
        parent_interface_id: ifParent === "" ? null : Number(ifParent),
      });
    },
    onSuccess: () => {
      setIfName("");
      setIfMac("");
      setIfSpeed("");
      setIfMtu("");
      setIfDesc("");
      setIfSort("0");
      setIfVlan("");
      setIfIpamVlan("");
      setIfIpamVrf("");
      setIfParent("");
      setErr(null);
      void qc.invalidateQueries({ queryKey: ["dcim", "devices", id, "interfaces"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const patchVlan = useMutation({
    mutationFn: ({ iid, vlan_id }: { iid: number; vlan_id: number | null }) =>
      api.updateDeviceInterface(id, iid, { vlan_id }),
    onSuccess: (_data, vars) => {
      setErr(null);
      setVlanDraft((prev) => {
        const next = { ...prev };
        delete next[vars.iid];
        return next;
      });
      void qc.invalidateQueries({ queryKey: ["dcim", "devices", id, "interfaces"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const patchIpamVlan = useMutation({
    mutationFn: ({ iid, ipam_vlan_id }: { iid: number; ipam_vlan_id: number | null }) =>
      api.updateDeviceInterface(id, iid, { ipam_vlan_id }),
    onSuccess: () => {
      setErr(null);
      void qc.invalidateQueries({ queryKey: ["dcim", "devices", id, "interfaces"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const patchIpamVrf = useMutation({
    mutationFn: ({ iid, ipam_vrf_id }: { iid: number; ipam_vrf_id: number | null }) =>
      api.updateDeviceInterface(id, iid, { ipam_vrf_id }),
    onSuccess: () => {
      setErr(null);
      void qc.invalidateQueries({ queryKey: ["dcim", "devices", id, "interfaces"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const patchParent = useMutation({
    mutationFn: ({ iid, parent_interface_id }: { iid: number; parent_interface_id: number | null }) =>
      api.updateDeviceInterface(id, iid, { parent_interface_id }),
    onSuccess: (_data, vars) => {
      setErr(null);
      setParentDraft((prev) => {
        const next = { ...prev };
        delete next[vars.iid];
        return next;
      });
      void qc.invalidateQueries({ queryKey: ["dcim", "devices", id, "interfaces"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const delIf = useMutation({
    mutationFn: (iid: number) => api.deleteDeviceInterface(id, iid),
    onSuccess: () => {
      setErr(null);
      void qc.invalidateQueries({ queryKey: ["dcim", "devices", id, "interfaces"] });
      void qc.invalidateQueries({ queryKey: ["dcim", "devices", id, "interface-lags"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const invalidateLags = () => {
    void qc.invalidateQueries({ queryKey: ["dcim", "devices", id, "interface-lags"] });
  };

  const createLag = useMutation({
    mutationFn: () => api.createDeviceInterfaceLag(id, { name: lagName.trim() }),
    onSuccess: () => {
      setLagName("");
      setErr(null);
      invalidateLags();
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const addLagMember = useMutation({
    mutationFn: () => api.addDeviceInterfaceLagMember(Number(lagId), Number(lagIfaceId)),
    onSuccess: () => {
      setLagIfaceId("");
      setErr(null);
      invalidateLags();
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const delLag = useMutation({
    mutationFn: (lid: number) => api.deleteDeviceInterfaceLag(lid),
    onSuccess: () => {
      setErr(null);
      invalidateLags();
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const delLagMember = useMutation({
    mutationFn: (mid: number) => api.deleteDeviceInterfaceLagMember(mid),
    onSuccess: () => {
      setErr(null);
      invalidateLags();
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const invalidateWg = () => {
    void qc.invalidateQueries({ queryKey: ["ipam", "wireguard-interfaces", id] });
  };

  const createWg = useMutation({
    mutationFn: () =>
      ipamApi.createWireGuardInterface({
        device_id: id,
        name: wgName.trim(),
        interface_id: wgDcimIface === "" ? null : Number(wgDcimIface),
        listen_port: wgListen.trim() === "" ? null : Number(wgListen),
        address: wgAddr.trim() === "" ? null : wgAddr.trim(),
        private_key_ref: wgPriv.trim() === "" ? null : wgPriv.trim(),
        tunnel_id: wgTunnelId === "" ? null : Number(wgTunnelId),
      }),
    onSuccess: () => {
      setWgName("");
      setWgListen("");
      setWgAddr("");
      setWgPriv("");
      setWgDcimIface("");
      setWgTunnelId("");
      setErr(null);
      invalidateWg();
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const addWgPeer = useMutation({
    mutationFn: () =>
      ipamApi.createWireGuardPeer(Number(wgPeerIface), {
        name: wgPeerName.trim(),
        public_key_ref: wgPeerKey.trim() === "" ? null : wgPeerKey.trim(),
        psk_ref: wgPeerPsk.trim() === "" ? null : wgPeerPsk.trim(),
        endpoint_host: wgPeerHost.trim() === "" ? null : wgPeerHost.trim(),
        endpoint_port: wgPeerPort.trim() === "" ? null : Number(wgPeerPort),
        allowed_ips:
          wgPeerAllowed.trim() === ""
            ? null
            : wgPeerAllowed.split(/[,\s]+/).map((x) => x.trim()).filter(Boolean),
      }),
    onSuccess: () => {
      setWgPeerName("");
      setWgPeerKey("");
      setWgPeerPsk("");
      setWgPeerHost("");
      setWgPeerPort("");
      setWgPeerAllowed("");
      setErr(null);
      invalidateWg();
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const delWg = useMutation({
    mutationFn: (wid: number) => ipamApi.deleteWireGuardInterface(wid),
    onSuccess: () => {
      setErr(null);
      invalidateWg();
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const delWgPeer = useMutation({
    mutationFn: (pid: number) => ipamApi.deleteWireGuardPeer(pid),
    onSuccess: () => {
      setErr(null);
      invalidateWg();
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const invalidateVlanMem = () => {
    void qc.invalidateQueries({ queryKey: ["dcim", "devices", id, "interface-vlans"] });
  };

  const addVlanMem = useMutation({
    mutationFn: () =>
      api.addDeviceInterfaceVlan(id, Number(vlanMemIfaceId), {
        ipam_vlan_id: Number(vlanMemVlanId),
        role: vlanMemRole === "" ? null : vlanMemRole,
      }),
    onSuccess: () => {
      setVlanMemVlanId("");
      setVlanMemRole("");
      setErr(null);
      invalidateVlanMem();
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const delVlanMem = useMutation({
    mutationFn: (mid: number) => api.deleteDeviceInterfaceVlan(mid),
    onSuccess: () => {
      setErr(null);
      invalidateVlanMem();
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const toggleIf = useMutation({
    mutationFn: ({ iid, enabled }: { iid: number; enabled: boolean }) =>
      api.updateDeviceInterface(id, iid, { enabled }),
    onSuccess: () => {
      setErr(null);
      void qc.invalidateQueries({ queryKey: ["dcim", "devices", id, "interfaces"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const createIp = useMutation({
    mutationFn: () => {
      const addr = ipAddr.trim();
      const body: { address: string; is_primary: boolean; ipv4_prefix_id?: number; ipv6_prefix_id?: number } = {
        address: addr,
        is_primary: ipPrimary,
      };
      if (looksIpv6(addr)) {
        if (ipPrefix6 !== "") body.ipv6_prefix_id = Number(ipPrefix6);
      } else if (ipPrefix !== "") {
        body.ipv4_prefix_id = Number(ipPrefix);
      }
      return api.createIfaceIpAssignment(id, Number(ipIface), body);
    },
    onSuccess: () => {
      setIpAddr("");
      setIpPrimary(false);
      setIpPrefix("");
      setIpPrefix6("");
      setErr(null);
      void qc.invalidateQueries({ queryKey: ["dcim", "devices", id, "interfaces"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const delIp = useMutation({
    mutationFn: ({ iid, aid }: { iid: number; aid: number }) =>
      api.deleteIfaceIpAssignment(id, iid, aid),
    onSuccess: () => {
      setErr(null);
      void qc.invalidateQueries({ queryKey: ["dcim", "devices", id, "interfaces"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const netDeleteBusy =
    delIf.isPending ||
    delIp.isPending ||
    delLag.isPending ||
    delLagMember.isPending ||
    delWg.isPending ||
    delWgPeer.isPending ||
    delVlanMem.isPending;
  const lags: DeviceInterfaceLag[] = lagsQ.data ?? [];
  const wgIfaces: IpamWireGuardInterface[] = wgQ.data ?? [];
  const lagTaken = new Set(lags.flatMap((b) => b.members.map((m) => m.interface_id)));
  const freeLagIfaces = (interfacesQ.data ?? []).filter((x) => !lagTaken.has(x.id));
  const vlanMembers: DeviceInterfaceVlanMember[] = vlanMemQ.data ?? [];

  const setPrimaryIp = useMutation({
    mutationFn: ({ iid, aid }: { iid: number; aid: number }) =>
      api.updateIfaceIpAssignment(id, iid, aid, { is_primary: true }),
    onSuccess: () => {
      setErr(null);
      void qc.invalidateQueries({ queryKey: ["dcim", "devices", id, "interfaces"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const createDevIp = useMutation({
    mutationFn: () => {
      const addr = devIpAddr.trim();
      const body: { address: string; is_primary: boolean; ipv4_prefix_id?: number; ipv6_prefix_id?: number } = {
        address: addr,
        is_primary: devIpPrimary,
      };
      if (looksIpv6(addr)) {
        if (devIpPrefix6 !== "") body.ipv6_prefix_id = Number(devIpPrefix6);
      } else if (devIpPrefix !== "") {
        body.ipv4_prefix_id = Number(devIpPrefix);
      }
      return api.createDeviceIpAssignment(id, body);
    },
    onSuccess: () => {
      setDevIpAddr("");
      setDevIpPrimary(false);
      setDevIpPrefix("");
      setDevIpPrefix6("");
      setErr(null);
      void qc.invalidateQueries({ queryKey: ["dcim", "devices", id, "device-ip-assignments"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const delDevIp = useMutation({
    mutationFn: (aid: number) => api.deleteDeviceIpAssignment(id, aid),
    onSuccess: () => {
      setErr(null);
      void qc.invalidateQueries({ queryKey: ["dcim", "devices", id, "device-ip-assignments"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const setPrimaryDevIp = useMutation({
    mutationFn: (aid: number) => api.updateDeviceIpAssignment(id, aid, { is_primary: true }),
    onSuccess: () => {
      setErr(null);
      void qc.invalidateQueries({ queryKey: ["dcim", "devices", id, "device-ip-assignments"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const patchDevIpPrefix = useMutation({
    mutationFn: ({
      aid,
      ipv4_prefix_id,
      ipv6_prefix_id,
    }: {
      aid: number;
      ipv4_prefix_id?: number | null;
      ipv6_prefix_id?: number | null;
    }) => api.updateDeviceIpAssignment(id, aid, { ipv4_prefix_id, ipv6_prefix_id }),
    onSuccess: (_d, vars) => {
      setErr(null);
      setDevIpPrefixDraft((prev) => {
        const next = { ...prev };
        delete next[vars.aid];
        return next;
      });
      setDevIpPrefix6Draft((prev) => {
        const next = { ...prev };
        delete next[vars.aid];
        return next;
      });
      void qc.invalidateQueries({ queryKey: ["dcim", "devices", id, "device-ip-assignments"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const patchIpPrefix = useMutation({
    mutationFn: ({
      iid,
      aid,
      ipv4_prefix_id,
      ipv6_prefix_id,
    }: {
      iid: number;
      aid: number;
      ipv4_prefix_id?: number | null;
      ipv6_prefix_id?: number | null;
    }) => api.updateIfaceIpAssignment(id, iid, aid, { ipv4_prefix_id, ipv6_prefix_id }),
    onSuccess: (_d, vars) => {
      setErr(null);
      setIpPrefixDraft((prev) => {
        const next = { ...prev };
        delete next[vars.aid];
        return next;
      });
      setIpPrefix6Draft((prev) => {
        const next = { ...prev };
        delete next[vars.aid];
        return next;
      });
      void qc.invalidateQueries({ queryKey: ["dcim", "devices", id, "interfaces"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  if (!Number.isFinite(id) || id < 1) {
    return (
      <Panel title={t("dcim.equip.dev.detailTitle")}>
        <p className={styles.err}>{t("dcim.equip.dev.invalidId")}</p>
        <Link to={backToDevices} className={styles.tableLink}>
          {t("dcim.equip.dev.backToList")}
        </Link>
      </Panel>
    );
  }

  if (deviceQ.isError) {
    return (
      <Panel title={t("dcim.equip.dev.detailTitle")}>
        <p className={styles.err}>{(deviceQ.error as Error).message}</p>
        <Link to={backToDevices} className={styles.tableLink}>
          {t("dcim.equip.dev.backToList")}
        </Link>
      </Panel>
    );
  }

  if (deviceQ.isLoading || !deviceQ.data) {
    return (
      <Panel title={t("dcim.equip.dev.detailTitle")}>
        <p className={styles.muted}>{t("dcim.common.loading")}</p>
      </Panel>
    );
  }

  const dev = deviceQ.data;
  const attrs = dev.attributes;
  const hasAttrs = attrs && Object.keys(attrs).length > 0;

  return (
    <>
      <p className={styles.mfrDetailBack}>
        <Link to={backToDevices} className={styles.tableLink}>
          ← {t("dcim.equip.dev.backToList")}
        </Link>
      </p>

      <Panel title={dev.name}>
        {err ? <p className={styles.err}>{err}</p> : null}
        <DcimInnerTabs
          tabs={[
            { id: "overview", label: t("dcim.equip.dev.tabOverview"), icon: "overview" },
            { id: "network", label: t("dcim.equip.dev.tabNetwork"), icon: "deviceNetwork" },
            { id: "hardware", label: t("dcim.equip.dev.tabHardware"), icon: "deviceHardware" },
            { id: "os", label: t("dcim.equip.dev.tabOs"), icon: "deviceOs" },
          ]}
          activeId={detailTab}
          onChange={setDetailTab}
          ariaLabel={t("dcim.equip.dev.detailTabsAria")}
        />

        {detailTab === "overview" ? (
          <>
            <p className={styles.muted} style={{ marginTop: 0 }}>
              {t("dcim.equip.dev.classificationNote")}
            </p>
            <p>
              <Link to={catalogProvisionHref(dev.id)} className={styles.tableLink}>
                {t("catalog.provision")}
              </Link>
              <span className={styles.muted}> — {t("catalog.provisionHint")}</span>
            </p>
            <dl className={styles.dlInline}>
              <dt>{t("dcim.common.id")}</dt>
              <dd>{dev.id}</dd>
              <dt>{t("dcim.equip.dev.modelCol")}</dt>
              <dd>{modelLabel ?? "—"}</dd>
              <dt>{t("dcim.equip.dev.effectiveTypeCol")}</dt>
              <dd>{typeLabel ?? "—"}</dd>
              <dt>{t("dcim.equip.dev.roleCol")}</dt>
              <dd>{roleLabel ?? "—"}</dd>
              <dt>{t("dcim.equip.dev.siteCol")}</dt>
              <dd>{siteLabel ?? "—"}</dd>
            </dl>
            <section className={styles.mfrDetailSection}>
              <h3 className={styles.mfrDetailSectionTitle}>{t("dcim.equip.dev.identityTitle")}</h3>
              <div className={styles.formRow}>
                <label>
                  {t("dcim.equip.dev.serial")}
                  <input value={serialDraft} onChange={(e) => setSerialDraft(e.target.value)} />
                </label>
                <label>
                  {t("dcim.equip.dev.assetTag")}
                  <input value={assetDraft} onChange={(e) => setAssetDraft(e.target.value)} />
                </label>
                <label style={{ flex: "1 1 18rem" }} title={t("dcim.equip.dev.iconUrlHint")}>
                  {t("dcim.equip.dev.iconUrl")}
                  <input
                    type="url"
                    value={iconUrlDraft}
                    onChange={(e) => setIconUrlDraft(e.target.value)}
                    placeholder="https://"
                  />
                </label>
                <button
                  type="button"
                  className={styles.btn}
                  disabled={patchIdentity.isPending}
                  onClick={() => {
                    setErr(null);
                    patchIdentity.mutate();
                  }}
                >
                  {patchIdentity.isPending ? "…" : t("dcim.equip.dev.identitySave")}
                </button>
              </div>
            </section>
            <section className={styles.mfrDetailSection}>
              <h3 className={styles.mfrDetailSectionTitle}>{t("dcim.equip.dev.snmpCommunitiesTitle")}</h3>
              <p className={styles.muted} style={{ marginTop: 0 }}>
                {t("dcim.equip.dev.snmpPersistHint")}
              </p>
              <div className={styles.formRow}>
                <label>
                  {t("dcim.equip.dev.snmpRead")}
                  <input value={snmpReadDraft} onChange={(e) => setSnmpReadDraft(e.target.value)} autoComplete="off" />
                </label>
                <label>
                  {t("dcim.equip.dev.snmpWrite")}
                  <input value={snmpWriteDraft} onChange={(e) => setSnmpWriteDraft(e.target.value)} autoComplete="off" />
                </label>
                <label style={{ flex: "1 1 14rem" }}>
                  {t("dcim.equip.dev.snmpExtra")}
                  <input
                    value={snmpExtraDraft}
                    onChange={(e) => setSnmpExtraDraft(e.target.value)}
                    placeholder="public, network"
                    autoComplete="off"
                  />
                </label>
                <button
                  type="button"
                  className={styles.btn}
                  disabled={patchSnmpAttrs.isPending}
                  onClick={() => {
                    setErr(null);
                    patchSnmpAttrs.mutate();
                  }}
                >
                  {patchSnmpAttrs.isPending ? "…" : t("dcim.equip.dev.snmpSave")}
                </button>
              </div>
            </section>
            <section className={styles.mfrDetailSection}>
              <h3 className={styles.mfrDetailSectionTitle}>{t("dcim.equip.dev.typeOverrideLabel")}</h3>
              <div className={styles.formRow}>
                <label>
                  {t("dcim.equip.dev.effectiveTypeCol")}
                  <select value={typeEdit} onChange={(e) => setTypeEdit(e.target.value)}>
                    <option value="">{t("dcim.equip.dev.typeInheritModel")}</option>
                    {(typesQ.data ?? []).map((x) => (
                      <option key={x.id} value={String(x.id)}>
                        {x.name} ({x.slug})
                      </option>
                    ))}
                  </select>
                </label>
                <button
                  type="button"
                  className={styles.btn}
                  disabled={!typeDirty || patchDeviceType.isPending || typesQ.isLoading}
                  onClick={() => {
                    setErr(null);
                    const next = typeEdit === "" ? null : Number(typeEdit);
                    patchDeviceType.mutate(next);
                  }}
                >
                  {patchDeviceType.isPending ? "…" : t("dcim.equip.dev.typeSave")}
                </button>
              </div>
            </section>
            <section className={styles.mfrDetailSection}>
              <h3 className={styles.mfrDetailSectionTitle}>{t("dcim.equip.dev.roleSection")}</h3>
              <p className={styles.muted} style={{ marginTop: 0 }}>
                {t("dcim.equip.role.hint")}
              </p>
              <div className={styles.formRow}>
                <label>
                  {t("dcim.equip.dev.roleLabel")}
                  <select value={roleEdit} onChange={(e) => setRoleEdit(e.target.value)}>
                    <option value="">{t("dcim.equip.dev.roleNone")}</option>
                    {(rolesQ.data ?? []).map((x) => (
                      <option key={x.id} value={String(x.id)}>
                        {x.name} ({x.kind})
                      </option>
                    ))}
                  </select>
                </label>
                <button
                  type="button"
                  className={styles.btn}
                  disabled={!roleDirty || patchDeviceRole.isPending || rolesQ.isLoading}
                  onClick={() => {
                    setErr(null);
                    const next = roleEdit === "" ? null : Number(roleEdit);
                    patchDeviceRole.mutate(next);
                  }}
                >
                  {patchDeviceRole.isPending ? "…" : t("dcim.equip.dev.roleSave")}
                </button>
              </div>
            </section>
            <section className={styles.mfrDetailSection}>
              <h3 className={styles.mfrDetailSectionTitle}>{t("dcim.equip.artifact.title")}</h3>
              <p className={styles.muted} style={{ marginTop: 0 }}>
                {t("dcim.equip.artifact.hint")}
              </p>
              <div className={styles.formRow}>
                <label>
                  {t("dcim.equip.artifact.title")}
                  <select value={artPick} onChange={(e) => setArtPick(e.target.value)}>
                    <option value="">{t("dcim.equip.artifact.pick")}</option>
                    {(artifactsQ.data ?? []).map((x) => (
                      <option key={x.id} value={String(x.id)}>
                        {x.name} {x.version}
                      </option>
                    ))}
                  </select>
                </label>
                <label>
                  {t("dcim.equip.artifact.intent")}
                  <select value={artIntent} onChange={(e) => setArtIntent(e.target.value as "recorded" | "intended")}>
                    <option value="recorded">{t("dcim.equip.artifact.intentRecorded")}</option>
                    <option value="intended">{t("dcim.equip.artifact.intentIntended")}</option>
                  </select>
                </label>
                <button
                  type="button"
                  className={styles.btn}
                  disabled={!artPick || recordArt.isPending}
                  onClick={() => {
                    setErr(null);
                    recordArt.mutate();
                  }}
                >
                  {recordArt.isPending ? "…" : t("dcim.common.add")}
                </button>
              </div>
              {(artifactRecQ.data ?? []).length > 0 ? (
                <ul style={{ margin: "0.5rem 0 0", paddingLeft: "1.25rem" }}>
                  {(artifactRecQ.data ?? []).map((r) => (
                    <li key={r.id}>
                      {r.artifact ? `${r.artifact.name} ${r.artifact.version}` : `#${r.artifact_id}`}{" "}
                      ({r.intent}){" "}
                      <button
                        type="button"
                        className={styles.tableIconBtn}
                        onClick={() => delArtRec.mutate(r.id)}
                        disabled={delArtRec.isPending}
                      >
                        {t("dcim.common.remove")}
                      </button>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className={styles.muted}>{t("dcim.equip.artifact.deviceEmpty")}</p>
              )}
            </section>
            <section className={styles.mfrDetailSection}>
              <h3 className={styles.mfrDetailSectionTitle}>{t("dcim.equip.baseline.assignTitle")}</h3>
              <p className={styles.muted} style={{ marginTop: 0 }}>
                {t("dcim.equip.baseline.assignHint")}
              </p>
              <div className={styles.formRow}>
                <label>
                  {t("dcim.equip.baseline.pick")}
                  <select value={blPick} onChange={(e) => setBlPick(e.target.value)}>
                    <option value="">{t("dcim.equip.baseline.choose")}</option>
                    {(baselinesQ.data ?? []).map((b) => (
                      <option key={b.id} value={String(b.id)}>
                        {b.name} ({b.kind})
                      </option>
                    ))}
                  </select>
                </label>
                <label>
                  {t("dcim.equip.artifact.intent")}
                  <select value={blIntent} onChange={(e) => setBlIntent(e.target.value as "recorded" | "intended")}>
                    <option value="recorded">{t("dcim.equip.artifact.intentRecorded")}</option>
                    <option value="intended">{t("dcim.equip.artifact.intentIntended")}</option>
                  </select>
                </label>
                <button
                  type="button"
                  className={styles.btn}
                  disabled={!blPick || assignBl.isPending}
                  onClick={() => {
                    setErr(null);
                    assignBl.mutate();
                  }}
                >
                  {assignBl.isPending ? "…" : t("dcim.equip.baseline.assignAdd")}
                </button>
              </div>
              {(blAssignQ.data ?? []).length > 0 ? (
                <ul style={{ margin: "0.5rem 0 0", paddingLeft: "1.25rem" }}>
                  {(blAssignQ.data ?? []).map((r) => (
                    <li key={r.id}>
                      {r.baseline_name ?? r.baseline_slug ?? `#${r.baseline_id}`}
                      {r.baseline_kind ? ` (${r.baseline_kind})` : ""} ({r.intent}){" "}
                      <button
                        type="button"
                        className={styles.tableIconBtn}
                        onClick={() => delBlAssign.mutate(r.id)}
                        disabled={delBlAssign.isPending}
                      >
                        {t("dcim.common.remove")}
                      </button>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className={styles.muted}>{t("dcim.equip.baseline.assignEmpty")}</p>
              )}
            </section>
            <section className={styles.mfrDetailSection}>
              <h3 className={styles.mfrDetailSectionTitle}>{t("dcim.equip.dev.vrfSection")}</h3>
              <p className={styles.muted} style={{ marginTop: 0 }}>
                {t("dcim.equip.dev.vrfHint")}
              </p>
              <div className={styles.formRow}>
                <label>
                  VRF
                  <select value={vrfPick} onChange={(e) => setVrfPick(e.target.value)}>
                    <option value="">{t("ipam.vrf.chooseVrf")}</option>
                    {(vrfsQ.data ?? []).map((x) => (
                      <option key={x.id} value={String(x.id)}>
                        {x.name}
                      </option>
                    ))}
                  </select>
                </label>
                <label>
                  {t("ipam.vrf.instanceIntent")}
                  <select value={vrfIntent} onChange={(e) => setVrfIntent(e.target.value as "recorded" | "intended")}>
                    <option value="recorded">{t("ipam.vrf.intentRecorded")}</option>
                    <option value="intended">{t("ipam.vrf.intentIntended")}</option>
                  </select>
                </label>
                <button
                  type="button"
                  className={styles.btn}
                  disabled={!vrfPick || recordVrf.isPending}
                  onClick={() => {
                    setErr(null);
                    recordVrf.mutate();
                  }}
                >
                  {recordVrf.isPending ? "…" : t("dcim.common.add")}
                </button>
              </div>
              {(vrfInstQ.data ?? []).length > 0 ? (
                <ul style={{ margin: "0.5rem 0 0", paddingLeft: "1.25rem" }}>
                  {(vrfInstQ.data ?? []).map((r) => (
                    <li key={r.id}>
                      {r.vrf_name}
                      {r.effective_rd ? ` · ${r.effective_rd}` : ""} ({r.intent}){" "}
                      <button
                        type="button"
                        className={styles.tableIconBtn}
                        onClick={() => delVrfInst.mutate(r.id)}
                        disabled={delVrfInst.isPending}
                      >
                        {t("dcim.common.remove")}
                      </button>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className={styles.muted}>{t("ipam.vrf.instanceEmpty")}</p>
              )}
            </section>
            {hasAttrs ? (
              <section className={styles.mfrDetailSection}>
                <h3 className={styles.mfrDetailSectionTitle}>{t("dcim.equip.dev.attributesBlock")}</h3>
                <pre className={styles.codeBlock}>{JSON.stringify(attrs, null, 2)}</pre>
              </section>
            ) : null}
          </>
        ) : null}

        {detailTab === "hardware" ? (
          <>
            <DcimOwnerComponentsPanel
              ownerKind="device"
              ownerId={id}
              canCopyFromModel={dev.device_model_id != null}
              onError={setErr}
            />
            <DevicePortsCablesPanel
              deviceId={id}
              siteId={dev.site_id ?? dev.effective_site_id}
              canCopyFromModel={dev.device_model_id != null}
              onError={setErr}
            />
            <section className={styles.mfrDetailSection}>
              {hwPlugins.length > 0 ? (
                <p className={styles.muted} style={{ marginTop: 0 }}>
                  {t("dcim.equip.dev.pluginHardwareIntegrationsPrefix")}{" "}
                  <strong>{hwPlugins.map((p) => p.name).join(", ")}</strong>.{" "}
                  {t("dcim.equip.dev.pluginHardwareIntegrationsSuffix")}
                </p>
              ) : null}
              <p
                className={styles.muted}
                style={{ marginTop: hwPlugins.length > 0 ? "var(--space-3)" : 0 }}
              >
                {t("dcim.equip.dev.pluginPlaceholderHardware")}
              </p>
              {pluginHwPath != null ? (
                <>
                  <h4 className={styles.mfrDetailSectionTitle} style={{ marginTop: "var(--space-4)" }}>
                    {primaryHwPlugin?.name ?? t("dcim.equip.dev.pluginPanelDataTitle")}
                  </h4>
                  {pluginHardwareQ.isLoading ? (
                    <p className={styles.muted}>{t("dcim.common.loading")}</p>
                  ) : null}
                  {pluginHardwareQ.isError ? (
                    <p className={styles.err}>{(pluginHardwareQ.error as Error).message}</p>
                  ) : null}
                  {pluginHardwareQ.data != null ? (
                    <pre className={styles.codeBlock}>
                      {JSON.stringify(pluginHardwareQ.data, null, 2)}
                    </pre>
                  ) : null}
                </>
              ) : null}
            </section>
          </>
        ) : null}

        {detailTab === "os" ? (
          <section className={styles.mfrDetailSection}>
            {osPlugins.length > 0 ? (
              <p className={styles.muted} style={{ marginTop: 0 }}>
                {t("dcim.equip.dev.pluginOsIntegrationsPrefix")}{" "}
                <strong>{osPlugins.map((p) => p.name).join(", ")}</strong>.{" "}
                {t("dcim.equip.dev.pluginOsIntegrationsSuffix")}
              </p>
            ) : null}
            <p
              className={styles.muted}
              style={{ marginTop: osPlugins.length > 0 ? "var(--space-3)" : 0 }}
            >
              {t("dcim.equip.dev.pluginPlaceholderOs")}
            </p>
            {pluginOsPath != null ? (
              <>
                <h4 className={styles.mfrDetailSectionTitle} style={{ marginTop: "var(--space-4)" }}>
                  {primaryOsPlugin?.name ?? t("dcim.equip.dev.pluginPanelDataTitle")}
                </h4>
                {pluginOsQ.isLoading ? (
                  <p className={styles.muted}>{t("dcim.common.loading")}</p>
                ) : null}
                {pluginOsQ.isError ? (
                  <p className={styles.err}>{(pluginOsQ.error as Error).message}</p>
                ) : null}
                {pluginOsQ.data != null ? (
                  <pre className={styles.codeBlock}>{JSON.stringify(pluginOsQ.data, null, 2)}</pre>
                ) : null}
              </>
            ) : null}
          </section>
        ) : null}

        {detailTab === "network" ? (
          <>
            <SnmpInventoryPanel
              mode="fixed_device"
              deviceId={id}
              initialHost={defaultSnmpHost}
              initialCommunity={snmpProbeRead}
              initialCommunityWrite={snmpProbeWrite}
              hostSyncKey={snmpHostSyncKey}
            />
            <h3 className={styles.mfrDetailSectionTitle}>{t("dcim.equip.ip.deviceTitle")}</h3>
            <p className={styles.muted} style={{ marginTop: 0 }}>
              {t("dcim.equip.ip.deviceHint")}
            </p>
            {deviceSiteId == null ? (
              <p className={styles.muted}>{t("dcim.equip.ip.prefixNeedsSite")}</p>
            ) : null}
            <form
              className={styles.formRow}
              onSubmit={(e) => {
                e.preventDefault();
                setErr(null);
                createDevIp.mutate();
              }}
            >
              <label>
                {t("dcim.equip.ip.address")}
                <input
                  value={devIpAddr}
                  onChange={(e) => setDevIpAddr(e.target.value)}
                  placeholder="192.168.1.1"
                  required
                />
              </label>
              {deviceSiteId != null ? (
                <>
                  <label>
                    {t("dcim.equip.ip.ipv4Prefix")}
                    <select value={devIpPrefix} onChange={(e) => setDevIpPrefix(e.target.value)}>
                      <option value="">{t("dcim.equip.ip.ipv4PrefixNone")}</option>
                      {(prefixesQ.data ?? []).map((p) => (
                        <option key={p.id} value={String(p.id)}>
                          {p.name} — {p.cidr}
                        </option>
                      ))}
                    </select>
                  </label>
                  <label>
                    {t("dcim.equip.ip.ipv6Prefix")}
                    <select value={devIpPrefix6} onChange={(e) => setDevIpPrefix6(e.target.value)}>
                      <option value="">{t("dcim.equip.ip.ipv6PrefixNone")}</option>
                      {(prefixes6Q.data ?? []).map((p) => (
                        <option key={p.id} value={String(p.id)}>
                          {p.name} — {p.cidr}
                        </option>
                      ))}
                    </select>
                  </label>
                </>
              ) : null}
              <label style={{ flexDirection: "row", alignItems: "center", gap: "0.5rem" }}>
                <input
                  type="checkbox"
                  checked={devIpPrimary}
                  onChange={(e) => setDevIpPrimary(e.target.checked)}
                />
                {t("dcim.equip.ip.primary")}
              </label>
              <button type="submit" className={styles.btn} disabled={createDevIp.isPending}>
                {createDevIp.isPending ? "…" : t("dcim.equip.ip.add")}
              </button>
            </form>
            {deviceIpsQ.data != null && deviceIpsQ.data.length > 0 ? (
              <ul className={styles.ipList} style={{ marginTop: "var(--space-2)" }}>
                {deviceIpsQ.data.map((ip: DeviceIpAssignment) => (
                  <li key={ip.id}>
                    <code>{ip.address}</code>{" "}
                    <span className={styles.muted}>({ip.family})</span>
                    {ip.family === "ipv4" && ip.ipv4_prefix_id != null ? (
                      <span className={styles.muted}>
                        {" "}
                        · {prefixById.get(ip.ipv4_prefix_id) ?? `#${ip.ipv4_prefix_id}`}
                      </span>
                    ) : null}
                    {ip.family === "ipv6" && ip.ipv6_prefix_id != null ? (
                      <span className={styles.muted}>
                        {" "}
                        · {prefix6ById.get(ip.ipv6_prefix_id) ?? `#${ip.ipv6_prefix_id}`}
                      </span>
                    ) : null}
                    {ip.family === "ipv4" && deviceSiteId != null ? (
                      <span
                        style={{
                          display: "inline-flex",
                          flexWrap: "wrap",
                          gap: "0.25rem",
                          alignItems: "center",
                          marginLeft: "0.35rem",
                        }}
                      >
                        <select
                          style={{ maxWidth: "14rem", fontSize: "var(--text-xs)" }}
                          value={
                            devIpPrefixDraft[ip.id] ??
                            (ip.ipv4_prefix_id != null ? String(ip.ipv4_prefix_id) : "")
                          }
                          onChange={(e) =>
                            setDevIpPrefixDraft((prev) => ({ ...prev, [ip.id]: e.target.value }))
                          }
                          title={t("dcim.equip.ip.ipv4Prefix")}
                        >
                          <option value="">{t("dcim.equip.ip.ipv4PrefixNone")}</option>
                          {(prefixesQ.data ?? []).map((p) => (
                            <option key={p.id} value={String(p.id)}>
                              {p.name} — {p.cidr}
                            </option>
                          ))}
                        </select>
                        <button
                          type="button"
                          className={styles.btn}
                          style={{ fontSize: "var(--text-xs)", padding: "0.15rem 0.45rem" }}
                          disabled={patchDevIpPrefix.isPending}
                          onClick={() => {
                            setErr(null);
                            const raw = (
                              devIpPrefixDraft[ip.id] ??
                              (ip.ipv4_prefix_id != null ? String(ip.ipv4_prefix_id) : "")
                            ).trim();
                            let ipv4_prefix_id: number | null = null;
                            if (raw !== "") {
                              const n = Number(raw);
                              if (!Number.isFinite(n)) return;
                              ipv4_prefix_id = n;
                            }
                            patchDevIpPrefix.mutate({ aid: ip.id, ipv4_prefix_id });
                          }}
                        >
                          {patchDevIpPrefix.isPending ? "…" : t("dcim.common.save")}
                        </button>
                      </span>
                    ) : null}
                    {ip.family === "ipv6" && deviceSiteId != null ? (
                      <span
                        style={{
                          display: "inline-flex",
                          flexWrap: "wrap",
                          gap: "0.25rem",
                          alignItems: "center",
                          marginLeft: "0.35rem",
                        }}
                      >
                        <select
                          style={{ maxWidth: "14rem", fontSize: "var(--text-xs)" }}
                          value={
                            devIpPrefix6Draft[ip.id] ??
                            (ip.ipv6_prefix_id != null ? String(ip.ipv6_prefix_id) : "")
                          }
                          onChange={(e) =>
                            setDevIpPrefix6Draft((prev) => ({ ...prev, [ip.id]: e.target.value }))
                          }
                          title={t("dcim.equip.ip.ipv6Prefix")}
                        >
                          <option value="">{t("dcim.equip.ip.ipv6PrefixNone")}</option>
                          {(prefixes6Q.data ?? []).map((p) => (
                            <option key={p.id} value={String(p.id)}>
                              {p.name} — {p.cidr}
                            </option>
                          ))}
                        </select>
                        <button
                          type="button"
                          className={styles.btn}
                          style={{ fontSize: "var(--text-xs)", padding: "0.15rem 0.45rem" }}
                          disabled={patchDevIpPrefix.isPending}
                          onClick={() => {
                            setErr(null);
                            const raw = (
                              devIpPrefix6Draft[ip.id] ??
                              (ip.ipv6_prefix_id != null ? String(ip.ipv6_prefix_id) : "")
                            ).trim();
                            let ipv6_prefix_id: number | null = null;
                            if (raw !== "") {
                              const n = Number(raw);
                              if (!Number.isFinite(n)) return;
                              ipv6_prefix_id = n;
                            }
                            patchDevIpPrefix.mutate({ aid: ip.id, ipv6_prefix_id });
                          }}
                        >
                          {patchDevIpPrefix.isPending ? "…" : t("dcim.common.save")}
                        </button>
                      </span>
                    ) : null}
                    {ip.is_primary ? (
                      <span className={styles.ipPrimaryMark}> {t("dcim.equip.ip.primaryMark")}</span>
                    ) : (
                      <button
                        type="button"
                        className={styles.btnLink}
                        onClick={() => setPrimaryDevIp.mutate(ip.id)}
                        disabled={setPrimaryDevIp.isPending}
                      >
                        {t("dcim.equip.ip.setPrimary")}
                      </button>
                    )}{" "}
                    <button
                      type="button"
                      className={styles.btnDanger}
                      style={{ fontSize: "var(--text-xs)", padding: "0.1rem 0.4rem" }}
                      onClick={() => delDevIp.mutate(ip.id)}
                      disabled={delDevIp.isPending}
                    >
                      {t("dcim.common.remove")}
                    </button>
                  </li>
                ))}
              </ul>
            ) : null}
            <h3 className={styles.mfrDetailSectionTitle}>{t("dcim.equip.if.title")}</h3>
            <p className={styles.muted} style={{ marginTop: 0 }}>
              {t("dcim.equip.if.hint")}
            </p>
        <form
          className={styles.formRow}
          onSubmit={(e) => {
            e.preventDefault();
            setErr(null);
            createIf.mutate();
          }}
        >
          <label>
            {t("dcim.equip.if.name")}
            <input value={ifName} onChange={(e) => setIfName(e.target.value)} required />
          </label>
          <label>
            {t("dcim.equip.if.parent")}
            <select value={ifParent} onChange={(e) => setIfParent(e.target.value)}>
              <option value="">{t("dcim.equip.if.parentRoot")}</option>
              {(interfacesQ.data ?? []).map((x) => (
                <option key={x.id} value={String(x.id)}>
                  {ifaceIndentedLabel(x)}
                </option>
              ))}
            </select>
          </label>
          <label>
            {t("dcim.equip.if.mac")}
            <input value={ifMac} onChange={(e) => setIfMac(e.target.value)} placeholder="aa:bb:cc:dd:ee:ff" />
          </label>
          <label>
            {t("dcim.equip.if.speed")}
            <input
              type="number"
              min={0}
              value={ifSpeed}
              onChange={(e) => setIfSpeed(e.target.value)}
              placeholder="1000"
            />
          </label>
          <label>
            {t("dcim.equip.if.mtu")}
            <input type="number" min={68} max={65535} value={ifMtu} onChange={(e) => setIfMtu(e.target.value)} />
          </label>
          <label>
            {t("dcim.equip.if.vlan")}
            <input
              type="number"
              min={1}
              max={4094}
              value={ifVlan}
              onChange={(e) => setIfVlan(e.target.value)}
              placeholder="100"
              title={t("dcim.equip.if.vlanHint")}
            />
          </label>
          <label title={t("dcim.equip.if.ipamVlanHint")}>
            {t("dcim.equip.if.ipamVlan")}
            {deviceSiteId == null ? (
              <span className={styles.muted}>{t("dcim.equip.if.ipamVlanNeedsSite")}</span>
            ) : (
              <select value={ifIpamVlan} onChange={(e) => setIfIpamVlan(e.target.value)}>
                <option value="">{t("dcim.equip.if.ipamVlanNone")}</option>
                {(vlansQ.data ?? []).map((v) => (
                  <option key={v.id} value={String(v.id)}>
                    {v.vid} {v.name}
                  </option>
                ))}
              </select>
            )}
          </label>
          <label title={t("dcim.equip.if.ipamVrfHint")}>
            {t("dcim.equip.if.ipamVrf")}
            {deviceSiteId == null ? (
              <span className={styles.muted}>{t("dcim.equip.if.ipamVrfNeedsSite")}</span>
            ) : (
              <select value={ifIpamVrf} onChange={(e) => setIfIpamVrf(e.target.value)}>
                <option value="">{t("dcim.equip.if.ipamVrfNone")}</option>
                {(vrfsQ.data ?? []).map((v) => (
                  <option key={v.id} value={String(v.id)}>
                    {v.name} ({v.slug})
                  </option>
                ))}
              </select>
            )}
          </label>
          <label>
            {t("dcim.equip.mfr.description")}
            <input value={ifDesc} onChange={(e) => setIfDesc(e.target.value)} />
          </label>
          <label>
            {t("dcim.equip.if.sort")}
            <input type="number" value={ifSort} onChange={(e) => setIfSort(e.target.value)} />
          </label>
          <button type="submit" className={styles.btn} disabled={createIf.isPending}>
            {createIf.isPending ? "…" : t("dcim.common.add")}
          </button>
        </form>

        {interfacesQ.data && interfacesQ.data.length > 0 ? (
          <>
            <h3 className={styles.mfrDetailSectionTitle}>{t("dcim.equip.ip.addTitle")}</h3>
            {deviceSiteId == null ? (
              <p className={styles.muted}>{t("dcim.equip.ip.prefixNeedsSite")}</p>
            ) : null}
            <form
              className={styles.formRow}
              onSubmit={(e) => {
                e.preventDefault();
                setErr(null);
                if (!ipIface) {
                  setErr(t("dcim.equip.ip.chooseIface"));
                  return;
                }
                createIp.mutate();
              }}
            >
              <label>
                {t("dcim.equip.if.name")}
                <select value={ipIface} onChange={(e) => setIpIface(e.target.value)}>
                  <option value="">{t("dcim.common.choose")}</option>
                  {interfacesQ.data.map((x) => (
                    <option key={x.id} value={String(x.id)}>
                      {ifaceIndentedLabel(x)}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                {t("dcim.equip.ip.address")}
                <input
                  value={ipAddr}
                  onChange={(e) => setIpAddr(e.target.value)}
                  placeholder="192.168.1.1 / 2001:db8::1"
                  required
                />
              </label>
              {deviceSiteId != null ? (
                <>
                  <label>
                    {t("dcim.equip.ip.ipv4Prefix")}
                    <select value={ipPrefix} onChange={(e) => setIpPrefix(e.target.value)}>
                      <option value="">{t("dcim.equip.ip.ipv4PrefixNone")}</option>
                      {(prefixesQ.data ?? []).map((p) => (
                        <option key={p.id} value={String(p.id)}>
                          {p.name} — {p.cidr}
                        </option>
                      ))}
                    </select>
                  </label>
                  <label>
                    {t("dcim.equip.ip.ipv6Prefix")}
                    <select value={ipPrefix6} onChange={(e) => setIpPrefix6(e.target.value)}>
                      <option value="">{t("dcim.equip.ip.ipv6PrefixNone")}</option>
                      {(prefixes6Q.data ?? []).map((p) => (
                        <option key={p.id} value={String(p.id)}>
                          {p.name} — {p.cidr}
                        </option>
                      ))}
                    </select>
                  </label>
                </>
              ) : null}
              <label style={{ flexDirection: "row", alignItems: "center", gap: "0.5rem" }}>
                <input
                  type="checkbox"
                  checked={ipPrimary}
                  onChange={(e) => setIpPrimary(e.target.checked)}
                />
                {t("dcim.equip.ip.primary")}
              </label>
              <button type="submit" className={styles.btn} disabled={createIp.isPending}>
                {createIp.isPending ? "…" : t("dcim.equip.ip.add")}
              </button>
            </form>
          </>
        ) : null}

        {interfacesQ.isLoading ? <p className={styles.muted}>{t("dcim.common.loading")}</p> : null}
        {interfacesQ.data && interfacesQ.data.length > 0 ? (
          <table className={styles.table}>
            <thead>
              <tr>
                <th>{t("dcim.common.id")}</th>
                <th>{t("dcim.equip.if.name")}</th>
                <th>{t("dcim.equip.if.parentCol")}</th>
                <th>{t("dcim.equip.if.mac")}</th>
                <th>{t("dcim.equip.if.speed")}</th>
                <th>{t("dcim.equip.if.mtu")}</th>
                <th>{t("dcim.equip.if.vlan")}</th>
                <th>{t("dcim.equip.if.ipamVrf")}</th>
                <th>{t("dcim.equip.if.enabled")}</th>
                <th>{t("dcim.equip.mfr.description")}</th>
                <th>{t("dcim.equip.ip.column")}</th>
                <th />
              </tr>
            </thead>
            <tbody>
              {interfacesQ.data.map((x) => {
                const selfAndDesc = new Set(ifaceDescendantIds.get(x.id) ?? []);
                selfAndDesc.add(x.id);
                return (
                <tr key={x.id}>
                  <td>{x.id}</td>
                  <td
                    style={{
                      paddingLeft: `calc(var(--space-2) + ${(ifaceDepthById.get(x.id) ?? 0) * 0.75}rem)`,
                    }}
                  >
                    {x.name}
                  </td>
                  <td>
                    <div style={{ display: "flex", flexWrap: "wrap", gap: "0.35rem", alignItems: "center" }}>
                      <select
                        style={{ maxWidth: "12rem", fontSize: "var(--text-xs)" }}
                        value={
                          parentDraft[x.id] ??
                          (x.parent_interface_id != null ? String(x.parent_interface_id) : "")
                        }
                        onChange={(e) =>
                          setParentDraft((prev) => ({ ...prev, [x.id]: e.target.value }))
                        }
                        title={t("dcim.equip.if.parent")}
                      >
                        <option value="">{t("dcim.equip.if.parentRoot")}</option>
                        {(interfacesQ.data ?? [])
                          .filter((c) => !selfAndDesc.has(c.id))
                          .map((c) => (
                            <option key={c.id} value={String(c.id)}>
                              {ifaceIndentedLabel(c)}
                            </option>
                          ))}
                      </select>
                      <button
                        type="button"
                        className={styles.tableIconBtn}
                        disabled={patchParent.isPending}
                        title={t("dcim.common.save")}
                        aria-label={t("dcim.common.save")}
                        onClick={() => {
                          setErr(null);
                          const raw = (
                            parentDraft[x.id] ??
                            (x.parent_interface_id != null ? String(x.parent_interface_id) : "")
                          ).trim();
                          const parent_interface_id = raw === "" ? null : Number(raw);
                          if (parent_interface_id != null && !Number.isFinite(parent_interface_id)) return;
                          patchParent.mutate({ iid: x.id, parent_interface_id });
                        }}
                      >
                        {patchParent.isPending ? "…" : <i className="fas fa-floppy-disk" aria-hidden />}
                      </button>
                    </div>
                  </td>
                  <td>{x.mac_address ?? "—"}</td>
                  <td>{x.speed_mbps ?? "—"}</td>
                  <td>{x.mtu ?? "—"}</td>
                  <td>
                    <div style={{ display: "flex", flexWrap: "wrap", gap: "0.35rem", alignItems: "center" }}>
                      <input
                        type="number"
                        min={1}
                        max={4094}
                        style={{ width: "4.5rem" }}
                        value={vlanDraft[x.id] ?? (x.vlan_id != null ? String(x.vlan_id) : "")}
                        onChange={(e) => setVlanDraft((prev) => ({ ...prev, [x.id]: e.target.value }))}
                        title={t("dcim.equip.if.vlanHint")}
                      />
                      <button
                        type="button"
                        className={styles.tableIconBtn}
                        disabled={patchVlan.isPending}
                        title={t("dcim.common.save")}
                        aria-label={t("dcim.common.save")}
                        onClick={() => {
                          setErr(null);
                          const raw = (
                            vlanDraft[x.id] ?? (x.vlan_id != null ? String(x.vlan_id) : "")
                          ).trim();
                          let vlan_id: number | null = null;
                          if (raw !== "") {
                            const n = Number(raw);
                            if (!Number.isFinite(n) || !Number.isInteger(n) || n < 1 || n > 4094) {
                              setErr(t("dcim.equip.if.badVlan"));
                              return;
                            }
                            vlan_id = n;
                          }
                          patchVlan.mutate({ iid: x.id, vlan_id });
                        }}
                      >
                        {patchVlan.isPending ? "…" : <i className="fas fa-floppy-disk" aria-hidden />}
                      </button>
                      {deviceSiteId == null ? (
                        <span className={styles.muted} title={t("dcim.equip.if.ipamVlanNeedsSite")}>
                          {t("dcim.equip.if.ipamVlanNone")}
                        </span>
                      ) : (
                        <select
                          value={x.ipam_vlan_id != null ? String(x.ipam_vlan_id) : ""}
                          title={t("dcim.equip.if.ipamVlanHint")}
                          aria-label={t("dcim.equip.if.ipamVlan")}
                          disabled={patchIpamVlan.isPending}
                          onChange={(e) => {
                            setErr(null);
                            const raw = e.target.value;
                            patchIpamVlan.mutate({
                              iid: x.id,
                              ipam_vlan_id: raw === "" ? null : Number(raw),
                            });
                          }}
                        >
                          <option value="">{t("dcim.equip.if.ipamVlanNone")}</option>
                          {(vlansQ.data ?? []).map((v) => (
                            <option key={v.id} value={String(v.id)}>
                              {v.vid} {v.name}
                            </option>
                          ))}
                        </select>
                      )}
                    </div>
                  </td>
                  <td>
                    {deviceSiteId == null ? (
                      <span className={styles.muted} title={t("dcim.equip.if.ipamVrfNeedsSite")}>
                        {t("dcim.equip.if.ipamVrfNone")}
                      </span>
                    ) : (
                      <select
                        value={x.ipam_vrf_id != null ? String(x.ipam_vrf_id) : ""}
                        title={t("dcim.equip.if.ipamVrfHint")}
                        aria-label={t("dcim.equip.if.ipamVrf")}
                        disabled={patchIpamVrf.isPending}
                        onChange={(e) => {
                          setErr(null);
                          const raw = e.target.value;
                          patchIpamVrf.mutate({
                            iid: x.id,
                            ipam_vrf_id: raw === "" ? null : Number(raw),
                          });
                        }}
                      >
                        <option value="">{t("dcim.equip.if.ipamVrfNone")}</option>
                        {(vrfsQ.data ?? []).map((v) => (
                          <option key={v.id} value={String(v.id)}>
                            {v.name} ({v.slug})
                          </option>
                        ))}
                      </select>
                    )}
                  </td>
                  <td>
                    <button
                      type="button"
                      className={styles.tableIconBtn}
                      title={x.enabled ? t("dcim.equip.if.disable") : t("dcim.equip.if.enable")}
                      aria-label={x.enabled ? t("dcim.equip.if.disable") : t("dcim.equip.if.enable")}
                      onClick={() => toggleIf.mutate({ iid: x.id, enabled: !x.enabled })}
                      disabled={toggleIf.isPending}
                    >
                      {toggleIf.isPending ? (
                        "…"
                      ) : (
                        <i className={x.enabled ? "fas fa-toggle-on" : "fas fa-toggle-off"} aria-hidden />
                      )}
                    </button>
                  </td>
                  <td>{x.description ?? "—"}</td>
                  <td>
                    <ul className={styles.ipList}>
                      {(x.ip_assignments ?? []).map((ip) => (
                        <li key={ip.id}>
                          <code>{ip.address}</code>{" "}
                          <span className={styles.muted}>({ip.family})</span>
                          {ip.family === "ipv4" && ip.ipv4_prefix_id != null ? (
                            <span className={styles.muted}>
                              {" "}
                              · {prefixById.get(ip.ipv4_prefix_id) ?? `#${ip.ipv4_prefix_id}`}
                            </span>
                          ) : null}
                          {ip.family === "ipv6" && ip.ipv6_prefix_id != null ? (
                            <span className={styles.muted}>
                              {" "}
                              · {prefix6ById.get(ip.ipv6_prefix_id) ?? `#${ip.ipv6_prefix_id}`}
                            </span>
                          ) : null}
                          {ip.family === "ipv4" && deviceSiteId != null ? (
                            <span
                              style={{
                                display: "inline-flex",
                                flexWrap: "wrap",
                                gap: "0.25rem",
                                alignItems: "center",
                                marginLeft: "0.35rem",
                              }}
                            >
                              <select
                                style={{ maxWidth: "14rem", fontSize: "var(--text-xs)" }}
                                value={
                                  ipPrefixDraft[ip.id] ??
                                  (ip.ipv4_prefix_id != null ? String(ip.ipv4_prefix_id) : "")
                                }
                                onChange={(e) =>
                                  setIpPrefixDraft((prev) => ({ ...prev, [ip.id]: e.target.value }))
                                }
                                title={t("dcim.equip.ip.ipv4Prefix")}
                              >
                                <option value="">{t("dcim.equip.ip.ipv4PrefixNone")}</option>
                                {(prefixesQ.data ?? []).map((p) => (
                                  <option key={p.id} value={String(p.id)}>
                                    {p.name} — {p.cidr}
                                  </option>
                                ))}
                              </select>
                              <button
                                type="button"
                                className={styles.tableIconBtn}
                                disabled={patchIpPrefix.isPending}
                                title={t("dcim.common.save")}
                                aria-label={t("dcim.common.save")}
                                onClick={() => {
                                  setErr(null);
                                  const raw = (
                                    ipPrefixDraft[ip.id] ??
                                    (ip.ipv4_prefix_id != null ? String(ip.ipv4_prefix_id) : "")
                                  ).trim();
                                  let ipv4_prefix_id: number | null = null;
                                  if (raw !== "") {
                                    const n = Number(raw);
                                    if (!Number.isFinite(n)) return;
                                    ipv4_prefix_id = n;
                                  }
                                  patchIpPrefix.mutate({ iid: x.id, aid: ip.id, ipv4_prefix_id });
                                }}
                              >
                                {patchIpPrefix.isPending ? "…" : <i className="fas fa-floppy-disk" aria-hidden />}
                              </button>
                            </span>
                          ) : null}
                          {ip.family === "ipv6" && deviceSiteId != null ? (
                            <span
                              style={{
                                display: "inline-flex",
                                flexWrap: "wrap",
                                gap: "0.25rem",
                                alignItems: "center",
                                marginLeft: "0.35rem",
                              }}
                            >
                              <select
                                style={{ maxWidth: "14rem", fontSize: "var(--text-xs)" }}
                                value={
                                  ipPrefix6Draft[ip.id] ??
                                  (ip.ipv6_prefix_id != null ? String(ip.ipv6_prefix_id) : "")
                                }
                                onChange={(e) =>
                                  setIpPrefix6Draft((prev) => ({ ...prev, [ip.id]: e.target.value }))
                                }
                                title={t("dcim.equip.ip.ipv6Prefix")}
                              >
                                <option value="">{t("dcim.equip.ip.ipv6PrefixNone")}</option>
                                {(prefixes6Q.data ?? []).map((p) => (
                                  <option key={p.id} value={String(p.id)}>
                                    {p.name} — {p.cidr}
                                  </option>
                                ))}
                              </select>
                              <button
                                type="button"
                                className={styles.tableIconBtn}
                                disabled={patchIpPrefix.isPending}
                                title={t("dcim.common.save")}
                                aria-label={t("dcim.common.save")}
                                onClick={() => {
                                  setErr(null);
                                  const raw = (
                                    ipPrefix6Draft[ip.id] ??
                                    (ip.ipv6_prefix_id != null ? String(ip.ipv6_prefix_id) : "")
                                  ).trim();
                                  let ipv6_prefix_id: number | null = null;
                                  if (raw !== "") {
                                    const n = Number(raw);
                                    if (!Number.isFinite(n)) return;
                                    ipv6_prefix_id = n;
                                  }
                                  patchIpPrefix.mutate({ iid: x.id, aid: ip.id, ipv6_prefix_id });
                                }}
                              >
                                {patchIpPrefix.isPending ? "…" : <i className="fas fa-floppy-disk" aria-hidden />}
                              </button>
                            </span>
                          ) : null}
                          {ip.is_primary ? (
                            <span className={styles.ipPrimaryMark}> {t("dcim.equip.ip.primaryMark")}</span>
                          ) : (
                            <button
                              type="button"
                              className={styles.btnLink}
                              onClick={() => setPrimaryIp.mutate({ iid: x.id, aid: ip.id })}
                              disabled={setPrimaryIp.isPending}
                            >
                              {t("dcim.equip.ip.setPrimary")}
                            </button>
                          )}{" "}
                          <button
                            type="button"
                            className={styles.btnDanger}
                            style={{ fontSize: "var(--text-xs)", padding: "0.1rem 0.4rem" }}
                            onClick={() => delIp.mutate({ iid: x.id, aid: ip.id })}
                            disabled={delIp.isPending}
                          >
                            {t("dcim.common.remove")}
                          </button>
                        </li>
                      ))}
                    </ul>
                    {(!x.ip_assignments || x.ip_assignments.length === 0) && (
                      <span className={styles.muted}>—</span>
                    )}
                  </td>
                  <td>
                    <button
                      type="button"
                      className={`${styles.tableIconBtn} ${styles.tableIconBtnDanger}`.trim()}
                      title={t("dcim.common.delete")}
                      aria-label={t("dcim.common.delete")}
                      onClick={() => setNetDeleteConfirm({ kind: "interface", iid: x.id, name: x.name })}
                      disabled={delIf.isPending}
                    >
                      <i className="fas fa-trash-can" aria-hidden />
                    </button>
                  </td>
                </tr>
                );
              })}
            </tbody>
          </table>
        ) : (
          !interfacesQ.isLoading && <p className={styles.muted}>{t("dcim.equip.if.empty")}</p>
        )}
        <h3 className={styles.mfrDetailSectionTitle}>{t("dcim.equip.lag.title")}</h3>
        <p className={styles.muted}>{t("dcim.equip.lag.hint")}</p>
        {lags.length === 0 && !lagsQ.isLoading ? <p className={styles.muted}>{t("dcim.equip.lag.empty")}</p> : null}
        {lags.length > 0 ? (
          <ul className={styles.ipList}>
            {lags.map((b) => (
              <li key={b.id}>
                {b.name}
                {b.members.length > 0
                  ? ` (${b.members.map((m) => m.interface_name).join(", ")})`
                  : ""}{" "}
                <button
                  type="button"
                  className={styles.btnLink}
                  onClick={() => setNetDeleteConfirm({ kind: "lag", lid: b.id, name: b.name })}
                >
                  {t("dcim.common.delete")}
                </button>
                {b.members.map((m) => (
                  <button
                    key={m.id}
                    type="button"
                    className={styles.btnLink}
                    onClick={() =>
                      setNetDeleteConfirm({ kind: "lag-member", mid: m.id, name: m.interface_name })
                    }
                  >
                    {t("dcim.equip.lag.removeMember")} {m.interface_name}
                  </button>
                ))}
              </li>
            ))}
          </ul>
        ) : null}
        <form
          className={styles.formRow}
          onSubmit={(e) => {
            e.preventDefault();
            setErr(null);
            createLag.mutate();
          }}
        >
          <label>
            {t("dcim.equip.lag.name")}
            <input value={lagName} onChange={(e) => setLagName(e.target.value)} required />
          </label>
          <button type="submit" className={styles.btn} disabled={createLag.isPending || lagName.trim() === ""}>
            {createLag.isPending ? "…" : t("dcim.equip.lag.add")}
          </button>
        </form>
        {lags.length > 0 ? (
          <form
            className={styles.formRow}
            onSubmit={(e) => {
              e.preventDefault();
              setErr(null);
              addLagMember.mutate();
            }}
          >
            <label>
              {t("dcim.equip.lag.lag")}
              <select value={lagId} onChange={(e) => setLagId(e.target.value)}>
                <option value="">{t("dcim.equip.lag.chooseLag")}</option>
                {lags.map((b) => (
                  <option key={b.id} value={String(b.id)}>
                    {b.name}
                  </option>
                ))}
              </select>
            </label>
            <label>
              {t("dcim.equip.lag.member")}
              <select value={lagIfaceId} onChange={(e) => setLagIfaceId(e.target.value)}>
                <option value="">{t("dcim.equip.lag.chooseIface")}</option>
                {freeLagIfaces.map((x) => (
                  <option key={x.id} value={String(x.id)}>
                    {ifaceIndentedLabel(x)}
                  </option>
                ))}
              </select>
            </label>
            <button
              type="submit"
              className={styles.btn}
              disabled={addLagMember.isPending || lagId === "" || lagIfaceId === ""}
            >
              {addLagMember.isPending ? "…" : t("dcim.equip.lag.bind")}
            </button>
          </form>
        ) : null}
        <h3 className={styles.mfrDetailSectionTitle}>{t("dcim.equip.wg.title")}</h3>
        <p className={styles.muted}>{t("dcim.equip.wg.hint")}</p>
        {wgIfaces.length === 0 && !wgQ.isLoading ? <p className={styles.muted}>{t("dcim.equip.wg.empty")}</p> : null}
        {wgIfaces.length > 0 ? (
          <ul className={styles.ipList}>
            {wgIfaces.map((w) => (
              <li key={w.id}>
                {w.name}
                {w.listen_port != null ? ` :${w.listen_port}` : ""}
                {w.address ? ` ${w.address}` : ""}
                {w.interface_name ? ` · ${w.interface_name}` : ""}
                {w.tunnel_slug ? ` · ${w.vpn_slug ?? ""}/${w.tunnel_slug}` : ""}{" "}
                <button
                  type="button"
                  className={styles.btnLink}
                  onClick={() => setNetDeleteConfirm({ kind: "wg", wid: w.id, name: w.name })}
                >
                  {t("dcim.common.delete")}
                </button>
                {w.peers.map((p) => (
                  <button
                    key={p.id}
                    type="button"
                    className={styles.btnLink}
                    onClick={() => setNetDeleteConfirm({ kind: "wg-peer", pid: p.id, name: p.name })}
                  >
                    {t("dcim.equip.wg.removePeer")} {p.name}
                    {p.allowed_ips && p.allowed_ips.length > 0 ? ` (${p.allowed_ips.join(", ")})` : ""}
                  </button>
                ))}
              </li>
            ))}
          </ul>
        ) : null}
        <form
          className={styles.formRow}
          onSubmit={(e) => {
            e.preventDefault();
            setErr(null);
            createWg.mutate();
          }}
        >
          <label>
            {t("dcim.equip.wg.name")}
            <input value={wgName} onChange={(e) => setWgName(e.target.value)} required />
          </label>
          <label>
            {t("dcim.equip.wg.listenPort")}
            <input value={wgListen} onChange={(e) => setWgListen(e.target.value)} inputMode="numeric" />
          </label>
          <label>
            {t("dcim.equip.wg.address")}
            <input value={wgAddr} onChange={(e) => setWgAddr(e.target.value)} />
          </label>
          <label>
            {t("dcim.equip.wg.privateRef")}
            <input value={wgPriv} onChange={(e) => setWgPriv(e.target.value)} placeholder="secret:…" />
          </label>
          <label>
            {t("dcim.equip.wg.dcimIface")}
            <select value={wgDcimIface} onChange={(e) => setWgDcimIface(e.target.value)}>
              <option value="">{t("dcim.equip.wg.dcimIfaceNone")}</option>
              {(interfacesQ.data ?? []).map((x) => (
                <option key={x.id} value={String(x.id)}>
                  {ifaceIndentedLabel(x)}
                </option>
              ))}
            </select>
          </label>
          <label>
            {t("dcim.equip.wg.vpn")}
            <select
              value={wgVpnId}
              onChange={(e) => {
                setWgVpnId(e.target.value);
                setWgTunnelId("");
              }}
            >
              <option value="">{t("dcim.equip.wg.vpnNone")}</option>
              {(wgVpnsQ.data ?? []).map((v) => (
                <option key={v.id} value={String(v.id)}>
                  {v.name}
                </option>
              ))}
            </select>
          </label>
          <label>
            {t("dcim.equip.wg.tunnel")}
            <select value={wgTunnelId} onChange={(e) => setWgTunnelId(e.target.value)} disabled={wgVpnId === ""}>
              <option value="">{t("dcim.equip.wg.tunnelNone")}</option>
              {(wgTunnelsQ.data ?? []).map((tun) => (
                <option key={tun.id} value={String(tun.id)}>
                  {tun.name}
                </option>
              ))}
            </select>
          </label>
          <button type="submit" className={styles.btn} disabled={createWg.isPending || wgName.trim() === ""}>
            {createWg.isPending ? "…" : t("dcim.equip.wg.add")}
          </button>
        </form>
        {wgIfaces.length > 0 ? (
          <form
            className={styles.formRow}
            onSubmit={(e) => {
              e.preventDefault();
              setErr(null);
              addWgPeer.mutate();
            }}
          >
            <label>
              {t("dcim.equip.wg.peerIface")}
              <select value={wgPeerIface} onChange={(e) => setWgPeerIface(e.target.value)}>
                <option value="">{t("dcim.equip.wg.chooseIface")}</option>
                {wgIfaces.map((w) => (
                  <option key={w.id} value={String(w.id)}>
                    {w.name}
                  </option>
                ))}
              </select>
            </label>
            <label>
              {t("dcim.equip.wg.peerName")}
              <input value={wgPeerName} onChange={(e) => setWgPeerName(e.target.value)} required />
            </label>
            <label>
              {t("dcim.equip.wg.peerKey")}
              <input value={wgPeerKey} onChange={(e) => setWgPeerKey(e.target.value)} placeholder="secret:…" />
            </label>
            <label>
              {t("dcim.equip.wg.peerPsk")}
              <input value={wgPeerPsk} onChange={(e) => setWgPeerPsk(e.target.value)} placeholder="secret:…" />
            </label>
            <label>
              {t("dcim.equip.wg.peerEndpoint")}
              <input value={wgPeerHost} onChange={(e) => setWgPeerHost(e.target.value)} />
            </label>
            <label>
              {t("dcim.equip.wg.peerPort")}
              <input value={wgPeerPort} onChange={(e) => setWgPeerPort(e.target.value)} inputMode="numeric" />
            </label>
            <label>
              {t("dcim.equip.wg.peerAllowed")}
              <input value={wgPeerAllowed} onChange={(e) => setWgPeerAllowed(e.target.value)} />
            </label>
            <button
              type="submit"
              className={styles.btn}
              disabled={addWgPeer.isPending || wgPeerIface === "" || wgPeerName.trim() === ""}
            >
              {addWgPeer.isPending ? "…" : t("dcim.equip.wg.addPeer")}
            </button>
          </form>
        ) : null}
        <h3 className={styles.mfrDetailSectionTitle}>{t("dcim.equip.vlanMem.title")}</h3>
        <p className={styles.muted}>{t("dcim.equip.vlanMem.hint")}</p>
        {vlanMembers.length === 0 && !vlanMemQ.isLoading ? (
          <p className={styles.muted}>{t("dcim.equip.vlanMem.empty")}</p>
        ) : null}
        {vlanMembers.length > 0 ? (
          <ul className={styles.ipList}>
            {vlanMembers.map((m) => (
              <li key={m.id}>
                {m.interface_name}: {m.vlan_name} ({m.vlan_slug}, vid {m.vlan_vid})
                {m.role ? ` · ${m.role}` : ""}{" "}
                <button
                  type="button"
                  className={styles.btnLink}
                  onClick={() =>
                    setNetDeleteConfirm({
                      kind: "vlan-member",
                      mid: m.id,
                      name: `${m.vlan_name} @ ${m.interface_name}`,
                    })
                  }
                >
                  {t("dcim.equip.vlanMem.remove")}
                </button>
              </li>
            ))}
          </ul>
        ) : null}
        {deviceSiteId == null ? (
          <p className={styles.muted}>{t("dcim.equip.vlanMem.needsSite")}</p>
        ) : (
          <form
            className={styles.formRow}
            onSubmit={(e) => {
              e.preventDefault();
              addVlanMem.mutate();
            }}
          >
            <label>
              {t("dcim.equip.vlanMem.iface")}
              <select value={vlanMemIfaceId} onChange={(e) => setVlanMemIfaceId(e.target.value)}>
                <option value="">{t("dcim.equip.vlanMem.chooseIface")}</option>
                {(interfacesQ.data ?? []).map((x) => (
                  <option key={x.id} value={x.id}>
                    {ifaceIndentedLabel(x)}
                  </option>
                ))}
              </select>
            </label>
            <label>
              {t("dcim.equip.vlanMem.vlan")}
              <select value={vlanMemVlanId} onChange={(e) => setVlanMemVlanId(e.target.value)}>
                <option value="">{t("dcim.equip.vlanMem.chooseVlan")}</option>
                {(vlansQ.data ?? []).map((v) => (
                  <option key={v.id} value={v.id}>
                    {v.name} ({v.slug}, vid {v.vid})
                  </option>
                ))}
              </select>
            </label>
            <label>
              {t("dcim.equip.vlanMem.role")}
              <select value={vlanMemRole} onChange={(e) => setVlanMemRole(e.target.value)}>
                <option value="">{t("dcim.equip.vlanMem.roleNone")}</option>
                <option value="tagged">{t("dcim.equip.vlanMem.roleTagged")}</option>
                <option value="untagged">{t("dcim.equip.vlanMem.roleUntagged")}</option>
                <option value="native">{t("dcim.equip.vlanMem.roleNative")}</option>
                <option value="other">{t("dcim.equip.vlanMem.roleOther")}</option>
              </select>
            </label>
            <button
              type="submit"
              className={styles.btn}
              disabled={addVlanMem.isPending || vlanMemIfaceId === "" || vlanMemVlanId === ""}
            >
              {addVlanMem.isPending ? "…" : t("dcim.equip.vlanMem.bind")}
            </button>
          </form>
        )}
          </>
        ) : null}
      </Panel>
      <ConfirmModal
        open={netDeleteConfirm != null}
        onClose={() => {
          if (!netDeleteBusy) setNetDeleteConfirm(null);
        }}
        title={
          netDeleteConfirm?.kind === "interface"
            ? t("dcim.equip.dev.deleteIfModalTitle", { name: netDeleteConfirm.name })
            : netDeleteConfirm?.kind === "ip"
              ? t("dcim.equip.dev.deleteIpModalTitle", { address: netDeleteConfirm.address })
              : netDeleteConfirm?.kind === "lag"
                ? t("dcim.equip.dev.deleteLagModalTitle", { name: netDeleteConfirm.name })
                : netDeleteConfirm?.kind === "lag-member"
                  ? t("dcim.equip.dev.deleteLagMemberModalTitle", { name: netDeleteConfirm.name })
                  : netDeleteConfirm?.kind === "vlan-member"
                    ? t("dcim.equip.dev.deleteVlanMemModalTitle", { name: netDeleteConfirm.name })
                    : netDeleteConfirm?.kind === "wg"
                      ? t("dcim.equip.dev.deleteWgModalTitle", { name: netDeleteConfirm.name })
                      : netDeleteConfirm?.kind === "wg-peer"
                        ? t("dcim.equip.dev.deleteWgPeerModalTitle", { name: netDeleteConfirm.name })
                        : ""
        }
        message={
          netDeleteConfirm?.kind === "interface"
            ? t("dcim.equip.dev.deleteIfModalHint")
            : netDeleteConfirm?.kind === "ip"
              ? t("dcim.equip.dev.deleteIpModalHint")
              : netDeleteConfirm?.kind === "lag"
                ? t("dcim.equip.dev.deleteLagModalHint")
                : netDeleteConfirm?.kind === "lag-member"
                  ? t("dcim.equip.dev.deleteLagMemberModalHint")
                  : netDeleteConfirm?.kind === "vlan-member"
                    ? t("dcim.equip.dev.deleteVlanMemModalHint")
                    : netDeleteConfirm?.kind === "wg"
                      ? t("dcim.equip.dev.deleteWgModalHint")
                      : netDeleteConfirm?.kind === "wg-peer"
                        ? t("dcim.equip.dev.deleteWgPeerModalHint")
                        : null
        }
        confirmLabel={
          netDeleteConfirm?.kind === "ip" ||
          netDeleteConfirm?.kind === "lag-member" ||
          netDeleteConfirm?.kind === "vlan-member" ||
          netDeleteConfirm?.kind === "wg-peer"
            ? t("dcim.common.remove")
            : t("dcim.common.delete")
        }
        cancelLabel={t("dcim.common.cancel")}
        danger
        pending={netDeleteBusy}
        onConfirm={() => {
          if (!netDeleteConfirm) return;
          if (netDeleteConfirm.kind === "interface") {
            delIf.mutate(netDeleteConfirm.iid, { onSettled: () => setNetDeleteConfirm(null) });
            return;
          }
          if (netDeleteConfirm.kind === "lag") {
            delLag.mutate(netDeleteConfirm.lid, { onSettled: () => setNetDeleteConfirm(null) });
            return;
          }
          if (netDeleteConfirm.kind === "lag-member") {
            delLagMember.mutate(netDeleteConfirm.mid, { onSettled: () => setNetDeleteConfirm(null) });
            return;
          }
          if (netDeleteConfirm.kind === "vlan-member") {
            delVlanMem.mutate(netDeleteConfirm.mid, { onSettled: () => setNetDeleteConfirm(null) });
            return;
          }
          if (netDeleteConfirm.kind === "wg") {
            delWg.mutate(netDeleteConfirm.wid, { onSettled: () => setNetDeleteConfirm(null) });
            return;
          }
          if (netDeleteConfirm.kind === "wg-peer") {
            delWgPeer.mutate(netDeleteConfirm.pid, { onSettled: () => setNetDeleteConfirm(null) });
            return;
          }
          delIp.mutate(
            { iid: netDeleteConfirm.iid, aid: netDeleteConfirm.aid },
            { onSettled: () => setNetDeleteConfirm(null) },
          );
        }}
      />
    </>
  );
}
