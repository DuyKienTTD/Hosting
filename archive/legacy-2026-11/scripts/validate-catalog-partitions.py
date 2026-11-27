#!/usr/bin/env python3
"""Verify lossless catalog partitions against legacy canonical registry."""
from pathlib import Path
import re
import sys
ROOT = Path(__file__).resolve().parents[1]
def records(text):
    body = text.split("\ndocuments:\n", 1)[1] if "\ndocuments:\n" in text else text.split("documents:\n", 1)[1]
    body = body.split("\ncollections:\n", 1)[0]
    return [s.rstrip() for s in re.split(r"(?=^  - id: )", body, flags=re.M)[1:]] if not body.startswith("  - id: ") else [s.rstrip() for s in re.split(r"(?=^  - id: )", body, flags=re.M) if s.strip()]
def keyed(rows, root):
    out = {}
    for row in rows:
        key = re.search(r"^  - id: (.+)$", row, re.M).group(1)
        if key in out:
            raise ValueError("duplicate ID: " + key)
        path = re.search(r"^    path: (.+)$", row, re.M).group(1)
        if not (root / path).is_file():
            raise ValueError("missing path: " + path)
        out[key] = row
    return out
def validate(root=ROOT):
    root = Path(root)
    source = keyed(records((root / "CATALOG.yaml").read_text(encoding="utf-8")), root)
    allowed = {"knowledge", "script", "inventory", "rule", "decision"}
    if any(not re.search(r"^    type: (" + "|".join(sorted(allowed)) + r")$", row, re.M) or re.search(r"^    path: (tasks|reports)/", row, re.M) for row in source.values()):
        raise ValueError("operational record in durable catalog")
    index = (root / "catalog/INDEX.yaml").read_text(encoding="utf-8")
    rows = []
    seen = set()
    for kind, path, count in re.findall(r"^  (\w+):\n    path: (catalog/[^\n]+)\n    count: (\d+)$", index, re.M):
        if kind not in allowed or kind in seen or Path(path).parent != Path("catalog"):
            raise ValueError("invalid partition: " + path)
        seen.add(kind)
        group = records((root / path).read_text(encoding="utf-8"))
        if len(group) != int(count) or any(not re.search(r"^    type: " + kind + "$", x, re.M) for x in group):
            raise ValueError("partition mismatch: " + path)
        rows.extend(group)
    if seen != allowed or keyed(rows, root) != source:
        raise ValueError("catalog partition drift")
    return len(source)
def main():
    print(f"PASS: {validate()} exact records")
if __name__ == "__main__":
    main()
