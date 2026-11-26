BEGIN;
CREATE FUNCTION purge_private.origin() RETURNS text
LANGUAGE sql STABLE SET search_path=pg_catalog,pg_temp AS $$
  SELECT system_identifier::text || ':' || (SELECT oid::text FROM pg_database WHERE datname=current_database())
  FROM pg_control_system();
$$;
CREATE FUNCTION public.purge_intent() RETURNS TABLE (origin text,xid text)
LANGUAGE sql SECURITY DEFINER SET search_path=pg_catalog,purge_private,pg_temp AS $$
  SELECT purge_private.origin(),pg_current_xact_id()::text;
$$;
CREATE FUNCTION public.purge_recovery_evidence(attempt uuid, target_id uuid, thread_id uuid, event_key text,
  row_version integer, policy_version integer, origin text, xid text, intent text)
RETURNS TABLE (status text,proof text)
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,purge_private,pg_temp AS $$
BEGIN
  IF EXISTS (SELECT 1 FROM commits c WHERE c.purge_id=attempt AND c.record_id=target_id
    AND c.conversation_id=thread_id AND c.event_id=event_key AND c.version=row_version
    AND c.policy_version=purge_recovery_evidence.policy_version
    AND c.commit_xid IS DISTINCT FROM pg_current_xact_id_if_assigned()) THEN
    RETURN QUERY SELECT 'confirmed'::text,purge_private.proof('confirmed',attempt,target_id,thread_id,event_key,row_version,policy_version);
  ELSIF origin=purge_private.origin() AND xid ~ '^[0-9]{1,20}$'
    AND intent=purge_private.proof('intent:'||origin||':'||xid,attempt,target_id,thread_id,event_key,row_version,policy_version)
    AND pg_xact_status(xid::xid8)='aborted' THEN
    RETURN QUERY SELECT 'rolled_back'::text,purge_private.proof('rolled_back',attempt,target_id,thread_id,event_key,row_version,policy_version);
  END IF;
END $$;
CREATE FUNCTION public.purge_restore_held(target_id uuid,thread_id uuid) RETURNS boolean
LANGUAGE sql SECURITY DEFINER SET search_path=pg_catalog,public,pg_temp AS $$
  SELECT EXISTS (SELECT 1 FROM legal_holds WHERE message_id=target_id AND released_at IS NULL)
    OR EXISTS (SELECT 1 FROM legal_holds h JOIN conversations c ON c.customer_id=h.customer_id
      WHERE c.id=thread_id AND h.released_at IS NULL);
$$;
REVOKE ALL ON FUNCTION purge_private.origin(),public.purge_intent(),
  public.purge_recovery_evidence(uuid,uuid,uuid,text,integer,integer,text,text,text),
  public.purge_restore_held(uuid,uuid) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION public.purge_intent(),
  public.purge_recovery_evidence(uuid,uuid,uuid,text,integer,integer,text,text,text) TO data_worker;
-- Missing rows are not rollback evidence and must not be garbage-collected.
CREATE OR REPLACE FUNCTION public.pending_purge_discardable(attempt uuid) RETURNS boolean
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,purge_private,pg_temp AS $$
BEGIN
  PERFORM pg_advisory_xact_lock(hashtextextended(attempt::text,481));
  RETURN EXISTS (SELECT 1 FROM commits WHERE purge_id=attempt AND published);
END $$;
CREATE TABLE purge_private.restore_gate (slot boolean PRIMARY KEY CHECK(slot), reconciled boolean NOT NULL);
CREATE TABLE purge_private.restore_unknown (
  purge_id uuid PRIMARY KEY, record_id uuid NOT NULL,
  version integer NOT NULL, policy_version integer NOT NULL
);
CREATE FUNCTION purge_private.quarantine_restore(attempt uuid,target_id uuid,revision integer,policy integer)
RETURNS void LANGUAGE plpgsql SET search_path=pg_catalog,public,pg_temp AS $$
BEGIN
  INSERT INTO purge_private.restore_unknown VALUES(attempt,target_id,revision,policy)
    ON CONFLICT DO NOTHING;
  UPDATE messages SET purge_after='infinity',purge_policy=policy WHERE id=target_id;
  INSERT INTO audit_log(actor,action,record_id) VALUES('restore','purge_unverified',target_id);
  RAISE WARNING 'restore_purge_unverified %',attempt;
END $$;
CREATE FUNCTION purge_private.resolve_restore(attempt uuid, decision text) RETURNS void
LANGUAGE plpgsql SET search_path=pg_catalog,public,pg_temp AS $$
DECLARE pending purge_private.restore_unknown; item messages;
BEGIN
  IF decision NOT IN ('delete','restore') OR decision IS NULL THEN RAISE EXCEPTION 'invalid_restore_decision'; END IF;
  LOCK TABLE legal_holds IN SHARE MODE;
  SELECT * INTO STRICT pending FROM purge_private.restore_unknown WHERE purge_id=attempt FOR UPDATE;
  SELECT * INTO item FROM messages WHERE id=pending.record_id FOR UPDATE;
  IF decision='delete' AND (EXISTS (SELECT 1 FROM legal_holds WHERE message_id=pending.record_id AND released_at IS NULL)
    OR (item.id IS NOT NULL AND (item.version>pending.version OR NOT deletion_unheld(item)))) THEN
    RAISE EXCEPTION 'restore_delete_blocked';
  END IF;
  IF decision='delete' AND item.id IS NOT NULL THEN
    INSERT INTO restore_tombstones VALUES(item.id,item.conversation_id,item.event_id,item.version,pending.policy_version)
      ON CONFLICT ON CONSTRAINT restore_tombstones_pkey DO NOTHING;
    INSERT INTO purge_private.receipts VALUES(item.id,pg_current_xact_id());
    DELETE FROM messages WHERE id=item.id;
    DELETE FROM purge_private.receipts WHERE record_id=item.id;
  END IF;
  DELETE FROM purge_private.restore_unknown WHERE purge_id=attempt;
  IF decision='restore' AND NOT EXISTS (SELECT 1 FROM purge_private.restore_unknown WHERE record_id=pending.record_id) THEN
    UPDATE messages SET purge_after=NULL,purge_policy=NULL WHERE id=pending.record_id;
  END IF;
  INSERT INTO audit_log(actor,action,record_id) VALUES(session_user,'restore_owner_'||decision,pending.record_id);
END $$;
CREATE FUNCTION purge_private.promote_restore() RETURNS void
LANGUAGE plpgsql SET search_path=pg_catalog,public,pg_temp AS $$
BEGIN
  LOCK TABLE purge_private.restore_gate,purge_private.restore_unknown IN EXCLUSIVE MODE;
  IF NOT EXISTS (SELECT 1 FROM purge_private.restore_gate WHERE slot AND reconciled)
    OR EXISTS (SELECT 1 FROM purge_private.restore_unknown) THEN
    RAISE EXCEPTION 'restore_promotion_blocked';
  END IF;
  EXECUTE format('GRANT CONNECT ON DATABASE %I TO data_worker,data_runtime,data_app',current_database());
  INSERT INTO audit_log(actor,action) VALUES(session_user,'restore_promoted');
END $$;
REVOKE ALL ON ALL FUNCTIONS IN SCHEMA purge_private FROM PUBLIC;
COMMIT;
