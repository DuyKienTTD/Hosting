#!/bin/sh
set -eu
postgres() {
    database=$1
    shift
    psql -X -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$database" "$@"
}
fresh() {
    [ "$(postgres "$POSTGRES_DB" -Atc "SELECT (to_regprocedure('public.web_create_operator(uuid,text,text,text,text)') IS NOT NULL) AND (to_regclass('public.oa_inbox') IS NOT NULL) AND (to_regclass('public.web_sessions') IS NOT NULL) AND EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema='public' AND table_name='web_reply_drafts' AND column_name='ai_message_id') AND to_regclass('public.web_agent_runs') IS NOT NULL AND to_regclass('public.oa_consent_prompts') IS NOT NULL")" = t ]
}
upgrade() {
    postgres "$POSTGRES_DB" -qc 'CREATE DATABASE web_upgrade_fixture' || return 1
    postgres web_upgrade_fixture -q -f /migrations/001.sql -f /migrations/002-runtime.sql \
      -f /migrations/runtime-grants.sql -f /migrations/003-purge.sql -f /migrations/004-purge-confirmation.sql \
      -f /migrations/005-purge-recovery.sql -f /migrations/purge-key.sql -f /migrations/006-oa.sql \
      -f /migrations/007-oa-quota.sql -f /migrations/008-nick-audit.sql -f /migrations/009-web-operator.sql || return 1
    postgres web_upgrade_fixture -qc "INSERT INTO customers(id,display_name) VALUES ('6aba31ba-8ecf-420c-9909-6e1182412852','Upgrade fixture'); INSERT INTO tasks(created_by,title) VALUES ('fixture','Existing work');" || return 1
    postgres web_upgrade_fixture -q -f /migrations/010-web-accounts.sql -f /migrations/011-web-oa-inbox.sql -f /migrations/012-ai-drafts.sql -f /migrations/014-nick-enrollment.sql || return 1
    postgres web_upgrade_fixture -q -f /migrations/015-room-agents.sql -f /migrations/016-oa-consent.sql || return 1
    [ "$(postgres web_upgrade_fixture -Atc "SELECT EXISTS (SELECT 1 FROM customers WHERE id='6aba31ba-8ecf-420c-9909-6e1182412852' AND display_name='Upgrade fixture') AND EXISTS (SELECT 1 FROM tasks WHERE created_by='fixture' AND title='Existing work') AND to_regprocedure('public.web_create_operator(uuid,text,text,text,text)') IS NOT NULL AND EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema='public' AND table_name='web_reply_drafts' AND column_name='ai_message_id') AND to_regclass('public.web_agent_runs') IS NOT NULL AND to_regclass('public.oa_consent_prompts') IS NOT NULL")" = t ]
}
if fresh; then echo 'PASS 08a fresh migrations 001→016'; else echo 'FAIL 08a fresh migrations 001→016'; exit 1; fi
if upgrade; then echo 'PASS 08b migration 012+014→016 preserves existing customer and work data'; else echo 'FAIL 08b migration 012+014→016 preserves existing customer and work data'; exit 1; fi
