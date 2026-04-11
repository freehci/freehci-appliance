import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useState, type ReactNode } from "react";
import { useI18n } from "@/i18n/I18nProvider";
import { ApiError } from "@/lib/api";
import * as dcimApi from "@/features/dcim/dcimApi";
import dcimStyles from "@/features/dcim/dcim.module.css";
import type { Manufacturer } from "@/features/dcim/types";
import * as snmpApi from "./snmpApi";

function enterpriseKey(pen: number | null): string {
  return pen == null ? "none" : String(pen);
}

function MibTreeList({
  nodes,
  depth,
}: {
  nodes: snmpApi.SnmpMibTreeNode[];
  depth: number;
}): ReactNode {
  const { t } = useI18n();
  if (!nodes.length) {
    return null;
  }
  return (
    <ul
      style={{
        margin: depth ? "var(--space-1) 0 0 0" : 0,
        paddingLeft: depth ? "1.25rem" : "1rem",
        listStyle: depth ? "disc" : "disc",
        fontSize: "var(--text-xs)",
      }}
    >
      {nodes.map((n) => (
        <li key={n.filename} style={{ marginBottom: "var(--space-1)" }}>
          <code>{n.filename}</code>
          {n.module_name ? <span className={dcimStyles.muted}> ({n.module_name})</span> : null}
          {n.extension_parent_module ? (
            <span className={dcimStyles.muted}> — {t("snmp.mibExtends")} {n.extension_parent_module}</span>
          ) : null}
          {n.parent_mib_missing ? (
            <span className={dcimStyles.err}> {t("snmp.mibParentMissing", { module: n.extension_parent_module ?? "?" })}</span>
          ) : null}
          {n.compile_status === "error" ? (
            <span className={dcimStyles.err} title={t("snmp.mibCompileErrorInTree")}>
              {" "}
              (⚠)
            </span>
          ) : null}
          {n.children?.length ? <MibTreeList nodes={n.children} depth={depth + 1} /> : null}
        </li>
      ))}
    </ul>
  );
}

export function SnmpEnterprisesPage() {
  const { t } = useI18n();
  const qc = useQueryClient();
  const [err, setErr] = useState<string | null>(null);
  const [autocreateMsg, setAutocreateMsg] = useState<string | null>(null);

  const entQ = useQuery({ queryKey: ["snmp", "enterprises"], queryFn: snmpApi.listSnmpEnterprises });
  const mfrQ = useQuery({ queryKey: ["dcim", "manufacturers", "all"], queryFn: dcimApi.listManufacturers });

  const invalidate = () => {
    void qc.invalidateQueries({ queryKey: ["snmp", "enterprises"] });
    void qc.invalidateQueries({ queryKey: ["snmp", "mibs"] });
    void qc.invalidateQueries({ queryKey: ["snmp", "mibs", "detailed"] });
  };

  const linkMfr = useMutation({
    mutationFn: ({ id, pen }: { id: number; pen: number | null }) =>
      dcimApi.updateManufacturer(id, { iana_enterprise_number: pen }),
    onSuccess: () => {
      setErr(null);
      void qc.invalidateQueries({ queryKey: ["dcim", "manufacturers"] });
      invalidate();
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const autocreateMut = useMutation({
    mutationFn: (pen: number | null) => snmpApi.autocreateSnmpDcimManufacturers({ enterprise_number: pen }),
    onSuccess: (r) => {
      setErr(null);
      const parts: string[] = [];
      if (r.created.length) {
        parts.push(t("snmp.autocreateCreatedCount", { n: String(r.created.length) }));
      }
      if (r.skipped.length) {
        parts.push(t("snmp.autocreateSkippedCount", { n: String(r.skipped.length) }));
      }
      setAutocreateMsg(parts.join(" · ") || t("snmp.autocreateNothing"));
      void qc.invalidateQueries({ queryKey: ["dcim", "manufacturers"] });
      invalidate();
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const manufacturers = mfrQ.data ?? [];
  const groups = entQ.data ?? [];

  return (
    <>
      {err ? <p className={dcimStyles.err}>{err}</p> : null}
      {autocreateMsg ? <p className={dcimStyles.muted}>{autocreateMsg}</p> : null}
      <p className={dcimStyles.muted} style={{ marginTop: 0 }}>
        {t("snmp.enterprisesPageIntro")}
      </p>

      <section className={dcimStyles.mfrDetailSection}>
        <h3 className={dcimStyles.mfrDetailSectionTitle}>{t("snmp.enterprisesBulkTitle")}</h3>
        <div className={dcimStyles.formRow} style={{ alignItems: "flex-end", flexWrap: "wrap", gap: "var(--space-2)" }}>
          <button
            type="button"
            className={dcimStyles.btn}
            disabled={autocreateMut.isPending}
            onClick={() => {
              setAutocreateMsg(null);
              if (!window.confirm(t("snmp.autocreateAllConfirm"))) return;
              autocreateMut.mutate(null);
            }}
            title={t("snmp.autocreateAllHint")}
          >
            {autocreateMut.isPending ? "…" : t("snmp.autocreateAllManufacturers")}
          </button>
        </div>
        <p className={dcimStyles.muted} style={{ marginBottom: 0 }}>
          {t("snmp.autocreateAllExplain")}
        </p>
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
                autocreatePending={autocreateMut.isPending}
                onAutocreateOne={() => {
                  setAutocreateMsg(null);
                  if (g.enterprise_number == null) return;
                  autocreateMut.mutate(g.enterprise_number);
                }}
              />
            ))}
          </div>
        ) : entQ.data && entQ.data.length === 0 && !entQ.isLoading ? (
          <p className={dcimStyles.muted}>{t("snmp.mibsEmpty")}</p>
        ) : null}
      </section>
    </>
  );
}

function EnterpriseGroupCard({
  group,
  manufacturers,
  onLink,
  onUnlink,
  linkPending,
  onAutocreateOne,
  autocreatePending,
}: {
  group: snmpApi.SnmpEnterpriseGroup;
  manufacturers: Manufacturer[];
  onLink: (manufacturerId: number, pen: number) => void;
  onUnlink: (manufacturerId: number) => void;
  linkPending: boolean;
  onAutocreateOne: () => void;
  autocreatePending: boolean;
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

  const tree = group.mib_tree?.length ? group.mib_tree : [];

  return (
    <div
      className={dcimStyles.adminDetails}
      style={{ padding: "var(--space-3)", marginBottom: 0 }}
    >
      <h4 style={{ marginTop: 0, marginBottom: "var(--space-2)", fontSize: "var(--text-sm)" }}>{title}</h4>
      {pen != null ? (
        <div
          className={dcimStyles.formRow}
          style={{ alignItems: "flex-end", marginBottom: "var(--space-2)", flexWrap: "wrap", gap: "var(--space-2)" }}
        >
          <button
            type="button"
            className={dcimStyles.btnMuted}
            disabled={autocreatePending || !!group.linked_manufacturer}
            onClick={onAutocreateOne}
            title={t("snmp.autocreateOneHint")}
          >
            {t("snmp.autocreateManufacturer")}
          </button>
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
      {tree.length > 0 ? (
        <MibTreeList nodes={tree} depth={0} />
      ) : (
        <ul style={{ margin: 0, paddingLeft: "1.2rem", fontSize: "var(--text-xs)" }}>
          {group.mib_files.map((n) => (
            <li key={n}>
              <code>{n}</code>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
