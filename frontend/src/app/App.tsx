import { Route, Routes } from "react-router-dom";
import { AppShell } from "@/components/layout/AppShell";
import { usePluginRouteElements } from "@/plugins/PluginRoutes";
import { DashboardPage } from "@/pages/DashboardPage";
import { PlaceholderPage } from "@/pages/PlaceholderPage";

export function App() {
  const pluginRoutes = usePluginRouteElements();

  return (
    <AppShell>
      <Routes>
        <Route path="/" element={<DashboardPage />} />
        <Route
          path="/dcim"
          element={
            <PlaceholderPage
              title="DCIM"
              description="Sites, rom, rekker, racks og utstyr – kommer i fase 2."
            />
          }
        />
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
