"""Changed-code tests for B2-P provenance, cutoff attribution, and Compose safety."""

from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import h6_b2p_preflight as p


class PreflightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.events = json.loads(p.BASE_EVIDENCE.read_bytes())["events"]
        cls.owner = "a" * 32

    def test_base_projection_matches_and_rejects_drift(self):
        wf = p.target_workflow()
        self.assertEqual(p.verified_projection(wf), p.b2o.PROJECTION)
        node = next(n for n in wf["nodes"] if n["id"] == "call-reasoner")
        node["parameters"]["options"]["timeout"] += 1
        with self.assertRaisesRegex(RuntimeError, "projection drift"):
            p.verified_projection(wf)

    def test_saved_cutoff_requires_unique_causal_guard_timer(self):
        self.assertGreater(p.verify_timer(self.events)["timer_to_read_end_s"], 0)
        timer = next(e for e in self.events if e["event"] == "guard_response_timer_fired")
        read_end = next(e for e in self.events if e["event"] == "transport_read_ended")
        without = [e for e in self.events if e is not timer]
        mutations = {"missing": without, "duplicate": self.events + [timer],
                     "wrong_role": without + [timer | {"role": "bridge"}],
                     "mixed_role": self.events + [timer | {"role": "bridge"}],
                     "non_integer_timestamp": without + [timer | {"mono_ns": str(timer["mono_ns"])}],
                     "after_read_end": without + [timer | {"mono_ns": read_end["mono_ns"] + 1}]}
        for label, events in mutations.items():
            with self.subTest(label=label), self.assertRaises(RuntimeError):
                p.verify_timer(events)

    def test_other_task_timer_is_outside_task_scope(self):
        timer = next(e for e in self.events if e["event"] == "guard_response_timer_fired")
        self.assertEqual(p.verify_timer(self.events + [timer | {"task": "b2o-31", "role": "bridge"}]),
                         p.verify_timer(self.events))

    def test_candidate_projection_pins_staged_content_before_returning_spec(self):
        with tempfile.TemporaryDirectory(prefix="h6-b2p-d1-projection-") as scratch:
            path = Path(scratch).resolve()
            spec, _, _, provenance = p.prepare(path, self.owner)
            staged = path / provenance["file"]
            candidate = p.verified_candidate_projection(staged.read_bytes(), spec)
            self.assertEqual(candidate, p.CANDIDATE_PROJECTION_SHA256)
            self.assertNotEqual(candidate, p.b2o.PROJECTION)
            self.assertEqual(provenance["candidate_staged_file_sha256"], p.digest(staged.read_bytes()))
            baseline_specification = p.b2o.specification

            def stage_wrong_route(staging_path, owner):
                result = baseline_specification(staging_path, owner)
                file = staging_path / "workflows.json"
                workflows = json.loads(file.read_bytes())
                node = next(n for n in workflows[0]["nodes"] if n["id"] == "call-reasoner")
                node["parameters"]["url"] += "/unexpected"
                file.write_bytes(p.b2o.canonical(workflows))
                return result

            with patch.object(p.b2o, "specification", side_effect=stage_wrong_route):
                with self.assertRaisesRegex(RuntimeError, "staged candidate workflow projection drift"):
                    p.prepare(path, self.owner)

    def test_candidate_rejects_changed_bytes_after_copy(self):
        with tempfile.TemporaryDirectory(prefix="h6-b2p-d1-copy-") as scratch:
            path = Path(scratch).resolve()
            _, _, _, provenance = p.prepare(path, self.owner)
            raw = (path / provenance["file"]).read_bytes()
            pin = provenance["candidate_staged_file_sha256"]
            copied = path / "copied-workflows.json"
            copied.write_bytes(raw)
            p.verify_staged_workflow(copied, pin)
            # Semantics are unchanged, so only the exact-byte check can catch this.
            copied.write_bytes(raw + b"\n")
            self.assertEqual(json.loads(raw), json.loads(copied.read_bytes()))
            with self.assertRaisesRegex(RuntimeError, "staged workflow bytes changed"):
                p.verify_staged_workflow(copied, pin)
            with self.assertRaisesRegex(RuntimeError, "missing exact staged workflow digest"):
                p.verify_staged_workflow(copied, None)


class RenderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.owner = "a" * 32
        with tempfile.TemporaryDirectory(prefix="h6-b2p-test-") as scratch:
            path = Path(scratch).resolve()
            cls.spec, _, cls.source, _ = p.prepare(path, cls.owner)
            rendered = p.b2o.docker("--context", "desktop-linux", "compose", "--project-directory", str(path),
                                    "-p", p.PROJECT, "--profile", "*", "-f", "-", "config", "--format", "json",
                                    "--no-path-resolution", input_data=p.b2o.canonical(cls.spec))
        cls.render = json.loads(rendered)

    def test_candidate_isolation_rejects_drift(self):
        p.validate(self.render, self.spec, self.owner, self.source)
        for risk in ("host_port", "host_bind", "external_network", "volume_owner", "memory_cap"):
            render = deepcopy(self.render)
            if risk == "host_port":
                render["services"]["guard"]["ports"] = [{"target": 8081, "published": "8081"}]
            elif risk == "host_bind":
                render["services"]["guard"]["volumes"][0]["source"] = "/var/run/docker.sock"
            elif risk == "external_network":
                render["networks"]["upstream"]["external"] = True
            elif risk == "volume_owner":
                render["volumes"]["receipt"]["labels"] = {}
            else:
                render["services"]["n8n"]["mem_limit"] = "0"
            with self.subTest(risk=risk), self.assertRaises(RuntimeError):
                p.validate(render, self.spec, self.owner, self.source)

    def test_projection_redacts_all_values_and_retains_topology(self):
        view = p.public_projection(self.render, self.source)
        self.assertEqual(set(view["services"]), set(p.b2o.NETWORKS))
        for row in view["services"].values():
            self.assertEqual(set(row["environment"].values()), {"<redacted-synthetic-config>"})
            self.assertNotIn(self.owner, row["volumes"][0]["source"])
        for collection in ("services", "volumes", "networks"):
            self.assertTrue(all(row["labels"][p.OWNER_LABEL] == "<owner-nonce>"
                                for row in view[collection].values()))


if __name__ == "__main__":
    unittest.main(verbosity=2)
