# Agent-notater (FreeHCI)

## Versjon ved hver push

GitHub-versjonen som UI-et sammenligner mot, kommer fra rotfilen `.ver`
(`https://raw.githubusercontent.com/freehci/freehci-appliance/main/.ver`).

- **Øk `.ver` i samme commit som skal pushes** (f.eks. `0.0.58` → `0.0.59`).
- Ikke push uten versjonsbump. Ellers viser GitHub/test-instansen gammel versjon,
  og «Oppdater nå» ser ingen ny release.

## Test-instans

Kjører her: [http://192.168.41.51:8080](http://192.168.41.51:8080)

Bruk den til å verifisere UI og API etter endringer når det er mulig.
