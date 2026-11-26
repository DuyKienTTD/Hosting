BEGIN;
CREATE TABLE customers (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  display_name text NOT NULL DEFAULT '',
  created_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE channel_identities (
  channel text NOT NULL CHECK (channel IN ('oa','nick','bot')),
  account_id text NOT NULL, uid text NOT NULL,
  customer_id uuid NOT NULL REFERENCES customers,
  PRIMARY KEY (channel, account_id, uid)
);
CREATE TABLE conversations (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id uuid NOT NULL REFERENCES customers,
  channel text NOT NULL CHECK (channel IN ('oa','nick','bot')),
  created_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE messages (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  conversation_id uuid NOT NULL REFERENCES conversations,
  event_id text NOT NULL,
  body text NOT NULL,
  version integer NOT NULL DEFAULT 1 CHECK (version > 0),
  received_at timestamptz NOT NULL DEFAULT now(),
  retain_until timestamptz NOT NULL,
  purge_after timestamptz,
  purge_policy integer,
  UNIQUE (conversation_id, event_id),
  CHECK ((purge_after IS NULL) = (purge_policy IS NULL))
);
CREATE TABLE consents (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id uuid NOT NULL REFERENCES customers,
  purpose text NOT NULL CHECK (purpose IN ('retain','respond','send','ads')),
  displayed_text text NOT NULL,
  policy_version text NOT NULL,
  evidence jsonb NOT NULL,
  occurred_at timestamptz NOT NULL DEFAULT now(),
  withdrawn boolean NOT NULL DEFAULT false,
  previous_id uuid REFERENCES consents,
  CHECK (NOT withdrawn OR previous_id IS NOT NULL),
  UNIQUE (previous_id)
);
ALTER TABLE consents ADD CONSTRAINT consent_predecessor_key UNIQUE (id,customer_id,purpose);
ALTER TABLE consents ADD CONSTRAINT consent_predecessor_scope
  FOREIGN KEY (previous_id,customer_id,purpose) REFERENCES consents(id,customer_id,purpose);
CREATE INDEX consents_history ON consents(customer_id, purpose, occurred_at DESC);
CREATE TABLE ad_status (
  customer_id uuid PRIMARY KEY REFERENCES customers,
  state text NOT NULL CHECK (state IN ('active','ads_paused_review','opted_out')),
  changed_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE send_log (
  idempotency_key varchar(128) PRIMARY KEY,
  customer_id uuid NOT NULL REFERENCES customers,
  state text NOT NULL CHECK (state IN ('reserved','sent','failed','unknown_delivery')),
  created_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE tasks (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  created_by text NOT NULL,
  title text NOT NULL CHECK (length(title) BETWEEN 1 AND 500),
  state text NOT NULL DEFAULT 'new' CHECK (state IN ('new','in_progress','review','done')),
  created_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE audit_log (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  actor text NOT NULL, action text NOT NULL, record_id uuid,
  occurred_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE legal_holds (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id uuid REFERENCES customers,
  message_id uuid,
  reason text NOT NULL,
  released_at timestamptz,
  CHECK (num_nonnulls(customer_id,message_id)=1)
);
-- Orders, accounting records, disputes and consent proofs never enter this scope.
CREATE TABLE deletion_policy (
  version integer PRIMARY KEY,
  quarantine_seconds integer NOT NULL CHECK (quarantine_seconds BETWEEN 1 AND 2592000),
  enabled boolean NOT NULL
);
INSERT INTO deletion_policy VALUES (1, 604800, true);
CREATE UNIQUE INDEX single_deletion_policy ON deletion_policy(enabled) WHERE enabled;
CREATE TABLE deletion_log (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  record_id uuid NOT NULL,
  event_id text NOT NULL,
  conversation_id uuid NOT NULL,
  version integer NOT NULL,
  policy_version integer NOT NULL,
  reason_code text NOT NULL CHECK (reason_code = 'retention_elapsed'),
  action text NOT NULL CHECK (action IN ('quarantine','purge','restore_tombstone')),
  occurred_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (record_id,version,action)
);
CREATE TABLE queue_jobs (
  message_id uuid PRIMARY KEY REFERENCES messages ON DELETE CASCADE,
  created_at timestamptz NOT NULL DEFAULT now(),
  processed_at timestamptz
);
CREATE TABLE restore_tombstones (
  record_id uuid PRIMARY KEY,
  conversation_id uuid NOT NULL,
  event_id text NOT NULL,
  version integer NOT NULL,
  policy_version integer NOT NULL,
  UNIQUE(conversation_id,event_id)
);
CREATE VIEW visible_messages AS SELECT id,conversation_id,body,received_at FROM messages WHERE purge_after IS NULL;
CREATE FUNCTION prevent_log_change() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
  RAISE EXCEPTION 'append_only';
END $$;
CREATE TRIGGER immutable_deletion_log BEFORE UPDATE OR DELETE OR TRUNCATE ON deletion_log
FOR EACH STATEMENT EXECUTE FUNCTION prevent_log_change();
CREATE TRIGGER immutable_consent_history BEFORE UPDATE OR DELETE OR TRUNCATE ON consents
FOR EACH STATEMENT EXECUTE FUNCTION prevent_log_change();
CREATE TRIGGER immutable_audit_log BEFORE UPDATE OR DELETE OR TRUNCATE ON audit_log
FOR EACH STATEMENT EXECUTE FUNCTION prevent_log_change();
CREATE FUNCTION reject_erased_message() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
  IF EXISTS (SELECT 1 FROM restore_tombstones WHERE record_id=NEW.id OR
             (conversation_id=NEW.conversation_id AND event_id=NEW.event_id)) THEN
    RAISE EXCEPTION 'erased_event';
  END IF;
  RETURN NEW;
END $$;
CREATE TRIGGER reject_erased BEFORE INSERT ON messages FOR EACH ROW EXECUTE FUNCTION reject_erased_message();
CREATE FUNCTION deletion_unheld(item messages) RETURNS boolean LANGUAGE sql STABLE AS $$
  SELECT NOT EXISTS (SELECT 1 FROM legal_holds h JOIN conversations c ON c.id=item.conversation_id
    WHERE h.released_at IS NULL AND (h.message_id=item.id OR h.customer_id=c.customer_id));
$$;
CREATE FUNCTION delete_eligible(record_id uuid, expected_version integer, policy_version integer, reason_code text)
RETURNS boolean LANGUAGE plpgsql SECURITY DEFINER SET search_path = pg_catalog, public AS $$
DECLARE item messages; delay_seconds integer;
BEGIN
  IF reason_code IS DISTINCT FROM 'retention_elapsed' THEN RETURN false; END IF;
  -- Also serializes against inserts/updates of holds, including holds for the whole customer.
  LOCK TABLE legal_holds IN SHARE MODE;
  SELECT * INTO item FROM messages WHERE id=record_id FOR UPDATE;
  SELECT quarantine_seconds INTO delay_seconds FROM deletion_policy WHERE version=policy_version AND enabled FOR SHARE;
  IF item.id IS NULL OR item.version IS DISTINCT FROM expected_version OR delay_seconds IS NULL
     OR item.retain_until>now() OR item.purge_after IS NOT NULL OR NOT deletion_unheld(item) THEN
    RETURN false;
  END IF;
  UPDATE messages SET purge_after=now()+make_interval(secs=>delay_seconds), purge_policy=policy_version WHERE id=record_id;
  INSERT INTO deletion_log(record_id,event_id,conversation_id,version,policy_version,reason_code,action)
    VALUES(item.id,item.event_id,item.conversation_id,item.version,policy_version,reason_code,'quarantine');
  RETURN true;
END $$;
CREATE FUNCTION purge_candidates(stage text) RETURNS TABLE
  (id uuid, conversation_id uuid, event_id text, version integer, policy_version integer)
LANGUAGE sql SECURITY DEFINER SET search_path=pg_catalog,public AS $$
  SELECT m.id,m.conversation_id,m.event_id,m.version,p.version
  FROM messages m JOIN deletion_policy p ON p.enabled
  WHERE (CASE stage WHEN 'quarantine' THEN m.purge_after IS NULL AND m.retain_until<=now()
    WHEN 'purge' THEN m.purge_after<=now() AND m.purge_policy=p.version ELSE false END)
    AND deletion_unheld(m)
  ORDER BY m.received_at LIMIT 100;
$$;
CREATE FUNCTION authorize_purge(record_id uuid, expected_version integer, policy_version integer)
RETURNS boolean LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,public AS $$
DECLARE item messages;
BEGIN
  LOCK TABLE legal_holds IN SHARE MODE;
  SELECT * INTO item FROM messages WHERE id=record_id FOR UPDATE;
  PERFORM 1 FROM deletion_policy WHERE version=policy_version AND enabled FOR SHARE;
  IF NOT FOUND OR item.id IS NULL OR item.version IS DISTINCT FROM expected_version
    OR item.purge_policy IS DISTINCT FROM policy_version OR item.purge_after IS NULL
    OR item.purge_after>now() OR item.retain_until>now() OR NOT deletion_unheld(item) THEN RETURN false; END IF;
  INSERT INTO restore_tombstones VALUES(item.id,item.conversation_id,item.event_id,item.version,policy_version)
    ON CONFLICT ON CONSTRAINT restore_tombstones_pkey DO NOTHING;
  INSERT INTO deletion_log(record_id,event_id,conversation_id,version,policy_version,reason_code,action)
    VALUES(item.id,item.event_id,item.conversation_id,item.version,policy_version,'retention_elapsed','purge');
  DELETE FROM messages WHERE id=item.id;
  RETURN true;
END $$;
REVOKE ALL ON FUNCTION delete_eligible(uuid,integer,integer,text),purge_candidates(text),
  authorize_purge(uuid,integer,integer) FROM PUBLIC;
COMMIT;
