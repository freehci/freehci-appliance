import { useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { useI18n } from "@/i18n/I18nProvider";
import * as api from "./dcimApi";
import { asList, dcimKeys } from "./dcimQuery";

export type RoomLocationValue = {
  siteId: string;
  buildingId: string;
  wingId: string;
  floorId: string;
};

type Props = {
  value: RoomLocationValue;
  onChange: (next: RoomLocationValue) => void;
  requireSite?: boolean;
};

export function DcimRoomLocationFields({ value, onChange, requireSite = true }: Props) {
  const { t } = useI18n();
  const sitesQ = useQuery({ queryKey: ["dcim", "sites"], queryFn: api.listSites });
  const siteNum = Number(value.siteId);
  const buildingNum = Number(value.buildingId);
  const buildingsQ = useQuery({
    queryKey: dcimKeys.buildings(Number.isFinite(siteNum) && siteNum > 0 ? siteNum : undefined),
    queryFn: () => api.listBuildings(siteNum),
    enabled: Number.isFinite(siteNum) && siteNum > 0,
  });
  const wingsQ = useQuery({
    queryKey: dcimKeys.wings(Number.isFinite(buildingNum) && buildingNum > 0 ? buildingNum : undefined),
    queryFn: () => api.listWings(buildingNum),
    enabled: Number.isFinite(buildingNum) && buildingNum > 0,
  });
  const floorsQ = useQuery({
    queryKey: dcimKeys.floors(
      Number.isFinite(buildingNum) && buildingNum > 0 ? { buildingId: buildingNum } : undefined,
    ),
    queryFn: () => api.listFloors({ buildingId: buildingNum }),
    enabled: Number.isFinite(buildingNum) && buildingNum > 0,
  });

  const floors = useMemo(() => {
    const all = asList(floorsQ.data);
    if (value.wingId === "") return all;
    const wid = Number(value.wingId);
    return all.filter((f) => f.wing_id === wid);
  }, [floorsQ.data, value.wingId]);

  return (
    <>
      <label>
        {t("dcim.common.site")}
        <select
          value={value.siteId}
          required={requireSite}
          onChange={(e) =>
            onChange({ siteId: e.target.value, buildingId: "", wingId: "", floorId: "" })
          }
        >
          <option value="">{t("dcim.common.choose")}</option>
          {(sitesQ.data ?? []).map((s) => (
            <option key={s.id} value={String(s.id)}>
              {s.name} ({s.slug})
            </option>
          ))}
        </select>
      </label>
      <label>
        {t("dcim.common.building")}
        <select
          value={value.buildingId}
          disabled={!value.siteId}
          onChange={(e) =>
            onChange({ ...value, buildingId: e.target.value, wingId: "", floorId: "" })
          }
        >
          <option value="">{t("dcim.common.skip")}</option>
          {asList(buildingsQ.data).map((b) => (
            <option key={b.id} value={String(b.id)}>
              {b.name}
            </option>
          ))}
        </select>
      </label>
      <label>
        {t("dcim.common.wing")}
        <select
          value={value.wingId}
          disabled={!value.buildingId}
          onChange={(e) => onChange({ ...value, wingId: e.target.value, floorId: "" })}
        >
          <option value="">{t("dcim.common.skip")}</option>
          {asList(wingsQ.data).map((w) => (
            <option key={w.id} value={String(w.id)}>
              {w.name}
            </option>
          ))}
        </select>
      </label>
      <label>
        {t("dcim.common.floor")}
        <select
          value={value.floorId}
          disabled={!value.buildingId}
          onChange={(e) => onChange({ ...value, floorId: e.target.value })}
        >
          <option value="">{t("dcim.common.skip")}</option>
          {floors.map((f) => (
            <option key={f.id} value={String(f.id)}>
              {f.name}
            </option>
          ))}
        </select>
      </label>
    </>
  );
}

export function optionalId(raw: string): number | null {
  const n = Number(raw);
  return Number.isFinite(n) && n > 0 ? n : null;
}
