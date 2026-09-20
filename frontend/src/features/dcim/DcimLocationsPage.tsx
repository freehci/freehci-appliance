import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { Panel } from "@/components/ui/Panel";
import { useI18n } from "@/i18n/I18nProvider";
import type { MessageKey } from "@/i18n/messages/en";
import { ApiError } from "@/lib/api";
import * as api from "./dcimApi";
import { DcimRoomLocationFields, optionalId, type RoomLocationValue } from "./DcimRoomLocationFields";
import { asList, dcimKeys } from "./dcimQuery";
import styles from "./dcim.module.css";
import locStyles from "./locations.module.css";
import { buildLocationTree, filterLocationTree, flattenLocationTree, type LocationKind, type LocationTreeNode } from "./locationTree";

const KIND_KEY: Record<LocationKind, MessageKey> = {
  site: "dcim.locations.kind.site",
  building: "dcim.locations.kind.building",
  wing: "dcim.locations.kind.wing",
  floor: "dcim.locations.kind.floor",
  room: "dcim.locations.kind.room",
};

function TreeBranch({
  nodes,
  t,
}: {
  nodes: LocationTreeNode[];
  t: (key: MessageKey, vars?: Record<string, string>) => string;
}) {
  return (
    <ul className={locStyles.tree}>
      {nodes.map((node) => (
        <li key={node.key} className={locStyles.treeItem}>
          <div className={locStyles.treeRow}>
            <span className={`${locStyles.kind} ${locStyles[`kind_${node.kind}`]}`}>{t(KIND_KEY[node.kind])}</span>
            <Link to={node.href} className={styles.tableLink}>
              {node.name}
            </Link>
            {node.kind === "floor" && node.extra != null ? (
              <span className={locStyles.meta}>{t("dcim.locations.level", { level: node.extra })}</span>
            ) : null}
            {node.kind === "site" && node.extra != null ? <span className={locStyles.meta}>{node.extra}</span> : null}
          </div>
          {node.children.length > 0 ? <TreeBranch nodes={node.children} t={t} /> : null}
        </li>
      ))}
    </ul>
  );
}

