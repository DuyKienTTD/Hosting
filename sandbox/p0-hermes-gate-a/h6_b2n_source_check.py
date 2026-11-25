"""Compare public B2-H evidence with pinned sources. No service startup or requests."""

import argparse
import ast
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
B2H = ROOT / "reports/evidence/2026-11-22-ttd-hermes-gate-b-h6-b2-h-read-only.json"
IMAGE_FILES = {
    "hermes_agent": "run_agent.py",
    "hermes_gateway": "api_server.py",
    "hermes_gateway_routes": "api_server_openai_routes.py",
}


def digest(data):
    return sha256(data).hexdigest()


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()


def source_bytes(path):
    return path.read_bytes().replace(b"\r\n", b"\n")


def workflow_candidate():
    seed = ROOT / "sandbox/p0-level1/fake-ads-audit-v1.workflow.json"
    with TemporaryDirectory() as tmp:
        target = Path(tmp) / "candidate.json"
        # Applies the public transform to the public seed containing a placeholder bearer.
        subprocess.run([sys.executable, "-B", str(HERE / "workflow_gate_a.py"), str(seed), str(target)],
                       check=True, timeout=10)
        workflow, = json.loads(target.read_bytes())
    return workflow


def evaluate_candidate(workflow):
    nodes = {node["id"]: node for node in workflow["nodes"]}
    call = nodes["call-reasoner"]
    assignment = {"auth": nodes["auth-router"]["parameters"]["jsCode"],
                  "validate": nodes["validate-callback"]["parameters"]["jsCode"]}
    node_program = """
const assert = require("node:assert/strict");
const fs = require("node:fs");
const src = JSON.parse(fs.readFileSync(0, "utf8"));
const authorize = new Function("$input", src.auth);
const validate = new Function("$json", src.validate);
const body = {phase: "callback", task_id: "fake-task", correlation_id: "fake-job",
  status: "hermes_mock_succeeded", result_hash: "a".repeat(64),
  result: {summary: "fixture", signals: [], recommendations: []},
  inference: {mode: "hermes_mock", paid: false, provider: "gate-a-provider-mock",
    model: "gpt-6-luna", hard_max_output_tokens: 600, input_upper_bound_tokens: 100,
    tools_enabled: false, physical_requests: 1, run_id_hash: "b".repeat(64),
    runtime: {provider: "openai-api", model: "gpt-6-luna"}}};
const auth = headers => authorize({first: () => ({json: {headers, body}})})[0].json.authorized;
const valid = (candidate) => validate({body: candidate})[0].json.valid;
const checks = {
  mock_success_accepted: valid(body),
  missing_bearer_rejected_by_router: !auth({}),
  wrong_bearer_rejected_by_router: !auth({authorization: "Bearer fixture-wrong"}),
  placeholder_bearer_accepted_by_router: auth({authorization: "Bearer __P0_TOKEN__"}),
  paid_success_rejected: !valid({...body, status: "paid_succeeded", inference: {...body.inference, paid: true}}),
  unknown_outcome_rejected: !valid({...body, status: "outcome_unknown"}),
  malformed_hash_rejected: !valid({...body, result_hash: "invalid"}),
  well_shaped_unbound_hash_accepted: valid({...body, result_hash: "c".repeat(64)}),
  different_task_correlation_and_run_accepted: valid({...body, task_id: "other", correlation_id: "other",
    inference: {...body.inference, run_id_hash: "d".repeat(64)}}),
  reexecuted_validator_accepts_same_shape: valid(body) && valid(body)
};
for (const [name, pass] of Object.entries(checks)) assert.ok(pass, name);
process.stdout.write(JSON.stringify(checks));
"""
    result = subprocess.run(["node", "-e", node_program], input=canonical(assignment), capture_output=True,
                            check=True, timeout=10)
    return {"workflow_id": workflow["id"], "public_candidate_sha256": digest(canonical(workflow)),
            "validator_sha256": digest(assignment["validate"].encode()),
            "reasoner_timeout_ms": call["parameters"]["options"]["timeout"], "retry": call["retryOnFail"],
            "checks": json.loads(result.stdout)}


def summarize_image(source_dir, expected):
    observed = {name: digest((source_dir / path).read_bytes()) for name, path in IMAGE_FILES.items()}
    routes = (source_dir / IMAGE_FILES["hermes_gateway_routes"]).read_text(encoding="utf-8")
    api = (source_dir / IMAGE_FILES["hermes_gateway"]).read_text(encoding="utf-8")
    scopes = []
    for file in (routes, api):
        for node in ast.walk(ast.parse(file)):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and (
                    "idempot" in node.name.lower() or node.name in ("_handle_create_run", "_handle_run_status")):
                scopes.append(node.name)
    result = {"sha256": observed, "matching_b2h": {name: value == expected[name] for name, value in observed.items()},
              "run_idempotency_source_symbols": sorted(set(scopes))}
    runs_path = source_dir / "api_server_runs.py"
    if runs_path.is_file():
        raw = runs_path.read_bytes()
        tree = ast.parse(raw)
        route = next(n for n in tree.body if isinstance(n, ast.AsyncFunctionDef) and n.name == "_handle_runs")
        calls = sorted((n.lineno, ast.unparse(n.func)) for n in ast.walk(route) if isinstance(n, ast.Call))
        replay = next(n.lineno for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "_replay_or_conflict")
        lookup = next(line for line, name in calls if name == "self._run_idempotency_store.lookup")
        reserve = next(line for line, name in calls if name == "self._run_idempotency_store.reserve")
        launch = next(line for line, name in calls if name == "asyncio.create_task")
        result["runs_module"] = {"sha256": digest(raw), "has_b2h_hash": False,
                                 "lookup_before_reserve_before_launch": lookup < reserve < launch,
                                 "handler_lines": {"lookup": lookup, "reserve": reserve, "launch": launch,
                                                   "replay_or_conflict": replay}}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image-sources", type=Path, help="read-only files extracted from the pinned public image")
    args = parser.parse_args()
    live = json.loads(B2H.read_bytes())["verified_live"]
    bridge = source_bytes(HERE / "bridge.py")
    tree = ast.parse(bridge)
    run = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "run_hermes")
    strings = {n.value for n in ast.walk(run) if isinstance(n, ast.Constant) and isinstance(n.value, str)}
    print(json.dumps({
        "bridge_source_matches_b2h": digest(bridge) == live["source_sha256"]["bridge"],
        "bridge_runs_create_and_poll": {"/v1/runs", "/v1/runs/", "Idempotency-Key"} <= strings,
        "public_n8n_candidate": evaluate_candidate(workflow_candidate()),
        "hermes_image_sources": summarize_image(args.image_sources, live["source_sha256"])
        if args.image_sources else None,
        "execution": "source-only; no Hermes, n8n or fake-provider process",
    }, indent=2))


if __name__ == "__main__":
    main()
