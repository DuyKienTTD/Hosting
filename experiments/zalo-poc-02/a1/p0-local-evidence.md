# ZALO-POC-02 A1 P0 — local synthetic test log (2026-11-24)

**Scope:** isolated hand-authored TypeScript and SQLite fixtures, exactly one synthetic account `synthetic_1`; fake callbacks only; no Zalo credentials, no model calls, no provider sends. Source execution did **not** include the full original application nor a proven external-egress-blocked namespace. This is `VERIFIED_LOCAL_ADAPTED`, **not** Work's `VERIFIED_NO_EGRESS` and not native combined-tree PASS.

## Commands / observed exit codes

```text
node --version
v22.16.0
node --experimental-strip-types --test /mnt/data/zalo_p0/atomic-send-admission.test.ts
first run: exit 1; 5 PASS / 1 FAIL because negative test incorrectly expected an invalid revision to return false rather than throw.
after correcting that test expectation:
exit 0; tests 6, pass 6, fail 0
node --experimental-strip-types --test /mnt/data/zalo_p0/atomic-send-admission.test.ts /mnt/data/zalo_p0/outbound-guard-runtime.test.ts
exit 0; tests 9, pass 9, fail 0
```

**Test cases (all synthetic):** STOP before dispatch admission; STOP after admission with existing request classified as in-flight; opt-out, takeover, expired/unknown policy deny; persisted uncertain attempt survives a new Node process and is not resent; rejected stale policy revision; group destination/type mismatch; serial policy mutation vs admission; runtime wrapper duplicate-key refusal; STOP microtask race in wrapper; unknown group sender binding fail-closed.

**Local source SHA-256 checks (before adaptation of import specifier):**
- `atomic-send-admission.ts`: `55c49485fb03d82750e9ef780abba8cfaa5c79dca1bedfed87c5e09e9bae7374`
- `atomic-send-admission.test.ts`: `d9584392368ce843576c927596fc1d0868d3010c612873d21f45b63ce510c2ba`

The GitHub staged files use conventional `.js` ESM specifiers whereas the local Node 22 type-stripping runner uses `.ts`. The staged tests include a typed Promise resolver and are **not byte-identical** to the local adapted fixtures. Work must independently compile and run **the exact new patch** inside its verified blocked-egress, pinned-source sandbox. Prior Work 15/15 was for earlier patch blob `65ad964d1c371b3124b7d09b3ba81320044e7a4f`, not this P0 revision.

**No-guarantee note:** The serialized SQLite authority calls the fake transport synchronously while holding its transaction lock, then commits and awaits completion. It proves dispatch *admission* linearization under the same DB connection/transaction writer, not cancellation or prevention of completion for a previously admitted in-flight provider call. Untrusted asynchronous transports that defer initiation need an actual final transport-site adapter and Work race proof. A real shared consent writer has **not** been connected.
