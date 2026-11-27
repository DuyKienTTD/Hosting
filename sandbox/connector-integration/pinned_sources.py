"""Load three immutable synthetic artifacts from Git objects already fetched."""

import hashlib
import importlib.util
import os
from pathlib import Path
import subprocess


MAIN = "e385c1bea2070973e3007e5717f7e980348d6ab3"
S1 = "79dfe8aae5c30d4e896c29333e0296ada1671b7e"
S2 = "0235b5f9bb38d0d7e99a600188705d50977527f5"
ROOT = Path(__file__).resolve().parents[2]
PINNED = {
    "offline_connector.py": (S1, "sandbox/connector-contracts/offline_connector.py",
                             "2bbfb4ef308e39ea1b548f22553c673d3a684a97"),
    "channel_mocks.py": (S2, "sandbox/connector-channel-mocks/channel_mocks.py",
                         "bfda39bf3ac07aba09009462bb60620970a31951"),
    "fixtures.json": (S2, "sandbox/connector-channel-mocks/fixtures.json",
                      "ec30d2dd9d2fb9a0dbd0b6179d0a424321fdd166"),
}


def check_blob(name, raw):
    actual = hashlib.sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest()
    if actual != PINNED[name][2]:
        raise RuntimeError(f"pinned source drift: {name}")


def stage(workspace):
    env = os.environ | {"GIT_NO_LAZY_FETCH": "1", "GIT_ALLOW_PROTOCOL": ""}
    for name, (commit, path, _) in PINNED.items():
        raw = subprocess.check_output(["git", "show", f"{commit}:{path}"], cwd=ROOT, env=env)
        check_blob(name, raw)
        with (workspace / name).open("xb") as staged:
            staged.write(raw)


def load(workspace):
    for name in PINNED:
        check_blob(name, (workspace / name).read_bytes())
    modules = []
    for name in ("offline_connector.py", "channel_mocks.py"):
        spec = importlib.util.spec_from_file_location("s3_pinned_" + name[:-3], workspace / name)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        if module.LIVE_ENABLED is not False:
            raise RuntimeError("pinned module is not offline")
        modules.append(module)
    return tuple(modules)
