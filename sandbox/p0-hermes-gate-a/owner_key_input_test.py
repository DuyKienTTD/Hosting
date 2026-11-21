#!/usr/bin/env python3
"""Fake-key tests for the owner-only H4 terminal interface."""

from __future__ import annotations

import contextlib
import io
import os
from pathlib import Path
import secrets
import stat
import tempfile
import unittest

import owner_key_input as subject


def fake_key() -> str:
    return "sk-" + secrets.token_urlsafe(36)


class OwnerKeyInputTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "secrets"
        self.path = self.root / "openai-provider-api-key"

    def tearDown(self) -> None:
        self.temp.cleanup()

    def install(self, key: str, *, action: str = "install", confirm: str | None = None) -> str:
        answers = iter(("PROJECT", confirm or action.upper()))
        hidden = iter((key, key))
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            subject.interactive_install(
                action,
                path=self.path,
                input_fn=lambda _prompt: next(answers),
                getpass_fn=lambda _prompt: next(hidden),
                validate_fn=lambda: None,
            )
        return output.getvalue()

    def test_fake_key_install_is_hidden_and_root_style_mode(self) -> None:
        key = fake_key()
        output = self.install(key)
        self.assertNotIn(key, output)
        self.assertEqual(self.path.read_text(encoding="ascii").strip(), key)
        if os.name == "posix":
            self.assertEqual(stat.S_IMODE(self.path.stat().st_mode), 0o600)
            self.assertEqual(stat.S_IMODE(self.root.stat().st_mode), 0o700)

    def test_invalid_key_never_creates_secret(self) -> None:
        answers = iter(("PROJECT", "INSTALL"))
        hidden = iter(("not-a-key", "not-a-key"))
        with self.assertRaises(ValueError):
            subject.interactive_install(
                "install",
                path=self.path,
                input_fn=lambda _prompt: next(answers),
                getpass_fn=lambda _prompt: next(hidden),
                validate_fn=lambda: None,
            )
        self.assertFalse(self.path.exists())

    def test_cancel_never_creates_secret(self) -> None:
        with self.assertRaises(subject.Cancelled):
            subject.interactive_install(
                "install",
                path=self.path,
                input_fn=lambda _prompt: "CANCEL",
                getpass_fn=lambda _prompt: self.fail("hidden input should not run"),
                validate_fn=lambda: None,
            )
        self.assertFalse(self.path.exists())

    def test_session_expiry_never_creates_secret(self) -> None:
        with self.assertRaises(subject.SessionExpired):
            subject.interactive_install(
                "install",
                path=self.path,
                timeout_seconds=0,
                input_fn=lambda _prompt: self.fail("input should not run"),
                getpass_fn=lambda _prompt: self.fail("hidden input should not run"),
                validate_fn=lambda: None,
            )
        self.assertFalse(self.path.exists())

    def test_rotate_replaces_without_echo(self) -> None:
        first = fake_key()
        second = fake_key()
        self.install(first)
        output = self.install(second, action="rotate")
        self.assertNotIn(second, output)
        self.assertEqual(self.path.read_text(encoding="ascii").strip(), second)

    def test_revoke_requires_exact_confirmation(self) -> None:
        self.install(fake_key())
        with self.assertRaises(subject.Cancelled):
            subject.interactive_revoke(path=self.path, input_fn=lambda _prompt: "NO", mounted_fn=lambda: [])
        self.assertTrue(self.path.exists())
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            subject.interactive_revoke(
                path=self.path,
                input_fn=lambda _prompt: "REVOKE",
                mounted_fn=lambda: [],
            )
        self.assertFalse(self.path.exists())

    def test_revoke_refuses_while_mounted(self) -> None:
        self.install(fake_key())
        with self.assertRaises(RuntimeError):
            subject.interactive_revoke(
                path=self.path,
                input_fn=lambda _prompt: "REVOKE",
                mounted_fn=lambda: [(subject.GUARD_CONTAINER, False)],
            )
        self.assertTrue(self.path.exists())

    def test_symlink_target_is_rejected(self) -> None:
        self.root.mkdir(mode=0o700)
        real = Path(self.temp.name) / "real"
        real.write_text("placeholder", encoding="ascii")
        try:
            self.path.symlink_to(real)
        except (OSError, NotImplementedError):
            self.skipTest("symlink creation is unavailable")
        with self.assertRaises(RuntimeError):
            subject.write_secret_atomic(self.path, bytearray(fake_key().encode("ascii")))

    def test_overlay_is_guard_only_and_has_no_ports(self) -> None:
        overlay = Path(__file__).with_name("compose.h4-provider-secret.yaml").read_text(encoding="utf-8")
        self.assertIn("  guard:\n", overlay)
        self.assertNotIn("  bridge:\n", overlay)
        self.assertNotIn("  hermes-aux:\n", overlay)
        self.assertNotIn("  provider-mock:\n", overlay)
        self.assertNotIn("ports:", overlay)
        self.assertIn(subject.SECRET_TARGET, overlay)

    def test_source_contains_no_network_listener(self) -> None:
        source = Path(subject.__file__).read_text(encoding="utf-8")
        self.assertNotIn("HTTPServer", source)
        self.assertNotIn("socket.listen", source)
        self.assertNotIn("localStorage", source)

    def test_source_contains_no_compose_mutation(self) -> None:
        source = Path(subject.__file__).read_text(encoding="utf-8")
        self.assertNotIn('"up"', source)
        self.assertNotIn('"down"', source)
        self.assertNotIn("--force-recreate", source)


if __name__ == "__main__":
    unittest.main(verbosity=2)
