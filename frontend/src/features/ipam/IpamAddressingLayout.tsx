import { Outlet } from "react-router-dom";
import { Panel } from "@/components/ui/Panel";
import { IpamFamilyTabs } from "./IpamFamilyTabs";

export function IpamAddressingLayout() {
  return (
    <Panel>
      <IpamFamilyTabs />
      <Outlet />
    </Panel>
  );
}
