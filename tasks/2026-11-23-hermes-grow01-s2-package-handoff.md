---
id: hermes-grow01-s2-package-handoff-2026-11-23
type: task
status: draft-delivered-for-review
updated_at: 2026-11-23
sensitivity: public-redacted
owner: hermes-webui
next_owner: chatgpt
---
# GROW-01/S2 — ACK: offline package handoff

- **Lệnh:** [PR #18 comment 7092051626](https://github.com/DuyKienTTD/Hosting/pull/18#issuecomment-7092051626). `ACK=EXECUTE GROW-01/S2`, recipient Hermes WebUI; review integration owner ChatGPT/Work; next owner ChatGPT Điều phối.
- **FIRST_ACTION:** fetch main và exact heads PR #6/#18/#25/#27/#16/#23; đọc rules `AGENTS.md`, `PROJECT.md`, `rules/AGENT_WORKFLOW.md`, `rules/REPOSITORY_SECURITY.md`, `STATE.md`, `CATALOG.yaml`, `agents/hermes.md`, S1 package JSON và approval runbook; kiểm branch/path trùng.
- **Base:** `origin/main=e385c1bea2070973e3007e5717f7e980348d6ab3`; rule blobs: AGENTS `cb6a8af9`, WORKFLOW `69ec0db9`, SECURITY `c24d6080`, STATE `c8e8941a`, CATALOG `719c9c5d`, Hermes `618b8efc` (full SHA dùng `git rev-parse`). Main workflow hiện chỉ §§1–7, không suy diễn §§8–10 trong main. S1 HEAD `3c8cb40357ee23d13a2c1aa7e07e6848ff5256dd`.
- **Reuse:** P1/P2/P3 S1 giữ `DRAFT`, rights/technical/channel `UNVERIFIED`; S1 5 fixture historical không chạy lại. GROW-02A D1 dictionary mới chỉ đề xuất; A0 register GOV-01/S2 vẫn 5 `AWAITING_A0_DECISION`.
- **WRITE_SET:** branch `hermes/grow-01-s2-offline-package-handoff-2026-11-23`, chỉ task này, `reports/2026-11-23-hermes-grow01-s2-package-contract.md`, `reports/evidence/2026-11-23-hermes-grow01-s2-package-fixtures.json`, `sandbox/grow01-package-contract/**`. Không edit S1, PR #25/#27/#23/#16, STATE/CATALOG/CHANGELOG/main.
- **STOP:** tài khoản, OAuth, production, real asset rights/technical approval, render, publish, paid services, customer data, webhook, VPS. In-memory mocks không phải IAM, độ bền ledger hay publish gate thật.
- **Pass:** >=10 test chạy thật, 3 fixture/3 source refs, state transition fail-closed, no publish/cost path, remote SHA/blob readback. Next owner ChatGPT Điều phối; Work browser QA và Codex backend contract gate cần quyết định sau review, không giao mới từ task này.
