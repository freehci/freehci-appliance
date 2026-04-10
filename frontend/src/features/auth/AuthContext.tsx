import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { getStoredAccessToken, setStoredAccessToken } from "@/lib/authStorage";

type AuthState = {
  token: string | null;
  setToken: (token: string | null) => void;
  logout: () => void;
};

const AuthContext = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setTokenState] = useState<string | null>(() => getStoredAccessToken());

  useEffect(() => {
    const onCleared = () => setTokenState(null);
    window.addEventListener("freehci:auth-cleared", onCleared);
    return () => window.removeEventListener("freehci:auth-cleared", onCleared);
  }, []);

  const setToken = useCallback((t: string | null) => {
    setStoredAccessToken(t);
    setTokenState(t);
  }, []);

  const logout = useCallback(() => {
    setStoredAccessToken(null);
    setTokenState(null);
  }, []);

  const value = useMemo(() => ({ token, setToken, logout }), [token, setToken, logout]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth uten AuthProvider");
  return ctx;
}
