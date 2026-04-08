import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { Panel } from "@/components/ui/Panel";
import { ApiError } from "@/lib/api";
import * as api from "./dcimApi";
import styles from "./dcim.module.css";

export function DcimEquipmentPage() {
  const qc = useQueryClient();
  const [err, setErr] = useState<string | null>(null);

  const [mfrName, setMfrName] = useState("");
  const [dmMfr, setDmMfr] = useState<string>("");
  const [dmName, setDmName] = useState("");
  const [dmU, setDmU] = useState("1");
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
      }),
    onSuccess: () => {
      setDmName("");
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
      <Panel title="Utstyr">
        {err ? <p className={styles.err}>{err}</p> : null}
        <p className={styles.muted} style={{ marginTop: 0 }}>
          Produsenter, modeller, enheter og rack-plassering. Dobbelt plassering av samme enhet i samme rack avvises av
          API-et.
        </p>
      </Panel>

      <Panel title="Produsenter">
        <form
          className={styles.formRow}
          onSubmit={(e) => {
            e.preventDefault();
            setErr(null);
            createMfr.mutate();
          }}
        >
          <label>
            Navn
            <input value={mfrName} onChange={(e) => setMfrName(e.target.value)} required />
          </label>
          <button type="submit" className={styles.btn} disabled={createMfr.isPending}>
            {createMfr.isPending ? "…" : "Legg til"}
          </button>
        </form>
        {manufacturersQ.isLoading ? <p className={styles.muted}>Laster…</p> : null}
        {manufacturersQ.data && manufacturersQ.data.length > 0 ? (
          <table className={styles.table}>
            <thead>
              <tr>
                <th>ID</th>
                <th>Navn</th>
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
                      Slett
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          !manufacturersQ.isLoading && <p className={styles.muted}>Ingen produsenter.</p>
        )}
      </Panel>

      <Panel title="Enhetsmodeller">
        <form
          className={styles.formRow}
          onSubmit={(e) => {
            e.preventDefault();
            setErr(null);
            createDm.mutate();
          }}
        >
          <label>
            Produsent
            <select value={dmMfr} onChange={(e) => setDmMfr(e.target.value)}>
              <option value="">— ingen —</option>
              {(manufacturersQ.data ?? []).map((m) => (
                <option key={m.id} value={String(m.id)}>
                  {m.name}
                </option>
              ))}
            </select>
          </label>
          <label>
            Modellnavn
            <input value={dmName} onChange={(e) => setDmName(e.target.value)} required />
          </label>
          <label>
            U-høyde
            <input type="number" min={1} max={64} value={dmU} onChange={(e) => setDmU(e.target.value)} />
          </label>
          <button type="submit" className={styles.btn} disabled={createDm.isPending}>
            {createDm.isPending ? "…" : "Opprett modell"}
          </button>
        </form>
        {modelsQ.isLoading ? <p className={styles.muted}>Laster…</p> : null}
        {modelsQ.data && modelsQ.data.length > 0 ? (
          <table className={styles.table}>
            <thead>
              <tr>
                <th>ID</th>
                <th>Prod.</th>
                <th>Navn</th>
                <th>U</th>
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
          !modelsQ.isLoading && <p className={styles.muted}>Ingen modeller.</p>
        )}
      </Panel>

      <Panel title="Enheter">
        <form
          className={styles.formRow}
          onSubmit={(e) => {
            e.preventDefault();
            setErr(null);
            createDev.mutate();
          }}
        >
          <label>
            Modell
            <select value={devModel} onChange={(e) => setDevModel(e.target.value)}>
              <option value="">— ingen —</option>
              {(modelsQ.data ?? []).map((x) => (
                <option key={x.id} value={String(x.id)}>
                  {x.name}
                </option>
              ))}
            </select>
          </label>
          <label>
            Navn / hostname
            <input value={devName} onChange={(e) => setDevName(e.target.value)} required />
          </label>
          <button type="submit" className={styles.btn} disabled={createDev.isPending}>
            {createDev.isPending ? "…" : "Opprett enhet"}
          </button>
        </form>
        {devicesQ.isLoading ? <p className={styles.muted}>Laster…</p> : null}
        {devicesQ.data && devicesQ.data.length > 0 ? (
          <table className={styles.table}>
            <thead>
              <tr>
                <th>ID</th>
                <th>Modell ID</th>
                <th>Navn</th>
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
          !devicesQ.isLoading && <p className={styles.muted}>Ingen enheter.</p>
        )}
      </Panel>

      <Panel title="Plasseringer i rack">
        <div className={styles.formRow}>
          <label>
            Filtrer på rack-ID
            <input
              type="number"
              min={1}
              value={rackFilter}
              onChange={(e) => setRackFilter(e.target.value)}
              placeholder="alle"
            />
          </label>
        </div>
        <form
          className={styles.formRow}
          onSubmit={(e) => {
            e.preventDefault();
            setErr(null);
            if (!plRack || !plDev) {
              setErr("Velg rack og enhet");
              return;
            }
            createPl.mutate();
          }}
        >
          <label>
            Rack
            <select value={plRack} onChange={(e) => setPlRack(e.target.value)} required>
              <option value="">— velg —</option>
              {(racksQ.data ?? []).map((k) => (
                <option key={k.id} value={String(k.id)}>
                  #{k.id} {k.name} (rom {k.room_id})
                </option>
              ))}
            </select>
          </label>
          <label>
            Enhet
            <select value={plDev} onChange={(e) => setPlDev(e.target.value)} required>
              <option value="">— velg —</option>
              {(devicesQ.data ?? []).map((d) => (
                <option key={d.id} value={String(d.id)}>
                  #{d.id} {d.name}
                </option>
              ))}
            </select>
          </label>
          <label>
            U-pos
            <input type="number" min={1} value={plU} onChange={(e) => setPlU(e.target.value)} />
          </label>
          <label>
            Mount
            <select value={plMount} onChange={(e) => setPlMount(e.target.value)}>
              <option value="front">front</option>
              <option value="rear">rear</option>
            </select>
          </label>
          <button type="submit" className={styles.btn} disabled={createPl.isPending}>
            {createPl.isPending ? "…" : "Plasser"}
          </button>
        </form>
        {placementsQ.isLoading ? <p className={styles.muted}>Laster…</p> : null}
        {placementsQ.data && placementsQ.data.length > 0 ? (
          <table className={styles.table}>
            <thead>
              <tr>
                <th>ID</th>
                <th>Rack</th>
                <th>Enhet</th>
                <th>U</th>
                <th>Mount</th>
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
                      Fjern
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          !placementsQ.isLoading && <p className={styles.muted}>Ingen plasseringer.</p>
        )}
      </Panel>
    </>
  );
}
