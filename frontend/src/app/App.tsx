import { Navigate, Outlet, Route, Routes } from "react-router-dom";
import { AppShell } from "@/components/layout/AppShell";
import { ChangePasswordPage } from "@/features/auth/ChangePasswordPage";
import { LoginPage } from "@/features/auth/LoginPage";
import { RequireAuth } from "@/features/auth/RequireAuth";
import { DcimDeviceDetailPage } from "@/features/dcim/DcimDeviceDetailPage";
import { DcimEquipmentPage } from "@/features/dcim/DcimEquipmentPage";
import { DcimManufacturerDetailPage } from "@/features/dcim/DcimManufacturerDetailPage";
import { DcimLayout } from "@/features/dcim/DcimLayout";
import { DcimOverviewPage } from "@/features/dcim/DcimOverviewPage";
import { DcimRacksPage } from "@/features/dcim/DcimRacksPage";
import { DcimRoomsPage } from "@/features/dcim/DcimRoomsPage";
import { DcimSitesPage } from "@/features/dcim/DcimSitesPage";
import { IpamPage } from "@/features/ipam/IpamPage";
import { NetworkScansPage } from "@/features/networkScans/NetworkScansPage";
import { SnmpLayout } from "@/features/snmp/SnmpLayout";
import { SnmpEnterprisesPage } from "@/features/snmp/SnmpEnterprisesPage";
import { SnmpMibsPage } from "@/features/snmp/SnmpMibsPage";
import { SnmpToolsPage } from "@/features/snmp/SnmpToolsPage";
import { usePluginRouteElements } from "@/plugins/PluginRoutes";
import { PluginProvider } from "@/plugins/PluginContext";
import { DashboardPage } from "@/pages/DashboardPage";
import { PlaceholderPage } from "@/pages/PlaceholderPage";

function AppShellLayout() {
  return (
    <AppShell>
      <Outlet />
    </AppShell>
  );
}

function AppRoutes() {
  const pluginRoutes = usePluginRouteElements();

  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route element={<RequireAuth />}>
        <Route element={<AppShellLayout />}>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/account/password" element={<ChangePasswordPage />} />
          <Route path="/dcim" element={<DcimLayout />}>
            <Route index element={<DcimOverviewPage />} />
            <Route path="sites" element={<DcimSitesPage />} />
            <Route path="rooms" element={<DcimRoomsPage />} />
            <Route path="racks" element={<DcimRacksPage />} />
            <Route path="equipment" element={<DcimEquipmentPage />} />
            <Route path="equipment/devices/:deviceId" element={<DcimDeviceDetailPage />} />
            <Route path="equipment/manufacturers/:manufacturerId" element={<DcimManufacturerDetailPage />} />
          </Route>
          <Route path="/ipam" element={<IpamPage />} />
          <Route path="/snmp" element={<SnmpLayout />}>
            <Route index element={<Navigate to="tools" replace />} />
            <Route path="tools" element={<SnmpToolsPage />} />
            <Route path="mibs" element={<SnmpMibsPage />} />
            <Route path="enterprises" element={<SnmpEnterprisesPage />} />
          </Route>
          <Route path="/jobs" element={<NetworkScansPage />} />
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
        </Route>
      </Route>
    </Routes>
  );
}

export function App() {
  return (
    <PluginProvider>
      <AppRoutes />
    </PluginProvider>
  );
}
