# P0 Level 2 provider sandbox

This directory is the secret-free source for the approved GPT-6 Luna provider
test. It upgrades only the auxiliary Level 1 runtime. It does not configure or
claim to be Hermes Agent E2E.

## Hard safety properties

- The reasoner has no direct Internet route. HTTPS leaves only through the
  companion CONNECT proxy, which accepts exactly `api.openai.com:443`.
- No container publishes a host port. Production n8n and Hermes are not
  mounted, restarted or reconfigured.
- Every provider attempt is admitted under an exclusive file lock and written
  atomically to a persistent ledger before the request is sent.
- Limits are five attempts total, 4,000 input tokens, 2,000 output tokens,
  USD 0.05 per UTC day and USD 0.05 for the whole P0. The live request uses a
  stricter 600-token output limit and reserves USD 0.0035 before dispatch.
- There is no automatic provider retry. A repeated `task_id` is served from the
  persistent task record and cannot create another paid call.
- The API key and bearer token are runtime-only values in a root-owned env file.
  This repository contains no secret value.

## Deployment outline

1. Verify model metadata, current official prices, account access, production
   and sandbox health, secret permissions and absence of public port mappings.
2. Back up the auxiliary Compose source, ledger and n8n sandbox data.
3. Replace only the auxiliary source files and workflow, preserving the
   dedicated n8n encryption key and bearer token.
4. Recreate the auxiliary reasoner and egress proxy; restart the auxiliary n8n
   only for its workflow import. Never restart a production service.
5. Run no-cost negative tests, then exactly one authenticated fake-data E2E
   request if every gate is still green.
6. Check the persistent ledger, idempotent replay, callback schema, final
   health and production restart counters.

`rollback.sh` restores the Level 1 source backup and auxiliary workflow/data
backup. It never touches production containers or their volumes.
