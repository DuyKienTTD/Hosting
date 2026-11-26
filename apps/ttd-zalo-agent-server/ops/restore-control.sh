#!/bin/sh
set -eu
[ "$#" -ge 2 ] || exit 2
db=$1
case "$db" in restore_*) ;; *) exit 2 ;; esac
case "$db" in *[!a-z0-9_]* ) exit 2 ;; esac
case "$2:$#" in
  list:2)
    psql -X -v ON_ERROR_STOP=1 -d "$db" -c 'SELECT purge_id,record_id FROM purge_private.restore_unknown' ;;
  promote:2)
    psql -X -v ON_ERROR_STOP=1 -d "$db" -c 'SELECT purge_private.promote_restore()' ;;
  resolve:4)
    psql -X -v ON_ERROR_STOP=1 -v attempt="$3" -v decision="$4" -d "$db" <<'SQL'
SELECT purge_private.resolve_restore(:'attempt', :'decision');
SQL
    ;;
  *) exit 2 ;;
esac
