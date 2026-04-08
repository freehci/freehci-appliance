#!/usr/bin/env bash
# FreeHCI Appliance – install build dependencies on Debian 13 (trixie) and run Docker Compose.
#
# Debian notes:
# - docker.io is often the daemon only; the client is docker-cli (may be "Recommended" and not installed).
# - Package "docker-compose" may install /usr/bin/docker-compose only (no "docker compose" plugin).
#
# Usage:
#   bash -c "$(curl -fsSL https://raw.githubusercontent.com/freehci/freehci-appliance/main/scripts/install-debian13.sh)"
#   sudo bash scripts/install-debian13.sh
#
# Environment (optional):
#   REPO_URL           – Git clone URL
#   INSTALL_DIR        – Clone target (default: ~/freehci-appliance)
#   GIT_BRANCH         – Branch (default: main)
#   COMPOSE_DETACH     – 1 = up -d (default), 0 = foreground
#   COMPOSE_DL_VERSION – Compose plugin tag for GitHub fallback (default: 2.33.1)
#   GIT_RESET_HARD     – default 1: if pull --ff-only fails (diverged/rewritten main), reset --hard to origin branch

set -euo pipefail

REPO_URL="${REPO_URL:-https://github.com/freehci/freehci-appliance.git}"
INSTALL_DIR="${INSTALL_DIR:-${HOME}/freehci-appliance}"
GIT_BRANCH="${GIT_BRANCH:-main}"
COMPOSE_DETACH="${COMPOSE_DETACH:-1}"
COMPOSE_DL_VERSION="${COMPOSE_DL_VERSION:-2.33.1}"

die() {
  echo "error: $*" >&2
  exit 1
}

if [[ "$(uname -s)" != "Linux" ]]; then
  die "this installer targets Linux (Debian). Detected: $(uname -s)"
fi

if [[ -f /etc/os-release ]]; then
  # shellcheck source=/dev/null
  . /etc/os-release
  if [[ "${ID:-}" != "debian" ]]; then
    echo "warning: expected Debian; found ID=${ID:-unknown}. Continuing anyway."
  fi
fi

SUDO=""
if [[ "${EUID:-1000}" -ne 0 ]]; then
  if command -v sudo >/dev/null 2>&1; then
    SUDO="sudo"
  else
    die "run as root or install sudo"
  fi
fi

export DEBIAN_FRONTEND=noninteractive

echo "==> Updating apt and installing Docker (engine + CLI), Git, curl..."
$SUDO apt-get update -qq
$SUDO apt-get install -y --no-install-recommends \
  git \
  ca-certificates \
  curl \
  docker.io \
  docker-cli

echo "==> Enabling and starting Docker..."
$SUDO systemctl enable --now docker 2>/dev/null || true

if ! command -v docker >/dev/null 2>&1; then
  die "docker CLI still missing. Install manually: apt install docker-cli"
fi

echo "==> Waiting for Docker daemon..."
for _ in 1 2 3 4 5 6 7 8 9 10; do
  if docker info >/dev/null 2>&1; then
    break
  fi
  sleep 1
done

if ! docker info >/dev/null 2>&1; then
  die "Cannot talk to Docker daemon. Check: systemctl status docker (install docker.io if needed)"
fi

docker_compose_plugin_works() {
  docker compose version >/dev/null 2>&1
}

install_compose_from_apt() {
  local pkg
  for pkg in docker-compose-v2 docker-compose-plugin docker-compose; do
    if apt-cache show "$pkg" >/dev/null 2>&1; then
      echo "==> Trying Compose via apt package: $pkg"
      $SUDO apt-get install -y --no-install-recommends "$pkg" || true
      if docker_compose_plugin_works; then
        return 0
      fi
      if command -v docker-compose >/dev/null 2>&1 && docker-compose version >/dev/null 2>&1; then
        echo "note: using standalone /usr/bin/docker-compose from $pkg"
        return 0
      fi
    fi
  done
  return 1
}

