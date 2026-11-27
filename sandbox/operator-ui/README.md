# Offline Operator Console

Open `index.html` in a local Chromium browser. No server, installation, sign-in or network connection is needed for the demo. CSS and JavaScript are local files. State stays in memory and resets on reload. Use the role selector for synthetic operator/reviewer/owner identities. It is a presentation feature. All live controls are disabled.

Start in Builder, load the sample, save, validate and simulate. The simulator recognizes only the predefined Trigger → Agent Task → Connector → Receipt graph. A fixture-only FNV identifier ties the graph, run and receipt to their displayed version. It is unsuitable for security or real approval binding.

## Test runner

```sh
node --check app.js
node dom-test.cjs
NODE_PATH=/path/to/installed/node_modules CHROMIUM_BIN=/usr/bin/chromium node browser-test.cjs /tmp/operator-ui-evidence
```

The DOM contract test exercises the actual handlers using Node and a small DOM substitute. The optional browser runner needs a preinstalled Playwright and Chromium. It drives actual browser controls, denies HTTP(S), checks 360/768/1280 px and 2x emulation, and saves two screenshots when the environment permits. No new package fetch is needed if those test tools exist.

## Boundary for S1 controls

| Control | Offline status | Limit |
| --- | --- | --- |
| C01 Navigation, workspace/env, filters and refresh | IMPLEMENTED_IN_OFFLINE_UI / DEMO_STUB | Nine destinations and Sandbox selection. Agent capability filter only; workspace switch, other filters and refresh are design-only. |
| C02 Capability and source inspect | IMPLEMENTED_IN_OFFLINE_UI | Labels and source PR references in static fixture cards. |
| C03 Workflow/version | IMPLEMENTED_IN_OFFLINE_UI / DEMO_STUB | Session draft, fixture load, fork and archive summary. Version diff UI is design-only. |
| C04 Node and typed ports | IMPLEMENTED_IN_OFFLINE_UI | Form editor, connections, mapping and ordered list. Canvas and zoom controls are design-only. |
| C05 Save/conflict | IMPLEMENTED_IN_OFFLINE_UI / BACKEND_REQUIRED | Save in memory. No ETag or multi-user conflicts. |
| C06 Validate | IMPLEMENTED_IN_OFFLINE_UI / BACKEND_REQUIRED | Local graph checks. Future server must independently validate. |
| C07 Simulate | IMPLEMENTED_IN_OFFLINE_UI | Only predefined graph runs, using one synthetic run/receipt per fixture digest. |
| C08 Approval queue/request/decide | IMPLEMENTED_IN_OFFLINE_UI / BACKEND_REQUIRED | Version/operation/mock ID, fake requester separation, explicit fixture expiry. No server approval or diff. |
| C09 Activate/schedule/pause | LIVE_DISABLED / BACKEND_REQUIRED | Activate is visibly locked. Real schedule and pause absent. |
| C10 GA4 proposal | IMPLEMENTED_IN_OFFLINE_UI | In-memory read-only fixture proposal and source status. |
| C11 Connect/verify/revoke | LIVE_DISABLED / BACKEND_REQUIRED | OAuth is visibly locked. Other access mutations absent. |
| C12 Runs/evidence | IMPLEMENTED_IN_OFFLINE_UI / DEMO_STUB | Timeline and inline IDs/receipt. No export/copy control. |
| C13 Reconcile/callback | IMPLEMENTED_IN_OFFLINE_UI / BACKEND_REQUIRED | Records fixture reconciliation; digest comparison only. No signature verifier or callback traffic. |
| C14 Retry/rollback | LIVE_DISABLED / BACKEND_REQUIRED | Unknown retry locked; rollback node editor only. |
| C15 Incidents | IMPLEMENTED_IN_OFFLINE_UI / DEMO_STUB | Readiness escalation and recovery, backup escalation. No incident integration, general notes or restore. |
| C16 Content draft and channel | IMPLEMENTED_IN_OFFLINE_UI / DEMO_STUB | Synthetic draft card and versioning. No media renderer or channel changes. |
| C17 Media review | IMPLEMENTED_IN_OFFLINE_UI / BACKEND_REQUIRED | Separate fixture review action. |
| C18 Publish | LIVE_DISABLED / BACKEND_REQUIRED | Locked even on approved draft. |
| C19 Settings/roles/audit/kill switch | IMPLEMENTED_IN_OFFLINE_UI / LIVE_DISABLED / BACKEND_REQUIRED | Demo role selector and transient read-only audit. Live role mutation and kill switch locked/absent. |
| C20 Keyboard/view helpers | IMPLEMENTED_IN_OFFLINE_UI / DEMO_STUB | Native controls, skip link and focus handling. Generic retry/reset/dismiss controls are design-only. |

Future server must enforce workspace and resource permissions, consent, budget, approval and expiry, idempotency, callback identity/binding, secret protection and audit. The prototype has no backend, account scopes or production credentials.
