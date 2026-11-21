# Hermes P0 hard-cap feasibility rehearsal

This directory contains a secret-free, network-free contract test for the
proposed pre-dispatch inference guard. It is a feasibility artifact, not a
deployable production service.

The rehearsal starts from a copy of the existing Level 2 ledger state (one
attempt and USD 0.0035 reserved). It proves that validation happens before
reservation, the enabled kill switch rejects without mutation, idempotent
replays do not reserve twice, and ten concurrent requests can admit only the
four remaining attempts.

Run with:

```text
python sandbox/p0-hermes-feasibility/offline_guard_contract_test.py
```

No network operation, provider credential or paid inference is used. A future
implementation needs separate approval and must use the real persistent Level
2 ledger rather than a copy.
