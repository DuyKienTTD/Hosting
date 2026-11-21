#!/usr/bin/env python3
"""Negative policy tests executed inside the guard container."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from pathlib import Path


URL = "http://127.0.0.1:8081"
TOKEN = Path("/run/secrets/guard_service_token").read_text().strip()


def post(path: str, body: dict, token: str = TOKEN) -> int:
    req = urllib.request.Request(
        URL + path,
        data=json.dumps(body).encode(),
        method="POST",
        headers={"Authorization": "Bearer " + token, "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=3) as response:
            response.read()
            return response.status
    except urllib.error.HTTPError as error:
        error.read()
        return error.code


base = {"model": "gpt-6-luna", "input": "fake", "stream": False}
cases = {
    "wrong_auth": post("/v1/responses", base, "wrong-token"),
    "wrong_path": post("/v1/chat/completions", base),
    "wrong_model": post("/v1/responses", {**base, "model": "other"}),
    "tools_present": post("/v1/responses", {**base, "tools": []}),
    "cap_too_high": post("/v1/responses", {**base, "max_output_tokens": 601}),
    "oversize": post("/v1/responses", {**base, "input": "x" * 4_100}),
}
expected = {"wrong_auth": 401, "wrong_path": 404, "wrong_model": 422, "tools_present": 422, "cap_too_high": 422, "oversize": 422}
assert cases == expected, (cases, expected)
print(json.dumps({"result": "PASS", "cases": cases}, sort_keys=True))
