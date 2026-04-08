import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { Panel } from "@/components/ui/Panel";
import { ApiError } from "@/lib/api";
import * as api from "./dcimApi";
import styles from "./dcim.module.css";

export function DcimSitesPage() {
  const qc = useQueryClient();
  const [name, setName] = useState("");
  const [slug, setSlug] = useState("");
  const [err, setErr] = useState<string | null>(null);

  const q = useQuery({ queryKey: ["dcim", "sites"], queryFn: api.listSites });
  const m = useMutation({
    mutationFn: () => api.createSite({ name: name.trim(), slug: slug.trim().toLowerCase() }),
    onSuccess: () => {
      setErr(null);
      setName("");
      setSlug("");
      void qc.invalidateQueries({ queryKey: ["dcim", "sites"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  return (
    <Panel title="Sites">
      {err ? <p className={styles.err}>{err}</p> : null}
      <form
        className={styles.formRow}
        onSubmit={(e) => {
          e.preventDefault();
          setErr(null);
          m.mutate();
        }}
      >
        <label>
          Navn
          <input value={name} onChange={(e) => setName(e.target.value)} required />
        </label>
        <label>
          Slug
          <input
            value={slug}
            onChange={(e) => setSlug(e.target.value)}
            placeholder="f.eks. oslo-dc"
            required
            pattern="[a-z0-9]+(?:-[a-z0-9]+)*"
            title="lowercase, tall og bindestrek"
          />
        </label>
        <button type="submit" className={styles.btn} disabled={m.isPending}>
          {m.isPending ? "Oppretter…" : "Opprett"}
        </button>
      </form>
      {q.isError ? (
        <p className={styles.err}>Kunne ikke hente sites: {(q.error as Error).message}</p>
      ) : null}
      {q.isLoading ? <p className={styles.muted}>Laster…</p> : null}
      {q.data && q.data.length === 0 ? <p className={styles.muted}>Ingen sites ennå.</p> : null}
      {q.data && q.data.length > 0 ? (
        <table className={styles.table}>
          <thead>
            <tr>
              <th>ID</th>
              <th>Navn</th>
              <th>Slug</th>
            </tr>
          </thead>
          <tbody>
            {q.data.map((s) => (
              <tr key={s.id}>
                <td>{s.id}</td>
                <td>{s.name}</td>
                <td>{s.slug}</td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : null}
    </Panel>
  );
}
