"""ENG-01A-S2 delta tests. No S1, sockets, HTTP clients or external fixtures."""

import argparse
import ast
import json
from pathlib import Path
import sys
import unittest

from channel_mocks import (
    DIMENSIONS, FIXTURE_FILE, GA4Mock, LIVE_ENABLED, ReadError, WpWooMock, digest,
    normalize_ga4, normalize_wp,
)


CASES = {}
REPORT = {"dimensions": DIMENSIONS, "metrics": ["sessions", "conversions"],
          "start_date": "2026-11-20", "end_date": "2026-11-21", "row_budget": 3}


def deny_network(event, _):
    if event.startswith("socket."):
        raise RuntimeError("S2 denies socket activity")


def save_case(name, expected, **observed):
    CASES[name] = {"expected": expected, "observed": observed}


class ChannelMockTests(unittest.TestCase):
    def setUp(self):
        self.ga4 = GA4Mock()
        self.wp = WpWooMock()

    def assert_read_error(self, status, read, *args, **kwargs):
        with self.assertRaises(ReadError) as failure:
            read(*args, **kwargs)
        self.assertEqual(failure.exception.status, status)

    def test_ga4_period_attribution_and_determinism(self):
        report = self.ga4.run_report(**REPORT)
        self.assertEqual(report, self.ga4.run_report(**REPORT))
        self.assertEqual(report["aggregate_row_count"], 3)
        self.assertEqual(report["period"], {"start_date": "2026-11-20", "end_date": "2026-11-21"})
        self.assertEqual((report["status"], report["provenance"], report["observed_at"]),
                         (200, "MOCK", "2026-11-23T09:00:00Z"))
        by_source = {row["source_record_id"]: row["data"] for row in report["attribution"]}
        expected = [("2026-11-20", "email", 5, 1), ("2026-11-20", "organic_search", 12, 2),
                    ("2026-11-21", "organic_search", 15, 3)]
        rows = []
        for event in report["records"]:
            data = event["data"]
            self.assertEqual({name: value["unit"] for name, value in data["metrics"].items()},
                             {"sessions": "count", "conversions": "count"})
            rows.append((data["date"], by_source[data["attribution_source_id"]]["channel"],
                         data["metrics"]["sessions"]["value"], data["metrics"]["conversions"]["value"]))
        self.assertEqual(rows, expected)
        self.assertEqual(len(report["attribution"]), 2)
        save_case("ga4_valid", "three attributed aggregates in inclusive period; deterministic repeat",
                  rows=rows, unique_source_records=2, report_sha256=digest(report))

    def test_ga4_rejects_invalid_requests_and_empty_period_is_valid(self):
        issues = {"dimension": {"dimensions": ["date", "source", "user_id"]},
                  "metric": {"metrics": ["user_email"]}, "duplicate_metric": {"metrics": ["sessions", "sessions"]},
                  "date_format": {"start_date": "20261120"}, "impossible_date": {"start_date": "2026-11-31"},
                  "reverse_period": {"start_date": "2026-11-22"}, "long_period": {"start_date": "2026-10-01"},
                  "future_period": {"end_date": "2026-11-24"}, "over_budget": {"row_budget": 2},
                  "bool_budget": {"row_budget": True}}
        for name, overrides in issues.items():
            with self.subTest(name=name):
                self.assert_read_error(422, self.ga4.run_report, **(REPORT | overrides))
        empty = self.ga4.run_report(**(REPORT | {"start_date": "2026-11-19", "end_date": "2026-11-19"}))
        self.assertEqual((empty["status"], empty["records"], empty["attribution"]), (200, [], []))
        save_case("ga4_validation", "invalid field/date/budget returns 422; empty valid report returns 200",
                  rejected=sorted(issues), rejection_status=422, empty_count=empty["aggregate_row_count"])

    def test_wp_resource_boundaries_and_locales(self):
        results = {}
        for locale in ("en", "vi"):
            for resource, kind, system in (("site", "content_asset", "wordpress"),
                                           ("posts", "content_asset", "wordpress"),
                                           ("pages", "content_asset", "wordpress"),
                                           ("products", "product", "woocommerce")):
                with self.subTest(locale=locale, resource=resource):
                    response = self.wp.list(resource, locale=locale, limit=1)
                    self.assertEqual(response["status"], 200)
                    row = response["records"][0]
                    self.assertEqual((row["record_type"], row["source_system"], row["data"]["locale"]), (kind, system, locale))
                    detail = self.wp.get(resource, locale=locale, record_id=row["source_record_id"])
                    self.assertEqual(detail["records"], [row])
                    ids = [row["source_record_id"]]
                    if resource == "site":
                        self.assertIsNone(response["next_cursor"])
                    else:
                        self.assertIsNotNone(response["next_cursor"])
                        page = self.wp.list(resource, locale=locale, limit=1, cursor=response["next_cursor"])
                        self.assertEqual(page["records"][0]["data"]["locale"], locale)
                        ids.append(page["records"][0]["source_record_id"])
                        self.assertNotEqual(ids[0], ids[1])
                    results[f"{resource}:{locale}"] = ids
        en = self.wp.list("products", locale="en")["records"][0]["data"]["price"]
        vi = self.wp.list("products", locale="vi")["records"][0]["data"]["price"]
        self.assertEqual(en, {"value": 1200, "currency": "USD", "unit": "minor_currency_unit"})
        self.assertEqual(vi, {"value": 49000, "currency": "VND", "unit": "minor_currency_unit"})
        save_case("wp_resource_locale", "four read resources in EN and VI; lists paginate, currencies preserved",
                  source_record_ids=results, prices=[en, vi])

    def test_cursor_scope_and_watermark_with_tied_updates(self):
        def page(**opts):
            return self.wp.list("posts", locale="en", limit=1, **opts)

        first = page()
        second = page(cursor=first["next_cursor"])
        third = page(cursor=second["next_cursor"])
        self.assertEqual(second, page(cursor=first["next_cursor"]))
        self.assertIsNone(first["next_watermark"])
        self.assertIsNone(second["next_watermark"])
        self.assertIsNone(third["next_cursor"])
        ids = [result["records"][0]["source_record_id"] for result in (first, second, third)]
        self.assertEqual(ids, ["fake-post-en-a", "fake-post-en-b", "fake-post-en-c"])
        stale = {"updated_at": "2026-11-21T00:00:00Z", "source_record_id": "fake-post-en-b"}
        fresh = page(modified_since=stale)
        self.assertEqual([row["source_record_id"] for row in fresh["records"]], [ids[-1]])
        unchanged = page(modified_since=third["next_watermark"])
        self.assertEqual((unchanged["records"], unchanged["next_watermark"]), ([], third["next_watermark"]))
        for target in ({"locale": "vi", "limit": 1}, {"locale": "en", "limit": 2},
                       {"locale": "en", "limit": 1, "modified_since": stale}):
            self.assert_read_error(409, self.wp.list, "posts", cursor=first["next_cursor"], **target)
        bound = first["next_cursor"].split(":")[0]
        for cursor in ("invalid", f"{bound}:0", f"{bound}:9"):
            self.assert_read_error(422, page, cursor=cursor)
        self.assert_read_error(422, page, modified_since=stale | {"updated_at": "2026-11-24T00:00:00Z"})
        save_case("wp_pagination", "stable same-snapshot cursor, exclusive watermark with tie-breaker, no skips",
                  page_ids=ids, repeat_equal=True, stale_cursor_status=409, malformed_status=422,
                  incremental_ids=[ids[-1]], terminal_watermark=third["next_watermark"])

    def test_errors_unknown_and_read_isolation(self):
        original_ga = self.ga4.run_report(**REPORT)
        first = self.wp.list("posts", locale="en", limit=1)
        expected = self.wp.list("posts", locale="en", limit=1, cursor=first["next_cursor"])
        statuses = {}
        for scenario, wanted in (("forbidden", 403), ("quota", 429), ("delayed", 504)):
            outcome = "outcome_unknown" if scenario == "delayed" else "failed"
            options = {"scenario": scenario, "deadline_ms": 15}
            ga = self.ga4.run_report(**REPORT, **options)
            wp = self.wp.list("posts", locale="en", limit=1, cursor=first["next_cursor"], **options)
            for result in (ga, wp):
                self.assertEqual((result["status"], result["outcome"], result["records"]), (wanted, outcome, []))
                self.assertNotIn("next_cursor", result)
                self.assertNotIn("next_watermark", result)
                if scenario == "delayed":
                    self.assertEqual(result["elapsed_ms"], 15)
                if scenario == "quota":
                    self.assertEqual(result["retry_after_ms"], 100)
            statuses[scenario] = {"status": wanted, "outcome": outcome}
        missing = self.wp.get("pages", locale="vi", record_id="fake-page-vi-z")
        self.assertEqual((missing["status"], missing["outcome"], missing["records"]), (404, "failed", []))
        self.assert_read_error(404, self.wp.list, "orders", locale="en")
        first["records"][0]["data"]["title"] = "Caller change"
        self.assertNotEqual(self.wp.list("posts", locale="en", limit=1), first)
        self.assertEqual(self.wp.list("posts", locale="en", limit=1, cursor=first["next_cursor"]), expected)
        self.assertEqual(self.ga4.run_report(**REPORT), original_ga)
        save_case("read_faults_isolation", "403/429/404/unknown omit rows and cannot advance local read state",
                  faults=statuses | {"missing": {"status": 404, "outcome": "failed"}},
                  before_after_equal=True, response_mutation_isolated=True)

    def test_mapping_schema_provenance_and_no_identity_fields(self):
        fixture = json.loads(FIXTURE_FILE.read_text(encoding="utf-8"))
        stamp = fixture["observed_at"]
        normalized = [*normalize_ga4(fixture["ga4"][0], stamp),
                      normalize_wp(fixture["wp_woo"][0], stamp), normalize_wp(fixture["wp_woo"][-1], stamp)]
        forbidden = {"lead", "lead_id", "user_id", "customer_id", "email_address", "phone"}
        for row in normalized:
            self.assertEqual(set(row), {"schema_version", "record_type", "source_system", "source_record_id",
                                        "observed_at", "data_classification", "source_status", "provenance", "data"})
            self.assertEqual((row["schema_version"], row["data_classification"], row["source_status"], row["provenance"]),
                             (1, "SYNTHETIC", "SYNTHETIC", "MOCK"))
            self.assertFalse(forbidden & (row.keys() | row["data"].keys()))
        ga = fixture["ga4"][0]
        wp = fixture["wp_woo"][-1]
        mutations = [(normalize_ga4, ga | {"channel": "email"}),
                     (normalize_ga4, ga | {"engaged_sessions": ga["sessions"] + 1}),
                     (normalize_ga4, ga | {"user_id": "rejected-placeholder"}),
                     (normalize_wp, wp | {"locale": "en"}),
                     (normalize_wp, wp | {"currency": "UNKNOWN"}),
                     (normalize_wp, wp | {"customer_id": "rejected-placeholder"}),
                     (normalize_wp, wp | {"updated_at": "2026-11-24T00:00:00Z"})]
        for normalizer, invalid in mutations:
            self.assert_read_error(422, normalizer, invalid, stamp)
        save_case("normalized_schema", "four normalized types with declared provenance and no lead/account identity",
                  record_types=sorted(row["record_type"] for row in normalized), inconsistent_rows_rejected=len(mutations))

    def test_offline_boundary_and_source_imports(self):
        self.assertIs(LIVE_ENABLED, False)
        imports = set()
        for node in ast.walk(ast.parse(FIXTURE_FILE.with_name("channel_mocks.py").read_bytes())):
            if isinstance(node, ast.Import):
                imports.update(alias.name for alias in node.names)
            if isinstance(node, ast.ImportFrom):
                imports.add(node.module)
        self.assertEqual(imports, {"datetime", "hashlib", "json", "pathlib", "re"})
        for adapter in (GA4Mock, WpWooMock):
            self.assert_read_error(422, adapter, endpoint="https://invalid.example")
            self.assert_read_error(422, adapter, credentials="rejected-placeholder")
        with self.assertRaisesRegex(RuntimeError, "denies socket"):
            sys.audit("socket.connect", None, None)
        for write in ("create", "update", "delete", "post", "put", "write"):
            self.assertFalse(hasattr(self.wp, write))
        save_case("offline_boundary", "no socket or write method; remote and credential configuration fail closed",
                  imports=sorted(imports), live_enabled=False, remote_config_denied=True,
                  credential_config_denied=True, socket_audit_self_check="denied")


if __name__ == "__main__":
    sys.addaudithook(deny_network)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence", type=Path)
    args = parser.parse_args()
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(ChannelMockTests))
    if args.evidence and result.wasSuccessful():
        args.evidence.write_text(json.dumps({"tests_run": result.testsRun, "cases": CASES}, indent=2) + "\n",
                                 encoding="utf-8")
    sys.exit(0 if result.wasSuccessful() else 1)
