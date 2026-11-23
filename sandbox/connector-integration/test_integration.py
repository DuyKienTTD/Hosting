"""S3 delta only, using pinned S1/S2 modules and actual worker process exits."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from bridge import Bridge, LIVE_ENABLED
import pinned_sources as pins


RESULTS = {}
CRASH = 86
GA = {"dimensions": ["date", "source", "channel"], "metrics": ["sessions", "conversions"],
      "start_date": "2026-11-20", "end_date": "2026-11-21", "row_budget": 3}


def socket_guard(event, _):
    if event.startswith("socket."):
        raise RuntimeError("S3 socket audit boundary")


def intent(key, operation="ga4.run_report", arguments=None, scenario="ok"):
    return {"contract_version": 1, "synthetic": True, "approval": "synthetic_approved",
            "idempotency_key": "fake-" + key, "operation": operation,
            "arguments": GA if arguments is None else arguments, "scenario": scenario,
            "budget": {"max_dispatches": 1, "max_units": 1}, "deadline_ms": 20}


def case(name, expected, **observed):
    RESULTS[name] = {"expected": expected, "observed": observed}


class IntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source_dir = Path(cls.enterClassContext(tempfile.TemporaryDirectory(prefix="eng01a-s3-imports-")))
        pins.stage(cls.source_dir)
        cls.s1, cls.s2 = pins.load(cls.source_dir)

    def setUp(self):
        self.store = self.enterContext(self.s1.temporary_sandbox())
        self.bridge = Bridge(self.s1, self.s2, self.store.root)

    def run_intent(self, request):
        admitted = self.bridge.admit(request, 0)
        self.assertEqual(admitted["http"], 202)
        self.assertEqual(admitted["request_sha256"], self.s1.sha(request))
        outcome = self.bridge.process(admitted["job_id"], 1)
        self.assert_receipt(outcome)
        return admitted, outcome

    def assert_receipt(self, view):
        native, binding = view["native"], view["receipt_binding"]
        event, receipt = native["callback"], native["receipt"]
        self.assertEqual(native["fake_dispatches"], 1)
        self.assertEqual(view["synthetic_read_attempts"], 1)
        self.assertFalse(view["external_effect_delivered"])
        audit = [e["event"] for e in native["audit"]]
        self.assertEqual(audit.count("fake_dispatch"), 1)
        self.assertEqual(audit.count("receipt_committed"), 1)
        self.assertEqual(audit.count("receipt_ack"), 1)
        self.assertLess(audit.index("receipt_committed"), audit.index("receipt_ack"))
        self.assertEqual(receipt["event_sha256"], self.s1.sha(event))
        self.assertEqual(receipt["callback_id"], event["callback_id"])
        self.assertEqual(binding["native_receipt_id"], receipt["receipt_id"])
        self.assertEqual(binding["native_request_sha256"], native["request_sha256"])
        self.assertEqual(binding["s3_request_sha256"], view["request_sha256"])
        self.assertEqual(binding["outcome"], native["outcome"])
        self.assertEqual(binding["result_sha256"], self.s1.sha(view["result"]) if view["result"] else None)
        self.assertEqual(binding["binding_sha256"], self.s1.sha({k: v for k, v in binding.items()
                                                               if k != "binding_sha256"}))

    def test_ga4_admission_replay_and_conflict(self):
        request = intent("ga")
        admitted, view = self.run_intent(request)
        self.assertEqual(view["native"]["state"], "completed")
        self.assertEqual(view["native"]["idempotency_key"], "fake-" + admitted["request_sha256"][:48])
        self.assertEqual(view["native"]["channel"], "fixture")
        self.assertEqual(view["result"], self.s2.GA4Mock().run_report(**GA, deadline_ms=19))
        self.assertEqual(len(view["result"]["records"]), 3)
        same = dict(reversed(list(request.items())))
        self.assertEqual(self.bridge.admit(same, 2), admitted | {"http": 200, "replayed": True})
        self.assertEqual(self.bridge.process(admitted["job_id"], 2), view)
        with self.assertRaises(self.s1.Conflict) as conflict:
            self.bridge.admit(request | {"arguments": GA | {"metrics": ["sessions"]}}, 2)
        self.assertEqual(conflict.exception.http_status, 409)
        case("ga4_admission_replay", "3 attributed rows, stable job and receipt, conflict 409",
             rows=3, replay_http=200, conflict_http=409, request_sha256=admitted["request_sha256"],
             receipt_binding=view["receipt_binding"], audit=view["native"]["audit"])

    def test_wp_woo_locales_pagination_and_snapshot(self):
        observed = {}
        for locale in ("en", "vi"):
            args = {"resource": "products", "locale": locale, "limit": 1}
            _, first = self.run_intent(intent("page1-" + locale, "wp_woo.list", args))
            _, second = self.run_intent(intent("page2-" + locale, "wp_woo.list",
                                              args | {"cursor": first["result"]["next_cursor"]}))
            _, reread = self.run_intent(intent("pagecopy-" + locale, "wp_woo.list", args))
            self.assertEqual(first["result"], reread["result"])
            self.assertIsNone(first["result"]["next_watermark"])
            self.assertIsNotNone(second["result"]["next_watermark"])
            ids = [v["result"]["records"][0]["source_record_id"] for v in (first, second)]
            self.assertNotEqual(*ids)
            currency = "USD" if locale == "en" else "VND"
            for view in (first, second):
                product = view["result"]["records"][0]
                self.assertEqual(product["data"]["locale"], locale)
                self.assertEqual(product["data"]["price"]["currency"], currency)
                self.assertEqual(product["data"]["price"]["unit"], "minor_currency_unit")
            observed[locale] = ids
        _, page = self.run_intent(intent("page-detail", "wp_woo.get",
                                         {"resource": "pages", "locale": "vi", "record_id": "fake-page-vi-a"}))
        self.assertEqual(page["result"]["records"][0]["data"]["kind"], "page")
        case("wp_woo_reads", "EN/VI list, correct currency, stable cursor and same snapshot re-read",
             per_locale=observed, detail="fake-page-vi-a", same_snapshot=True)

    def test_failures_unknown_and_cursor_isolation(self):
        args = {"resource": "posts", "locale": "en", "limit": 1}
        _, first = self.run_intent(intent("posts", "wp_woo.list", args))
        args |= {"cursor": first["result"]["next_cursor"]}
        observed = {}
        for scenario, status, expected in (("forbidden", 403, "failed"), ("quota", 429, "failed"),
                                            ("delayed", 504, "outcome_unknown")):
            request = intent("posts-" + scenario, "wp_woo.list", args, scenario)
            admitted, view = self.run_intent(request)
            self.assertEqual((view["result"]["status"], view["native"]["state"]), (status, expected))
            self.assertEqual(view["result"]["records"], [])
            self.assertNotIn("next_cursor", view["result"])
            self.assertNotIn("next_watermark", view["result"])
            self.assertEqual(self.bridge.process(admitted["job_id"], 2), view)
            observed[scenario] = {"http": status, "outcome": expected, "dispatches": 1, "receipts": 1}
        _, missing = self.run_intent(intent("missing", "wp_woo.get",
                                           {"resource": "pages", "locale": "en", "record_id": "fake-page-en-z"}))
        self.assertEqual((missing["result"]["status"], missing["native"]["state"]), (404, "failed"))
        _, invalid = self.run_intent(intent("invalid-field", arguments=GA | {"metrics": ["unapproved"]}))
        self.assertEqual((invalid["result"]["status"], invalid["native"]["state"]), (422, "failed"))
        self.assertEqual(invalid["result"]["observed_at"], first["result"]["observed_at"])
        _, valid = self.run_intent(intent("posts-after", "wp_woo.list", args))
        self.assertEqual(valid["result"], self.s2.WpWooMock().list(**args, deadline_ms=19))
        case("errors_and_unknown", "403/429/404/422 failed, 504 unknown, no cursor/watermark advancement or retry",
             **observed, missing_status=404, invalid_status=422, same_cursor_valid_after_faults=True)

    def test_native_deadline_blocks_first_synthetic_read(self):
        admitted = self.bridge.admit(intent("expired"), 0)
        job = admitted["job_id"]
        view = self.bridge.process(job, 20)
        self.assertEqual(view["native"]["state"], "outcome_unknown")
        self.assertEqual((view["native"]["fake_dispatches"], view["synthetic_read_attempts"]), (0, 0))
        self.assertEqual([event["event"] for event in view["native"]["audit"]].count("receipt_committed"), 1)
        self.assertIsNone(view["result"])
        self.assertEqual(self.bridge.process(job, 21), view)
        case("native_deadline", "expired S1 deadline creates an unknown receipt with zero fake dispatches and S2 reads",
             outcome="outcome_unknown", dispatches=0, read_attempts=0, receipts=1,
             receipt_binding=view["receipt_binding"])

    def test_callback_and_receipt_binding(self):
        admitted, view = self.run_intent(intent("binding"))
        callback = view["native"]["callback"]
        offer = callback | {"request_sha256": "0" * 64}
        offer["callback_id"] = "callback-" + self.s1.sha({k: v for k, v in offer.items() if k != "callback_id"})
        with self.assertRaises(self.s1.Conflict):
            self.store.receive_callback(offer, 2)
        receipt = self.store.receive_callback(callback, 2)
        self.assertEqual(receipt, view["native"]["receipt"])
        self.assertEqual(self.bridge.snapshot(admitted["job_id"]), view)
        case("callback_binding", "mismatched native request denied, valid callback returns same receipt",
             rejected=True, unchanged=True, receipt_binding=view["receipt_binding"])

    def worker_process(self, job, tick, fault, expected=0):
        args = [sys.executable, "-X", "utf8", "-B", __file__, "--worker", str(self.source_dir),
                str(self.store.root), job, str(tick), fault]
        proc = subprocess.run(args, capture_output=True, encoding="utf-8", timeout=10)
        self.assertEqual(proc.returncode, expected, proc.stderr)
        obs = json.loads(proc.stdout)
        self.assertNotEqual(obs["pid"], os.getpid())
        self.assertEqual(obs["checkpoint"], fault if expected else "finished")
        return obs["pid"]

    def test_crash_after_s2_read_abandons_result_without_redispatch(self):
        admitted = self.bridge.admit(intent("working"), 0)
        job = admitted["job_id"]
        crash = self.worker_process(job, 1, "after_s2_read_before_receipt", CRASH)
        before = self.bridge.snapshot(job)
        self.assertEqual((before["native"]["state"], before["native"]["fake_dispatches"],
                          before["synthetic_read_attempts"], before["native"]["receipt"]), ("working", 1, 1, None))
        recovery = self.worker_process(job, 2, "none")
        self.assertNotEqual(crash, recovery)
        after = self.bridge.snapshot(job)
        self.assert_receipt(after)
        self.assertEqual((after["native"]["state"], after["result"]), ("outcome_unknown", None))
        with self.assertRaises(self.s1.Conflict):
            self.store.settle(job, admitted["native_request_sha256"], "completed", 3)
        self.assertEqual(self.bridge.process(job, 3), after)
        case("crash_after_read", "one fake dispatch/read before crash; immutable unknown and one receipt after restart",
             before_state="working", outcome="outcome_unknown", dispatches=1, read_attempts=1, receipts=1,
             late_settlement_rejected=True, result_exposed=False, external_effect_delivered=False, exit=CRASH,
             crash_pid=crash, recovery_pid=recovery, receipt_binding=after["receipt_binding"], audit=after["native"]["audit"])

    def test_crash_after_receipt_before_ack_replays_receipt_only(self):
        admitted = self.bridge.admit(intent("sending", "wp_woo.list", {"resource": "pages", "locale": "vi"}), 0)
        job = admitted["job_id"]
        crash = self.worker_process(job, 1, "sending_after_receipt", CRASH)
        before = self.bridge.snapshot(job)
        self.assertEqual(before["native"]["state"], "sending")
        self.assertIsNotNone(before["native"]["receipt"])
        self.assertIsNone(before["result"])
        recovery = self.worker_process(job, 2, "none")
        self.assertNotEqual(crash, recovery)
        after = self.bridge.snapshot(job)
        self.assert_receipt(after)
        self.assertEqual(after["native"]["state"], "completed")
        self.assertEqual(after["native"]["receipt"], before["native"]["receipt"])
        self.assertEqual(after["native"]["callback"], before["native"]["callback"])
        self.assertEqual(after["result"]["status"], 200)
        self.assertEqual(after["receipt_binding"]["result_sha256"], self.bridge._intent(job)["result_sha256"])
        self.assertEqual(self.bridge.process(job, 3), after)
        case("crash_after_receipt", "same outbox and committed receipt after fresh worker ACK, no reread",
             before_state="sending", outcome="completed", same_native_receipt=True, same_callback=True,
             dispatches=1, read_attempts=1, receipts=1, external_effect_delivered=False, exit=CRASH,
             crash_pid=crash, recovery_pid=recovery, receipt_binding=after["receipt_binding"], audit=after["native"]["audit"])

    def assert_unbound_unknown(self, admitted):
        job = admitted["job_id"]
        reopened = Bridge(self.s1, self.s2, self.store.root)
        after = reopened.process(job, 2)
        self.assert_receipt(after)
        self.assertEqual(after["native"]["state"], "outcome_unknown")
        self.assertIsNone(after["result"])
        self.assertIsNone(after["receipt_binding"]["result_sha256"])
        with self.assertRaises(self.s1.Conflict):
            self.store.settle(job, admitted["native_request_sha256"], "completed", 3)
        self.assertEqual(reopened.process(job, 3), after)
        return after

    def test_recovery_does_not_bind_orphan_delayed_result(self):
        request = intent("orphan-504", scenario="delayed")
        admitted = self.bridge.admit(request, 0)
        job = admitted["job_id"]
        with patch.object(self.s1.OfflineAdapter, "settle", side_effect=RuntimeError("injected before S1 settle")):
            with self.assertRaisesRegex(RuntimeError, "injected before S1 settle"):
                self.bridge.process(job, 1)
        row = self.bridge._intent(job)
        self.assertEqual(json.loads(row["prepared_result"])["status"], 504)
        self.assertIsNone(row["event_sha256"])
        before = self.bridge.snapshot(job)
        self.assertEqual(before["native"]["state"], "working")
        self.assertIsNone(before["native"]["callback"])
        self.assertIsNone(before["native"]["receipt"])
        self.assertIsNone(before["result"])
        after = self.assert_unbound_unknown(admitted)
        reopened = Bridge(self.s1, self.s2, self.store.root)
        self.assertEqual(reopened.admit(request, 3), admitted | {"http": 200, "replayed": True})
        case("orphan_504", "prepared 504 survived pre-settlement exception but is absent from recovery receipt",
             prepared_status=504, before_state="working", dispatches=1, reads=1, receipts=1,
             replay_stable=True, late_settlement_rejected=True, binding=after["receipt_binding"])

    def test_crash_inside_settlement_rolls_back_outbox_and_binding(self):
        admitted = self.bridge.admit(intent("settlement-crash", scenario="delayed"), 0)
        job = admitted["job_id"]
        crash = self.worker_process(job, 1, "settlement_before_commit", CRASH)
        row = self.bridge._intent(job)
        self.assertEqual(json.loads(row["prepared_result"])["status"], 504)
        self.assertIsNone(row["event_sha256"])
        before = self.bridge.snapshot(job)
        self.assertEqual(before["native"]["state"], "working")
        self.assertIsNone(before["native"]["callback"])
        self.assertIsNone(before["native"]["receipt"])
        self.assertNotIn("sending", [entry["event"] for entry in before["native"]["audit"]])
        after = self.assert_unbound_unknown(admitted)
        case("transaction_crash", "exit rolls back outbox and association; recovery suppresses unbound 504",
             exit=CRASH, crash_pid=crash, before_state="working", outbox_rolled_back=True,
             association_rolled_back=True, dispatches=1, reads=1, receipts=1, binding=after["receipt_binding"])

    def test_completed_delayed_result_is_bound_after_outbox_restart(self):
        request = intent("committed-504", scenario="delayed")
        admitted, normal = self.run_intent(request)
        job = admitted["job_id"]
        initial = Bridge(self.s1, self.s2, self.store.root)
        self.assertEqual(initial.process(job, 2), normal)
        self.assertEqual(normal["native"]["state"], "outcome_unknown")
        self.assertEqual(normal["result"]["status"], 504)
        self.assertEqual(normal["result"]["records"], [])
        self.assertEqual(initial._intent(job)["event_sha256"], normal["native"]["receipt"]["event_sha256"])
        self.assertEqual(initial._intent(job)["result_sha256"], normal["receipt_binding"]["result_sha256"])

        admitted = self.bridge.admit(intent("restart-504", scenario="delayed"), 0)
        job = admitted["job_id"]
        crash = self.worker_process(job, 1, "sending_before_receipt", CRASH)
        before = self.bridge.snapshot(job)
        self.assertEqual(before["native"]["state"], "sending")
        self.assertIsNone(before["result"])
        self.assertIsNone(before["native"]["receipt"])
        row = self.bridge._intent(job)
        self.assertEqual(row["event_sha256"], self.s1.sha(before["native"]["callback"]))
        recovery = self.worker_process(job, 2, "none")
        self.assertNotEqual(crash, recovery)
        reopened = Bridge(self.s1, self.s2, self.store.root)
        after = reopened.snapshot(job)
        self.assert_receipt(after)
        self.assertEqual(after["native"]["state"], "outcome_unknown")
        self.assertEqual(after["native"]["callback"], before["native"]["callback"])
        self.assertEqual(after["native"]["receipt"]["event_sha256"], row["event_sha256"])
        self.assertEqual(after["receipt_binding"]["result_sha256"], row["result_sha256"])
        self.assertEqual(after["result"], normal["result"])
        self.assertEqual(reopened.process(job, 3), after)
        case("bound_504", "normal 504 and committed outbox restart both expose a verified 504 under native unknown",
             status=504, dispatches=1, reads=1, receipts=1, normal_binding=normal["receipt_binding"],
             exit=CRASH, crash_pid=crash, recovery_pid=recovery, recovered_binding=after["receipt_binding"])

    def test_mismatched_or_legacy_binding_suppresses_prepared_result(self):
        observed = {}
        for mode in ("event", "result", "malformed", "legacy"):
            with self.subTest(mode=mode):
                scenario = "ok" if mode == "legacy" else "delayed"
                admitted, bound = self.run_intent(intent("unbound-" + mode, scenario=scenario))
                job = admitted["job_id"]
                with self.store.tx() as db:
                    if mode == "event":
                        db.execute("UPDATE s3_settled_results SET event_sha256=? WHERE job_id=?", ("0" * 64, job))
                    elif mode == "result":
                        changed = self.s1.wire(bound["result"] | {"elapsed_ms": 99})
                        db.execute("UPDATE s3_intents SET prepared_result=? WHERE job_id=?", (changed, job))
                    elif mode == "malformed":
                        changed = b"{"
                        db.execute("UPDATE s3_intents SET prepared_result=? WHERE job_id=?", (changed, job))
                        db.execute("UPDATE s3_settled_results SET result_sha256=? WHERE job_id=?",
                                   (hashlib.sha256(changed).hexdigest(), job))
                    else:
                        db.execute("DELETE FROM s3_settled_results WHERE job_id=?", (job,))
                reopened = Bridge(self.s1, self.s2, self.store.root)
                after = reopened.process(job, 2)
                self.assert_receipt(after)
                self.assertEqual(after["native"], bound["native"])
                self.assertIsNone(after["result"])
                self.assertIsNone(after["receipt_binding"]["result_sha256"])
                self.assertEqual(reopened.process(job, 3), after)
                observed[mode] = {"native_state": after["native"]["state"], "native_receipt_unchanged": True,
                                  "result": None, "result_sha256": None}
        case("invalid_or_legacy_binding", "wrong event, changed bytes, malformed JSON and absent association are suppressed",
             **observed)

    def test_offline_denials_provenance_and_no_personal_fields(self):
        self.assertIs(LIVE_ENABLED, False)
        for overrides in ({"approval": "missing"}, {"synthetic": False}, {"operation": "wp_woo.update"},
                          {"budget": {"max_dispatches": 2, "max_units": 1}},
                          {"arguments": GA | {"property_id": "rejected-placeholder"}},
                          {"arguments": GA | {"start_date": "https://invalid.example"}}):
            with self.assertRaises(self.s1.InvalidContract):
                self.bridge.admit(intent("denied") | overrides, 0)
        for runtime_config in ({"endpoint": "https://invalid.example"}, {"credentials": "rejected-placeholder"}):
            with self.assertRaises(self.s1.InvalidContract):
                Bridge(self.s1, self.s2, self.store.root, **runtime_config)
        with self.assertRaisesRegex(RuntimeError, "socket audit boundary"):
            sys.audit("socket.connect", None, None)
        with tempfile.TemporaryDirectory(prefix="eng01a-s3-pin-negative-") as temp:
            staged = Path(temp)
            pins.stage(staged)
            file = staged / "fixtures.json"
            file.write_bytes(file.read_bytes() + b"\n")
            with self.assertRaisesRegex(RuntimeError, "pinned source drift"):
                pins.load(staged)
        _, view = self.run_intent(intent("provenance"))
        rows = view["result"]["records"] + view["result"]["attribution"]
        banned = {"lead_id", "user_id", "customer_id", "email_address", "phone"}
        for row in rows:
            self.assertEqual((row["source_status"], row["provenance"], row["data_classification"]),
                             ("SYNTHETIC", "MOCK", "SYNTHETIC"))
            self.assertFalse(banned & (row.keys() | row["data"].keys()))
        case("offline_safety", "malformed/unauthorized/live config denied, pin drift refused, synthetic provenance",
             invalid_intents=6, endpoint_denied=True, credentials_denied=True, socket_audit_denied=True,
             pin_mutation_rejected=True, normalized_rows=len(rows), personal_fields=0)


def worker(source, root, job, tick, fault):
    def checkpoint(name):
        if name == fault:
            print(json.dumps({"pid": os.getpid(), "checkpoint": name}), flush=True)
            os._exit(CRASH)

    Bridge(*pins.load(Path(source)), Path(root)).process(job, int(tick), checkpoint)
    print(json.dumps({"pid": os.getpid(), "checkpoint": "finished"}), flush=True)


if __name__ == "__main__":
    sys.addaudithook(socket_guard)
    if len(sys.argv) == 7 and sys.argv[1] == "--worker":
        worker(*sys.argv[2:])
    else:
        parser = argparse.ArgumentParser(description=__doc__)
        parser.add_argument("--evidence", type=Path)
        parser.add_argument("--test", action="append", help="run a named IntegrationTests method")
        args = parser.parse_args()
        available = unittest.defaultTestLoader.getTestCaseNames(IntegrationTests)
        names = args.test or available
        if any(name not in available for name in names):
            parser.error("--test requires a named IntegrationTests method")
        result = unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite(IntegrationTests(name) for name in names))
        if args.evidence and result.wasSuccessful():
            args.evidence.write_text(json.dumps({"tests_run": result.testsRun, "cases": RESULTS}, indent=2) + "\n",
                                     encoding="utf-8")
        sys.exit(0 if result.wasSuccessful() else 1)
