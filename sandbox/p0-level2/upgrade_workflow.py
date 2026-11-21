#!/usr/bin/env python3
"""Upgrade the existing private Level 1 workflow for Provider E2E only."""

from __future__ import annotations

import json
import sys
from pathlib import Path


VALIDATOR = """const b = $json.body ?? {};
const u = b.inference?.usage ?? {};
const valid = b.phase === 'callback' && typeof b.task_id === 'string' && typeof b.correlation_id === 'string' && b.status === 'provider_succeeded' && typeof b.result_hash === 'string' && /^[a-f0-9]{64}$/.test(b.result_hash) && b.result && typeof b.result.summary === 'string' && Array.isArray(b.result.signals) && b.result.signals.every(x => typeof x === 'string') && Array.isArray(b.result.recommendations) && b.result.recommendations.every(x => typeof x === 'string') && b.inference?.mode === 'openai' && b.inference?.paid === true && b.inference?.provider === 'openai' && typeof b.inference?.model === 'string' && (b.inference.model === 'gpt-6-luna' || b.inference.model.startsWith('gpt-6-luna-')) && Number.isInteger(u.input_tokens) && u.input_tokens >= 0 && u.input_tokens <= 4000 && Number.isInteger(u.output_tokens) && u.output_tokens >= 0 && u.output_tokens <= 2000 && typeof b.inference?.actual_cost_usd === 'number' && b.inference.actual_cost_usd >= 0 && b.inference.actual_cost_usd <= 0.01;
return [{ json: { valid, response: valid ? { ack: true, task_id: b.task_id, correlation_id: b.correlation_id, status: b.status, result_hash: b.result_hash, schema_valid: true, provider: b.inference.provider, model: b.inference.model, usage: u, actual_cost_usd: b.inference.actual_cost_usd } : { ack: false, status: 'invalid_callback', error: 'P0_OUTPUT_SCHEMA', schema_valid: false } } }];"""


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("usage: upgrade_workflow.py INPUT OUTPUT")
    source = Path(sys.argv[1])
    target = Path(sys.argv[2])
    workflows = json.loads(source.read_text(encoding="utf-8"))
    if not isinstance(workflows, list) or len(workflows) != 1:
        raise SystemExit("expected exactly one workflow")
    workflow = workflows[0]
    if workflow.get("id") != "ttdP0FakeAdsV1" or workflow.get("name") != "fake-ads-audit-v1":
        raise SystemExit("unexpected workflow identity")
    nodes = {node["id"]: node for node in workflow["nodes"]}
    nodes["validate-callback"]["parameters"]["jsCode"] = VALIDATOR
    call = nodes["call-reasoner"]
    call["parameters"]["options"] = {"timeout": 30000}
    call["retryOnFail"] = False
    call["maxTries"] = 1
    call["waitBetweenTries"] = 0
    workflow["active"] = True
    target.write_text(json.dumps(workflows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
