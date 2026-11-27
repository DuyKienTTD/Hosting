"""Cross-process-only delta tests. No subprocess can open another role's store."""

from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
from http.client import RemoteDisconnected
import json
import multiprocessing as mp
from pathlib import Path
import secrets
import sqlite3
from tempfile import TemporaryDirectory
import unittest

from h6_b2k_services import BINDING, encode, rpc, run_service, signature


class CrossServiceTests(unittest.TestCase):
    def setUp(self):
        tmp = TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.context = mp.get_context("spawn")
        self.tokens = {role: secrets.token_hex(32) for role in ("adapter", "receiver", "hermes")}
        self.callback_key, self.receipt_key = secrets.token_bytes(32), secrets.token_bytes(32)
        self.clock = self.context.Value("i", 1000)
        self.ports, self.processes = {}, {}
        self.paths = {role: self.root / role / "fixture.sqlite3" for role in self.tokens}
        for path in self.paths.values():
            path.parent.mkdir()
        self.addCleanup(self.stop_all)
        for role in ("hermes", "receiver", "adapter"):
            self.spawn(role)

    def spawn(self, role):
        inbox, outbox = self.context.Pipe(duplex=False)
        token_map = self.tokens if role == "adapter" else {role: self.tokens[role]}
        keys = (None, None) if role == "hermes" else (self.callback_key, self.receipt_key)
        ports = self.ports if role == "adapter" else {}
        proc = self.context.Process(target=run_service, args=(
            role, self.paths[role], token_map, *keys, self.clock, ports, outbox, self.ports.get(role, 0),
        ))
        proc.start()
        self.processes[role] = proc
        outbox.close()
        with inbox:
            self.assertTrue(inbox.poll(5), "child ready timeout")
            self.ports[role] = inbox.recv()

    def stop(self, role):
        proc = self.processes.pop(role)
        proc.terminate()
        proc.join(5)
        if proc.is_alive():
            proc.kill()
            proc.join(5)
        self.assertFalse(proc.is_alive())
        proc.close()

    def stop_all(self):
        for role in tuple(self.processes):
            self.stop(role)

    def restart(self, role):
        previous_pid = self.processes[role].pid
        self.stop(role)
        self.spawn(role)
        self.assertNotEqual(previous_pid, self.processes[role].pid)

    def call(self, role, path, payload=None, headers=None, timeout=2):
        return rpc(self.ports[role], path, self.tokens[role], payload, headers, timeout)

    def query(self, role, sql):
        with closing(sqlite3.connect(self.paths[role].as_uri() + "?mode=ro", uri=True)) as db:
            return db.execute(sql).fetchall()

    def submit_body(self):
        return {"task_id": "fake-task", "correlation_id": "fake-correlation",
                "schema_version": 1, "synthetic": True, "input": "fake input"}

    def admit(self):
        code, job = self.call("adapter", "/jobs", self.submit_body())
        self.assertEqual(code, 202)
        return "/jobs/" + job["job_id"], job

    def prepare(self, path):
        self.assertIn(self.call("adapter", path + "/sync", {})[0], (200, 201))
        status = self.call("adapter", path)[1]
        return "/runs/" + status["run_id"], {key: status[key] for key in BINDING}

    def callback(self, value, key=None, at=None):
        at = self.clock.value if at is None else at
        proof = signature(self.callback_key if key is None else key, b"event", at, encode(value))
        return rpc(self.ports["receiver"], "/callback", payload=value, headers={
            "X-Callback-Time": str(at), "X-Callback-Proof": proof,
        })

    def assert_counts(self, dispatches, settlements, reserve, receipts):
        self.assertEqual(self.query("adapter", "SELECT count(*) FROM jobs"), [(1,)])
        self.assertEqual(self.query("hermes", "SELECT dispatches,settlements,reserve FROM runs"),
                         [(dispatches, settlements, reserve)])
        self.assertEqual(self.query("receiver", "SELECT count(receipt) FROM inbox"), [(receipts,)])

    def test_disjoint_stores_lost_admission_and_hermes_ack(self):
        self.assertEqual(len({proc.pid for proc in self.processes.values()}), 3)
        for role, table in (("adapter", "jobs"), ("hermes", "runs"), ("receiver", "inbox")):
            self.assertEqual(self.query(role, "SELECT name FROM sqlite_master WHERE type='table'"), [(table,)])
        with self.assertRaises(TimeoutError):
            self.call("adapter", "/jobs", self.submit_body(), {"X-Fixture-Hold-Ack": "1"}, timeout=0.08)
        original = self.query("adapter", "SELECT job_id FROM jobs")[0][0]
        self.restart("adapter")
        path, job = self.admit()
        self.assertEqual(job["job_id"], original)
        self.assertEqual(self.call("adapter", path + "/sync", {"drop_ack": True})[0], 502)
        persisted_run = self.query("hermes", "SELECT run_id FROM runs")[0][0]
        self.assertIsNone(self.call("adapter", path)[1]["run_id"])
        self.restart("hermes")
        run, binding = self.prepare(path)
        self.assertEqual(binding["run_id"], persisted_run)
        self.assertEqual(binding["request_sha256"], job["request_sha256"])
        self.assertEqual(self.call("hermes", run + "/start", {})[0], 202)
        self.assertEqual(self.call("hermes", run + "/finish", {"outcome": "paid_succeeded"})[0], 200)
        self.assertEqual(self.call("adapter", path + "/collect", {})[0], 200)
        self.assertEqual(self.call("adapter", path + "/deliver", {})[0], 200)
        self.assert_counts(1, 1, "settled", 1)

    def test_concurrent_admission_mapping_and_dispatch(self):
        with ThreadPoolExecutor(max_workers=6) as pool:
            jobs = list(pool.map(lambda _: self.admit(), range(6)))
            path = jobs[0][0]
            self.assertTrue(all(row == jobs[0] for row in jobs))
            runs = list(pool.map(lambda _: self.prepare(path), range(4)))
            self.assertTrue(all(row == runs[0] for row in runs))
            run = runs[0][0]
            codes = list(pool.map(lambda _: self.call("hermes", run + "/start", {})[0], range(4)))
        self.assertEqual(sorted(codes), [202, 409, 409, 409])
        self.assertEqual(self.call("hermes", run + "/finish", {"outcome": "mock_succeeded"})[0], 200)
        for _ in range(2):
            self.assertEqual(self.call("adapter", path + "/collect", {})[0], 200)
        self.assertEqual(self.call("adapter", path + "/deliver", {})[0], 200)
        self.assertEqual(self.call("adapter", path + "/deliver", {})[0], 409)
        self.assertEqual(self.call("adapter", "/jobs", self.submit_body() | {"input": "drift"})[0], 409)
        self.assert_counts(1, 1, "settled", 1)

    def test_wrong_binding_order_token_and_replay_after_restart(self):
        path, job = self.admit()
        fake = job | {"run_id": "a" * 32, "sequence": 1, "outcome": "mock_succeeded"}
        self.assertEqual(self.callback(fake)[0], 409)
        run, binding = self.prepare(path)
        value = binding | {"sequence": 1, "outcome": "mock_succeeded"}
        self.assertEqual(self.call("adapter", path + "/collect", {})[0], 409)
        self.assertEqual(self.callback(value, key=secrets.token_bytes(32))[0], 401)
        self.assertEqual(self.callback(value, at=self.clock.value - 11)[0], 401)
        self.assertEqual(self.callback(value | {"sequence": 2})[0], 422)
        for wrong in ({"run_id": "b" * 32}, {"request_sha256": "f" * 64},
                      {"job_id": "c" * 32}, {"task_id": "changed"}, {"correlation_id": "changed"}):
            self.assertEqual(self.callback(value | wrong)[0], 409)
        self.assertEqual(self.call("hermes", run + "/start", {})[0], 202)
        self.assertEqual(self.call("hermes", run + "/finish", {"outcome": "mock_succeeded"})[0], 200)
        self.call("adapter", path + "/collect", {})
        self.assertEqual(self.callback(value)[0], 200)
        self.restart("receiver")
        self.assertEqual(self.callback(value)[0], 409)
        self.assertEqual(self.callback(value | {"outcome": "paid_succeeded"})[0], 409)
        self.assertEqual(self.call("adapter", path + "/deliver", {})[0], 200)
        self.assert_counts(1, 1, "settled", 1)

    def test_unknown_dispatch_ack_callback_ack_and_explicit_redelivery(self):
        path, _ = self.admit()
        run, _ = self.prepare(path)
        with self.assertRaises(RemoteDisconnected):
            self.call("hermes", run + "/start", {}, {"X-Fixture-Drop-Ack": "1"})
        self.restart("hermes")
        self.assertEqual(self.call("hermes", run + "/start", {})[0], 409)
        self.assertEqual(self.call("hermes", run + "/finish", {"outcome": "outcome_unknown"})[0], 200)
        self.assertEqual(self.call("adapter", path + "/collect", {})[0], 200)
        self.assertEqual(self.call("adapter", path + "/deliver", {"drop_ack": True})[0], 502)
        self.assertEqual(self.call("adapter", path)[1]["delivery"], "dead_letter")
        self.assert_counts(1, 0, "held", 1)
        self.restart("receiver")
        self.restart("adapter")
        self.clock.value += 11
        self.assertEqual(self.call("adapter", path + "/deliver", {})[0], 200)
        self.assertEqual(self.call("adapter", path)[1]["outcome"], "outcome_unknown")
        self.assertEqual(self.call("hermes", run + "/finish", {"outcome": "paid_succeeded"})[0], 409)
        self.assertEqual(self.query("adapter", "SELECT attempts FROM jobs"), [(2,)])
        self.assert_counts(1, 0, "held", 1)

    def test_receiver_unreachable_recovers_without_dispatch(self):
        path, _ = self.admit()
        run, _ = self.prepare(path)
        self.call("hermes", run + "/start", {})
        self.call("hermes", run + "/finish", {"outcome": "failed"})
        self.assertEqual(self.call("adapter", path + "/collect", {})[0], 200)
        self.stop("receiver")
        self.assertEqual(self.call("adapter", path + "/deliver", {})[0], 502)
        self.assertEqual(self.call("adapter", path)[1]["delivery"], "dead_letter")
        self.spawn("receiver")
        self.assertEqual(self.call("adapter", path + "/deliver", {})[0], 200)
        self.assert_counts(1, 1, "settled", 1)

    def test_signed_receipt_tamper_keeps_outbox_unconfirmed(self):
        path, _ = self.admit()
        run, _ = self.prepare(path)
        self.call("hermes", run + "/start", {})
        self.call("hermes", run + "/finish", {"outcome": "mock_succeeded"})
        self.call("adapter", path + "/collect", {})
        self.assertEqual(self.call("adapter", path + "/deliver", {"corrupt_receipt": True})[0], 502)
        self.assertEqual(self.call("adapter", path)[1]["delivery"], "dead_letter")
        self.assert_counts(1, 1, "settled", 1)
        self.assertEqual(self.call("adapter", path + "/deliver", {})[0], 200)
        self.assert_counts(1, 1, "settled", 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
