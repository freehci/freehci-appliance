import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useMemo, useRef, useState } from "react";
import "leaflet/dist/leaflet.css";
import L from "leaflet";
import { MapContainer, Marker, Popup, TileLayer, useMap } from "react-leaflet";
import { Link, useParams } from "react-router-dom";
import { ConfirmModal } from "@/components/ui/ConfirmModal";
import { Panel } from "@/components/ui/Panel";
import { useI18n } from "@/i18n/I18nProvider";
import { ApiError } from "@/lib/api";
import * as ipamApi from "@/features/ipam/ipamApi";
import * as api from "./dcimApi";
import styles from "./dcim.module.css";

import marker2x from "leaflet/dist/images/marker-icon-2x.png";
import marker1x from "leaflet/dist/images/marker-icon.png";
import markerShadow from "leaflet/dist/images/marker-shadow.png";

function SiteMapRecenter({ lat, lon }: { lat: number; lon: number }) {
  const map = useMap();
  useEffect(() => {
    map.setView([lat, lon], map.getZoom());
  }, [lat, lon, map]);
  return null;
}

export function DcimSiteDetailPage() {
  const { t } = useI18n();
  const qc = useQueryClient();
  const { siteId: siteParam } = useParams<{ siteId: string }>();
  const siteId = Number(siteParam);
  const ok = Number.isFinite(siteId) && siteId > 0;
  const [err, setErr] = useState<string | null>(null);
  const [edit, setEdit] = useState<Record<string, string>>({});
  const [geocodeResult, setGeocodeResult] = useState<api.SiteGeocodeResponse | null>(null);
  const [grantUserId, setGrantUserId] = useState("");
  const [grantRoleId, setGrantRoleId] = useState("");
  const [grantIsContact, setGrantIsContact] = useState(true);
  const [grantNotes, setGrantNotes] = useState("");
  const [newPerson, setNewPerson] = useState(false);
  const [newUsername, setNewUsername] = useState("");
  const [newDisplayName, setNewDisplayName] = useState("");
  const [newEmail, setNewEmail] = useState("");
  const [newPhone, setNewPhone] = useState("");
  const [grantDeleteId, setGrantDeleteId] = useState<number | null>(null);
  const [bannerVersion, setBannerVersion] = useState("");
  const bannerFileRef = useRef<HTMLInputElement | null>(null);
  const [buildingName, setBuildingName] = useState("");
  const [buildingSlug, setBuildingSlug] = useState("");
  const hydrated = useRef(false);

  const siteQ = useQuery({
    queryKey: ["dcim", "sites", siteId],
    queryFn: () => api.getSite(siteId),
    enabled: ok,
  });
  const tenantsQ = useQuery({ queryKey: ["tenants"], queryFn: api.listTenants });
  const rolesQ = useQuery({ queryKey: ["dcim", "site-roles"], queryFn: api.listSiteRoles });
  const usersQ = useQuery({ queryKey: ["ipam", "users"], queryFn: () => ipamApi.listUsers(500) });
  const grantsQ = useQuery({
    queryKey: ["dcim", "site-access", siteId],
    queryFn: () => api.listSiteAccess(siteId),
    enabled: ok,
  });
  const buildingsQ = useQuery({
    queryKey: ["dcim", "buildings", siteId],
    queryFn: () => api.listBuildings(siteId),
    enabled: ok,
  });
  const roomsQ = useQuery({
    queryKey: ["dcim", "rooms", siteId],
    queryFn: () => api.listRooms(siteId),
    enabled: ok,
  });

  const site = siteQ.data;
  useEffect(() => {
    hydrated.current = false;
  }, [siteId]);
  useEffect(() => {
    if (!site || hydrated.current) return;
    setEdit({
      tenant_id: String(site.tenant_id),
      name: site.name ?? "",
      description: site.description ?? "",
      address_line1: site.address_line1 ?? "",
      address_line2: site.address_line2 ?? "",
      postal_code: site.postal_code ?? "",
      city: site.city ?? "",
      county: site.county ?? "",
      country: site.country ?? "",
      latitude: site.latitude != null ? String(site.latitude) : "",
      longitude: site.longitude != null ? String(site.longitude) : "",
      address_note: site.address_note ?? "",
    });
    setBannerVersion(site.has_banner ? String(Date.now()) : "");
    hydrated.current = true;
  }, [site]);

  const roomsWithoutBuilding = useMemo(
    () => (roomsQ.data ?? []).filter((r) => r.building_id == null),
    [roomsQ.data],
  );
  const latLon = useMemo(() => {
    const lat = edit.latitude?.trim() ? Number(edit.latitude) : null;
    const lon = edit.longitude?.trim() ? Number(edit.longitude) : null;
    if (lat == null || lon == null) return null;
    if (!Number.isFinite(lat) || !Number.isFinite(lon)) return null;
    return { lat, lon };
  }, [edit.latitude, edit.longitude]);

  const um = useMutation({
    mutationFn: () =>
      api.updateSite(siteId, {
        tenant_id: edit.tenant_id?.trim() ? Number(edit.tenant_id) : undefined,
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
    mutationFn: () => api.geocodeSite(siteId, { query: null, limit: 5 }),
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
      return api.createSiteAccess(siteId, {
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
      void qc.invalidateQueries({ queryKey: ["dcim", "site-access", siteId] });
      void qc.invalidateQueries({ queryKey: ["ipam", "users"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const uploadBannerM = useMutation({
    mutationFn: (file: File) => api.uploadSiteBanner(siteId, file),
    onSuccess: () => {
      setErr(null);
      setBannerVersion(String(Date.now()));
      if (bannerFileRef.current) bannerFileRef.current.value = "";
      void qc.invalidateQueries({ queryKey: ["dcim", "sites"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const removeBannerM = useMutation({
    mutationFn: () => api.deleteSiteBanner(siteId),
    onSuccess: () => {
      setErr(null);
      setBannerVersion("");
      void qc.invalidateQueries({ queryKey: ["dcim", "sites"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const delGrantM = useMutation({
    mutationFn: (grantId: number) => api.deleteSiteAccess(siteId, grantId),
    onSuccess: () => void qc.invalidateQueries({ queryKey: ["dcim", "site-access", siteId] }),
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const createBuilding = useMutation({
    mutationFn: () =>
      api.createBuilding({
        site_id: siteId,
        name: buildingName.trim(),
        slug: buildingSlug.trim().toLowerCase(),
      }),
    onSuccess: () => {
      setErr(null);
      setBuildingName("");
      setBuildingSlug("");
      void qc.invalidateQueries({ queryKey: ["dcim", "buildings"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  if (!ok) {
    return (
      <Panel title={t("nav.dcimSites")}>
        <p className={styles.err}>{t("dcim.sites.invalidId")}</p>
      </Panel>
    );
  }
  if (siteQ.isError) {
    return (
      <Panel title={t("nav.dcimSites")}>
        <p className={styles.err}>{(siteQ.error as Error).message}</p>
        <Link to="/dcim/sites" className={styles.tableLink}>
          {t("dcim.sites.backToList")}
        </Link>
      </Panel>
    );
  }
  if (siteQ.isLoading || !site) {
    return (
      <Panel title={t("nav.dcimSites")}>
        <p className={styles.muted}>{t("dcim.common.loading")}</p>
      </Panel>
    );
  }

  return (
    <>
      <p className={styles.mfrDetailBack}>
        <Link to="/dcim/sites" className={styles.tableLink}>
          ← {t("dcim.sites.backToList")}
        </Link>
      </p>
      <Panel title={site.name}>
        {err ? <p className={styles.err}>{err}</p> : null}

        <section className={styles.mfrDetailSection}>
          <h3 className={styles.mfrDetailSectionTitle}>{t("dcim.sites.editTitle")}</h3>
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
              {t("dcim.sites.tenant")}
              <select
                value={edit.tenant_id ?? ""}
                onChange={(e) => setEdit((x) => ({ ...x, tenant_id: e.target.value }))}
              >
                {(tenantsQ.data ?? []).map((tn) => (
                  <option key={tn.id} value={String(tn.id)}>
                    {tn.name}
                  </option>
                ))}
              </select>
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
              <input value={edit.county ?? ""} onChange={(e) => setEdit((x) => ({ ...x, county: e.target.value }))} />
            </label>
            <label>
              {t("dcim.sites.country")}
              <input value={edit.country ?? ""} onChange={(e) => setEdit((x) => ({ ...x, country: e.target.value }))} />
            </label>
            <label>
              {t("dcim.sites.latitude")}
              <input value={edit.latitude ?? ""} onChange={(e) => setEdit((x) => ({ ...x, latitude: e.target.value }))} />
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
            </div>
            {geocodeResult?.candidates?.length ? (
              <div style={{ flex: "1 1 100%", fontSize: "var(--text-xs)", color: "var(--color-text-muted)" }}>
                {t("dcim.sites.geocodeBestPrefix")} <span>{geocodeResult.candidates[0].display_name}</span>
              </div>
            ) : null}
          </form>
        </section>

        <section className={styles.mfrDetailSection}>
          <h3 className={styles.mfrDetailSectionTitle}>{t("dcim.sites.bannerTitle")}</h3>
          {site.has_banner ? (
            <p style={{ margin: "0 0 0.5rem" }}>
              <img
                src={api.siteBannerUrl(siteId, bannerVersion)}
                alt=""
                className={styles.mfrLogoThumb}
                style={{ maxWidth: "100%", width: "auto", height: "auto", maxHeight: "10rem" }}
              />
            </p>
          ) : (
            <p className={styles.muted}>{t("dcim.sites.bannerEmpty")}</p>
          )}
          <div className={styles.formRow}>
            <label>
              {t("dcim.sites.bannerUpload")}
              <input
                ref={bannerFileRef}
                type="file"
                accept="image/png,image/jpeg,image/webp"
                onChange={(e) => {
                  const f = e.target.files?.[0];
                  if (f) {
                    setErr(null);
                    uploadBannerM.mutate(f);
                  }
                }}
              />
            </label>
            {site.has_banner ? (
              <button
                type="button"
                className={styles.btnMuted}
                disabled={removeBannerM.isPending}
                onClick={() => {
                  setErr(null);
                  removeBannerM.mutate();
                }}
              >
                {removeBannerM.isPending ? "…" : t("dcim.sites.bannerRemove")}
              </button>
            ) : null}
          </div>
          <p className={styles.muted}>{t("dcim.sites.bannerHint")}</p>
        </section>

        {latLon ? (
          <section className={styles.mfrDetailSection}>
            <h3 className={styles.mfrDetailSectionTitle}>{t("dcim.sites.mapTitle")}</h3>
            <MapContainer
              center={[latLon.lat, latLon.lon]}
              zoom={15}
              style={{ height: 280, width: "100%", borderRadius: "var(--radius-sm)" }}
            >
              <SiteMapRecenter lat={latLon.lat} lon={latLon.lon} />
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
                    <div style={{ fontWeight: 600 }}>{site.name}</div>
                    <div>
                      {latLon.lat.toFixed(6)}, {latLon.lon.toFixed(6)}
                    </div>
                  </div>
                </Popup>
              </Marker>
            </MapContainer>
          </section>
        ) : null}

        <section className={styles.mfrDetailSection}>
          <h3 className={styles.mfrDetailSectionTitle}>{t("dcim.sites.buildingsTitle")}</h3>
          <p className={styles.muted}>{t("dcim.sites.noBuildingsHint")}</p>
          <form
            className={styles.formRow}
            onSubmit={(e) => {
              e.preventDefault();
              setErr(null);
              createBuilding.mutate();
            }}
          >
            <label>
              {t("dcim.common.name")}
              <input value={buildingName} onChange={(e) => setBuildingName(e.target.value)} required />
            </label>
            <label>
              {t("dcim.common.slug")}
              <input
                value={buildingSlug}
                onChange={(e) => setBuildingSlug(e.target.value)}
                placeholder={t("dcim.buildings.slugPh")}
                required
                pattern="[a-z0-9]+(?:-[a-z0-9]+)*"
                title={t("dcim.sites.slugPatternTitle")}
              />
            </label>
            <button type="submit" className={styles.btn} disabled={createBuilding.isPending}>
              {createBuilding.isPending ? t("dcim.common.creating") : t("dcim.buildings.create")}
            </button>
          </form>
          {buildingsQ.isError ? (
            <p className={styles.err}>
              {t("dcim.buildings.loadError")} {(buildingsQ.error as Error).message}
            </p>
          ) : null}
          {(buildingsQ.data ?? []).length === 0 ? <p className={styles.muted}>{t("dcim.buildings.empty")}</p> : null}
          {(buildingsQ.data ?? []).length > 0 ? (
            <table className={styles.table}>
              <thead>
                <tr>
                  <th>{t("dcim.common.name")}</th>
                  <th>{t("dcim.common.slug")}</th>
                </tr>
              </thead>
              <tbody>
                {(buildingsQ.data ?? []).map((b) => (
                  <tr key={b.id}>
                    <td>
                      <Link to={`/dcim/sites/${siteId}/buildings/${b.id}`} className={styles.tableLink}>
                        {b.name}
                      </Link>
                    </td>
                    <td>{b.slug}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : null}
        </section>

        <section className={styles.mfrDetailSection}>
          <h3 className={styles.mfrDetailSectionTitle}>{t("dcim.sites.roomsWithoutBuilding")}</h3>
          {roomsWithoutBuilding.length === 0 ? <p className={styles.muted}>{t("dcim.rooms.empty")}</p> : null}
          {roomsWithoutBuilding.length > 0 ? (
            <table className={styles.table}>
              <thead>
                <tr>
                  <th>{t("dcim.common.name")}</th>
                  <th>{t("dcim.rooms.floor")}</th>
                </tr>
              </thead>
              <tbody>
                {roomsWithoutBuilding.map((r) => (
                  <tr key={r.id}>
                    <td>
                      <Link to={`/dcim/rooms/${r.id}`} className={styles.tableLink}>
                        {r.name}
                      </Link>
                    </td>
                    <td>{r.floor ?? "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : null}
        </section>

        <section className={styles.mfrDetailSection}>
          <h3 className={styles.mfrDetailSectionTitle}>{t("dcim.sites.accessTitle")}</h3>
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
        </section>
      </Panel>
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
    </>
  );
}
