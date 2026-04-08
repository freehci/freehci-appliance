import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { Panel } from "@/components/ui/Panel";
import { ApiError } from "@/lib/api";
import * as api from "./dcimApi";
import styles from "./dcim.module.css";

export function DcimRoomsPage() {
  const qc = useQueryClient();
  const [siteFilter, setSiteFilter] = useState<string>("");
  const [siteId, setSiteId] = useState<string>("");
  const [name, setName] = useState("");
  const [err, setErr] = useState<string | null>(null);

  const sitesQ = useQuery({ queryKey: ["dcim", "sites"], queryFn: api.listSites });
  const filterNum = useMemo(() => {
    const n = Number(siteFilter);
    return Number.isFinite(n) && n > 0 ? n : undefined;
  }, [siteFilter]);

  const roomsQ = useQuery({
    queryKey: ["dcim", "rooms", filterNum ?? "all"],
    queryFn: () => api.listRooms(filterNum),
  });

  const m = useMutation({
    mutationFn: () =>
      api.createRoom({ site_id: Number(siteId), name: name.trim() }),
    onSuccess: () => {
      setErr(null);
      setName("");
      void qc.invalidateQueries({ queryKey: ["dcim", "rooms"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  return (
    <Panel title="Rom">
      {err ? <p className={styles.err}>{err}</p> : null}
      <div className={styles.formRow}>
        <label>
          Filtrer på site-ID
          <input
            type="number"
            min={1}
            value={siteFilter}
            onChange={(e) => setSiteFilter(e.target.value)}
            placeholder="alle"
          />
        </label>
      </div>
      <form
        className={styles.formRow}
        onSubmit={(e) => {
          e.preventDefault();
          setErr(null);
          if (!siteId) {
            setErr("Velg site");
            return;
          }
          m.mutate();
        }}
      >
        <label>
          Site
          <select value={siteId} onChange={(e) => setSiteId(e.target.value)} required>
            <option value="">— velg —</option>
            {(sitesQ.data ?? []).map((s) => (
              <option key={s.id} value={String(s.id)}>
                {s.name} ({s.slug})
              </option>
            ))}
          </select>
        </label>
        <label>
          Romnavn
          <input value={name} onChange={(e) => setName(e.target.value)} required />
        </label>
        <button type="submit" className={styles.btn} disabled={m.isPending || sitesQ.isLoading}>
          {m.isPending ? "Oppretter…" : "Opprett rom"}
        </button>
      </form>
      {roomsQ.isError ? (
        <p className={styles.err}>Kunne ikke hente rom: {(roomsQ.error as Error).message}</p>
      ) : null}
      {roomsQ.isLoading ? <p className={styles.muted}>Laster…</p> : null}
      {roomsQ.data && roomsQ.data.length === 0 ? <p className={styles.muted}>Ingen rom.</p> : null}
      {roomsQ.data && roomsQ.data.length > 0 ? (
        <table className={styles.table}>
          <thead>
            <tr>
              <th>ID</th>
              <th>Site ID</th>
              <th>Navn</th>
            </tr>
          </thead>
          <tbody>
            {roomsQ.data.map((r) => (
              <tr key={r.id}>
                <td>{r.id}</td>
                <td>{r.site_id}</td>
                <td>{r.name}</td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : null}
    </Panel>
  );
}
