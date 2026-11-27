#!/usr/bin/env python3
"""Kiểm tra bắt buộc của repo Hosting. CI và hook Stop cùng gọi script này.

Dùng: python3 scripts/check.py            # kiểm toàn bộ
      PR_BODY="..." python3 scripts/check.py  # CI trên PR: thêm cổng "xong" theo Closes #N
      python3 scripts/check.py --changed  # chỉ file thay đổi so với origin/main (nhanh, cho hook)
Thoát 0 = đạt, 1 = có lỗi (in danh sách lỗi).
"""
from __future__ import annotations

import ipaddress
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ALLOW_FILE = ROOT / "scripts" / "check-allow.txt"
TEXT_EXT = {".md", ".txt", ".json", ".yml", ".yaml", ".py", ".sh", ".ps1", ".toml", ".js", ".mjs", ".ts", ".sql", ".conf", ".env", ".example", ""}

SECRET_PATTERNS = [
    ("private key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("GitHub token", re.compile(r"\b(ghp|gho|ghs|ghu|ghr)_[A-Za-z0-9]{30,}\b|\bgithub_pat_[A-Za-z0-9_]{40,}")),
    ("OpenAI/Anthropic key", re.compile(r"\bsk-(ant-|proj-)?[A-Za-z0-9_\-]{24,}")),
    ("AWS key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("Google API key", re.compile(r"\bAIza[0-9A-Za-z_\-]{35}\b")),
    ("secret assignment", re.compile(r"(?i)\b(password|passwd|secret|api[_-]?key|access[_-]?token|auth[_-]?token)\b\s*[:=]\s*['\"][A-Za-z0-9/+_\-]{20,}['\"]")),
]
PHONE = re.compile(r"(?<![\w.])(?:\+84|0)(?:3|5|7|8|9)\d{8}(?![\w])")
IPV4 = re.compile(r"(?<![\w.\-])(\d{1,3}(?:\.\d{1,3}){3})(?![\w.\-])")
MD_LINK = re.compile(r"\]\(([^)\s]+)\)")


def git(*args: str) -> str:
    return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True, check=False).stdout


def tracked_files(changed_only: bool) -> list[str]:
    if changed_only:
        base = git("merge-base", "HEAD", "origin/main").strip() or "HEAD"
        names = set(git("diff", "--name-only", "--diff-filter=ACMR", base).split())
        names |= set(git("ls-files", "--others", "--exclude-standard").split())
        return sorted(n for n in names if (ROOT / n).is_file())
    out = set(git("ls-files").split("\n"))
    out |= set(git("ls-files", "--others", "--exclude-standard").split("\n"))
    return sorted(n for n in out if n and (ROOT / n).is_file())


def load_allow() -> list[re.Pattern[str]]:
    if not ALLOW_FILE.exists():
        return []
    pats = []
    for line in ALLOW_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            pats.append(re.compile(line))
    return pats


def allowed(path: str, line: str, allow: list[re.Pattern[str]]) -> bool:
    probe = f"{path}:{line}"
    return any(p.search(probe) for p in allow)


def is_public_ip(text: str) -> bool:
    try:
        ip = ipaddress.ip_address(text)
    except ValueError:
        return False
    if ip.is_private or ip.is_loopback or ip.is_reserved or ip.is_multicast or ip.is_unspecified or ip.is_link_local:
        return False
    for net in ("192.0.2.0/24", "198.51.100.0/24", "203.0.113.0/24"):
        if ip in ipaddress.ip_network(net):
            return False
    return True


def check_content(files: list[str], allow: list[re.Pattern[str]]) -> list[str]:
    errors = []
    for rel in files:
        p = ROOT / rel
        name = p.name.lower()
        if name == ".env" or (name.startswith(".env.") and not name.endswith(".example")):
            errors.append(f"{rel}: file .env không được commit")
            continue
        if p.suffix.lower() not in TEXT_EXT or p.stat().st_size > 2_000_000:
            continue
        if rel == "scripts/check.py":
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for no, line in enumerate(text.splitlines(), 1):
            if allowed(rel, line, allow):
                continue
            for label, pat in SECRET_PATTERNS:
                if pat.search(line):
                    errors.append(f"{rel}:{no}: nghi là {label}")
            if PHONE.search(line):
                errors.append(f"{rel}:{no}: nghi là số điện thoại thật")
            for m in IPV4.finditer(line):
                if is_public_ip(m.group(1)):
                    errors.append(f"{rel}:{no}: IP công khai {m.group(1)}")
    return errors


def check_paths(files: list[str]) -> list[str]:
    return [f"{f}: đường dẫn chứa 'zalo' — thuộc repo TTD-Zalo-Assistant" for f in files if "zalo" in f.lower()]


def check_work(files: list[str]) -> list[str]:
    errors = []
    for rel in files:
        if not (rel.startswith("work/") and rel.endswith(".json")):
            continue
        try:
            data = json.loads((ROOT / rel).read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"{rel}: JSON lỗi ({exc})")
            continue
        for key in ("issue", "title", "status", "criteria"):
            if key not in data:
                errors.append(f"{rel}: thiếu trường '{key}'")
        if data.get("status") not in {"todo", "in_progress", "blocked", "done"}:
            errors.append(f"{rel}: status phải là todo|in_progress|blocked|done")
        if data.get("status") == "blocked" and not data.get("blocker"):
            errors.append(f"{rel}: status blocked phải có blocker")
        crit = data.get("criteria") or []
        if not isinstance(crit, list) or not crit:
            errors.append(f"{rel}: criteria phải là danh sách không rỗng")
            continue
        for c in crit:
            cid = c.get("id", "?")
            for key in ("id", "description", "verify", "passes"):
                if key not in c:
                    errors.append(f"{rel}: tiêu chí {cid} thiếu '{key}'")
            if c.get("passes") is True and not c.get("evidence"):
                errors.append(f"{rel}: tiêu chí {cid} passes=true nhưng không có evidence")
        if data.get("status") == "done" and not all(c.get("passes") is True for c in crit):
            errors.append(f"{rel}: status done nhưng còn tiêu chí chưa đạt")
    return errors


def check_links(files: list[str]) -> list[str]:
    errors = []
    for rel in files:
        if not rel.endswith(".md") or rel.startswith("archive/"):
            continue
        p = ROOT / rel
        for no, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
            for target in MD_LINK.findall(line):
                if re.match(r"^[a-z]+:", target) or target.startswith("#"):
                    continue
                path = target.split("#", 1)[0]
                if path and not (p.parent / path).exists():
                    errors.append(f"{rel}:{no}: link hỏng -> {target}")
    return errors


def check_pr_done() -> list[str]:
    """Cổng "xong" cho mọi người thực thi, kể cả công cụ không có hook (ChatGPT Work, Codex cloud).

    PR có "Closes #N" thì work/N.json phải tồn tại, và hoặc status=done (mọi tiêu chí passes=true),
    hoặc status=blocked kèm blocker. PR không đóng issue nào thì bỏ qua.
    """
    body = os.environ.get("PR_BODY")
    if body is None:
        return []
    errors = []
    for num in sorted(set(re.findall(r"(?i)\b(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?)\s+#(\d+)", body))):
        f = ROOT / "work" / f"{num}.json"
        if not f.exists():
            errors.append(f"PR đóng #{num} nhưng thiếu work/{num}.json")
            continue
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue  # check_work đã báo
        if d.get("status") not in {"done", "blocked"}:
            left = [c.get("id", "?") for c in d.get("criteria") or [] if c.get("passes") is not True]
            errors.append(f"#{num} chưa xong (status={d.get('status')}, còn {', '.join(left) or '?'}); "
                          "hoàn thành và đặt status=done, hoặc status=blocked kèm blocker")
    return errors


def main() -> int:
    changed = "--changed" in sys.argv
    files = tracked_files(changed)
    allow = load_allow()
    errors = check_paths(files) + check_content(files, allow) + check_work(files) + check_links(files) + check_pr_done()
    if errors:
        print("CHECK FAIL")
        for e in errors:
            print(" -", e)
        return 1
    print(f"CHECK PASS ({len(files)} file)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
