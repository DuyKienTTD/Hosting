BEGIN;
CREATE TABLE settings(key text PRIMARY KEY,value bigint NOT NULL);
INSERT INTO settings VALUES ('global',1),('ADS_ENABLED',0);
CREATE TABLE runtime_identity(slot integer PRIMARY KEY CHECK(slot=1),digest text NOT NULL);
CREATE TABLE contact(target text PRIMARY KEY, revision bigint NOT NULL DEFAULT 0,
  expires bigint NOT NULL DEFAULT 0, retain integer NOT NULL DEFAULT 0, respond integer NOT NULL DEFAULT 0,
  send integer NOT NULL DEFAULT 0, takeover integer NOT NULL DEFAULT 0, ads integer NOT NULL DEFAULT 0,
  opted_out integer NOT NULL DEFAULT 0, accepted integer NOT NULL DEFAULT 0, interest bigint NOT NULL DEFAULT 0,
  ads_paused_review text);
CREATE TABLE runtime_customer(target text PRIMARY KEY REFERENCES contact, customer_id uuid NOT NULL UNIQUE REFERENCES customers);
ALTER TABLE consents ADD COLUMN valid_until_ms bigint;
ALTER TABLE conversations ADD COLUMN runtime_thread text,
  ADD UNIQUE (customer_id,channel,runtime_thread);
-- Proof-backed grants use the newest event in each purpose. A grant with no
-- expiration is deliberately inactive for runtime traffic.
CREATE VIEW runtime_contact_policy AS
  SELECT c.target, c.revision, c.expires, c.takeover, c.accepted,c.interest,
         CASE WHEN r.withdrawn=false AND r.valid_until_ms IS NOT NULL THEN 1 ELSE 0 END AS retain,
         CASE WHEN p.withdrawn=false AND p.valid_until_ms IS NOT NULL THEN 1 ELSE 0 END AS respond,
         CASE WHEN s.withdrawn=false AND s.valid_until_ms IS NOT NULL THEN 1 ELSE 0 END AS send,
         CASE WHEN status.state='active' AND a.withdrawn=false AND a.valid_until_ms IS NOT NULL THEN 1 ELSE 0 END AS ads,
         r.valid_until_ms AS retain_until, p.valid_until_ms AS respond_until,
         s.valid_until_ms AS send_until, a.valid_until_ms AS ads_until,
         CASE WHEN status.state='opted_out' THEN 1 ELSE 0 END AS opted_out,
         CASE WHEN status.state='ads_paused_review' THEN coalesce(c.ads_paused_review,'pending') END AS ads_paused_review
  FROM contact c LEFT JOIN runtime_customer x USING(target)
  LEFT JOIN ad_status status USING(customer_id)
  LEFT JOIN LATERAL (SELECT withdrawn,valid_until_ms FROM consents WHERE customer_id=x.customer_id AND purpose='retain' ORDER BY occurred_at DESC,id DESC LIMIT 1) r ON true
  LEFT JOIN LATERAL (SELECT withdrawn,valid_until_ms FROM consents WHERE customer_id=x.customer_id AND purpose='respond' ORDER BY occurred_at DESC,id DESC LIMIT 1) p ON true
  LEFT JOIN LATERAL (SELECT withdrawn,valid_until_ms FROM consents WHERE customer_id=x.customer_id AND purpose='send' ORDER BY occurred_at DESC,id DESC LIMIT 1) s ON true
  LEFT JOIN LATERAL (SELECT withdrawn,valid_until_ms FROM consents WHERE customer_id=x.customer_id AND purpose='ads' ORDER BY occurred_at DESC,id DESC LIMIT 1) a ON true;
ALTER TABLE send_log RENAME COLUMN idempotency_key TO id;
ALTER TABLE send_log ALTER COLUMN customer_id DROP NOT NULL;
ALTER TABLE send_log ADD COLUMN target text, ADD COLUMN agent text, ADD COLUMN kind text, ADD COLUMN at bigint;
CREATE INDEX runtime_send_kind ON send_log(kind,at);
CREATE INDEX runtime_send_target ON send_log(target,kind,at);

