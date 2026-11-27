#!/usr/bin/env python3
"""Hook Stop (Codex và Claude Code): không cho agent kết thúc khi việc chưa xong.

Chặn khi:
  1. Một file work/*.json đã bị sửa trong phiên này có status in_progress
     mà còn tiêu chí passes=false (chưa xong và cũng chưa khai báo blocked).
  2. scripts/check.py --changed báo lỗi (bí mật, PII, JSON sai, link hỏng).
Mỗi lượt chỉ chặn một lần: nếu stop_hook_active=true thì cho dừng, tránh vòng lặp.
Hai công cụ cùng hiểu output {"decision": "block", "reason": "..."}.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def git(*args: str) -> str:
    return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True, check=False).stdout


def touched_work_files() -> list[Path]:
    base = git("merge-base", "HEAD", "origin/main").strip() or "HEAD"
    names = set(git("diff", "--name-only", base).split())
    names |= set(git("ls-files", "--others", "--exclude-standard").split())
    return [ROOT / n for n in names if n.startswith("work/") and n.endswith(".json") and n != "work/TEMPLATE.json"]


def pending_reasons() -> list[str]:
    reasons = []
    for f in touched_work_files():
        if not f.exists():
            continue
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            reasons.append(f"{f.name}: JSON lỗi")
            continue
        if d.get("status") == "in_progress":
            left = [c.get("id", "?") for c in d.get("criteria") or [] if c.get("passes") is not True]
            if left:
                reasons.append(
                    f"#{d.get('issue')} còn tiêu chí chưa đạt: {', '.join(left)}. "
                    "Hãy hoàn thành và chạy verify, hoặc đặt status=blocked kèm blocker."
                )
    r = subprocess.run([sys.executable, str(ROOT / "scripts" / "check.py"), "--changed"],
                       capture_output=True, text=True, check=False)
    if r.returncode != 0:
        reasons.append("scripts/check.py báo lỗi:\n" + r.stdout[-2000:])
    return reasons


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        payload = {}
    if payload.get("stop_hook_active"):
        print(json.dumps({}))
        return
    try:
        reasons = pending_reasons()
    except Exception as exc:  # noqa: BLE001 - lỗi hook không được giữ agent mãi
        print(json.dumps({"systemMessage": f"stop_gate lỗi: {exc}"}))
        return
    if reasons:
        print(json.dumps({"decision": "block", "reason": "Chưa được kết thúc:\n- " + "\n- ".join(reasons)}, ensure_ascii=False))
    else:
        print(json.dumps({}))


if __name__ == "__main__":
    main()
