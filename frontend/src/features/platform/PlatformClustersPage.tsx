import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { Link } from "react-router-dom";
import { Panel } from "@/components/ui/Panel";
import { listDevices } from "@/features/dcim/dcimApi";
import dcimStyles from "@/features/dcim/dcim.module.css";
import { useI18n } from "@/i18n/I18nProvider";
import { ApiError } from "@/lib/api";
import * as api from "./platformApi";

export function PlatformClustersPage() {
  const { t } = useI18n();
  const qc = useQueryClient();
  const [err, setErr] = useState<string | null>(null);
  const [name, setName] = useState("");
  const [kind, setKind] = useState<api.ClusterKind>("other");
  const [memberCluster, setMemberCluster] = useState("");
  const [memberDevice, setMemberDevice] = useState("");
  const [vmCluster, setVmCluster] = useState("");
  const [vmName, setVmName] = useState("");
  const [vmDevice, setVmDevice] = useState("");
  const [stCluster, setStCluster] = useState("");
  const [stName, setStName] = useState("");
  const [stKind, setStKind] = useState("other");

  const clQ = useQuery({ queryKey: ["platform-clusters"], queryFn: api.listClusters });
  const devQ = useQuery({ queryKey: ["dcim-devices"], queryFn: listDevices });
  const fail = (e: Error) => setErr(e instanceof ApiError ? e.message : e.message);
  const devices = new Map((devQ.data ?? []).map((d) => [d.id, d.name]));

  const createM = useMutation({
    mutationFn: () => api.createCluster({ name: name.trim(), kind }),
    onSuccess: () => {
      setErr(null);
      setName("");
      void qc.invalidateQueries({ queryKey: ["platform-clusters"] });
    },
    onError: fail,
  });
  const addM = useMutation({
    mutationFn: () =>
      api.addClusterMember(Number(memberCluster), { device_id: Number(memberDevice), role: "node" }),
    onSuccess: () => {
      setErr(null);
      setMemberDevice("");
      void qc.invalidateQueries({ queryKey: ["platform-clusters"] });
    },
    onError: fail,
  });
  const vmM = useMutation({
    mutationFn: () =>
      api.createVm(Number(vmCluster), {
        name: vmName.trim(),
        device_id: vmDevice ? Number(vmDevice) : null,
        status: "active",
      }),
    onSuccess: () => {
      setErr(null);
      setVmName("");
      void qc.invalidateQueries({ queryKey: ["platform-clusters"] });
    },
    onError: fail,
  });
  const stM = useMutation({
    mutationFn: () =>
      api.createStoragePool(Number(stCluster), { name: stName.trim(), kind: stKind, status: "active" }),
    onSuccess: () => {
      setErr(null);
      setStName("");
      void qc.invalidateQueries({ queryKey: ["platform-clusters"] });
    },
    onError: fail,
  });

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "1.25rem" }}>
      <Panel title={t("platform.title")}>
        <p style={{ marginTop: 0 }}>{t("platform.intro")}</p>
        {err ? <p className={dcimStyles.err}>{err}</p> : null}
        <form
          className={dcimStyles.formRow}
          onSubmit={(e) => {
            e.preventDefault();
            if (name.trim()) createM.mutate();
          }}
        >
          <label>
            {t("dcim.common.name")}
            <input value={name} onChange={(e) => setName(e.target.value)} />
          </label>
          <label>
            {t("platform.kind")}
            <select value={kind} onChange={(e) => setKind(e.target.value as api.ClusterKind)}>
              <option value="other">{t("platform.kindOther")}</option>
              <option value="proxmox">Proxmox</option>
              <option value="talos">Talos</option>
            </select>
          </label>
          <button type="submit" className={dcimStyles.btn} disabled={createM.isPending || !name.trim()}>
            {t("platform.addCluster")}
          </button>
        </form>
        {(clQ.data ?? []).length === 0 && !clQ.isLoading ? (
          <p className={dcimStyles.muted}>{t("platform.empty")}</p>
        ) : null}
        {(clQ.data ?? []).map((c) => (
          <section key={c.id} className={dcimStyles.mfrDetailSection}>
            <h3 className={dcimStyles.mfrDetailSectionTitle}>
              {c.name} ({c.kind})
            </h3>
            <p className={dcimStyles.muted}>{c.slug}</p>
            {c.members.length === 0 ? <p className={dcimStyles.muted}>{t("platform.noMembers")}</p> : null}
            {c.members.length > 0 ? (
              <ul className={dcimStyles.ipList}>
                {c.members.map((m) => (
                  <li key={m.id}>
                    <Link to={`/dcim/equipment/devices/${m.device_id}`}>
                      {devices.get(m.device_id) ?? `#${m.device_id}`}
                    </Link>{" "}
                    — {m.role}
                  </li>
                ))}
              </ul>
            ) : null}
            <p className={dcimStyles.muted}>{t("platform.vms")}</p>
            {(c.vms ?? []).length === 0 ? <p className={dcimStyles.muted}>{t("platform.noVms")}</p> : null}
            {(c.vms ?? []).length > 0 ? (
              <ul className={dcimStyles.ipList}>
                {(c.vms ?? []).map((v) => (
                  <li key={v.id}>
                    {v.name} — {v.status}
                    {v.device_id != null ? ` → ${devices.get(v.device_id) ?? `#${v.device_id}`}` : ""}
                  </li>
                ))}
              </ul>
            ) : null}
            <p className={dcimStyles.muted}>{t("platform.storage")}</p>
            {(c.storage_pools ?? []).length === 0 ? (
              <p className={dcimStyles.muted}>{t("platform.noStorage")}</p>
            ) : null}
            {(c.storage_pools ?? []).length > 0 ? (
              <ul className={dcimStyles.ipList}>
                {(c.storage_pools ?? []).map((p) => (
                  <li key={p.id}>
                    {p.name} — {p.kind} — {p.status}
                  </li>
                ))}
              </ul>
            ) : null}
          </section>
        ))}
        {(clQ.data ?? []).length > 0 ? (
          <form
            className={dcimStyles.formRow}
            onSubmit={(e) => {
              e.preventDefault();
              if (memberCluster && memberDevice) addM.mutate();
            }}
          >
            <label>
              {t("platform.cluster")}
              <select value={memberCluster} onChange={(e) => setMemberCluster(e.target.value)}>
                <option value="">{t("dcim.common.choose")}</option>
                {(clQ.data ?? []).map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.name}
                  </option>
                ))}
              </select>
            </label>
            <label>
              {t("catalog.device")}
              <select value={memberDevice} onChange={(e) => setMemberDevice(e.target.value)}>
                <option value="">{t("dcim.common.choose")}</option>
                {(devQ.data ?? []).map((d) => (
                  <option key={d.id} value={d.id}>
                    {d.name}
                  </option>
                ))}
              </select>
            </label>
            <button type="submit" className={dcimStyles.btn} disabled={addM.isPending || !memberCluster || !memberDevice}>
              {t("platform.addMember")}
            </button>
          </form>
        ) : null}
        {(clQ.data ?? []).length > 0 ? (
          <form
            className={dcimStyles.formRow}
            onSubmit={(e) => {
              e.preventDefault();
              if (vmCluster && vmName.trim()) vmM.mutate();
            }}
          >
            <label>
              {t("platform.cluster")}
              <select value={vmCluster} onChange={(e) => setVmCluster(e.target.value)}>
                <option value="">{t("dcim.common.choose")}</option>
                {(clQ.data ?? []).map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.name}
                  </option>
                ))}
              </select>
            </label>
            <label>
              {t("platform.vmName")}
              <input value={vmName} onChange={(e) => setVmName(e.target.value)} />
            </label>
            <label>
              {t("platform.vmHost")}
              <select value={vmDevice} onChange={(e) => setVmDevice(e.target.value)}>
                <option value="">{t("dcim.common.none")}</option>
                {(devQ.data ?? []).map((d) => (
                  <option key={d.id} value={d.id}>
                    {d.name}
                  </option>
                ))}
              </select>
            </label>
            <button type="submit" className={dcimStyles.btn} disabled={vmM.isPending || !vmCluster || !vmName.trim()}>
              {t("platform.addVm")}
            </button>
          </form>
        ) : null}
        {(clQ.data ?? []).length > 0 ? (
          <form
            className={dcimStyles.formRow}
            onSubmit={(e) => {
              e.preventDefault();
              if (stCluster && stName.trim()) stM.mutate();
            }}
          >
            <label>
              {t("platform.cluster")}
              <select value={stCluster} onChange={(e) => setStCluster(e.target.value)}>
                <option value="">{t("dcim.common.choose")}</option>
                {(clQ.data ?? []).map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.name}
                  </option>
                ))}
              </select>
            </label>
            <label>
              {t("platform.storageName")}
              <input value={stName} onChange={(e) => setStName(e.target.value)} />
            </label>
            <label>
              {t("platform.storageKind")}
              <select value={stKind} onChange={(e) => setStKind(e.target.value)}>
                <option value="other">{t("platform.kindOther")}</option>
                <option value="datastore">datastore</option>
                <option value="pool">pool</option>
              </select>
            </label>
            <button type="submit" className={dcimStyles.btn} disabled={stM.isPending || !stCluster || !stName.trim()}>
              {t("platform.addStorage")}
            </button>
          </form>
        ) : null}
      </Panel>
    </div>
  );
}
