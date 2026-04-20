import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { Panel } from "@/components/ui/Panel";
import * as ipamApi from "@/features/ipam/ipamApi";
import { useI18n } from "@/i18n/I18nProvider";
import { ApiError } from "@/lib/api";
import * as api from "./dcimApi";
import dcimStyles from "./dcim.module.css";

export function DcimTenantsPage() {
  const { t } = useI18n();
  const qc = useQueryClient();
  const [err, setErr] = useState<string | null>(null);
  const [newName, setNewName] = useState("");
  const [newSlug, setNewSlug] = useState("");
  const [newDesc, setNewDesc] = useState("");
  const [selectedId, setSelectedId] = useState<number | null>(null);

  const [memberUserId, setMemberUserId] = useState("");
  const [memberRole, setMemberRole] = useState("member");

  const [grantScope, setGrantScope] = useState<"site" | "room" | "rack">("site");
  const [grantTargetId, setGrantTargetId] = useState("");
  const [grantAccess, setGrantAccess] = useState<"view" | "manage">("view");

  const tenantsQ = useQuery({ queryKey: ["tenants"], queryFn: api.listTenants });
  const usersQ = useQuery({ queryKey: ["ipam", "users"], queryFn: () => ipamApi.listUsers(500) });
  const sitesQ = useQuery({ queryKey: ["dcim", "sites"], queryFn: api.listSites });
  const roomsQ = useQuery({ queryKey: ["dcim", "rooms", "all"], queryFn: () => api.listRooms() });
  const racksQ = useQuery({ queryKey: ["dcim", "racks", "all-tenants-ui"], queryFn: () => api.listRacks() });

  const membersQ = useQuery({
    queryKey: ["tenants", selectedId, "members"],
    queryFn: () => api.listTenantMembers(selectedId!),
    enabled: selectedId != null && selectedId > 0,
  });

  const grantsQ = useQuery({
    queryKey: ["tenants", selectedId, "dcim-grants"],
    queryFn: () => api.listTenantDcimGrants(selectedId!),
    enabled: selectedId != null && selectedId > 0,
  });

  const userLabel = useMemo(() => {
    const m = new Map<number, string>();
    for (const u of usersQ.data ?? []) m.set(u.id, u.display_name ?? u.username);
    return m;
  }, [usersQ.data]);

  const grantScopeOptions = useMemo(() => {
    if (grantScope === "site") {
      return (sitesQ.data ?? []).map((s) => ({ id: s.id, label: `${s.name} (#${s.id})` }));
    }
    if (grantScope === "room") {
      return (roomsQ.data ?? []).map((r) => ({ id: r.id, label: `${r.name} — site ${r.site_id} (#${r.id})` }));
    }
    return (racksQ.data ?? []).map((k) => ({ id: k.id, label: `${k.name} — rom ${k.room_id} (#${k.id})` }));
  }, [grantScope, sitesQ.data, roomsQ.data, racksQ.data]);

  const createTenantM = useMutation({
    mutationFn: () =>
      api.createTenant({
        name: newName.trim(),
        slug: newSlug.trim().toLowerCase(),
        description: newDesc.trim() === "" ? null : newDesc.trim(),
      }),
    onSuccess: () => {
      setErr(null);
      setNewName("");
      setNewSlug("");
      setNewDesc("");
      void qc.invalidateQueries({ queryKey: ["tenants"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const addMemberM = useMutation({
    mutationFn: () =>
      api.addTenantMember(selectedId!, {
        user_id: Number(memberUserId),
        role: memberRole.trim() || "member",
      }),
    onSuccess: () => {
      setErr(null);
      setMemberUserId("");
      setMemberRole("member");
      void qc.invalidateQueries({ queryKey: ["tenants", selectedId, "members"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const removeMemberM = useMutation({
    mutationFn: (userId: number) => api.removeTenantMember(selectedId!, userId),
    onSuccess: () => {
      setErr(null);
      void qc.invalidateQueries({ queryKey: ["tenants", selectedId, "members"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const addGrantM = useMutation({
    mutationFn: () =>
      api.addTenantDcimGrant(selectedId!, {
        scope_type: grantScope,
        scope_id: Number(grantTargetId),
        access: grantAccess,
      }),
    onSuccess: () => {
      setErr(null);
      setGrantTargetId("");
      void qc.invalidateQueries({ queryKey: ["tenants", selectedId, "dcim-grants"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const removeGrantM = useMutation({
    mutationFn: (grantId: number) => api.removeTenantDcimGrant(selectedId!, grantId),
    onSuccess: () => {
      setErr(null);
      void qc.invalidateQueries({ queryKey: ["tenants", selectedId, "dcim-grants"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  return (
    <Panel title={t("dcim.tenants.title")}>
      <p className={dcimStyles.muted}>{t("dcim.tenants.intro")}</p>
      {err ? <p className={dcimStyles.err}>{err}</p> : null}

      <section className={dcimStyles.mfrDetailSection}>
        <h3 className={dcimStyles.mfrDetailSectionTitle}>{t("dcim.tenants.createTitle")}</h3>
        <form
          className={dcimStyles.formRow}
          style={{ flexWrap: "wrap", alignItems: "flex-end" }}
          onSubmit={(e) => {
            e.preventDefault();
            setErr(null);
            if (!newName.trim() || !newSlug.trim()) {
              setErr(t("dcim.tenants.createMissing"));
              return;
            }
            createTenantM.mutate();
          }}
        >
          <label>
            {t("dcim.tenants.name")}
            <input value={newName} onChange={(e) => setNewName(e.target.value)} required />
          </label>
          <label>
            {t("dcim.tenants.slug")}
            <input value={newSlug} onChange={(e) => setNewSlug(e.target.value)} placeholder="kunde-140" required />
          </label>
          <label className={dcimStyles.formFullWidth} style={{ minWidth: "220px" }}>
            {t("dcim.tenants.description")}
            <input value={newDesc} onChange={(e) => setNewDesc(e.target.value)} />
          </label>
          <button type="submit" className={dcimStyles.btn} disabled={createTenantM.isPending}>
            {createTenantM.isPending ? "…" : t("dcim.tenants.createBtn")}
          </button>
        </form>
      </section>

      <h3 className={dcimStyles.mfrDetailSectionTitle} style={{ marginTop: "var(--space-4)" }}>
        {t("dcim.tenants.listTitle")}
      </h3>
      {tenantsQ.isLoading ? <p className={dcimStyles.muted}>{t("dcim.common.loading")}</p> : null}
      {tenantsQ.data && tenantsQ.data.length === 0 && !tenantsQ.isLoading ? (
        <p className={dcimStyles.muted}>{t("dcim.tenants.empty")}</p>
      ) : null}
      {tenantsQ.data && tenantsQ.data.length > 0 ? (
        <table className={dcimStyles.table}>
          <thead>
            <tr>
              <th>{t("dcim.common.id")}</th>
              <th>{t("dcim.tenants.name")}</th>
              <th>{t("dcim.tenants.slug")}</th>
              <th>{t("dcim.tenants.createdCol")}</th>
              <th>{t("dcim.tenants.selectCol")}</th>
            </tr>
          </thead>
          <tbody>
            {(tenantsQ.data ?? []).map((tn) => (
              <tr key={tn.id}>
                <td>{tn.id}</td>
                <td>{tn.name}</td>
                <td>
                  <code>{tn.slug}</code>
                </td>
                <td className={dcimStyles.muted}>{new Date(tn.created_at).toLocaleString()}</td>
                <td>
                  <button
                    type="button"
                    className={dcimStyles.btnLink}
                    onClick={() => {
                      setSelectedId(tn.id);
                      setErr(null);
                      setGrantTargetId("");
                    }}
                  >
                    {selectedId === tn.id ? t("dcim.tenants.selected") : t("dcim.tenants.select")}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : null}

      {selectedId != null ? (
        <>
          <section className={dcimStyles.mfrDetailSection} style={{ marginTop: "var(--space-4)" }}>
            <h3 className={dcimStyles.mfrDetailSectionTitle}>{t("dcim.tenants.membersTitle")}</h3>
            <p className={dcimStyles.muted}>{t("dcim.tenants.membersIntro")}</p>
            <form
              className={dcimStyles.formRow}
              style={{ flexWrap: "wrap", alignItems: "flex-end" }}
              onSubmit={(e) => {
                e.preventDefault();
                setErr(null);
                const uid = Number(memberUserId);
                if (!Number.isFinite(uid) || uid < 1) {
                  setErr(t("dcim.tenants.memberUserInvalid"));
                  return;
                }
                addMemberM.mutate();
              }}
            >
              <label>
                {t("dcim.tenants.user")}
                <select value={memberUserId} onChange={(e) => setMemberUserId(e.target.value)} required>
                  <option value="">{t("dcim.common.choose")}</option>
                  {(usersQ.data ?? []).map((u) => (
                    <option key={u.id} value={String(u.id)}>
                      {u.display_name ?? u.username} (#{u.id})
                    </option>
                  ))}
                </select>
              </label>
              <label>
                {t("dcim.tenants.role")}
                <input value={memberRole} onChange={(e) => setMemberRole(e.target.value)} />
              </label>
              <button type="submit" className={dcimStyles.btn} disabled={addMemberM.isPending}>
                {addMemberM.isPending ? "…" : t("dcim.tenants.addMember")}
              </button>
            </form>
            {membersQ.isLoading ? <p className={dcimStyles.muted}>{t("dcim.common.loading")}</p> : null}
            {membersQ.data && membersQ.data.length > 0 ? (
              <table className={dcimStyles.table} style={{ marginTop: "var(--space-2)" }}>
                <thead>
                  <tr>
                    <th>{t("dcim.common.id")}</th>
                    <th>{t("dcim.tenants.user")}</th>
                    <th>{t("dcim.tenants.role")}</th>
                    <th />
                  </tr>
                </thead>
                <tbody>
                  {membersQ.data.map((m) => (
                    <tr key={m.id}>
                      <td>{m.id}</td>
                      <td>
                        {userLabel.get(m.user_id) ?? `#${m.user_id}`} ({m.user_id})
                      </td>
                      <td>{m.role}</td>
                      <td>
                        <button
                          type="button"
                          className={dcimStyles.btnLink}
                          disabled={removeMemberM.isPending}
                          onClick={() => removeMemberM.mutate(m.user_id)}
                        >
                          {t("dcim.common.delete")}
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              !membersQ.isLoading && <p className={dcimStyles.muted}>{t("dcim.tenants.membersEmpty")}</p>
            )}
          </section>

          <section className={dcimStyles.mfrDetailSection} style={{ marginTop: "var(--space-4)" }}>
            <h3 className={dcimStyles.mfrDetailSectionTitle}>{t("dcim.tenants.grantsTitle")}</h3>
            <p className={dcimStyles.muted}>{t("dcim.tenants.grantsIntro")}</p>
            <form
              className={dcimStyles.formRow}
              style={{ flexWrap: "wrap", alignItems: "flex-end" }}
              onSubmit={(e) => {
                e.preventDefault();
                setErr(null);
                const sid = Number(grantTargetId);
                if (!Number.isFinite(sid) || sid < 1) {
                  setErr(t("dcim.tenants.grantTargetInvalid"));
                  return;
                }
                addGrantM.mutate();
              }}
            >
              <label>
                {t("dcim.tenants.scopeType")}
                <select
                  value={grantScope}
                  onChange={(e) => {
                    setGrantScope(e.target.value as "site" | "room" | "rack");
                    setGrantTargetId("");
                  }}
                >
                  <option value="site">{t("dcim.tenants.scopeSite")}</option>
                  <option value="room">{t("dcim.tenants.scopeRoom")}</option>
                  <option value="rack">{t("dcim.tenants.scopeRack")}</option>
                </select>
              </label>
              <label>
                {t("dcim.tenants.scopeTarget")}
                <select
                  value={grantTargetId}
                  onChange={(e) => setGrantTargetId(e.target.value)}
                  required
                >
                  <option value="">{t("dcim.common.choose")}</option>
                  {grantScopeOptions.map((o) => (
                    <option key={o.id} value={String(o.id)}>
                      {o.label}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                {t("dcim.tenants.access")}
                <select value={grantAccess} onChange={(e) => setGrantAccess(e.target.value as "view" | "manage")}>
                  <option value="view">{t("dcim.tenants.accessView")}</option>
                  <option value="manage">{t("dcim.tenants.accessManage")}</option>
                </select>
              </label>
              <button type="submit" className={dcimStyles.btn} disabled={addGrantM.isPending}>
                {addGrantM.isPending ? "…" : t("dcim.tenants.addGrant")}
              </button>
            </form>
            {grantsQ.isLoading ? <p className={dcimStyles.muted}>{t("dcim.common.loading")}</p> : null}
            {grantsQ.data && grantsQ.data.length > 0 ? (
              <table className={dcimStyles.table} style={{ marginTop: "var(--space-2)" }}>
                <thead>
                  <tr>
                    <th>{t("dcim.common.id")}</th>
                    <th>{t("dcim.tenants.scopeType")}</th>
                    <th>{t("dcim.tenants.scopeIdCol")}</th>
                    <th>{t("dcim.tenants.access")}</th>
                    <th />
                  </tr>
                </thead>
                <tbody>
                  {grantsQ.data.map((g) => (
                    <tr key={g.id}>
                      <td>{g.id}</td>
                      <td>{g.scope_type}</td>
                      <td>{g.scope_id}</td>
                      <td>{g.access}</td>
                      <td>
                        <button
                          type="button"
                          className={dcimStyles.btnLink}
                          disabled={removeGrantM.isPending}
                          onClick={() => removeGrantM.mutate(g.id)}
                        >
                          {t("dcim.common.delete")}
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              !grantsQ.isLoading && <p className={dcimStyles.muted}>{t("dcim.tenants.grantsEmpty")}</p>
            )}
          </section>
        </>
      ) : (
        <p className={dcimStyles.muted} style={{ marginTop: "var(--space-3)" }}>
          {t("dcim.tenants.selectHint")}
        </p>
      )}
    </Panel>
  );
}
