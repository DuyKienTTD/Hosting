# ENG-01A-S3 offline integration

This source harness runs the S1 and S2 modules from pinned local Git objects. The runner needs Git, Python 3.12+ and both upstream commit objects already fetched. It does not fetch, install dependencies, start services or import a network client.

```powershell
python -X utf8 -B sandbox/connector-integration/test_integration.py
python -X utf8 -B sandbox/connector-integration/merge_preview.py --evidence "$env:TEMP/ttd-eng01a-s3-merge.json"
```

S1 comes from [PR #10 at `79dfe8a`](https://github.com/DuyKienTTD/Hosting/commit/79dfe8aae5c30d4e896c29333e0296ada1671b7e). S2 comes from [PR #13 at `0235b5f`](https://github.com/DuyKienTTD/Hosting/commit/0235b5f9bb38d0d7e99a600188705d50977527f5). The loader verifies Git blob hashes on extraction and before each import, including worker restarts. All SQLite state lives in an S1-owned temporary directory. `LIVE_ENABLED=False`, Git lazy fetching and external Git protocols are disabled in the harness, and the test runner denies Python socket activity.

## Contract v1

An intent contains `contract_version=1`, `synthetic=true`, synthetic approval, a `fake-…` public idempotency key, operation, allowlisted arguments, scenario, resource budget and logical deadline. Only `ga4.run_report`, `wp_woo.get` and `wp_woo.list` are wired.

The adapter binds the original key to S1 canonical JSON and the full S3 request SHA-256 in a sidecar table inside the same fixture SQLite. The native S1 request stays `channel=fixture`, `source=synthetic`, payload `{mode: "success"}` and uses the first 48 hex digits of the S3 intent digest as its synthetic key suffix. The sidecar binds the full intent and native request digests. An identical request gets the same native job and receipt. An approved key reused with changed valid arguments returns 409. If admission is interrupted between the sidecar reservation and native admission, an identical retry can complete admission within the original deadline. Such an interruption is outside the two measured crash windows.

S1 owns admission, the worker lock, fake dispatch, outcome, outbox, receipt and ACK. S3 invokes S2 after the fake dispatch and commits the prepared result to its sidecar. During S1 settlement, S3 inserts one association per job in `s3_settled_results` with the SHA-256 of the durable outbox event and canonical prepared bytes. The association and outbox commit in the same `state.sqlite` transaction. The separate `worker-lock.sqlite` connection serializes worker execution and is only used as a lock. The settlement hook relies on the pinned S1 implementation calling one `tx()` for the outbox write.

After ACK, S3 exposes the prepared result only when the native receipt validates against the outbox event and the stored association verifies both the event digest and prepared bytes. The v1 supplementary receipt binding keeps the original fields. With a missing or invalid association, `result` and `result_sha256` are null and the native receipt and outcome are preserved. Existing v1 fixtures gain the association table on open. Previously prepared results have no trustworthy association and are never backfilled. This is a local integrity check inside the synthetic datastore.

If the worker exits before the settlement transaction commits, the outbox and association are both absent. Recovery closes `working` as unknown with no attached result and no repeat S2 read. If settlement has committed, recovery resumes the durable callback and, when present, reuses the original receipt before ACK. A normal synthetic delayed/504 attaches its result through this path and still settles `outcome_unknown`. A pending job whose S1 deadline has arrived makes no fake dispatch and no S2 read. The fixture tests cover process exits and replay; external effects and power-loss durability are outside their scope.

## Compatibility

| Surface | S1/S2 difference and S3 mapping |
| --- | --- |
| Identity | S1 schema v1 and synthetic job fields remain native. S2 operation/arguments bind through S3 intent v1. The local bridge adds the full request/result/receipt binding. |
| Status | S1 admission 202/200/409 is separate from S2 read 200/403/404/422/429/504. Validation and known faults settle failed. Logical 504 settles unknown. A 429 retry hint does not cause a retry. |
| Date and locale | S1 clock is logical milliseconds. S2 observation/update timestamps are UTC ISO strings, GA4 filter dates are inclusive, and WordPress/Woo locale is EN/VI. S3 passes fixture data without replacing those clocks or fields. |
| Money and units | S1 budget is one fake dispatch with synthetic units. S2 GA metrics are counts and Woo prices are integer minor currency units plus currency. S3 performs no conversion or billing. |
| Provenance and privacy | S2 records retain schema/source ID/observation/classification/source status/provenance. A GA4 aggregate references only its attribution source. No lead/customer linkage or personal fields are added. |
| Pagination, budget and timeout | Cursor and watermark belong to the S2 snapshot. Errors expose no advancement. S1 keeps its admission and expiry gate; S2 gets the remaining logical window capped at 1000 ms. A logical elapsed value is not a measured runtime deadline. |

## Integration and merge scope

S3 is a test harness over the pinned API and subprocess seam. If the S1 worker checkpoint contract changes, review a small explicit interface delta and re-pin both modules. A real connector would need separate auth, pricing, quotas, consent, retention, transport and external idempotency approval. `REAL_CONNECTOR_UNTESTED`. Linux was not run because the only local WSL distro was Docker Desktop, outside scope.

The merge preview uses a detached temporary worktree and `git merge-tree --write-tree`. It does not commit a merge or update refs. Proposed order is independent review and merge of S1 first, review S2 against the resulting main and preserve both metadata additions, then review S3. The full proposed metadata diff is in the evidence JSON. This branch changes no existing shared metadata.
