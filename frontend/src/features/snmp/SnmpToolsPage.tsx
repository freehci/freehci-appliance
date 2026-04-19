import { useMutation } from "@tanstack/react-query";
import { useEffect, useMemo, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { useI18n } from "@/i18n/I18nProvider";
import { ApiError } from "@/lib/api";
import dcimStyles from "@/features/dcim/dcim.module.css";
import * as snmpApi from "./snmpApi";
import { SnmpInventoryPanel } from "./SnmpInventoryPanel";

const SYS_NAME_OID_SUFFIX = "1.3.6.1.2.1.1.5.0";

function suggestedDeviceNameFromProbe(r: snmpApi.SnmpProbeResult, fallbackHost: string): string {
  const host = fallbackHost.trim();
  if (!r.ok) return host;
  const norm = (oid: string) => oid.replace(/\s+/g, "").trim();
  for (const vb of r.varbinds) {
    const o = norm(vb.oid);
    if (o === SYS_NAME_OID_SUFFIX || o.endsWith(".1.1.5.0")) {
      const v = vb.value.trim();
      if (v !== "") return v;
    }
  }
  return host;
}

export function SnmpToolsPage() {
  const { t } = useI18n();
  const [searchParams] = useSearchParams();
  const hostFromQuery = searchParams.get("host")?.trim() ?? "";

  const [err, setErr] = useState<string | null>(null);
  const [probeHost, setProbeHost] = useState(() => hostFromQuery);
  const [probePort, setProbePort] = useState("161");
  const [probeCommunity, setProbeCommunity] = useState("public");
  const [probeOid, setProbeOid] = useState("1.3.6.1.2.1.1.1.0");
  const [probeOp, setProbeOp] = useState<"get" | "walk">("get");
  const [probeResult, setProbeResult] = useState<snmpApi.SnmpProbeResult | null>(null);
  const [discoveryResult, setDiscoveryResult] = useState<snmpApi.SnmpHostDiscoveryResult | null>(null);

  useEffect(() => {
    if (hostFromQuery !== "") setProbeHost(hostFromQuery);
  }, [hostFromQuery]);

  const probeMut = useMutation({
    mutationFn: () =>
      snmpApi.snmpProbe({
        host: probeHost.trim(),
        port: Number(probePort) || 161,
        community: probeCommunity,
        oid: probeOid.trim(),
        operation: probeOp,
      }),
    onSuccess: (r) => {
      setErr(null);
      setProbeResult(r);
    },
    onError: (e: Error) => {
      setProbeResult(null);
      setErr(e instanceof ApiError ? e.message : e.message);
    },
  });

  const discoveryMut = useMutation({
    mutationFn: () =>
      snmpApi.snmpHostDiscovery({
        host: probeHost.trim(),
        port: Number(probePort) || 161,
        community: probeCommunity,
      }),
    onSuccess: (r) => {
      setErr(null);
      setDiscoveryResult(r);
    },
    onError: (e: Error) => {
      setDiscoveryResult(null);
      setErr(e instanceof ApiError ? e.message : e.message);
    },
  });

  const dcimPrefillName = useMemo(
    () =>
      probeResult && probeHost.trim() !== ""
        ? suggestedDeviceNameFromProbe(probeResult, probeHost)
        : "",
    [probeResult, probeHost],
  );

  const dcimEquipmentHref =
    dcimPrefillName !== "" && probeHost.trim() !== ""
      ? `/dcim/equipment/devices/new?prefillDeviceName=${encodeURIComponent(dcimPrefillName)}&snmpHost=${encodeURIComponent(probeHost.trim())}`
      : null;

  const dcimFromDiscoveryHref = useMemo(() => {
    if (!discoveryResult?.ok || probeHost.trim() === "") return null;
    const name = discoveryResult.sys_name?.trim() || probeHost.trim();
    const params = new URLSearchParams();
    params.set("prefillDeviceName", name);
    params.set("snmpHost", probeHost.trim());
    const m = discoveryResult.linked_manufacturer;
    if (m) params.set("prefillManufacturer", String(m.id));
    return `/dcim/equipment/devices/new?${params.toString()}`;
  }, [discoveryResult, probeHost]);

  const discoveryField = (label: string, value: string | null | undefined) => (
    <tr>
      <th scope="row" style={{ verticalAlign: "top", whiteSpace: "nowrap" }}>
        {label}
      </th>
      <td>
        {value != null && value !== "" ? (
          <code style={{ whiteSpace: "pre-wrap", wordBreak: "break-word" }}>{value}</code>
        ) : (
          <span className={dcimStyles.muted}>—</span>
        )}
      </td>
    </tr>
  );

  return (
    <>
      {err ? <p className={dcimStyles.err}>{err}</p> : null}
      <p className={dcimStyles.muted} style={{ marginTop: 0 }}>
        {t("snmp.intro")}
      </p>

      <section className={dcimStyles.mfrDetailSection}>
        <h3 className={dcimStyles.mfrDetailSectionTitle}>{t("snmp.probeTitle")}</h3>
        <p className={dcimStyles.muted} style={{ marginTop: 0 }}>
          {t("snmp.probeHint")}
        </p>
        <form
          className={dcimStyles.formRow}
          onSubmit={(e) => {
            e.preventDefault();
            setErr(null);
            if (probeHost.trim() === "" || probeOid.trim() === "") {
              setErr(t("snmp.probeMissing"));
              return;
            }
            probeMut.mutate();
          }}
        >
          <label>
            {t("snmp.probeHost")}
            <input value={probeHost} onChange={(e) => setProbeHost(e.target.value)} placeholder="192.168.1.1" />
          </label>
          <label>
            {t("snmp.probePort")}
            <input value={probePort} onChange={(e) => setProbePort(e.target.value)} />
          </label>
          <label>
            {t("snmp.probeCommunity")}
            <input value={probeCommunity} onChange={(e) => setProbeCommunity(e.target.value)} />
          </label>
          <label>
            {t("snmp.probeOid")}
            <input value={probeOid} onChange={(e) => setProbeOid(e.target.value)} />
          </label>
          <label>
            {t("snmp.probeOperation")}
            <select value={probeOp} onChange={(e) => setProbeOp(e.target.value as "get" | "walk")}>
              <option value="get">GET</option>
              <option value="walk">WALK (bulk)</option>
            </select>
          </label>
          <button type="submit" className={dcimStyles.btn} disabled={probeMut.isPending}>
            {probeMut.isPending ? "…" : t("snmp.probeRun")}
          </button>
        </form>

        {probeResult ? (
          <div style={{ marginTop: "var(--space-2)" }}>
            {probeResult.ok ? (
              <div style={{ display: "flex", flexWrap: "wrap", alignItems: "center", gap: "var(--space-2)" }}>
                <p className={dcimStyles.muted} style={{ margin: 0 }}>
                  {t("snmp.probeOk")}
                </p>
                {dcimEquipmentHref ? (
                  <Link className={dcimStyles.btnMuted} to={dcimEquipmentHref} title={t("snmp.addDeviceDcimHint")}>
                    {t("snmp.addDeviceDcim")}
                  </Link>
                ) : null}
              </div>
            ) : (
              <p className={dcimStyles.err}>
                {t("snmp.probeFail")}: {probeResult.error ?? "—"}
              </p>
            )}
            {probeResult.varbinds.length > 0 ? (
              <div style={{ maxHeight: "50vh", overflow: "auto" }}>
                <table className={dcimStyles.table}>
                  <thead>
                    <tr>
                      <th>{t("snmp.colOid")}</th>
                      <th>{t("snmp.probeValue")}</th>
                    </tr>
                  </thead>
                  <tbody>
                    {probeResult.varbinds.map((vb, i) => (
                      <tr key={`${vb.oid}-${i}`}>
                        <td>
                          <code>{vb.oid}</code>
                        </td>
                        <td>
                          <code>{vb.value}</code>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : null}
          </div>
        ) : null}
      </section>

      <section className={dcimStyles.mfrDetailSection}>
        <h3 className={dcimStyles.mfrDetailSectionTitle}>{t("snmp.discoveryTitle")}</h3>
        <p className={dcimStyles.muted} style={{ marginTop: 0 }}>
          {t("snmp.discoveryHint")}
        </p>
        <div className={dcimStyles.formRow}>
          <button
            type="button"
            className={dcimStyles.btn}
            disabled={discoveryMut.isPending}
            onClick={() => {
              setErr(null);
              if (probeHost.trim() === "") {
                setErr(t("snmp.discoveryMissingHost"));
                return;
              }
              discoveryMut.mutate();
            }}
          >
            {discoveryMut.isPending ? "…" : t("snmp.discoveryRun")}
          </button>
          <span className={dcimStyles.muted}>{t("snmp.probeHost")}: samme som over</span>
        </div>

        {discoveryResult ? (
          <div style={{ marginTop: "var(--space-3)" }}>
            {!discoveryResult.ok ? (
              <p className={dcimStyles.err}>
                {t("snmp.discoveryFail")}: {discoveryResult.error ?? "—"}
              </p>
            ) : (
              <>
                <div style={{ display: "flex", flexWrap: "wrap", alignItems: "center", gap: "var(--space-2)" }}>
                  {dcimFromDiscoveryHref ? (
                    <Link
                      className={dcimStyles.btnMuted}
                      to={dcimFromDiscoveryHref}
                      title={t("snmp.discoveryAddDcimHint")}
                    >
                      {t("snmp.discoveryAddDcim")}
                    </Link>
                  ) : null}
                  <Link className={dcimStyles.btnMuted} to="/snmp/enterprises">
                    {t("snmp.discoveryOpenEnterprises")}
                  </Link>
                  <Link className={dcimStyles.btnMuted} to="/snmp/mibs">
                    {t("snmp.discoveryOpenMibs")}
                  </Link>
                </div>
                <table className={dcimStyles.table} style={{ marginTop: "var(--space-2)" }}>
                  <tbody>
                    {discoveryField(t("snmp.discoverySysName"), discoveryResult.sys_name)}
                    {discoveryField(t("snmp.discoverySysDescr"), discoveryResult.sys_descr)}
                    {discoveryField(t("snmp.discoverySysLocation"), discoveryResult.sys_location)}
                    {discoveryField(t("snmp.discoverySysContact"), discoveryResult.sys_contact)}
                    {discoveryField(t("snmp.discoverySysUptime"), discoveryResult.sys_uptime)}
                    {discoveryField(t("snmp.discoverySysObjectId"), discoveryResult.sys_object_id)}
                    {discoveryField(t("snmp.discoverySysObjectNumeric"), discoveryResult.sys_object_id_numeric)}
                    {discoveryField(
                      t("snmp.discoveryEnterprise"),
                      discoveryResult.enterprise_number != null ? String(discoveryResult.enterprise_number) : null,
                    )}
                    {discoveryField(t("snmp.discoveryIanaOrg"), discoveryResult.iana_organization)}
                    {discoveryField(
                      t("snmp.discoveryDcimMfr"),
                      discoveryResult.linked_manufacturer
                        ? `${discoveryResult.linked_manufacturer.name} (id ${discoveryResult.linked_manufacturer.id})`
                        : null,
                    )}
                  </tbody>
                </table>
                {discoveryResult.enterprise_number == null && discoveryResult.sys_object_id ? (
                  <p className={dcimStyles.muted} style={{ marginTop: "var(--space-2)" }}>
                    {t("snmp.discoveryNoPen")}
                  </p>
                ) : null}
                <p className={dcimStyles.muted} style={{ marginTop: "var(--space-2)", marginBottom: "var(--space-1)" }}>
                  {t("snmp.discoveryMibFiles")}
                </p>
                {discoveryResult.mib_files_in_library.length > 0 ? (
                  <ul style={{ marginTop: 0 }}>
                    {discoveryResult.mib_files_in_library.map((f) => (
                      <li key={f}>
                        <code>{f}</code>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className={dcimStyles.muted} style={{ marginTop: 0 }}>
                    {t("snmp.discoveryMibFilesEmpty")}
                  </p>
                )}
              </>
            )}
          </div>
        ) : null}
      </section>

      <SnmpInventoryPanel
        mode="picker"
        initialHost={hostFromQuery}
        hostSyncKey={hostFromQuery}
      />
    </>
  );
}
