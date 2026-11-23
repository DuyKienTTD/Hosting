"""Changed-code tests for B2-P provenance, cutoff attribution, and Compose safety."""

from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest

import h6_b2p_preflight as p


class PreflightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.baseline = json.loads(p.BASE_EVIDENCE.read_bytes())
        cls.events = cls.baseline["events"]
        cls.owner = "a" * 32
        with tempfile.TemporaryDirectory(prefix="h6-b2p-test-") as scratch:
            path = Path(scratch).resolve()
            cls.spec, _, cls.source = p.prepare(path, cls.owner)
            rendered = p.b2o.docker("--context", "desktop-linux", "compose", "--project-directory", str(path),
                                    "-p", p.PROJECT, "--profile", "*", "-f", "-", "config", "--format", "json",
                                    "--no-path-resolution", input_data=p.b2o.canonical(cls.spec))
        cls.render = json.loads(rendered)

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
                     "after_read_end": without + [timer | {"mono_ns": read_end["mono_ns"] + 1}]}
        for label, events in mutations.items():
            with self.subTest(label=label), self.assertRaises(RuntimeError):
                p.verify_timer(events)

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
