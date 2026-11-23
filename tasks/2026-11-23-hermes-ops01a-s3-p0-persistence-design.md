---
id: hermes-ops01a-s3-p0-persistence-design
type: task
status: design-complete-pending-independent-review
updated_at: 2026-11-23
owner: hermes-webui
next_owner: chatgpt
sensitivity: public-redacted
---
# HERMES-OPS01A-S3-P0-PERSISTENCE-DESIGN — offline design scope

**Assignment:** [PR #36 comment 7094362338](https://github.com/DuyKienTTD/Hosting/pull/36#issuecomment-7094362338). **ACK:** `EXECUTE HERMES-OPS01A-S3-P0-PERSISTENCE-DESIGN`. **COST_ROUTING:** Hermes WebUI designs from the already accepted D3 semantics; no Codex, Hostinger PAUSED, independent A1/Work reviewer to be selected by ChatGPT. No paid inference or runtime action.

**Source pins:** main `e385c1bea2070973e3007e5717f7e980348d6ab3`; PR24 `e9c2d8f759850ea9c654de7e103549e041f66679`; PR36 D3 `5626bb55072cdcca0d39f3ba57180d3c57af05ad`, `sandbox/ops-monitoring-lifecycle/lifecycle.py` blob `0043cb1a00ff1a3e9fbc7f1267900ebde02f4769`; PR31 §11 (separate, not merged) `210c15568bb2ecae17c59874d9a36c6cd2a27fda`. Rule blobs at main: `AGENTS.md@cb6a8af9d2634cc4eb959132d6c3f2fafcbfaf35`, `rules/AGENT_WORKFLOW.md@69ec0db902f457f06dd547dae171220331df0f5e`, `rules/REPOSITORY_SECURITY.md@c24d608036b11dcd3fafcaefbefa23fdb591990e`, `STATE.md@c8e8941aa1418f70ed9542063f0485a129739d25`, `CATALOG.yaml@719c9c5d2832382285d732b9ad21f55d8c163733`, `agents/hermes.md@618b8efce4738e242f54788d46d77068b8f747fa`.

**Prior state / no repeat:** `DONE_VERIFIED` independent D3 QA 17/17 offline, [decision #7094319094](https://github.com/DuyKienTTD/Hosting/pull/36#issuecomment-7094319094), [report](https://github.com/DuyKienTTD/Hosting/blob/eb1885bd7052934a96fd52a21da1791a6aa25310/reports/2026-11-23-hermes-qa-a1-ops01a-s2-d3.md). Author 44/44 is `DONE_REPORTED`, not independently rerun. Live durability and continuity are `NOT_RUN`. Change trigger for this task: two explicitly accepted D3 limitations (256-ID capacity freezes all new samples; untrusted v2 snapshot can erase dedupe history). No S2 test rerun or source edit.

**READ_SET:** rules, PR31 §11, PR24 baseline, PR36 source/policy/README/D3 report/test, D3 independent evidence and official database docs linked in report. **WRITE_SET:** this task; `reports/2026-11-23-hermes-ops01a-s3-p0-persistence-design.md`; `reports/evidence/2026-11-23-hermes-ops01a-s3-p0-design-matrix.json`. **DO_NOT_TOUCH:** A1 PR36, PR24, PR31, PR34, main, STATE/CATALOG/CHANGELOG, VPS/production/credentials/paid API/Codex/CI/merge. **FIRST_ACTION:** pin and read exact refs and rules; done. **DEPENDENCIES:** design uses only public sources; future implementation depends on independent review, A0 scope approval, authenticated source and isolated test environment. **INVARIANTS:** D3 F1-R1/R2, single accepted ID namespace across good/bad/interruptions, incident/cooldown and no fabricated live test. **TEST_DELTA:** create proposed matrix only, all `DESIGNED_NOT_RUN`. **STOP:** drift or missing rights before side effects; separate approval before implementation or live. **HANDOFF:** ChatGPT Điều phối receives report/evidence URLs for independent A1/Work review, not automatic execution.
