CREATE TABLE IF NOT EXISTS coordination_room (
  singleton boolean PRIMARY KEY CHECK (singleton),
  state jsonb NOT NULL
);

CREATE TABLE IF NOT EXISTS coordination_applied_rename (
  ticket_id uuid NOT NULL,
  proposal_index integer NOT NULL,
  PRIMARY KEY (ticket_id, proposal_index)
);

GRANT SELECT, INSERT, UPDATE(state) ON coordination_room TO data_app;
GRANT INSERT ON coordination_applied_rename TO data_app;
