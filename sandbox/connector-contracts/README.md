# ENG-01A-S1 offline connector contract

This package models admission, execution, an immutable callback and a durable receipt with a Python standard-library fixture. Run it from the repository root with Python 3.12 or later.

```powershell
python -X utf8 -B sandbox/connector-contracts/test_offline_connector.py
```

## Contract v1

| Object | Required fields and semantics |
| --- | --- |
| Request | `schema_version=1`, `synthetic=true`, `idempotency_key`, `channel`, `source`, `approval`, `budget`, `deadline_ms`, `payload`. The fake implementation accepts `fake-…` keys, `channel=fixture`, `source=synthetic`, `approval=synthetic_approved`, `budget.max_dispatches=1`, `budget.max_units=1..10`, and only a `payload.mode` of `success`, `failure` or `timeout`. The adapter counts one synthetic unit per dispatch. The deadline is a logical millisecond timestamp, at most 60,000 ms ahead at admission. |
| Admission and job | Canonical ASCII JSON with sorted keys and no whitespace or NaN is hashed with SHA-256. The adapter binds the key and digest in one transaction and derives `job_id` from the digest. First admission returns 202. An identical valid request returns 200 with the same job ID even after expiry. A different valid request with the same key returns 409. Status includes the original channel/source, approval, budget, deadline, state, outcome and observed fake dispatch/units. The response codes are in-process contract values. |
| Callback | `schema_version`, `synthetic`, `job_id`, `request_sha256`, `channel`, `source`, `outcome`, `sequence=1`, `occurred_ms`, `callback_id`. The callback ID is derived from all other fields. The receiver compares canonical bytes with the persisted outbox for the same job before committing. Missing identity returns 422 and a mismatched binding returns 409, even with a recomputed callback ID. |
| Receipt | `job_id`, `callback_id`, `request_sha256`, `event_sha256`, `outcome`, `committed_ms`, `receipt_id`. The receiver commits at most one receipt per job before the worker ACK. Exact event replay returns the original receipt. |
| Audit | Each job has an ordered append-only fixture trace with `sequence`, `event` and `observed_ms`. It records admission, working, fake dispatch when applicable, sending, receipt commit and ACK. The job ID scopes audit reads. |

## Recovery boundary

- `pending → working → sending → completed|failed|outcome_unknown`. The adapter commits its claim before the locally recorded fake dispatch, and it commits the outcome/outbox before delivery.
- A separate SQLite lock serializes worker processes. A replacement worker that acquires the lock converts an abandoned `working` job to `outcome_unknown` and delivers that callback without dispatching. A crash before the dispatch can therefore yield zero dispatches and one receipt.
- In `sending`, a replacement worker uses the same persisted callback. If the receipt was already committed, it reads the original receipt and commits the ACK without inserting another one. Callback recovery is separate from dispatch. No worker retries an unknown dispatch.
- Timeout uses a logical fixture clock. A result observed at or after the deadline cannot change the outcome to success. Once sending or terminal, a conflicting result or callback cannot overwrite the durable decision.
- The test harness kills Python subprocesses using `os._exit` and restarts fresh processes on the same temporary SQLite files. This demonstrates process crash behavior. The fake dispatch, outbox and receipt share one database with separate transactions. Host power failure, distributed callback delivery and irreversible external effects remain untested.

## Offline scope and future connectors

`LIVE_ENABLED=False`. The adapter exposes no listener, network transport, token or account interface. It rejects endpoint/credential configuration and only opens dedicated temporary fixture storage. The test processes enforce Python socket audit denial. Local callback identity is a binding check rather than authentication of a remote sender.

Generic parts include job/idempotency, digest, budget and deadline fields, immutable terminal outcomes, outbox/receipt identity and audit. A real connector needs its own owner approval, channel authentication and OAuth scope, transport-level callback authentication, resource/quota and rate-limit enforcement, consent and retention policy, provider pricing and compatible provider-supported idempotency or a separate transaction/reconciliation boundary. `OFFLINE_CONTRACT_PASS / REAL_CONNECTOR_UNTESTED` applies only to the fixture.
