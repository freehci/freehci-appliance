import { useQuery } from "@tanstack/react-query";
import { createContext, useContext, type ReactNode } from "react";
import { apiGet } from "@/lib/api";
import type { PluginListResponse, PluginManifest } from "./types";

const PluginContext = createContext<PluginManifest[] | null>(null);

export function PluginProvider({ children }: { children: ReactNode }) {
  const { data } = useQuery({
    queryKey: ["plugins"],
    queryFn: () => apiGet<PluginListResponse>("/api/v1/plugins"),
    staleTime: 60_000,
  });

  const plugins = data?.plugins ?? [];

  return <PluginContext.Provider value={plugins}>{children}</PluginContext.Provider>;
}

export function usePlugins() {
  const ctx = useContext(PluginContext);
  if (ctx === null) throw new Error("usePlugins uten PluginProvider");
  return ctx;
}
