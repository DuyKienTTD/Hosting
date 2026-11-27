#!/usr/bin/env python3
"""Owner-only, no-echo OpenAI key setup for the GATE B sandbox guard.

This program opens no network listener and never calls an OpenAI endpoint.  It
validates the sandbox Compose overlay read-only and stores the credential in a
root-only file.  It never starts, stops, or recreates a container.
"""

from __future__ import annotations

import argparse
import contextlib
import getpass
import json
import os
from pathlib import Path
import re
import secrets
import signal
import stat
import subprocess
import sys
import tempfile
from typing import Callable, Iterator

try:
    import fcntl
except ImportError:  # pragma: no cover - tests may import this module on Windows
    fcntl = None


PROJECT_LABEL = "TTD METAL / GATE B / owner-selected OpenAI project"
PROJECT_DIR = Path("/root/ttd-hermes-gate-a")
SECRET_PATH = PROJECT_DIR / "secrets" / "openai-provider-api-key"
SECRET_TARGET = "/run/secrets/openai_provider_api_key"
BASE_COMPOSE = PROJECT_DIR / "compose.yaml"
OVERLAY_COMPOSE = PROJECT_DIR / "compose.h4-provider-secret.yaml"
LOCK_PATH = Path("/run/lock/ttd-h4-owner-key-input.lock")
GUARD_CONTAINER = "ttd-gate-a-guard"
KEY_PATTERN = re.compile(r"\Ask-[!-~]{17,509}\Z")


class Cancelled(RuntimeError):
    """The owner cancelled before a secret was changed."""


class SessionExpired(RuntimeError):
    """The no-echo input window expired before a secret was changed."""


def validate_key(value: str) -> bytearray:
    if not KEY_PATTERN.fullmatch(value):
        raise ValueError("Key must start with sk-, contain no whitespace, and be 20-512 ASCII characters.")
    return bytearray(value.encode("ascii"))


def _assert_safe_parent(parent: Path) -> None:
    parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    info = parent.lstat()
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
        raise RuntimeError("Secret directory is not a regular directory.")
    os.chmod(parent, 0o700)
    if os.name == "posix" and info.st_uid != 0:
        raise RuntimeError("Secret directory is not owned by root.")


def secret_status(path: Path) -> dict[str, object]:
    if not path.exists():
        return {"present": False}
    info = path.lstat()
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode):
        raise RuntimeError("Secret target is not a regular file.")
    return {
        "present": True,
        "mode": stat.S_IMODE(info.st_mode),
        "owner_uid": info.st_uid if os.name == "posix" else None,
    }


def write_secret_atomic(path: Path, key: bytearray) -> None:
    _assert_safe_parent(path.parent)
    existing = secret_status(path)
    if os.name == "posix" and existing.get("present") and existing.get("mode") != 0o600:
        raise RuntimeError("Existing secret has an unsafe mode; refusing replacement.")
    fd, temp_name = tempfile.mkstemp(prefix=".openai-key-", dir=path.parent)
    temp_path = Path(temp_name)
    try:
        if hasattr(os, "fchmod"):
            os.fchmod(fd, 0o600)
        else:  # Windows-only unit-test path; the VPS path is POSIX.
            os.chmod(temp_path, 0o600)
        with os.fdopen(fd, "wb", closefd=True) as handle:
            fd = -1
            handle.write(key)
            handle.write(b"\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_path, path)
        os.chmod(path, 0o600)
        if os.name == "posix":
            directory_fd = os.open(path.parent, os.O_RDONLY)
            try:
                os.fsync(directory_fd)
            finally:
                os.close(directory_fd)
    finally:
        if fd >= 0:
            os.close(fd)
        if temp_path.exists():
            temp_path.unlink()


def _compose_config_command() -> list[str]:
    return [
        "docker",
        "compose",
        "-f",
        str(BASE_COMPOSE),
        "-f",
        str(OVERLAY_COMPOSE),
        "config",
        "--quiet",
    ]


def _run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=PROJECT_DIR,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env={key: value for key, value in os.environ.items() if key != "OPENAI_API_KEY"},
    )


def _inspect_all_secret_mounts() -> list[tuple[str, bool]]:
    ids = _run(["docker", "ps", "-aq"]).stdout.split()
    found: list[tuple[str, bool]] = []
    for container_id in ids:
        raw = _run(["docker", "inspect", container_id]).stdout
        inspected = json.loads(raw)[0]
        name = str(inspected.get("Name", "")).lstrip("/")
        for mount in inspected.get("Mounts", []):
            if mount.get("Destination") == SECRET_TARGET:
                found.append((name, bool(mount.get("RW"))))
    return found


