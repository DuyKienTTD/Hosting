BEGIN;
CREATE TABLE nick_enrollment (
  singleton integer PRIMARY KEY CHECK (singleton=1),
  code_hash text,
  expires_at bigint,
  credential_hash text,
  CHECK ((code_hash IS NULL) = (expires_at IS NULL))
);
GRANT SELECT,INSERT,UPDATE,DELETE ON nick_enrollment TO data_runtime;
COMMIT;
