#!/usr/bin/env bash
# FreeHCI Appliance – pull latest Git, rebuild Compose images, restart stack.
#
# Run from anywhere:
#   bash scripts/upgrade.sh
# From clone root:
#   ./scripts/upgrade.sh
#
# Environment:
#   NO_CACHE=1     – docker compose build --no-cache (clean rebuild)
#   GIT_BRANCH     – checkout this branch before pull (optional)
#   SKIP_GIT=1     – skip git fetch/pull (only rebuild & up)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${REPO_ROOT}"

if [[ ! -f "${REPO_ROOT}/docker-compose.yml" ]]; then
  echo "error: docker-compose.yml not found in ${REPO_ROOT}" >&2
  exit 1
fi

echo "==> Repository: ${REPO_ROOT}"

if [[ "${SKIP_GIT:-0}" != "1" ]]; then
  if [[ ! -d "${REPO_ROOT}/.git" ]]; then
    echo "error: not a git clone; use SKIP_GIT=1 to only rebuild" >&2
    exit 1
  fi
  if [[ -n "${GIT_BRANCH:-}" ]]; then
    echo "==> Fetching and checking out ${GIT_BRANCH}..."
    git fetch origin "${GIT_BRANCH}"
    git checkout "${GIT_BRANCH}"
    git pull --ff-only origin "${GIT_BRANCH}"
  else
    echo "==> Pulling latest changes..."
    git pull --ff-only
  fi
else
  echo "==> Skipping git (SKIP_GIT=1)"
fi

BUILD_ARGS=()
if [[ "${NO_CACHE:-0}" == "1" ]]; then
  BUILD_ARGS+=(--no-cache)
  echo "==> Building images (--no-cache)..."
else
  echo "==> Building images..."
fi

docker compose build "${BUILD_ARGS[@]}"

echo "==> Recreating containers..."
docker compose up -d

echo ""
echo "Upgrade complete."
echo "  Logs: cd ${REPO_ROOT} && docker compose logs -f"
echo "  Health: curl -sS http://127.0.0.1:8000/api/v1/health/live"
