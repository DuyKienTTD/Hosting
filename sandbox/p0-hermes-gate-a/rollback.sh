#!/usr/bin/env sh
set -eu

root=/root/ttd-hermes-gate-a
backup_dir=${1:?usage: rollback.sh BACKUP_DIRECTORY}
test -d "$backup_dir"

cd "$root"
docker compose -f compose.yaml down --remove-orphans

install -m 600 -o 1000 -g 1000 "$backup_dir/workflow-before.json" \
  /root/ttd-p0-level1/n8n_data/gate-a-rollback.workflow.json
docker exec -u node ttd-p0-n8n-sandbox n8n import:workflow --input=/home/node/.n8n/gate-a-rollback.workflow.json
docker exec -u node ttd-p0-n8n-sandbox n8n publish:workflow --id=ttdP0FakeAdsV1

cd /root/ttd-p0-level1
docker compose -f compose.yaml up -d reasoner
printf '%s\n' 'GATE A auxiliary containers stopped and previous sandbox reasoner/workflow restored.'
