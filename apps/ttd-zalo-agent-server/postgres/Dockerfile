FROM postgres:17-bookworm
RUN apt-get update && apt-get install -y --no-install-recommends age rclone python3 ca-certificates && rm -rf /var/lib/apt/lists/*
COPY 001.sql 002-runtime.sql runtime-grants.sql 003-purge.sql 004-purge-confirmation.sql 005-purge-recovery.sql purge-key.sql 006-oa.sql 007-oa-quota.sql 008-nick-audit.sql 009-web-operator.sql /migrations/
COPY init.sh /docker-entrypoint-initdb.d/001-initialize.sh
