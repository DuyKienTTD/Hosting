BEGIN;
ALTER TABLE send_log DROP CONSTRAINT send_log_state_check;
ALTER TABLE send_log ADD CONSTRAINT send_log_state_check
  CHECK (state IN ('reserved','sent','failed','unknown_delivery','committed_before_revoke'));
COMMIT;
