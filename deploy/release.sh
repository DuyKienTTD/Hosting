#!/usr/bin/env bash
set -Eeuo pipefail
umask 077

repo=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
manifest_tool="$repo/deploy/release-manifest.py"
repository=DuyKienTTD/Hosting
mode=deploy
adopt=
if [[ ${1:-} == --rollback ]]; then mode=rollback; shift; fi
if [[ ${1:-} == --adopt-through ]]; then
  adopt=${2:?provide the last verified migration filename}
  shift 2
fi
if [[ $# -gt 1 || ( $# -eq 0 && $mode != rollback ) ]]; then
  echo 'Usage: release.sh [--adopt-through FILE] COMMIT|MANIFEST or release.sh --rollback [MANIFEST]' >&2
  exit 2
fi

env_file=$(realpath -e "${RELEASE_ENV_FILE:?set RELEASE_ENV_FILE}")
state=$(realpath -m "${RELEASE_STATE_DIR:?set RELEASE_STATE_DIR}")
site=$(realpath -e "${RELEASE_NGINX_SITE:?set RELEASE_NGINX_SITE}")
origin=${RELEASE_SMOKE_ORIGIN:?set RELEASE_SMOKE_ORIGIN}
[[ $origin =~ ^https://[A-Za-z0-9.-]+(:[0-9]+)?$ ]] || { echo 'Invalid HTTPS smoke origin' >&2; exit 2; }
mkdir -p "$state/releases" "$state/backups"
exec 9>"$state/release.lock"
flock -n 9 || { echo 'Another release is running' >&2; exit 1; }
work=$(mktemp -d "$state/.release.XXXXXX")
apps=(runtime oa-ingress data-api worker)
project=${RELEASE_COMPOSE_PROJECT:-ttd-cskh}
old_compose="${RELEASE_BOOTSTRAP_COMPOSE:-$repo/deploy/compose.prod.yml}"
compose_file=$old_compose
env_changed=0
nginx_changed=0
services_changed=0
schema_changed=0
backup=
docker_env=( "PATH=$PATH" "HOME=$HOME" )
for variable in DOCKER_HOST DOCKER_CONTEXT DOCKER_CONFIG DOCKER_TLS DOCKER_TLS_VERIFY DOCKER_CERT_PATH XDG_RUNTIME_DIR; do
  if [[ -v $variable ]]; then docker_env+=("$variable=${!variable}"); fi
done
docker_release() { env -i "${docker_env[@]}" docker "$@"; }
compose_with() {
  local environment=$1 definition=$2
  shift 2
  docker_release compose -p "$project" --env-file "$environment" -f "$definition" "$@"
}
compose() { compose_with "$env_file" "$compose_file" "$@"; }
psql_admin() {
  # shellcheck disable=SC2016
  compose exec -T postgres sh -c 'exec psql -X -q -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB" "$@"' sh "$@"
}
restore_file() {
  local source=$1 target=$2 temp
  temp=$(mktemp "$(dirname -- "$target")/.release.XXXXXX")
  cp -p -- "$source" "$temp" && mv -fT -- "$temp" "$target"
}

cleanup() {
  local status=$?
  trap - EXIT
  if ((status != 0)); then
    set +e
    if ((env_changed)); then
      if cmp -s "$work/new.env" "$env_file"; then
        restore_file "$work/old.env" "$env_file" || echo 'Restore .env failed' >&2
      elif ! cmp -s "$work/old.env" "$env_file"; then
        echo 'Environment changed concurrently. Review image pointers before restarting apps.' >&2
        schema_changed=1
      fi
    fi
    if ((nginx_changed)); then
      restore_file "$work/old.nginx" "$site" && nginx -t && systemctl reload nginx || echo 'Restore Nginx failed' >&2
    fi
    if ((services_changed)); then
      if ((schema_changed)); then
        compose stop "${apps[@]}" || true
        echo "Schema or environment requires review. App services stopped. Recovery dump: ${backup:-none}" >&2
      else
        compose_file=$old_compose
        compose up -d --wait || echo 'Restart previous services failed' >&2
      fi
    fi
  fi
  rm -rf -- "$work"
  exit "$status"
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

input=${1:-"$state/previous.json"}
if [[ $input =~ ^[a-f0-9]{40}$ ]]; then
  run=$(gh run list --repo "$repository" --workflow z6-release.yml --event push --commit "$input" \
    --status success --limit 1 --json databaseId --jq '.[0].databaseId')
  [[ $run =~ ^[0-9]+$ ]] || { echo 'No successful release for this commit' >&2; exit 1; }
  gh run download "$run" --repo "$repository" --name "release-$input" --dir "$work"
else
  cp -- "$input" "$work/release-manifest.json"
fi
manifest="$work/release-manifest.json"
python3 "$manifest_tool" values "$manifest" > "$work/values"
mapfile -t values < "$work/values"
commit=${values[0]} app_image=${values[1]} pg_image=${values[2]}
if [[ $input =~ ^[a-f0-9]{40}$ && $input != "$commit" ]]; then echo 'Commit mismatch' >&2; exit 1; fi
verify() {
  gh attestation verify "$1" --repo "$repository" --signer-workflow "$repository/.github/workflows/z6-release.yml" \
    --source-ref refs/heads/dev/ttd-zalo-mvp01 --source-digest "$commit" >/dev/null
}
verify "$manifest"
verify "oci://$app_image"
verify "oci://$pg_image"
git -C "$repo" cat-file -e "$commit^{commit}" 2>/dev/null || git -C "$repo" fetch --no-tags origin "$commit"
mkdir "$work/assets"
git -C "$repo" archive "$commit" deploy apps/ttd-zalo-agent-server/postgres apps/ttd-zalo-agent-server/ops |
  tar -x -C "$work/assets"
assets="$state/releases/$commit"
if [[ ! -d $assets ]]; then mv -- "$work/assets" "$assets"; fi
if [[ -f $state/current.json ]]; then
  python3 "$manifest_tool" values "$state/current.json" > "$work/current"
  read -r current < "$work/current"
  old_compose="$state/releases/$current/deploy/compose.prod.yml"
fi
compose_file=$old_compose
[[ -f $compose_file ]] || { echo 'Active Compose file is missing' >&2; exit 1; }
docker_release pull "$app_image"
docker_release pull "$pg_image"

ledger="$work/ledger"
: > "$ledger"
tracked=$(psql_admin -Atc "SELECT to_regclass('public.release_migrations') IS NOT NULL")
if [[ $tracked == t ]]; then
  psql_admin -Atc "SELECT name || '|' || sha256 FROM public.release_migrations ORDER BY name" > "$ledger"
fi
python3 "$manifest_tool" plan "$manifest" "$assets" "$ledger" "$adopt" "$mode" > "$work/plan"

cp -p -- "$env_file" "$work/old.env"
cp -p -- "$site" "$work/old.nginx"
template="$assets/deploy/nginx/cskh-https.conf"
if [[ -n ${RELEASE_NGINX_RENDERER:-} ]]; then
  "$RELEASE_NGINX_RENDERER" "$template" > "$work/nginx"
  template="$work/nginx"
fi
cp -p -- "$env_file" "$work/new.env"
python3 - "$work/new.env" "$app_image" "$pg_image" <<'PY'
import re
import sys
from pathlib import Path

path = Path(sys.argv[1])
data = path.read_bytes()
for key, value in zip((b"DATA_APP_IMAGE", b"DATA_POSTGRES_IMAGE"), sys.argv[2:]):
    data, count = re.subn(rb"(?m)^" + key + rb"=[^\r\n]*", key + b"=" + value.encode("ascii"), data)
    if count != 1:
        sys.exit("Expected exactly one definition for " + key.decode("ascii"))
path.write_bytes(data)
PY
compose_with "$work/new.env" "$assets/deploy/compose.prod.yml" config --quiet
if grep -q '^apply|' "$work/plan"; then
  services_changed=1
  compose stop "${apps[@]}"
  backup="$state/backups/$commit-${work##*.}.dump"
  # shellcheck disable=SC2016
  compose exec -T postgres sh -c 'exec pg_dump -Fc -U "$POSTGRES_USER" -d "$POSTGRES_DB"' > "$work/pre-migration.dump"
  compose exec -T postgres pg_restore -l < "$work/pre-migration.dump" >/dev/null
  mv -- "$work/pre-migration.dump" "$backup"
  python3 "$manifest_tool" sql "$assets" "$work/plan" > "$work/migrations.sql"
  # If the connection drops during COMMIT, treat the schema as changed.
  schema_changed=1
  psql_admin < "$work/migrations.sql"
elif [[ -s $work/plan ]]; then
  python3 "$manifest_tool" sql "$assets" "$work/plan" > "$work/migrations.sql"
  psql_admin < "$work/migrations.sql"
fi

if ! cmp -s "$work/old.env" "$env_file"; then echo 'Environment changed during release' >&2; exit 1; fi
env_changed=1
restore_file "$work/new.env" "$env_file"
compose_file="$assets/deploy/compose.prod.yml"
if ! cmp -s "$template" "$site"; then
  nginx_changed=1
  cp -p -- "$site" "$work/new.nginx"
  cat "$template" > "$work/new.nginx"
  restore_file "$work/new.nginx" "$site"
  nginx -t
  systemctl reload nginx
fi
services_changed=1
compose up -d --wait
check() {
  local path=$1 wanted=$2
  shift 2
  local status
  status=$(curl --silent --show-error --max-time 10 --output "$work/body" --write-out '%{http_code}' "$@" "$origin$path")
  if [[ $status != "$wanted" ]]; then echo "Smoke $path expected $wanted, got $status" >&2; return 1; fi
}
check /health 200
check / 200
check /webhooks/zalo-oa 200 -H 'Content-Type: application/json' -H 'X-ZEvent-Signature: mac=invalid' --data '{}'
python3 -c 'import json,sys; sys.exit(0 if json.load(open(sys.argv[1])) == {"error": 0} else 1)' "$work/body"
check /internal 404
if [[ -f $state/current.json ]] && ! cmp -s "$state/current.json" "$manifest"; then
  cp -- "$state/current.json" "$work/previous.json"
  mv -- "$work/previous.json" "$state/previous.json"
fi
mv -f -- "$manifest" "$state/current.json"
printf '%s %s\nRuntime: %s\nPostgres: %s\n' "$mode" "$commit" "$app_image" "$pg_image"
cat "$work/plan"
[[ -z $backup ]] || printf 'Pre-migration dump: %s\n' "$backup"
echo 'Smoke passed: /health, /, webhook, /internal'
