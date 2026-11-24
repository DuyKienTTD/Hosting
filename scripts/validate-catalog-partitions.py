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
def keyed(rows):
    out = {}
    for row in rows:
        key = re.search(r"^  - id: (.+)$", row, re.M).group(1)
        if key in out:
            raise ValueError("duplicate ID: " + key)
        path = re.search(r"^    path: (.+)$", row, re.M).group(1)
        if not (ROOT / path).is_file():
            raise ValueError("missing path: " + path)
        out[key] = row
    return out
def main():
    source = keyed(records((ROOT / "CATALOG.yaml").read_text(encoding="utf-8")))
    index = (ROOT / "catalog/INDEX.yaml").read_text(encoding="utf-8")
    rows = []
    for kind, path, count in re.findall(r"^  (\w+):\n    path: (catalog/[^\n]+)\n    count: (\d+)$", index, re.M):
        group = records((ROOT / path).read_text(encoding="utf-8"))
        if len(group) != int(count) or any(not re.search(r"^    type: " + kind + "$", x, re.M) for x in group):
            raise ValueError("partition mismatch: " + path)
        rows.extend(group)
    if keyed(rows) != source:
        raise ValueError("catalog partition drift")
    print(f"PASS: {len(source)} exact records")
if __name__ == "__main__":
    main()
