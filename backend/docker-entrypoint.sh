#!/bin/sh
set -e
mkdir -p /app/data/uploads /app/data/mibs /app/data/mibs/compiled
if [ "$(id -u)" = 0 ]; then
  chown -R freehci:freehci /app/data/uploads /app/data/mibs
  exec runuser -u freehci -- "$@"
fi
exec "$@"