export function DcimLocationsPage() {
  const { t } = useI18n();
  const qc = useQueryClient();
  const [view, setView] = useState<"tree" | "list">("tree");
  const [search, setSearch] = useState("");
  const [err, setErr] = useState<string | null>(null);
  const [siteName, setSiteName] = useState("");
  const [siteSlug, setSiteSlug] = useState("");
  const [newTenantId, setNewTenantId] = useState("");
  const [roomName, setRoomName] = useState("");
  const [loc, setLoc] = useState<RoomLocationValue>({
    siteId: "",
    buildingId: "",
    wingId: "",
    floorId: "",
  });

  const sitesQ = useQuery({ queryKey: dcimKeys.sites(), queryFn: api.listSites });
  const buildingsQ = useQuery({ queryKey: dcimKeys.buildings(), queryFn: () => api.listBuildings() });
  const wingsQ = useQuery({ queryKey: dcimKeys.wings(), queryFn: () => api.listWings() });
  const floorsQ = useQuery({ queryKey: dcimKeys.floors(), queryFn: () => api.listFloors() });
  const roomsQ = useQuery({ queryKey: dcimKeys.rooms(), queryFn: () => api.listRooms() });
  const tenantsQ = useQuery({ queryKey: ["tenants"], queryFn: api.listTenants });

  const sites = asList(sitesQ.data);
  const buildings = asList(buildingsQ.data);
  const wings = asList(wingsQ.data);
  const floors = asList(floorsQ.data);
  const rooms = asList(roomsQ.data);

  const tree = useMemo(
    () => filterLocationTree(buildLocationTree(sites, buildings, wings, floors, rooms), search),
    [sites, buildings, wings, floors, rooms, search],
  );
  const flat = useMemo(() => flattenLocationTree(tree), [tree]);

  const createSite = useMutation({
    mutationFn: () =>
      api.createSite({
        name: siteName.trim(),
        slug: siteSlug.trim().toLowerCase(),
        tenant_id: newTenantId === "" ? undefined : Number(newTenantId),
      }),
    onSuccess: () => {
      setErr(null);
      setSiteName("");
      setSiteSlug("");
      setNewTenantId("");
      void qc.invalidateQueries({ queryKey: ["dcim", "sites"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const createRoom = useMutation({
    mutationFn: () =>
      api.createRoom({
        site_id: Number(loc.siteId),
        name: roomName.trim(),
        building_id: optionalId(loc.buildingId),
        wing_id: optionalId(loc.wingId),
        floor_id: optionalId(loc.floorId),
      }),
    onSuccess: () => {
      setErr(null);
      setRoomName("");
      void qc.invalidateQueries({ queryKey: ["dcim", "rooms"] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const loading = sitesQ.isLoading || buildingsQ.isLoading || wingsQ.isLoading || floorsQ.isLoading || roomsQ.isLoading;
  const loadError =
    (sitesQ.error as Error | undefined) ??
    (buildingsQ.error as Error | undefined) ??
    (wingsQ.error as Error | undefined) ??
    (floorsQ.error as Error | undefined) ??
    (roomsQ.error as Error | undefined);

  return (
    <Panel title={t("nav.locations")}>
      <p className={styles.muted} style={{ marginTop: 0 }}>
        {t("dcim.locations.intro")}
      </p>
      {err ? <p className={styles.err}>{err}</p> : null}
      {loadError ? (
        <p className={styles.err}>
          {t("dcim.locations.loadError")} {loadError.message}
        </p>
      ) : null}

      <div className={locStyles.toolbar}>
        <label className={locStyles.search}>
          {t("dcim.locations.search")}
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder={t("dcim.locations.searchPh")}
          />
        </label>
        <div className={locStyles.viewToggle} role="group" aria-label={t("dcim.locations.viewAria")}>
          <button
            type="button"
            className={`${styles.btn} ${view === "tree" ? locStyles.viewActive : styles.btnMuted}`}
            aria-pressed={view === "tree"}
            onClick={() => setView("tree")}
          >
            {t("dcim.locations.tree")}
          </button>
          <button
            type="button"
            className={`${styles.btn} ${view === "list" ? locStyles.viewActive : styles.btnMuted}`}
            aria-pressed={view === "list"}
            onClick={() => setView("list")}
          >
            {t("dcim.locations.list")}
          </button>
        </div>
      </div>

      {loading ? <p className={styles.muted}>{t("dcim.common.loading")}</p> : null}
      {!loading && tree.length === 0 ? (
        <p className={styles.muted}>{search.trim() ? t("dcim.locations.emptySearch") : t("dcim.locations.empty")}</p>
      ) : null}

      {!loading && tree.length > 0 && view === "tree" ? <TreeBranch nodes={tree} t={t} /> : null}

      {!loading && tree.length > 0 && view === "list" ? (
        <table className={styles.table}>
          <thead>
            <tr>
              <th>{t("dcim.locations.kindCol")}</th>
              <th>{t("dcim.common.name")}</th>
              <th>{t("dcim.locations.path")}</th>
            </tr>
          </thead>
          <tbody>
            {flat.map(({ node, path }) => (
              <tr key={node.key}>
                <td>
                  <span className={`${locStyles.kind} ${locStyles[`kind_${node.kind}`]}`}>{t(KIND_KEY[node.kind])}</span>
                </td>
                <td>
                  <Link to={node.href} className={styles.tableLink}>
                    {node.name}
                  </Link>
                </td>
                <td className={locStyles.path}>{path.join(" / ")}</td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : null}

      <section className={styles.mfrDetailSection}>
        <h3 className={styles.mfrDetailSectionTitle}>{t("dcim.locations.createSite")}</h3>
        <form
          className={styles.formRow}
          onSubmit={(e) => {
            e.preventDefault();
            setErr(null);
            createSite.mutate();
          }}
        >
          <label>
            {t("dcim.common.name")}
            <input value={siteName} onChange={(e) => setSiteName(e.target.value)} required />
          </label>
          <label>
            {t("dcim.common.slug")}
            <input
              value={siteSlug}
              onChange={(e) => setSiteSlug(e.target.value)}
              placeholder={t("dcim.sites.slugPh")}
              required
              pattern="[a-z0-9]+(?:-[a-z0-9]+)*"
              title={t("dcim.sites.slugPatternTitle")}
            />
          </label>
          <label>
            {t("dcim.sites.tenant")}
            <select value={newTenantId} onChange={(e) => setNewTenantId(e.target.value)}>
              <option value="">{t("dcim.sites.tenantDefault")}</option>
              {(tenantsQ.data ?? []).map((tn) => (
                <option key={tn.id} value={String(tn.id)}>
                  {tn.name}
                </option>
              ))}
            </select>
          </label>
          <button type="submit" className={styles.btn} disabled={createSite.isPending}>
            {createSite.isPending ? t("dcim.common.creating") : t("dcim.common.create")}
          </button>
        </form>
      </section>

      <section className={styles.mfrDetailSection}>
        <h3 className={styles.mfrDetailSectionTitle}>{t("dcim.locations.createRoom")}</h3>
        <form
          className={styles.formRow}
          onSubmit={(e) => {
            e.preventDefault();
            setErr(null);
            if (!loc.siteId) {
              setErr(t("dcim.rooms.chooseSite"));
              return;
            }
            createRoom.mutate();
          }}
        >
          <DcimRoomLocationFields value={loc} onChange={setLoc} />
          <label>
            {t("dcim.rooms.roomName")}
            <input value={roomName} onChange={(e) => setRoomName(e.target.value)} required />
          </label>
          <button type="submit" className={styles.btn} disabled={createRoom.isPending || sitesQ.isLoading}>
            {createRoom.isPending ? t("dcim.common.creating") : t("dcim.rooms.create")}
          </button>
        </form>
      </section>
    </Panel>
  );
}
