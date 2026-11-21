# Hermes auxiliary GATE A — mock only

This directory is the public, secret-free source for `TTD-HERMES-GATE-A-001`.
It deploys a stock Hermes `0.22.5` auxiliary API server, authenticated bridge,
pre-dispatch inference guard and private provider fixture.

Safety properties:

- Every GATE A network is Docker `internal=true`; no service publishes a host
  port. Hermes cannot reach the existing provider egress proxy or the Internet.
- The guard accepts only `/v1/responses`, exact `gpt-6-luna`, no tool fields and
  a strict full-request byte upper bound of 4,000. It injects
  `max_output_tokens=600` before mock dispatch.
- The real Level 2 ledger is mounted read-only. Guard startup and every request
  require its kill switch to remain on; the ledger is never reset or reserved
  for mock traffic.
- The only new secret values are `API_SERVER_KEY` and the guard service token.
  They are generated on the VPS and never enter this repository. The existing
  P0 webhook bearer is copied to a root-only runtime file without rotation.
- Production n8n/Hermes volumes, configuration, credentials and networks are
  not mounted or changed.

`rollback.sh` removes only GATE A services/networks, restores the previous
sandbox workflow and starts the previous sandbox reasoner. It does not touch
production. Mock PASS is not paid Hermes E2E evidence and does not authorize
GATE B.
