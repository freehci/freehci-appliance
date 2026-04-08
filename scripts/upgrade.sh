#!/usr/bin/env bash
# FreeHCI Appliance – pull latest Git, rebuild Compose images, restart stack.
#
# Run from anywhere:
#   bash scripts/upgrade.sh
# From clone root:
#   ./scripts/upgrade.sh
#
# Environment:
#   NO_CACHE=1      – docker compose build --no-cache (clean rebuild)
#   GIT_BRANCH      – checkout this branch before pull (optional)
#   SKIP_GIT=1      – skip git fetch/pull (only rebuild & up)
#   GIT_RESET_HARD  – default 1: after failed ff-only, git reset --hard origin/<branch>

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${REPO_ROOT}"

if [[ ! -f "${REPO_ROOT}/docker-compose.yml" ]]; then
  echo "error: docker-compose.yml not found in ${REPO_ROOT}" >&2
  exit 1
fi

echo "==> Repository: ${REPO_ROOT}"

die() {
  echo "error: $*" >&2
  exit 1
}

git_try_pull_or_reset() {
  local branch="$1"
  if git pull --ff-only origin "${branch}"; then
    return 0
  fi
  if [[ "${GIT_RESET_HARD:-1}" == "1" ]]; then
    echo "warning: could not fast-forward ${branch}. Resetting to origin/${branch} — local commits in this clone are discarded."
    git reset --hard "origin/${branch}"
    return 0
  fi
  die "git pull --ff-only failed. Fix manually or set GIT_RESET_HARD=1"
}

if [[ "${SKIP_GIT:-0}" != "1" ]]; then
  if [[ ! -d "${REPO_ROOT}/.git" ]]; then
    echo "error: not a git clone; use SKIP_GIT=1 to only rebuild" >&2
    exit 1
  fi
  if [[ -n "${GIT_BRANCH:-}" ]]; then
    echo "==> Fetching and checking out ${GIT_BRANCH}..."
    git fetch origin "${GIT_BRANCH}"
    git checkout "${GIT_BRANCH}"
    git_try_pull_or_reset "${GIT_BRANCH}"
  else
    echo "==> Pulling latest changes..."
    current="$(git rev-parse --abbrev-ref HEAD)"
    git fetch origin "${current}"
    if git pull --ff-only; then
      :
    elif [[ "${GIT_RESET_HARD:-1}" == "1" ]]; then
      echo "warning: could not fast-forward ${current}. Resetting to origin/${current} — local commits in this clone are discarded."
      git reset --hard "origin/${current}"
    else
      die "git pull --ff-only failed. Fix manually or set GIT_RESET_HARD=1"
    fi
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