CREATE TABLE catalogue(id text PRIMARY KEY,sku text,kind text NOT NULL,title text NOT NULL,
  summary text NOT NULL,version text NOT NULL,effective text NOT NULL,until text,
  origin text NOT NULL,amount bigint,unit text);
CREATE INDEX catalogue_runtime_fts ON catalogue USING gin
  (to_tsvector('simple',coalesce(sku,'')||' '||title||' '||summary));
CREATE TABLE inbound(id text PRIMARY KEY,target text NOT NULL,received bigint NOT NULL);
CREATE TABLE customer_field(id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,target text NOT NULL,
  source text NOT NULL REFERENCES inbound,kind text NOT NULL,value text NOT NULL,created bigint NOT NULL,
  UNIQUE(target,source,kind,value));
CREATE INDEX runtime_customer_fields ON customer_field(target,kind,id);
CREATE TABLE failures(at bigint NOT NULL);
CREATE TABLE ledger(id text PRIMARY KEY,cycle text NOT NULL,date text NOT NULL,model text NOT NULL,
  amount bigint NOT NULL,state text NOT NULL,batch text,input bigint,output bigint,cache_write bigint,
  cache_read bigint,settled_cycle text,provider text NOT NULL DEFAULT 'anthropic',
  rate_multiplier double precision NOT NULL DEFAULT 1,input_bound bigint);
CREATE INDEX runtime_ledger_cycle ON ledger(cycle,date);
CREATE TABLE jobs(id text PRIMARY KEY,kind text NOT NULL,target text,status text NOT NULL,
  created bigint NOT NULL,revision bigint,epoch bigint,body text);
CREATE TABLE notices(key text PRIMARY KEY,at bigint NOT NULL,body text NOT NULL);
CREATE TABLE adapter_inbox(seq bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,scope text NOT NULL,
  event text NOT NULL,stream text NOT NULL,sender text NOT NULL,expires bigint NOT NULL,sealed text NOT NULL,
  UNIQUE(scope,event));
CREATE INDEX runtime_inbox_page ON adapter_inbox(scope,stream,seq);
CREATE TABLE adapter_writes(scope text NOT NULL,key text NOT NULL,fingerprint text NOT NULL,result text,PRIMARY KEY(scope,key));
CREATE TABLE adapter_throttle(scope text PRIMARY KEY,until bigint NOT NULL);

CREATE FUNCTION runtime_policy_lock() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
  PERFORM pg_advisory_xact_lock(76425161);
  RETURN NULL;
END $$;
CREATE TRIGGER runtime_settings_lock BEFORE INSERT OR UPDATE OR DELETE ON settings
  FOR EACH STATEMENT EXECUTE FUNCTION runtime_policy_lock();
CREATE TRIGGER runtime_consents_lock BEFORE INSERT ON consents
  FOR EACH STATEMENT EXECUTE FUNCTION runtime_policy_lock();
CREATE TRIGGER runtime_ads_lock BEFORE INSERT OR UPDATE OR DELETE ON ad_status
  FOR EACH STATEMENT EXECUTE FUNCTION runtime_policy_lock();
CREATE TRIGGER runtime_sends_lock BEFORE INSERT OR UPDATE OR DELETE ON send_log
  FOR EACH STATEMENT EXECUTE FUNCTION runtime_policy_lock();
CREATE TRIGGER runtime_ledger_lock BEFORE INSERT OR UPDATE OR DELETE ON ledger
  FOR EACH STATEMENT EXECUTE FUNCTION runtime_policy_lock();
CREATE FUNCTION runtime_revise_policy() RETURNS trigger LANGUAGE plpgsql SECURITY DEFINER
  SET search_path FROM CURRENT AS $$
BEGIN
  UPDATE contact SET revision=revision+1 WHERE target IN
    (SELECT target FROM runtime_customer WHERE customer_id=coalesce(NEW.customer_id,OLD.customer_id));
  RETURN NULL;
END $$;
CREATE TRIGGER runtime_consent_revision AFTER INSERT ON consents
  FOR EACH ROW EXECUTE FUNCTION runtime_revise_policy();
COMMIT;
