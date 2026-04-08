import { Route, Routes } from "react-router-dom";
import { AppShell } from "@/components/layout/AppShell";
import { DcimEquipmentPage } from "@/features/dcim/DcimEquipmentPage";
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
        </Route>
        <Route
          path="/ipam"
          element={
            <PlaceholderPage
              title="IPAM"
              description="VRF, VLAN, prefiks og tildelinger – redesignes i fase 3."
            />
          }
        />
        <Route
          path="/jobs"
          element={
            <PlaceholderPage
              title="Jobs"
              description="Celery-arbeidere, discovery og synk – fase 4."
            />
          }
        />
        <Route
          path="/integrations"
          element={
            <PlaceholderPage
              title="Integrasjoner"
              description="Provider-rammeverk og katalog – fase 5."
            />
          }
        />
        <Route
          path="/service-catalog"
          element={
            <PlaceholderPage
              title="Servicekatalog"
              description="Maler for deployment og tjenester – fase 6."
            />
          }
        />
        {pluginRoutes}
      </Routes>
    </AppShell>
  );
}
