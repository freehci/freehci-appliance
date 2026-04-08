#!/bin/sh
set -e
mkdir -p /app/data/uploads
if [ "$(id -u)" = 0 ]; then
  chown -R freehci:freehci /app/data/uploads
  exec runuser -u freehci -- "$@"
fi
exec "$@"
