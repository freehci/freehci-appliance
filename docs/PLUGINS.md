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

### DCIM-enhetsdetalj (reserverte capabilities)

Stabile strenger i `manifest.capabilities` som kjernen kan bruke til å vite hva en plugin tilbyr:

| Capability-ID | Betydning |
|---------------|-----------|
| `dcim.device.hardware_view` | Kan levere maskinvare/BMC-data for en enhet (f.eks. iDRAC/iLO). |
| `dcim.device.os_view` | Kan levere OS-info for en enhet. |

Bruk `device_type_slugs` på manifestet for å begrense hvilke DCIM `device_type.slug` pluginen gjelder for (tom liste = ikke begrenset i frontend-filtreringen i dag).

**Modellering:** `device_type` er en *logisk* klasse (f.eks. `server`, `switch`). Produsent og produktserie (PowerEdge, ProLiant, …) hører til **modell** / **produsent**. Ulike styringsplaner (iDRAC, iLO, OME, OneView) er **plugins** som senere kan skille på `manufacturer_id`, modellnavn, `attributes` eller egne slug-er — ikke nødvendigvis én `device_type` per leverandør.

Eksempel-plugin (`freehci.example`) eksponerer stubber:

- `GET /api/v1/plugins/freehci/example/devices/{device_id}/hardware`
- `GET /api/v1/plugins/freehci/example/devices/{device_id}/os`

Enhetsdetalj i UI henter fra **første** plugin som matcher capability + enhetstype og har `api_route_prefix` i manifest-responsen.

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
