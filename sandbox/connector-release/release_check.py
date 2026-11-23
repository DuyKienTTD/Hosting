"""Check and assemble the reviewed sandbox-only release without any network."""

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[2]
MANIFEST_FILE = Path(__file__).with_name("manifest.json")
MAIN = "refs/remotes/origin/main"
PACKAGES = (
    ("s1", 10, "eng-01a-s1-offline-contract-2026-11-23", "sandbox/connector-contracts"),
    ("s2", 13, "eng-01a-s2-fake-channel-adapters-2026-11-23", "sandbox/connector-channel-mocks"),
    ("s3", 19, "eng-01a-s3-offline-integration-2026-11-23", "sandbox/connector-integration"),
)
POLICY = {"LIVE_ENABLED": False, "MOCK_ONLY": True, "backend": "BACKEND_PRODUCTION_NOT_READY",
          "connector": "REAL_CONNECTOR_UNTESTED", "allow_external_network": False, "allow_live_endpoint": False,
          "allow_credentials": False, "allow_production_hostname": False, "allow_account_id": False,
          "allow_real_data": False, "allow_paid": False, "allow_external_side_effect": False}
TEST_COMMAND = "PYTHONDONTWRITEBYTECODE=1 python3 -X utf8 -B sandbox/connector-integration/test_integration.py"


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("ascii")


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def git(*args, codes=(0,)):
    env = os.environ | {"GIT_NO_LAZY_FETCH": "1", "GIT_ALLOW_PROTOCOL": ""}
    result = subprocess.run(["git", *args], cwd=ROOT, env=env, capture_output=True)
    require(result.returncode in codes, f"local Git check failed: {args[0]}")
    return result


def ref(name):
    return git("rev-parse", "--verify", name + "^{commit}").stdout.decode("ascii").strip()


def checked_path(path, prefix):
    require(isinstance(path, str) and re.fullmatch(r"[a-zA-Z0-9._/-]+", path), "invalid artifact path")
    parts = PurePosixPath(path).parts
    require(path == "/".join(parts) and ".." not in parts and path.startswith(prefix + "/"),
            "artifact path outside declared sandbox package")


def inventory(commit, prefix):
    entries = {}
    for entry in git("ls-tree", "-r", "-z", commit, "--", prefix).stdout.split(b"\0"):
        if not entry:
            continue
        header, name = entry.decode("ascii").split("\t")
        mode, kind, blob = header.split()
        checked_path(name, prefix)
        require((mode, kind) == ("100644", "blob") and name not in entries, "nonregular or duplicate source file")
        entries[name] = blob
    require(entries, "empty package at pinned commit")
    return entries


def ref_pins():
    return {MAIN: ref(MAIN), **{f"refs/remotes/origin/codex/{branch}": ref(f"refs/remotes/origin/codex/{branch}")
                              for _, _, branch, _ in PACKAGES}}


def capture():
    """Read the local remote-tracking snapshot. Pin changes require a new review."""
    before = ref_pins()
    base = before[MAIN]
    base_tree = git("rev-parse", f"{base}^{{tree}}").stdout.decode("ascii").strip()
    packages, payloads = [], {}
    for name, pr, branch, prefix in PACKAGES:
        reference = "refs/remotes/origin/codex/" + branch
        head = before[reference]
        files = []
        for path, blob in sorted(inventory(head, prefix).items()):
            raw = git("cat-file", "blob", blob).stdout
            require(hashlib.sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest() == blob, "Git object hash mismatch")
            require(path.casefold() not in {item.casefold() for item in payloads}, "ambiguous artifact path")
            payloads[path] = raw
            files.append({"path": path, "git_blob_sha1": blob, "content_sha256": sha(raw)})
        packages.append({"name": name, "pr": pr, "ref": reference, "head": head, "prefix": prefix, "files": files})
    require(ref_pins() == before, "tracked heads moved during manifest capture")
    result = {"manifest_version": 1, "contract_versions": {"s1": 1, "s2": 1, "s3": 1},
              "baseline": {"ref": MAIN, "commit": base, "tree": base_tree},
              "packages": packages, "policy": POLICY.copy(), "offline_s3_delta_command": TEST_COMMAND}
    return result, payloads


def unique_keys(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate manifest key")
        result[key] = value
    return result


def read_manifest(path=MANIFEST_FILE):
    return json.loads(path.read_bytes(), object_pairs_hook=unique_keys)


def verify(manifest):
    actual, payloads = capture()
    require(canonical(manifest) == canonical(actual), "release manifest does not match the pinned local Git snapshot")
    return payloads


def exact_refs(manifest):
    base = manifest["baseline"]
    return {base["ref"]: base["commit"], **{item["ref"]: item["head"] for item in manifest["packages"]}}


def check_assembly(manifest, root):
    expected = {row["path"]: row["content_sha256"] for package in manifest["packages"] for row in package["files"]}
    directories = {parent.as_posix() for name in expected for parent in PurePosixPath(name).parents if parent.parts}
    require(root.is_dir() and not root.is_symlink(), "assembly root is not a regular directory")
    found = {}
    for entry in root.rglob("*"):
        name = entry.relative_to(root).as_posix()
        require(not entry.is_symlink(), "assembly contains a symlink")
        if entry.is_dir():
            require(name in directories, "undeclared assembly directory")
        else:
            require(entry.is_file() and name in expected, "undeclared assembly file")
            found[name] = sha(entry.read_bytes())
    require(found == expected, "assembly content hash, path or completeness mismatch")
    return sha(canonical(found))


def assemble(manifest, root):
    payloads = verify(manifest)
    require(ref_pins() == exact_refs(manifest), "tracked heads moved before assembly")
    # mkdir and exclusive file creation refuse an existing destination.
    root.mkdir(exist_ok=False)
    for name, raw in sorted(payloads.items()):
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("xb") as stream:
            stream.write(raw)
    bundle = check_assembly(manifest, root)
    require(ref_pins() == exact_refs(manifest), "tracked heads moved during assembly")
    return bundle


def check():
    manifest = read_manifest()
    with tempfile.TemporaryDirectory(prefix="eng01a-s4-release-") as directory:
        root = Path(directory)
        first = assemble(manifest, root / "first")
        second = assemble(manifest, root / "second")
        require(first == second, "bundle changed across independent assembly roots")
    return {"manifest_sha256": sha(canonical(manifest)), "bundle_sha256": first, "assemblies_equal": True,
            "files_verified": sum(len(package["files"]) for package in manifest["packages"]),
            "temporary_assemblies_removed": True}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()
    observed = check()
    with args.evidence.open("x", encoding="utf-8") as stream:
        json.dump(observed, stream, indent=2)
        stream.write("\n")
    print("RELEASE_ASSEMBLY_VERIFIED", observed["bundle_sha256"])
