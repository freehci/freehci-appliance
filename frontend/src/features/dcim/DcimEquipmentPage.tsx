import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useId, useMemo, useRef, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { Panel } from "@/components/ui/Panel";
import { useI18n } from "@/i18n/I18nProvider";
import { ApiError } from "@/lib/api";
import * as api from "./dcimApi";
import { DcimInnerTabs } from "./DcimInnerTabs";
import styles from "./dcim.module.css";
import { deviceModelListThumbSrc } from "./modelImages";
import type { DeviceModel, Rack, RackPlacement } from "./types";

type EquipTab = "mfr" | "dt" | "dm" | "dev" | "pl";

export function DcimEquipmentPage() {
  const { t } = useI18n();
  const qc = useQueryClient();
  const [searchParams] = useSearchParams();
  const dmPanelRef = useRef<HTMLDivElement | null>(null);
  const devPanelRef = useRef<HTMLFormElement | null>(null);
  const dmFileFrontRef = useRef<HTMLInputElement | null>(null);
  const dmFileBackRef = useRef<HTMLInputElement | null>(null);
  const dmFileProductRef = useRef<HTMLInputElement | null>(null);
  const [err, setErr] = useState<string | null>(null);

  const [mfrName, setMfrName] = useState("");
  const [mfrDesc, setMfrDesc] = useState("");
  const [mfrUrl, setMfrUrl] = useState("");
  const [dmMfr, setDmMfr] = useState<string>("");
  const [dmDt, setDmDt] = useState<string>("");
  const [dmName, setDmName] = useState("");
  const [dmU, setDmU] = useState("1");
  const [dmImgFront, setDmImgFront] = useState("");
  const [dmImgBack, setDmImgBack] = useState("");
  const [dmImgProduct, setDmImgProduct] = useState("");
  const [dtName, setDtName] = useState("");
  const [dtSlug, setDtSlug] = useState("");
  const [dtDesc, setDtDesc] = useState("");
  const [devModel, setDevModel] = useState<string>("");
  const [devDt, setDevDt] = useState<string>("");
  const [devName, setDevName] = useState("");
  const [devAttrsJson, setDevAttrsJson] = useState("{}");
  const [plRack, setPlRack] = useState<string>("");
  const [plDev, setPlDev] = useState<string>("");
  const [plU, setPlU] = useState("1");
  const [dmSnmpPrefix, setDmSnmpPrefix] = useState("");
  const [dmEditId, setDmEditId] = useState<number | null>(null);
  const [dmEditName, setDmEditName] = useState("");
  const [dmEditU, setDmEditU] = useState("1");
  const [dmEditMfr, setDmEditMfr] = useState("");
  const [dmEditDt, setDmEditDt] = useState("");
  const [dmEditSnmp, setDmEditSnmp] = useState("");
  const [dmMatchOid, setDmMatchOid] = useState("");
  const [dmMatchResult, setDmMatchResult] = useState<DeviceModel[] | null>(null);
  const [plMount, setPlMount] = useState("front");
  const [rackFilter, setRackFilter] = useState<string>("");
  const [devListFilter, setDevListFilter] = useState("");
  const [equipTab, setEquipTab] = useState<EquipTab>("mfr");
  const [mfrPendingDelete, setMfrPendingDelete] = useState<{ id: number; name: string } | null>(null);
  const mfrDeleteTitleId = useId();

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
    const raw = searchParams.get("prefillManufacturer");
    if (raw == null || raw === "") return;
    const n = Number(raw);
    if (!Number.isFinite(n) || n < 1) return;
    setDmMfr(String(n));
    setEquipTab("dm");
    requestAnimationFrame(() =>
      dmPanelRef.current?.scrollIntoView({ behavior: "smooth", block: "start" }),
    );
  }, [searchParams]);

  useEffect(() => {
    const name = searchParams.get("prefillDeviceName")?.trim() ?? "";
    const snmpHost = searchParams.get("snmpHost")?.trim() ?? "";
    if (name === "" && snmpHost === "") return;

    if (name !== "") setDevName(name);
    if (snmpHost !== "") {
      setDevAttrsJson((prev) => {
        try {
          const raw = prev.trim() === "" ? "{}" : prev;
          const obj = JSON.parse(raw) as unknown;
          if (obj !== null && typeof obj === "object" && !Array.isArray(obj)) {
            return JSON.stringify({ ...(obj as Record<string, unknown>), snmp_host: snmpHost }, null, 2);
          }
        } catch {
          /* ignore */
        }
        return JSON.stringify({ snmp_host: snmpHost }, null, 2);
      });
    }
    setEquipTab("dev");
    requestAnimationFrame(() =>
      devPanelRef.current?.scrollIntoView({ behavior: "smooth", block: "start" }),
    );
  }, [searchParams]);

  useEffect(() => {
    if (!mfrPendingDelete) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") setMfrPendingDelete(null);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [mfrPendingDelete]);

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

  const createDm = useMutation({
    mutationFn: () => {
      const uN = Number(dmU);
      const u_height = Number.isFinite(uN) && uN >= 0 ? uN : 1;
      const snmp = dmSnmpPrefix.trim();
      return api.createDeviceModel({
        name: dmName.trim(),
        u_height,
        manufacturer_id: dmMfr === "" ? null : Number(dmMfr),
        device_type_id: dmDt === "" ? null : Number(dmDt),
        image_front_url: dmImgFront.trim() === "" ? null : dmImgFront.trim(),
        image_back_url: dmImgBack.trim() === "" ? null : dmImgBack.trim(),
        image_product_url: dmImgProduct.trim() === "" ? null : dmImgProduct.trim(),
        snmp_sys_object_id_prefix: snmp === "" ? null : snmp,
      });
    },
    onSuccess: async (created) => {
      const ff = dmFileFrontRef.current?.files?.[0];
      const fb = dmFileBackRef.current?.files?.[0];
      const fp = dmFileProductRef.current?.files?.[0];
      try {
        if (ff) await api.uploadDeviceModelImageFront(created.id, ff);
        if (fb) await api.uploadDeviceModelImageBack(created.id, fb);
        if (fp) await api.uploadDeviceModelImageProduct(created.id, fp);
        setErr(null);
      } catch (e) {
        setErr(e instanceof ApiError ? e.message : (e as Error).message);
      }
      setDmName("");
      setDmSnmpPrefix("");
      setDmImgFront("");
      setDmImgBack("");
      setDmImgProduct("");
      if (dmFileFrontRef.current) dmFileFrontRef.current.value = "";
      if (dmFileBackRef.current) dmFileBackRef.current.value = "";
      if (dmFileProductRef.current) dmFileProductRef.current.value = "";
      void qc.invalidateQueries({ queryKey: ["dcim", "device-models"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const patchDm = useMutation({
    mutationFn: () => {
      if (dmEditId == null) throw new Error("missing model");
      const uN = Number(dmEditU);
      const u_height = Number.isFinite(uN) && uN >= 0 ? uN : 1;
      const snmp = dmEditSnmp.trim();
      return api.updateDeviceModel(dmEditId, {
        name: dmEditName.trim(),
        u_height,
        manufacturer_id: dmEditMfr === "" ? null : Number(dmEditMfr),
        device_type_id: dmEditDt === "" ? null : Number(dmEditDt),
        snmp_sys_object_id_prefix: snmp === "" ? null : snmp,
      });
    },
    onSuccess: () => {
      setErr(null);
      setDmEditId(null);
      void qc.invalidateQueries({ queryKey: ["dcim", "device-models"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const createDev = useMutation({
    mutationFn: () => {
      let attrs: Record<string, unknown> | null = null;
      const raw = devAttrsJson.trim();
      if (raw !== "") {
        try {
          const parsed: unknown = JSON.parse(raw);
          if (parsed === null || typeof parsed !== "object" || Array.isArray(parsed)) {
            throw new Error(t("dcim.equip.dev.attributesInvalid"));
          }
          attrs = parsed as Record<string, unknown>;
        } catch {
          throw new Error(t("dcim.equip.dev.attributesInvalid"));
        }
      }
      return api.createDevice({
        name: devName.trim(),
        device_model_id: devModel === "" ? null : Number(devModel),
        device_type_id: devDt === "" ? null : Number(devDt),
        attributes: attrs,
      });
    },
    onSuccess: () => {
      setDevName("");
      setDevDt("");
      setDevAttrsJson("{}");
      setErr(null);
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
                <th>{t("dcim.common.id")}</th>
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
                  <td>{x.id}</td>
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
                <th>{t("dcim.common.id")}</th>
                <th>{t("dcim.common.name")}</th>
                <th>{t("dcim.equip.dt.slug")}</th>
                <th />
              </tr>
            </thead>
            <tbody>
              {deviceTypesQ.data.map((x) => (
                <tr key={x.id}>
                  <td>{x.id}</td>
                  <td>{x.name}</td>
                  <td>
                    <code>{x.slug}</code>
                  </td>
                  <td>
                    <button
                      type="button"
                      className={styles.btnDanger}
                      onClick={() => delDt.mutate(x.id)}
                      disabled={delDt.isPending}
                    >
                      {t("dcim.common.delete")}
                    </button>
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
        <div ref={dmPanelRef}>
          <p className={styles.muted} style={{ marginTop: 0 }}>
            {t("dcim.equip.dm.uploadHint")}
          </p>
        <form
          className={styles.formRow}
          onSubmit={(e) => {
            e.preventDefault();
            setErr(null);
            createDm.mutate();
          }}
        >
          <label>
            {t("dcim.equip.dm.mfr")}
            <select value={dmMfr} onChange={(e) => setDmMfr(e.target.value)}>
              <option value="">{t("dcim.common.none")}</option>
              {(manufacturersQ.data ?? []).map((m) => (
                <option key={m.id} value={String(m.id)}>
                  {m.name}
                </option>
              ))}
            </select>
          </label>
          <label>
            {t("dcim.equip.dm.dt")}
            <select value={dmDt} onChange={(e) => setDmDt(e.target.value)}>
              <option value="">{t("dcim.common.none")}</option>
              {(deviceTypesQ.data ?? []).map((d) => (
                <option key={d.id} value={String(d.id)}>
                  {d.name} ({d.slug})
                </option>
              ))}
            </select>
          </label>
          <label>
            {t("dcim.equip.dm.modelName")}
            <input value={dmName} onChange={(e) => setDmName(e.target.value)} required />
          </label>
          <label>
            {t("dcim.equip.dm.u")}
            <input type="number" min={0} max={64} value={dmU} onChange={(e) => setDmU(e.target.value)} />
          </label>
          <label title={t("dcim.equip.dm.snmpOidPrefixHint")}>
            {t("dcim.equip.dm.snmpOidPrefix")}
            <input
              value={dmSnmpPrefix}
              onChange={(e) => setDmSnmpPrefix(e.target.value)}
              placeholder="1.3.6.1.4.1.…"
              spellCheck={false}
            />
          </label>
          <label>
            {t("dcim.equip.dm.imageFront")}
            <input
              type="url"
              value={dmImgFront}
              onChange={(e) => setDmImgFront(e.target.value)}
              placeholder="https://"
            />
          </label>
          <label>
            {t("dcim.equip.dm.imageBack")}
            <input
              type="url"
              value={dmImgBack}
              onChange={(e) => setDmImgBack(e.target.value)}
              placeholder="https://"
            />
          </label>
          <label>
            {t("dcim.equip.dm.imageProduct")}
            <input
              type="url"
              value={dmImgProduct}
              onChange={(e) => setDmImgProduct(e.target.value)}
              placeholder="https://"
              title={t("dcim.equip.dm.imageProductHint")}
            />
          </label>
          <label>
            {t("dcim.equip.dm.imageFrontFile")}
            <input
              ref={dmFileFrontRef}
              type="file"
              accept="image/png,image/jpeg,image/webp,image/svg+xml"
            />
          </label>
          <label>
            {t("dcim.equip.dm.imageBackFile")}
            <input
              ref={dmFileBackRef}
              type="file"
              accept="image/png,image/jpeg,image/webp,image/svg+xml"
            />
          </label>
          <label>
            {t("dcim.equip.dm.imageProductFile")}
            <input
              ref={dmFileProductRef}
              type="file"
              accept="image/png,image/jpeg,image/webp,image/svg+xml"
              title={t("dcim.equip.dm.imageProductHint")}
            />
          </label>
          <button type="submit" className={styles.btn} disabled={createDm.isPending}>
            {createDm.isPending ? "…" : t("dcim.equip.dm.create")}
          </button>
        </form>
        <p className={styles.muted} style={{ marginTop: "var(--space-2)" }}>
          {t("dcim.equip.dm.uHintZero")}
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
                    <code>#{m.id}</code> {m.name}{" "}
                    <span className={styles.muted}>
                      ({m.snmp_sys_object_id_prefix ?? "—"})
                    </span>
                  </li>
                ))}
              </ul>
            </div>
          )
        ) : null}
        {dmEditId != null ? (
          <section className={styles.mfrDetailSection} style={{ marginTop: "var(--space-4)" }}>
            <h3 className={styles.mfrDetailSectionTitle}>
              {t("dcim.equip.dm.editTitle")} #{dmEditId}
            </h3>
            <form
              className={styles.formRow}
              onSubmit={(e) => {
                e.preventDefault();
                setErr(null);
                patchDm.mutate();
              }}
            >
              <label>
                {t("dcim.equip.dm.mfr")}
                <select value={dmEditMfr} onChange={(e) => setDmEditMfr(e.target.value)}>
                  <option value="">{t("dcim.common.none")}</option>
                  {(manufacturersQ.data ?? []).map((m) => (
                    <option key={m.id} value={String(m.id)}>
                      {m.name}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                {t("dcim.equip.dm.dt")}
                <select value={dmEditDt} onChange={(e) => setDmEditDt(e.target.value)}>
                  <option value="">{t("dcim.common.none")}</option>
                  {(deviceTypesQ.data ?? []).map((d) => (
                    <option key={d.id} value={String(d.id)}>
                      {d.name} ({d.slug})
                    </option>
                  ))}
                </select>
              </label>
              <label>
                {t("dcim.equip.dm.modelName")}
                <input value={dmEditName} onChange={(e) => setDmEditName(e.target.value)} required />
              </label>
              <label>
                {t("dcim.equip.dm.u")}
                <input
                  type="number"
                  min={0}
                  max={64}
                  value={dmEditU}
                  onChange={(e) => setDmEditU(e.target.value)}
                />
              </label>
              <label title={t("dcim.equip.dm.snmpOidPrefixHint")}>
                {t("dcim.equip.dm.snmpOidPrefix")}
                <input
                  value={dmEditSnmp}
                  onChange={(e) => setDmEditSnmp(e.target.value)}
                  placeholder="1.3.6.1.4.1.…"
                  spellCheck={false}
                />
              </label>
              <button type="submit" className={styles.btn} disabled={patchDm.isPending}>
                {patchDm.isPending ? "…" : t("dcim.equip.dm.editSave")}
              </button>
              <button
                type="button"
                className={styles.btn}
                disabled={patchDm.isPending}
                onClick={() => setDmEditId(null)}
              >
                {t("dcim.equip.dm.editCancel")}
              </button>
            </form>
          </section>
        ) : null}
        {modelsQ.isLoading ? <p className={styles.muted}>{t("dcim.common.loading")}</p> : null}
        {modelsQ.data && modelsQ.data.length > 0 ? (
          <table className={styles.table}>
            <thead>
              <tr>
                <th>{t("dcim.equip.dm.thumbCol")}</th>
                <th>{t("dcim.common.id")}</th>
                <th>{t("dcim.equip.dm.mfrCol")}</th>
                <th>{t("dcim.equip.dm.typeCol")}</th>
                <th>{t("dcim.common.name")}</th>
                <th>{t("dcim.equip.dm.u")}</th>
                <th>{t("dcim.equip.dm.snmpOidPrefix")}</th>
                <th>{t("dcim.equip.dm.actionsCol")}</th>
              </tr>
            </thead>
            <tbody>
              {modelsQ.data.map((x) => {
                const src = deviceModelListThumbSrc(x);
                const pfx = x.snmp_sys_object_id_prefix ?? "";
                const pfxShort = pfx.length > 28 ? `${pfx.slice(0, 28)}…` : pfx;
                return (
                  <tr key={x.id}>
                    <td className={styles.mfrLogoCell}>
                      {src ? (
                        <img src={src} alt="" className={styles.mfrLogoThumb} />
                      ) : (
                        <span className={styles.muted}>—</span>
                      )}
                    </td>
                    <td>{x.id}</td>
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
                      {x.device_type_id != null ? (
                        <span title={deviceTypesById.get(x.device_type_id)?.slug}>
                          {deviceTypesById.get(x.device_type_id)?.name ?? `#${x.device_type_id}`}
                        </span>
                      ) : (
                        "—"
                      )}
                    </td>
                    <td>{x.name}</td>
                    <td>{x.u_height}</td>
                    <td title={pfx || undefined}>{pfxShort !== "" ? <code>{pfxShort}</code> : "—"}</td>
                    <td>
                      <button
                        type="button"
                        className={styles.btn}
                        onClick={() => {
                          setErr(null);
                          setDmEditId(x.id);
                          setDmEditName(x.name);
                          setDmEditU(String(x.u_height));
                          setDmEditMfr(x.manufacturer_id != null ? String(x.manufacturer_id) : "");
                          setDmEditDt(x.device_type_id != null ? String(x.device_type_id) : "");
                          setDmEditSnmp(x.snmp_sys_object_id_prefix ?? "");
                        }}
                      >
                        {t("dcim.equip.dm.edit")}
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        ) : (
          !modelsQ.isLoading && <p className={styles.muted}>{t("dcim.equip.dm.empty")}</p>
        )}
        </div>
      ) : null}
      {equipTab === "dev" ? (
        <>
        <form
          ref={devPanelRef}
          className={styles.formRow}
          onSubmit={(e) => {
            e.preventDefault();
            setErr(null);
            createDev.mutate();
          }}
        >
          <label>
            {t("dcim.equip.dev.model")}
            <select value={devModel} onChange={(e) => setDevModel(e.target.value)}>
              <option value="">{t("dcim.common.none")}</option>
              {(modelsQ.data ?? []).map((x) => (
                <option key={x.id} value={String(x.id)}>
                  {x.name}
                </option>
              ))}
            </select>
          </label>
          <label>
            {t("dcim.equip.dev.dtOverride")}
            <select value={devDt} onChange={(e) => setDevDt(e.target.value)}>
              <option value="">{t("dcim.equip.dev.dtInherit")}</option>
              {(deviceTypesQ.data ?? []).map((d) => (
                <option key={d.id} value={String(d.id)}>
                  {d.name}
                </option>
              ))}
            </select>
          </label>
          <label>
            {t("dcim.equip.dev.hostname")}
            <input value={devName} onChange={(e) => setDevName(e.target.value)} required />
          </label>
          <label style={{ minWidth: "12rem", flex: "1 1 280px" }}>
            {t("dcim.equip.dev.attributesJson")}
            <textarea
              value={devAttrsJson}
              onChange={(e) => setDevAttrsJson(e.target.value)}
              rows={3}
              className={styles.mfrTextarea}
              placeholder='{"os":"Linux"}'
              spellCheck={false}
            />
          </label>
          <button type="submit" className={styles.btn} disabled={createDev.isPending}>
            {createDev.isPending ? "…" : t("dcim.equip.dev.create")}
          </button>
        </form>
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
                <th>{t("dcim.common.id")}</th>
                <th>{t("dcim.equip.dev.modelCol")}</th>
                <th>{t("dcim.equip.dev.effectiveTypeCol")}</th>
                <th>{t("dcim.common.name")}</th>
                <th>{t("dcim.equip.dev.placementCol")}</th>
              </tr>
            </thead>
            <tbody>
              {filteredDevices.map((x) => {
                const pl = placementByDeviceId.get(x.id);
                const r = pl ? racksById.get(pl.rack_id) : undefined;
                const roomId = r?.room_id ?? "";
                const eff = x.effective_device_type_id;
                return (
                  <tr key={x.id}>
                    <td>{x.id}</td>
                    <td>{x.device_model_id ?? "—"}</td>
                    <td>
                      {eff != null ? (
                        <span title={deviceTypesById.get(eff)?.slug}>
                          {deviceTypesById.get(eff)?.name ?? `#${eff}`}
                        </span>
                      ) : (
                        "—"
                      )}
                    </td>
                    <td>
                      <Link to={`/dcim/equipment/devices/${x.id}`} className={styles.tableLink}>
                        {x.name}
                      </Link>
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
                <th>{t("dcim.common.id")}</th>
                <th>{t("dcim.common.rack")}</th>
                <th>{t("dcim.equip.pl.device")}</th>
                <th>{t("dcim.equip.pl.uPos")}</th>
                <th>{t("dcim.equip.pl.mount")}</th>
                <th>{t("dcim.equip.pl.openInRack")}</th>
                <th />
              </tr>
            </thead>
            <tbody>
              {placementsQ.data.map((p) => (
                <tr key={p.id}>
                  <td>{p.id}</td>
                  <td>{p.rack_id}</td>
                  <td>{p.device_id}</td>
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
                    <button
                      type="button"
                      className={styles.btnDanger}
                      onClick={() => delPl.mutate(p.id)}
                      disabled={delPl.isPending}
                    >
                      {t("dcim.common.remove")}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          !placementsQ.isLoading && <p className={styles.muted}>{t("dcim.equip.pl.empty")}</p>
        )}
        </>
      ) : null}
    </Panel>
    {mfrPendingDelete ? (
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
          if (e.target === e.currentTarget) setMfrPendingDelete(null);
        }}
      >
        <div
          role="dialog"
          aria-modal="true"
          aria-labelledby={mfrDeleteTitleId}
          style={{
            width: "min(28rem, 100%)",
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
          <h2 id={mfrDeleteTitleId} style={{ marginTop: 0 }}>
            {t("dcim.equip.mfr.deleteModalTitle", { name: mfrPendingDelete.name })}
          </h2>
          <p className={styles.muted} style={{ marginTop: 0 }}>
            {t("dcim.equip.mfr.deleteModalHint")}
          </p>
          <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem", marginTop: "var(--space-3)" }}>
            <button
              type="button"
              className={styles.btnDanger}
              disabled={delMfr.isPending}
              onClick={() => {
                const id = mfrPendingDelete.id;
                delMfr.mutate(id, {
                  onSettled: () => setMfrPendingDelete(null),
                });
              }}
            >
              {delMfr.isPending ? "…" : t("dcim.common.delete")}
            </button>
            <button
              type="button"
              className={styles.btnMuted}
              onClick={() => setMfrPendingDelete(null)}
              disabled={delMfr.isPending}
            >
              {t("dcim.common.cancel")}
            </button>
          </div>
        </div>
      </div>
    ) : null}
    </>
  );
}
