BEGIN;
CREATE FUNCTION public.web_create_operator(
  actor uuid, login text, display_label text, operator_role text, password_verifier text
) RETURNS uuid LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog AS $$
DECLARE created uuid;
BEGIN
  IF actor IS NULL THEN
    LOCK TABLE public.web_operators IN SHARE ROW EXCLUSIVE MODE;
    IF operator_role <> 'owner' OR EXISTS (SELECT 1 FROM public.web_operators) THEN RETURN NULL; END IF;
  ELSE
    IF operator_role NOT IN ('sales','support') THEN RETURN NULL; END IF;
    PERFORM 1 FROM public.web_operators WHERE id=actor AND role='owner' AND enabled FOR SHARE;
    IF NOT FOUND THEN RETURN NULL; END IF;
  END IF;
  INSERT INTO public.web_operators(account,label,role,verifier)
    VALUES(login,display_label,operator_role,password_verifier)
    ON CONFLICT(account) DO NOTHING RETURNING id INTO created;
  RETURN created;
END $$;
REVOKE ALL ON FUNCTION public.web_create_operator(uuid,text,text,text,text) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION public.web_create_operator(uuid,text,text,text,text) TO data_runtime;
COMMIT;
