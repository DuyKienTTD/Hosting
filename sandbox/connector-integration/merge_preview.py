"""Inspect a local merge tree without creating a merge commit or moving refs."""

import argparse
import json
import os
from pathlib import Path
import subprocess
import tempfile

from pinned_sources import MAIN, ROOT, S1, S2


METADATA = ("CATALOG.yaml", "STATE.md", "CHANGELOG.md")


def git(*args, cwd=ROOT, codes=(0,)):
    env = os.environ | {"GIT_NO_LAZY_FETCH": "1", "GIT_ALLOW_PROTOCOL": ""}
    proc = subprocess.run(["git", *args], cwd=cwd, env=env, capture_output=True, encoding="utf-8", errors="strict")
    if proc.returncode not in codes:
        raise RuntimeError(f"Git preview failed with exit {proc.returncode}: {proc.stderr.strip()}")
    return proc


def preview():
    if git("merge-base", S1, S2).stdout.strip() != MAIN:
        raise RuntimeError("unexpected merge base")
    refs = git("for-each-ref", "--format=%(refname) %(objectname)", "refs/heads", "refs/remotes/origin").stdout
    with tempfile.TemporaryDirectory(prefix="eng01a-s3-merge-") as directory:
        root = Path(directory)
        worktree = root / "preview"
        git("-c", f"core.hooksPath={root / 'no-hooks'}", "worktree", "add", "--detach", str(worktree), S1)
        try:
            result = git("merge-tree", "--write-tree", "--name-only", S1, S2, cwd=worktree, codes=(0, 1))
            tree, *rest = result.stdout.splitlines()
            conflicts = [line for line in rest if line and not line.startswith(("Auto-merging ", "CONFLICT "))]
            metadata_diff = None
            if result.returncode == 0:
                metadata_diff = git("diff", "--no-ext-diff", MAIN, tree, "--", *METADATA, cwd=worktree).stdout
                for path in METADATA:
                    content = git("show", f"{tree}:{path}", cwd=worktree).stdout
                    if not all(f"eng-01a-{stage}" in content or f"ENG-01A-{stage.upper()}" in content
                               for stage in ("s1", "s2")):
                        raise RuntimeError(f"{path}: combined metadata is incomplete")
            intact = git("diff", "--name-only", S1, tree, "--", "sandbox/connector-contracts", cwd=worktree).stdout == ""
            intact &= git("diff", "--name-only", S2, tree, "--", "sandbox/connector-channel-mocks", cwd=worktree).stdout == ""
            if git("status", "--porcelain", cwd=worktree).stdout:
                raise RuntimeError("merge preview checkout is dirty")
        finally:
            git("worktree", "remove", str(worktree))
    if refs != git("for-each-ref", "--format=%(refname) %(objectname)", "refs/heads", "refs/remotes/origin").stdout:
        raise RuntimeError("refs changed during merge preview")
    if result.returncode == 0 and (conflicts or not intact):
        raise RuntimeError("merge preview did not preserve both packages")
    return {"merge_base": MAIN, "s1": S1, "s2": S2, "merged_tree": tree,
            "status": "CLEAN_PREVIEW" if result.returncode == 0 else "CONFLICTS_FOUND",
            "conflict_paths": conflicts,
            "metadata_conflict_matrix": {path: path in conflicts for path in METADATA},
            "functional_packages_unchanged": intact, "refs_unchanged": True,
            "detached_checkout_removed": True, "proposed_metadata_diff": metadata_diff}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()
    result = preview()
    args.evidence.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(result["status"], result["merged_tree"], result["conflict_paths"])
