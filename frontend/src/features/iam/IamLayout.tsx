import { Outlet } from "react-router-dom";

/** IAM-ruter uten egen ramme — hver underside bruker `Panel` der det trengs. */
export function IamLayout() {
  return <Outlet />;
}
