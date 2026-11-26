BEGIN;
CREATE SCHEMA purge_private;
CREATE EXTENSION IF NOT EXISTS pgcrypto WITH SCHEMA purge_private;
CREATE TABLE purge_private.signing_key (
  slot boolean PRIMARY KEY CHECK(slot),
  secret bytea NOT NULL CHECK(octet_length(secret)=32)
);
CREATE TABLE purge_private.receipts (
  record_id uuid PRIMARY KEY,
  transaction_id xid8 NOT NULL
);
DROP FUNCTION public.authorize_purge(uuid,integer,integer);

CREATE FUNCTION purge_private.verify(record_id uuid, conversation_id uuid, event_id text,
  row_version integer, policy_version integer, signature text)
RETURNS boolean LANGUAGE sql STABLE SET search_path=pg_catalog,purge_private AS $$
  SELECT coalesce(signature ~ '^[a-f0-9]{64}$' AND
    encode(hmac(convert_to(concat_ws('|','z4-tombstone-v1',record_id,conversation_id,event_id,
      row_version,policy_version),'UTF8'),secret,'sha256'),'hex')=signature,false)
  FROM signing_key WHERE slot;
$$;

CREATE FUNCTION purge_private.require_receipt() RETURNS trigger
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,purge_private AS $$
BEGIN
  IF TG_OP='TRUNCATE' THEN RAISE EXCEPTION 'purge_receipt_required'; END IF;
  IF NOT EXISTS (SELECT 1 FROM receipts WHERE record_id=OLD.id AND transaction_id=pg_current_xact_id()) THEN
    RAISE EXCEPTION 'purge_receipt_required';
  END IF;
  RETURN OLD;
END $$;
CREATE TRIGGER messages_require_receipt BEFORE DELETE ON public.messages
  FOR EACH ROW EXECUTE FUNCTION purge_private.require_receipt();
CREATE TRIGGER messages_forbid_truncate BEFORE TRUNCATE ON public.messages
  FOR EACH STATEMENT EXECUTE FUNCTION purge_private.require_receipt();

CREATE FUNCTION public.purge_message(target_id uuid, expected_version integer, policy_version integer, signature text)
RETURNS boolean LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,public AS $$
DECLARE item messages;
BEGIN
  LOCK TABLE legal_holds IN SHARE MODE;
  SELECT * INTO item FROM messages WHERE id=target_id FOR UPDATE;
  PERFORM 1 FROM deletion_policy WHERE version=policy_version AND enabled FOR SHARE;
  IF NOT FOUND OR item.id IS NULL OR item.version IS DISTINCT FROM expected_version
    OR item.purge_policy IS DISTINCT FROM policy_version OR item.purge_after IS NULL
    OR item.purge_after>now() OR item.retain_until>now() OR NOT deletion_unheld(item) THEN RETURN false; END IF;
  -- A null signature acquires the policy/row locks without changing any data.
  IF signature IS NULL THEN RETURN true; END IF;
  IF purge_private.verify(item.id,item.conversation_id,item.event_id,item.version,policy_version,signature)
    IS DISTINCT FROM true THEN RAISE EXCEPTION 'purge_receipt_required'; END IF;
  INSERT INTO restore_tombstones VALUES(item.id,item.conversation_id,item.event_id,item.version,policy_version)
    ON CONFLICT ON CONSTRAINT restore_tombstones_pkey DO NOTHING;
  INSERT INTO deletion_log(record_id,event_id,conversation_id,version,policy_version,reason_code,action)
    VALUES(item.id,item.event_id,item.conversation_id,item.version,policy_version,'retention_elapsed','purge');
  INSERT INTO purge_private.receipts VALUES(item.id,pg_current_xact_id());
  DELETE FROM messages WHERE id=item.id;
  DELETE FROM purge_private.receipts WHERE record_id=item.id;
  RETURN true;
END $$;
REVOKE ALL ON FUNCTION public.purge_message(uuid,integer,integer,text) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION public.purge_message(uuid,integer,integer,text) TO data_worker;
REVOKE ALL ON FUNCTION public.deletion_unheld(public.messages) FROM PUBLIC;

-- Exclusive to the restore operator. The replay script signs only documents
-- read from the independent archive while all serving roles are disconnected.
CREATE FUNCTION purge_private.replay_tombstone(target_id uuid, thread_id uuid, event_key text,
  row_version integer, policy_version integer, signature text)
RETURNS void LANGUAGE plpgsql SET search_path=pg_catalog,public AS $$
BEGIN
  IF purge_private.verify(target_id,thread_id,event_key,row_version,policy_version,signature)
    IS DISTINCT FROM true THEN RAISE EXCEPTION 'purge_receipt_required'; END IF;
  INSERT INTO restore_tombstones VALUES(target_id,thread_id,event_key,row_version,policy_version)
    ON CONFLICT ON CONSTRAINT restore_tombstones_pkey DO NOTHING;
  INSERT INTO deletion_log(record_id,conversation_id,event_id,version,policy_version,reason_code,action)
    VALUES(target_id,thread_id,event_key,row_version,policy_version,'retention_elapsed','restore_tombstone')
    ON CONFLICT DO NOTHING;
  INSERT INTO purge_private.receipts
    SELECT id,pg_current_xact_id() FROM messages WHERE id=target_id OR (conversation_id=thread_id AND event_id=event_key);
  DELETE FROM messages WHERE id IN (SELECT record_id FROM purge_private.receipts WHERE transaction_id=pg_current_xact_id());
  DELETE FROM purge_private.receipts WHERE transaction_id=pg_current_xact_id();
END $$;
REVOKE ALL ON SCHEMA purge_private FROM PUBLIC;
REVOKE ALL ON ALL FUNCTIONS IN SCHEMA purge_private FROM PUBLIC;
COMMIT;
