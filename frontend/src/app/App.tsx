import { Route, Routes } from "react-router-dom";
import { AppShell } from "@/components/layout/AppShell";
import { DcimDeviceDetailPage } from "@/features/dcim/DcimDeviceDetailPage";
import { DcimEquipmentPage } from "@/features/dcim/DcimEquipmentPage";
import { DcimManufacturerDetailPage } from "@/features/dcim/DcimManufacturerDetailPage";
import { DcimLayout } from "@/features/dcim/DcimLayout";
import { DcimOverviewPage } from "@/features/dcim/DcimOverviewPage";
import { DcimRacksPage } from "@/features/dcim/DcimRacksPage";
import { DcimRoomsPage } from "@/features/dcim/DcimRoomsPage";
import { DcimSitesPage } from "@/features/dcim/DcimSitesPage";
import { usePluginRouteElements } from "@/plugins/PluginRoutes";
import { DashboardPage } from "@/pages/DashboardPage";
import { PlaceholderPage } from "@/pages/PlaceholderPage";

export function App() {
  const pluginRoutes = usePluginRouteElements();

  return (
    <AppShell>
      <Routes>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/dcim" element={<DcimLayout />}>
          <Route index element={<DcimOverviewPage />} />
          <Route path="sites" element={<DcimSitesPage />} />
          <Route path="rooms" element={<DcimRoomsPage />} />
          <Route path="racks" element={<DcimRacksPage />} />
          <Route path="equipment" element={<DcimEquipmentPage />} />
          <Route path="equipment/devices/:deviceId" element={<DcimDeviceDetailPage />} />
          <Route path="equipment/manufacturers/:manufacturerId" element={<DcimManufacturerDetailPage />} />
        </Route>
        <Route
          path="/ipam"
          element={
            <PlaceholderPage
              titleKey="placeholders.ipam.title"
              descriptionKey="placeholders.ipam.desc"
            />
          }
        />
        <Route
          path="/jobs"
          element={
            <PlaceholderPage titleKey="placeholders.jobs.title" descriptionKey="placeholders.jobs.desc" />
          }
        />
        <Route
          path="/integrations"
          element={
            <PlaceholderPage
              titleKey="placeholders.integrations.title"
              descriptionKey="placeholders.integrations.desc"
            />
          }
        />
        <Route
          path="/service-catalog"
          element={
            <PlaceholderPage
              titleKey="placeholders.serviceCatalog.title"
              descriptionKey="placeholders.serviceCatalog.desc"
            />
          }
        />
        {pluginRoutes}
      </Routes>
    </AppShell>
  );
}
