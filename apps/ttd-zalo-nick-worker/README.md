# TTD Zalo nick worker

## Windows fixture test

Install Node.js 22 or newer and use PowerShell from this directory.

```powershell
npm ci
npx playwright install chromium
npm test
```

The test starts an HTTP server bound to loopback, opens the synthetic fixture in Chromium and exercises the worker with an in-process server endpoint. No account is needed.

## Windows runtime configuration

Install Google Chrome Stable. Start the process under the Windows user that owns its dedicated profile directory. Playwright starts Chrome over a local CDP pipe without an open debugging port. Run one worker per profile and keep its runtime directory outside the Git checkout.

| Environment variable | Value |
|---|---|
| `NICK_PROFILE_ROOT` | Absolute, access-controlled local directory for this worker |
| `NICK_WEB_URL` | Local synthetic fixture URL with the fixture selectors |
| `NICK_SELECTOR_FILE` | Absolute path to a reviewed, versioned selector JSON. The included `selectors/fixture-v2.json` targets the fixture |
| `NICK_SERVER_URL` | WSS endpoint implementing the [protocol](../../docs/nick-worker-protocol.md) |
| `NICK_WORKER_AUTH` | Runtime credential supplied by the approved local secret mechanism |

Start the configured process with `npm start`; stop it with Ctrl+C. The server STOP and UI safety markers latch a durable stop. Preserve `delivery.jsonl` and the profile on restart. Any reactivation requires operator review of the cause and controlled restoration that preserves the delivery journal's idempotency records. A blocked attempt can leave a draft in the composer. The worker requires an empty composer before starting the next job.

The supplied selectors only cover synthetic HTML. A separately reviewed selector configuration and server integration are prerequisites for live use. The worker rotates through visible existing 1-1 inbox rows and checks the active recipient before sending. Off-screen inbox rows and unrendered history are outside the scanner.
