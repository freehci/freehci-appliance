import { Navigate, Outlet, Route, Routes } from "react-router-dom";
import { AppShell } from "@/components/layout/AppShell";
import { ChangePasswordPage } from "@/features/auth/ChangePasswordPage";
import { LoginPage } from "@/features/auth/LoginPage";
import { RequireAuth } from "@/features/auth/RequireAuth";
import { DcimDeviceDetailPage } from "@/features/dcim/DcimDeviceDetailPage";
import { DcimDeviceModelDetailPage } from "@/features/dcim/DcimDeviceModelDetailPage";
import { DcimDeviceNewPage } from "@/features/dcim/DcimDeviceNewPage";
import { DcimDeviceTypeDetailPage } from "@/features/dcim/DcimDeviceTypeDetailPage";
import { DcimEquipmentPage } from "@/features/dcim/DcimEquipmentPage";
import { DcimManufacturerDetailPage } from "@/features/dcim/DcimManufacturerDetailPage";
import { DcimLayout } from "@/features/dcim/DcimLayout";
import { DcimOverviewPage } from "@/features/dcim/DcimOverviewPage";
import { DcimRacksPage } from "@/features/dcim/DcimRacksPage";
import { DcimRoomDetailPage } from "@/features/dcim/DcimRoomDetailPage";
import { DcimRoomsPage } from "@/features/dcim/DcimRoomsPage";
import { DcimSitesPage } from "@/features/dcim/DcimSitesPage";
import { IpamPage } from "@/features/ipam/IpamPage";
import { JobsLayout } from "@/features/jobs/JobsLayout";
import { JobsRunsPage } from "@/features/jobs/JobsRunsPage";
import { JobsSchedulerPage } from "@/features/jobs/JobsSchedulerPage";
import { JobsTemplatesPage } from "@/features/jobs/JobsTemplatesPage";
import { SnmpLayout } from "@/features/snmp/SnmpLayout";
import { SnmpEnterprisesPage } from "@/features/snmp/SnmpEnterprisesPage";
import { SnmpMibsPage } from "@/features/snmp/SnmpMibsPage";
import { SnmpToolsPage } from "@/features/snmp/SnmpToolsPage";
import { SnmpBrowserPage } from "@/features/snmp/SnmpBrowserPage";
import { usePluginRouteElements } from "@/plugins/PluginRoutes";
import { PluginProvider } from "@/plugins/PluginContext";
import { DashboardPage } from "@/pages/DashboardPage";
import { IntegrationsPage } from "@/features/integrations/IntegrationsPage";
import { IamGroupDetailPage } from "@/features/iam/IamGroupDetailPage";
import { IamGroupsPage } from "@/features/iam/IamGroupsPage";
import { IamLayout } from "@/features/iam/IamLayout";
import { IamLegacyPersonRedirect } from "@/features/iam/IamLegacyPersonRedirect";
import { IamPersonDetailPage } from "@/features/iam/IamPersonDetailPage";
import { IamServiceAccountsPage } from "@/features/iam/IamServiceAccountsPage";
import { IamRoleDetailPage } from "@/features/iam/IamRoleDetailPage";
import { IamRolesPage } from "@/features/iam/IamRolesPage";
import { IamUserComingSoonTab } from "@/features/iam/IamUserComingSoonTab";
import { IamUserDetailLayout } from "@/features/iam/IamUserDetailLayout";
import { IamUserGroupsTab } from "@/features/iam/IamUserGroupsTab";
import { IamUserProfileTab } from "@/features/iam/IamUserProfileTab";
import { IamUserRolesTab } from "@/features/iam/IamUserRolesTab";
import { IamUsersListPage } from "@/features/iam/IamUsersListPage";
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
            <Route path="rooms/:roomId" element={<DcimRoomDetailPage />} />
            <Route path="rooms" element={<DcimRoomsPage />} />
            <Route path="racks" element={<DcimRacksPage />} />
            <Route path="equipment" element={<DcimEquipmentPage />} />
            <Route path="equipment/devices/new" element={<DcimDeviceNewPage />} />
            <Route path="equipment/devices/:deviceId" element={<DcimDeviceDetailPage />} />
            <Route path="equipment/device-types/:deviceTypeId" element={<DcimDeviceTypeDetailPage />} />
            <Route path="equipment/device-models/:deviceModelId" element={<DcimDeviceModelDetailPage />} />
            <Route path="equipment/manufacturers/:manufacturerId" element={<DcimManufacturerDetailPage />} />
          </Route>
          <Route path="/ipam" element={<IpamPage />} />
          <Route path="/snmp" element={<SnmpLayout />}>
            <Route index element={<Navigate to="tools" replace />} />
            <Route path="tools" element={<SnmpToolsPage />} />
            <Route path="mibs" element={<SnmpMibsPage />} />
            <Route path="enterprises" element={<SnmpEnterprisesPage />} />
            <Route path="browser" element={<SnmpBrowserPage />} />
          </Route>
          <Route path="/jobs" element={<JobsLayout />}>
            <Route index element={<JobsRunsPage />} />
            <Route path="scheduler" element={<JobsSchedulerPage />} />
            <Route path="templates" element={<JobsTemplatesPage />} />
          </Route>
          <Route path="/integrations" element={<IntegrationsPage />} />
          <Route path="/iam" element={<IamLayout />}>
            <Route index element={<Navigate to="users" replace />} />
            <Route path="persons" element={<Navigate to="/iam/users" replace />} />
            <Route path="persons/:personId" element={<IamLegacyPersonRedirect />} />
            <Route path="users" element={<IamUsersListPage />} />
            <Route path="users/:userId" element={<IamUserDetailLayout />}>
              <Route index element={<Navigate to="user" replace />} />
              <Route path="user" element={<IamUserProfileTab />} />
              <Route path="login-devices" element={<IamUserComingSoonTab />} />
              <Route path="groups" element={<IamUserGroupsTab />} />
              <Route path="roles" element={<IamUserRolesTab />} />
              <Route path="applications" element={<IamUserComingSoonTab />} />
              <Route path="company" element={<IamUserComingSoonTab />} />
              <Route path="log" element={<IamUserComingSoonTab />} />
            </Route>
            <Route path="service-accounts" element={<IamServiceAccountsPage />} />
            <Route path="service-accounts/:personId" element={<IamPersonDetailPage />} />
            <Route path="roles" element={<IamRolesPage />} />
            <Route path="roles/:roleId" element={<IamRoleDetailPage />} />
            <Route path="groups" element={<IamGroupsPage />} />
            <Route path="groups/:groupId" element={<IamGroupDetailPage />} />
          </Route>
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
