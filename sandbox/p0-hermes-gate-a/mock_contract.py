"""Wire bytes and synthetic usage for the one-shot provider mock rehearsal."""

import hashlib
import json
from decimal import Decimal

from one_shot import MODEL, RESERVE_USD, usd

MAX_INPUT = 4_000
MAX_OUTPUT = 600
MAX_RESPONSE_BYTES = 256 * 1024
ALLOWED_FIELDS = {"model", "input", "instructions", "include", "prompt_cache_key",
                  "reasoning", "store", "stream", "max_output_tokens", "service_tier"}


def no_duplicate_keys(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError("DUPLICATE_JSON_KEY")
        value[key] = item
    return value


def encode(value):
    return json.dumps(value, ensure_ascii=True, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("ascii")


def freeze(body):
    if (body.keys() - ALLOWED_FIELDS or body.get("model") != MODEL
            or body.get("service_tier", "default") != "default"):
        raise ValueError("ONE_SHOT_REQUEST_POLICY")
    final = dict(body, service_tier="default", max_output_tokens=MAX_OUTPUT, store=False)
    wire = encode(final)
    if len(wire) > MAX_INPUT:
        raise ValueError("MOCK_WIRE_SIZE_LIMIT")
    return wire, hashlib.sha256(wire).hexdigest()


def usage_from_response(payload, streaming):
    if streaming:
        events = []
        blocks = payload.decode("utf-8").replace("\r\n", "\n").split("\n\n")
        for block in blocks[:-1]:
            data = "\n".join(line[5:].lstrip(" ") for line in block.splitlines()
                             if line.startswith("data:"))
            if data and data != "[DONE]":
                events.append(json.loads(data, object_pairs_hook=no_duplicate_keys))
        terminal = [event for event in events if event.get("type") in
                    {"response.completed", "response.incomplete", "response.failed"}]
        if len(terminal) != 1 or terminal[0] is not events[-1] or blocks[-1].strip():
            raise ValueError("TERMINAL_EVENT_REQUIRED")
        response = terminal[0]["response"]
        if terminal[0]["type"] != "response." + response["status"]:
            raise ValueError("TERMINAL_STATUS_MISMATCH")
    else:
        response = json.loads(payload, object_pairs_hook=no_duplicate_keys)
    if (response["status"] not in {"completed", "incomplete", "failed"}
            or response["model"] != MODEL or response["service_tier"] != "default"
            or not isinstance(response["id"], str) or not response["id"]):
        raise ValueError("RESPONSE_SCOPE_MISMATCH")
    usage = response["usage"]
    input_tokens = usage["input_tokens"]
    output_tokens = usage["output_tokens"]
    input_details = usage["input_tokens_details"]
    cached = input_details["cached_tokens"]
    writes = input_details.get("cache_write_tokens", 0)
    longer_writes = (input_details.get("cache_write_tokens_details") or {}).get("ttl_12h_tokens", 0)
    reasoning = usage["output_tokens_details"]["reasoning_tokens"]
    counts = (input_tokens, output_tokens, cached, writes, longer_writes, reasoning, usage["total_tokens"])
    if (any(type(count) is not int or count < 0 for count in counts)
            or cached + writes > input_tokens or longer_writes != 0
            or reasoning > output_tokens or usage["total_tokens"] != input_tokens + output_tokens
            or input_tokens > MAX_INPUT or output_tokens > MAX_OUTPUT):
        raise ValueError("USAGE_OUT_OF_POLICY")
    cost = ((input_tokens - cached - writes) * Decimal("0.10") + cached * Decimal("0.01")
            + writes * Decimal("0.125") + output_tokens * Decimal("0.50")) / 1_000_000
    if cost > usd(RESERVE_USD):
        raise ValueError("USAGE_ABOVE_RESERVATION")
    return {"model": MODEL, "service_tier": "default", "response_status": response["status"],
            "response_id_hash": hashlib.sha256(response["id"].encode()).hexdigest(),
            "input_tokens": input_tokens, "output_tokens": output_tokens,
            "reasoning_tokens": reasoning, "cached_tokens": cached, "cache_write_tokens": writes,
            "estimated_cost_usd": str(cost)}
