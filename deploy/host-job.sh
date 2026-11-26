#!/bin/bash
set -euo pipefail
umask 077

job=${1:-}
case "$job" in backup|drill|monitor) ;; *) exit 2 ;; esac
if [[ ${2:-} == --dry-run ]]; then
  printf 'ttd-cskh %s: local plan only\n' "$job"
  exit 0
fi
root=${CSKH_ROOT:?set the checkout directory}
state=${CSKH_STATE_DIR:?set the private state directory}
project=${CSKH_PROJECT:?set the deployment project}
database=${CSKH_DB_NAME:-zalo}
db_user=${CSKH_DB_USER:-zalo_admin}
cert_seconds=${CERT_ALERT_SECONDS:-1209600}
disk_percent=${DISK_ALERT_PERCENT:-85}
backup_seconds=${BACKUP_ALERT_SECONDS:-93600}
ai_percent=${AI_ALERT_PERCENT:-80}
oa_access_minutes=${OA_ACCESS_ALERT_MINUTES:-15}
oa_refresh_days=${OA_REFRESH_ALERT_DAYS:-7}
for threshold in "$cert_seconds" "$disk_percent" "$backup_seconds" "$ai_percent" "$oa_access_minutes" "$oa_refresh_days"; do
  [[ $threshold =~ ^[1-9][0-9]{0,8}$ ]] || exit 2
done
((disk_percent <= 100 && ai_percent <= 100)) || exit 2
install -d -m 0700 "$state"
compose() { docker compose -p "$project" --env-file "$root/deploy/.env" -f "$root/deploy/compose.prod.yml" "$@"; }
sql() { compose exec -T postgres psql -XAtq -v ON_ERROR_STOP=1 -U "$db_user" "$@"; }
maintenance() { compose --profile maintenance run --rm -T "$@"; }

if [[ $job != monitor ]]; then
  exec 9>"$state/backup.lock"
  flock -n 9
fi
exec >>"$state/$job.log" 2>&1

case "$job" in
  backup)
    maintenance -e BACKUP_RETENTION_COUNT="${BACKUP_RETENTION_COUNT:-30}" backup postgres
    maintenance backup receipts
    printf '%s\n' "$(date +%s)" > "$state/backup-success.tmp"
    mv -f "$state/backup-success.tmp" "$state/backup-success"
    ;;
  drill)
    stage=${CSKH_DRILL_DB:-restore_drill}
    [[ $stage =~ ^restore_[a-z0-9_]{1,54}$ ]] || exit 2
    existing=$(sql -d postgres -c "SELECT 1 FROM pg_database WHERE datname='$stage'")
    [[ -z $existing ]] || { echo 'Existing drill database left untouched'; exit 1; }
    : "${AGE_IDENTITY_HOST_FILE:?}" "${DATA_TOMBSTONE_KEY:?}"
    dump=${2:?pass a dump name}
    trap 'sql -d postgres -c "DROP DATABASE IF EXISTS $stage WITH (FORCE)"' EXIT
    export DATA_TOMBSTONE_KEY
    maintenance -e DATA_TOMBSTONE_KEY -e AGE_IDENTITY_FILE=/run/age-identity \
      -e RESTORE_SOURCE_DATABASE="$database" -v "$AGE_IDENTITY_HOST_FILE:/run/age-identity:ro" \
      --entrypoint sh backup /deploy/with-rclone-config.sh sh /ops/restore.sh "$dump" "$stage"
    [[ $(sql -d "$stage" -c "SELECT reconciled AND NOT EXISTS (SELECT 1 FROM purge_private.restore_unknown)
      AND NOT has_database_privilege('data_runtime',current_database(),'CONNECT')
      FROM purge_private.restore_gate WHERE slot") == t ]]
    sql -d "$stage" -c 'SELECT count(*) FROM customers' >/dev/null
    printf 'restore drill passed %s\n' "$(date -u +%FT%TZ)"
    ;;
  monitor)
    alert() {
      local key=$1 message=$2
      printf '%s %s %s\n' "$(date -u +%FT%TZ)" "$key" "$message"
      sql -d "$database" -v alert_key="monitor:$key" -v alert_message="$message" <<'SQL' ||
INSERT INTO notices(key,at,body) VALUES(:'alert_key',extract(epoch FROM now())*1000,:'alert_message')
ON CONFLICT(key) DO UPDATE SET at=excluded.at,body=excluded.body;
SQL
        echo 'Owner notice unavailable'
    }
    for service in runtime oa-ingress data-api worker postgres; do
      container=$(compose ps -q "$service" 2>/dev/null) || container=
      status=
      if [[ -n $container ]]; then
        status=$(docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{end}}' "$container" 2>/dev/null) || status=
      fi
      [[ $status == healthy ]] || alert "health-$service" "Service $service không healthy"
    done
    cert=${CSKH_CERT_FILE:-}
    openssl x509 -in "$cert" -noout -checkend "$cert_seconds" >/dev/null 2>&1 ||
      alert cert 'Chứng chỉ thiếu hoặc hết hạn trong ngưỡng cảnh báo'
    for path in "$root" "$(docker info --format '{{.DockerRootDir}}' 2>/dev/null || printf %s "$root")"; do
      if ! df -P "$path" | awk -v limit="$disk_percent" 'NR==2 {sub(/%/,"",$5); if ($5<limit) ok=1} END {exit !ok}'; then
        alert disk 'Phân vùng ứng dụng hoặc Docker không đọc được hoặc vượt ngưỡng cảnh báo'
      fi
    done
    last=$(cat "$state/backup-success" 2>/dev/null) || last=
    now=$(date +%s)
    if [[ ! $last =~ ^[0-9]{1,11}$ ]] || ((10#$last > now || now - 10#$last > backup_seconds)); then
      alert backup 'Thiếu backup hoàn chỉnh trong cửa sổ giám sát'
    fi
    cap=$(compose exec -T runtime printenv AI_ROUTER_DAILY_USD 2>/dev/null) || cap=
    if [[ $cap =~ ^[0-9]+([.][0-9]+)?$ ]] && result=$(sql -d "$database" -v cap="$cap" -v alert_percent="$ai_percent" <<'SQL'
SELECT coalesce(sum(amount),0) >= :'cap'::numeric*10000000*:'alert_percent'::numeric
FROM ledger WHERE date=to_char(now() AT TIME ZONE 'Asia/Ho_Chi_Minh','YYYY-MM-DD')
AND provider='anthropic-compatible';
SQL
    ); then
      [[ $result == f ]] || alert ai 'Chi phí và giữ chỗ AI đạt ngưỡng cảnh báo theo trần ngày'
    else
      alert ai-unavailable 'Không đọc được mức sử dụng hoặc trần AI'
    fi
    if result=$(sql -d "$database" -c "SELECT coalesce(bool_or(refresh_cipher IS NULL OR access_until<=now()+make_interval(mins=>$oa_access_minutes)
      OR refresh_until<=now()+make_interval(days=>$oa_refresh_days)),true) FROM oa_oauth"); then
      [[ $result == f ]] || alert oa-token 'Token OA thiếu hoặc gần hạn access/refresh'
    else
      alert oa-unavailable 'Không đọc được hạn token OA'
    fi
    ;;
esac
