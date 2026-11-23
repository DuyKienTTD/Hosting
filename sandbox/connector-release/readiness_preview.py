"""Three-way previews of the verified current heads, without commits or ref updates."""

import argparse
from collections import Counter
import json
from pathlib import Path
import re

import release_check as release


METADATA = ("CATALOG.yaml", "STATE.md", "CHANGELOG.md")
PLAN = "refs/remotes/origin/planning/multi-agent-capability-allocation-2026-11-23"
PLAN_PATH = "tasks/2026-11-23-multi-agent-master-allocation-review.md"


def text(*args):
    return release.git(*args).stdout.decode("utf-8")


def paths(tree):
    return set(text("ls-tree", "-r", "-z", "--name-only", tree).strip("\0").split("\0"))


def indexes(tree):
    catalog = text("show", f"{tree}:CATALOG.yaml")
    entries = re.findall(r"^  - id: (\S+)\n    path: (\S+)\n    type: \S+\n    status: (\S+)$", catalog, re.M)
    release.require(len(entries) == len(re.findall(r"^  - id: ", catalog, re.M)), "unrecognized catalog entry")
    links = {path for _, path, _ in entries}
    for index in ("STATE.md", "CHANGELOG.md"):
        links.update(match for match in re.findall(r"\]\(([^)#\s]+)", text("show", f"{tree}:{index}"))
                     if not match.startswith(("http://", "https://", "#", "mailto:")))
    return entries, links


def semantics(base, tree, plan):
    entries, links = indexes(tree)
    _, baseline_links = indexes(base)
    base_missing = baseline_links - paths(base)
    merged_paths = paths(tree)
    missing = links - merged_paths
    task_status = {path: state for _, path, state in entries if path.startswith("tasks/") and "eng-01a-" in path}
    expected = {path for path in merged_paths if "eng-01a-s3-" in path and path.startswith(("tasks/", "reports/"))}
    unindexed = sorted(expected - {path for _, path, _ in entries})
    duplicates = sorted(key for key, count in Counter(key for key, _, _ in entries).items() if count > 1)
    document = text("show", f"{plan}:{PLAN_PATH}")
    plan_rows = [line for line in document.splitlines() if line.startswith("| ENG-01A |")]
    return {
        "duplicate_catalog_ids": duplicates,
        "new_missing_relative_index_links": sorted(missing - base_missing),
        "preexisting_missing_relative_index_links": sorted(missing & base_missing),
        "offline_task_catalog_status": task_status,
        "s3_existing_paths_not_yet_indexed": unindexed,
        "plan_eng01a_stale_no_task_yet": any("NO_TASK_YET" in line for line in plan_rows),
        "plan_eng01a_mentions_s3": any("PR #19" in line or "S3" in line for line in plan_rows),
    }


def preview(manifest):
    release.verify(manifest)
    expected = release.exact_refs(manifest)
    plan = release.ref(PLAN)
    base = manifest["baseline"]["commit"]
    previous = base
    steps = []
    for package in manifest["packages"]:
        head = package["head"]
        anchor = text("merge-base", base, head).strip()
        merged = release.git("merge-tree", "--write-tree", "--name-only", f"--merge-base={anchor}",
                             previous, head, codes=(0, 1))
        tree, *lines = merged.stdout.decode("utf-8").splitlines()
        # With --name-only, conflicting names precede the first blank line.
        conflicts = []
        if merged.returncode:
            for line in lines:
                if not line:
                    break
                conflicts.append(line)
            release.require(conflicts, "merge reported conflict without named paths")
        steps.append({"pr": package["pr"], "head": head, "merge_base": anchor,
                      "input_tree_or_commit": previous, "preview_tree": tree,
                      "functional_conflicts": [path for path in conflicts if path.startswith("sandbox/")],
                      "shared_metadata_conflicts": [path for path in conflicts if path in METADATA],
                      "other_conflicts": [path for path in conflicts
                                          if path not in METADATA and not path.startswith("sandbox/")]})
        previous = tree
        if conflicts:
            break
    result = {"base": base, "plan_pr6_head": plan, "steps": steps}
    if len(steps) == len(manifest["packages"]) and not conflicts:
        for package in manifest["packages"]:
            expected_files = {row["path"]: row["git_blob_sha1"] for row in package["files"]}
            release.require(release.inventory(previous, package["prefix"]) == expected_files,
                            "preview altered a pinned functional package")
        result |= {"status": "CLEAN_TEXT_PREVIEW", "combined_tree": previous, "functional_blobs_unchanged": True,
                   "index_semantics": semantics(base, previous, plan)}
    else:
        result["status"] = "CONFLICTS_FOUND"
    release.require(release.ref_pins() == expected and release.ref(PLAN) == plan, "tracked heads moved during preview")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()
    observed = preview(release.read_manifest())
    with args.evidence.open("x", encoding="utf-8") as stream:
        json.dump(observed, stream, indent=2)
        stream.write("\n")
    print(observed["status"])
