import { lazy, type ComponentType } from "react";
import type { PluginManifest } from "./types";

const ExamplePluginPage = lazy(() => import("@/features/plugins/ExamplePluginPage"));

/** Innebygde frontend-moduler knyttet til backend plugin-ID. */
const builtin: Record<string, ComponentType> = {
  "freehci.example": ExamplePluginPage,
};

export function getBuiltinPluginPage(manifest: PluginManifest): ComponentType | null {
  return builtin[manifest.id] ?? null;
}

export function hasBuiltinFrontend(manifest: PluginManifest): boolean {
  return manifest.id in builtin;
}
