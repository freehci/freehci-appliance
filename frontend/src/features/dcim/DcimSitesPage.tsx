import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import "leaflet/dist/leaflet.css";
import L from "leaflet";
import { MapContainer, Marker, Popup, TileLayer } from "react-leaflet";
import { ConfirmModal } from "@/components/ui/ConfirmModal";
import { Panel } from "@/components/ui/Panel";
import { useI18n } from "@/i18n/I18nProvider";
import { ApiError } from "@/lib/api";
import * as api from "./dcimApi";
import { DcimInnerTabs } from "./DcimInnerTabs";
import styles from "./dcim.module.css";
import * as ipamApi from "@/features/ipam/ipamApi";

// Fix standard marker icons under bundlers (Vite).
import marker2x from "leaflet/dist/images/marker-icon-2x.png";
import marker1x from "leaflet/dist/images/marker-icon.png";
import markerShadow from "leaflet/dist/images/marker-shadow.png";

export function DcimSitesPage() {
  const { t } = useI18n();
  const qc = useQueryClient();
  const [name, setName] = useState("");
  const [slug, setSlug] = useState("");
  const [err, setErr] = useState<string | null>(null);
  const [tab, setTab] = useState("main");
  const [editId, setEditId] = useState<number | null>(null);
  const [edit, setEdit] = useState<Record<string, string>>({});
  const [geocodeResult, setGeocodeResult] = useState<api.SiteGeocodeResponse | null>(null);
  const [grantUserId, setGrantUserId] = useState<string>("");
  const [grantRoleId, setGrantRoleId] = useState<string>("");
  const [grantIsContact, setGrantIsContact] = useState<boolean>(true);
  const [grantNotes, setGrantNotes] = useState<string>("");
  const [newPerson, setNewPerson] = useState<boolean>(false);
  const [newUsername, setNewUsername] = useState<string>("");
  const [newDisplayName, setNewDisplayName] = useState<string>("");
  const [newEmail, setNewEmail] = useState<string>("");
  const [newPhone, setNewPhone] = useState<string>("");
  const [grantDeleteId, setGrantDeleteId] = useState<number | null>(null);

  const q = useQuery({ queryKey: ["dcim", "sites"], queryFn: api.listSites });
  const selected = useMemo(() => (q.data ?? []).find((s) => s.id === editId) ?? null, [q.data, editId]);
  const rolesQ = useQuery({ queryKey: ["dcim", "site-roles"], queryFn: api.listSiteRoles });
  const usersQ = useQuery({ queryKey: ["ipam", "users"], queryFn: () => ipamApi.listUsers(500) });
  const grantsQ = useQuery({
    queryKey: ["dcim", "site-access", editId],
    queryFn: () => api.listSiteAccess(editId!),
    enabled: editId != null,
  });
  const latLon = useMemo(() => {
    const lat = edit.latitude?.trim() ? Number(edit.latitude) : null;
    const lon = edit.longitude?.trim() ? Number(edit.longitude) : null;
    if (lat == null || lon == null) return null;
    if (!Number.isFinite(lat) || !Number.isFinite(lon)) return null;
    return { lat, lon };
  }, [edit.latitude, edit.longitude]);
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

  const um = useMutation({
    mutationFn: () =>
      api.updateSite(editId!, {
        name: edit.name?.trim() || undefined,
        description: edit.description?.trim() || null,
        address_line1: edit.address_line1?.trim() || null,
        address_line2: edit.address_line2?.trim() || null,
        postal_code: edit.postal_code?.trim() || null,
        city: edit.city?.trim() || null,
        county: edit.county?.trim() || null,
        country: edit.country?.trim() || null,
        latitude: edit.latitude?.trim() ? Number(edit.latitude) : null,
        longitude: edit.longitude?.trim() ? Number(edit.longitude) : null,
        address_note: edit.address_note?.trim() || null,
      }),
    onSuccess: () => {
      setErr(null);
      void qc.invalidateQueries({ queryKey: ["dcim", "sites"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const geocodeM = useMutation({
    mutationFn: () =>
      api.geocodeSite(editId!, {
        query: null,
        limit: 5,
      }),
    onSuccess: (data) => {
      setGeocodeResult(data);
      const best = data.candidates[0];
      if (best) {
        setEdit((x) => ({ ...x, latitude: String(best.latitude), longitude: String(best.longitude) }));
      }
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const addGrantM = useMutation({
    mutationFn: async () => {
      const roleId = Number(grantRoleId);
      if (!Number.isFinite(roleId) || roleId <= 0) throw new Error("role_id mangler");

      let userId: number;
      if (newPerson) {
        const u = await ipamApi.createUser({
          username: newUsername.trim(),
          display_name: newDisplayName.trim() || null,
          email: newEmail.trim() || null,
          phone: newPhone.trim() || null,
          kind: "person",
          notes: null,
        });
        userId = u.id;
      } else {
        const uid = Number(grantUserId);
        if (!Number.isFinite(uid) || uid <= 0) throw new Error("user_id mangler");
        userId = uid;
      }

      return api.createSiteAccess(editId!, {
        user_id: userId,
        role_id: roleId,
        is_contact: grantIsContact,
        notes: grantNotes.trim() || null,
      });
    },
    onSuccess: () => {
      setErr(null);
      setGrantNotes("");
      setNewPerson(false);
      setNewUsername("");
      setNewDisplayName("");
      setNewEmail("");
      setNewPhone("");
      void qc.invalidateQueries({ queryKey: ["dcim", "site-access", editId] });
      void qc.invalidateQueries({ queryKey: ["ipam", "users"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const delGrantM = useMutation({
    mutationFn: (grantId: number) => api.deleteSiteAccess(editId!, grantId),
    onSuccess: () => void qc.invalidateQueries({ queryKey: ["dcim", "site-access", editId] }),
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  return (
    <Panel title={t("nav.dcimSites")}>
      <DcimInnerTabs
        tabs={[{ id: "main", label: t("nav.dcimSites"), icon: "sites" }]}
        activeId={tab}
        onChange={setTab}
        ariaLabel={t("dcim.innerNavAria")}
      />
      {tab === "main" ? (
        <>
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
          {t("dcim.common.name")}
          <input value={name} onChange={(e) => setName(e.target.value)} required />
        </label>
        <label>
          {t("dcim.common.slug")}
          <input
            value={slug}
            onChange={(e) => setSlug(e.target.value)}
            placeholder={t("dcim.sites.slugPh")}
            required
            pattern="[a-z0-9]+(?:-[a-z0-9]+)*"
            title={t("dcim.sites.slugPatternTitle")}
          />
        </label>
        <button type="submit" className={styles.btn} disabled={m.isPending}>
          {m.isPending ? t("dcim.common.creating") : t("dcim.common.create")}
        </button>
      </form>
      {q.isError ? (
        <p className={styles.err}>
          {t("dcim.sites.loadError")} {(q.error as Error).message}
        </p>
      ) : null}
      {q.isLoading ? <p className={styles.muted}>{t("dcim.common.loading")}</p> : null}
      {q.data && q.data.length === 0 ? <p className={styles.muted}>{t("dcim.sites.empty")}</p> : null}
      {q.data && q.data.length > 0 ? (
        <table className={styles.table}>
          <thead>
            <tr>
              <th>{t("dcim.common.id")}</th>
              <th>{t("dcim.common.name")}</th>
              <th>{t("dcim.common.slug")}</th>
              <th>{t("dcim.common.actions")}</th>
            </tr>
          </thead>
          <tbody>
            {q.data.map((s) => (
              <tr key={s.id}>
                <td>{s.id}</td>
                <td>{s.name}</td>
                <td>{s.slug}</td>
                <td>
                  <button
                    type="button"
                    className={styles.btnMuted}
                    onClick={() => {
                      setEditId(s.id);
                      setGeocodeResult(null);
                      setGrantUserId("");
                      setGrantRoleId("");
                      setGrantIsContact(true);
                      setGrantNotes("");
                      setNewPerson(false);
                      setNewUsername("");
                      setNewDisplayName("");
                      setNewEmail("");
                      setNewPhone("");
                      setEdit({
                        name: s.name ?? "",
                        description: s.description ?? "",
                        address_line1: (s.address_line1 ?? "") as string,
                        address_line2: (s.address_line2 ?? "") as string,
                        postal_code: (s.postal_code ?? "") as string,
                        city: (s.city ?? "") as string,
                        county: (s.county ?? "") as string,
                        country: (s.country ?? "") as string,
                        latitude: s.latitude != null ? String(s.latitude) : "",
                        longitude: s.longitude != null ? String(s.longitude) : "",
                        address_note: (s.address_note ?? "") as string,
                      });
                    }}
                  >
                    {t("dcim.sites.edit")}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : null}
      {selected && editId != null ? (
        <div style={{ marginTop: "1rem" }}>
          <div style={{ fontSize: "var(--text-sm)", fontWeight: 600, marginBottom: "0.5rem" }}>
            {t("dcim.sites.editTitle")}
          </div>
          <form
            className={styles.formRow}
            onSubmit={(e) => {
              e.preventDefault();
              setErr(null);
              um.mutate();
            }}
          >
            <label>
              {t("dcim.common.name")}
              <input value={edit.name ?? ""} onChange={(e) => setEdit((x) => ({ ...x, name: e.target.value }))} />
            </label>
            <label>
              {t("dcim.common.description")}
              <input
                value={edit.description ?? ""}
                onChange={(e) => setEdit((x) => ({ ...x, description: e.target.value }))}
              />
            </label>
            <label>
              {t("dcim.sites.addressLine1")}
              <input
                value={edit.address_line1 ?? ""}
                onChange={(e) => setEdit((x) => ({ ...x, address_line1: e.target.value }))}
              />
            </label>
            <label>
              {t("dcim.sites.addressLine2")}
              <input
                value={edit.address_line2 ?? ""}
                onChange={(e) => setEdit((x) => ({ ...x, address_line2: e.target.value }))}
              />
            </label>
            <label>
              {t("dcim.sites.postalCode")}
              <input
                value={edit.postal_code ?? ""}
                onChange={(e) => setEdit((x) => ({ ...x, postal_code: e.target.value }))}
              />
            </label>
            <label>
              {t("dcim.sites.city")}
              <input value={edit.city ?? ""} onChange={(e) => setEdit((x) => ({ ...x, city: e.target.value }))} />
            </label>
            <label>
              {t("dcim.sites.county")}
              <input
                value={edit.county ?? ""}
                onChange={(e) => setEdit((x) => ({ ...x, county: e.target.value }))}
              />
            </label>
            <label>
              {t("dcim.sites.country")}
              <input
                value={edit.country ?? ""}
                onChange={(e) => setEdit((x) => ({ ...x, country: e.target.value }))}
              />
            </label>
            <label>
              {t("dcim.sites.latitude")}
              <input
                value={edit.latitude ?? ""}
                onChange={(e) => setEdit((x) => ({ ...x, latitude: e.target.value }))}
              />
            </label>
            <label>
              {t("dcim.sites.longitude")}
              <input
                value={edit.longitude ?? ""}
                onChange={(e) => setEdit((x) => ({ ...x, longitude: e.target.value }))}
              />
            </label>
            <label style={{ flex: "1 1 100%" }}>
              {t("dcim.sites.addressNote")}
              <input
                value={edit.address_note ?? ""}
                onChange={(e) => setEdit((x) => ({ ...x, address_note: e.target.value }))}
              />
            </label>
            <div style={{ display: "flex", gap: "0.5rem", flex: "1 1 100%" }}>
              <button type="submit" className={styles.btn} disabled={um.isPending}>
                {um.isPending ? t("dcim.common.saving") : t("dcim.common.save")}
              </button>
              <button
                type="button"
                className={styles.btnMuted}
                disabled={geocodeM.isPending}
                onClick={() => {
                  setErr(null);
                  geocodeM.mutate();
                }}
              >
                {geocodeM.isPending ? t("dcim.sites.geocoding") : t("dcim.sites.geocode")}
              </button>
              <button
                type="button"
                className={styles.btnMuted}
                onClick={() => {
                  setEditId(null);
                  setEdit({});
                  setGeocodeResult(null);
                }}
              >
                {t("dcim.common.cancel")}
              </button>
            </div>
            {geocodeResult?.candidates?.length ? (
              <div style={{ flex: "1 1 100%", fontSize: "var(--text-xs)", color: "var(--color-text-muted)" }}>
                {t("dcim.sites.geocodeBestPrefix")} <span>{geocodeResult.candidates[0].display_name}</span>
              </div>
            ) : null}
          </form>
          {latLon ? (
            <div style={{ marginTop: "0.75rem" }}>
              <div style={{ fontSize: "var(--text-xs)", color: "var(--color-text-muted)", marginBottom: "0.25rem" }}>
                {t("dcim.sites.mapTitle")}
              </div>
              <MapContainer
                center={[latLon.lat, latLon.lon]}
                zoom={15}
                style={{ height: 280, width: "100%", borderRadius: "var(--radius-sm)" }}
              >
                <TileLayer
                  attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                  url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />
                <Marker
                  position={[latLon.lat, latLon.lon]}
                  icon={
                    new L.Icon({
                      iconUrl: marker1x,
                      iconRetinaUrl: marker2x,
                      shadowUrl: markerShadow,
                      iconSize: [25, 41],
                      iconAnchor: [12, 41],
                      popupAnchor: [1, -34],
                      shadowSize: [41, 41],
                    })
                  }
                >
                  <Popup>
                    <div style={{ fontSize: 12 }}>
                      <div style={{ fontWeight: 600 }}>{selected.name}</div>
                      <div>
                        {latLon.lat.toFixed(6)}, {latLon.lon.toFixed(6)}
                      </div>
                    </div>
                  </Popup>
                </Marker>
              </MapContainer>
            </div>
          ) : null}

          <div style={{ marginTop: "1rem" }}>
            <div style={{ fontSize: "var(--text-xs)", color: "var(--color-text-muted)", marginBottom: "0.25rem" }}>
              {t("dcim.sites.accessTitle")}
            </div>

            {grantsQ.isLoading ? <p className={styles.muted}>{t("dcim.common.loading")}</p> : null}
            {grantsQ.isError ? <p className={styles.err}>{(grantsQ.error as Error).message}</p> : null}

            {grantsQ.data?.length ? (
              <table className={styles.table}>
                <thead>
                  <tr>
                    <th>{t("dcim.sites.accessKind")}</th>
                    <th>{t("dcim.sites.accessUser")}</th>
                    <th>{t("dcim.sites.accessRole")}</th>
                    <th>{t("dcim.common.actions")}</th>
                  </tr>
                </thead>
                <tbody>
                  {grantsQ.data.map((g) => {
                    const u = (usersQ.data ?? []).find((x) => x.id === g.user_id);
                    const r = (rolesQ.data ?? []).find((x) => x.id === g.role_id);
                    return (
                      <tr key={g.id}>
                        <td>{g.is_contact ? t("dcim.sites.accessKindContact") : t("dcim.sites.accessKindAccess")}</td>
                        <td>{u?.display_name || u?.username || String(g.user_id)}</td>
                        <td>{r?.name || String(g.role_id)}</td>
                        <td>
                          <div className={styles.tableIconActions}>
                            <button
                              type="button"
                              className={`${styles.tableIconBtn} ${styles.tableIconBtnDanger}`.trim()}
                              title={t("dcim.common.delete")}
                              aria-label={t("dcim.common.delete")}
                              disabled={delGrantM.isPending}
                              onClick={() => setGrantDeleteId(g.id)}
                            >
                              <i className="fas fa-trash-can" aria-hidden />
                            </button>
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            ) : null}

            <form
              className={styles.formRow}
              onSubmit={(e) => {
                e.preventDefault();
                setErr(null);
                addGrantM.mutate();
              }}
              style={{ marginTop: "0.75rem" }}
            >
              <label>
                {t("dcim.sites.accessKind")}
                <select
                  value={grantIsContact ? "contact" : "access"}
                  onChange={(e) => setGrantIsContact(e.target.value === "contact")}
                >
                  <option value="contact">{t("dcim.sites.accessKindContact")}</option>
                  <option value="access">{t("dcim.sites.accessKindAccess")}</option>
                </select>
              </label>
              <label>
                {t("dcim.sites.accessUser")}
                <div style={{ display: "flex", gap: "0.5rem", alignItems: "center" }}>
                  <input
                    type="checkbox"
                    checked={newPerson}
                    onChange={(e) => setNewPerson(e.target.checked)}
                    aria-label={t("dcim.sites.accessNewPerson")}
                  />
                  <span style={{ fontSize: "var(--text-xs)", color: "var(--color-text-muted)" }}>
                    {t("dcim.sites.accessNewPerson")}
                  </span>
                </div>
                {!newPerson ? (
                  <select value={grantUserId} onChange={(e) => setGrantUserId(e.target.value)} required>
                    <option value="">{t("dcim.common.choose")}</option>
                    {(usersQ.data ?? []).map((u) => (
                      <option key={u.id} value={String(u.id)}>
                        {u.display_name || u.username}
                      </option>
                    ))}
                  </select>
                ) : (
                  <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem" }}>
                    <input
                      value={newUsername}
                      onChange={(e) => setNewUsername(e.target.value)}
                      placeholder={t("dcim.sites.accessUsernamePh")}
                      required
                    />
                    <input
                      value={newDisplayName}
                      onChange={(e) => setNewDisplayName(e.target.value)}
                      placeholder={t("dcim.sites.accessDisplayNamePh")}
                    />
                    <input
                      value={newEmail}
                      onChange={(e) => setNewEmail(e.target.value)}
                      placeholder={t("dcim.sites.accessEmailPh")}
                    />
                    <input
                      value={newPhone}
                      onChange={(e) => setNewPhone(e.target.value)}
                      placeholder={t("dcim.sites.accessPhonePh")}
                    />
                  </div>
                )}
              </label>
              <label>
                {t("dcim.sites.accessRole")}
                <select value={grantRoleId} onChange={(e) => setGrantRoleId(e.target.value)} required>
                  <option value="">{t("dcim.common.choose")}</option>
                  {(rolesQ.data ?? []).map((r) => (
                    <option key={r.id} value={String(r.id)}>
                      {r.name}
                    </option>
                  ))}
                </select>
              </label>
              <label style={{ flex: "1 1 100%" }}>
                {t("dcim.sites.accessNotes")}
                <input value={grantNotes} onChange={(e) => setGrantNotes(e.target.value)} />
              </label>
              <button type="submit" className={styles.btn} disabled={addGrantM.isPending}>
                {addGrantM.isPending ? t("dcim.common.creating") : t("dcim.common.add")}
              </button>
            </form>
          </div>
        </div>
      ) : null}
        </>
      ) : null}
      <ConfirmModal
        open={grantDeleteId != null}
        onClose={() => {
          if (!delGrantM.isPending) setGrantDeleteId(null);
        }}
        title={t("ui.confirmTitle")}
        message={t("dcim.sites.deleteGrantConfirm")}
        confirmLabel={t("dcim.common.delete")}
        cancelLabel={t("dcim.common.cancel")}
        danger
        pending={delGrantM.isPending}
        onConfirm={() => {
          if (grantDeleteId == null) return;
          delGrantM.mutate(grantDeleteId, { onSettled: () => setGrantDeleteId(null) });
        }}
      />
    </Panel>
  );
}
