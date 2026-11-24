# Hosting — KNG-01 knowledge entry

**Priority (A0, 2026-11-23): KNG-01 ONLY.** G0/UC01/UI/Ads/media/infra ngoài KNG đang hold, không tự gửi việc mới. [Canonical candidate current routing](program/current.json), [WBS 32 IDs](program/WORK_BREAKDOWN.md), [A1 roadmap](program/roadmaps/a1.md). Candidate không cấp quyền production, chi phí, merge hay tự tạo Work ACK.

**Mandatory for every new task:** read complete [AGENTS.md](AGENTS.md), [AGENT_WORKFLOW.md](rules/AGENT_WORKFLOW.md), [REPOSITORY_SECURITY.md](rules/REPOSITORY_SECURITY.md), [STATE.md](STATE.md), relevant agent profile and exact task/evidence at pinned SHA. Do not skip full security rules or replace source with short summaries. CATALOG is a machine-validated registry: consult only the relevant IDs/paths; do not load its full contents into every Agent context. [PROJECT charter](PROJECT.md).

**Authoritative facts:** current KNG owner/route in `program/current.json` only after A0-authorized main merge; current task receipts need real ACK. Historical Git/QA evidence in [reports](reports/) and [tasks](tasks/); [CATALOG](CATALOG.yaml) for stable IDs. Live VPS/WordPress/Ads state requires fresh authorized read, not Git inference.

**Security:** the full [Repository Security rule](rules/REPOSITORY_SECURITY.md) is authoritative; this quick-start does not duplicate or supersede any clause. STOP unapproved live/paid/production/merge/force-push. Reuse prior verified tests, validate diff and readback.

**Previous full README** remains retrievable at [main `e385c1be`](https://github.com/DuyKienTTD/Hosting/blob/e385c1bea2070973e3007e5717f7e980348d6ab3/README.md).
