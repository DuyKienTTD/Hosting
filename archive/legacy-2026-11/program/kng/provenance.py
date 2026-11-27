"""KNG pinned Git object verifier. A missing Git graph is BLOCKED, not PASS."""
import re
import subprocess
from pathlib import Path

SHA = re.compile(r'^[0-9a-f]{40}$')

class GitObjects:
    def __init__(self, root):
        self.root = Path(root)

    def run(self, *args):
        try:
            proc = subprocess.run(['git', '-C', str(self.root), *args], capture_output=True, text=True, timeout=10, check=False)
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise LookupError(str(exc)) from exc
        if proc.returncode:
            raise LookupError((proc.stderr or proc.stdout).strip()[:240])
        return proc.stdout.strip()

    def verify(self, commit, path, expected):
        if not SHA.fullmatch(commit) or not SHA.fullmatch(expected):
            raise ValueError('invalid pinned git hash')
        if not path or path.startswith('/') or '..' in Path(path).parts:
            raise ValueError('unsafe source path')
        actual_commit = self.run('rev-parse', '--verify', commit + '^{commit}')
        if actual_commit != commit:
            raise ValueError('commit differs from pin')
        actual_blob = self.run('rev-parse', '--verify', commit + ':' + path)
        blob_type = self.run('cat-file', '-t', actual_blob)
        if blob_type != 'blob':
            raise ValueError('source object is not blob')
        if actual_blob != expected:
            raise ValueError(f'source blob mismatch: {path} {actual_blob} != {expected}')
        return True
