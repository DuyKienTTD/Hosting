"""Run in a disposable Linux container with --network none, using only synthetic data."""

import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

import h6_writer as writer
import one_shot
from h6_stage_a_test import check_impostor, check_peers, state, wait_until
from mock_contract import encode, usage_from_response

TASK = "synthetic-gate-b"
SCOPE = {"task_id": TASK, "key_hash": "a" * 64, "fingerprint": "b" * 64}
LEGACY = "synthetic-level2"
HISTORY = {"state": "complete", "result_hash": "c" * 64, "model": one_shot.MODEL,
           "response_id_hash": "d" * 64, "actual_cost_usd": 0.00005,
           "usage": {"input_tokens": 25, "cached_input_tokens": 0, "output_tokens": 8, "reasoning_tokens": 0},
           "legacy_extension": {"note": "\u0111\u1eef li\u1ec7u gi\u1ea3"}}


def level2_adapter(source, ledger):
    spec = importlib.util.spec_from_file_location("b2a_level2", source)
    adapter = importlib.util.module_from_spec(spec)
    environment = {"P0_MODE": "openai", "P0_TOKEN": "fixture-authorization" * 2,
                   "OPENAI_API_KEY": "fixture-placeholder-only", "P0_BUDGET_PATH": str(ledger),
                   "P0_CALLBACK_URL": "http://n8n-p0-sandbox:5678/synthetic"}
    with patch.dict(os.environ, environment):
        spec.loader.exec_module(adapter)

    def forbid_network(*args, **kwargs):
        raise AssertionError("network dispatch forbidden in ledger interop test")

    adapter.provider_request = forbid_network
    adapter.send_callback = forbid_network
    return adapter


