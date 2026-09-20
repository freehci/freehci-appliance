import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { Panel } from "@/components/ui/Panel";
import { useI18n } from "@/i18n/I18nProvider";
import * as api from "./dcimApi";
import { asList, dcimKeys } from "./dcimQuery";
import styles from "./dcim.module.css";

export function DcimOverviewPage() {
  const { t } = useI18n();
  const sitesQ = useQuery({ queryKey: dcimKeys.sites(), queryFn: api.listSites });
  const buildingsQ = useQuery({ queryKey: dcimKeys.buildings(), queryFn: () => api.listBuildings() });
  const floorsQ = useQuery({ queryKey: dcimKeys.floors(), queryFn: () => api.listFloors() });
  const roomsQ = useQuery({ queryKey: dcimKeys.rooms(), queryFn: () => api.listRooms() });
  const racksQ = useQuery({ queryKey: ["dcim", "racks"], queryFn: () => api.listRacks() });
  const devicesQ = useQuery({ queryKey: ["dcim", "devices"], queryFn: api.listDevices });

  const counts = [
    { to: "/dcim/locations", label: t("dcim.overview.sites"), value: asList(sitesQ.data).length },
    { to: "/dcim/locations", label: t("dcim.overview.buildings"), value: asList(buildingsQ.data).length },
    { to: "/dcim/locations", label: t("dcim.overview.floors"), value: asList(floorsQ.data).length },
    { to: "/dcim/locations", label: t("dcim.overview.rooms"), value: asList(roomsQ.data).length },
    { to: "/dcim/racks", label: t("dcim.overview.racks"), value: asList(racksQ.data).length },
    { to: "/dcim/equipment", label: t("dcim.overview.devices"), value: asList(devicesQ.data).length },
  ];

  return (
    <Panel title={t("dcim.overview.title")}>
      <p className={styles.muted} style={{ marginTop: 0 }}>
        {t("dcim.overview.p1")} <code>/api/v1/dcim</code>.
      </p>
      <p style={{ fontSize: "var(--text-sm)" }}>{t("dcim.overview.p2")}</p>
      <table className={styles.table}>
        <tbody>
          {counts.map((row) => (
            <tr key={row.label}>
              <th>
                <Link to={row.to} className={styles.tableLink}>
                  {row.label}
                </Link>
              </th>
              <td>{row.value}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </Panel>
  );
}
