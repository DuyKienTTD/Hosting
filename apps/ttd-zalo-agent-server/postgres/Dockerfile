FROM postgres:17-bookworm
RUN apt-get update && apt-get install -y --no-install-recommends age rclone python3 ca-certificates && rm -rf /var/lib/apt/lists/*
COPY 001.sql 002-runtime.sql runtime-grants.sql /migrations/
COPY init.sh /docker-entrypoint-initdb.d/001-initialize.sh
