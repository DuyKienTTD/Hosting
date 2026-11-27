#!/usr/bin/env python3
"""Hook SessionStart (Codex và Claude Code). In ngữ cảnh bắt buộc vào đầu phiên.

Stdout được công cụ thêm vào ngữ cảnh của agent. Không bao giờ làm hỏng phiên:
mọi lỗi đều bị nuốt và vẫn thoát 0.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def progress_head(max_lines: int = 40) -> str:
    p = ROOT / "PROGRESS.md"
    if not p.exists():
        return "(chưa có PROGRESS.md)"
    return "\n".join(p.read_text(encoding="utf-8").splitlines()[:max_lines])


def open_work() -> list[str]:
    rows = []
    for f in sorted((ROOT / "work").glob("*.json")):
        if f.name == "TEMPLATE.json":
            continue
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            rows.append(f"- {f.name}: JSON lỗi, sửa trước khi làm việc khác")
            continue
        if d.get("status") == "done":
            continue
        crit = d.get("criteria") or []
        left = sum(1 for c in crit if c.get("passes") is not True)
        extra = f" — bị chặn: {d.get('blocker')}" if d.get("status") == "blocked" else ""
        rows.append(f"- #{d.get('issue')} {d.get('title')} [{d.get('status')}, còn {left}/{len(crit)} tiêu chí]{extra}")
    return rows


def open_issues() -> str:
    try:
        r = subprocess.run(
            ["gh", "issue", "list", "--state", "open", "--limit", "20"],
            cwd=ROOT, capture_output=True, text=True, timeout=15, check=False,
        )
        return r.stdout.strip() if r.returncode == 0 and r.stdout.strip() else ""
    except (OSError, subprocess.TimeoutExpired):
        return ""


def main() -> None:
    try:
        parts = [
            "# Ngữ cảnh phiên (tự động)",
            "Quy tắc: AGENTS.md. Làm đúng một issue; cuối phiên cập nhật work/<issue>.json và PROGRESS.md.",
            "## PROGRESS.md (đầu file)",
            progress_head(),
            "## Việc đang mở trong work/",
            "\n".join(open_work()) or "(không có)",
        ]
        issues = open_issues()
        if issues:
            parts += ["## Issue đang mở trên GitHub", issues]
        print("\n".join(parts))
    except Exception as exc:  # noqa: BLE001 - hook không được làm hỏng phiên
        print(f"(session_start lỗi: {exc}; hãy tự đọc PROGRESS.md và work/)")


if __name__ == "__main__":
    main()
