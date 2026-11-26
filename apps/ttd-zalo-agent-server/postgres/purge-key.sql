\getenv tombstone_key DATA_TOMBSTONE_KEY
INSERT INTO purge_private.signing_key VALUES(true,decode(:'tombstone_key','hex'))
ON CONFLICT(slot) DO UPDATE SET secret=excluded.secret;
