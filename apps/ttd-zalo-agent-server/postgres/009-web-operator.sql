BEGIN;
CREATE TABLE web_operators (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  account text NOT NULL UNIQUE,
  label text NOT NULL,
  role text NOT NULL CHECK (role IN ('owner','sales','support','a0')),
  verifier text NOT NULL CHECK (verifier ~ '^[a-f0-9]{32}:[a-f0-9]{128}$'),
  enabled boolean NOT NULL DEFAULT true
);
CREATE TABLE web_sessions (
  digest text PRIMARY KEY,
  operator_id uuid NOT NULL REFERENCES web_operators ON DELETE CASCADE,
  expires_at timestamptz NOT NULL
);
CREATE INDEX web_session_expiry ON web_sessions(expires_at);
CREATE TABLE web_approved_prices (
  catalogue_id text NOT NULL REFERENCES catalogue,
  price_list text NOT NULL,
  millimetres_per_bar integer NOT NULL CHECK (millimetres_per_bar BETWEEN 1 AND 100000),
  bars_per_set integer NOT NULL CHECK (bars_per_set BETWEEN 1 AND 1000),
  vnd_per_metre integer NOT NULL CHECK (vnd_per_metre > 0),
  approved_at timestamptz NOT NULL DEFAULT clock_timestamp(),
  revoked_at timestamptz,
  PRIMARY KEY (catalogue_id,price_list)
);
CREATE UNIQUE INDEX web_active_price ON web_approved_prices(catalogue_id) WHERE revoked_at IS NULL;
CREATE TABLE web_quotes (
  id text PRIMARY KEY,
  send_key text,
  operator_id uuid NOT NULL REFERENCES web_operators,
  customer_id uuid NOT NULL REFERENCES customers,
  catalogue_id text NOT NULL,
  price_list text NOT NULL,
  unit text NOT NULL CHECK (unit IN ('metre','bar','set')),
  quantity numeric NOT NULL CHECK (quantity > 0),
  total_mm bigint NOT NULL CHECK (total_mm > 0),
  total_vnd bigint NOT NULL CHECK (total_vnd > 0),
  created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
  FOREIGN KEY(catalogue_id,price_list) REFERENCES web_approved_prices
);
CREATE TABLE web_room_messages (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  operator_id uuid NOT NULL REFERENCES web_operators,
  body text NOT NULL CHECK (length(body) BETWEEN 1 AND 1000),
  created_at timestamptz NOT NULL DEFAULT clock_timestamp()
);
CREATE TABLE web_task_agents (
  task_id uuid PRIMARY KEY REFERENCES tasks,
  agent text NOT NULL CHECK (agent IN ('Claude','A1','A2'))
);
CREATE TABLE web_deletion_requests (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id uuid NOT NULL REFERENCES customers,
  operator_id uuid NOT NULL REFERENCES web_operators,
  reason text NOT NULL CHECK (length(reason) BETWEEN 1 AND 500),
  created_at timestamptz NOT NULL DEFAULT clock_timestamp()
);
CREATE TABLE web_reply_drafts (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  conversation_id uuid NOT NULL REFERENCES conversations,
  inbound_id text NOT NULL REFERENCES inbound,
  body text NOT NULL,
  revision integer NOT NULL DEFAULT 1,
  delivery text NOT NULL DEFAULT 'draft' CHECK (delivery IN ('draft','queued','sent','blocked','unknown_delivery')),
  UNIQUE(conversation_id,inbound_id)
);
GRANT SELECT ON web_operators, web_approved_prices, channel_identities, visible_messages TO data_runtime;
GRANT SELECT,INSERT,DELETE ON web_sessions TO data_runtime;
GRANT SELECT,INSERT ON web_quotes,web_room_messages,web_task_agents,web_deletion_requests TO data_runtime;
GRANT SELECT,INSERT ON tasks TO data_runtime;
GRANT SELECT,INSERT,UPDATE(revision,delivery,body) ON web_reply_drafts TO data_runtime;
COMMIT;
