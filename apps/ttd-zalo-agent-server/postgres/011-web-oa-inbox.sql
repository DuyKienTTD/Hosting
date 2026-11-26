BEGIN;
CREATE TABLE web_oa_projection (
  scope text NOT NULL,
  event_id text NOT NULL,
  conversation_id uuid REFERENCES conversations ON DELETE CASCADE,
  target text NOT NULL,
  origin_id text,
  received_ms bigint NOT NULL,
  retained boolean NOT NULL DEFAULT false,
  PRIMARY KEY(scope,event_id)
);
CREATE INDEX web_oa_projection_thread ON web_oa_projection(conversation_id,received_ms DESC);
CREATE INDEX web_oa_projection_target ON web_oa_projection(target,origin_id,received_ms);
CREATE TABLE web_oa_replies (
  send_id text PRIMARY KEY REFERENCES send_log(id),
  conversation_id uuid NOT NULL REFERENCES conversations ON DELETE CASCADE
);
CREATE INDEX web_oa_replies_thread ON web_oa_replies(conversation_id);
GRANT SELECT,INSERT ON web_oa_projection,web_oa_replies TO data_runtime;
GRANT INSERT ON channel_identities TO data_runtime;
COMMIT;