compose_binary_arch() {
  case "$(uname -m)" in
    x86_64) echo x86_64 ;;
    aarch64) echo aarch64 ;;
    armv7l) echo armv7 ;;
    *)
      die "unsupported CPU for Compose binary: $(uname -m)"
      ;;
  esac
}

install_compose_from_github() {
  local arch version url dir tmp
  arch="$(compose_binary_arch)"
  version="$COMPOSE_DL_VERSION"
  url="https://github.com/docker/compose/releases/download/v${version}/docker-compose-linux-${arch}"
  dir="/usr/local/lib/docker/cli-plugins"

  echo "==> Installing Docker Compose CLI plugin v${version} from GitHub (${arch})..."
  $SUDO mkdir -p "$dir"
  tmp="$(mktemp)"
  curl -fsSL "$url" -o "$tmp"
  $SUDO install -m 0755 "$tmp" "$dir/docker-compose"
  rm -f "$tmp"
}

run_compose() {
  if docker_compose_plugin_works; then
    docker compose "$@"
  elif command -v docker-compose >/dev/null 2>&1; then
    docker-compose "$@"
  else
    die "no working docker compose command (plugin or docker-compose)"
  fi
}

install_compose_from_apt || true
if ! docker_compose_plugin_works && ! command -v docker-compose >/dev/null 2>&1; then
  echo "note: no usable compose from apt; installing Compose CLI plugin from GitHub."
  install_compose_from_github
fi

if ! docker_compose_plugin_works && ! command -v docker-compose >/dev/null 2>&1; then
  die "docker compose still not available. Set COMPOSE_DL_VERSION or install compose manually."
fi

# Smoke-test
run_compose version >/dev/null

echo "==> Cloning or updating repository..."
if [[ -d "${INSTALL_DIR}/.git" ]]; then
  git -C "${INSTALL_DIR}" fetch origin "${GIT_BRANCH}" --depth 1 || git -C "${INSTALL_DIR}" fetch origin "${GIT_BRANCH}"
  git -C "${INSTALL_DIR}" checkout "${GIT_BRANCH}"
  if git -C "${INSTALL_DIR}" pull --ff-only origin "${GIT_BRANCH}"; then
    :
  elif [[ "${GIT_RESET_HARD:-1}" == "1" ]]; then
    echo "warning: could not fast-forward ${GIT_BRANCH} (diverged history or force-push). Resetting to origin/${GIT_BRANCH} — local commits in this clone are discarded."
    git -C "${INSTALL_DIR}" reset --hard "origin/${GIT_BRANCH}"
  else
    die "git pull --ff-only failed. Resolve conflicts manually or rerun with GIT_RESET_HARD=1"
  fi
else
  mkdir -p "$(dirname "${INSTALL_DIR}")"
  git clone --branch "${GIT_BRANCH}" --depth 1 "${REPO_URL}" "${INSTALL_DIR}"
fi

cd "${INSTALL_DIR}"

echo "==> Making scripts/*.sh executable…"
shopt -s nullglob
for _sh in scripts/*.sh; do
  chmod +x "${_sh}" || true
done
shopt -u nullglob

echo "==> Building and starting services (PostgreSQL, Redis, API, worker, frontend)..."
if [[ "${COMPOSE_DETACH}" == "1" ]]; then
  run_compose up --build -d
else
  run_compose up --build
fi

echo ""
echo "FreeHCI is starting."
echo "  Web UI:  http://localhost:8080"
echo "  API docs: http://localhost:8000/docs"
echo ""
echo "To follow logs: cd ${INSTALL_DIR} && $(docker_compose_plugin_works && echo 'docker compose' || echo 'docker-compose') logs -f"
echo "To stop:        cd ${INSTALL_DIR} && $(docker_compose_plugin_works && echo 'docker compose' || echo 'docker-compose') down"
