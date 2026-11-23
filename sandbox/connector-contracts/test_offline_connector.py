"""Run only S1 contract/recovery cases, including actual process termination."""

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest

from offline_connector import Conflict, InvalidContract, OfflineAdapter, sha, temporary_sandbox


CASES = {}
CRASH_CODE = 86


def deny_network(event, _):
    if event.startswith("socket."):
        raise RuntimeError("network audit boundary")


def request(mode="success"):
    return {"schema_version": 1, "synthetic": True, "idempotency_key": "fake-demo", "channel": "fixture",
            "source": "synthetic", "approval": "synthetic_approved", "budget": {"max_dispatches": 1, "max_units": 1},
            "deadline_ms": 20, "payload": {"mode": mode}}


class OfflineContractTests(unittest.TestCase):
    def setUp(self):
        self.adapter = self.enterContext(temporary_sandbox())

    def job(self, mode="success"):
        return self.adapter.admit(request(mode), 0)["job_id"]

    def assert_terminal(self, job, outcome, dispatches):
        row = self.adapter.snapshot(job)
        self.assertEqual((row["state"], row["outcome"], row["fake_dispatches"]), (outcome, outcome, dispatches))
        self.assertEqual(row["fake_units"], dispatches)
        events = [item["event"] for item in row["audit"]]
        self.assertEqual(events.count("fake_dispatch"), dispatches)
        self.assertEqual(events.count("receipt_committed"), 1)
        self.assertEqual(events.count("receipt_ack"), 1)
        self.assertLess(events.index("receipt_committed"), events.index("receipt_ack"))
        self.assertEqual(row["receipt"]["event_sha256"], sha(row["callback"]))
        return {"outcome": outcome, "dispatches": dispatches, "receipts": 1,
                "job_id": job, "receipt_id": row["receipt"]["receipt_id"], "audit": row["audit"]}

    def test_contract_and_offline_boundary(self):
        accepted = self.adapter.admit(request(), 0)
        self.assertEqual((accepted["http"], accepted["request_sha256"]), (202, sha(request())))
        self.assertEqual(self.adapter.snapshot(accepted["job_id"])["state"], "pending")
        rejected = {"missing": {k: v for k, v in request().items() if k != "source"},
                    "mode": request() | {"payload": {"mode": "actual"}},
                    "unapproved": request() | {"approval": "pending"},
                    "budget": request() | {"budget": {"max_dispatches": 2, "max_units": 1}},
                    "deadline": request() | {"idempotency_key": "fake-expired", "deadline_ms": 0},
                    "real_channel": request() | {"channel": "ads"},
                    "real_key": request() | {"idempotency_key": "account-key"},
                    "endpoint": request() | {"endpoint": "https://invalid.example"},
                    "credentials": request() | {"credentials": "rejected-placeholder"}}
        for name, candidate in rejected.items():
            with self.subTest(name=name), self.assertRaises(InvalidContract):
                self.adapter.admit(candidate, 0)
        with self.assertRaises(InvalidContract):
            OfflineAdapter(self.adapter.root, endpoint="https://invalid.example")
        with self.assertRaises(InvalidContract):
            OfflineAdapter(self.adapter.root, credentials="rejected-placeholder")
        with self.assertRaises(InvalidContract):
            OfflineAdapter(Path.cwd())
        with self.assertRaisesRegex(RuntimeError, "network audit boundary"):
            sys.audit("socket.connect", None, None)
        CASES["contract"] = {"expected": "202 for valid synthetic admission and deny invalid schema/network/credentials",
                             "observed": {"admission": 202, "rejected": list(rejected), "endpoint_config_denied": True,
                                          "credential_config_denied": True, "nonfixture_storage_denied": True,
                                          "socket_audit_self_check": "denied"}}

    def test_success_replay_and_key_conflict(self):
        job = self.job()
        self.adapter.process(job, 1)
        before = self.adapter.snapshot(job)
        repeated = self.adapter.admit(request(), 50)
        self.assertEqual(repeated, {"http": 200, "job_id": job, "request_sha256": sha(request()), "replayed": True})
        with self.assertRaises(Conflict) as failure:
            self.adapter.admit(request("failure"), 2)
        self.assertEqual(failure.exception.http_status, 409)
        self.assertEqual(self.adapter.process(job, 51), before)
        self.assertEqual(self.adapter.receive_callback(before["callback"], 51), before["receipt"])
        self.assertEqual(self.adapter.snapshot(job), before)
        CASES["success_replay_conflict"] = {"expected": "completed, one dispatch/receipt, stable replay and conflict 409",
                                           "observed": self.assert_terminal(job, "completed", 1) |
                                           {"conflict_http": 409, "replay_http": 200, "unchanged": True}}

    def test_known_failure(self):
        job = self.job("failure")
        self.adapter.process(job, 1)
        CASES["known_failure"] = {"expected": "failed with one dispatch and one receipt",
                                  "observed": self.assert_terminal(job, "failed", 1)}

    def test_timeout_rejects_late_result_and_conflicting_callback(self):
        job = self.job("timeout")
        self.adapter.process(job, 1)
        row = self.adapter.snapshot(job)
        self.assertEqual(row["callback"]["occurred_ms"], row["deadline_ms"])
        with self.assertRaises(Conflict):
            self.adapter.settle(job, row["request_sha256"], "completed", 21)
        with self.assertRaises(Conflict):
            self.adapter.receive_callback(row["callback"] | {"outcome": "completed"}, 21)
        self.assertEqual(self.adapter.process(job, 22), row)
        self.assertEqual(self.adapter.receive_callback(row["callback"], 22), row["receipt"])
        self.assertEqual(self.adapter.snapshot(job), row)
        CASES["timeout_and_late_result"] = {"expected": "unknown at deadline, reject late settlement/callback, no redispatch",
                                           "observed": self.assert_terminal(job, "outcome_unknown", 1) |
                                           {"deadline_ms": 20, "late_settlement_rejected": True,
                                            "conflicting_callback_rejected": True, "same_receipt": True}}

    def test_deadline_before_dispatch(self):
        job = self.job()
        self.adapter.process(job, 20)
        CASES["expired_pending"] = {"expected": "unknown with no dispatch and one receipt",
                                    "observed": self.assert_terminal(job, "outcome_unknown", 0)}

    def test_rejects_missing_or_forged_callback_before_receipt(self):
        job = self.job()
        self.worker_process(job, 1, "sending_before_receipt", CRASH_CODE)
        before = self.adapter.snapshot(job)
        event = before["callback"]
        self.assertIsNone(before["receipt"])
        with self.assertRaises(InvalidContract):
            self.adapter.receive_callback({k: v for k, v in event.items() if k != "callback_id"}, 2)
        forged = event | {"request_sha256": "0" * 64}
        binding = {k: v for k, v in forged.items() if k != "callback_id"}
        forged["callback_id"] = "callback-" + sha(binding)
        with self.assertRaises(Conflict):
            self.adapter.receive_callback(forged, 2)
        self.assertEqual(self.adapter.snapshot(job), before)
        self.worker_process(job, 3)
        CASES["callback_identity"] = {"expected": "missing and forged identities rejected before valid recovery",
                                      "observed": self.assert_terminal(job, "completed", 1) |
                                      {"missing_http": 422, "mismatch_http": 409, "state_unchanged": True}}

    def test_worker_lock_prevents_live_recovery(self):
        job = self.job()
        with self.adapter.worker(), self.assertRaises(Conflict):
            self.adapter.process(job, 1)
        self.assertEqual(self.adapter.snapshot(job)["state"], "pending")
        CASES["worker_lock"] = {"expected": "another worker cannot recover while lock is held",
                                "observed": {"recovery_denied": True, "state": "pending", "dispatches": 0}}

    def worker_process(self, job, tick, fault="none", expected_code=0):
        cmd = [sys.executable, "-B", __file__, "--worker", str(self.adapter.root), job, str(tick), fault]
        run = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        self.assertEqual(run.returncode, expected_code, run.stderr)
        started = json.loads(run.stdout)
        self.assertNotEqual(started["pid"], os.getpid())
        return started["pid"]

    def test_cold_restart_windows(self):
        windows = {"working_before_dispatch": ("working", 0, False, "outcome_unknown"),
                   "working_after_dispatch": ("working", 1, False, "outcome_unknown"),
                   "sending_before_receipt": ("sending", 1, False, "completed"),
                   "sending_after_receipt": ("sending", 1, True, "completed")}
        for fault, (state, dispatches, committed, outcome) in windows.items():
            with self.subTest(fault=fault):
                input_doc = request() | {"idempotency_key": "fake-" + fault.replace("_", "-")}
                job = self.adapter.admit(input_doc, 0)["job_id"]
                crash_pid = self.worker_process(job, 1, fault, CRASH_CODE)
                before = self.adapter.snapshot(job)
                self.assertEqual((before["state"], before["fake_dispatches"], before["receipt"] is not None),
                                 (state, dispatches, committed))
                recovery_pid = self.worker_process(job, 2)
                self.assertNotEqual(crash_pid, recovery_pid)
                row = self.adapter.snapshot(job)
                replay = self.adapter.admit(input_doc, 3)
                self.assertEqual(replay["job_id"], job)
                self.assertTrue(replay["replayed"])
                self.assertEqual(self.adapter.process(job, 4), row)
                if committed:
                    self.assertEqual(before["receipt"], row["receipt"])
                CASES[fault] = {"expected": {"interrupted_state": state, "outcome": outcome,
                                            "dispatches": dispatches, "receipts": 1},
                                "observed": self.assert_terminal(job, outcome, dispatches) |
                                {"interrupted_state": before["state"], "receipt_committed_before_crash": committed,
                                 "same_receipt_on_recovery": row["receipt"] == before["receipt"] if committed else None,
                                 "crash_exit": CRASH_CODE, "crash_pid": crash_pid, "recovery_pid": recovery_pid,
                                 "replay_same_job": True}}


def run_worker(root, job, tick, fault):
    def checkpoint(name):
        if name == fault:
            os._exit(CRASH_CODE)

    print(json.dumps({"pid": os.getpid()}), flush=True)
    OfflineAdapter(root).process(job, int(tick), checkpoint)


if __name__ == "__main__":
    sys.addaudithook(deny_network)
    if len(sys.argv) == 6 and sys.argv[1] == "--worker":
        run_worker(*sys.argv[2:])
    else:
        parser = argparse.ArgumentParser(description=__doc__)
        parser.add_argument("--evidence", type=Path)
        args = parser.parse_args()
        result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(OfflineContractTests))
        if args.evidence and result.wasSuccessful():
            args.evidence.write_text(json.dumps({"tests_run": result.testsRun, "cases": CASES}, indent=2) + "\n",
                                     encoding="utf-8")
        sys.exit(0 if result.wasSuccessful() else 1)
