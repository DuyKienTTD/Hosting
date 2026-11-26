BEGIN;
ALTER TABLE web_reply_drafts DROP CONSTRAINT ai_draft_has_message;
ALTER TABLE web_reply_drafts ADD CONSTRAINT ai_draft_has_message CHECK (
  (ai_state IS NULL AND ai_message_id IS NULL)
  OR (ai_state IS NOT NULL AND ai_message_id IS NOT NULL)
  OR (ai_state IS NOT DISTINCT FROM 'needs_human' AND ai_reason IS NOT DISTINCT FROM 'consent'
      AND ai_message_id IS NULL AND body = '')
);
COMMIT;
