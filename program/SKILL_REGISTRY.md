# Skill and Tool Registry — candidate routing matrix

Date: 2026-11-23 | **Distinguish evidence from possibility.** Tools are session-dependent; A0 states all available permissions granted, so do not run generic capability surveys. If a specific task tool fails, record exact `BLOCKED_TECHNICAL` or `BLOCKED_SECURITY` and continue independent work.

Skill states: `EVIDENCED` = demonstrated with report/PR, `REPORTED` = in that agent's survey, `INSTALLABLE` = candidate, not installed/enabled/verified, `GATED` = requires technical or risk clearance. “Full skills” means any applicable actually present tool, not permission to claim uninstalled tools exist.

| Capability family / examples | A1 Chat Standard | A2 Chat Standard | Work | Hostinger | Suggested installation/addition (not automatically installed) |
|---|---|---|---|---|---|
| GitHub read/write, PR, diff, commit and SHA | EVIDENCED PR32/36 | Applicable; A2 untested | EVIDENCED QA comments | REPORTED survey | GitHub Actions validators, GitHub rulesets after review |
| Document analysis, roadmap, dependency modelling | EVIDENCED | Assigned primary; not yet evidenced | EVIDENCED multi-step QA | REPORTED | Document/Sheets skills where accessible |
| Python/JS/JSON/YAML, schema/test fixtures | EVIDENCED A1 tests | Applicable with execution environment | EVIDENCED Linux testing | sandbox code reported | JSON Schema, PyYAML, pytest, Ruff, link checker, secret scanner |
| Knowledge indexing, context packs, retrieval | Agent-based design skill | Usability reviewer | End-to-end QA | infra data author | local grep/ripgrep, deterministic index generator; semantic/RAG only if measured need |
| Web/UI browser interaction, accessibility | Connector-dependent | Connector-dependent | Environment-dependent Work/Computer Use | hPanel tools | Playwright, axe-core, browser automation *only where executable* |
| Hostinger hPanel, VPS/SSH/Docker/network | Not evidenced | Not evidenced | Environment-dependent | EVIDENCED provider inventory | Compose tooling, health/backup monitoring; any installation after preflight |
| WP/Woo content read and SEO review | A1 self-report, coordinator actual live WP read | Assigned primary using available connection | Integration QA | Hostinger hosting side | WordPress/Jetpack connector already available; Woo-specific connector only if needed |
| GA4, Ads, UTM/lead analytics | A1 self-reported Ads read | Assigned business/data analysis | Integrated multistep if tool available | Hosting diagnostics only | Supermetrics, GA4 official connectors only for verified field gaps |
| Google Drive/Docs/Sheets/Calendar/Gmail | A1 self-reported | Connector-dependent | Work multistep | Not provider specialty | Native connected apps, Sheets integration/SQL reporting |
| Media design, voice, video, social | A1 reported Canva/HeyGen/vidIQ | Content/measurement lead | Media pipeline execution | Storage/worker infra | Canva, HeyGen, ElevenLabs, Kling, vidIQ; verify credits/cost/scope |
| n8n, callbacks, DB state, workflow monitoring | Design/validator | Business acceptance | Integration/test | VPS runtime/health owner | n8n nodes, Postgres migration, Prometheus/Grafana/Uptime Kuma (candidates) |
| Testing, security/backup, QA evidence | Offline tests | Business QA | Independent Linux/UX QA | hPanel/VPS audit | Trivy, Gitleaks, restore-test scripts, pytest, CI |
| Agent session UI dispatch | No persistent chat control evidenced | No persistent chat control evidenced | PoC candidate only | Not specialized | Windows Desktop Session Controller + UI automation, test before adopting |

## Role expectations
**A1 — Knowledge Engineering & automation quality:** Git/validator/code, context packing, metadata consistency, branch-scoped tests, reuse evidence. May use connected Workspace/WordPress/Ads/media tools when relevant; not restricted to documentation.
**A2 — Product/Data & business operations:** goals/UI requirements, WordPress/SEO audit, attribution/Ads/GA4, content quality, business KPIs, acceptance criteria; script or use connected apps as needed. Assigned role ≠ proof of any specific A2 connector.
**Work — Integration/Experience & test:** UI prototype and real workflows, cross-app integration, Linux QA, browser or computer-use when available, author code and build when useful; independent reviewer must be different from author.
**Hostinger — Infrastructure/operations:** VPS/hPanel/Cloud WordPress, DNS/TLS, backups, Docker/n8n, security and recovery. A0 has lifted *general* PAUSED; historical frozen work is not auto-reassigned.
**Chat Điều phối — Orchestrator:** portfolio decisions, source conflict resolution, dependency/acceptance at roadmap scale; can itself execute suitable connected source tasks, not just administrative forwarding.
**Hermes — restricted**: WebUI terminal, files, Git, browser, memory, skills, session search (survey), separated from VPS runtime; HOLD due cost.
**Codex — restricted**: Windows shell, code/Git/Computer Use (survey), exception-only due cost.

## Installation decision rule
Prefer already connected tools. Install a skill/plugin/tool only if a specific work item demands a missing capability, data protection and costs are bounded, installation/environment can be rolled back, and permission is real. Record `SKILL_ID, provider, reason, status, cost, granted_scope, test_evidence`; never claim candidates already installed.
