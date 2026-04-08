#!/usr/bin/env bash
# FreeHCI Appliance – install build dependencies on Debian 13 (trixie) and run Docker Compose.
#
# Why not only apt compose packages? On some Debian images only docker.io is published;
# docker-compose-v2 / docker-compose-plugin may be missing. This script falls back to the
# official Compose CLI plugin binary from GitHub.
#
# Usage:
#   curl -fsSL …/install-debian13.sh | bash
#   sudo bash scripts/install-debian13.sh
#
# Environment (optional):
#   REPO_URL           – Git clone URL
#   INSTALL_DIR        – Clone target (default: ~/freehci-appliance)
#   GIT_BRANCH         – Branch (default: main)
#   COMPOSE_DETACH     – 1 = docker compose up -d (default), 0 = foreground
#   COMPOSE_DL_VERSION – Compose release tag for binary fallback (default: 2.33.1)
#                        Use a v2.x tag if Docker Engine from Debian is very old.

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

echo "==> Updating apt and installing Docker, Git, curl..."
$SUDO apt-get update -qq
$SUDO apt-get install -y --no-install-recommends \
  git \
  ca-certificates \
  curl \
  docker.io

compose_works() {
  docker compose version >/dev/null 2>&1
}

install_compose_from_apt() {
  local pkg
  for pkg in docker-compose-v2 docker-compose-plugin docker-compose; do
    if apt-cache show "$pkg" >/dev/null 2>&1; then
      echo "==> Trying Compose via apt package: $pkg"
      $SUDO apt-get install -y --no-install-recommends "$pkg" || true
      if compose_works; then
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
  local arch version url dir target tmp
  arch="$(compose_binary_arch)"
  version="$COMPOSE_DL_VERSION"
  url="https://github.com/docker/compose/releases/download/v${version}/docker-compose-linux-${arch}"
  dir="/usr/local/lib/docker/cli-plugins"
  target="${dir}/docker-compose"

  echo "==> Installing Docker Compose CLI plugin v${version} from GitHub (${arch})..."
  $SUDO mkdir -p "$dir"
  tmp="$(mktemp)"
  curl -fsSL "$url" -o "$tmp"
  $SUDO install -m 0755 "$tmp" "$target"
  rm -f "$tmp"
}

install_compose_from_apt || true
if ! compose_works; then
  echo "note: 'docker compose' not available from apt; installing Compose CLI plugin from GitHub."
  install_compose_from_github
fi

echo "==> Enabling and starting Docker..."
$SUDO systemctl enable --now docker 2>/dev/null || true

if ! docker info >/dev/null 2>&1; then
  die "Docker is not running. Check: systemctl status docker"
fi

if ! compose_works; then
  die "docker compose still not available after install. Set COMPOSE_DL_VERSION or install compose manually."
fi

echo "==> Cloning or updating repository..."
if [[ -d "${INSTALL_DIR}/.git" ]]; then
  git -C "${INSTALL_DIR}" fetch --depth 1 origin "${GIT_BRANCH}" || git -C "${INSTALL_DIR}" fetch origin
  git -C "${INSTALL_DIR}" checkout "${GIT_BRANCH}"
  git -C "${INSTALL_DIR}" pull --ff-only origin "${GIT_BRANCH}" || true
else
  mkdir -p "$(dirname "${INSTALL_DIR}")"
  git clone --branch "${GIT_BRANCH}" --depth 1 "${REPO_URL}" "${INSTALL_DIR}"
fi

cd "${INSTALL_DIR}"

echo "==> Building and starting services (PostgreSQL, Redis, API, worker, frontend)..."
if [[ "${COMPOSE_DETACH}" == "1" ]]; then
  docker compose up --build -d
else
  docker compose up --build
fi

echo ""
echo "FreeHCI is starting."
echo "  Web UI:  http://localhost:8080"
echo "  API docs: http://localhost:8000/docs"
echo ""
echo "To follow logs: cd ${INSTALL_DIR} && docker compose logs -f"
echo "To stop:        cd ${INSTALL_DIR} && docker compose down"
