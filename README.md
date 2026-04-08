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

Stop the stack:

```bash
docker compose down
```

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

**`wget` alternative:**

```bash
sudo apt-get install -y wget ca-certificates
wget -qO install-freehci.sh https://raw.githubusercontent.com/freehci/freehci-appliance/main/scripts/install-debian13.sh
chmod +x install-freehci.sh
sudo ./install-freehci.sh
```

### Run the installer

As root or with `sudo`:

```bash
curl -fsSL https://raw.githubusercontent.com/freehci/freehci-appliance/main/scripts/install-debian13.sh -o install-freehci.sh
chmod +x install-freehci.sh
sudo ./install-freehci.sh
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

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [Design / theme tokens](docs/DESIGN.md)
- [Plugin framework](docs/PLUGINS.md)
