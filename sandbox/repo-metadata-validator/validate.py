"""Audit a versioned repository metadata snapshot using local Git objects."""

import argparse
from collections import Counter, defaultdict
from functools import cache
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys


SHA = re.compile(r"[0-9a-f]{40}\Z")
IDENTIFIER = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]*\Z")
READINESS = {"SOURCE_REVIEW", "QA_PASS_OFFLINE", "QA_PENDING", "LINUX_NOT_RUN", "REAL_UNTESTED", "BLOCKED"}
SHARED = ("CATALOG.yaml", "STATE.md", "CHANGELOG.md")
ROLES = {"task": ("tasks/", ".md"), "report": ("reports/", ".md"), "evidence": ("reports/evidence/", ".json")}


class Unavailable(RuntimeError):
    pass


def require(condition, message):
    if not condition:
        raise ValueError(message)


def unique_keys(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, f"duplicate JSON key: {key}")
        result[key] = value
    return result


def sha(value):
    return isinstance(value, str) and SHA.fullmatch(value) is not None


def safe_path(value):
    return (isinstance(value, str) and re.fullmatch(r"[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)*", value)
            and not {".", ".."}.intersection(value.split("/")))


class Git:
    def __init__(self, root):
        self.root = root

    def run(self, *args):
        env = os.environ | {"GIT_ALLOW_PROTOCOL": "", "GIT_NO_LAZY_FETCH": "1", "GIT_NO_REPLACE_OBJECTS": "1"}
        result = subprocess.run(["git", *args], cwd=self.root, env=env, capture_output=True)
        if result.returncode:
            raise Unavailable(f"local Git {args[0]} could not read {args[-1]}")
        return result.stdout

    @cache
    def inventory(self, head):
        result = {}
        for row in self.run("ls-tree", "-r", "-z", head).split(b"\0"):
            if row:
                header, name = row.split(b"\t", 1)
                mode, kind, oid = header.decode("ascii").split()
                if kind == "blob" and mode in {"100644", "100755"}:
                    result[name.decode("utf-8")] = oid
        return result

    @cache
    def blob(self, oid):
        raw = self.run("cat-file", "blob", oid)
        header = f"blob {len(raw)}\0".encode("ascii")
        if hashlib.sha1(header + raw).hexdigest() != oid:
            raise Unavailable(f"Git blob content hash differs for {oid}")
        return raw


def frontmatter(text):
    lines = text.splitlines()
    if lines and lines[0] == "---" and "---" in lines[1:]:
        return dict(re.findall(r"^([a-z_]+): *([^\n]+)$", "\n".join(lines[1:lines.index("---", 1)]), re.M))
    return {}


def catalog_entries(text):
    # Read the repository's current documents-list layout, without YAML execution.
    _, marker, documents = text.partition("\ndocuments:\n")
    require(marker, "unsupported CATALOG documents layout")
    rows = re.split(r"(?m)^  - ", documents)[1:]
    pairs = []
    for row in rows:
        match = re.match(r"id: (\S+)\n    path: (\S+)\n", row)
        require(match is not None and safe_path(match[2]), "unsupported CATALOG entry")
        status = re.search(r"^    status: ([A-Za-z_-]+)\s*$", row, re.M)
        pairs.append((match[1], match[2], status[1].lower() if status else None))
    return pairs


