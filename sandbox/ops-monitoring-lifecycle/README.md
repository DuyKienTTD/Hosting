# OPS-01A/S2 lifecycle sandbox

This directory is an offline synthetic contract only. It does not read VPS/KVM2, production metrics, credentials, notification channels, cron, webhooks or paid providers.

## D1 contract

- Validate fields, UTC timestamp, resource, source, rule version, freshness, health and signal before control-state mutation.
- Reject exact and conflicting sample-ID replays before control-state mutation.
- Require strictly advancing UTC timestamps. Rejected samples do not advance trusted time or streaks; audit entries are diagnostic only.
- `OPEN` is an incident lifecycle state. A cooldown controls notification eligibility, not incident identity.
- `OPEN` + bad×3 never increments incident sequence. At `+899` notification is suppressed; at `+900` and `+901` a new notification is eligible when the bad×3 condition is present.
- `RECOVERED` + bad×3 starts a fresh incident independent of the previous notification cooldown. Notification emission remains separately reported.
- `incident_id` and `sequence` are stable for the active incident.
- S1 composition is represented only by the pinned minimal test fixture. No runtime S1 composition claim is made.
- Snapshot/replay is synthetic serialization only and must not create duplicate incidents or notifications.

The original S2 10/10 provenance remains historical; D1 evidence is reported separately.

## D2 delta: trusted interruption, payload and explicit rule

- Trusted `UNKNOWN` / stale-freshness / blocked-health sample with fully valid
  ID, finite JSON payload, configured resource/source/rule version (and matching
  optional explicit rule), and a strictly later UTC timestamp **breaks both
  consecutive streaks**. Diagnostic audit records `TRUSTED_INTERRUPTION`.
  It does **not** advance clock, consume ID, change incident identity, send
  notification or modify lifecycle state. Three new consecutive qualifying
  goods are required to recover after the interruption; three new bads to OPEN.
- Foreign resource/source/rule/version, malformed ID or payload, replay or
  non-advancing timestamp are rejected **without any control-state mutation**;
  only bounded, sanitized sample IDs (or null) are included in audit. This
  differs deliberately from trusted interruptions; audit is not a security log.
- Sample ID: 1..128 ASCII alphanumeric / `_.:-` characters. Required fields
  as in `policy.json`, only optional `rule`. NaN/Infinity, non-JSON values,
  cycles, extra fields and non-string IDs fail closed with `INVALID_PAYLOAD`
  or `INVALID_SAMPLE_ID`. Replay check precedes watermark check.
- Backward-compatible *synthetic single-rule v1 envelope*: absence of `rule`
  is permitted for unchanged S2 fixtures; if explicitly supplied, the rule
  must equal configured `N8N_READINESS` or reject `RULE_MISMATCH`. This does
  not authenticate real sources and does not define a production ingest API.
- The test helper `PinnedS1Evaluator` is a local equivalence stand-in;
  **S1_EQUIVALENCE_FIXTURE_ONLY**; neither real S1 import nor S1 composition
  execution was tested. D1 cooldown/incident and snapshot claims remain
  synthetic-only. No VPS, outbound notification or paid service.

## D3 trusted interruption replay registry (offline)

- Independent Hermes QA (PR #36, 21 groups: 19 PASS / 2 FAIL) found that an
  already-applied `TRUSTED_INTERRUPTION` could reset a later good streak again
  before the accepted-sample watermark had caught up, including after restore.
  This D3 delta stores `sample_id -> canonical JSON` in a separate
  `interruption_replays` map when an **actually accepted** interruption breaks
  both streaks. `seen` remains strictly for accepted normal good/bad samples.
- All future occurrences of that ID are classified as `EXACT_REPLAY` if the
  canonical payload is identical, otherwise `CONFLICTING_REPLAY`; neither
  resets streaks. A valid good/bad sample with an already-interrupted ID is
  **not** treated as a correction: it is `CONFLICTING_REPLAY`. Malformed or
  foreign inputs do **not** reserve IDs in this registry. An interruption
  reusing an already accepted valid-sample ID also conflicts.
- Snapshot **version 2** includes the registry and restores it with size and
  overlap checks. Legacy v1 snapshots without interruption evidence may be
  restored; a v1 snapshot containing an interruption audit is rejected because
  the replay map cannot be reconstructed from a nonauthoritative audit.
  Caller-supplied snapshot JSON is **not authenticated**, and an adversary
  deleting history is outside this synthetic offline boundary.
- At most **256** interruption IDs per in-process Lifecycle. **No eviction**:
  once full, all *new* sample IDs fail with `INTERRUPTION_REGISTRY_FULL`,
  leaving state/time/streaks unchanged, while previously registered replay
  IDs still reject normally. This halts the mock to avoid silently weakening
  dedupe and requires a separately approved reset/new instance; no live
  notification or auto-reset is implemented. The original `seen` map for
  good/bad samples is separately unbounded and is **not** solved here.
- Scope remains `S1_EQUIVALENCE_FIXTURE_ONLY`, not S1 runtime import. No
  durable database, multiprocess dedupe/atomicity, real monitoring, VPS,
  notifications, production or paid API. Work/Hermes independent D3 QA pending.
