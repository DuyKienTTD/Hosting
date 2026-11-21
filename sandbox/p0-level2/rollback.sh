#!/usr/bin/env sh
set -eu

cd /root/ttd-p0-level1
backup_dir=${1:?usage: rollback.sh BACKUP_DIRECTORY}
test -d "$backup_dir"

# These names are deliberately limited to the auxiliary P0 project.
docker compose -f compose.yaml stop reasoner provider-egress n8n-sandbox || true
cp "$backup_dir/compose.yaml" compose.yaml
cp "$backup_dir/adapter.py" adapter.py
cp "$backup_dir/fake-ads-audit-v1.workflow.json" fake-ads-audit-v1.workflow.json
if [ -d "$backup_dir/n8n_data" ]; then
  failed_dir="n8n_data.level2-failed.$(date -u +%Y%m%dT%H%M%SZ)"
  mv n8n_data "$failed_dir"
  cp -a "$backup_dir/n8n_data" n8n_data
fi
docker compose -f compose.yaml up -d reasoner n8n-sandbox
printf '%s\n' 'Level 1 auxiliary runtime restored; production was not changed.'
