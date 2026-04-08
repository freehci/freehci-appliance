import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { Panel } from "@/components/ui/Panel";
import { useI18n } from "@/i18n/I18nProvider";
import { ApiError } from "@/lib/api";
import * as api from "./dcimApi";
import styles from "./dcim.module.css";

export function DcimEquipmentPage() {
  const { t } = useI18n();
  const qc = useQueryClient();
  const [err, setErr] = useState<string | null>(null);

  const [mfrName, setMfrName] = useState("");
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

  const createMfr = useMutation({
    mutationFn: () => api.createManufacturer({ name: mfrName.trim() }),
    onSuccess: () => {
      setMfrName("");
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
    onSuccess: () => {
      setDmName("");
      setDmImgFront("");
      setDmImgBack("");
      setErr(null);
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
          <button type="submit" className={styles.btn} disabled={createMfr.isPending}>
            {createMfr.isPending ? "…" : t("dcim.common.add")}
          </button>
        </form>
        {manufacturersQ.isLoading ? <p className={styles.muted}>{t("dcim.common.loading")}</p> : null}
        {manufacturersQ.data && manufacturersQ.data.length > 0 ? (
          <table className={styles.table}>
            <thead>
              <tr>
                <th>{t("dcim.common.id")}</th>
                <th>{t("dcim.common.name")}</th>
                <th />
              </tr>
            </thead>
            <tbody>
              {manufacturersQ.data.map((x) => (
                <tr key={x.id}>
                  <td>{x.id}</td>
                  <td>{x.name}</td>
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

      <Panel title={t("dcim.equip.dm.title")}>
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
          <button type="submit" className={styles.btn} disabled={createDm.isPending}>
            {createDm.isPending ? "…" : t("dcim.equip.dm.create")}
          </button>
        </form>
        {modelsQ.isLoading ? <p className={styles.muted}>{t("dcim.common.loading")}</p> : null}
        {modelsQ.data && modelsQ.data.length > 0 ? (
          <table className={styles.table}>
            <thead>
              <tr>
                <th>{t("dcim.common.id")}</th>
                <th>{t("dcim.equip.dm.mfrCol")}</th>
                <th>{t("dcim.common.name")}</th>
                <th>{t("dcim.equip.dm.u")}</th>
              </tr>
            </thead>
            <tbody>
              {modelsQ.data.map((x) => (
                <tr key={x.id}>
                  <td>{x.id}</td>
                  <td>{x.manufacturer_id ?? "—"}</td>
                  <td>{x.name}</td>
                  <td>{x.u_height}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          !modelsQ.isLoading && <p className={styles.muted}>{t("dcim.equip.dm.empty")}</p>
        )}
      </Panel>

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
              </tr>
            </thead>
            <tbody>
              {devicesQ.data.map((x) => (
                <tr key={x.id}>
                  <td>{x.id}</td>
                  <td>{x.device_model_id ?? "—"}</td>
                  <td>{x.name}</td>
                </tr>
              ))}
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
