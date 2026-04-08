#!/bin/sh
set -e
mkdir -p /app/data/uploads
chown -R freehci:freehci /app/data/uploads
exec runuser -u freehci -- "$@"
