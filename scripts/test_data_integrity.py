import importlib.util
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location("integrity", Path(__file__).with_name("validate-data-integrity.py"))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class IntegrityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.put("scripts/validate-catalog-partitions.py", "def validate(root): return 1\n")
    def put(self, rel, text):
        p = self.root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    def codes(self, changed, new=(), removed=()):
        return {x["code"] for x in mod.inspect(self.root, changed, set(new), removed)}
    def test_clean(self):
        self.put("README.md", "# OK\n")
        self.assertEqual(self.codes(["README.md"]), set())
    def test_broken_link(self):
        self.put("README.md", "[bad](absent.md)")
        self.assertIn("BROKEN_RELATIVE_LINK", self.codes(["README.md"]))
    def test_delete(self):
        self.assertIn("DELETION_REQUIRES_REVIEW", self.codes([], removed=["old.md"]))
    def test_missing_metadata(self):
        self.put("tasks/new.md", "# Task")
        self.assertIn("LIFECYCLE_METADATA_REQUIRED", self.codes(["tasks/new.md"], ["tasks/new.md"]))
    def test_legacy_unchanged_schema(self):
        self.put("tasks/old.md", "# Task")
        self.assertEqual(self.codes(["tasks/old.md"]), set())
    def test_pinned_report(self):
        self.put("reports/new.md", "---\nlifecycle: DURABLE\nowner: Work\ntask_id: T1\n---\n")
        self.assertIn("PINNED_TASK_LINK_REQUIRED", self.codes(["reports/new.md"], ["reports/new.md"]))
    def test_path_escape(self):
        self.assertIn("UNSAFE_PATH", self.codes(["../outside.md"]))
    def test_sensitive_path(self):
        self.put(".env", "")
        self.assertIn("SENSITIVE_OR_ARCHIVE_PATH", self.codes([".env"]))
    def test_catalog_failure(self):
        self.put("scripts/validate-catalog-partitions.py", "def validate(root): raise ValueError('bad')\n")
        self.assertIn("CATALOG_INVALID", self.codes([]))

    def test_duplicate_knowledge(self):
        body = "Reusable verified knowledge. " * 8
        self.put("knowledge/a.md", body)
        self.put("knowledge/b.md", body)
        self.assertIn("EXACT_NORMALIZED_KNOWLEDGE_DUPLICATE", self.codes(["knowledge/b.md"]))
    def test_duplicate_id(self):
        body = "---\nid: same\n---\n"
        self.put("knowledge/a.md", body)
        self.put("knowledge/b.md", body)
        self.assertIn("DUPLICATE_DOCUMENT_ID", self.codes(["knowledge/b.md"]))
    def test_authority_collision(self):
        body = "---\nauthority_key: policy:retention\nstatus: current\n---\n"
        self.put("rules/a.md", body)
        self.put("rules/b.md", body)
        self.assertIn("MULTIPLE_ACTIVE_AUTHORITY_CLAIMS", self.codes(["rules/b.md"]))
    def test_wrong_authority_source(self):
        self.put("knowledge/a.md", "---\nauthority_key: policy:retention\nstatus: current\n---\n")
        self.assertIn("AUTHORITY_WRONG_SOURCE", self.codes(["knowledge/a.md"]))
    def test_reverse_dependency(self):
        self.put("knowledge/a.md", "[source](b.md)")
        self.assertIn("DELETED_REFERENCED_DOCUMENT", self.codes([], removed=["knowledge/b.md"]))
    def test_change_impact(self):
        self.put("knowledge/a.md", "[source](b.md)")
        self.put("knowledge/b.md", "Source")
        metrics = {}
        mod.inspect(self.root, ["knowledge/b.md"], set(), [], metrics=metrics)
        self.assertIn({"source": "knowledge/a.md", "target": "knowledge/b.md"}, metrics["direct_impacts"])

if __name__ == "__main__":
    unittest.main()
