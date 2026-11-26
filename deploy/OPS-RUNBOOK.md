# Backup and monitoring jobs

Copy `ops.env.example` into a private configuration file and substitute the placeholders. Set file access to owner only. Store key material separately.

1. Load the private setup configuration and run `setup-rclone-gdrive.sh` locally on the deployment host. On the browser machine, follow the headless authorization command emitted by rclone. Use the approved Drive account and paste the resulting authorization response into the private prompt. [Rclone headless authorization](https://rclone.org/remote_setup/)
2. Set `BACKUP_REMOTE=<BACKUP_REMOTE>`, `PURGE_RECEIPT_REMOTE=<RECEIPT_REMOTE>`, `PURGE_RECEIPT_BACKUP_REMOTE=<RECEIPT_BACKUP_REMOTE>`, rclone mount paths, and `BACKUP_RETENTION_COUNT=<DUMP_COUNT>` in the external Compose environment. Choose separate destinations for receipt storage and its recovery copy according to the operator policy.
3. Install the checked-in units. In private service drop-ins, set `EnvironmentFile=<OPS_ENV_FILE>` under `[Service]`. In private timer drop-ins, set `OnCalendar=<BACKUP_SCHEDULE>` and `OnCalendar=<MONITOR_SCHEDULE>` under `[Timer]`, respectively. Validate each calendar expression before enabling the timers.
4. Run `host-job.sh backup` once with the private environment and verify the success marker. Run `host-job.sh drill <DUMP_NAME>` with the age identity and tombstone key provided through the private environment. The drill never promotes staging. It refuses to reuse an existing staging database.
5. Check the logs under `<STATE_DIR>` and review owner notices after running `host-job.sh monitor`. Monitor reads service health, certificate expiry, disk use, backup freshness, budget consumption, and OA token expiry. Alerts are recorded locally and in owner notices when the database is reachable.
