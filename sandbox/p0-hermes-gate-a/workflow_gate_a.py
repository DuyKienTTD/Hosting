#!/usr/bin/env python3
"""Convert the current private P0 workflow validator to GATE A mock semantics."""

from __future__ import annotations

import json
import sys
from pathlib import Path


VALIDATOR = """const b = $json.body ?? {};
const i = b.inference ?? {};
const u = i.runtime ?? {};
const valid = b.phase === 'callback' && typeof b.task_id === 'string' && typeof b.correlation_id === 'string' && b.status === 'hermes_mock_succeeded' && typeof b.result_hash === 'string' && /^[a-f0-9]{64}$/.test(b.result_hash) && b.result && typeof b.result.summary === 'string' && Array.isArray(b.result.signals) && b.result.signals.every(x => typeof x === 'string') && Array.isArray(b.result.recommendations) && b.result.recommendations.every(x => typeof x === 'string') && i.mode === 'hermes_mock' && i.paid === false && i.provider === 'gate-a-provider-mock' && i.model === 'gpt-6-luna' && i.hard_max_output_tokens === 600 && Number.isInteger(i.input_upper_bound_tokens) && i.input_upper_bound_tokens >= 0 && i.input_upper_bound_tokens <= 4000 && i.tools_enabled === false && i.physical_requests === 1 && u.provider === 'openai-api' && u.model === 'gpt-6-luna';
return [{ json: { valid, response: valid ? { ack: true, task_id: b.task_id, correlation_id: b.correlation_id, status: b.status, result_hash: b.result_hash, schema_valid: true, mode: i.mode, paid: false, provider: i.provider, model: i.model, input_upper_bound_tokens: i.input_upper_bound_tokens, hard_max_output_tokens: i.hard_max_output_tokens, tools_enabled: false, physical_requests: 1 } : { ack: false, status: 'invalid_callback', error: 'P0_GATE_A_OUTPUT_SCHEMA', schema_valid: false } } }];"""


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("usage: workflow_gate_a.py INPUT OUTPUT")
    source, target = map(Path, sys.argv[1:])
    workflows = json.loads(source.read_text(encoding="utf-8"))
    if not isinstance(workflows, list) or len(workflows) != 1:
        raise SystemExit("expected one workflow")
    workflow = workflows[0]
    nodes = {node["id"]: node for node in workflow["nodes"]}
    required = {"validate-callback", "call-reasoner"}
    if not required.issubset(nodes):
        raise SystemExit("unexpected workflow shape")
    nodes["validate-callback"]["parameters"]["jsCode"] = VALIDATOR
    call = nodes["call-reasoner"]
    call["parameters"]["url"] = "http://reasoner-p0:8080/v1/reason"
    call["parameters"]["options"] = {"timeout": 30000}
    call["retryOnFail"] = False
    call["maxTries"] = 1
    call["waitBetweenTries"] = 0
    workflow["active"] = True
    target.write_text(json.dumps(workflows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
