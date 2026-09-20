import { occupiedUnitsForRack } from "@/features/dcim/rackUtils";
import type { DeviceInstance, DeviceModel, Rack, RackPlacement, Room, Site } from "@/features/dcim/types";
import type { Ipv4Prefix } from "@/features/ipam/types";
import { prefixUsage } from "@/features/ipam/prefixPageUi";

export type SiteCardRow = {
  site: Site;
  rooms: number;
  racks: number;
};

export type RackUtilRow = {
  rack: Rack;
  siteName: string;
  roomName: string;
  used: number;
  total: number;
  pct: number;
};

export function buildSiteCards(sites: Site[], rooms: Room[], racks: Rack[]): SiteCardRow[] {
  const roomsBySite = new Map<number, Room[]>();
  for (const room of rooms) {
    const arr = roomsBySite.get(room.site_id) ?? [];
    arr.push(room);
    roomsBySite.set(room.site_id, arr);
  }
  const racksByRoom = new Map<number, number>();
  for (const rack of racks) {
    racksByRoom.set(rack.room_id, (racksByRoom.get(rack.room_id) ?? 0) + 1);
  }
  return [...sites]
    .sort((a, b) => a.name.localeCompare(b.name))
    .map((site) => {
      const siteRooms = roomsBySite.get(site.id) ?? [];
      const rackCount = siteRooms.reduce((sum, room) => sum + (racksByRoom.get(room.id) ?? 0), 0);
      return { site, rooms: siteRooms.length, racks: rackCount };
    });
}

export function buildRackUtils(
  racks: Rack[],
  rooms: Room[],
  sites: Site[],
  placements: RackPlacement[],
  devicesById: Map<number, DeviceInstance>,
  modelsById: Map<number, DeviceModel>,
): RackUtilRow[] {
  const roomById = new Map(rooms.map((r) => [r.id, r]));
  const siteById = new Map(sites.map((s) => [s.id, s]));
  return racks
    .map((rack) => {
      const used = occupiedUnitsForRack(placements, rack.id, devicesById, modelsById).size;
      const total = rack.u_height;
      const room = roomById.get(rack.room_id);
      const site = room ? siteById.get(room.site_id) : undefined;
      return {
        rack,
        siteName: site?.name ?? "",
        roomName: room?.name ?? "",
        used,
        total,
        pct: total > 0 ? (100 * used) / total : 0,
      };
    })
    .sort((a, b) => b.pct - a.pct || a.rack.name.localeCompare(b.rack.name));
}

export function topPrefixesByUsage(prefixes: Ipv4Prefix[], limit = 5): Ipv4Prefix[] {
  return [...prefixes]
    .sort((a, b) => prefixUsage(b).pct - prefixUsage(a).pct || a.cidr.localeCompare(b.cidr))
    .slice(0, limit);
}

export function ipv4Inventory(prefixes: Ipv4Prefix[]): { used: number; total: number; pct: number } {
  let used = 0;
  let total = 0;
  for (const p of prefixes) {
    const u = prefixUsage(p);
    used += u.used;
    total += u.total;
  }
  return { used, total, pct: total > 0 ? (100 * used) / total : 0 };
}

export function siteInitials(name: string): string {
  const parts = name.trim().split(/\s+/).filter(Boolean);
  if (parts.length === 0) return "?";
  if (parts.length === 1) return parts[0]!.slice(0, 2).toUpperCase();
  return `${parts[0]![0] ?? ""}${parts[1]![0] ?? ""}`.toUpperCase();
}
