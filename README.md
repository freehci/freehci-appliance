# FreeHCI Appliance

Modern **FastAPI** backend and **React (TypeScript)** frontend with Docker Compose, plugin hooks, and a visual language aligned with the original FreeHCI dark UI.

## Requirements

For the full stack (recommended):

- **Docker** with **Compose v2** (`docker compose`)
- **Git**

For local development without Docker:

- Python **3.11+**
- Node.js **20+** (22 recommended for builds)
- Redis (if you run the Celery worker locally)

---

## Quick start: clone and build with Docker

Public repository:

```text
https://github.com/freehci/freehci-appliance.git
```

Clone and start all services (PostgreSQL, Redis, API, worker, frontend):

```bash
git clone https://github.com/freehci/freehci-appliance.git
cd freehci-appliance
docker compose up --build
```

Detached mode (background):

```bash
docker compose up --build -d
```

Then open:

- **Web UI:** [http://localhost:8080](http://localhost:8080) (nginx proxies `/api/` to the API)
- **OpenAPI:** [http://localhost:8000/docs](http://localhost:8000/docs)

On a fresh database the API creates a local admin user **admin** / **admin** at startup. Sign in through the UI, then change the password (key icon in the header). For production, set a strong **`JWT_SECRET`** (see [`.env.example`](.env.example) and `docker-compose.yml`).

**DCIM images in the UI:** `GET` requests for manufacturer logos and device-model front/back files are allowed **without** a JWT, because browsers do not send `Authorization` on `<img src="…">`. Uploading or deleting those files still requires a logged-in admin.

Stop the stack:

```bash
docker compose down
```

### Upgrade an existing install

From the clone directory (where `docker-compose.yml` lives):

```bash
bash scripts/upgrade.sh
```

This runs `git pull --ff-only`, `docker compose build`, and `docker compose up -d --force-recreate` for **api**, **worker**, and **frontend** (so new images are actually used; plain `up -d` often keeps old containers).

Options via environment:

| Variable    | Effect |
|-------------|--------|
| `UPLOAD_ROOT` | Katalog for opplastede DCIM-filer (produsent-logoer og modellbilder); standard i Compose er `/app/data/uploads`. Compose bruker et **navngitt volum** (`dcim_uploads`) mot denne stien for varig lagring. |
| `MIB_ROOT` | Katalog for opplastede SNMP-MIB-filer; standard i Compose er `/app/data/mibs`. Volumet **`dcim_mibs`** sørger for at MIB-er overlever image-rebuild (samme mønster som opplastinger). |
| `MIB_COMPILED_ROOT` | Katalog for PySNMP-kompilerte MIB-moduler (`.py` fra pysmi). I Compose er standarden `/app/data/mibs/compiled` (under samme volum som `MIB_ROOT`). |
| `NO_CACHE=1` | `docker compose build --no-cache` (full rebuild) |
| `SKIP_GIT=1` | Only rebuild and restart; no `git pull` |
| `GIT_BRANCH=name` | `git fetch` + checkout branch before pull |
| `GIT_RESET_HARD=0` | Stop if `git pull --ff-only` fails instead of resetting to `origin/<branch>` (default is reset) |

Optional environment file: copy [`.env.example`](.env.example) and adjust values; override variables in `docker-compose.yml` or via a Compose `env_file` if you extend the setup.

---

## Automated install on Debian 13

The helper script installs **`docker.io`** and **`docker-cli`** (on Debian the CLI is a separate package and is often only “recommended”, so a minimal install can leave you with a running daemon but no `docker` command), **Docker Compose** (tries apt packages first, including standalone `docker-compose`; if needed it installs the [Compose CLI plugin](https://github.com/docker/compose) from GitHub), **Git**, and **curl**. It then clones the repo (or updates an existing clone) and runs Compose.

### Prerequisites on minimal images

To **download** the script you need `curl` or `wget` (or clone the repo with Git instead):

```bash
sudo apt-get update
sudo apt-get install -y curl ca-certificates
```

**`wget` alternative** (if `curl` is missing): `sudo apt-get install -y wget ca-certificates`, then download the script and run `sudo bash install-debian13.sh`, or use the Git clone path below.

### One-liner install

Requires `curl` (see prerequisites above). Run as root **or** as a user with `sudo`; the script elevates for `apt` / Docker when needed.

```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/freehci/freehci-appliance/main/scripts/install-debian13.sh)"
```

**No `curl` yet?** Install Git, clone the repository, then run the script from the tree (the script will install the rest):

```bash
sudo apt-get update && sudo apt-get install -y git ca-certificates
git clone https://github.com/freehci/freehci-appliance.git
cd freehci-appliance
sudo bash scripts/install-debian13.sh
```

Optional environment variables:

| Variable             | Default                                           | Purpose |
|----------------------|---------------------------------------------------|---------|
| `REPO_URL`           | `https://github.com/freehci/freehci-appliance.git` | Git remote to clone |
| `INSTALL_DIR`        | `$HOME/freehci-appliance`                         | Clone / install directory |
| `GIT_BRANCH`         | `main`                                            | Branch to checkout |
| `COMPOSE_DETACH`     | `1`                                               | `1` = `docker compose up -d`, `0` = foreground |
| `COMPOSE_DL_VERSION` | `2.33.1`                                          | Compose release tag when apt has no compose package (override if needed) |
| `GIT_RESET_HARD`     | `1`                                               | If `git pull --ff-only` fails (diverged/`main` rewritten), run `git reset --hard origin/<branch>`. Set `0` to abort instead. |

After install, add your user to the `docker` group if you want to run `docker` without `sudo`:

```bash
sudo usermod -aG docker "$USER"
# log out and back in
```

---

## Local development (without Docker)

**Backend** (from `backend/`):

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
mkdir -p data
export DATABASE_URL="${DATABASE_URL:-sqlite:///./data/freehci.db}"
alembic upgrade head
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend** (from `frontend/`):

```bash
npm install
npm run dev
```

The Vite dev server proxies `/api` to `http://127.0.0.1:8000`. Set `CORS_ORIGINS` on the API if you use another origin or port.

**Frontend production build** (from `frontend/`):

```bash
npm ci
npm run build
```

Output is written to `frontend/dist/`.

---

## Docker Compose: vanlige loggmeldinger

Etter `docker compose up` er dette normalt eller forventet i utvikling:

| Kilde | Melding | Forklaring |
|--------|---------|------------|
| **API** | Alembic `Running upgrade -> 20260408_0001` | Første migrasjon kjørt; OK. |
| **Frontend (nginx)** | `default.conf differs from the packaged version` | Vi bytter ut standard nginx-konfig; **ingen feil**. |
| **Frontend → API** | `404` på `/api/v1/...` via proxy etter oppgradering | Tidligere brukte vi variabel i `proxy_pass` **med** `/api/`-suffiks; da ble ikke stien omskrevet riktig. Nå brukes **`$request_uri`**. Kjør **`docker compose build frontend && docker compose up -d`**. |
| **Frontend → API** | `502` / «connection refused» rett etter `up` | API kjører Alembic før Uvicorn lytter. Compose venter nå på **`api` healthcheck** før frontend startes; ved manuell rekkefølge: vent til `GET /api/v1/health/live` svarer. |
| **PostgreSQL (Alpine)** | `locale: not found` / `no usable system locales` | Vanlig i slanke images; databasen bruker likevel UTF-8. Kan ignoreres for dev. |
| **PostgreSQL** | `trust` authentication for local | Typisk ved første `initdb` i container; **ikke** bruk slik i produksjon uten ekte `pg_hba`-sikkerhet. |
| **Redis** | `Memory overcommit must be enabled` | **Verten** (Linux): kjør én gang `sysctl vm.overcommit_memory=1` eller legg i `/etc/sysctl.d/` og last på nytt. |
| **Celery worker** | `running the worker with superuser privileges` | Oppstår hvis prosessen kjører som root. Sjekk at **`docker-compose.yml` ikke setter `user:`** på api/worker (da feiler `runuser` i entrypoint). Etter **`git pull`**: **`docker compose build --no-cache api worker frontend && docker compose up -d`**. Uvicorn/Celery skal startes som brukeren **`freehci`** (UID 10001) via **`backend/docker-entrypoint.sh`**. |

---

## DCIM & IPAM integration

- **Interface hierarchy:** DCIM device interfaces may set optional **`parent_interface_id`** (e.g. Juniper physical `me0` as parent, logical `me0.0` as child). The MAC often belongs on the parent; VLAN and IP assignments often belong on the child.
- **IPv4 inventory** responses include read-only **`interface_name`** when an address is tied to a DCIM interface, so lists can show `me0.0` instead of only a numeric id.
- **Assign** (IPAM request with `mode=assign`) creates both an **IPAM address row** and a **DCIM `InterfaceIpAssignment`**. If the request includes **`device_id`**, it must match the device that owns the chosen **`interface_id`** (the UI always sends both). **Release** on that address removes the assignment and clears the inventory link fields in a consistent way.
- In the UI, device names in IPAM link to **DCIM device detail → Network** (`?tab=network`).

For optional hardware/OS panels on devices, see [Plugin framework](docs/PLUGINS.md).

---

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [Design / theme tokens](docs/DESIGN.md)
- [Plugin framework](docs/PLUGINS.md)
