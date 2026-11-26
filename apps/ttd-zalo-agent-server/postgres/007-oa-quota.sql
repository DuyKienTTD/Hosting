BEGIN;
ALTER TABLE send_log
  ADD COLUMN message_type text,
  ADD COLUMN send_window text,
  ADD COLUMN quota_account text,
  ADD COLUMN quota_month text,
  ADD COLUMN quota_bucket text,
  ADD CONSTRAINT oa_send_classification CHECK (
    num_nonnulls(message_type,send_window,quota_account,quota_month,quota_bucket) = 0
    OR (
      message_type IS NOT NULL AND message_type = 'oa_consultation'
      AND send_window IS NOT NULL AND quota_bucket IS NOT NULL AND quota_account IS NOT NULL
      AND (
        (send_window = 'within_48h' AND quota_bucket = 'free_window' AND quota_month IS NULL)
        OR (send_window = '48h_to_7d' AND quota_bucket IN ('monthly','paid_overflow')
          AND quota_month IS NOT NULL AND quota_month ~ '^[0-9]{4}-(0[1-9]|1[0-2])$')
      )
    )
  );
CREATE INDEX oa_monthly_quota ON send_log(quota_account, quota_month)
  WHERE quota_bucket='monthly' AND state IN ('reserved','sent','unknown_delivery');
COMMIT;
