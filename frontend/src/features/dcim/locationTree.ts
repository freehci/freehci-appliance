import type { Building, Floor, Room, Site, Wing } from "./types";

export type LocationKind = "site" | "building" | "wing" | "floor" | "room";

export type LocationTreeNode = {
  key: string;
  kind: LocationKind;
  id: number;
  name: string;
  href: string;
  extra?: string;
  children: LocationTreeNode[];
};

export type LocationFlatRow = {
  node: LocationTreeNode;
  path: string[];
};

export function siteHref(siteId: number): string {
  return `/dcim/sites/${siteId}`;
}

export function buildingHref(siteId: number, buildingId: number): string {
  return `/dcim/sites/${siteId}/buildings/${buildingId}`;
}

export function wingHref(siteId: number, buildingId: number, wingId: number): string {
  return `/dcim/sites/${siteId}/buildings/${buildingId}/wings/${wingId}`;
}

export function floorHref(siteId: number, buildingId: number, floorId: number): string {
  return `/dcim/sites/${siteId}/buildings/${buildingId}/floors/${floorId}`;
}

export function roomHref(roomId: number): string {
  return `/dcim/rooms/${roomId}`;
}

function groupBy<T>(items: T[], key: (item: T) => number | null | undefined): Map<number, T[]> {
  const m = new Map<number, T[]>();
  for (const item of items) {
    const id = key(item);
    if (id == null) continue;
    const rows = m.get(id) ?? [];
    rows.push(item);
    m.set(id, rows);
  }
  return m;
}

function sortByName<T extends { name: string; id: number }>(rows: T[]): T[] {
  return [...rows].sort((a, b) => a.name.localeCompare(b.name) || a.id - b.id);
}

function roomNode(room: Room): LocationTreeNode {
  return {
    key: `room-${room.id}`,
    kind: "room",
    id: room.id,
    name: room.name,
    href: roomHref(room.id),
    children: [],
  };
}

function floorNode(floor: Floor, siteId: number, rooms: Room[]): LocationTreeNode {
  return {
    key: `floor-${floor.id}`,
    kind: "floor",
    id: floor.id,
    name: floor.name,
    href: floorHref(siteId, floor.building_id, floor.id),
    extra: String(floor.level),
    children: sortByName(rooms).map(roomNode),
  };
}

export function buildLocationTree(
  sites: Site[],
  buildings: Building[],
  wings: Wing[],
  floors: Floor[],
  rooms: Room[],
): LocationTreeNode[] {
  const buildingsBySite = groupBy(buildings, (b) => b.site_id);
  const wingsByBuilding = groupBy(wings, (w) => w.building_id);
  const floorsByWing = groupBy(
    floors.filter((f) => f.wing_id != null),
    (f) => f.wing_id,
  );
  const floorsByBuildingBare = groupBy(
    floors.filter((f) => f.wing_id == null),
    (f) => f.building_id,
  );
  const roomsByFloor = groupBy(
    rooms.filter((r) => r.floor_id != null),
    (r) => r.floor_id,
  );
  const roomsByWingBare = groupBy(
    rooms.filter((r) => r.floor_id == null && r.wing_id != null),
    (r) => r.wing_id,
  );
  const roomsByBuildingBare = groupBy(
    rooms.filter((r) => r.floor_id == null && r.wing_id == null && r.building_id != null),
    (r) => r.building_id,
  );
  const roomsBySiteBare = groupBy(
    rooms.filter((r) => r.floor_id == null && r.wing_id == null && r.building_id == null),
    (r) => r.site_id,
  );

  return sortByName(sites).map((site) => {
    const siteBuildings = sortByName(buildingsBySite.get(site.id) ?? []);
    const buildingNodes = siteBuildings.map((building) => {
      const buildingWings = sortByName(wingsByBuilding.get(building.id) ?? []);
      const wingNodes = buildingWings.map((wing) => {
        const wingFloors = sortByName(floorsByWing.get(wing.id) ?? []);
        return {
          key: `wing-${wing.id}`,
          kind: "wing" as const,
          id: wing.id,
          name: wing.name,
          href: wingHref(site.id, building.id, wing.id),
          children: [
            ...wingFloors.map((floor) => floorNode(floor, site.id, roomsByFloor.get(floor.id) ?? [])),
            ...sortByName(roomsByWingBare.get(wing.id) ?? []).map(roomNode),
          ],
        };
      });
      const bareFloors = sortByName(floorsByBuildingBare.get(building.id) ?? []);
      return {
        key: `building-${building.id}`,
        kind: "building" as const,
        id: building.id,
        name: building.name,
        href: buildingHref(site.id, building.id),
        children: [
          ...wingNodes,
          ...bareFloors.map((floor) => floorNode(floor, site.id, roomsByFloor.get(floor.id) ?? [])),
          ...sortByName(roomsByBuildingBare.get(building.id) ?? []).map(roomNode),
        ],
      };
    });
    return {
      key: `site-${site.id}`,
      kind: "site" as const,
      id: site.id,
      name: site.name,
      href: siteHref(site.id),
      extra: site.slug,
      children: [...buildingNodes, ...sortByName(roomsBySiteBare.get(site.id) ?? []).map(roomNode)],
    };
  });
}

export function filterLocationTree(nodes: LocationTreeNode[], query: string): LocationTreeNode[] {
  const q = query.trim().toLowerCase();
  if (q === "") return nodes;

  const walk = (node: LocationTreeNode): LocationTreeNode | null => {
    const selfMatch =
      node.name.toLowerCase().includes(q) ||
      (node.extra != null && node.extra.toLowerCase().includes(q)) ||
      node.kind.includes(q);
    const children = node.children.map(walk).filter((c): c is LocationTreeNode => c != null);
    if (selfMatch || children.length > 0) {
      return { ...node, children: selfMatch && children.length === 0 ? node.children : children };
    }
    return null;
  };

  return nodes.map(walk).filter((n): n is LocationTreeNode => n != null);
}

export function flattenLocationTree(nodes: LocationTreeNode[], ancestors: string[] = []): LocationFlatRow[] {
  const rows: LocationFlatRow[] = [];
  for (const node of nodes) {
    const path = [...ancestors, node.name];
    rows.push({ node, path });
    rows.push(...flattenLocationTree(node.children, path));
  }
  return rows;
}
