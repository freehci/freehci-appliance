import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useMemo, useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { ConfirmModal } from "@/components/ui/ConfirmModal";
import { Panel } from "@/components/ui/Panel";
import { useI18n } from "@/i18n/I18nProvider";
import { ApiError } from "@/lib/api";
import * as api from "./dcimApi";
import { DcimInnerTabs } from "./DcimInnerTabs";
import styles from "./dcim.module.css";
import { deviceTypeFaIconClass } from "./dcimTypeIcons";
import { deviceInstanceListThumbSrc, deviceModelListThumbSrc } from "./modelImages";
import type { DeviceInstance, DeviceModel, Rack, RackPlacement } from "./types";

type EquipTab = "mfr" | "dt" | "dm" | "dev" | "pl";

export function DcimEquipmentPage() {
  const { t } = useI18n();
  const qc = useQueryClient();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [err, setErr] = useState<string | null>(null);

  const [mfrName, setMfrName] = useState("");
  const [mfrDesc, setMfrDesc] = useState("");
  const [mfrUrl, setMfrUrl] = useState("");
  const [dtName, setDtName] = useState("");
  const [dtSlug, setDtSlug] = useState("");
  const [dtDesc, setDtDesc] = useState("");
  const [plRack, setPlRack] = useState<string>("");
  const [plDev, setPlDev] = useState<string>("");
  const [plU, setPlU] = useState("1");
  const [dmMatchOid, setDmMatchOid] = useState("");
  const [dmMatchResult, setDmMatchResult] = useState<DeviceModel[] | null>(null);
  const [plMount, setPlMount] = useState("front");
  const [rackFilter, setRackFilter] = useState<string>("");
  const [devListFilter, setDevListFilter] = useState("");
  const [equipTab, setEquipTab] = useState<EquipTab>("mfr");
  const [mfrPendingDelete, setMfrPendingDelete] = useState<{ id: number; name: string } | null>(null);
  const [dtPendingDelete, setDtPendingDelete] = useState<{ id: number; name: string } | null>(null);
  const [plPendingRemove, setPlPendingRemove] = useState<RackPlacement | null>(null);

  const manufacturersQ = useQuery({
    queryKey: ["dcim", "manufacturers"],
    queryFn: api.listManufacturers,
  });
  const deviceTypesQ = useQuery({
    queryKey: ["dcim", "device-types"],
    queryFn: api.listDeviceTypes,
  });
  const modelsQ = useQuery({ queryKey: ["dcim", "device-models"], queryFn: api.listDeviceModels });
  const devicesQ = useQuery({ queryKey: ["dcim", "devices"], queryFn: api.listDevices });
  const racksQ = useQuery({ queryKey: ["dcim", "racks", "all-equip"], queryFn: () => api.listRacks() });

  const rackIdFilter = rackFilter.trim() === "" ? undefined : Number(rackFilter);
  const placementsQ = useQuery({
    queryKey: ["dcim", "placements", rackIdFilter ?? "all"],
    queryFn: () => api.listPlacements(rackIdFilter),
  });

  const allPlacementsLinkQ = useQuery({
    queryKey: ["dcim", "placements", "all"],
    queryFn: () => api.listPlacements(),
  });

  const racksById = useMemo(() => {
    const m = new Map<number, Rack>();
    for (const r of racksQ.data ?? []) m.set(r.id, r);
    return m;
  }, [racksQ.data]);

  const placementByDeviceId = useMemo(() => {
    const m = new Map<number, RackPlacement>();
    for (const p of allPlacementsLinkQ.data ?? []) m.set(p.device_id, p);
    return m;
  }, [allPlacementsLinkQ.data]);

  const manufacturersById = useMemo(() => {
    const m = new Map<number, string>();
    for (const x of manufacturersQ.data ?? []) m.set(x.id, x.name);
    return m;
  }, [manufacturersQ.data]);

  const deviceTypesById = useMemo(() => {
    const m = new Map<number, { name: string; slug: string }>();
    for (const x of deviceTypesQ.data ?? []) m.set(x.id, { name: x.name, slug: x.slug });
    return m;
  }, [deviceTypesQ.data]);

  const modelNameById = useMemo(() => {
    const m = new Map<number, string>();
    for (const mo of modelsQ.data ?? []) m.set(mo.id, mo.name);
    return m;
  }, [modelsQ.data]);

  const modelsById = useMemo(() => {
    const m = new Map<number, DeviceModel>();
    for (const mo of modelsQ.data ?? []) m.set(mo.id, mo);
    return m;
  }, [modelsQ.data]);

  const devicesById = useMemo(() => {
    const m = new Map<number, DeviceInstance>();
    for (const d of devicesQ.data ?? []) m.set(d.id, d);
    return m;
  }, [devicesQ.data]);

  const filteredDevices = useMemo(() => {
    const rows = devicesQ.data ?? [];
    const q = devListFilter.trim().toLowerCase();
    if (q === "") return rows;
    return rows.filter((x) => {
      const pl = placementByDeviceId.get(x.id);
      const r = pl ? racksById.get(pl.rack_id) : undefined;
      const placementStr = pl
        ? `${pl.rack_id} ${pl.u_position} ${pl.mounting} ${r?.name ?? ""}`.toLowerCase()
        : "";
      const modelName =
        x.device_model_id != null ? (modelNameById.get(x.device_model_id) ?? "").toLowerCase() : "";
      const eff = x.effective_device_type_id;
      const dt = eff != null ? deviceTypesById.get(eff) : undefined;
      const typeStr = dt != null ? `${dt.name} ${dt.slug}`.toLowerCase() : "";
      const blob = [
        String(x.id),
        x.name.toLowerCase(),
        (x.serial_number ?? "").toLowerCase(),
        (x.asset_tag ?? "").toLowerCase(),
        x.device_model_id != null ? String(x.device_model_id) : "",
        modelName,
        typeStr,
        placementStr,
      ].join(" ");
      return blob.includes(q);
    });
  }, [
    devicesQ.data,
    devListFilter,
    placementByDeviceId,
    racksById,
    modelNameById,
    deviceTypesById,
  ]);

  useEffect(() => {
    const name = searchParams.get("prefillDeviceName")?.trim() ?? "";
    const snmpHost = searchParams.get("snmpHost")?.trim() ?? "";
    const mfr = searchParams.get("prefillManufacturer")?.trim() ?? "";
    if (name === "" && snmpHost === "" && mfr === "") return;
    if (name !== "" || snmpHost !== "") {
      const qs = new URLSearchParams();
      if (name !== "") qs.set("prefillDeviceName", name);
      if (snmpHost !== "") qs.set("snmpHost", snmpHost);
      if (mfr !== "") qs.set("prefillManufacturer", mfr);
      navigate(`/dcim/equipment/devices/new?${qs}`, { replace: true });
      return;
    }
    const n = Number(mfr);
    if (Number.isFinite(n) && n >= 1) {
      navigate(`/dcim/equipment/device-models/new?prefillManufacturer=${n}`, { replace: true });
    }
  }, [searchParams, navigate]);

  const createMfr = useMutation({
    mutationFn: () =>
      api.createManufacturer({
        name: mfrName.trim(),
        description: mfrDesc.trim() === "" ? null : mfrDesc.trim(),
        website_url: mfrUrl.trim() === "" ? null : mfrUrl.trim(),
      }),
    onSuccess: () => {
      setMfrName("");
      setMfrDesc("");
      setMfrUrl("");
      setErr(null);
      void qc.invalidateQueries({ queryKey: ["dcim", "manufacturers"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const delMfr = useMutation({
    mutationFn: (id: number) => api.deleteManufacturer(id),
    onSuccess: () => {
      setErr(null);
      void qc.invalidateQueries({ queryKey: ["dcim", "manufacturers"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const createDt = useMutation({
    mutationFn: () =>
      api.createDeviceType({
        name: dtName.trim(),
        slug: dtSlug.trim().toLowerCase(),
        description: dtDesc.trim() === "" ? null : dtDesc.trim(),
      }),
    onSuccess: () => {
      setDtName("");
      setDtSlug("");
      setDtDesc("");
      setErr(null);
      void qc.invalidateQueries({ queryKey: ["dcim", "device-types"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const delDt = useMutation({
    mutationFn: (id: number) => api.deleteDeviceType(id),
    onSuccess: () => {
      setErr(null);
      void qc.invalidateQueries({ queryKey: ["dcim", "device-types"] });
      void qc.invalidateQueries({ queryKey: ["dcim", "device-models"] });
      void qc.invalidateQueries({ queryKey: ["dcim", "devices"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const createPl = useMutation({
    mutationFn: () => {
      const uN = Number(plU);
      const u_position = Number.isFinite(uN) ? uN : 0;
      return api.createPlacement({
        rack_id: Number(plRack),
        device_id: Number(plDev),
        u_position,
        mounting: plMount,
      });
    },
    onSuccess: () => {
      setErr(null);
      void qc.invalidateQueries({ queryKey: ["dcim", "placements"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const delPl = useMutation({
    mutationFn: (id: number) => api.deletePlacement(id),
    onSuccess: () => {
      setErr(null);
      void qc.invalidateQueries({ queryKey: ["dcim", "placements"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  return (
    <>
    <Panel title={t("nav.dcimEquipment")}>
      {err ? <p className={styles.err}>{err}</p> : null}
      <p className={styles.muted} style={{ marginTop: 0 }}>
        {t("dcim.equip.introBody")}
      </p>
      <DcimInnerTabs
        tabs={[
          { id: "mfr", label: t("dcim.equip.mfr.title"), icon: "manufacturers" },
          { id: "dt", label: t("dcim.equip.dt.title"), icon: "deviceTypes" },
          { id: "dm", label: t("dcim.equip.dm.title"), icon: "deviceModels" },
          { id: "dev", label: t("dcim.equip.dev.title"), icon: "devices" },
          { id: "pl", label: t("dcim.equip.pl.title"), icon: "placements" },
        ]}
        activeId={equipTab}
        onChange={(id) => setEquipTab(id as EquipTab)}
        ariaLabel={t("dcim.innerNavAria")}
      />
      {equipTab === "mfr" ? (
        <>
        <form
          className={styles.formRow}
          onSubmit={(e) => {
            e.preventDefault();
            setErr(null);
            createMfr.mutate();
          }}
        >
          <label>
            {t("dcim.common.name")}
            <input value={mfrName} onChange={(e) => setMfrName(e.target.value)} required />
          </label>
          <label>
            {t("dcim.equip.mfr.description")}
            <input value={mfrDesc} onChange={(e) => setMfrDesc(e.target.value)} />
          </label>
          <label>
            {t("dcim.equip.mfr.website")}
            <input
              type="url"
              value={mfrUrl}
              onChange={(e) => setMfrUrl(e.target.value)}
              placeholder="https://"
            />
          </label>
          <button type="submit" className={styles.btn} disabled={createMfr.isPending}>
            {createMfr.isPending ? "…" : t("dcim.common.add")}
          </button>
        </form>
        {manufacturersQ.isLoading ? <p className={styles.muted}>{t("dcim.common.loading")}</p> : null}
        {manufacturersQ.data && manufacturersQ.data.length > 0 ? (
          <table className={styles.table}>
            <thead>
              <tr>
                <th>{t("dcim.equip.mfr.logoCol")}</th>
                <th>{t("dcim.common.name")}</th>
                <th>{t("dcim.equip.mfr.website")}</th>
                <th scope="col">
                  <span className="sr-only">{t("dcim.equip.actionsCol")}</span>
                </th>
              </tr>
            </thead>
            <tbody>
              {manufacturersQ.data.map((x) => (
                <tr key={x.id}>
                  <td className={styles.mfrLogoCell}>
                    {x.has_logo ? (
                      <img
                        src={api.manufacturerLogoUrl(x.id)}
                        alt=""
                        className={styles.mfrLogoThumb}
                      />
                    ) : (
                      <span className={styles.muted}>—</span>
                    )}
                  </td>
                  <td>
                    <Link to={`/dcim/equipment/manufacturers/${x.id}`} className={styles.tableLink}>
                      {x.name}
                    </Link>
                  </td>
                  <td>
                    {x.website_url ? (
                      <a href={x.website_url} target="_blank" rel="noreferrer" className={styles.tableLink}>
                        {x.website_url}
                      </a>
                    ) : (
                      "—"
                    )}
                  </td>
                  <td>
                    <div className={styles.tableIconActions}>
                      <button
                        type="button"
                        className={`${styles.tableIconBtn} ${styles.tableIconBtnDanger}`.trim()}
                        title={t("dcim.common.delete")}
                        aria-label={t("dcim.equip.mfr.deleteManufacturerAria", { name: x.name })}
                        disabled={delMfr.isPending}
                        onClick={() => setMfrPendingDelete({ id: x.id, name: x.name })}
                      >
                        <i className="fas fa-trash-can" aria-hidden />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          !manufacturersQ.isLoading && <p className={styles.muted}>{t("dcim.equip.mfr.empty")}</p>
        )}
        </>
      ) : null}
      {equipTab === "dt" ? (
        <>
        <p className={styles.muted} style={{ marginTop: 0 }}>
          {t("dcim.equip.dt.hint")}
        </p>
        <form
          className={styles.formRow}
          onSubmit={(e) => {
            e.preventDefault();
            setErr(null);
            createDt.mutate();
          }}
        >
          <label>
            {t("dcim.common.name")}
            <input value={dtName} onChange={(e) => setDtName(e.target.value)} required />
          </label>
          <label>
            {t("dcim.equip.dt.slug")}
            <input
              value={dtSlug}
              onChange={(e) => setDtSlug(e.target.value)}
              placeholder="switch"
              required
              pattern="[a-z0-9]+(-[a-z0-9]+)*"
              title={t("dcim.sites.slugPatternTitle")}
            />
          </label>
          <label>
            {t("dcim.equip.mfr.description")}
            <input value={dtDesc} onChange={(e) => setDtDesc(e.target.value)} />
          </label>
          <button type="submit" className={styles.btn} disabled={createDt.isPending}>
            {createDt.isPending ? "…" : t("dcim.common.add")}
          </button>
        </form>
        {deviceTypesQ.isLoading ? <p className={styles.muted}>{t("dcim.common.loading")}</p> : null}
        {deviceTypesQ.data && deviceTypesQ.data.length > 0 ? (
          <table className={styles.table}>
            <thead>
              <tr>
                <th>{t("dcim.equip.dt.iconCol")}</th>
                <th>{t("dcim.common.name")}</th>
                <th>{t("dcim.equip.dt.slug")}</th>
                <th scope="col">
                  <span className="sr-only">{t("dcim.equip.actionsCol")}</span>
                </th>
              </tr>
            </thead>
            <tbody>
              {deviceTypesQ.data.map((x) => (
                <tr key={x.id}>
                  <td className={styles.mfrLogoCell} aria-hidden>
                    <i className={`fas ${deviceTypeFaIconClass(x.slug)}`} />
                  </td>
                  <td>
                    <Link to={`/dcim/equipment/device-types/${x.id}`} className={styles.tableLink}>
                      {x.name}
                    </Link>
                  </td>
                  <td>
                    <code>{x.slug}</code>
                  </td>
                  <td>
                    <div className={styles.tableIconActions}>
                      <button
                        type="button"
                        className={`${styles.tableIconBtn} ${styles.tableIconBtnDanger}`.trim()}
                        title={t("dcim.common.delete")}
                        aria-label={t("dcim.equip.dt.deleteTypeAria", { name: x.name })}
                        disabled={delDt.isPending}
                        onClick={() => setDtPendingDelete({ id: x.id, name: x.name })}
                      >
                        <i className="fas fa-trash-can" aria-hidden />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          !deviceTypesQ.isLoading && <p className={styles.muted}>{t("dcim.equip.dt.empty")}</p>
        )}
        </>
      ) : null}
      {equipTab === "dm" ? (
        <>
          <div className={styles.formRow} style={{ alignItems: "center", flexWrap: "wrap", marginTop: 0 }}>
            <Link
              to="/dcim/equipment/device-models/new"
              className={styles.btn}
              aria-label={t("dcim.equip.dm.newButtonAria")}
            >
              <i className="fas fa-plus" aria-hidden /> {t("dcim.equip.dm.newButton")}
            </Link>
          </div>
          <p className={styles.muted} style={{ marginTop: "var(--space-2)" }}>
            {t("dcim.equip.dm.listHint")}
          </p>
          <div className={styles.formRow} style={{ marginTop: "var(--space-3)", alignItems: "flex-end" }}>
            <label style={{ flex: "1 1 14rem" }}>
              {t("dcim.equip.dm.matchSnmpLabel")}
              <input
                value={dmMatchOid}
                onChange={(e) => {
                  setDmMatchOid(e.target.value);
                  setDmMatchResult(null);
                }}
                placeholder={t("dcim.equip.dm.matchSnmpPlaceholder")}
                spellCheck={false}
              />
            </label>
            <button
              type="button"
              className={styles.btn}
              disabled={dmMatchOid.trim() === ""}
              onClick={() => {
                setErr(null);
                void api.matchDeviceModelsBySnmpOid(dmMatchOid.trim()).then(setDmMatchResult).catch((e: Error) => {
                  setDmMatchResult(null);
                  setErr(e instanceof ApiError ? e.message : e.message);
                });
              }}
            >
              {t("dcim.equip.dm.matchSnmpRun")}
            </button>
          </div>
          {dmMatchResult != null ? (
            dmMatchResult.length === 0 ? (
              <p className={styles.muted}>{t("dcim.equip.dm.matchSnmpEmpty")}</p>
            ) : (
              <div className={styles.mfrDetailSection} style={{ marginTop: "var(--space-2)" }}>
                <p className={styles.muted} style={{ marginTop: 0 }}>
                  {t("dcim.equip.dm.matchSnmpResult")}
                </p>
                <ul className={styles.ipList}>
                  {dmMatchResult.map((m) => (
                    <li key={m.id}>
                      <Link to={`/dcim/equipment/device-models/${m.id}`} className={styles.tableLink}>
                        {m.name}
                      </Link>{" "}
                      <span className={styles.muted}>
                        (<code>{m.snmp_sys_object_id_prefix ?? "—"}</code>)
                      </span>
                    </li>
                  ))}
                </ul>
              </div>
            )
          ) : null}
          {modelsQ.isLoading ? <p className={styles.muted}>{t("dcim.common.loading")}</p> : null}
          {modelsQ.data && modelsQ.data.length > 0 ? (
            <table className={styles.table}>
              <thead>
                <tr>
                  <th>{t("dcim.equip.dm.thumbCol")}</th>
                  <th>{t("dcim.common.name")}</th>
                  <th>{t("dcim.equip.dm.mfrCol")}</th>
                  <th>{t("dcim.equip.dm.typeCol")}</th>
                  <th>{t("dcim.equip.dm.u")}</th>
                  <th>{t("dcim.equip.dm.snmpOidPrefix")}</th>
                </tr>
              </thead>
              <tbody>
                {modelsQ.data.map((x) => {
                  const src = deviceModelListThumbSrc(x);
                  const pfx = x.snmp_sys_object_id_prefix ?? "";
                  const pfxShort = pfx.length > 28 ? `${pfx.slice(0, 28)}…` : pfx;
                  const dtId = x.device_type_id;
                  return (
                    <tr key={x.id}>
                      <td className={styles.mfrLogoCell}>
                        {src ? (
                          <img src={src} alt="" className={styles.mfrLogoThumb} />
                        ) : (
                          <span className={styles.muted}>—</span>
                        )}
                      </td>
                      <td>
                        <Link to={`/dcim/equipment/device-models/${x.id}`} className={styles.tableLink}>
                          {x.name}
                        </Link>
                      </td>
                      <td>
                        {x.manufacturer_id != null ? (
                          <Link
                            to={`/dcim/equipment/manufacturers/${x.manufacturer_id}`}
                            className={styles.tableLink}
                          >
                            {manufacturersById.get(x.manufacturer_id) ?? `#${x.manufacturer_id}`}
                          </Link>
                        ) : (
                          "—"
                        )}
                      </td>
                      <td>
                        {dtId != null ? (
                          <Link
                            to={`/dcim/equipment/device-types/${dtId}`}
                            className={styles.tableLink}
                            title={deviceTypesById.get(dtId)?.slug}
                          >
                            {deviceTypesById.get(dtId)?.name ?? `#${dtId}`}
                          </Link>
                        ) : (
                          "—"
                        )}
                      </td>
                      <td>{x.u_height}</td>
                      <td title={pfx || undefined}>{pfxShort !== "" ? <code>{pfxShort}</code> : "—"}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          ) : (
            !modelsQ.isLoading && <p className={styles.muted}>{t("dcim.equip.dm.empty")}</p>
          )}
        </>
      ) : null}
      {equipTab === "dev" ? (
        <>
          <div className={styles.formRow} style={{ alignItems: "center", flexWrap: "wrap", marginTop: 0 }}>
            <Link
              to="/dcim/equipment/devices/new"
              className={styles.btn}
              aria-label={t("dcim.equip.dev.newButtonAria")}
            >
              <i className="fas fa-plus" aria-hidden /> {t("dcim.equip.dev.newButton")}
            </Link>
          </div>
          <div className={styles.formRow} style={{ marginTop: "var(--space-2)" }}>
            <label style={{ flex: "1 1 16rem" }}>
              {t("dcim.equip.dev.filterList")}
              <input
                value={devListFilter}
                onChange={(e) => setDevListFilter(e.target.value)}
                placeholder={t("dcim.equip.dev.filterPlaceholder")}
              />
            </label>
          </div>
          {devicesQ.isLoading ? <p className={styles.muted}>{t("dcim.common.loading")}</p> : null}
          {devicesQ.data && devicesQ.data.length > 0 && filteredDevices.length === 0 ? (
            <p className={styles.muted}>{t("dcim.equip.dev.filterNoResults")}</p>
          ) : null}
          {filteredDevices.length > 0 ? (
            <table className={styles.table}>
              <thead>
                <tr>
                  <th>{t("dcim.equip.dev.iconCol")}</th>
                  <th>{t("dcim.common.name")}</th>
                  <th>{t("dcim.equip.dev.modelNameCol")}</th>
                  <th>{t("dcim.equip.dev.effectiveTypeCol")}</th>
                  <th>{t("dcim.equip.dev.placementCol")}</th>
                </tr>
              </thead>
              <tbody>
                {filteredDevices.map((x) => {
                  const pl = placementByDeviceId.get(x.id);
                  const r = pl ? racksById.get(pl.rack_id) : undefined;
                  const roomId = r?.room_id ?? "";
                  const eff = x.effective_device_type_id;
                  const effSlug = eff != null ? (deviceTypesById.get(eff)?.slug ?? "") : "";
                  const model = x.device_model_id != null ? modelsById.get(x.device_model_id) : undefined;
                  const thumb = deviceInstanceListThumbSrc(x, model);
                  return (
                    <tr key={x.id}>
                      <td className={styles.mfrLogoCell}>
                        {thumb ? (
                          <img src={thumb} alt="" className={styles.mfrLogoThumb} />
                        ) : (
                          <i className={`fas ${deviceTypeFaIconClass(effSlug)}`} aria-hidden />
                        )}
                      </td>
                      <td>
                        <Link to={`/dcim/equipment/devices/${x.id}`} className={styles.tableLink}>
                          {x.name}
                        </Link>
                      </td>
                      <td>
                        {model && x.device_model_id != null ? (
                          <Link
                            to={`/dcim/equipment/device-models/${x.device_model_id}`}
                            className={styles.tableLink}
                          >
                            {model.name}
                          </Link>
                        ) : (
                          "—"
                        )}
                      </td>
                      <td>
                        {eff != null ? (
                          <Link
                            to={`/dcim/equipment/device-types/${eff}`}
                            className={styles.tableLink}
                            title={deviceTypesById.get(eff)?.slug}
                          >
                            {deviceTypesById.get(eff)?.name ?? `#${eff}`}
                          </Link>
                        ) : (
                          "—"
                        )}
                      </td>
                      <td>
                        {pl ? (
                          <>
                            <span className={styles.muted}>
                              #{pl.rack_id} U{pl.u_position} ({pl.mounting})
                            </span>{" "}
                            <Link
                              to={`/dcim/racks?room=${roomId}&highlightPlacement=${pl.id}`}
                              className={styles.tableLink}
                            >
                              {t("dcim.equip.dev.openInRack")}
                            </Link>
                          </>
                        ) : (
                          "—"
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          ) : !devicesQ.isLoading && (!devicesQ.data || devicesQ.data.length === 0) ? (
            <p className={styles.muted}>{t("dcim.equip.dev.empty")}</p>
          ) : null}
        </>
      ) : null}
      {equipTab === "pl" ? (
        <>
        <div className={styles.formRow}>
          <label>
            {t("dcim.equip.pl.filterRack")}
            <input
              type="number"
              min={1}
              value={rackFilter}
              onChange={(e) => setRackFilter(e.target.value)}
              placeholder={t("dcim.common.all")}
            />
          </label>
        </div>
        <form
          className={styles.formRow}
          onSubmit={(e) => {
            e.preventDefault();
            setErr(null);
            if (!plRack || !plDev) {
              setErr(t("dcim.equip.pl.chooseRackDev"));
              return;
            }
            createPl.mutate();
          }}
        >
          <label>
            {t("dcim.common.rack")}
            <select value={plRack} onChange={(e) => setPlRack(e.target.value)} required>
              <option value="">{t("dcim.common.choose")}</option>
              {(racksQ.data ?? []).map((k) => (
                <option key={k.id} value={String(k.id)}>
                  #{k.id} {k.name} ({t("dcim.common.room")} {k.room_id})
                </option>
              ))}
            </select>
          </label>
          <label>
            {t("dcim.equip.pl.device")}
            <select value={plDev} onChange={(e) => setPlDev(e.target.value)} required>
              <option value="">{t("dcim.common.choose")}</option>
              {(devicesQ.data ?? []).map((d) => (
                <option key={d.id} value={String(d.id)}>
                  #{d.id} {d.name}
                </option>
              ))}
            </select>
          </label>
          <label>
            {t("dcim.equip.pl.uPos")}
            <input type="number" min={0} value={plU} onChange={(e) => setPlU(e.target.value)} />
          </label>
          <label>
            {t("dcim.equip.pl.mount")}
            <select value={plMount} onChange={(e) => setPlMount(e.target.value)}>
              <option value="front">{t("dcim.equip.mountFront")}</option>
              <option value="rear">{t("dcim.equip.mountRear")}</option>
            </select>
          </label>
          <button type="submit" className={styles.btn} disabled={createPl.isPending}>
            {createPl.isPending ? "…" : t("dcim.equip.pl.place")}
          </button>
        </form>
        <p className={styles.muted} style={{ marginTop: "var(--space-2)" }}>
          {t("dcim.equip.pl.uPosHint")}
        </p>
        {placementsQ.isLoading ? <p className={styles.muted}>{t("dcim.common.loading")}</p> : null}
        {placementsQ.data && placementsQ.data.length > 0 ? (
          <table className={styles.table}>
            <thead>
              <tr>
                <th>{t("dcim.equip.dev.iconCol")}</th>
                <th>{t("dcim.equip.pl.deviceCol")}</th>
                <th>{t("dcim.equip.pl.rackCol")}</th>
                <th>{t("dcim.equip.pl.uPos")}</th>
                <th>{t("dcim.equip.pl.mount")}</th>
                <th>{t("dcim.equip.pl.openInRack")}</th>
                <th />
              </tr>
            </thead>
            <tbody>
              {placementsQ.data.map((p) => {
                const devRow = devicesById.get(p.device_id);
                const eff = devRow?.effective_device_type_id;
                const effSlug = eff != null ? (deviceTypesById.get(eff)?.slug ?? "") : "";
                const model =
                  devRow?.device_model_id != null ? modelsById.get(devRow.device_model_id) : undefined;
                const thumb = devRow ? deviceInstanceListThumbSrc(devRow, model) : null;
                const rack = racksById.get(p.rack_id);
                return (
                  <tr key={p.id}>
                    <td className={styles.mfrLogoCell}>
                      {thumb ? (
                        <img src={thumb} alt="" className={styles.mfrLogoThumb} />
                      ) : devRow ? (
                        <i className={`fas ${deviceTypeFaIconClass(effSlug)}`} aria-hidden />
                      ) : (
                        <span className={styles.muted}>—</span>
                      )}
                    </td>
                    <td>
                      {devRow ? (
                        <Link to={`/dcim/equipment/devices/${devRow.id}`} className={styles.tableLink}>
                          {devRow.name}
                        </Link>
                      ) : (
                        `— (#${p.device_id})`
                      )}
                    </td>
                    <td>
                      {rack ? (
                        <>
                          <span className={styles.muted}>#{p.rack_id}</span> {rack.name}
                        </>
                      ) : (
                        `#${p.rack_id}`
                      )}
                    </td>
                    <td>{p.u_position}</td>
                    <td>{p.mounting}</td>
                    <td>
                      <Link
                        to={`/dcim/racks?room=${racksById.get(p.rack_id)?.room_id ?? ""}&highlightPlacement=${p.id}`}
                        className={styles.tableLink}
                      >
                        {t("dcim.equip.pl.openInRack")}
                      </Link>
                    </td>
                    <td>
                      <div className={styles.tableIconActions}>
                        <button
                          type="button"
                          className={`${styles.tableIconBtn} ${styles.tableIconBtnDanger}`.trim()}
                          title={t("dcim.common.remove")}
                          aria-label={t("dcim.equip.pl.removePlacementAria", { id: String(p.id) })}
                          disabled={delPl.isPending}
                          onClick={() => setPlPendingRemove(p)}
                        >
                          <i className="fas fa-link-slash" aria-hidden />
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        ) : (
          !placementsQ.isLoading && <p className={styles.muted}>{t("dcim.equip.pl.empty")}</p>
        )}
        </>
      ) : null}
    </Panel>
    <ConfirmModal
      open={mfrPendingDelete != null}
      onClose={() => {
        if (!delMfr.isPending) setMfrPendingDelete(null);
      }}
      title={mfrPendingDelete ? t("dcim.equip.mfr.deleteModalTitle", { name: mfrPendingDelete.name }) : ""}
      message={t("dcim.equip.mfr.deleteModalHint")}
      confirmLabel={t("dcim.common.delete")}
      cancelLabel={t("dcim.common.cancel")}
      danger
      pending={delMfr.isPending}
      onConfirm={() => {
        if (!mfrPendingDelete) return;
        delMfr.mutate(mfrPendingDelete.id, { onSettled: () => setMfrPendingDelete(null) });
      }}
    />
    <ConfirmModal
      open={dtPendingDelete != null}
      onClose={() => {
        if (!delDt.isPending) setDtPendingDelete(null);
      }}
      title={dtPendingDelete ? t("dcim.equip.dt.deleteModalTitle", { name: dtPendingDelete.name }) : ""}
      message={t("dcim.equip.dt.deleteModalHint")}
      confirmLabel={t("dcim.common.delete")}
      cancelLabel={t("dcim.common.cancel")}
      danger
      pending={delDt.isPending}
      onConfirm={() => {
        if (!dtPendingDelete) return;
        delDt.mutate(dtPendingDelete.id, { onSettled: () => setDtPendingDelete(null) });
      }}
    />
    <ConfirmModal
      open={plPendingRemove != null}
      onClose={() => {
        if (!delPl.isPending) setPlPendingRemove(null);
      }}
      title={t("dcim.equip.pl.removeModalTitle")}
      message={t("dcim.equip.pl.removeModalHint")}
      confirmLabel={t("dcim.common.remove")}
      cancelLabel={t("dcim.common.cancel")}
      danger
      pending={delPl.isPending}
      onConfirm={() => {
        if (!plPendingRemove) return;
        delPl.mutate(plPendingRemove.id, { onSettled: () => setPlPendingRemove(null) });
      }}
    />
    </>
  );
}
