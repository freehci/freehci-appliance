# Plugin-rammeverk

Plugins kan utvide **API**, **bakgrunnsjobber** og **React-UI** uten at kjernen endres for hver integrasjon.

## Backend

### Kontrakt

- `BackendPlugin` (`app/integrations/base/plugin.py`) med `manifest` og valgfri `get_router()` / `register_routes()`.
- `PluginManifest` inneholder `id`, `name`, `version`, `description`, `capabilities`, samt valgfrie `frontend_module_url` og `frontend_route_prefix`.

### Registrering

1. **Innebygd:** lastes eksplisitt i `app/main.py` via `registry.load_builtin_module("app.plugins_builtin.example")`.
2. **Distribusjon:** setuptools **entry points** i gruppen `freehci.backend_plugins` som peker på et `BackendPlugin`-objekt eller en fabrikk uten argumenter.

### HTTP

Plugin-ruter monteres under:

`/api/v1/plugins/<plugin-id-med-slash-for-punktum>/...`

Eksempel: `freehci.example` → `/api/v1/plugins/freehci/example/hello`.

### Oppdagelses-API

`GET /api/v1/plugins` returnerer manifest for kjørende plugins slik at frontend (eller andre klienter) kan bygge meny og ruter dynamisk.

## Frontend

- **`builtinRegistry.tsx`** mapper `PluginManifest.id` til `React.lazy`-komponenter som ships med appen (for ting som ikke lastes som ekstern ESM ennå).
- **`PluginRoutes`** leser manifest fra API og registrerer ruter. Mangler innebygd modul men `frontend_module_url` er satt: viser plassholder (fremtid: dynamisk `import()` av URL når sikkerhetsmodell er på plass).
- Sidebar kan utvides manuelt eller genereres fra manifest i senere iterasjon.

## Anbefalt pakkestruktur for tredjeparts-plugin

```
my_plugin/
  pyproject.toml          # entry_points: freehci.backend_plugins
  my_plugin/
    __init__.py           # plugin = MyPlugin()
    routes.py             # APIRouter
```

Tilhørende frontend kan publiseres som npm-pakke og refereres i manifest via `frontend_module_url`, eller integreres i monorepo under `frontend/src/features/plugins/vendor/...`.