def validate(manifest, git):
    require(type(manifest["version"]) is int and manifest["version"] == 1, "unsupported manifest version")
    issues = []
    sources = []
    artifacts = []

    def issue(code, subject, detail, severity="error"):
        issues.append({"code": code, "subject": str(subject), "detail": detail, "severity": severity})

    def source(pin, subject):
        head, tree, ref = pin["head"], pin["tree"], pin["ref"]
        require(sha(head) and sha(tree) and isinstance(ref, str)
                and re.fullmatch(r"refs/remotes/origin/[A-Za-z0-9_./-]+", ref), f"invalid source pin: {subject}")
        try:
            actual_tree = git.run("rev-parse", "--verify", head + "^{tree}").decode().strip()
            actual_head = git.run("rev-parse", "--verify", ref + "^{commit}").decode().strip()
            if actual_tree != tree or actual_head != head:
                issue("SHA_DRIFT", subject, f"observed tree {actual_tree}, head {actual_head}")
            git.inventory(head)
        except Unavailable as exc:
            issue("SOURCE_UNAVAILABLE", subject, str(exc))
            return False
        sources.append({"subject": str(subject), "ref": ref, "head": head, "tree": tree})
        return True

    def read(head, path, subject, missing_code, expected=None):
        require(safe_path(path), f"unsafe source path: {path}")
        oid = git.inventory(head).get(path)
        if oid is None:
            issue(missing_code, subject, path)
            return None
        if expected is not None and oid != expected:
            issue("SHA_DRIFT", subject, f"{path}: observed blob {oid}")
        try:
            return git.blob(oid).decode("utf-8")
        except (Unavailable, UnicodeError) as exc:
            issue("SOURCE_UNAVAILABLE", subject, f"{path}: {exc}")
            return None

    packages = manifest["packages"]
    require(isinstance(packages, list) and packages, "packages must be a nonempty list")
    identifiers = Counter(p["task_id"] for p in packages)
    pr_ids = Counter(p["pr"] for p in packages)
    for key, count in identifiers.items():
        if count > 1:
            issue("DUPLICATE_TASK_ID", key, f"{count} manifest entries")
    for key, count in pr_ids.items():
        if count > 1:
            issue("DUPLICATE_PR", key, f"{count} manifest entries")
    baseline, planning = manifest["baseline"], manifest["plan"]
    base_ok = source(baseline, "main")
    plan_ok = source(planning, f"PR#{planning['pr']}")
    catalog_ids, catalog_paths, accepted_paths = defaultdict(set), set(), set()
    checked_catalogs = set()

    def index(head, subject):
        if head in checked_catalogs:
            return
        checked_catalogs.add(head)
        catalog = read(head, SHARED[0], subject, "MISSING_CATALOG")
        if catalog is None:
            return
        rows = catalog_entries(catalog)
        for key, count in Counter(key for key, _, _ in rows).items():
            if count > 1:
                issue("DUPLICATE_CATALOG_ID", subject, key)
        for key, path, status in rows:
            catalog_ids[key].add(path)
            catalog_paths.add(path)
            if status in {"approved", "accepted", "offline_accepted", "accepted_offline"}:
                accepted_paths.add(path)
            if path not in git.inventory(head):
                issue("BROKEN_CATALOG_PATH", subject, path)
        for name in SHARED[1:]:
            text = read(head, name, subject, "REFERENCED_SOURCE_MISSING")
            if text is not None:
                for path in sorted(set(re.findall(r"\]\(((?!https?://|mailto:)[^\s)#]+)", text))):
                    if path not in git.inventory(head):
                        issue("BROKEN_INDEX_LINK", subject, f"{name}: {path}")
                if re.search(r"(?mi)^\s*production_ready:\s*true\s*$", text):
                    issue("DEPLOYMENT_CONTRADICTION", subject, f"{name} asserts production readiness in an offline audit")

    if base_ok:
        index(baseline["head"], "main")
    plan_text = None
    if plan_ok:
        require(sha(planning["blob"]), "plan needs an exact blob pin")
        plan_text = read(planning["head"], planning["path"], f"PR#{planning['pr']}",
                         "REFERENCED_SOURCE_MISSING", planning["blob"])

    candidates, known_portfolios, writers = set(), set(), defaultdict(list)
    document_id_paths = defaultdict(set)
    for package in packages:
        task = package["task_id"]
        require(IDENTIFIER.fullmatch(task) and IDENTIFIER.fullmatch(package["portfolio_id"])
                and IDENTIFIER.fullmatch(package["owner"]) and type(package["pr"]) is int and package["pr"] > 0,
                "invalid task ID, portfolio, owner or PR")
        readiness, approval = package["readiness"], package["approval"]
        require(isinstance(readiness, list) and readiness and set(readiness) <= READINESS
                and approval in {"DRAFT", "REVIEW", "OFFLINE_ACCEPTED"} and type(package["pr_draft"]) is bool
                and type(package["production_ready"]) is bool and package["scope"] in {"OFFLINE", "DESIGN"},
                f"invalid status fields: {task}")
        if package["production_ready"]:
            issue("DEPLOYMENT_CONTRADICTION", task, "offline/design scope cannot assert production readiness")
        if approval == "OFFLINE_ACCEPTED" and (package["pr_draft"] or "QA_PASS_OFFLINE" not in readiness):
            issue("DRAFT_AS_APPROVED", task, "offline acceptance requires QA evidence and a non-draft PR")
        if {"QA_PASS_OFFLINE", "QA_PENDING"} <= set(readiness):
            issue("CONFLICTING_READINESS", task, "QA cannot be both passed and pending for the same item")
        for dep in package["dependencies"]:
            if dep not in identifiers or dep == task:
                issue("INVALID_DEPENDENCY", task, dep)
        if not source(package, task):
            continue
        head = package["head"]
        index(head, f"PR#{package['pr']}")
        require(sha(package["base"]), f"invalid PR base: {task}")
        try:
            changes = git.run("diff", "--name-only", "-z", f"{package['base']}...{head}", "--", *SHARED).split(b"\0")
            for path in changes:
                if path:
                    writers[path.decode("ascii")].append(package["pr"])
        except Unavailable as exc:
            issue("SOURCE_UNAVAILABLE", task, str(exc))
        seen_ids, report_text = {}, None
        for role, (prefix, suffix) in ROLES.items():
            artifact = package[role]
            path, blob = artifact["path"], artifact["blob"]
            require(safe_path(path) and path.startswith(prefix) and path.endswith(suffix) and sha(blob),
                    f"invalid {role} reference: {task}")
            text = read(head, path, task, f"MISSING_{role.upper()}", blob)
            if text is None:
                continue
            candidates.add((task, path))
            artifacts.append({"task_id": task, "role": role, "path": path, "blob": git.inventory(head)[path]})
            fields = frontmatter(text)
            if role == "task":
                if fields.get("id") != task or fields.get("owner") != package["owner"]:
                    issue("TASK_IDENTITY_DRIFT", task, path)
                else:
                    known_portfolios.add(package["portfolio_id"])
            if role == "report":
                report_text = text
            if approval == "OFFLINE_ACCEPTED" and "draft" in fields.get("status", "").lower():
                issue("DRAFT_AS_APPROVED", task, path)
            doc_id = fields.get("id")
            if doc_id and doc_id in seen_ids:
                issue("DOCUMENT_ID_REUSED", task, f"{seen_ids[doc_id]}, {path}", "finding")
            if doc_id:
                seen_ids[doc_id] = path
                document_id_paths[doc_id].add(path)
            if role == "evidence":
                json.loads(text, object_pairs_hook=unique_keys)
                if not isinstance(package["verdict"], str) or not re.search(
                    rf"(?<![A-Za-z0-9_]){re.escape(package['verdict'])}(?![A-Za-z0-9_])", (report_text or "") + "\n" + text
                ):
                    issue("VERDICT_NOT_SOURCED", task, package["verdict"])

    for doc_id, paths in sorted(document_id_paths.items()):
        if len(paths) > 1:
            issue("DUPLICATE_DOCUMENT_ID", doc_id, ", ".join(sorted(paths)), "finding")
    for key, paths in sorted(catalog_ids.items()):
        if len(paths) > 1:
            issue("DUPLICATE_CATALOG_ID", key, ", ".join(sorted(paths)))
    for task, path in sorted(candidates):
        if path not in catalog_paths:
            issue("NOT_INDEXED", task, path, "finding")
    for package in packages:
        if package["approval"] == "DRAFT" and package["task"]["path"] in accepted_paths:
            issue("DRAFT_AS_APPROVED", package["task_id"], "CATALOG treats a draft task as accepted")
    for path, prs in sorted(writers.items()):
        if len(prs) > 1:
            issue("SHARED_FILE_OVERLAP", path, f"PRs {', '.join(map(str, sorted(prs)))}", "finding")
    if plan_text is not None:
        for portfolio, line in re.findall(r"(?m)^\|\s*([\w-]+)\s*\|([^\n]*)$", plan_text):
            if portfolio in known_portfolios and re.search(r"\bNO_TASK_YET\b", line):
                issue("STALE_NO_TASK_YET", portfolio, planning["path"], "finding")
    return {"source_count": len(sources), "artifact_count": len(artifacts), "sources": sources, "artifacts": artifacts,
            "shared_writers": dict(sorted(writers.items())), "issues": issues}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--evidence", type=Path)
    args = parser.parse_args()
    try:
        result = validate(json.loads(args.manifest.read_text(encoding="utf-8"), object_pairs_hook=unique_keys),
                          Git(args.repo))
    except (ValueError, TypeError, KeyError, OSError) as exc:
        print(f"INVALID_INPUT: {exc}", file=sys.stderr)
        return 2
    output = json.dumps(result, indent=2) + "\n"
    if args.evidence:
        with args.evidence.open("x", encoding="utf-8") as stream:
            stream.write(output)
    else:
        print(output, end="")
    return 2 if any(row["severity"] == "error" for row in result["issues"]) else 1 if result["issues"] else 0


if __name__ == "__main__":
    sys.exit(main())
