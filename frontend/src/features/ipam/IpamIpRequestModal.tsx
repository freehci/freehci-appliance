import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useId, useState } from "react";
import * as dcimApi from "@/features/dcim/dcimApi";
import dcimStyles from "@/features/dcim/dcim.module.css";
import { interfaceDepthByInterfaceList, interfaceIndentedName } from "@/features/dcim/interfaceTreeLabels";
import { useI18n } from "@/i18n/I18nProvider";
import { ApiError } from "@/lib/api";
import * as ipamApi from "./ipamApi";

type Props = {
  open: boolean;
  onClose: () => void;
  prefixId: number;
  prefixCidr: string;
  initialPreferred: string;
  onAllocated: () => void;
};

export function IpamIpRequestModal({ open, onClose, prefixId, prefixCidr, initialPreferred, onAllocated }: Props) {
  const { t } = useI18n();
  const titleId = useId();
  const qc = useQueryClient();
  const [count, setCount] = useState(1);
  const [preferredText, setPreferredText] = useState("");
  const [mode, setMode] = useState<"reserve" | "assign">("reserve");
  const [ownerUserId, setOwnerUserId] = useState("");
  const [note, setNote] = useState("");
  const [deviceId, setDeviceId] = useState("");
  const [ifaceId, setIfaceId] = useState("");
  const [localErr, setLocalErr] = useState<string | null>(null);
  const [infoMsg, setInfoMsg] = useState<string | null>(null);

  const usersQ = useQuery({ queryKey: ["ipam", "users"], queryFn: () => ipamApi.listUsers(500), enabled: open });
  const devicesQ = useQuery({ queryKey: ["dcim", "devices"], queryFn: dcimApi.listDevices, enabled: open });

  const deviceIdNum = deviceId === "" ? null : Number(deviceId);
  const interfacesQ = useQuery({
    queryKey: ["dcim", "devices", deviceIdNum, "interfaces", "ipam-req-modal"],
    queryFn: () => dcimApi.listDeviceInterfaces(deviceIdNum!),
    enabled: open && deviceIdNum != null && deviceIdNum > 0,
  });
  const ifaceDepth = interfaceDepthByInterfaceList(interfacesQ.data ?? []);

  useEffect(() => {
    if (!open) return;
    setPreferredText(initialPreferred.trim());
    setCount(1);
    setMode("reserve");
    setOwnerUserId("");
    setNote("");
    setDeviceId("");
    setIfaceId("");
    setLocalErr(null);
    setInfoMsg(null);
  }, [open, initialPreferred, prefixId]);

  useEffect(() => {
    setIfaceId("");
  }, [deviceId]);

  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  const batchM = useMutation({
    mutationFn: () => {
      const lines = preferredText
        .split(/[\n,;]+/)
        .map((s) => s.trim())
        .filter(Boolean);
      return ipamApi.requestIpv4AddressBatch({
        ipv4_prefix_id: prefixId,
        mode,
        count,
        preferred_addresses: lines,
        owner_user_id: ownerUserId.trim() !== "" ? Number(ownerUserId) : null,
        note: note.trim() !== "" ? note.trim() : null,
        device_id: mode === "assign" && deviceId.trim() !== "" ? Number(deviceId) : null,
        interface_id: mode === "assign" && ifaceId.trim() !== "" ? Number(ifaceId) : null,
      });
    },
    onSuccess: (res) => {
      setLocalErr(null);
      if (res.allocated_count < res.requested_count) {
        setInfoMsg(
          t("ipam.addr.requestModal.partial", {
            allocated: String(res.allocated_count),
            requested: String(res.requested_count),
          }),
        );
      } else {
        setInfoMsg(null);
      }
      void qc.invalidateQueries({ queryKey: ["ipam", "ipv4-prefixes"] });
      void qc.invalidateQueries({ queryKey: ["ipam", "explore"] });
      void qc.invalidateQueries({ queryKey: ["ipam", "address-grid"] });
      onAllocated();
      if (res.allocated_count >= res.requested_count) onClose();
    },
    onError: (e: Error) => setLocalErr(e instanceof ApiError ? e.message : e.message),
  });

  if (!open) return null;

  const submit = () => {
    setLocalErr(null);
    setInfoMsg(null);
    if (!Number.isFinite(count) || count < 1 || count > 256) {
      setLocalErr(t("ipam.addr.requestModal.badCount"));
      return;
    }
    if (mode === "assign") {
      if (deviceId.trim() === "") {
        setLocalErr(t("ipam.addr.assignNeedsDevice"));
        return;
      }
      if (ifaceId.trim() === "") {
        setLocalErr(t("dcim.equip.ip.chooseIface"));
        return;
      }
    }
    batchM.mutate();
  };

  return (
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
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
        style={{
          width: "min(36rem, 100%)",
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
        <h2 id={titleId} style={{ marginTop: 0 }}>
          {t("ipam.addr.requestModal.title")}
        </h2>
        <p className={dcimStyles.muted} style={{ marginTop: 0 }}>
          <code>{prefixCidr}</code> · #{prefixId}
        </p>
        {localErr ? <p className={dcimStyles.err}>{localErr}</p> : null}
        {infoMsg ? <p className={dcimStyles.muted}>{infoMsg}</p> : null}

        <div className={dcimStyles.formRow} style={{ flexDirection: "column", alignItems: "stretch" }}>
          <label>
            {t("ipam.addr.requestModal.count")}
            <input
              type="number"
              min={1}
              max={256}
              value={count}
              onChange={(e) => setCount(Number(e.target.value))}
            />
          </label>
          <label>
            {t("ipam.addr.requestModal.preferred")}
            <textarea
              rows={4}
              value={preferredText}
              onChange={(e) => setPreferredText(e.target.value)}
              placeholder={t("ipam.addr.requestModal.preferredPlaceholder")}
            />
          </label>
          <label>
            {t("ipam.addr.mode")}
            <select value={mode} onChange={(e) => setMode(e.target.value as "reserve" | "assign")}>
              <option value="reserve">{t("ipam.addr.mode.reserve")}</option>
              <option value="assign">{t("ipam.addr.mode.assign")}</option>
            </select>
          </label>
          <label>
            {t("ipam.addr.device")}
            <select value={deviceId} onChange={(e) => setDeviceId(e.target.value)} disabled={mode !== "assign"}>
              <option value="">{t("dcim.common.choose")}</option>
              {(devicesQ.data ?? []).map((d) => (
                <option key={d.id} value={String(d.id)}>
                  #{d.id} · {d.name}
                </option>
              ))}
            </select>
          </label>
          <label>
            {t("ipam.addr.interfaceId")}
            <select value={ifaceId} onChange={(e) => setIfaceId(e.target.value)} disabled={mode !== "assign"}>
              <option value="">{t("dcim.common.choose")}</option>
              {(interfacesQ.data ?? []).map((x) => (
                <option key={x.id} value={String(x.id)}>
                  #{x.id} · {interfaceIndentedName(x, ifaceDepth)}
                </option>
              ))}
            </select>
          </label>
          <label>
            {t("ipam.addr.ownerUserId")}
            <select value={ownerUserId} onChange={(e) => setOwnerUserId(e.target.value)}>
              <option value="">{t("dcim.common.choose")}</option>
              {(usersQ.data ?? []).map((u) => (
                <option key={u.id} value={String(u.id)}>
                  #{u.id} · {u.display_name ?? u.username}
                </option>
              ))}
            </select>
          </label>
          <label>
            {t("ipam.addr.note")}
            <input value={note} onChange={(e) => setNote(e.target.value)} />
          </label>
        </div>

        <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem", marginTop: "var(--space-3)" }}>
          <button type="button" className={dcimStyles.btn} disabled={batchM.isPending} onClick={submit}>
            {batchM.isPending ? "…" : t("ipam.addr.requestBtn")}
          </button>
          <button type="button" className={dcimStyles.btnMuted} onClick={onClose} disabled={batchM.isPending}>
            {t("ipam.ipv4.cancel")}
          </button>
        </div>
      </div>
    </div>
  );
}
