\getenv runtime_password DATA_RUNTIME_PASSWORD
SELECT format('CREATE ROLE data_runtime LOGIN PASSWORD %L', :'runtime_password') WHERE NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname='data_runtime') \gexec
GRANT SELECT,INSERT,UPDATE ON settings,contact TO data_runtime;
GRANT SELECT,INSERT ON runtime_identity,runtime_customer,customers TO data_runtime;
GRANT SELECT,INSERT ON consents TO data_runtime;
GRANT SELECT,INSERT,UPDATE ON ad_status TO data_runtime;
GRANT SELECT ON runtime_contact_policy TO data_runtime;
GRANT SELECT,INSERT,UPDATE ON send_log TO data_runtime;
GRANT SELECT,INSERT ON catalogue TO data_runtime;
GRANT SELECT,INSERT ON conversations TO data_runtime;
GRANT UPDATE(runtime_thread) ON conversations TO data_runtime;
GRANT SELECT(id,conversation_id,event_id),INSERT(conversation_id,event_id,body,received_at,retain_until) ON messages TO data_runtime;
GRANT SELECT ON restore_tombstones TO data_runtime;
GRANT SELECT,INSERT,UPDATE ON inbound TO data_runtime;
GRANT SELECT,INSERT,DELETE ON customer_field TO data_runtime;
GRANT SELECT,INSERT,DELETE ON failures TO data_runtime;
GRANT SELECT,INSERT,UPDATE ON ledger,notices TO data_runtime;
GRANT SELECT,INSERT,UPDATE,DELETE ON jobs,adapter_inbox,adapter_writes TO data_runtime;
GRANT SELECT,INSERT,UPDATE ON adapter_throttle TO data_runtime;
