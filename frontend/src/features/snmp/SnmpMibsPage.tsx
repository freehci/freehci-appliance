import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { useI18n } from "@/i18n/I18nProvider";
import { ApiError } from "@/lib/api";
import * as dcimApi from "@/features/dcim/dcimApi";
import dcimStyles from "@/features/dcim/dcim.module.css";
import type { Manufacturer } from "@/features/dcim/types";
import * as snmpApi from "./snmpApi";

function enterpriseKey(pen: number | null): string {
  return pen == null ? "none" : String(pen);
}

export function SnmpMibsPage() {
  const { t } = useI18n();
  const qc = useQueryClient();
  const [err, setErr] = useState<string | null>(null);
  const [files, setFiles] = useState<File[]>([]);

  const mibsQ = useQuery({ queryKey: ["snmp", "mibs", "detailed"], queryFn: snmpApi.listSnmpMibsDetailed });
  const entQ = useQuery({ queryKey: ["snmp", "enterprises"], queryFn: snmpApi.listSnmpEnterprises });
  const mfrQ = useQuery({ queryKey: ["dcim", "manufacturers", "all"], queryFn: dcimApi.listManufacturers });

  const invalidate = () => {
    void qc.invalidateQueries({ queryKey: ["snmp", "mibs"] });
    void qc.invalidateQueries({ queryKey: ["snmp", "enterprises"] });
  };

  const uploadBatch = useMutation({
    mutationFn: (fs: File[]) => snmpApi.uploadSnmpMibsBatch(fs),
    onSuccess: () => {
      setErr(null);
      setFiles([]);
      invalidate();
      void qc.invalidateQueries({ queryKey: ["snmp", "mibs", "detailed"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const syncIana = useMutation({
    mutationFn: () => snmpApi.syncSnmpIana(),
    onSuccess: () => {
      setErr(null);
      invalidate();
      void qc.invalidateQueries({ queryKey: ["snmp", "mibs", "detailed"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const compileAll = useMutation({
    mutationFn: () => snmpApi.compileAllSnmpMibs(),
    onSuccess: () => {
      setErr(null);
      void qc.invalidateQueries({ queryKey: ["snmp", "mibs", "detailed"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const compileOne = useMutation({
    mutationFn: (name: string) => snmpApi.compileSnmpMib(name),
    onSuccess: () => {
      setErr(null);
      void qc.invalidateQueries({ queryKey: ["snmp", "mibs", "detailed"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const delMib = useMutation({
    mutationFn: (name: string) => snmpApi.deleteSnmpMib(name),
    onSuccess: () => {
      setErr(null);
      invalidate();
      void qc.invalidateQueries({ queryKey: ["snmp", "mibs", "detailed"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const linkMfr = useMutation({
    mutationFn: ({ id, pen }: { id: number; pen: number | null }) =>
      dcimApi.updateManufacturer(id, { iana_enterprise_number: pen }),
    onSuccess: () => {
      setErr(null);
      void qc.invalidateQueries({ queryKey: ["dcim", "manufacturers"] });
      invalidate();
      void qc.invalidateQueries({ queryKey: ["snmp", "mibs", "detailed"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const manufacturers = mfrQ.data ?? [];
  const groups = entQ.data ?? [];

  return (
    <>
      {err ? <p className={dcimStyles.err}>{err}</p> : null}
      <p className={dcimStyles.muted} style={{ marginTop: 0 }}>
        {t("snmp.mibsPageIntro")}
      </p>

      <section className={dcimStyles.mfrDetailSection}>
        <h3 className={dcimStyles.mfrDetailSectionTitle}>{t("snmp.mibsUploadTitle")}</h3>
        <div className={dcimStyles.formRow} style={{ alignItems: "flex-end" }}>
          <label>
            {t("snmp.mibFilesMulti")}
            <input
              type="file"
              multiple
              accept=".mib,.my,.txt,text/plain"
              onChange={(e) => setFiles(e.target.files ? Array.from(e.target.files) : [])}
            />
          </label>
          <button
            type="button"
            className={dcimStyles.btn}
            disabled={files.length === 0 || uploadBatch.isPending}
            onClick={() => uploadBatch.mutate(files)}
          >
            {uploadBatch.isPending ? "…" : t("snmp.mibUploadBatch")}
          </button>
          <button
            type="button"
            className={dcimStyles.btnMuted}
            disabled={syncIana.isPending}
            onClick={() => syncIana.mutate()}
            title={t("snmp.ianaSyncHint")}
          >
            {syncIana.isPending ? "…" : t("snmp.ianaSync")}
          </button>
          <button
            type="button"
            className={dcimStyles.btnMuted}
            disabled={compileAll.isPending || (mibsQ.data?.length ?? 0) === 0}
            onClick={() => {
              if (!window.confirm(t("snmp.compileAllConfirm"))) return;
              compileAll.mutate();
            }}
            title={t("snmp.compileAllHint")}
          >
            {compileAll.isPending ? "…" : t("snmp.compileAll")}
          </button>
        </div>
      </section>

      <section className={dcimStyles.mfrDetailSection}>
        <h3 className={dcimStyles.mfrDetailSectionTitle}>{t("snmp.enterprisesTitle")}</h3>
        <p className={dcimStyles.muted} style={{ marginTop: 0 }}>
          {t("snmp.enterprisesHint")}
        </p>
        {entQ.isLoading ? <p className={dcimStyles.muted}>{t("dcim.common.loading")}</p> : null}
        {groups.length > 0 ? (
          <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-3)" }}>
            {groups.map((g) => (
              <EnterpriseGroupCard
                key={enterpriseKey(g.enterprise_number)}
                group={g}
                manufacturers={manufacturers}
                onLink={(id, pen) => linkMfr.mutate({ id, pen })}
                onUnlink={(id) => linkMfr.mutate({ id, pen: null })}
                linkPending={linkMfr.isPending}
              />
            ))}
          </div>
        ) : entQ.data && entQ.data.length === 0 && !entQ.isLoading ? (
          <p className={dcimStyles.muted}>{t("snmp.mibsEmpty")}</p>
        ) : null}
      </section>

      <section className={dcimStyles.mfrDetailSection}>
        <h3 className={dcimStyles.mfrDetailSectionTitle}>{t("snmp.mibsTableTitle")}</h3>
        {mibsQ.isLoading ? <p className={dcimStyles.muted}>{t("dcim.common.loading")}</p> : null}
        {mibsQ.data && mibsQ.data.length > 0 ? (
          <div style={{ overflowX: "auto" }}>
            <table className={dcimStyles.table}>
              <thead>
                <tr>
                  <th>{t("snmp.mibColName")}</th>
                  <th>{t("snmp.mibColModule")}</th>
                  <th>{t("snmp.mibColEnterprise")}</th>
                  <th>{t("snmp.mibColIanaOrg")}</th>
                  <th>{t("snmp.mibColCompile")}</th>
                  <th>{t("snmp.mibColMfr")}</th>
                  <th>{t("ipam.ipv4.actionsCol")}</th>
                </tr>
              </thead>
              <tbody>
                {mibsQ.data.map((m) => (
                  <tr key={m.name}>
                    <td>
                      <code>{m.name}</code>
                    </td>
                    <td className={dcimStyles.muted}>{m.module_name ?? "—"}</td>
                    <td>{m.enterprise_number ?? "—"}</td>
                    <td className={dcimStyles.muted}>{m.iana_organization ?? "—"}</td>
                    <td>
                      <span className={dcimStyles.muted}>{m.compile_status}</span>
                      {m.compile_message ? (
                        <span className={dcimStyles.err} title={m.compile_message}>
                          {" "}
                          (⚠)
                        </span>
                      ) : null}
                    </td>
                    <td>{m.linked_manufacturer?.name ?? "—"}</td>
                    <td>
                      <button
                        type="button"
                        className={dcimStyles.btnLink}
                        style={{ marginRight: "var(--space-2)" }}
                        disabled={compileOne.isPending}
                        onClick={() => compileOne.mutate(m.name)}
                      >
                        {t("snmp.compileOne")}
                      </button>
                      <button
                        type="button"
                        className={dcimStyles.btnDanger}
                        disabled={delMib.isPending}
                        onClick={() => {
                          if (!window.confirm(t("snmp.mibDeleteConfirm"))) return;
                          delMib.mutate(m.name);
                        }}
                      >
                        {t("dcim.common.delete")}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : mibsQ.data && mibsQ.data.length === 0 && !mibsQ.isLoading ? (
          <p className={dcimStyles.muted}>{t("snmp.mibsEmpty")}</p>
        ) : null}
      </section>

      <p className={dcimStyles.muted}>{t("snmp.mibsVendorNote")}</p>
    </>
  );
}

function EnterpriseGroupCard({
  group,
  manufacturers,
  onLink,
  onUnlink,
  linkPending,
}: {
  group: snmpApi.SnmpEnterpriseGroup;
  manufacturers: Manufacturer[];
  onLink: (manufacturerId: number, pen: number) => void;
  onUnlink: (manufacturerId: number) => void;
  linkPending: boolean;
}) {
  const { t } = useI18n();
  const pen = group.enterprise_number;
  const [selected, setSelected] = useState<string>(
    group.linked_manufacturer ? String(group.linked_manufacturer.id) : "",
  );

  useEffect(() => {
    setSelected(group.linked_manufacturer ? String(group.linked_manufacturer.id) : "");
  }, [group.linked_manufacturer?.id]);

  const title =
    pen == null
      ? t("snmp.enterpriseUnknown")
      : `${t("snmp.enterprisePenLabel")} ${pen} — ${group.iana_organization ?? "—"}`;

  return (
    <div
      className={dcimStyles.adminDetails}
      style={{ padding: "var(--space-3)", marginBottom: 0 }}
    >
      <h4 style={{ marginTop: 0, marginBottom: "var(--space-2)", fontSize: "var(--text-sm)" }}>{title}</h4>
      {pen != null ? (
        <div className={dcimStyles.formRow} style={{ alignItems: "flex-end", marginBottom: "var(--space-2)" }}>
          <label>
            {t("snmp.linkDcimManufacturer")}
            <select
              value={selected}
              onChange={(e) => setSelected(e.target.value)}
              disabled={linkPending || manufacturers.length === 0}
            >
              <option value="">{t("snmp.linkManufacturerPlaceholder")}</option>
              {manufacturers.map((m) => (
                <option key={m.id} value={String(m.id)}>
                  {m.name}
                  {m.iana_enterprise_number != null ? ` (PEN ${m.iana_enterprise_number})` : ""}
                </option>
              ))}
            </select>
          </label>
          <button
            type="button"
            className={dcimStyles.btn}
            disabled={linkPending || selected === ""}
            onClick={() => onLink(Number(selected), pen)}
          >
            {t("snmp.linkApply")}
          </button>
          {group.linked_manufacturer ? (
            <button
              type="button"
              className={dcimStyles.btnMuted}
              disabled={linkPending}
              onClick={() => onUnlink(group.linked_manufacturer!.id)}
            >
              {t("snmp.linkRemove")}
            </button>
          ) : null}
        </div>
      ) : (
        <p className={dcimStyles.muted}>{t("snmp.enterpriseNoPenHint")}</p>
      )}
      <ul style={{ margin: 0, paddingLeft: "1.2rem", fontSize: "var(--text-xs)" }}>
        {group.mib_files.map((n) => (
          <li key={n}>
            <code>{n}</code>
          </li>
        ))}
      </ul>
    </div>
  );
}
