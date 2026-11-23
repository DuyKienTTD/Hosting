# OPS-01A/S1 Offline Monitoring Contract

Synthetic-only deterministic evaluator using Python standard library. No HTTP, sockets, cron, Docker daemon, credentials, email, webhooks, paging or live monitoring.

Run `python3 tests/test_evaluator.py`.

The policy thresholds are proposed and must be tuned only after an approved source, scope, identity, retention and alert channel exist. Missing or blocked data remains UNKNOWN.
