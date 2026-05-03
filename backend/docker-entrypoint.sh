#!/bin/sh
set -e
mkdir -p /app/data/uploads /app/data/mibs /app/data/mibs/compiled /app/data/plugins/installed /app/data/redfish-schemas
if [ "$(id -u)" = 0 ]; then
  chown -R freehci:freehci /app/data/uploads /app/data/mibs /app/data/plugins /app/data/redfish-schemas
  exec runuser -u freehci -- "$@"
fi
exec "$@"
