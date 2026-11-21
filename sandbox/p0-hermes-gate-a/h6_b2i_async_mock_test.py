"""Run with python -B h6_b2i_async_mock_test.py. Uses only local HTTP and disposable SQLite."""

from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from http.client import HTTPConnection
import json
from pathlib import Path
import secrets
import sys
from tempfile import TemporaryDirectory
from threading import Barrier, Event, Thread
import time
import unittest

from h6_b2i_async_mock import (
    MockHttpHandler, MockJobs, callback_signature, decode, encode, loopback_fixture,
)


BRIDGE_LEGACY_WAIT = 20
N8N_LEGACY_WAIT = 30
WALL_CLOCK = "--wall-clock" in sys.argv


class FixtureTests(unittest.TestCase):
    def setUp(self):
        temp = TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.scratch = Path(temp.name)
        self.key = secrets.token_bytes(32)
        self.token = secrets.token_hex(32).encode()
        self.now = 1000
        self.restart()

    def restart(self):
        self.jobs = MockJobs(self.scratch, lambda: self.now, self.key)

    @contextmanager
    def http(self, handler=MockHttpHandler):
        with loopback_fixture(self.jobs, self.token, handler) as server:
            worker = Thread(target=server.serve_forever, kwargs={"poll_interval": 0.02})
            worker.start()
            self.port = server.server_port
            try:
                yield
            finally:
                server.shutdown()
                worker.join()

    def request(self, method, path, raw=None, headers=None, timeout=2):
        connection = HTTPConnection("127.0.0.1", self.port, timeout=timeout)
        try:
            if headers is None:
                headers = {"Authorization": "Bearer " + self.token.decode()}
            connection.request(method, path, raw, headers)
            with connection.getresponse() as response:
                return response.status, decode(response.read()), response.getheader("Location")
        finally:
            connection.close()

    def submission(self, duration=5, fault="none", intent="synthetic_paid"):
        return {"schema_version": 1, "synthetic": True, "task_id": "fake-task",
                "correlation_id": "fake-correlation", "intent": intent,
                "duration_seconds": duration, "fault": fault}

    def submit(self, value, expected=202):
        status, body, location = self.request("POST", "/jobs", encode(value))
        self.assertEqual(status, expected)
        if status == 202:
            self.assertEqual(location, "/jobs/" + body["job_id"])
        return body["job_id"]

    def status(self, job):
        status, body, _ = self.request("GET", "/jobs/" + job)
        self.assertEqual(status, 200)
        return body

    def counters(self, job):
        with self.jobs.transaction() as db:
            row = db.execute("SELECT * FROM jobs WHERE job_id=?", (job,)).fetchone()
            receipts = db.execute("SELECT count(*) FROM receipts WHERE job_id=?", (job,)).fetchone()[0]
            return {"dispatches": row["dispatches"], "settlements": row["settlements"],
                    "reserve": row["reserve"], "receipts": receipts,
                    "delivery_attempts": row["delivery_attempts"]}

    def event(self, job):
        with self.jobs.transaction() as db:
            return decode(db.execute("SELECT outbox FROM jobs WHERE job_id=?", (job,)).fetchone()[0])

    def signed(self, value, key=None, at=None):
        raw = encode(value)
        timestamp = str(self.now if at is None else at)
        return raw, timestamp, callback_signature(self.key if key is None else key, timestamp, raw)

    def send(self, raw, timestamp, signature, timeout=2):
        code, body, _ = self.request("POST", "/callback", raw, {
            "X-Callback-Timestamp": timestamp, "X-Callback-Signature": signature,
        }, timeout)
        return code, body

    def start(self, job):
        self.jobs.advance(job)
        self.jobs.advance(job)

    def timeline(self, duration, outcome):
        with self.http():
            value = self.submission(duration)
            start_wall = time.perf_counter()
            job = self.submit(value)
            ack_ms = round((time.perf_counter() - start_wall) * 1000, 3)
            self.assertLess(ack_ms, 2000)
            self.assertEqual(self.status(job)["state"], "accepted")
            self.assertEqual(self.counters(job)["dispatches"], 0)
            self.jobs.advance(job)
            self.assertEqual(self.counters(job)["reserve"], "held")
            self.assertEqual(self.counters(job)["dispatches"], 0)
            self.jobs.advance(job)
            start = self.now
            dispatch_wall = time.perf_counter()

            def set_elapsed(elapsed):
                if WALL_CLOCK:
                    time.sleep(max(0, dispatch_wall + elapsed - time.perf_counter()))
                self.now = start + elapsed

            finish = min(duration, 45)
            for elapsed in sorted({finish - 1, BRIDGE_LEGACY_WAIT, N8N_LEGACY_WAIT}):
                if elapsed < finish:
                    set_elapsed(elapsed)
                    self.jobs.advance(job)
                    self.assertEqual(self.status(job)["state"], "running")
            set_elapsed(finish)
            self.jobs.advance(job)
            self.assertEqual(self.status(job)["state"], outcome)
            self.assertEqual(self.status(job)["delivery"], "pending")
            self.jobs.deliver(job, self.send)
            callback_wall = round(time.perf_counter() - dispatch_wall, 3)
            if duration > finish:
                set_elapsed(duration)
                self.jobs.advance(job)  # Late synthetic provider data cannot change terminal state.
            self.assertEqual(self.status(job)["state"], outcome)
            self.assertEqual(self.status(job)["delivery"], "delivered")
            self.assertEqual(self.submit(value, expected=200), job)
            self.jobs.advance(job)
            self.jobs.deliver(job, self.send)
            expected_settlements = int(outcome != "outcome_unknown")
            counts = self.counters(job)
            self.assertEqual(counts, {"dispatches": 1, "settlements": expected_settlements,
                                      "reserve": "settled" if expected_settlements else "held",
                                      "receipts": 1, "delivery_attempts": 1})
            print("B2I_TIMELINE", json.dumps({"duration_s": duration, "terminal_at_s": finish,
                  "callback_at_s": finish, "callback_wall_s": callback_wall, "wall_clock_wait": WALL_CLOCK,
                  "post_202_wall_ms": ack_ms, "outcome": outcome, **counts}), flush=True)

    def test_delay_05(self):
        self.timeline(5, "paid_succeeded")

    def test_delay_21(self):
        self.timeline(21, "paid_succeeded")

    def test_delay_31(self):
        self.timeline(31, "paid_succeeded")

    def test_delay_46(self):
        self.timeline(46, "outcome_unknown")

    def test_concurrent_admission_and_workers(self):
        with self.http(), ThreadPoolExecutor(max_workers=8) as pool:
            gate = Barrier(8, timeout=5)

            def submit_together(_):
                gate.wait()
                return self.submit(self.submission())

            job, *duplicates = pool.map(submit_together, range(8))
            self.assertEqual(duplicates, [job] * 7)
            list(pool.map(self.jobs.advance, [job] * 8))
            self.now += 5
            list(pool.map(self.jobs.advance, [job] * 8))
            list(pool.map(lambda _: self.jobs.deliver(job, self.send), range(8)))
            self.assertEqual(list(self.counters(job).values()), [1, 1, "settled", 1, 1])
            for change in ({"duration_seconds": 21}, {"correlation_id": "other"},
                           {"task_id": "other"}):
                self.assertEqual(self.request("POST", "/jobs", encode(self.submission() | change))[0], 409)

    def test_admission_http_timeout_after_commit(self):
        committed, unblock = Event(), Event()

        class LostAcceptance(MockHttpHandler):
            def reply(self, code, value):
                if code == 202 and not committed.is_set():
                    committed.set()
                    unblock.wait(2)
                return super().reply(code, value)

        value = self.submission(31)
        with self.http(LostAcceptance):
            try:
                with self.assertRaises(TimeoutError):
                    self.request("POST", "/jobs", encode(value), timeout=0.15)
                self.assertTrue(committed.is_set())
            finally:
                unblock.set()
            job = self.submit(value)
            self.start(job)
            self.now += 31
            self.jobs.advance(job)
            self.jobs.deliver(job, self.send)
            self.assertEqual(self.status(job)["delivery"], "delivered")
            self.assertEqual(list(self.counters(job).values()), [1, 1, "settled", 1, 1])

    def test_callback_auth_binding_strict_schema_and_replay_after_restart(self):
        with self.http():
            job = self.submit(self.submission(intent="mock"))
            self.start(job)
            pending = self.status(job)
            early = {name: pending[name] for name in ("job_id", "task_id", "correlation_id", "request_sha256")}
            early.update(schema_version=1, synthetic=True, sequence=1, outcome="mock_succeeded")
            self.assertEqual(self.send(*self.signed(early))[0], 409)
            self.now += 5
            self.jobs.advance(job)
            value = self.event(job)
            self.assertEqual(value, early)
            for key, at in ((secrets.token_bytes(32), self.now), (self.key, self.now - 11),
                            (self.key, self.now + 1)):
                self.assertEqual(self.send(*self.signed(value, key=key, at=at))[0], 401)
            self.assertEqual(self.request("POST", "/callback", encode(value))[0], 401)
            for change in ({"job_id": "a" * 32}, {"task_id": "other"}, {"correlation_id": "other"},
                           {"request_sha256": "0" * 64}, {"outcome": "paid_succeeded"}):
                self.assertEqual(self.send(*self.signed(value | change))[0], 409)
            for change in ({"sequence": 2}, {"sequence": True}, {"schema_version": 2},
                           {"synthetic": False}, {"outcome": "bogus"}, {"paid": True}):
                self.assertEqual(self.send(*self.signed(value | change))[0], 422)
            missing = value.copy()
            del missing["request_sha256"]
            self.assertEqual(self.send(*self.signed(missing))[0], 422)
            raw, ts, sig = self.signed(value)
            self.assertEqual(self.send(raw + b" ", ts, sig)[0], 401)
            duplicate_field = raw[:-1] + b',"sequence":1}'
            self.assertEqual(self.send(duplicate_field, ts, callback_signature(self.key, ts, duplicate_field))[0], 400)
            self.assertEqual(self.counters(job)["receipts"], 0)
            self.assertEqual(self.send(raw, ts, sig)[0], 200)
        self.restart()
        with self.http():
            self.assertEqual(self.send(raw, ts, sig)[0], 409)
            self.now += 11
            self.assertEqual(self.send(raw, ts, sig)[0], 401)
            self.assertEqual(self.send(*self.signed(value))[0], 409)
            self.jobs.deliver(job, self.send)
            self.assertEqual(self.status(job)["delivery"], "delivered")
            self.assertEqual(list(self.counters(job).values()), [1, 1, "settled", 1, 1])

    def test_dead_letter_and_redelivery_after_callback_timeout(self):
        receipt_committed, unblock = Event(), Event()

        class LostReceipt(MockHttpHandler):
            def reply(self, code, value):
                if code == 200 and "receipt" in value:
                    receipt_committed.set()
                    unblock.wait(2)
                return super().reply(code, value)

        def lose_response(raw, timestamp, signature, budget):
            self.assertEqual(budget, 5)
            return self.send(raw, timestamp, signature, timeout=0.15)

        value = self.submission(fault="transport_timeout")
        with self.http(LostReceipt):
            job = self.submit(value)
            self.start(job)
            self.now += 45
            self.jobs.advance(job)
            try:
                self.jobs.deliver(job, lose_response)
                self.assertTrue(receipt_committed.is_set())
            finally:
                unblock.set()
            self.assertEqual(self.status(job)["delivery"], "dead_letter")
            self.assertEqual(list(self.counters(job).values()), [1, 0, "held", 1, 1])
        self.restart()
        self.now += 11
        with self.http():
            self.assertEqual(self.submit(value, expected=200), job)
            self.jobs.deliver(job, self.send)
            self.assertEqual(self.status(job)["delivery"], "delivered")
            self.assertEqual(self.status(job)["state"], "outcome_unknown")
            attempted_refund = self.event(job) | {"outcome": "failed"}
            self.assertEqual(self.send(*self.signed(attempted_refund))[0], 409)
            self.assertEqual(list(self.counters(job).values()), [1, 0, "held", 1, 2])

    def test_unreachable_callback_bounded_reconciliation(self):
        def offline(*args):
            raise ConnectionRefusedError

        with self.http():
            job = self.submit(self.submission(fault="known_failure"))
            self.start(job)
            self.now += 5
            self.jobs.advance(job)
            for _ in range(3):
                self.jobs.deliver(job, offline)
            self.assertEqual(self.status(job)["state"], "failed")
            self.assertEqual(self.status(job)["delivery"], "dead_letter")
            self.assertEqual(list(self.counters(job).values()), [1, 1, "settled", 0, 2])

    def test_ipc_connect_sdk_and_settlement_faults(self):
        cases = (
            ("ipc_timeout", 4, 0, 0),
            ("connect_timeout", 5, 0, 0),
            ("none", 60, 0, 0),  # Simulated SDK cutoff expires before dispatch.
            ("none", 57, 1, 3),  # Three seconds remain for the SDK after simulated queue delay.
            ("settlement_ack_lost", 0, 1, 5),
        )
        with self.http():
            for index, (fault, before_dispatch, dispatches, after_dispatch) in enumerate(cases):
                with self.subTest(fault=fault, before_dispatch=before_dispatch):
                    suffix = str(index)
                    job = self.submit(self.submission(fault=fault) | {
                        "task_id": "fake-task-" + suffix, "correlation_id": "fake-correlation-" + suffix,
                    })
                    self.jobs.advance(job)
                    if fault in ("ipc_timeout", "connect_timeout"):
                        self.now += before_dispatch - 1
                        self.jobs.advance(job)
                        self.assertEqual(self.status(job)["state"], "reserved")
                        self.now += 1
                    else:
                        self.now += before_dispatch
                    self.jobs.advance(job)
                    self.now += after_dispatch
                    self.jobs.advance(job)
                    self.jobs.deliver(job, self.send)
                    self.assertEqual(self.status(job)["state"], "outcome_unknown")
                    self.assertEqual(list(self.counters(job).values()), [dispatches, 0, "held", 1, 1])

    def test_abandoned_dispatch_and_sender_restart(self):
        with self.http():
            value = self.submission()
            job = self.submit(value)
            self.start(job)
        self.restart()
        self.jobs.abandon(job)
        # Inject the persisted sender state at the crash boundary before any callback ACK.
        with self.jobs.transaction(write=True) as db:
            db.execute("UPDATE jobs SET delivery='sending', delivery_attempts=1 WHERE job_id=?", (job,))
        self.restart()
        with self.http():
            self.assertEqual(self.submit(value, expected=200), job)
            self.jobs.recover_delivery(job)
            self.jobs.deliver(job, self.send)
            self.jobs.advance(job)
            self.assertEqual(self.status(job)["state"], "outcome_unknown")
            self.assertEqual(list(self.counters(job).values()), [1, 0, "held", 1, 2])

    def test_job_auth_and_mock_only_submission(self):
        with self.http():
            value = self.submission()
            self.assertEqual(self.request("POST", "/jobs", encode(value), {})[0], 401)
            for patch in ({"synthetic": False}, {"intent": "paid"}, {"duration_seconds": True},
                          {"schema_version": True}, {"provider_url": "invalid"}):
                self.assertEqual(self.request("POST", "/jobs", encode(value | patch))[0], 422)
            job = self.submit(value)
            self.assertEqual(self.request("GET", "/jobs/" + job, headers={})[0], 401)
            self.assertEqual(self.request("GET", "/jobs/" + "f" * 32)[0], 404)
            self.assertEqual(self.status(job)["state"], "accepted")
            self.assertEqual(list(self.counters(job).values()), [0, 0, "none", 0, 0])


if __name__ == "__main__":
    if WALL_CLOCK:
        sys.argv.remove("--wall-clock")
    unittest.main(verbosity=2)
