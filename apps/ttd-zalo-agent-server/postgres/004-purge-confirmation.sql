BEGIN;
DROP FUNCTION public.purge_message(uuid,integer,integer,text);
DROP FUNCTION purge_private.replay_tombstone(uuid,uuid,text,integer,integer,text);
DROP FUNCTION purge_private.verify(uuid,uuid,text,integer,integer,text);

CREATE TABLE purge_private.commits (
  purge_id uuid PRIMARY KEY,
  record_id uuid NOT NULL,
  conversation_id uuid NOT NULL,
  event_id text NOT NULL,
  version integer NOT NULL,
  policy_version integer NOT NULL,
  commit_xid xid8 NOT NULL,
  published boolean NOT NULL DEFAULT false
);

CREATE FUNCTION purge_private.proof(phase text, attempt uuid, record_id uuid, conversation_id uuid, event_id text,
  row_version integer, policy_version integer)
RETURNS text LANGUAGE sql STABLE SET search_path=pg_catalog,purge_private,pg_temp AS $$
  SELECT encode(hmac(convert_to(concat_ws('|','z4-tombstone-v2',phase,attempt,record_id,conversation_id,event_id,
      row_version,policy_version),'UTF8'),secret,'sha256'),'hex')
  FROM purge_private.signing_key WHERE slot;
$$;

CREATE FUNCTION public.purge_message(target_id uuid, expected_version integer, policy_version integer, attempt uuid, signature text)
RETURNS boolean LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,public,pg_temp AS $$
DECLARE item messages;
BEGIN
  PERFORM pg_advisory_xact_lock(hashtextextended(attempt::text,481));
  LOCK TABLE legal_holds IN SHARE MODE;
  SELECT * INTO item FROM messages WHERE id=target_id FOR UPDATE;
  PERFORM 1 FROM deletion_policy WHERE version=policy_version AND enabled FOR SHARE;
  IF NOT FOUND OR item.id IS NULL OR item.version IS DISTINCT FROM expected_version
    OR item.purge_policy IS DISTINCT FROM policy_version OR item.purge_after IS NULL
    OR item.purge_after>now() OR item.retain_until>now() OR NOT deletion_unheld(item) THEN RETURN false; END IF;
  -- A null signature acquires the policy/row locks without changing any data.
  IF signature IS NULL THEN RETURN true; END IF;
  IF signature IS DISTINCT FROM purge_private.proof('pending',attempt,item.id,item.conversation_id,item.event_id,item.version,policy_version) THEN RAISE EXCEPTION 'purge_receipt_required'; END IF;
  INSERT INTO restore_tombstones VALUES(item.id,item.conversation_id,item.event_id,item.version,policy_version)
    ON CONFLICT ON CONSTRAINT restore_tombstones_pkey DO NOTHING;
  INSERT INTO deletion_log(record_id,event_id,conversation_id,version,policy_version,reason_code,action)
    VALUES(item.id,item.event_id,item.conversation_id,item.version,policy_version,'retention_elapsed','purge');
  INSERT INTO purge_private.receipts VALUES(item.id,pg_current_xact_id());
  DELETE FROM messages WHERE id=item.id;
  DELETE FROM purge_private.receipts WHERE record_id=item.id;
  INSERT INTO purge_private.commits(purge_id,record_id,conversation_id,event_id,version,policy_version,commit_xid)
    VALUES(attempt,item.id,item.conversation_id,item.event_id,item.version,policy_version,pg_current_xact_id());
  RETURN true;
END $$;
REVOKE ALL ON FUNCTION public.purge_message(uuid,integer,integer,uuid,text) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION public.purge_message(uuid,integer,integer,uuid,text) TO data_worker;

CREATE FUNCTION public.committed_purges() RETURNS TABLE
  (purge_id uuid, id uuid, conversation_id uuid, event_id text, version integer, policy_version integer, proof text)
LANGUAGE sql SECURITY DEFINER SET search_path=pg_catalog,purge_private,pg_temp AS $$
  SELECT c.purge_id,c.record_id,c.conversation_id,c.event_id,c.version,c.policy_version,
    purge_private.proof('confirmed',c.purge_id,c.record_id,c.conversation_id,c.event_id,c.version,c.policy_version)
  FROM purge_private.commits c
  WHERE NOT c.published AND c.commit_xid IS DISTINCT FROM pg_current_xact_id_if_assigned()
  ORDER BY c.purge_id LIMIT 100;
