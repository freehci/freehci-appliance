import { useMutation, useQuery } from "@tanstack/react-query";
import { useEffect, useId, useState } from "react";
import { Link } from "react-router-dom";
import * as dcimApi from "@/features/dcim/dcimApi";
import dcimStyles from "@/features/dcim/dcim.module.css";
import { interfaceDepthByInterfaceList, interfaceIndentedName } from "@/features/dcim/interfaceTreeLabels";
import { useI18n } from "@/i18n/I18nProvider";
import { ApiError } from "@/lib/api";
import * as ipamApi from "./ipamApi";
import { ADDRESS_ROLES, ADDRESS_STATUSES, type PrefixAddressGridRow } from "./types";

type Props = {
  open: boolean;
  onClose: () => void;
  prefixId: number;
  prefixCidr: string;
  siteId: number | null;
  rows: PrefixAddressGridRow[];
  onSaved: () => void;
};

export function IpamAddressEditModal({ open, onClose, prefixId, prefixCidr, siteId, rows, onSaved }: Props) {
  const { t } = useI18n();
  const titleId = useId();
  const bulk = rows.length > 1;
  const single = rows[0] ?? null;
  const [status, setStatus] = useState("");
  const [role, setRole] = useState("");
  const [ownerUserId, setOwnerUserId] = useState("");
  const [note, setNote] = useState("");
  const [deviceId, setDeviceId] = useState("");
  const [ifaceId, setIfaceId] = useState("");
  const [localErr, setLocalErr] = useState<string | null>(null);

  const usersQ = useQuery({ queryKey: ["ipam", "users"], queryFn: () => ipamApi.listUsers(500), enabled: open });
  const devicesQ = useQuery({ queryKey: ["dcim", "devices"], queryFn: dcimApi.listDevices, enabled: open });
  const deviceIdNum = deviceId === "" ? null : Number(deviceId);
  const interfacesQ = useQuery({
    queryKey: ["dcim", "devices", deviceIdNum, "interfaces", "ipam-addr-edit"],
    queryFn: () => dcimApi.listDeviceInterfaces(deviceIdNum!),
    enabled: open && deviceIdNum != null && deviceIdNum > 0,
  });
  const ifaceDepth = interfaceDepthByInterfaceList(interfacesQ.data ?? []);

  useEffect(() => {
    if (!open) return;
    setLocalErr(null);
    if (rows.length === 1) {
      const inv = rows[0].inventory;
      const asg = rows[0].assignment;
      setStatus(inv?.status ?? "reserved");
      setRole(inv?.role ?? "");
      setOwnerUserId(inv?.owner_user_id != null ? String(inv.owner_user_id) : "");
      setNote(inv?.note ?? "");
      setDeviceId(asg?.device_id != null ? String(asg.device_id) : inv?.device_id != null ? String(inv.device_id) : "");
      setIfaceId(asg?.interface_id != null ? String(asg.interface_id) : inv?.interface_id != null ? String(inv.interface_id) : "");
      return;
    }
    setStatus("");
    setRole("");
    setOwnerUserId("");
    setNote("");
    setDeviceId("");
    setIfaceId("");
  }, [open, rows]);

  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  const saveM = useMutation({
    mutationFn: async () => {
      for (const row of rows) {
        let invId = row.inventory?.id ?? null;
        const patch: Parameters<typeof ipamApi.patchIpv4Address>[1] = {};
        if (!bulk || status !== "") patch.status = status || "reserved";
        if (!bulk || role !== "") {
          if (role !== "") patch.role = role;
        }
        if (!bulk || ownerUserId !== "") patch.owner_user_id = ownerUserId === "" ? null : Number(ownerUserId);
        if (!bulk || note.trim() !== "") patch.note = note.trim() || null;
        const shouldBind = deviceId !== "";
        const needsInv = Object.keys(patch).length > 0 || shouldBind;
        if (!invId && needsInv) {
          const created = await ipamApi.ensureIpv4Address({ ipv4_prefix_id: prefixId, address: row.address });
          invId = created.id;
        }
        if (invId != null && Object.keys(patch).length > 0) {
          await ipamApi.patchIpv4Address(invId, patch);
        }
        if (invId != null && shouldBind) {
          await ipamApi.bindIpv4Address(invId, {
            device_id: Number(deviceId),
            interface_id: ifaceId === "" ? null : Number(ifaceId),
          });
        }
      }
    },
    onSuccess: () => {
      setLocalErr(null);
      onSaved();
      onClose();
    },
    onError: (e: Error) => setLocalErr(e instanceof ApiError ? e.message : e.message),
  });

  const releaseM = useMutation({
    mutationFn: async () => {
      const invId = single?.inventory?.id;
      if (invId == null) return;
      await ipamApi.releaseIpv4Address(invId);
    },
    onSuccess: () => {
      setLocalErr(null);
      onSaved();
      onClose();
    },
    onError: (e: Error) => setLocalErr(e instanceof ApiError ? e.message : e.message),
  });

  if (!open || rows.length === 0) return null;

  const siteDevices = (devicesQ.data ?? []).filter((d) => {
    if (siteId == null) return true;
    if (d.effective_site_id === siteId || d.site_id === siteId) return true;
    return deviceIdNum != null && d.id === deviceIdNum;
  });
  const boundDevice = siteDevices.find((d) => d.id === deviceIdNum) ?? (devicesQ.data ?? []).find((d) => d.id === deviceIdNum);
  const canRelease =
    !bulk && single?.inventory != null && (single.inventory.status === "reserved" || single.inventory.status === "assigned");

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
          {bulk ? t("ipam.detail.editAddresses") : t("ipam.detail.editAddress")}
        </h2>
        <p className={dcimStyles.muted} style={{ marginTop: 0 }}>
          <code>{prefixCidr}</code>
          {bulk ? ` · ${t("ipam.detail.selectedCount", { count: String(rows.length) })}` : ` · ${single?.address ?? ""}`}
        </p>
        {bulk ? (
          <>
            <p className={dcimStyles.muted}>{t("ipam.detail.bulkHint")}</p>
            <p className={dcimStyles.muted} style={{ fontFamily: "var(--font-mono, ui-monospace, monospace)" }}>
              {rows
                .slice(0, 12)
                .map((r) => r.address)
                .join(", ")}
              {rows.length > 12 ? ` … +${rows.length - 12}` : ""}
            </p>
          </>
        ) : null}
        {localErr ? <p className={dcimStyles.err}>{localErr}</p> : null}

        <div className={dcimStyles.formRow} style={{ flexDirection: "column", alignItems: "stretch" }}>
          <label>
            {t("ipam.addr.colStatus")}
            <select value={status} onChange={(e) => setStatus(e.target.value)}>
              {bulk ? <option value="">{t("ipam.detail.unchanged")}</option> : null}
              {ADDRESS_STATUSES.map((s) => (
                <option key={s} value={s}>
                  {s}
                </option>
              ))}
            </select>
          </label>
          <label>
            {t("ipam.grid.colRole")}
            <select value={role} onChange={(e) => setRole(e.target.value)}>
              <option value="">{bulk ? t("ipam.detail.unchanged") : t("dcim.common.choose")}</option>
              {ADDRESS_ROLES.map((r) => (
                <option key={r} value={r}>
                  {r}
                </option>
              ))}
            </select>
          </label>
          <label>
            {t("ipam.addr.colOwner")}
            <select value={ownerUserId} onChange={(e) => setOwnerUserId(e.target.value)}>
              <option value="">{bulk ? t("ipam.detail.unchanged") : t("dcim.common.choose")}</option>
              {(usersQ.data ?? []).map((u) => (
                <option key={u.id} value={String(u.id)}>
                  {u.display_name ?? u.username}
                </option>
              ))}
            </select>
          </label>
          <label>
            {t("ipam.addr.note")}
            <input value={note} onChange={(e) => setNote(e.target.value)} placeholder={bulk ? t("ipam.detail.unchanged") : undefined} />
          </label>
          <label>
            {t("ipam.ipv4.colDevice")}
            <select
              value={deviceId}
              onChange={(e) => {
                setDeviceId(e.target.value);
                setIfaceId("");
              }}
            >
              <option value="">{bulk ? t("ipam.detail.unchanged") : t("dcim.common.choose")}</option>
              {siteDevices.map((d) => (
                <option key={d.id} value={String(d.id)}>
                  {d.name}
                </option>
              ))}
            </select>
          </label>
          {deviceIdNum != null ? (
            <p style={{ margin: 0 }}>
              {t("ipam.detail.boundEquipment")}:{" "}
              <Link to={`/dcim/equipment/devices/${deviceIdNum}`}>{boundDevice?.name ?? `#${deviceIdNum}`}</Link>
            </p>
          ) : null}
          <label>
            {t("ipam.ipv4.colInterface")}
            <select value={ifaceId} onChange={(e) => setIfaceId(e.target.value)} disabled={deviceIdNum == null}>
              <option value="">{bulk ? t("ipam.detail.unchanged") : t("dcim.common.choose")}</option>
              {(interfacesQ.data ?? []).map((x) => (
                <option key={x.id} value={String(x.id)}>
                  {interfaceIndentedName(x, ifaceDepth)}
                </option>
              ))}
            </select>
          </label>
        </div>

        <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem", marginTop: "var(--space-3)" }}>
          <button type="button" className={dcimStyles.btn} disabled={saveM.isPending} onClick={() => saveM.mutate()}>
            {saveM.isPending ? "…" : t("dcim.common.save")}
          </button>
          <button type="button" className={dcimStyles.btnMuted} onClick={onClose} disabled={saveM.isPending || releaseM.isPending}>
            {t("dcim.common.cancel")}
          </button>
          {canRelease ? (
            <button type="button" className={dcimStyles.btnDanger} disabled={releaseM.isPending} onClick={() => releaseM.mutate()}>
              {t("ipam.addr.release")}
            </button>
          ) : null}
        </div>
      </div>
    </div>
  );
}
