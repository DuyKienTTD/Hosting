# OPS-01A/S2 Offline Lifecycle

Synthetic-only state machine for one resource and rule.

- `NORMAL -> OPEN -> RECOVERED -> OPEN`
- exact cooldown boundary: 899 seconds suppressed, 900 seconds eligible
- duplicate/out-of-order/resource/source checks fail closed
- snapshot/replay is synthetic serialization only
- no external notifications or live monitoring

Run `python3 -m unittest discover -s tests -v`.