def seed(source, path):
    adapter = level2_adapter(source, path)
    assert adapter.admit(LEGACY, "e" * 64)[0] == "admitted"
    adapter.update_task(LEGACY, HISTORY, HISTORY["actual_cost_usd"])
    with adapter.locked_ledger() as ledger:
        ledger["kill_switch"] = True  # This is an isolated fixture created by the actual Level 2 code.
        ledger["h6_stage_a_fixture"] = True
        ledger["future_field"] = {"label": "synthetic-only"}
        ledger["days"][adapter.utc_day()]["day_extension"] = ["preserve"]
        ledger["one_shot_permits"] = {TASK: {
            "state": "ready", "key_hash": SCOPE["key_hash"], "fingerprint": SCOPE["fingerprint"],
            "model": adapter.MODEL, "mock_input_tokens": 321, "permit_extension": "preserve",
            "expires_at": (datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat(),
        }}


def adapter_write(source, path):
    adapter = level2_adapter(source, path)
    atomic_write = adapter.atomic_write

    def wait_while_locked(path, value):
        print("locked", flush=True)
        assert sys.stdin.readline().strip() == "release"
        atomic_write(path, value)

    with patch.object(adapter, "atomic_write", wait_while_locked):
        adapter.update_task(LEGACY, {"concurrent_level2": True}, 0.00001)
    try:
        adapter.admit("synthetic-new", "f" * 64)
    except RuntimeError as error:
        assert str(error) == "P0_KILL_SWITCH"
    else:
        raise AssertionError("unexpected Level 2 admission")


def run_as(uid, *args, **kwargs):
    return subprocess.Popen([sys.executable, "-B", __file__, *map(str, args)],
                            user=uid, group=writer.IPC_GID, extra_groups=[], **kwargs)


def rpc(address, op, **fields):
    with run_as(writer.GUARD_UID, "rpc", address, op, json.dumps(fields),
                stdout=subprocess.PIPE, text=True) as process:
        output, _ = process.communicate(timeout=8)
    assert process.returncode == 0
    return json.loads(output)


def rpc_child(address, op, fields):
    try:
        result = writer.call(address, op, **json.loads(fields))
    except (OSError, ValueError, RuntimeError):
        result = None
    print(json.dumps(result))


def new_case(root, source):
    root.mkdir(mode=0o755)
    ipc = root / "ipc"
    ledger = root / "mock-ledger"
    for path, mode in ((ipc, 0o750), (ledger, 0o700)):
        path.mkdir(mode=mode)
        os.chown(path, writer.WRITER_UID, writer.IPC_GID)
    path = ledger / writer.FIXTURE_PATH.name
    with run_as(writer.WRITER_UID, "seed", source, path) as process:
        assert process.wait(timeout=8) == 0
    return ipc / "writer.sock", path


@contextmanager
def serving(address, path, action="normal"):
    with run_as(writer.WRITER_UID, action, address, path) as process:
        try:
            wait_until(lambda: address.exists() and rpc(address, "snapshot") is not None)
            yield
        finally:
            if process.poll() is None:
                process.terminate()
            process.wait(timeout=8)


def observed_writer(address, path):
    lock = one_shot.fcntl.flock

    def observed_lock(fd, operation):
        descriptor = fd if isinstance(fd, int) else fd.fileno()
        if os.readlink(f"/proc/self/fd/{descriptor}") == str(path.with_suffix(".json.lock")):
            (address.parent / "writer-at-lock").touch()
        return lock(fd, operation)

    with patch.object(one_shot.fcntl, "flock", observed_lock):
        writer.serve(address, path)


def interop(case, source):
    address, path = new_case(case, source)
    lock_inode = path.with_suffix(".json.lock").stat().st_ino
    initial = state(path)
    with serving(address, path, "observed"), path.open("rb") as old:
        check_peers(address)
        with run_as(writer.WRITER_UID, "adapter_write", source, path, stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE, text=True) as adapter:
            assert adapter.stdout.readline().strip() == "locked"
            with ThreadPoolExecutor(max_workers=4) as pool:
                calls = [pool.submit(rpc, address, "admit", **SCOPE) for _ in range(4)]
                try:
                    wait_until(lambda: (address.parent / "writer-at-lock").exists())
                    assert not any(call.done() for call in calls) and state(path) == initial
                finally:
                    adapter.stdin.write("release\n")
                    adapter.stdin.flush()
                assert sum(call.result() is True for call in calls) == 1
            assert adapter.wait(timeout=8) == 0
        written = state(path)
        assert json.load(old) == initial and os.fstat(old.fileno()).st_ino != path.stat().st_ino
        assert path.with_suffix(".json.lock").stat().st_ino == lock_inode
        assert rpc(address, "snapshot")["sha256"] == hashlib.sha256(path.read_bytes()).hexdigest()
        assert written["tasks"][LEGACY] == dict(initial["tasks"][LEGACY], concurrent_level2=True)
        assert written["future_field"] == initial["future_field"]
        day = written["tasks"][TASK]["day"]
        assert written["days"][day] == {"attempts": 2, "reserved_usd": 0.007,
                                        "actual_usd": 0.00006, "day_extension": ["preserve"]}
        assert written["actual_usd"] == 0.00006 and written["reserved_usd"] == 0.007
        assert written["schema_version"] == 1 and written["kill_switch"] is True
        assert written["one_shot_permits"][TASK]["permit_extension"] == "preserve"
        assert written["one_shot_permits"][TASK]["state"] == "consumed"
        settlement = {"task_id": TASK, "fingerprint": SCOPE["fingerprint"],
                      "outcome": "outcome_unknown", "usage": None}
        assert rpc(address, "settle", **settlement) is True
        terminal = path.read_bytes()
        assert rpc(address, "settle", **settlement) is True and path.read_bytes() == terminal
        assert rpc(address, "settle", **dict(settlement, usage={"unexpected": 1})) is None
        assert state(path)["tasks"][TASK]["state"] == "outcome_unknown"
        assert state(path)["actual_usd"] == written["actual_usd"] and state(path)["reserved_usd"] == 0.007
    with serving(address, path):
        assert rpc(address, "admit", **SCOPE) is None
        assert rpc(address, "settle", **settlement) is True
        assert path.read_bytes() == terminal


def known_settlement(root, source):
    address, path = new_case(root, source)
    synthetic = {"id": "synthetic", "model": one_shot.MODEL, "status": "completed", "service_tier": "default",
                 "usage": {"input_tokens": 321, "output_tokens": 21, "total_tokens": 342,
                           "input_tokens_details": {"cached_tokens": 0},
                           "output_tokens_details": {"reasoning_tokens": 0}}}
    usage = usage_from_response(encode(synthetic), False)
    settlement = {"task_id": TASK, "fingerprint": SCOPE["fingerprint"],
                  "outcome": "usage_recorded", "usage": usage}
    with serving(address, path):
        assert rpc(address, "admit", **SCOPE) is True
        assert rpc(address, "settle", **settlement) is True
        terminal = path.read_bytes()
        assert state(path)["tasks"][TASK]["mock_usage"] == usage
        assert state(path)["actual_usd"] == 0.00005 and state(path)["reserved_usd"] == 0.007
    with serving(address, path):
        assert rpc(address, "settle", **settlement) is True
        assert rpc(address, "settle", **dict(settlement, outcome="outcome_unknown", usage=None)) is None
        assert path.read_bytes() == terminal


def injected_writer(address, path, phase):
    durable = one_shot._durable_write
    if phase == "before_fsync":
        with patch.object(one_shot.os, "fsync", side_effect=lambda fd: os._exit(31)):
            writer.serve(address, path)
    else:
        def commit_then_exit(path, ledger):
            durable(path, ledger)
            os._exit(32)

        with patch.object(one_shot, "_durable_write", commit_then_exit):
            writer.serve(address, path)


def crashes(root, source):
    for phase, code in (("before_fsync", 31), ("after_commit", 32)):
        address, path = new_case(root / phase, source)
        initial = path.read_bytes()
        with run_as(writer.WRITER_UID, phase, address, path) as process:
            wait_until(lambda: address.exists() and rpc(address, "snapshot") is not None)
            assert rpc(address, "admit", **SCOPE) is None
            assert process.wait(timeout=8) == code
        if phase == "before_fsync":
            assert path.read_bytes() == initial
        else:
            assert state(path)["tasks"][TASK]["state"] == "inflight"
            assert state(path)["one_shot_permits"][TASK]["state"] == "consumed"
            assert state(path)["reserved_usd"] == 0.007
            with serving(address, path):
                assert rpc(address, "admit", **SCOPE) is None


def rejected_inputs(root, source):
    address, path = new_case(root, source)
    with serving(address, path):
        good = path.read_bytes()
        ledger = json.loads(good)
        day, day_row = next(iter(ledger["days"].items()))
        cases = [b"{bad", good.replace(b'"attempts":1', b'"attempts":1,"attempts":2', 1),
                 good.replace(b'"reserved_usd":0.0035', b'"reserved_usd":1e999', 1),
                 None, encode(dict(ledger, schema_version=2)), encode(dict(ledger, h6_stage_a_fixture=False)),
                 encode(dict(ledger, kill_switch=False)), encode(dict(ledger, attempts=5)),
                 encode(dict(ledger, reserved_usd=0.049)), encode(dict(ledger, actual_usd=0.049)),
                 encode(dict(ledger, days={day: dict(day_row, reserved_usd=0.005)})),
                 encode(dict(ledger, one_shot_permits=dict(ledger["one_shot_permits"], extra={})))]
        for payload in cases:
            if payload is None:
                path.unlink()
            else:
                path.write_bytes(payload)
                os.chown(path, writer.WRITER_UID, writer.IPC_GID)
            assert rpc(address, "admit", **SCOPE) is None
            assert (path.read_bytes() if path.exists() else None) == payload
        path.write_bytes(good)
        assert rpc(address, "admit", **dict(SCOPE, fingerprint="e" * 64)) is None
        assert path.read_bytes() == good
        old = path.with_name("old-fixture")
        path.rename(old)
        path.symlink_to(old)
        assert rpc(address, "snapshot") is None and rpc(address, "admit", **SCOPE) is None
        assert old.read_bytes() == good
        return len(cases) + 2


def main(source):
    assert os.geteuid() == 0 and set(os.listdir("/sys/class/net")) == {"lo"}
    assert not Path("/run/secrets/openai_provider_api_key").exists()
    with tempfile.TemporaryDirectory(prefix="h6-b2a-") as tmp:
        root = Path(tmp)
        root.chmod(0o755)
        check_impostor(root)
        interop(root / "interop", source)
        known_settlement(root / "known", source)
        crashes(root, source)
        denied = rejected_inputs(root / "invalid", source)
    print(json.dumps({"result": "PASS", "schema_version": 1, "concurrent_h6": 4,
                      "crash_cases": 2, "rejection_cases": denied, "provider_operations": 0}))


if __name__ == "__main__":
    command, *arguments = sys.argv[1:]
    if command == "test":
        main(Path(arguments[0]).resolve(strict=True))
    elif command == "seed":
        seed(Path(arguments[0]), Path(arguments[1]))
    elif command == "adapter_write":
        adapter_write(Path(arguments[0]), Path(arguments[1]))
    elif command == "rpc":
        rpc_child(*arguments)
    elif command == "observed":
        observed_writer(*(Path(item) for item in arguments))
    elif command == "normal":
        writer.serve(*(Path(item) for item in arguments))
    elif command in {"before_fsync", "after_commit"}:
        injected_writer(*(Path(item) for item in arguments), command)
    else:
        raise SystemExit("expected test command and Level 2 adapter source")
