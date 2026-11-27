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

## One-shot mock rehearsal

Use `compose.mock-one-shot.yaml` with a disposable ledger copy. Pass that copy
and the reviewed fake Hermes request JSON to `prepare_mock_permit.py`. Review
the request before staging the permit. Any change to the final bytes, including
dynamic Hermes request fields, requires a new rehearsal. Run
`python3 mock_contract_test.py` on Linux to verify the guard and mock over
loopback. The test uses temporary state and does not need Docker or secrets.

The mock ledger keeps the reservation after a response or a timeout. Validated
usage is recorded for comparison with the pricing formula. Incomplete transport
leaves the outcome unknown and the permit consumed. The 4,000-byte mock limit
does not measure provider formatting tokens.

## H4 owner-entered provider credential

`owner_key_input.py` is a terminal-only, no-echo interface for the project
owner. It opens no listener and makes no provider request. On the VPS it stores
the key at a root-owned `0600` path excluded from Git and validates
`compose.h4-provider-secret.yaml` with `docker compose config --quiet`. It does
not start, stop, or recreate any container. The reviewed overlay is prepared to
mount the credential read-only at `/run/secrets/openai_provider_api_key` on
`guard` alone, but applying that mount requires separate approval.

Run `python3 owner_key_input_test.py` with fake values before owner input. The
`install`, `rotate`, `status`, and `revoke` actions never print the key.
`revoke` refuses to delete a mounted secret. The overlay adds no port, does not
change the provider route, does not create a paid permit, and does not
authorize a Responses request. Provider capability, approved guard recreate,
and token-count preflight remain separate after the owner has entered the key.