$$;
CREATE FUNCTION public.purge_published(attempt uuid, signature text) RETURNS void
LANGUAGE sql SECURITY DEFINER SET search_path=pg_catalog,purge_private,pg_temp AS $$
  UPDATE purge_private.commits SET published=true WHERE purge_id=attempt
    AND commit_xid IS DISTINCT FROM pg_current_xact_id_if_assigned()
    AND signature=purge_private.proof('published',purge_id,record_id,conversation_id,event_id,version,policy_version);
$$;
CREATE FUNCTION public.pending_purge_discardable(attempt uuid) RETURNS boolean
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,purge_private,pg_temp AS $$
BEGIN
  PERFORM pg_advisory_xact_lock(hashtextextended(attempt::text,481));
  RETURN NOT EXISTS (SELECT 1 FROM purge_private.commits WHERE purge_id=attempt AND NOT published);
END $$;
REVOKE ALL ON FUNCTION public.committed_purges(),public.purge_published(uuid,text),
  public.pending_purge_discardable(uuid) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION public.committed_purges(),public.purge_published(uuid,text),
  public.pending_purge_discardable(uuid) TO data_worker;

CREATE FUNCTION purge_private.replay_tombstone(attempt uuid, target_id uuid, thread_id uuid, event_key text,
  row_version integer, policy_version integer, signature text)
RETURNS void LANGUAGE plpgsql SET search_path=pg_catalog,public,pg_temp AS $$
DECLARE item messages;
BEGIN
  IF signature IS NULL OR signature IS DISTINCT FROM
    purge_private.proof('confirmed',attempt,target_id,thread_id,event_key,row_version,policy_version)
    THEN RAISE EXCEPTION 'purge_confirmation_required'; END IF;
  LOCK TABLE legal_holds IN SHARE MODE;
  SELECT * INTO item FROM messages WHERE id=target_id FOR UPDATE;
  IF EXISTS (SELECT 1 FROM legal_holds WHERE message_id=target_id AND released_at IS NULL)
     OR EXISTS (SELECT 1 FROM legal_holds h JOIN conversations c ON c.customer_id=h.customer_id
       WHERE c.id=thread_id AND h.released_at IS NULL)
     OR EXISTS (SELECT 1 FROM messages WHERE conversation_id=thread_id AND event_id=event_key AND id<>target_id)
     OR (item.id IS NOT NULL AND (item.conversation_id<>thread_id OR item.event_id<>event_key
       OR item.version>row_version OR NOT deletion_unheld(item))) THEN
    INSERT INTO audit_log(actor,action,record_id) VALUES('restore','purge_blocked',target_id);
    RAISE WARNING 'restore_tombstone_blocked %',target_id;
    RETURN;
  END IF;
  INSERT INTO restore_tombstones VALUES(target_id,thread_id,event_key,row_version,policy_version)
    ON CONFLICT ON CONSTRAINT restore_tombstones_pkey DO NOTHING;
  INSERT INTO deletion_log(record_id,conversation_id,event_id,version,policy_version,reason_code,action)
    VALUES(target_id,thread_id,event_key,row_version,policy_version,'retention_elapsed','restore_tombstone')
    ON CONFLICT DO NOTHING;
  IF item.id IS NOT NULL THEN
    INSERT INTO purge_private.receipts VALUES(target_id,pg_current_xact_id());
    DELETE FROM messages WHERE id=target_id;
    DELETE FROM purge_private.receipts WHERE record_id=target_id;
  END IF;
END $$;
CREATE FUNCTION purge_private.reconcile_restore_pending(attempt uuid, target_id uuid, thread_id uuid, event_key text,
  row_version integer, policy_version integer)
RETURNS void LANGUAGE plpgsql SET search_path=pg_catalog,public,pg_temp AS $$
BEGIN
  IF EXISTS (SELECT 1 FROM purge_private.commits c WHERE c.purge_id=attempt
    AND c.record_id=target_id AND c.conversation_id=thread_id AND c.event_id=event_key
    AND c.version=row_version AND c.policy_version=reconcile_restore_pending.policy_version) THEN
    INSERT INTO audit_log(actor,action,record_id) VALUES('restore','pending_awaits_confirmation',target_id);
    RAISE WARNING 'pending_purge_awaits_confirmation %',attempt;
  ELSE
    INSERT INTO audit_log(actor,action,record_id) VALUES('restore','pending_ignored_no_commit',target_id);
    RAISE WARNING 'pending_purge_ignored_no_commit %',attempt;
  END IF;
END $$;
REVOKE ALL ON ALL FUNCTIONS IN SCHEMA purge_private FROM PUBLIC;
COMMIT;
