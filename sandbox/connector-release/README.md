# ENG-01A offline release checker

`manifest.json` lists the exact Git blobs and SHA-256 digests of the three sandbox packages. `release_check.py` verifies the recorded main tree and package refs, assembles from local Git objects in two temporary directories and compares the bundle digests. The checker rejects moved refs, nonregular or ambiguous files, mismatched digests and existing destinations. Fetching is a separate step. If an upstream ref moves, an updated manifest requires review.

`readiness_preview.py` previews the three PRs against that local snapshot without changing refs, the index or the checkout. It also reads the fetched plan PR branch. Review the Git conflicts and index findings separately.

## Linux verification

Use an existing authorized, isolated local Linux machine with no connector credentials, outbound network disabled and Python 3.12 or later with SQLite support. Transfer an offline local Git copy with the S4 checkout, all package objects and the remote-tracking refs in the manifest. Check the remote heads before transfer. Run these commands from the S4 checkout using a regular account.

```sh
set -eu
umask 077
export PYTHONDONTWRITEBYTECODE=1 GIT_NO_LAZY_FETCH=1 GIT_ALLOW_PROTOCOL=
s4_checkout=$(pwd -P)
run_dir=$(mktemp -d "${TMPDIR:-/tmp}/eng01a-s4-linux.XXXXXX")
mkdir -m 700 "$run_dir/fixtures"
export TMPDIR="$run_dir/fixtures"
uname -srm > "$run_dir/platform.txt"
python3 -c 'import platform, sqlite3; print(platform.python_version(), sqlite3.sqlite_version)' >> "$run_dir/platform.txt"
python3 -X utf8 -B sandbox/connector-release/release_check.py --evidence "$run_dir/assembly.json"
python3 -X utf8 -B sandbox/connector-release/test_release_check.py --evidence "$run_dir/s4-delta.json"
s3=$(python3 -c 'import json; print(next(p["head"] for p in json.load(open("sandbox/connector-release/manifest.json", encoding="utf-8"))["packages"] if p["name"] == "s3"))')
git worktree add --detach "$run_dir/checkout" "$s3"
(
  cd "$run_dir/checkout"
  test "$(git rev-parse HEAD)" = "$s3"
  python3 -X utf8 -B sandbox/connector-integration/test_integration.py --evidence "$run_dir/s3-linux.json"
)
git -C "$s4_checkout" worktree remove "$run_dir/checkout"
test -z "$(ls -A "$run_dir/fixtures")"
printf 'Evidence directory: %s\n' "$run_dir"
```

Verify that the pinned S3 suite and the S4 delta pass. Check exit status 86 at the deliberate process crash points, rollback of the outbox and result association before commit, and replay of the same receipt after commit. An unbound delayed result must remain hidden and a settled 504 must retain its bound result. Verify exact source pins, no extra synthetic read or dispatch and no external side effect. Check that SQLite files were created under the private fixture directory and cleanup left it empty. Retain only redacted evidence and platform versions. If a command fails, record it and remove the owned worktree after the worker exits and the checkout is verified clean.
