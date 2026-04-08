import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { Panel } from "@/components/ui/Panel";
import { ApiError } from "@/lib/api";
import * as api from "./dcimApi";
import styles from "./dcim.module.css";

export function DcimRacksPage() {
  const qc = useQueryClient();
  const [roomFilter, setRoomFilter] = useState<string>("");
  const [roomId, setRoomId] = useState<string>("");
  const [name, setName] = useState("");
  const [uHeight, setUHeight] = useState("42");
  const [err, setErr] = useState<string | null>(null);

  const roomsQ = useQuery({ queryKey: ["dcim", "rooms", "all"], queryFn: () => api.listRooms() });
  const filterNum = useMemo(() => {
    const n = Number(roomFilter);
    return Number.isFinite(n) && n > 0 ? n : undefined;
  }, [roomFilter]);

  const racksQ = useQuery({
    queryKey: ["dcim", "racks", filterNum ?? "all"],
    queryFn: () => api.listRacks(filterNum),
  });

  const m = useMutation({
    mutationFn: () =>
      api.createRack({
        room_id: Number(roomId),
        name: name.trim(),
        u_height: Number(uHeight) || 42,
      }),
    onSuccess: () => {
      setErr(null);
      setName("");
      void qc.invalidateQueries({ queryKey: ["dcim", "racks"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  return (
    <Panel title="Racks">
      {err ? <p className={styles.err}>{err}</p> : null}
      <div className={styles.formRow}>
        <label>
          Filtrer på rom-ID
          <input
            type="number"
            min={1}
            value={roomFilter}
            onChange={(e) => setRoomFilter(e.target.value)}
            placeholder="alle"
          />
        </label>
      </div>
      <form
        className={styles.formRow}
        onSubmit={(e) => {
          e.preventDefault();
          setErr(null);
          if (!roomId) {
            setErr("Velg rom");
            return;
          }
          m.mutate();
        }}
      >
        <label>
          Rom
          <select value={roomId} onChange={(e) => setRoomId(e.target.value)} required>
            <option value="">— velg —</option>
            {(roomsQ.data ?? []).map((r) => (
              <option key={r.id} value={String(r.id)}>
                #{r.id} — {r.name} (site {r.site_id})
              </option>
            ))}
          </select>
        </label>
        <label>
          Rack-navn
          <input value={name} onChange={(e) => setName(e.target.value)} required />
        </label>
        <label>
          U-høyde
          <input
            type="number"
            min={1}
            max={64}
            value={uHeight}
            onChange={(e) => setUHeight(e.target.value)}
          />
        </label>
        <button type="submit" className={styles.btn} disabled={m.isPending || roomsQ.isLoading}>
          {m.isPending ? "Oppretter…" : "Opprett rack"}
        </button>
      </form>
      {racksQ.isError ? (
        <p className={styles.err}>Kunne ikke hente racks: {(racksQ.error as Error).message}</p>
      ) : null}
      {racksQ.isLoading ? <p className={styles.muted}>Laster…</p> : null}
      {racksQ.data && racksQ.data.length === 0 ? <p className={styles.muted}>Ingen racks.</p> : null}
      {racksQ.data && racksQ.data.length > 0 ? (
        <table className={styles.table}>
          <thead>
            <tr>
              <th>ID</th>
              <th>Rom ID</th>
              <th>Navn</th>
              <th>U</th>
            </tr>
          </thead>
          <tbody>
            {racksQ.data.map((k) => (
              <tr key={k.id}>
                <td>{k.id}</td>
                <td>{k.room_id}</td>
                <td>{k.name}</td>
                <td>{k.u_height}</td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : null}
    </Panel>
  );
}
