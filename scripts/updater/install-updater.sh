#!/usr/bin/env bash
set -euo pipefail

# Installer helper: install systemd unit for updater-service.
#
# Expected env:
#   INSTALL_DIR – repo root (where docker-compose.yml lives)

INSTALL_DIR="${INSTALL_DIR:-}"
if [[ -z "${INSTALL_DIR}" ]]; then
  echo "error: INSTALL_DIR is required" >&2
  exit 1
fi

if [[ ! -f "${INSTALL_DIR}/scripts/updater/freehci_updater.py" ]]; then
  echo "error: updater script not found: ${INSTALL_DIR}/scripts/updater/freehci_updater.py" >&2
  exit 1
fi

tmpl="${INSTALL_DIR}/scripts/updater/freehci-updater.service.template"
out="/etc/systemd/system/freehci-updater.service"
if [[ ! -f "${tmpl}" ]]; then
  echo "error: service template not found: ${tmpl}" >&2
  exit 1
fi

echo "==> Installing FreeHCI updater systemd service..."
sed "s|{{INSTALL_DIR}}|${INSTALL_DIR}|g" "${tmpl}" > "${out}"
chmod 0644 "${out}"
if [[ ! -s "${out}" ]]; then
  echo "error: failed to write systemd unit: ${out}" >&2
  exit 1
fi

systemctl daemon-reload
systemctl enable --now freehci-updater.service
systemctl restart freehci-updater.service

echo "==> Updater service status:"
systemctl --no-pager --full status freehci-updater.service

