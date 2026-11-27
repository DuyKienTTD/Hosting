#!/usr/bin/env bash
# Run as the operator on KVM2 with the staged H3 source. Never copy a repository
# Compose base over the live base. This override only recreates sandbox services.
set -euo pipefail
umask 077
export H3_DIR
H3_DIR=$(realpath "${1:?private H3 directory required}")
cd "${2:?live sandbox Compose directory required}"
real_ledger=${3:?real ledger path required for read-only baseline}
ledger="$H3_DIR/mock-ledger/level2-budget.json"
mkdir -m 700 "$H3_DIR/mock-ledger"
cp -p compose.yaml "$H3_DIR/base-compose.backup"
docker cp ttd-gate-a-bridge:/opt/ttd/state/bridge-tasks.json "$H3_DIR/bridge-state.backup"
chmod 600 "$H3_DIR/"*.backup
before=$(sha256sum "$real_ledger")
install -m 600 "$real_ledger" "$ledger"
task=h3-mock-$(cat /proc/sys/kernel/random/uuid)
fixture="$H3_DIR/src/fixture.json"
python3 -B "$H3_DIR/src/h3_mock.py" stage capture "$task" "$fixture"
python3 -B "$H3_DIR/src/prepare_mock_permit.py" "$ledger" "$fixture"
base=(docker compose -f compose.yaml)
test_compose=("${base[@]}" -f "$H3_DIR/src/compose.h3-mock.yaml")
proxy_check() {
    test "$(docker network inspect ttd-gate-b-guard-private --format '{{.Internal}} {{len .Containers}}')" = 'true 2'
    docker network inspect ttd-gate-b-guard-private --format '{{range .Containers}}{{println .Name}}{{end}}' |
        sed '/^$/d' | sort | diff - <(printf '%s\n' ttd-gate-a-guard ttd-p0-provider-egress)
}
rollback() {
    "${base[@]}" up -d --no-deps --wait --wait-timeout 35 guard provider-mock &&
        cmp -s compose.yaml "$H3_DIR/base-compose.backup" && proxy_check &&
        test "$before" = "$(sha256sum "$real_ledger")" && echo H3_ROLLBACK_PASS
}
"${test_compose[@]}" config --quiet
proxy_check
trap rollback EXIT
"${test_compose[@]}" up -d --no-deps --wait --wait-timeout 35 guard provider-mock
proxy_check
docker exec ttd-gate-a-guard python3 -B /h3/h3_mock.py negatives /h3/fixture.json "$task"
test -z "$(docker logs ttd-gate-a-provider-mock 2>&1 | grep '"h3_received"' || true)"
docker exec -i ttd-gate-a-bridge python3 - "$task" "corr-$task" < "$H3_DIR/src/one_shot_e2e_test.py"
docker logs ttd-gate-a-provider-mock 2>&1 | grep '"h3_received"' > "$H3_DIR/provider-evidence.jsonl"
python3 - "$ledger" "$task" "$fixture" "$H3_DIR/provider-evidence.jsonl" <<'PY'
import hashlib
import json
import sys
from pathlib import Path

ledger, task_id, fixture, evidence = sys.argv[1:]
state = json.loads(Path(ledger).read_bytes())
task = state["tasks"][task_id]
hits = [json.loads(line) for line in Path(evidence).read_text().splitlines()]
digest = hashlib.sha256(Path(fixture).read_bytes()).hexdigest()
permit = state["one_shot_permits"][task_id]
assert hits == [{"h3_received": True, "wire_sha256": digest, "consumed_and_reserved_on_receipt": True}]
assert permit["state"] == "consumed" and permit["fingerprint"] == digest
assert task["state"] == "usage_recorded" and state["kill_switch"] is True
assert task["reserved_usd"] == 0.0035
print(json.dumps({"h3_combined": "PASS", "physical_mock_requests": len(hits),
                  "wire_sha256": digest, "mock_usage": task["mock_usage"],
                  "provider_input_tokens_verified": False}))
PY
rollback
trap - EXIT