def validate_compose_read_only() -> None:
    if not BASE_COMPOSE.is_file() or not OVERLAY_COMPOSE.is_file():
        raise RuntimeError("Compose base or H4 overlay is unavailable.")
    _run(_compose_config_command())


@contextlib.contextmanager
def session_deadline(seconds: int) -> Iterator[None]:
    if seconds <= 0:
        raise SessionExpired("Input session expired.")
    if os.name != "posix":
        yield
        return

    def expired(_signum: int, _frame: object) -> None:
        raise SessionExpired("Input session expired.")

    old_handler = signal.signal(signal.SIGALRM, expired)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old_handler)


@contextlib.contextmanager
def exclusive_lock(path: Path = LOCK_PATH) -> Iterator[None]:
    if fcntl is None:
        yield
        return
    fd = os.open(path, os.O_CREAT | os.O_RDWR, 0o600)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        yield
    finally:
        fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)


def interactive_install(
    action: str,
    *,
    path: Path = SECRET_PATH,
    timeout_seconds: int = 300,
    input_fn: Callable[[str], str] = input,
    getpass_fn: Callable[[str], str] = getpass.getpass,
    validate_fn: Callable[[], None] = validate_compose_read_only,
) -> None:
    current = secret_status(path)
    if action == "install" and current.get("present"):
        raise RuntimeError("A secret already exists; use rotate or revoke.")
    if action == "rotate" and not current.get("present"):
        raise RuntimeError("No existing secret is present; use install.")

    print("OpenAI provider credential setup — GATE B sandbox")
    print(f"Project: {PROJECT_LABEL}")
    print("Destination: root-only staging file for a future guard-only mount")
    print("This interface opens no listener, performs no provider request, and changes no container.")

    validate_fn()

    key = bytearray()
    repeated = bytearray()
    with session_deadline(timeout_seconds):
        if input_fn("Type PROJECT to confirm the selected project in your OpenAI dashboard: ") != "PROJECT":
            raise Cancelled("Project confirmation cancelled.")
        key = validate_key(getpass_fn("OpenAI API key (hidden): "))
        repeated = validate_key(getpass_fn("Repeat API key (hidden): "))
        if not secrets.compare_digest(key, repeated):
            raise ValueError("The two hidden values do not match.")
        expected = action.upper()
        if input_fn(f"Type {expected} to store the key, or anything else to cancel: ") != expected:
            raise Cancelled("Final confirmation cancelled.")

    try:
        write_secret_atomic(path, key)
    finally:
        for buffer in (key, repeated):
            for index in range(len(buffer)):
                buffer[index] = 0

    verified = secret_status(path)
    if os.name == "posix" and verified.get("mode") != 0o600:
        raise RuntimeError("Secret mode verification failed.")
    print("STORED_NOT_MOUNTED: secret stored root-only; no container was changed.")
    print("A separately approved guard recreate is required before the secret can be mounted.")
    print("No OpenAI request, paid inference, permit, ledger change, or public listener was created.")


def interactive_revoke(
    *,
    path: Path = SECRET_PATH,
    input_fn: Callable[[str], str] = input,
    mounted_fn: Callable[[], list[tuple[str, bool]]] = _inspect_all_secret_mounts,
) -> None:
    if not secret_status(path).get("present"):
        print("ABSENT: no provider secret is stored.")
        return
    if input_fn("Type REVOKE to delete the unmounted stored provider key: ") != "REVOKE":
        raise Cancelled("Revocation cancelled.")
    if mounted_fn():
        raise RuntimeError("Secret is mounted; obtain separate approval to recreate the guard before deletion.")
    path.unlink()
    print("REVOKED: unmounted provider key removed; no container or ledger was touched.")


def print_status(path: Path = SECRET_PATH) -> None:
    current = secret_status(path)
    if not current.get("present"):
        print("ABSENT: no provider secret is stored.")
        return
    mounted = _inspect_all_secret_mounts()
    safe_mount = mounted == [(GUARD_CONTAINER, False)]
    print(
        "PRESENT: mode=0600, "
        f"mounted={str(bool(mounted)).lower()}, "
        f"guard_only_read_only={str(safe_mount).lower()}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("install", "rotate", "revoke", "status"))
    parser.add_argument("--timeout-seconds", type=int, default=300)
    args = parser.parse_args()
    if os.name != "posix" or os.geteuid() != 0:
        raise SystemExit("Run only as root in the authenticated VPS terminal.")
    with exclusive_lock():
        try:
            if args.action in ("install", "rotate"):
                interactive_install(args.action, timeout_seconds=args.timeout_seconds)
            elif args.action == "revoke":
                interactive_revoke()
            else:
                print_status()
        except (Cancelled, SessionExpired, ValueError, RuntimeError, subprocess.CalledProcessError) as error:
            print(f"STOPPED: {error}", file=sys.stderr)
            return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
