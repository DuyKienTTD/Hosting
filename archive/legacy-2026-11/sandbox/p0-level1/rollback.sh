#!/usr/bin/env sh
set -eu

cd /root/ttd-p0-level1

# Stop only the two Level 1 auxiliary services. Keep their root-only data and
# evidence intact so the deployment can be inspected or recovered.
docker compose -f compose.yaml stop reasoner n8n-sandbox

printf '%s\n' 'P0 auxiliary containers stopped; primary services were not changed.'
