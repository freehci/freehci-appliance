# Arkitektur (FreeHCI rewrite)

## Oversikt

Monorepoet er delt i:

- **`backend/`** – FastAPI, SQLAlchemy 2.x, Alembic, Celery-klargjort worker.
- **`frontend/`** – React 18, TypeScript, Vite, React Query, React Router.
- **`docker-compose.yml`** – Postgres, Redis, API, worker og statisk frontend (nginx).

Den eksisterende rot-applikasjonen (`main.py`, `html/ui`, `routers/`) er **legacy** og berøres ikke av den nye kjernen.

## Backend – lag

| Lag | Ansvar |
|-----|--------|
| `app/api/` | HTTP-routers, avhengighetsinjeksjon (`deps.py`), ingen forretningslogikk. |
| `app/services/` | Orkestrering og mapping til API-skjemaer. |
| `app/integrations/` | Plugin-registry og base-typer for leverandører. |
| `app/models/` | SQLAlchemy `DeclarativeBase` og fremtidige tabeller. |
| `app/workers/` | Celery-app og task-moduler. |
| `app/plugins_builtin/` | Referanse-plugins (kan fjernes eller erstattes). |

## API-versjonering

Alle nye endepunkter under `/api/v1/`. Helse: `/api/v1/health/live`, `/api/v1/health/ready`.

## Database

- **SQLite** lokalt (standard `sqlite:///./data/freehci.db`).
- **PostgreSQL** i Docker via `DATABASE_URL=postgresql+psycopg://...`.

Migrasjoner kjøres med Alembic; API-container kjører `alembic upgrade head` ved oppstart.

## Observabilitet

Grunnmur: strukturert stdout-logging. Utvid later med audit-tabell, metrikker og sporings-ID.

## Kubernetes (senere)

Bygges stein på stein: samme containerimages, miljøvariabler for database, Redis, og evt. secrets for broker.
