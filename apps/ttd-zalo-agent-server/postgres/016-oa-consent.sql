CREATE TABLE oa_consent_prompts (
  scope text NOT NULL,
  target text NOT NULL,
  send_id text NOT NULL REFERENCES send_log(id) ON DELETE CASCADE,
  at bigint NOT NULL,
  displayed_text text NOT NULL,
  policy_version text NOT NULL,
  PRIMARY KEY (scope,target)
);

CREATE TABLE oa_consent_decisions (
  scope text NOT NULL,
  receipt text NOT NULL,
  decided_at timestamptz NOT NULL DEFAULT clock_timestamp(),
  PRIMARY KEY (scope,receipt)
);
GRANT SELECT, INSERT, UPDATE ON oa_consent_prompts TO data_runtime;
GRANT SELECT, INSERT ON oa_consent_decisions TO data_runtime;
