#!/bin/sh
set -eu
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" -f /migrations/001.sql -f /migrations/002-runtime.sql -f /migrations/runtime-grants.sql
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<'SQL'
\getenv app_password DATA_APP_PASSWORD
\getenv worker_password DATA_WORKER_PASSWORD
SELECT format('CREATE ROLE data_app LOGIN PASSWORD %L', :'app_password') \gexec
SELECT format('CREATE ROLE data_worker LOGIN PASSWORD %L', :'worker_password') \gexec
GRANT SELECT ON customers,visible_messages,tasks,conversations,restore_tombstones TO data_app;
GRANT INSERT(display_name), UPDATE(display_name) ON customers TO data_app;
GRANT INSERT(conversation_id,event_id,body,retain_until) ON messages TO data_app;
GRANT SELECT(id,conversation_id,event_id) ON messages TO data_app;
GRANT INSERT(message_id) ON queue_jobs TO data_app;
GRANT INSERT(created_by,title), UPDATE(state) ON tasks TO data_app;
GRANT INSERT ON audit_log TO data_app,data_worker;
GRANT SELECT ON queue_jobs,visible_messages TO data_worker;
GRANT UPDATE(processed_at) ON queue_jobs TO data_worker;
GRANT EXECUTE ON FUNCTION delete_eligible(uuid,integer,integer,text),purge_candidates(text) TO data_worker;
SQL
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" -f /migrations/003-purge.sql -f /migrations/004-purge-confirmation.sql -f /migrations/005-purge-recovery.sql -f /migrations/purge-key.sql
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" -f /migrations/006-oa.sql -f /migrations/007-oa-quota.sql -f /migrations/008-nick-audit.sql
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" -f /migrations/009-web-operator.sql
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" -f /migrations/010-web-accounts.sql
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" -f /migrations/011-web-oa-inbox.sql
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" -f /migrations/012-ai-drafts.sql
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" -f /migrations/014-nick-enrollment.sql
