"""Targeted checks against a synthetic local Git repository."""

import argparse
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest

from validate import Git, validate


OBSERVED = {}
TASK = "tasks/sample.md"
REPORT = "reports/sample.md"
EVIDENCE = "reports/evidence/sample.json"
PLAN = "tasks/plan.md"
CATALOG = ("schema_version: 1\ndocuments:\n"
           "  - id: sample\n    path: tasks/sample.md\n"
           "  - id: report-sample\n    path: reports/sample.md\n"
           "  - id: evidence-sample\n    path: reports/evidence/sample.json\n")


class ValidatorTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(self.enterContext(tempfile.TemporaryDirectory(prefix="gov02-fixture-")))
        self.git = Git(self.root)
        self.git.run("init", "-q")
        self.git.run("config", "user.email", "fixture@example.invalid")
        self.git.run("config", "user.name", "Synthetic Fixture")
        self.git.run("config", "commit.gpgsign", "false")
        self.write(TASK, "---\nid: sample\nowner: codex\nstatus: ready_for_review\n---\n")
        self.write(REPORT, "---\nid: report-sample\nstatus: current\n---\n\nFIXTURE_PASS\n")
        self.write(EVIDENCE, '{"verdict":"FIXTURE_PASS"}\n')
        self.write(PLAN, "| DEMO | task known |\n")
        self.write("CATALOG.yaml", CATALOG)
        self.write("STATE.md", "[report](reports/sample.md)\n")
        self.write("CHANGELOG.md", "# Change history\n")
        self.commit()
        main = self.pin("main")
        item = self.pin("sample") | {
            "task_id": "sample", "portfolio_id": "DEMO", "owner": "codex", "pr": 10,
            "base": main["head"], "scope": "OFFLINE", "verdict": "FIXTURE_PASS",
            "approval": "OFFLINE_ACCEPTED", "pr_draft": False, "production_ready": False,
            "readiness": ["QA_PASS_OFFLINE", "LINUX_NOT_RUN", "REAL_UNTESTED"], "dependencies": [],
            "task": self.blob(TASK), "report": self.blob(REPORT), "evidence": self.blob(EVIDENCE),
        }
        self.manifest = {"version": 1, "baseline": main, "plan": self.pin("plan") | self.blob(PLAN) | {"pr": 6},
                         "packages": [item]}

    def write(self, path, text):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")

    def commit(self):
        self.git.run("add", "-A")
        self.git.run("-c", "core.hooksPath=.git/disabled-fixture-hooks", "commit", "-qm", "synthetic fixture")

    def pin(self, name):
        ref = "refs/remotes/origin/" + name
        head = self.git.run("rev-parse", "HEAD").decode().strip()
        self.git.run("update-ref", ref, head)
        return {"ref": ref, "head": head, "tree": self.git.run("rev-parse", head + "^{tree}").decode().strip()}

    def blob(self, path):
        return {"path": path, "blob": self.git.run("rev-parse", "HEAD:" + path).decode().strip()}

    def verify_issue(self, manifest, code, severity="error"):
        result = validate(manifest, self.git)
        observed = [row for row in result["issues"] if row["code"] == code]
        self.assertEqual([row["severity"] for row in observed], [severity])
        OBSERVED.setdefault(self._testMethodName, []).append({"expected": [code, severity], "observed": observed})

    def test_positive(self):
        result = validate(self.manifest, self.git)
        self.assertEqual(result["issues"], [])
        self.assertEqual((result["source_count"], result["artifact_count"]), (3, 3))
        OBSERVED[self._testMethodName] = {"expected": "3 sources, 3 artifacts, no findings",
                                          "observed": {"sources": 3, "artifacts": 3, "issues": []}}

    def test_missing_report_evidence_or_source(self):
        for role in ("report", "evidence"):
            with self.subTest(role=role):
                manifest = deepcopy(self.manifest)
                path = "reports/evidence/missing.json" if role == "evidence" else "reports/missing.md"
                manifest["packages"][0][role]["path"] = path
                self.verify_issue(manifest, "MISSING_" + role.upper())
        manifest = deepcopy(self.manifest)
        manifest["plan"]["path"] = "tasks/missing.md"
        self.verify_issue(manifest, "REFERENCED_SOURCE_MISSING")

    def test_duplicate_catalog_and_manifest_id(self):
        self.write("CATALOG.yaml", CATALOG + "  - id: sample\n    path: tasks/sample.md\n")
        self.commit()
        self.manifest["packages"][0].update(self.pin("sample"))
        self.verify_issue(self.manifest, "DUPLICATE_CATALOG_ID")
        self.manifest["packages"].append(deepcopy(self.manifest["packages"][0]) | {"pr": 13})
        self.verify_issue(self.manifest, "DUPLICATE_TASK_ID")

    def test_sha_drift_and_missing_local_commit(self):
        for role, key in (("baseline", "tree"), ("report", "blob")):
            with self.subTest(role=role):
                manifest = deepcopy(self.manifest)
                obj = manifest["baseline"] if role == "baseline" else manifest["packages"][0]["report"]
                obj[key] = "0" * 40
                self.verify_issue(manifest, "SHA_DRIFT")
        manifest = deepcopy(self.manifest)
        manifest["packages"][0]["head"] = "0" * 40
        self.verify_issue(manifest, "SOURCE_UNAVAILABLE")

    def test_stale_plan_for_existing_task(self):
        self.write(PLAN, "| DEMO | NO_TASK_YET |\n| FUTURE | NO_TASK_YET |\n")
        self.commit()
        self.manifest["plan"].update(self.pin("plan") | self.blob(PLAN))
        self.verify_issue(self.manifest, "STALE_NO_TASK_YET", "finding")

    def test_production_claim_with_linux_unrun(self):
        self.manifest["packages"][0]["production_ready"] = True
        self.verify_issue(self.manifest, "DEPLOYMENT_CONTRADICTION")

    def test_draft_cannot_be_indexed_as_approved(self):
        manifest = deepcopy(self.manifest)
        manifest["packages"][0]["pr_draft"] = True
        self.verify_issue(manifest, "DRAFT_AS_APPROVED")
        self.write(REPORT, "---\nid: report-sample\nstatus: draft_ready_for_review\n---\nFIXTURE_PASS\n")
        self.commit()
        self.manifest["packages"][0].update(self.pin("sample") | {"report": self.blob(REPORT)})
        self.verify_issue(self.manifest, "DRAFT_AS_APPROVED")
        marked = CATALOG.replace("    path: tasks/sample.md\n", "    path: tasks/sample.md\n    status: approved\n")
        self.write("CATALOG.yaml", marked)
        self.commit()
        self.manifest["packages"][0].update(self.pin("sample") | {"approval": "DRAFT", "pr_draft": True})
        self.verify_issue(self.manifest, "DRAFT_AS_APPROVED")

    def second_package(self, *, report_id="report-sample", report_path="reports/other.md"):
        """Pin a second package at a new Git snapshot, reusing or replacing its report path."""
        self.write("tasks/other.md", "---\nid: other\nowner: codex\nstatus: ready_for_review\n---\n")
        if report_path != REPORT:
            self.write(report_path, f"---\nid: {report_id}\nstatus: current\n---\n\nFIXTURE_PASS\n")
        self.write("reports/evidence/other.json", '{"verdict":"FIXTURE_PASS"}\n')
        more_catalog = ("  - id: other\n    path: tasks/other.md\n"
                        "  - id: other-evidence\n    path: reports/evidence/other.json\n")
        if report_path != REPORT:
            more_catalog += "  - id: other-report\n    path: reports/other.md\n"
        self.write("CATALOG.yaml", CATALOG + more_catalog)
        self.commit()
        item = deepcopy(self.manifest["packages"][0])
        item.update(self.pin("other") | {
            "task_id": "other", "portfolio_id": "DEMO2", "pr": 11,
            "task": self.blob("tasks/other.md"),
            "report": self.blob(report_path),
            "evidence": self.blob("reports/evidence/other.json"),
        })
        manifest = deepcopy(self.manifest)
        manifest["packages"].append(item)
        return manifest

    def test_cross_package_document_id_collision(self):
        manifest = self.second_package()
        findings = [row for row in validate(manifest, self.git)["issues"]
                    if row["code"] == "DUPLICATE_DOCUMENT_ID"]
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["subject"], "report-sample")
        self.assertEqual(findings[0]["severity"], "finding")
        self.assertIn("reports/sample.md", findings[0]["detail"])
        self.assertIn("reports/other.md", findings[0]["detail"])
        self.assertFalse(any(row["code"] in {"DUPLICATE_TASK_ID", "DUPLICATE_CATALOG_ID"}
                             for row in validate(manifest, self.git)["issues"]))

    def test_repeated_path_in_multiple_snapshots_is_not_collision(self):
        manifest = self.second_package(report_path=REPORT)
        findings = [row for row in validate(manifest, self.git)["issues"]
                    if row["code"] in {"DUPLICATE_DOCUMENT_ID", "DOCUMENT_ID_REUSED"}]
        self.assertEqual(findings, [])

    def test_different_document_ids_remain_valid(self):
        manifest = self.second_package(report_id="report-other")
        findings = [row for row in validate(manifest, self.git)["issues"]
                    if row["code"] in {"DUPLICATE_DOCUMENT_ID", "DOCUMENT_ID_REUSED"}]
        self.assertEqual(findings, [])

    def test_within_package_document_id_reused_still_reported(self):
        self.write(REPORT, "---\nid: sample\nstatus: current\n---\n\nFIXTURE_PASS\n")
        self.commit()
        self.manifest["packages"][0].update(self.pin("sample") | {"report": self.blob(REPORT)})
        findings = [row["code"] for row in validate(self.manifest, self.git)["issues"]]
        self.assertIn("DOCUMENT_ID_REUSED", findings)
        self.assertIn("DUPLICATE_DOCUMENT_ID", findings)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()
    run = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(ValidatorTests))
    with args.evidence.open("x", encoding="utf-8") as stream:
        json.dump({"run": run.testsRun, "failures": len(run.failures), "errors": len(run.errors),
                   "skipped": len(run.skipped), "observed": OBSERVED}, stream, indent=2)
    raise SystemExit(not run.wasSuccessful())
