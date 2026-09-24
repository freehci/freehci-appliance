import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { useI18n } from "@/i18n/I18nProvider";
import { ApiError } from "@/lib/api";
import * as api from "./dcimApi";
import styles from "./dcim.module.css";
import type { CablePathHop } from "./types";

const PORT_KINDS = ["power-port", "power-outlet", "front-port", "rear-port"] as const;
const CABLE_TYPES = ["power", "cat6", "cat6a", "sm-os2", "mm-om4", "dac", "other"] as const;
const FIBER_CABLE_TYPES = new Set(["sm-os2", "mm-om4"]);

export function DevicePortsCablesPanel({
  deviceId,
  siteId,
  canCopyFromModel,
  onError,
}: {
  deviceId: number;
  siteId: number | null;
  canCopyFromModel: boolean;
  onError: (msg: string | null) => void;
}) {
  const { t } = useI18n();
  const qc = useQueryClient();
  const [kind, setKind] = useState<string>("power-port");
  const [name, setName] = useState("");
  const [cableName, setCableName] = useState("");
  const [cableType, setCableType] = useState("power");
  const [endA, setEndA] = useState("");
  const [endZ, setEndZ] = useState("");
  const [path, setPath] = useState<CablePathHop[] | null>(null);

  const portsQ = useQuery({
    queryKey: ["dcim", "devices", deviceId, "ports"],
    queryFn: () => api.listDevicePorts(deviceId),
  });
  const cablesQ = useQuery({
    queryKey: ["dcim", "cables", "device", deviceId],
    queryFn: () => api.listCables(undefined, deviceId),
  });
  const feedsQ = useQuery({
    queryKey: ["dcim", "power-feeds", siteId ?? "none"],
    queryFn: () => api.listPowerFeeds({ siteId: siteId ?? undefined }),
    enabled: siteId != null,
  });

  const fail = (e: Error) => onError(e instanceof ApiError ? e.message : e.message);
  const refresh = () => {
    void qc.invalidateQueries({ queryKey: ["dcim", "devices", deviceId, "ports"] });
    void qc.invalidateQueries({ queryKey: ["dcim", "cables"] });
  };

  const createPort = useMutation({
    mutationFn: () => api.createDevicePort(deviceId, { kind, name: name.trim() }),
    onSuccess: () => {
      setName("");
      onError(null);
      refresh();
    },
    onError: fail,
  });
  const copyPorts = useMutation({
    mutationFn: () => api.copyDevicePortsFromTemplates(deviceId),
    onSuccess: () => {
      onError(null);
      refresh();
    },
    onError: fail,
  });
  const delPort = useMutation({
    mutationFn: (id: number) => api.deleteDevicePort(id),
    onSuccess: () => {
      onError(null);
      refresh();
    },
    onError: fail,
  });
  const createCable = useMutation({
    mutationFn: () => {
      if (siteId == null) throw new Error(t("dcim.cables.needSite"));
      const [aType, aId] = endA.split(":");
      const [zType, zId] = endZ.split(":");
      return api.createCable({
        site_id: siteId,
        name: cableName.trim(),
        cable_type: cableType,
        a: { object_type: aType, object_id: Number(aId) },
        z: { object_type: zType, object_id: Number(zId) },
      });
    },
    onSuccess: () => {
      setCableName("");
      onError(null);
      refresh();
    },
    onError: fail,
  });
  const delCable = useMutation({
    mutationFn: (id: number) => api.deleteCable(id),
    onSuccess: () => {
      onError(null);
      refresh();
    },
    onError: fail,
  });

  const ends = [
    ...(portsQ.data ?? []).map((p) => ({
      value: `device-port:${p.id}`,
      label: `${p.kind} ${p.name}`,
    })),
    ...(feedsQ.data ?? []).map((f) => ({
      value: `power-feed:${f.id}`,
      label: `feed ${f.name}`,
    })),
  ];

  return (
    <section className={styles.mfrDetailSection}>
      <h3 className={styles.mfrDetailSectionTitle}>{t("dcim.ports.title")}</h3>
      <p className={styles.muted}>{t("dcim.ports.hint")}</p>
      {(portsQ.data ?? []).length === 0 && !portsQ.isLoading ? <p className={styles.muted}>{t("dcim.ports.empty")}</p> : null}
      {(portsQ.data ?? []).length > 0 ? (
        <table className={styles.table}>
          <thead>
            <tr>
              <th>{t("dcim.ports.kind")}</th>
              <th>{t("dcim.common.name")}</th>
              <th>{t("dcim.ports.connector")}</th>
              <th>{t("dcim.equip.actionsCol")}</th>
            </tr>
          </thead>
          <tbody>
            {(portsQ.data ?? []).map((p) => (
              <tr key={p.id}>
                <td>{p.kind}</td>
                <td>{p.name}</td>
                <td>{p.connector ?? "—"}</td>
                <td>
                  <button
                    type="button"
                    className={styles.btnLink}
                    onClick={() => {
                      void api.getDevicePortPath(p.id).then((r) => setPath(r.hops));
                    }}
                  >
                    {t("dcim.ports.path")}
                  </button>{" "}
                  <button type="button" className={styles.btnLink} onClick={() => delPort.mutate(p.id)}>
                    {t("dcim.common.delete")}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : null}
      {path ? (
        <p className={styles.muted}>
          {path.map((h) => h.label).join(" → ")}
        </p>
      ) : null}
      <form
        className={styles.formRow}
        onSubmit={(e) => {
          e.preventDefault();
          createPort.mutate();
        }}
      >
        <label>
          {t("dcim.ports.kind")}
          <select value={kind} onChange={(e) => setKind(e.target.value)}>
            {PORT_KINDS.map((k) => (
              <option key={k} value={k}>
                {k}
              </option>
            ))}
          </select>
        </label>
        <label>
          {t("dcim.common.name")}
          <input value={name} onChange={(e) => setName(e.target.value)} required />
        </label>
        <button type="submit" className={styles.btn} disabled={createPort.isPending}>
          {t("dcim.ports.add")}
        </button>
        {canCopyFromModel ? (
          <button type="button" className={styles.btn} disabled={copyPorts.isPending} onClick={() => copyPorts.mutate()}>
            {t("dcim.ports.fromTemplates")}
          </button>
        ) : null}
      </form>

      <h3 className={styles.mfrDetailSectionTitle}>{t("dcim.cables.title")}</h3>
      {(cablesQ.data ?? []).length === 0 && !cablesQ.isLoading ? <p className={styles.muted}>{t("dcim.cables.empty")}</p> : null}
      {(cablesQ.data ?? []).length > 0 ? (
        <ul className={styles.ipList}>
          {(cablesQ.data ?? []).map((c) => (
            <li key={c.id}>
              {c.name} ({c.cable_type}){" "}
              {c.terminations.map((x) => x.label ?? `${x.object_type}:${x.object_id}`).join(" ↔ ")}{" "}
              <button type="button" className={styles.btnLink} onClick={() => delCable.mutate(c.id)}>
                {t("dcim.common.delete")}
              </button>
              {FIBER_CABLE_TYPES.has(c.cable_type) ? (
                <>
                  <FiberStrandsInline cableId={c.id} onError={onError} />
                  <FiberBundlesInline cableId={c.id} onError={onError} />
                </>
              ) : null}
            </li>
          ))}
        </ul>
      ) : null}
      <form
        className={styles.formRow}
        onSubmit={(e) => {
          e.preventDefault();
          createCable.mutate();
        }}
      >
        <label>
          {t("dcim.common.name")}
          <input value={cableName} onChange={(e) => setCableName(e.target.value)} required />
        </label>
        <label>
          {t("dcim.cables.type")}
          <select value={cableType} onChange={(e) => setCableType(e.target.value)}>
            {CABLE_TYPES.map((x) => (
              <option key={x} value={x}>
                {x}
              </option>
            ))}
          </select>
        </label>
        <label>
          {t("dcim.cables.endA")}
          <select value={endA} onChange={(e) => setEndA(e.target.value)} required>
            <option value="">{t("dcim.cables.chooseEnd")}</option>
            {ends.map((e) => (
              <option key={e.value} value={e.value}>
                {e.label}
              </option>
            ))}
          </select>
        </label>
        <label>
          {t("dcim.cables.endZ")}
          <select value={endZ} onChange={(e) => setEndZ(e.target.value)} required>
            <option value="">{t("dcim.cables.chooseEnd")}</option>
            {ends.map((e) => (
              <option key={`z-${e.value}`} value={e.value}>
                {e.label}
              </option>
            ))}
          </select>
        </label>
        <button type="submit" className={styles.btn} disabled={createCable.isPending || siteId == null}>
          {t("dcim.cables.add")}
        </button>
      </form>
    </section>
  );
}

function FiberStrandsInline({
  cableId,
  onError,
}: {
  cableId: number;
  onError: (msg: string | null) => void;
}) {
  const { t } = useI18n();
  const qc = useQueryClient();
  const [position, setPosition] = useState("1");
  const [label, setLabel] = useState("");
  const strandsQ = useQuery({
    queryKey: ["dcim", "cables", cableId, "strands"],
    queryFn: () => api.listFiberStrands(cableId),
  });
  const fail = (e: Error) => onError(e instanceof ApiError ? e.message : e.message);
  const createStrand = useMutation({
    mutationFn: () =>
      api.createFiberStrand(cableId, {
        position: Number(position),
        label: label.trim() || null,
      }),
    onSuccess: () => {
      setLabel("");
      onError(null);
      void qc.invalidateQueries({ queryKey: ["dcim", "cables", cableId, "strands"] });
    },
    onError: fail,
  });
  const delStrand = useMutation({
    mutationFn: (id: number) => api.deleteFiberStrand(id),
    onSuccess: () => {
      onError(null);
      void qc.invalidateQueries({ queryKey: ["dcim", "cables", cableId, "strands"] });
    },
    onError: fail,
  });
  const strands = strandsQ.data ?? [];

  return (
    <div>
      <h4 className={styles.mfrDetailSectionTitle}>{t("dcim.strands.title")}</h4>
      <p className={styles.muted}>{t("dcim.strands.hint")}</p>
      {strands.length === 0 && !strandsQ.isLoading ? <p className={styles.muted}>{t("dcim.strands.empty")}</p> : null}
      {strands.length > 0 ? (
        <ul className={styles.ipList}>
          {strands.map((s) => (
            <li key={s.id}>
              #{s.position}
              {s.label ? ` ${s.label}` : ""} ({s.status}){" "}
              <button type="button" className={styles.btnLink} onClick={() => delStrand.mutate(s.id)}>
                {t("dcim.common.delete")}
              </button>
            </li>
          ))}
        </ul>
      ) : null}
      <form
        className={styles.formRow}
        onSubmit={(e) => {
          e.preventDefault();
          createStrand.mutate();
        }}
      >
        <label>
          {t("dcim.strands.position")}
          <input type="number" min={1} value={position} onChange={(e) => setPosition(e.target.value)} required />
        </label>
        <label>
          {t("dcim.strands.label")}
          <input value={label} onChange={(e) => setLabel(e.target.value)} />
        </label>
        <button type="submit" className={styles.btn} disabled={createStrand.isPending}>
          {t("dcim.strands.add")}
        </button>
      </form>
    </div>
  );
}

function FiberBundlesInline({
  cableId,
  onError,
}: {
  cableId: number;
  onError: (msg: string | null) => void;
}) {
  const { t } = useI18n();
  const qc = useQueryClient();
  const [name, setName] = useState("");
  const [bundleId, setBundleId] = useState("");
  const [strandId, setStrandId] = useState("");
  const strandsQ = useQuery({
    queryKey: ["dcim", "cables", cableId, "strands"],
    queryFn: () => api.listFiberStrands(cableId),
  });
  const bundlesQ = useQuery({
    queryKey: ["dcim", "cables", cableId, "bundles"],
    queryFn: () => api.listFiberBundles(cableId),
  });
  const fail = (e: Error) => onError(e instanceof ApiError ? e.message : e.message);
  const invalidate = () => {
    void qc.invalidateQueries({ queryKey: ["dcim", "cables", cableId, "bundles"] });
  };
  const createBundle = useMutation({
    mutationFn: () => api.createFiberBundle(cableId, { name: name.trim() }),
    onSuccess: () => {
      setName("");
      onError(null);
      invalidate();
    },
    onError: fail,
  });
  const addMember = useMutation({
    mutationFn: () => api.addFiberBundleMember(Number(bundleId), Number(strandId)),
    onSuccess: () => {
      setStrandId("");
      onError(null);
      invalidate();
    },
    onError: fail,
  });
  const delBundle = useMutation({
    mutationFn: (id: number) => api.deleteFiberBundle(id),
    onSuccess: () => {
      onError(null);
      invalidate();
    },
    onError: fail,
  });
  const delMember = useMutation({
    mutationFn: (id: number) => api.deleteFiberBundleMember(id),
    onSuccess: () => {
      onError(null);
      invalidate();
    },
    onError: fail,
  });
  const bundles = bundlesQ.data ?? [];
  const taken = new Set(bundles.flatMap((b) => b.members.map((m) => m.strand_id)));
  const freeStrands = (strandsQ.data ?? []).filter((s) => !taken.has(s.id));

  return (
    <div>
      <h4 className={styles.mfrDetailSectionTitle}>{t("dcim.bundles.title")}</h4>
      <p className={styles.muted}>{t("dcim.bundles.hint")}</p>
      {bundles.length === 0 && !bundlesQ.isLoading ? <p className={styles.muted}>{t("dcim.bundles.empty")}</p> : null}
      {bundles.length > 0 ? (
        <ul className={styles.ipList}>
          {bundles.map((b) => (
            <li key={b.id}>
              {b.name}
              {b.members.length > 0
                ? ` (${b.members.map((m) => `#${m.position}${m.label ? ` ${m.label}` : ""}`).join(", ")})`
                : ""}{" "}
              <button type="button" className={styles.btnLink} onClick={() => delBundle.mutate(b.id)}>
                {t("dcim.common.delete")}
              </button>
              {b.members.map((m) => (
                <button
                  key={m.id}
                  type="button"
                  className={styles.btnLink}
                  onClick={() => delMember.mutate(m.id)}
                >
                  {t("dcim.bundles.removeMember")} #{m.position}
                </button>
              ))}
            </li>
          ))}
        </ul>
      ) : null}
      <form
        className={styles.formRow}
        onSubmit={(e) => {
          e.preventDefault();
          createBundle.mutate();
        }}
      >
        <label>
          {t("dcim.bundles.name")}
          <input value={name} onChange={(e) => setName(e.target.value)} required />
        </label>
        <button type="submit" className={styles.btn} disabled={createBundle.isPending || name.trim() === ""}>
          {t("dcim.bundles.add")}
        </button>
      </form>
      {bundles.length > 0 ? (
        <form
          className={styles.formRow}
          onSubmit={(e) => {
            e.preventDefault();
            addMember.mutate();
          }}
        >
          <label>
            {t("dcim.bundles.bundle")}
            <select value={bundleId} onChange={(e) => setBundleId(e.target.value)}>
              <option value="">{t("dcim.bundles.chooseBundle")}</option>
              {bundles.map((b) => (
                <option key={b.id} value={String(b.id)}>
                  {b.name}
                </option>
              ))}
            </select>
          </label>
          <label>
            {t("dcim.bundles.strand")}
            <select value={strandId} onChange={(e) => setStrandId(e.target.value)}>
              <option value="">{t("dcim.bundles.chooseStrand")}</option>
              {freeStrands.map((s) => (
                <option key={s.id} value={String(s.id)}>
                  #{s.position}
                  {s.label ? ` ${s.label}` : ""}
                </option>
              ))}
            </select>
          </label>
          <button
            type="submit"
            className={styles.btn}
            disabled={addMember.isPending || bundleId === "" || strandId === ""}
          >
            {t("dcim.bundles.bind")}
          </button>
        </form>
      ) : null}
    </div>
  );
}
