---
id: z4-nick-worker-protocol
type: knowledge
status: draft
updated_at: 2026-11-26
sensitivity: public
---

# Nick worker protocol v1

Z4-S3-NICK. One outbound WebSocket over verified TLS per worker. The upgrade uses a worker-scoped Bearer credential from the OS environment. The server binds the authenticated identity to exactly one nick and must fence concurrent connections for that nick. Use UTF-8 JSON objects, a 64 KiB frame limit and synchronized clocks. Absolute timestamps are Unix milliseconds. Job, peer and message IDs match `[a-zA-Z0-9_-]{1,100}`.

| Direction | Type | Fields and semantics |
|---|---|---|
| Worker → server | `hello` | `protocol: 1`, `stopped`. Start with sending disabled. |
| Worker → server | `heartbeat` | `stopped`. Sent about once a second. |
| Server → worker | `pong` | Respond on the same connection. After 15 seconds without pong the worker closes the socket. Reconnect backoff is 1–30 seconds. |
| Server → worker | `policy` | `hour`, `day` as nonnegative integers, `adsEnabled: false`, `expiresAt` at most 30 seconds ahead. Zero disables admission. Refresh before expiry. Limits count attempted dispatches over rolling windows. Policy is cleared on reconnect. |
| Worker → server | `inbound` | `peer`, `id`, `text`. Deduplicate by authenticated nick plus peer and message ID. Persist before ACK. Treat text as customer data. |
| Server → worker | `inbound_ack` | `peer`, `id`. Duplicate inbound can still arrive, including on restart. |
| Server → worker | `send` | `id`, `peer`, `text`, `expiresAt` at most 60 seconds ahead. Text is a single line up to 500 UTF-16 units. One pending job per worker. |
| Worker → server | `authorize` | `id`, `peer`, `nonce`, `text`. Match exact contents against the original authorized server job. Respond within 3 seconds or let the request expire. |
| Server → worker | `permit` | Echo `id`, `peer`, `nonce`. Requires `guard: "allow"`, `purpose: "customer_service"`, `optOut: "not_opted_out"`, `adsEnabled: false`, and `expiresAt` at most 1 second ahead. Single use, bound to the connection. |
| Server → worker | `revoke_permit` | `id`, `nonce`. Revokes the matching pending permit on the current connection before dispatch. |
| Worker → server | `audit_alert` | `id` (job ID), `code: "committed_before_revoke"`, `audience: "owner"`, `idempotencyKey: "nick:committed_before_revoke:<job-id>"`. Retried on heartbeat until acknowledged. |
| Server → worker | `audit_ack` | `id`, `idempotencyKey`. Send after recording the audit annotation and durable owner alert. |
| Worker → server | `result` | `id`, `result` of `rejected`, `sent` or `unknown_delivery`. Friendship rejections include `reason: "not_friend"` or `reason: "friend_status_unknown"`. `sent` means a fresh own-message echo in the matched chat. It does not assert that the recipient read or received it. |
| Server → worker | `stop` | Latches STOP across reconnect and restart. No remote resume message. |
| Worker → server | `stopped` | `reason` such as `server_stop`, `logged_out`, `verification`, `warning`, `restricted`, `unexpected_origin`, `ui_unrecognized`, `browser_unavailable`. On reconnect `hello.stopped` remains authoritative even if the previous event was lost. |

## Server integration contract

Before issuing each permit, atomically check Guard and reserve the send in Postgres. Verify current account and global STOP, service consent, all three opt-out states, ads disabled, known inbound relationship, job expiry and server-side rate limits. Only the explicit not-opted-out state may pass. Bind the reservation to the original immutable job, nick, peer and nonce. Use a single-use permit and persist a terminal outcome by job ID. Never reissue a permitted job or automatically retry `unknown_delivery`. If a permit may have reached the worker and the terminal result is missing, resolve conservatively to `unknown_delivery`. Use STOP and withhold permits when disabling sending. Socket closure and replacement invalidate the connection epoch. The worker arms a page-local, single-use permit keyed by nonce and connection epoch. Disconnect, connection replacement, STOP, a disabling policy and matching revocation immediately enqueue a gate clear in Chromium. Gate updates carry monotone revisions to fence out stale writes. The permit is bound to a unique worker page ID, active chat element, exact peer and URL. The worker owns one registered Chromium target in a dedicated profile. Playwright page, popup, navigation and close notifications plus CDP target discovery invalidate the epoch and page permit. The worker revalidates the CDP identity and sole-page invariant before evaluation. Renderer focus, visibility, URL and chat checks provide a second gate. After yielding to the renderer, the final synchronous task checks the permit, expiry, document visibility and focus, active recipient, friendship and UI safety. Consuming the permit in this task is the **send commit point**. The task clicks immediately after consumption with no await or wait loop.

An invalidation delivered before the commit point prevents the click. A revocation observed after commit cannot cancel it. For a matching committed permit, the worker journals and emits `audit_alert`. The authenticated runtime endpoint `/internal/nick-worker` records the job state `committed_before_revoke` in `send_log` and the owner alert in `notices` in one Postgres statement before sending `audit_ack`. It accepts only existing reply reservations with `agent='nick-worker'` under the single configured nick worker credential. The notice key is the audit idempotency key. The state records browser admission and is independent of proof of delivery and never enqueue another send for the job. A commit confirms browser admission only. Delivery can still be `unknown_delivery`. If Chromium disappears before commit evidence can be read, preserve the conservative delivery state.

The worker requires positive friendship evidence in the active direct chat for the exact requested peer ID before typing and checks it again in the same browser operation as the click. Inbound history and display names do not establish friendship. The reviewed selector config specifies `friendStatus` (scoped to the active chat) and `friendStatusAttribute`. Exactly one visible marker with value `friend` allows the friendship check to pass. A visible marker with value `not_friend` rejects with that reason. Missing, hidden, ambiguous or unrecognized evidence rejects with `friend_status_unknown`. Neither a Guard permit nor a matching display name overrides this check. Friendship rejections and their reasons are journaled by job ID.

The worker persists an attempt with provisional `unknown_delivery` before initiating the click. It reports the stored outcome for duplicate job IDs that reached this boundary. Early rejections can occur without a journal record. Treat any reported result as terminal for that job and never reuse its ID for another message. A reconnect requires fresh policy and credentials bound to the same nick. Handle a missed or ambiguous send outcome in the operator workflow.

The worker rotates through visible existing 1-1 inbox rows and reads up to the last 50 rendered inbound messages per chat. During a send it pauses navigation. Browser UI and virtualization can hide chats and message history. Server ACKs are held in worker memory and the server is the persistent deduplication authority. Body content is sent only over WSS and absent from the worker's delivery journal. The worker does not scroll virtualized inbox rows or persist a browser-side message backlog.

The runtime endpoint implements audit ingest and heartbeat only. Job dispatch, reservation creation, and live provisioning require the nick channel integration. See the [Windows worker README](../apps/ttd-zalo-nick-worker/README.md).
