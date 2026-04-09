import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useMemo, useState } from "react";
import { Link, useParams, useSearchParams } from "react-router-dom";
import { Panel } from "@/components/ui/Panel";
import { useI18n } from "@/i18n/I18nProvider";
import { ApiError, apiGet } from "@/lib/api";
import * as ipamApi from "@/features/ipam/ipamApi";
import * as api from "./dcimApi";
import type { DeviceInterface } from "./types";
import { CAP_DCIM_DEVICE_HARDWARE_VIEW, CAP_DCIM_DEVICE_OS_VIEW } from "@/plugins/capabilities";
import { pluginsWithCapability } from "@/plugins/devicePluginSupport";
import { usePlugins } from "@/plugins/PluginContext";
import { DcimInnerTabs } from "./DcimInnerTabs";
import styles from "./dcim.module.css";

const DEVICE_DETAIL_TABS = new Set(["overview", "network", "hardware", "os"]);
type DeviceDetailTab = "overview" | "network" | "hardware" | "os";

export function DcimDeviceDetailPage() {
  const { t } = useI18n();
  const qc = useQueryClient();
  const plugins = usePlugins();
  const { deviceId } = useParams<{ deviceId: string }>();
  const [searchParams, setSearchParams] = useSearchParams();
  const id = Number(deviceId);

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
  const [ifParent, setIfParent] = useState("");
  const [vlanDraft, setVlanDraft] = useState<Record<number, string>>({});
  const [parentDraft, setParentDraft] = useState<Record<number, string>>({});
  const [ipIface, setIpIface] = useState("");
  const [ipAddr, setIpAddr] = useState("");
  const [ipPrimary, setIpPrimary] = useState(false);
  const [ipPrefix, setIpPrefix] = useState("");
  const [ipPrefixDraft, setIpPrefixDraft] = useState<Record<number, string>>({});
  const [typeEdit, setTypeEdit] = useState("");

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

  const typesQ = useQuery({
    queryKey: ["dcim", "device-types"],
    queryFn: api.listDeviceTypes,
  });

  const modelsQ = useQuery({
    queryKey: ["dcim", "device-models"],
    queryFn: api.listDeviceModels,
  });

  const sitesQ = useQuery({ queryKey: ["dcim", "sites"], queryFn: api.listSites });

  const deviceSiteId = deviceQ.data?.effective_site_id ?? null;

  const prefixesQ = useQuery({
    queryKey: ["ipam", "ipv4-prefixes", deviceSiteId ?? "none"],
    queryFn: () => ipamApi.listIpv4Prefixes(deviceSiteId!),
    enabled: deviceSiteId != null && deviceSiteId > 0,
  });

  const prefixById = useMemo(() => {
    const m = new Map<number, string>();
    for (const p of prefixesQ.data ?? []) m.set(p.id, p.cidr);
    return m;
  }, [prefixesQ.data]);

  const ifaceDepthById = useMemo(() => {
    const rows = interfacesQ.data ?? [];
    const m = new Map<number, number>();
    for (const r of rows) {
      const p = r.parent_interface_id;
      const depth = p == null ? 0 : (m.get(p) ?? 0) + 1;
      m.set(r.id, depth);
    }
    return m;
  }, [interfacesQ.data]);

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

  const ifaceIndentedLabel = (x: DeviceInterface) => {
    const d = ifaceDepthById.get(x.id) ?? 0;
    return `${"\u00A0\u00A0".repeat(d)}${x.name}`;
  };

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

  const siteLabel = useMemo(() => {
    const sid = deviceQ.data?.effective_site_id;
    if (sid == null) return null;
    const row = (sitesQ.data ?? []).find((x) => x.id === sid);
    return row ? `${row.name} (#${sid})` : `#${sid}`;
  }, [deviceQ.data?.effective_site_id, sitesQ.data]);

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
  }, [deviceQ.data?.id, deviceQ.data?.device_type_id]);

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
      const body: { address: string; is_primary: boolean; ipv4_prefix_id?: number } = {
        address: ipAddr.trim(),
        is_primary: ipPrimary,
      };
      if (ipPrefix !== "") body.ipv4_prefix_id = Number(ipPrefix);
      return api.createIfaceIpAssignment(id, Number(ipIface), body);
    },
    onSuccess: () => {
      setIpAddr("");
      setIpPrimary(false);
      setIpPrefix("");
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

  const setPrimaryIp = useMutation({
    mutationFn: ({ iid, aid }: { iid: number; aid: number }) =>
      api.updateIfaceIpAssignment(id, iid, aid, { is_primary: true }),
    onSuccess: () => {
      setErr(null);
      void qc.invalidateQueries({ queryKey: ["dcim", "devices", id, "interfaces"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const patchIpPrefix = useMutation({
    mutationFn: ({
      iid,
      aid,
      ipv4_prefix_id,
    }: {
      iid: number;
      aid: number;
      ipv4_prefix_id: number | null;
    }) => api.updateIfaceIpAssignment(id, iid, aid, { ipv4_prefix_id }),
    onSuccess: (_d, vars) => {
      setErr(null);
      setIpPrefixDraft((prev) => {
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
        <Link to="/dcim/equipment" className={styles.tableLink}>
          {t("dcim.equip.dev.backToList")}
        </Link>
      </Panel>
    );
  }

  if (deviceQ.isError) {
    return (
      <Panel title={t("dcim.equip.dev.detailTitle")}>
        <p className={styles.err}>{(deviceQ.error as Error).message}</p>
        <Link to="/dcim/equipment" className={styles.tableLink}>
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
        <Link to="/dcim/equipment" className={styles.tableLink}>
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
            <dl className={styles.dlInline}>
              <dt>{t("dcim.common.id")}</dt>
              <dd>{dev.id}</dd>
              <dt>{t("dcim.equip.dev.modelCol")}</dt>
              <dd>{modelLabel ?? "—"}</dd>
              <dt>{t("dcim.equip.dev.effectiveTypeCol")}</dt>
              <dd>{typeLabel ?? "—"}</dd>
              <dt>{t("dcim.equip.dev.siteCol")}</dt>
              <dd>{siteLabel ?? "—"}</dd>
            </dl>
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
            {hasAttrs ? (
              <section className={styles.mfrDetailSection}>
                <h3 className={styles.mfrDetailSectionTitle}>{t("dcim.equip.dev.attributesBlock")}</h3>
                <pre className={styles.codeBlock}>{JSON.stringify(attrs, null, 2)}</pre>
              </section>
            ) : null}
          </>
        ) : null}

        {detailTab === "hardware" ? (
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
                        className={styles.btn}
                        disabled={patchParent.isPending}
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
                        {patchParent.isPending ? "…" : t("dcim.common.save")}
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
                        className={styles.btn}
                        disabled={patchVlan.isPending}
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
                        {patchVlan.isPending ? "…" : t("dcim.common.save")}
                      </button>
                    </div>
                  </td>
                  <td>
                    <button
                      type="button"
                      className={styles.btn}
                      onClick={() => toggleIf.mutate({ iid: x.id, enabled: !x.enabled })}
                      disabled={toggleIf.isPending}
                    >
                      {x.enabled ? t("dcim.equip.if.disable") : t("dcim.equip.if.enable")}
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
                                className={styles.btn}
                                style={{ fontSize: "var(--text-xs)", padding: "0.15rem 0.45rem" }}
                                disabled={patchIpPrefix.isPending}
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
                                {patchIpPrefix.isPending ? "…" : t("dcim.common.save")}
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
                      className={styles.btnDanger}
                      onClick={() => delIf.mutate(x.id)}
                      disabled={delIf.isPending}
                    >
                      {t("dcim.common.delete")}
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
          </>
        ) : null}
      </Panel>
    </>
  );
}
