BEGIN;
ALTER TABLE ledger ADD COLUMN agent_role text
  CHECK (agent_role IN ('router','support','sales','crm','report','campaign','community','listen'));
CREATE INDEX ledger_agent_daily ON ledger(date,agent_role) WHERE agent_role IS NOT NULL;
ALTER TABLE web_task_agents DROP CONSTRAINT web_task_agents_agent_check;
ALTER TABLE web_task_agents ADD CONSTRAINT web_task_agents_agent_check
  CHECK (agent IN ('Claude','A1','A2','router','support','sales','crm','report','campaign','community','listen'));
CREATE TABLE web_agent_runs (
  task_id uuid PRIMARY KEY REFERENCES web_task_agents(task_id),
  started_at timestamptz,
  result text,
  reviewed_by uuid REFERENCES web_operators,
  review_decision text CHECK (review_decision IN ('accept','dismiss')),
  reviewed_at timestamptz
);
GRANT SELECT,INSERT ON web_agent_runs TO data_runtime;
GRANT UPDATE(started_at,result,reviewed_by,review_decision,reviewed_at) ON web_agent_runs TO data_runtime;
GRANT UPDATE(state) ON tasks TO data_runtime;
COMMIT;
