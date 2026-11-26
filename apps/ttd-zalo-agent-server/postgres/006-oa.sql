BEGIN;
CREATE TABLE oa_oauth (
  scope text PRIMARY KEY,
  generation uuid NOT NULL,
  access_cipher bytea,
  refresh_cipher bytea,
  access_until timestamptz NOT NULL,
  refresh_until timestamptz NOT NULL
);
CREATE VIEW oa_access_generation AS
  SELECT scope,generation FROM oa_oauth WHERE access_cipher IS NOT NULL;
CREATE TABLE oa_contacts (
  scope text NOT NULL,
  target text NOT NULL,
  interaction_at bigint NOT NULL DEFAULT 0,
  follow_at bigint NOT NULL DEFAULT 0,
  following boolean NOT NULL DEFAULT false,
  withdrawn boolean NOT NULL DEFAULT false,
  PRIMARY KEY (scope,target)
);
CREATE TABLE oa_inbox (
  seq bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  scope text NOT NULL,
  event_id text NOT NULL,
  target text NOT NULL,
  expires_at timestamptz NOT NULL,
  sealed bytea,
  UNIQUE(scope,event_id)
);
CREATE INDEX oa_inbox_page ON oa_inbox(scope,seq) WHERE sealed IS NOT NULL;
CREATE INDEX oa_inbox_target ON oa_inbox(scope,target) WHERE sealed IS NOT NULL;
CREATE INDEX oa_inbox_expiry ON oa_inbox(expires_at) WHERE sealed IS NOT NULL;
-- One autocommit statement, so a synchronous Guard connection cannot block
-- the Node event loop while an ingress transaction waits for its next command.
CREATE FUNCTION oa_accept_event(
  p_scope text, p_event text, p_target text, p_at bigint,
  p_kind text, p_expires timestamptz, p_sealed bytea
) RETURNS void LANGUAGE plpgsql AS $$
DECLARE purposes text[];
BEGIN
  SET LOCAL lock_timeout = '650ms';
  SET LOCAL synchronous_commit = on;
  PERFORM pg_advisory_xact_lock(76425161);
  INSERT INTO oa_inbox(scope,event_id,target,expires_at,sealed)
    VALUES (p_scope,p_event,p_target,p_expires,
      CASE WHEN NOT EXISTS (
        SELECT 1 FROM oa_contacts WHERE scope=p_scope AND target=p_target AND withdrawn
      ) THEN p_sealed END)
    ON CONFLICT(scope,event_id) DO NOTHING;
  IF NOT FOUND THEN RETURN; END IF;
  IF p_kind = 'message' THEN
    INSERT INTO oa_contacts(scope,target,interaction_at) VALUES(p_scope,p_target,p_at)
      ON CONFLICT(scope,target) DO UPDATE SET interaction_at=GREATEST(oa_contacts.interaction_at,excluded.interaction_at)
      WHERE NOT oa_contacts.withdrawn;
    RETURN;
  ELSIF p_kind = 'user_withdraw' THEN
    INSERT INTO oa_contacts(scope,target,withdrawn) VALUES(p_scope,p_target,true)
      ON CONFLICT(scope,target) DO UPDATE SET withdrawn=true,following=false,interaction_at=0;
    UPDATE oa_inbox SET sealed=NULL WHERE scope=p_scope AND target=p_target AND sealed IS NOT NULL;
    purposes := ARRAY['retain','respond','send','ads'];
  ELSIF p_kind IN ('follow','unfollow') THEN
    INSERT INTO oa_contacts(scope,target,follow_at,following) VALUES(p_scope,p_target,p_at,p_kind='follow')
      ON CONFLICT(scope,target) DO UPDATE SET follow_at=excluded.follow_at,following=excluded.following
      WHERE NOT oa_contacts.withdrawn AND (excluded.follow_at>oa_contacts.follow_at OR
        (excluded.follow_at=oa_contacts.follow_at AND NOT excluded.following));
    IF NOT FOUND OR p_kind = 'follow' THEN RETURN; END IF;
    purposes := ARRAY['ads'];
  ELSE
    RETURN;
  END IF;

  INSERT INTO consents(customer_id,purpose,displayed_text,policy_version,evidence,occurred_at,withdrawn,previous_id)
    SELECT customer_id,purpose,displayed_text,policy_version,
      jsonb_build_object('source','zalo_oa','kind',p_kind,'eventId',p_event,'at',p_at),clock_timestamp(),true,id
    FROM (SELECT DISTINCT ON (purpose) c.* FROM consents c JOIN runtime_customer r USING(customer_id)
      WHERE r.target=p_target AND purpose=ANY(purposes) ORDER BY purpose,occurred_at DESC,id DESC) latest
    WHERE NOT withdrawn;
  INSERT INTO ad_status(customer_id,state)
    SELECT customer_id,'opted_out' FROM runtime_customer WHERE target=p_target
    ON CONFLICT(customer_id) DO UPDATE SET state='opted_out',changed_at=clock_timestamp()
    WHERE ad_status.state<>'opted_out';
END $$;
REVOKE ALL ON FUNCTION oa_accept_event(text,text,text,bigint,text,timestamptz,bytea) FROM PUBLIC;
GRANT SELECT,INSERT,UPDATE ON oa_oauth TO data_runtime;
GRANT SELECT ON oa_access_generation TO data_runtime;
GRANT SELECT,INSERT,UPDATE ON oa_contacts TO data_runtime;
GRANT SELECT,INSERT,UPDATE ON oa_inbox TO data_runtime;
GRANT EXECUTE ON FUNCTION oa_accept_event(text,text,text,bigint,text,timestamptz,bytea) TO data_runtime;
COMMIT;
