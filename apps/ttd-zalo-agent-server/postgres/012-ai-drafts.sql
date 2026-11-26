BEGIN;
ALTER TABLE web_reply_drafts
  ADD COLUMN ai_message_id uuid REFERENCES messages ON DELETE CASCADE,
  ADD COLUMN ai_state text CHECK (ai_state IN ('pending','generating','ready','needs_human','approved')),
  ADD COLUMN ai_intent text CHECK (ai_intent IN ('price','technical','complaint','other')),
  ADD COLUMN ai_reason text CHECK (ai_reason IN ('mock','budget','consent','unavailable','no_knowledge')),
  ADD COLUMN ai_source_ids jsonb NOT NULL DEFAULT '[]'::jsonb,
  ADD COLUMN ai_started_at timestamptz,
  ADD COLUMN ai_approved_by uuid REFERENCES web_operators,
  ADD COLUMN ai_approved_at timestamptz,
  ADD CONSTRAINT ai_draft_has_message CHECK ((ai_state IS NULL) = (ai_message_id IS NULL));
CREATE INDEX ai_draft_conversation ON web_reply_drafts(conversation_id) WHERE ai_state IS NOT NULL;
GRANT UPDATE(ai_state,ai_intent,ai_reason,ai_source_ids,ai_started_at,ai_approved_by,ai_approved_at) ON web_reply_drafts TO data_runtime;
COMMIT;
