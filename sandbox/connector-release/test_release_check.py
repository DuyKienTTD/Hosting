"""Run the S4 release delta against temporary, extracted Git blobs only."""

import argparse
import ast
from contextlib import closing
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest
from unittest.mock import patch

import release_check as release


OBSERVED = {}


def deny_socket(event, _):
    if event.startswith("socket."):
        raise RuntimeError("S4 socket audit boundary")


def load(path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ReleaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = release.read_manifest()
        cls.payloads = release.verify(cls.manifest)

    def setUp(self):
        self.root = Path(self.enterContext(tempfile.TemporaryDirectory(prefix="eng01a-s4-test-")))

    def test_two_independent_assemblies_are_identical(self):
        first = release.assemble(self.manifest, self.root / "first")
        second = release.assemble(self.manifest, self.root / "second")
        self.assertEqual(first, second)
        OBSERVED["repeatability"] = {"files": len(self.payloads), "bundle_sha256": first}

    def test_manifest_changes_fail_closed(self):
        mutations = {
            "baseline_tree": lambda m: m["baseline"].update(tree="0" * 40),
            "source_head": lambda m: m["packages"][0].update(head="0" * 40),
            "content_digest": lambda m: m["packages"][0]["files"][0].update(content_sha256="0" * 64),
            "undeclared_path": lambda m: m["packages"][0]["files"][0].update(path="sandbox/unknown.py"),
            "duplicate_path": lambda m: m["packages"][0]["files"].append(m["packages"][0]["files"][0]),
            "enable_network": lambda m: m["policy"].update(allow_external_network=True),
        }
        for name, mutate in mutations.items():
            with self.subTest(name=name):
                manifest = deepcopy(self.manifest)
                mutate(manifest)
                dest = self.root / name
                with self.assertRaisesRegex(RuntimeError, "pinned local Git snapshot"):
                    release.assemble(manifest, dest)
                self.assertFalse(dest.exists())
        OBSERVED["manifest_drift"] = {"denied_before_destination_creation": list(mutations)}

    def test_ambiguous_json_is_rejected(self):
        duplicate = self.root / "duplicate.json"
        duplicate.write_text('{"policy":{"MOCK_ONLY":false,"MOCK_ONLY":true}}', encoding="ascii")
        with self.assertRaisesRegex(RuntimeError, "duplicate manifest key"):
            release.read_manifest(duplicate)
        OBSERVED["ambiguous_json"] = {"duplicate_nested_key_rejected": True}

    def test_concurrent_ref_movement_is_rejected(self):
        pins = release.ref_pins()
        moved = pins | {release.MAIN: "0" * 40}
        with patch.object(release, "ref_pins", side_effect=[pins, moved]):
            with self.assertRaisesRegex(RuntimeError, "heads moved"):
                release.capture()
        OBSERVED["ref_movement"] = {"simulated_tracking_ref_movement_rejected": True}

    def test_assembly_refuses_modified_or_unexpected_files_and_overwrite(self):
        dest = self.root / "release"
        release.assemble(self.manifest, dest)
        extra = dest / "extra.py"
        extra.write_bytes(b"synthetic extra")
        with self.assertRaisesRegex(RuntimeError, "undeclared assembly file"):
            release.check_assembly(self.manifest, dest)
        with self.assertRaises(FileExistsError):
            release.assemble(self.manifest, dest)
        self.assertEqual(extra.read_bytes(), b"synthetic extra")
        extra.unlink()
        name, raw = next(iter(self.payloads.items()))
        (dest / name).write_bytes(raw + b"\n")
        with self.assertRaisesRegex(RuntimeError, "assembly content hash"):
            release.check_assembly(self.manifest, dest)
        OBSERVED["assembly_rejection"] = {"unexpected_file": True, "changed_bytes": True, "overwrite": True}

    def test_assembled_runtime_has_no_live_transport(self):
        runtime = ("offline_connector.py", "channel_mocks.py", "bridge.py")
        transport = {"socket", "ssl", "urllib", "requests", "http", "httpx", "aiohttp", "ftplib", "google", "subprocess"}
        for name, raw in self.payloads.items():
            if Path(name).name in runtime:
                syntax = ast.parse(raw)
                imported = {alias.name.split(".")[0] for node in ast.walk(syntax)
                            if isinstance(node, ast.Import) for alias in node.names}
                imported.update(node.module.split(".")[0] for node in ast.walk(syntax)
                                if isinstance(node, ast.ImportFrom) and node.module)
                self.assertFalse(imported & transport, name)
                self.assertTrue(any(isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant)
                                    and node.value.value is False and any(isinstance(target, ast.Name)
                                    and target.id == "LIVE_ENABLED" for target in node.targets)
                                    for node in syntax.body), name)
            if Path(name).name in (*runtime, "fixtures.json"):
                self.assertNotIn(b"http://", raw)
                self.assertNotIn(b"https://", raw)
        with self.assertRaisesRegex(RuntimeError, "S4 socket audit boundary"):
            sys.audit("socket.connect", None, None)
        OBSERVED["offline_runtime"] = {"modules_checked": list(runtime), "socket_audit_denial_observed": True}

    def test_assembled_unknown_receipt_survives_reopen_and_late_settlement(self):
        dest = self.root / "release"
        bundle = release.assemble(self.manifest, dest)
        integration = dest / "sandbox/connector-integration"
        pins = load(integration / "pinned_sources.py")
        bridge_class = load(integration / "bridge.py").Bridge
        sources = self.root / "pinned-imports"
        sources.mkdir()
        for name, (_, path, _) in pins.PINNED.items():
            (sources / name).write_bytes((dest / path).read_bytes())
        s1, s2 = pins.load(sources)
        store = self.enterContext(s1.temporary_sandbox())
        bridge = bridge_class(s1, s2, store.root)
        request = {"contract_version": 1, "synthetic": True, "approval": "synthetic_approved",
                   "idempotency_key": "fake-s4-unknown", "operation": "ga4.run_report",
                   "arguments": {"dimensions": ["date", "source", "channel"], "metrics": ["sessions"],
                                 "start_date": "2026-11-20", "end_date": "2026-11-21", "row_budget": 3},
                   "scenario": "delayed", "budget": {"max_dispatches": 1, "max_units": 1}, "deadline_ms": 20}
        admitted = bridge.admit(request, 0)
        job = admitted["job_id"]
        view = bridge.process(job, 1)
        self.assertEqual(view["native"]["state"], "outcome_unknown")
        self.assertEqual(view["native"]["channel"], "fixture")
        self.assertEqual(view["native"]["fake_dispatches"], 1)
        self.assertEqual(view["synthetic_read_attempts"], 1)
        self.assertFalse(view["external_effect_delivered"])
        self.assertEqual(view["result"]["status"], 504)
        self.assertEqual(view["result"]["records"], [])
        reopened = bridge_class(s1, s2, store.root)
        self.assertEqual(reopened.admit(request, 2)["job_id"], job)
        self.assertEqual(reopened.process(job, 2), view)
        with self.assertRaises(s1.Conflict):
            store.settle(job, admitted["native_request_sha256"], "completed", 3)
        self.assertEqual(reopened.process(job, 3), view)
        self.assertEqual(release.check_assembly(self.manifest, dest), bundle)
        journals = {}
        for db in store.root.glob("*.sqlite*"):
            with closing(sqlite3.connect(db.resolve().as_uri() + "?mode=ro", uri=True)) as connection:
                journals[db.name] = connection.execute("PRAGMA journal_mode").fetchone()[0]
        OBSERVED["assembled_unknown"] = {
            "state": view["native"]["state"], "native_channel": view["native"]["channel"],
            "synthetic_http": 504, "synthetic_records": 0,
            "receipt_binding": view["receipt_binding"], "fake_dispatches": 1, "synthetic_reads": 1,
            "stable_after_reopen": True, "late_settlement_rejected": True, "external_side_effect": False,
            "artifact_digest_unchanged": True, "observed_fixture_journals": journals,
        }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()
    sys.addaudithook(deny_socket)
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(ReleaseTests))
    with args.evidence.open("x", encoding="utf-8") as stream:
        json.dump({"run": result.testsRun, "failures": len(result.failures), "errors": len(result.errors),
                   "skipped": len(result.skipped), "passed": result.wasSuccessful(), "observed": OBSERVED},
                  stream, indent=2)
        stream.write("\n")
    sys.exit(not result.wasSuccessful())
