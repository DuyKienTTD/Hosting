# GOV-02/S1 repository metadata audit

Run from a checkout with the recorded Git objects and remote-tracking refs already available. The checker reads Git objects only. It does not fetch, switch branches, test source PRs, execute a merge or call external services.

```powershell
python -X utf8 -B sandbox/repo-metadata-validator/validate.py sandbox/repo-metadata-validator/manifest.json --evidence "$env:TEMP/gov02-audit.json"
python -X utf8 -B sandbox/repo-metadata-validator/test_validate.py --evidence "$env:TEMP/gov02-fixtures.json"
```

Output files must be new. The audit exits `0` for a clean result, `1` for governance findings, and `2` for invalid input, unavailable source or integrity errors. The checked-in snapshot is expected to exit `1` while its index gaps remain.

## Manifest v1

`baseline` and `plan` record Git refs, commits and trees. The plan also records its PR, path and blob. `packages` associates each task ID and portfolio ID with an owner, PR number, PR base, local remote-tracking ref, immutable commit/tree, and task/report/evidence path and blob. Verdicts are quoted from the pinned source. `scope`, `approval`, `readiness` and dependencies describe this review snapshot. `QA_PASS_OFFLINE` has fixture scope. Draft status, source-review and readiness fields cannot confer account permissions or production approval. A source change requires deliberate review of pins.

The audit validates the simple `documents` list in the current CATALOG format, relative links in STATE/CHANGELOG and portfolio rows in the pinned plan. It checks the union of observed catalog paths across sources and reports paths absent from that union. The union is for tracing coverage across open PRs. Before an index update, validate each target path on the intended base. A shared file edited in multiple PRs is a coordination finding even when a textual preview is clean. External URLs, prose approval intent and live service readiness are outside this local check.
