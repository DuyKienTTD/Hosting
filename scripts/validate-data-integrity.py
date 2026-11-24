#!/usr/bin/env python3
"""Read-only, stdlib repository integrity checks; no network or auto-remediation."""
import argparse
import datetime as dt
import json
from pathlib import Path, PurePosixPath
import re
import runpy
import subprocess
import sys

PIN = re.compile(r"https://github\.com/DuyKienTTD/Hosting/blob/[0-9a-f]{40}/tasks/[^\s)>]+")
LINK = re.compile(r"(?<!!)\[[^\]\n]+\]\(([^)\n]+)\)")
CREDENTIAL = re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|(?i:password|client_secret|access_token|api_key)\s*[:=]\s*['\"][^'\"\s]{12,}['\"]")
LIFECYCLE = {"DURABLE", "ACTIVE", "TEMPORARY"}

def git(root, *args):
    return subprocess.check_output(["git", "-C", str(root), *args], stderr=subprocess.DEVNULL).decode("utf-8")

def metadata(text):
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---\n", 4)
    if end < 0:
        return {}
    return dict(re.findall(r"^([a-z_]+):\s*([^\n]+)$", text[4:end], re.M))

def safe_path(root, name):
    p = PurePosixPath(name)
    if p.is_absolute() or ".." in p.parts or "\\" in name:
        raise ValueError("unsafe path")
    dest = (root / name).resolve()
    if not dest.is_relative_to(root.resolve()):
        raise ValueError("path escapes root")
    return dest

def inspect(root, changed, new, removed, today=None):
    root = Path(root).resolve()
    today = today or dt.date.today()
    findings = []
    def add(level, code, path):
        findings.append({"level": level, "code": code, "path": str(path)})
    try:
        runpy.run_path(str(root/"scripts/validate-catalog-partitions.py"))["validate"](root)
    except (OSError, ValueError, KeyError, AttributeError, IndexError):
        add("ERROR", "CATALOG_INVALID", "CATALOG.yaml")
    for rel in sorted(set(removed)):
        add("ERROR", "DELETION_REQUIRES_REVIEW", rel)
    for rel in sorted(set(changed) - set(removed)):
        try:
            file = safe_path(root, rel)
        except ValueError:
            add("ERROR", "UNSAFE_PATH", rel)
            continue
        if not file.is_file():
            add("ERROR", "MISSING_CHANGED_FILE", rel)
            continue
        name = file.name.lower()
        if name == ".env" or (name.startswith(".env.") and name != ".env.example") or file.suffix.lower() in {".pem", ".key", ".p12", ".pfx", ".sqlite", ".db", ".zip", ".tar", ".gz"}:
            add("ERROR", "SENSITIVE_OR_ARCHIVE_PATH", rel)
        if file.suffix.lower() not in {".md", ".yaml", ".yml", ".json", ".txt", ".py", ".ps1", ".sh", ".js", ".ts", ".tsx"}:
            continue
        if file.stat().st_size > 2_000_000:
            add("WARN", "LARGE_FILE_NOT_SCANNED", rel)
            continue
        try:
            text = file.read_text(encoding="utf-8")
        except UnicodeError:
            add("ERROR", "INVALID_TEXT_ENCODING", rel)
            continue
        if CREDENTIAL.search(text):
            add("ERROR", "CREDENTIAL_PATTERN_REVIEW", rel)
        if file.suffix != ".md":
            continue
        # Ignore fenced code examples; links outside fences are checked.
        prose = re.sub(r"(?ms)^\s*```.*?^\s*```[^\n]*", "", text)
        for match in LINK.finditer(prose):
            dest = match.group(1).split("#", 1)[0].split("?", 1)[0].strip()
            if not dest or re.match(r"^(https?://|mailto:|tel:)", dest):
                continue
            target = (file.parent / dest).resolve()
            if not target.is_relative_to(root) or not target.exists():
                add("ERROR", "BROKEN_RELATIVE_LINK", rel)
        m = metadata(text)
        operational = rel.startswith(("tasks/", "reports/", "checkpoints/")) and name != "readme.md"
        if operational and rel in new:
            if m.get("lifecycle") not in LIFECYCLE or not m.get("owner") or not m.get("task_id"):
                add("ERROR", "LIFECYCLE_METADATA_REQUIRED", rel)
            if m.get("lifecycle") in {"ACTIVE", "TEMPORARY"} and not (m.get("review_on") or m.get("retention_trigger")):
                add("ERROR", "RETENTION_TRIGGER_REQUIRED", rel)
            if rel.startswith("reports/") and not rel.startswith("reports/evidence/") and not PIN.search(text):
                add("ERROR", "PINNED_TASK_LINK_REQUIRED", rel)
            if rel.startswith("tasks/") and not ("READ_SET" in text and ("reports/" in text or "roadmap" in text.lower())):
                add("ERROR", "TASK_READSET_OR_REPORT_PATH_REQUIRED", rel)
        if m.get("review_on"):
            try:
                if dt.date.fromisoformat(m["review_on"]) < today:
                    add("WARN", "REVIEW_OVERDUE", rel)
            except ValueError:
                add("ERROR", "INVALID_REVIEW_DATE", rel)
    return findings

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--root", default=".")
    p.add_argument("--base", required=True)
    p.add_argument("--json", action="store_true")
    a = p.parse_args()
    root = Path(a.root).resolve()
    try:
        if not re.fullmatch(r"[0-9a-f]{40}", a.base):
            raise ValueError("base must be full trusted commit SHA")
        git(root, "rev-parse", "--verify", a.base+"^{commit}")
        changed = git(root, "diff", "--name-only", "--no-renames", a.base, "--").splitlines()
        new = git(root, "diff", "--name-only", "--diff-filter=A", "--no-renames", a.base, "--").splitlines()
        removed = git(root, "diff", "--name-only", "--diff-filter=D", "--no-renames", a.base, "--").splitlines()
        untracked = git(root, "ls-files", "--others", "--exclude-standard").splitlines()
        changed += untracked
        new += untracked
        findings = inspect(root, changed, set(new), removed)
        result = {"scope": "working_tree_delta_and_full_catalog", "base": a.base, "changed": len(set(changed)), "findings": findings}
        code = int(any(x["level"] == "ERROR" for x in findings))
        result["status"] = "FAIL" if code else "PASS_WITH_WARNINGS" if findings else "PASS"
    except (OSError, subprocess.CalledProcessError, ValueError):
        result = {"status": "BLOCKED_PREREQUISITE", "detail": "trusted base/Git working tree unavailable"}
        code = 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return code

if __name__ == "__main__":
    sys.exit(main())
