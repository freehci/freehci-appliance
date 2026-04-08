import { Suspense } from "react";
import { Route } from "react-router-dom";
import { Panel } from "@/components/ui/Panel";
import { getBuiltinPluginPage } from "./builtinRegistry";
import { usePlugins } from "./PluginContext";

function routePathFromPrefix(prefix: string | null): string | null {
  if (!prefix) return null;
  const p = prefix.replace(/^\//, "").replace(/\/$/, "");
  return `${p}/*`;
}

export function PluginRoutes() {
  const plugins = usePlugins();

  return (
    <>
      {plugins.map((m) => {
        const pathPattern = routePathFromPrefix(m.frontend_route_prefix);
        if (!pathPattern) return null;
        const Cmp = getBuiltinPluginPage(m);
        if (!Cmp) {
          return (
            <Route
              key={m.id}
              path={pathPattern}
              element={
                <Panel title={m.name}>
                  <p>
                    Ingen innebygd frontend for <code>{m.id}</code>.
                    {m.frontend_module_url
                      ? ` Ekstern modul: ${m.frontend_module_url}`
                      : null}
                  </p>
                </Panel>
              }
            />
          );
        }
        return (
          <Route
            key={m.id}
            path={pathPattern}
            element={
              <Suspense fallback={<Panel title="Laster …">…</Panel>}>
                <Cmp />
              </Suspense>
            }
          />
        );
      })}
    </>
  );
}
