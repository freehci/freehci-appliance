import { Navigate, useParams } from "react-router-dom";

/** Gammel URL /iam/persons/:id → /iam/users/:id/user */
export function IamLegacyPersonRedirect() {
  const { personId } = useParams<{ personId: string }>();
  if (!personId) return <Navigate to="/iam/users" replace />;
  return <Navigate to={`/iam/users/${personId}/user`} replace />;
}
