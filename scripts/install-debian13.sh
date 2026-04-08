#!/usr/bin/env bash
# FreeHCI Appliance – install build dependencies on Debian 13 and run Docker Compose.
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/freehci/freehci-appliance/main/scripts/install-debian13.sh | bash
#   # or after cloning:
#   sudo bash scripts/install-debian13.sh
#
# Environment (optional):
#   REPO_URL      – Git clone URL (default: https://github.com/freehci/freehci-appliance.git)
#   INSTALL_DIR    – Clone target (default: ~/freehci-appliance)
#   GIT_BRANCH     – Branch to checkout (default: main)
#   COMPOSE_DETACH – if set to 0, run compose in foreground (default: 1 = -d)

set -euo pipefail

REPO_URL="${REPO_URL:-https://github.com/freehci/freehci-appliance.git}"
INSTALL_DIR="${INSTALL_DIR:-${HOME}/freehci-appliance}"
GIT_BRANCH="${GIT_BRANCH:-main}"
COMPOSE_DETACH="${COMPOSE_DETACH:-1}"

die() {
  echo "error: $*" >&2
  exit 1
}

if [[ "$(uname -s)" != "Linux" ]]; then
  die "this installer targets Linux (Debian 13). Detected: $(uname -s)"
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

echo "==> Updating apt and installing Docker, Git, and Compose..."
$SUDO apt-get update
$SUDO apt-get install -y --no-install-recommends \
  git \
  ca-certificates \
  curl \
  docker.io

if ! $SUDO apt-get install -y --no-install-recommends docker-compose-v2; then
  echo "note: docker-compose-v2 missing; trying docker-compose-plugin..."
  $SUDO apt-get install -y --no-install-recommends docker-compose-plugin \
    || die "install docker-compose-v2 or docker-compose-plugin from Debian"
fi

echo "==> Enabling and starting Docker..."
$SUDO systemctl enable --now docker 2>/dev/null || true

if ! docker info >/dev/null 2>&1; then
  die "Docker is not running. Check: systemctl status docker"
fi

if ! docker compose version >/dev/null 2>&1; then
  die "docker compose (v2 plugin) not available. Install docker-compose-v2."
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
