/** TanStack Query-nøkler. Liste og detalj må aldri dele samme nøkkel (ID-kollisjon). */

export function asList<T>(data: T[] | T | undefined | null): T[] {
  return Array.isArray(data) ? data : [];
}

export const dcimKeys = {
  sites: () => ["dcim", "sites"] as const,
  site: (id: number) => ["dcim", "sites", id] as const,
  buildings: (siteId?: number) => ["dcim", "buildings", "list", siteId ?? "all"] as const,
  building: (id: number) => ["dcim", "buildings", id] as const,
  wings: (buildingId?: number) => ["dcim", "wings", "list", buildingId ?? "all"] as const,
  wing: (id: number) => ["dcim", "wings", id] as const,
  floors: (filters?: { buildingId?: number; wingId?: number }) =>
    ["dcim", "floors", "list", filters?.buildingId ?? "all", filters?.wingId ?? "all"] as const,
  floor: (id: number) => ["dcim", "floors", id] as const,
  rooms: (siteId?: number) => ["dcim", "rooms", "list", siteId ?? "all"] as const,
  roomsByBuilding: (buildingId: number) => ["dcim", "rooms", "list", "building", buildingId] as const,
  roomsByWing: (wingId: number) => ["dcim", "rooms", "list", "wing", wingId] as const,
  roomsByFloor: (floorId: number) => ["dcim", "rooms", "list", "floor", floorId] as const,
  room: (id: number) => ["dcim", "rooms", id] as const,
};
