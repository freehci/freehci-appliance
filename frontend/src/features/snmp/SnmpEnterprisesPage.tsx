import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useState, type ReactNode } from "react";
import { ConfirmModal } from "@/components/ui/ConfirmModal";
import { HoverHelpCard } from "@/components/ui/HoverHelpCard";
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
  const [penInput, setPenInput] = useState("");
  const [autocreateAllConfirmOpen, setAutocreateAllConfirmOpen] = useState(false);

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
      const summary = parts.join(" · ") || t("snmp.autocreateNothing");
      const detailLines: string[] = [
        ...r.created.map((c) => `${c.name} (PEN ${c.enterprise_number})`),
        ...r.skipped.slice(0, 12),
      ];
      const detail = detailLines.join("\n");
      setAutocreateMsg([summary, detail].filter(Boolean).join("\n"));
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
      {autocreateMsg ? (
        <pre
          className={dcimStyles.muted}
          style={{ whiteSpace: "pre-wrap", fontFamily: "inherit", fontSize: "var(--text-sm)" }}
        >
          {autocreateMsg}
        </pre>
      ) : null}
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
              setAutocreateAllConfirmOpen(true);
            }}
            title={t("snmp.autocreateAllHint")}
          >
            {autocreateMut.isPending ? "…" : t("snmp.autocreateAllManufacturers")}
          </button>
        </div>
        <p className={dcimStyles.muted} style={{ marginBottom: "var(--space-2)" }}>
          {t("snmp.autocreateAllExplain")}
        </p>
        <h4 className={dcimStyles.mfrDetailSectionTitle} style={{ fontSize: "var(--text-sm)", marginBottom: "var(--space-2)" }}>
          {t("snmp.autocreateByPenTitle")}
        </h4>
        <div className={dcimStyles.formRow} style={{ alignItems: "flex-end", flexWrap: "wrap", gap: "var(--space-2)" }}>
          <label>
            {t("snmp.autocreateByPenLabel")}
            <input
              type="number"
              min={0}
              step={1}
              value={penInput}
              onChange={(e) => setPenInput(e.target.value)}
              placeholder="1588"
              style={{ width: "8rem", marginLeft: "var(--space-2)" }}
            />
          </label>
          <button
            type="button"
            className={dcimStyles.btnMuted}
            disabled={autocreateMut.isPending || penInput.trim() === ""}
            onClick={() => {
              setAutocreateMsg(null);
              const n = Number.parseInt(penInput.trim(), 10);
              if (!Number.isFinite(n) || n < 0) {
                setErr(t("snmp.autocreateByPenInvalid"));
                return;
              }
              setErr(null);
              autocreateMut.mutate(n);
            }}
          >
            {autocreateMut.isPending ? "…" : t("snmp.autocreateByPenButton")}
          </button>
        </div>
        <p className={dcimStyles.muted} style={{ marginTop: "var(--space-2)", marginBottom: 0 }}>
          {t("snmp.autocreateByPenHint")}
        </p>
      </section>

      <section className={dcimStyles.mfrDetailSection}>
        <h3 className={dcimStyles.mfrDetailSectionTitle}>{t("snmp.enterprisesTitle")}</h3>
        <p
          className={dcimStyles.muted}
          style={{
            marginTop: 0,
            display: "flex",
            flexWrap: "wrap",
            alignItems: "center",
            gap: "0.35rem",
          }}
        >
          <span>{t("snmp.enterprisesHintShort")}</span>
          <HoverHelpCard ariaLabel={t("snmp.enterprisesHelpAria")}>
            <p>{t("snmp.enterprisesHint")}</p>
          </HoverHelpCard>
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
      <ConfirmModal
        open={autocreateAllConfirmOpen}
        onClose={() => {
          if (!autocreateMut.isPending) setAutocreateAllConfirmOpen(false);
        }}
        title={t("ui.confirmTitle")}
        message={t("snmp.autocreateAllConfirm")}
        confirmLabel={t("ui.confirmProceed")}
        cancelLabel={t("dcim.common.cancel")}
        pending={autocreateMut.isPending}
        onConfirm={() => {
          autocreateMut.mutate(null, { onSettled: () => setAutocreateAllConfirmOpen(false) });
        }}
      />
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
    <div className={dcimStyles.adminDetails} style={{ marginTop: 0 }}>
      <div className={dcimStyles.enterpriseGroupInner}>
        <h4 className={dcimStyles.mfrDetailSectionTitle} style={{ fontSize: "var(--text-sm)" }}>
          {title}
        </h4>
        {pen != null ? (
          <form
            className={dcimStyles.formRow}
            style={{ flexDirection: "column", alignItems: "stretch", marginBottom: 0 }}
            onSubmit={(e) => e.preventDefault()}
          >
            <label>
              {t("snmp.linkDcimManufacturer")}
              <select
                value={selected}
                onChange={(e) => setSelected(e.target.value)}
                disabled={linkPending || manufacturers.length === 0}
                style={{ width: "100%", maxWidth: "28rem" }}
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
            <div
              className={dcimStyles.formRow}
              style={{
                marginBottom: 0,
                marginTop: 0,
                alignItems: "center",
                flexWrap: "wrap",
                gap: "var(--space-2)",
              }}
              role="group"
              aria-label={t("snmp.enterpriseActionsAria")}
            >
              <button
                type="button"
                className={dcimStyles.btn}
                disabled={autocreatePending}
                onClick={onAutocreateOne}
                title={
                  group.linked_manufacturer
                    ? t("snmp.autocreateOneDespiteLinkHint")
                    : t("snmp.autocreateOneHint")
                }
              >
                {t("snmp.autocreateManufacturer")}
              </button>
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
          </form>
        ) : (
          <p className={dcimStyles.muted}>{t("snmp.enterpriseNoPenHint")}</p>
        )}
        {tree.length > 0 ? (
          <MibTreeList nodes={tree} depth={0} />
        ) : (
          <ul style={{ margin: "var(--space-2) 0 0", paddingLeft: "1.2rem", fontSize: "var(--text-xs)" }}>
            {group.mib_files.map((n) => (
              <li key={n}>
                <code>{n}</code>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
