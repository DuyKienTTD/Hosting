---
id: zalo-zpc-04-threat-model
type: knowledge
status: draft
owner: A1
task_id: ZPC-04-SECURITY
updated_at: 2026-11-26
sensitivity: public
---
# Threat model
[Index](README.md) · [Matrix](TEST_MATRIX.md) · [Architecture](https://github.com/DuyKienTTD/Hosting/blob/d441205/program/zalo-mvp01/PRODUCT_COMPLETION_PLAN.md#5-target-architecture--extend-do-not-rebuild)

Assets: customer-scoped messages/facts, consent and STOP epochs, approval digest and intent, source/version provenance, provider/channel credentials, cursor and receipt integrity. Actors: untrusted customer/document/model output, compromised renderer, stale asynchronous worker, replaying channel peer, local unprivileged Windows user. Trusted boundary: main/application Policy Core + durable state, not model/renderer; operator authority required for outbound. All interfaces deny by default.

| Flow / trust crossing | Threat and impact | Required controls and oracle |
|---|---|---|
| AI adapter (ZPC-08) | Oversharing, injection, malformed output, stale callback, tool misuse | Allowlist serialized fields, customer/thread scope, consent/epoch before invocation and publication; structured draft and verified source IDs only; no send tools/credentials; timeout/refusal/schema fail closed. Inspect actual fake request and output, not just prompt templates. |
| Knowledge ingestion (ZPC-07) | Instructions hidden in valid document, markup, stale/conflicting prices, forged source | Parse inert bounded content; version/effective-date provenance, source allowlist, abstain on unresolved conflicts; never execute embedded instructions or remote resources. |
| Customer memory (ZPC-06) | Same-name collision, cross-thread retrieval, denied/ephemeral persistence, resurrection after deletion | Stable account/customer/thread/message IDs, separate consent gates, scoped retrieval and provenance, deletion fencing, export scoped; inspect persistent stores, indexes/cache and restart. |
| Future channel (ZPC-09) | Forged event, replay, lost cursor, wrong destination, duplicate/unknown delivery, stale send | Authorized documented adapter only; verify signature/identity, transactional dedup/cursor, exact approval, durable unique reservation and final initiation fence; unknown delivery reconciled not retried. No unofficial route or live test. |
| IPC/renderer (ZPC-11) | Privileged command from wrong sender/frame, malformed input, injected markup, blocked STOP UI | Narrow validated IPC and CSP/sandbox; check sender/frame/URL/arity/schema; main-side policy independent of disabled UI; STOP accessible during pending work. No raw provider/channel handles in renderer. |
| Local storage/credential (ZPC-06/08/09/11) | Plaintext credentials, logs, cache residue, unauthorized user, crash/restart | Windows protected credential storage (implementation choice pending), fail closed when unavailable, no plaintext fallback; minimize audit, scoped export/delete and document residual backup/retention limits. No claim of disk encryption from SQLite alone. |

Baseline source observations: Foundation uses BEGIN IMMEDIATE, per-target revisions, global epoch, exact digest including account/target/thread/type/content, unique intent reservation and synchronous fake receipt under writer lock. Existing edit invalidation removes map approvals; reserved send requires a separate race oracle on future adapter. Renderer STOP currently disabled while busy; future asynchronous AI path requires explicit test N34, not a claim of current runtime exploit. Main process validates sender/frame/document/arity, uses sandbox/context isolation and narrow bridge. Existing fake draft is deterministic and cannot establish adversarial model safety. SQLite retain revocation hides previously retained records, not physical deletion. No protected credential store or real channel/provider present at baseline.

Acceptance: P0 any unauthorized disclosure, mutation or transport start blocks candidate. Use deterministic barriers, fake clock and sequence numbers; distinguish already-started transport from new post-STOP starts. Unknown delivery is not success or retry permission. P1 faults block affected capability unless A0 explicitly accepts residual risk; future channel/Windows cases remain gated, never count unavailable runtime as PASS.