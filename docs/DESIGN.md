# Design system

## Visuell arv

Palett og tett «operator»-følelse er hentet fra legacy `html/ui/static/css/dark.css`:

- Bakgrunn / flater: `#1A233A`, `#272E48`
- Kant / aksent: `#596280`
- Tekst: `#bcd0f7`
- Status: grønn `#3DE010`, rød/gul for ned/ukjent

## Implementasjon

- **Én strategi:** globale **CSS-variabler** i `frontend/src/theme/tokens.css`, komponentstiler med **CSS Modules** der det gir isolasjon (`*.module.css`).
- **Tema:** `data-theme="dark" | "light"` på `documentElement`, persisteres som `localStorage["freehci-theme"]`. Lys modus beholder samme kantfarge for gjenkjennelse.
- **Typografi:** Arial / Helvetica / system-ui, primær brødtekst `0.825rem` som i legacy.

## Ikke-mål

- Mobil/layout-breakpoints er bevisst minimale (desktop først).
