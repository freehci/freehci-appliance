import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useMemo, useRef, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { Panel } from "@/components/ui/Panel";
import { useI18n } from "@/i18n/I18nProvider";
import { ApiError } from "@/lib/api";
import * as api from "./dcimApi";
import styles from "./dcim.module.css";
import { deviceModelFrontSrc } from "./modelImages";
import type { Rack, RackPlacement } from "./types";

export function DcimEquipmentPage() {
  const { t } = useI18n();
  const qc = useQueryClient();
  const [searchParams] = useSearchParams();
  const dmPanelRef = useRef<HTMLDivElement | null>(null);
  const dmFileFrontRef = useRef<HTMLInputElement | null>(null);
  const dmFileBackRef = useRef<HTMLInputElement | null>(null);
  const [err, setErr] = useState<string | null>(null);

  const [mfrName, setMfrName] = useState("");
  const [mfrDesc, setMfrDesc] = useState("");
  const [mfrUrl, setMfrUrl] = useState("");
  const [dmMfr, setDmMfr] = useState<string>("");
  const [dmName, setDmName] = useState("");
  const [dmU, setDmU] = useState("1");
  const [dmImgFront, setDmImgFront] = useState("");
  const [dmImgBack, setDmImgBack] = useState("");
  const [devModel, setDevModel] = useState<string>("");
  const [devName, setDevName] = useState("");
  const [plRack, setPlRack] = useState<string>("");
  const [plDev, setPlDev] = useState<string>("");
  const [plU, setPlU] = useState("1");
  const [plMount, setPlMount] = useState("front");
  const [rackFilter, setRackFilter] = useState<string>("");

  const manufacturersQ = useQuery({
    queryKey: ["dcim", "manufacturers"],
    queryFn: api.listManufacturers,
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

  useEffect(() => {
    const raw = searchParams.get("prefillManufacturer");
    if (raw == null || raw === "") return;
    const n = Number(raw);
    if (!Number.isFinite(n) || n < 1) return;
    setDmMfr(String(n));
    requestAnimationFrame(() =>
      dmPanelRef.current?.scrollIntoView({ behavior: "smooth", block: "start" }),
    );
  }, [searchParams]);

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

  const createDm = useMutation({
    mutationFn: () =>
      api.createDeviceModel({
        name: dmName.trim(),
        u_height: Number(dmU) || 1,
        manufacturer_id: dmMfr === "" ? null : Number(dmMfr),
        image_front_url: dmImgFront.trim() === "" ? null : dmImgFront.trim(),
        image_back_url: dmImgBack.trim() === "" ? null : dmImgBack.trim(),
      }),
    onSuccess: async (created) => {
      const ff = dmFileFrontRef.current?.files?.[0];
      const fb = dmFileBackRef.current?.files?.[0];
      try {
        if (ff) await api.uploadDeviceModelImageFront(created.id, ff);
        if (fb) await api.uploadDeviceModelImageBack(created.id, fb);
        setErr(null);
      } catch (e) {
        setErr(e instanceof ApiError ? e.message : (e as Error).message);
      }
      setDmName("");
      setDmImgFront("");
      setDmImgBack("");
      if (dmFileFrontRef.current) dmFileFrontRef.current.value = "";
      if (dmFileBackRef.current) dmFileBackRef.current.value = "";
      void qc.invalidateQueries({ queryKey: ["dcim", "device-models"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const createDev = useMutation({
    mutationFn: () =>
      api.createDevice({
        name: devName.trim(),
        device_model_id: devModel === "" ? null : Number(devModel),
      }),
    onSuccess: () => {
      setDevName("");
      setErr(null);
      void qc.invalidateQueries({ queryKey: ["dcim", "devices"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const createPl = useMutation({
    mutationFn: () =>
      api.createPlacement({
        rack_id: Number(plRack),
        device_id: Number(plDev),
        u_position: Number(plU) || 1,
        mounting: plMount,
      }),
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
      <Panel title={t("dcim.equip.introTitle")}>
        {err ? <p className={styles.err}>{err}</p> : null}
        <p className={styles.muted} style={{ marginTop: 0 }}>
          {t("dcim.equip.introBody")}
        </p>
      </Panel>

      <Panel title={t("dcim.equip.mfr.title")}>
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
                <th />
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
                    <button
                      type="button"
                      className={styles.btnDanger}
                      onClick={() => delMfr.mutate(x.id)}
                      disabled={delMfr.isPending}
                    >
                      {t("dcim.common.delete")}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          !manufacturersQ.isLoading && <p className={styles.muted}>{t("dcim.equip.mfr.empty")}</p>
        )}
      </Panel>

      <div ref={dmPanelRef}>
        <Panel title={t("dcim.equip.dm.title")}>
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
            {t("dcim.equip.dm.modelName")}
            <input value={dmName} onChange={(e) => setDmName(e.target.value)} required />
          </label>
          <label>
            {t("dcim.equip.dm.u")}
            <input type="number" min={1} max={64} value={dmU} onChange={(e) => setDmU(e.target.value)} />
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
          <button type="submit" className={styles.btn} disabled={createDm.isPending}>
            {createDm.isPending ? "…" : t("dcim.equip.dm.create")}
          </button>
        </form>
        {modelsQ.isLoading ? <p className={styles.muted}>{t("dcim.common.loading")}</p> : null}
        {modelsQ.data && modelsQ.data.length > 0 ? (
          <table className={styles.table}>
            <thead>
              <tr>
                <th>{t("dcim.equip.dm.thumbCol")}</th>
                <th>{t("dcim.common.id")}</th>
                <th>{t("dcim.equip.dm.mfrCol")}</th>
                <th>{t("dcim.common.name")}</th>
                <th>{t("dcim.equip.dm.u")}</th>
              </tr>
            </thead>
            <tbody>
              {modelsQ.data.map((x) => {
                const src = deviceModelFrontSrc(x);
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
                    <td>{x.name}</td>
                    <td>{x.u_height}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        ) : (
          !modelsQ.isLoading && <p className={styles.muted}>{t("dcim.equip.dm.empty")}</p>
        )}
        </Panel>
      </div>

      <Panel title={t("dcim.equip.dev.title")}>
        <form
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
            {t("dcim.equip.dev.hostname")}
            <input value={devName} onChange={(e) => setDevName(e.target.value)} required />
          </label>
          <button type="submit" className={styles.btn} disabled={createDev.isPending}>
            {createDev.isPending ? "…" : t("dcim.equip.dev.create")}
          </button>
        </form>
        {devicesQ.isLoading ? <p className={styles.muted}>{t("dcim.common.loading")}</p> : null}
        {devicesQ.data && devicesQ.data.length > 0 ? (
          <table className={styles.table}>
            <thead>
              <tr>
                <th>{t("dcim.common.id")}</th>
                <th>{t("dcim.equip.dev.modelCol")}</th>
                <th>{t("dcim.common.name")}</th>
                <th>{t("dcim.equip.dev.placementCol")}</th>
              </tr>
            </thead>
            <tbody>
              {devicesQ.data.map((x) => {
                const pl = placementByDeviceId.get(x.id);
                const r = pl ? racksById.get(pl.rack_id) : undefined;
                const roomId = r?.room_id ?? "";
                return (
                  <tr key={x.id}>
                    <td>{x.id}</td>
                    <td>{x.device_model_id ?? "—"}</td>
                    <td>{x.name}</td>
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
        ) : (
          !devicesQ.isLoading && <p className={styles.muted}>{t("dcim.equip.dev.empty")}</p>
        )}
      </Panel>

      <Panel title={t("dcim.equip.pl.title")}>
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
            <input type="number" min={1} value={plU} onChange={(e) => setPlU(e.target.value)} />
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
      </Panel>
    </>
  );
}
