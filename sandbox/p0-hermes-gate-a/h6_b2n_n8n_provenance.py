"""Read-only B2-N projection. Emits only allowlisted metadata and comparisons."""

import ast
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
import sys
import types
import urllib.request


BASE = "322a2c15be6688ec33c1b3d72336bbeee5196e05"
PROBE = "564a92879d5eafa5a0e2a65637df70143f4067ce"
SOURCE = "sandbox/p0-hermes-gate-a/"
SEED = "sandbox/p0-level1/fake-ads-audit-v1.workflow.json"
SEED_BLOB = "83d478a04309037cffe4d7771eeb31c8211d10a3"
TRANSFORM_BLOB = "9db7a59eb4244e1c4ebbe4dafd4877a135723128"
PROBE_BLOB = "246a74752940fd2cc92fdedd82da53acaffee5d6"
CONTAINER = "/ttd-p0-n8n-sandbox"
PROJECT = "ttd-p0-level1"
WORKFLOW = "ttdP0FakeAdsV1"
MOUNT = "/home/node/.n8n"
IGNORED = {"position", "webhookId", "notes", "notesInFlow"}
NODE_FIELDS = {"id", "name", "type", "typeVersion", "parameters", "credentials", "disabled", "retryOnFail",
               "maxTries", "waitBetweenTries", "onError", "continueOnFail", "executeOnce", "alwaysOutputData"}
IMAGE_DIGEST = re.compile(r"sha256:[a-f0-9]{64}")


def need(condition, code):
    if not condition:
        raise RuntimeError(code)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False).encode()


def fetch(commit, path, blob):
    url = f"https://raw.githubusercontent.com/DuyKienTTD/Hosting/{commit}/{path}"
    with urllib.request.urlopen(url, timeout=15) as response:
        raw = response.read(512 * 1024 + 1)
    actual = hashlib.sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest()
    need(len(raw) <= 512 * 1024 and actual == blob, "PIN_MISMATCH")
    return raw


def candidate(seed, transform):
    tree = ast.parse(transform)
    validator = next(ast.literal_eval(node.value) for node in tree.body if isinstance(node, ast.Assign)
                     and any(isinstance(target, ast.Name) and target.id == "VALIDATOR" for target in node.targets))
    wf, = json.loads(seed)
    nodes = {node["id"]: node for node in wf["nodes"]}
    nodes["validate-callback"]["parameters"]["jsCode"] = validator
    call = nodes["call-reasoner"]
    call["parameters"].update(url="http://reasoner-p0:8080/v1/reason", options={"timeout": 30000})
    call.update(retryOnFail=False, maxTries=1, waitBetweenTries=0)
    return wf


def projected(workflow, auth_template):
    nodes = {}
    for raw in workflow["nodes"]:
        item = {key: deepcopy(value) for key, value in raw.items() if key not in IGNORED}
        node_id = item["id"]
        need(node_id not in nodes, "DUPLICATE_NODE_ID")
        opts = item["parameters"]
        if node_id == "auth-router":
            # Only redact a literal in the public template. Any other source is a delta.
            left, right = auth_template.split("'__P0_TOKEN__'")
            auth = opts.get("jsCode")
            if isinstance(auth, str) and re.fullmatch(
                re.escape(left) + r"(?:'[^'\\\r\n]*'|\"[^\"\\\r\n]*\")" + re.escape(right), auth
            ):
                opts["jsCode"] = left + "'<fixture-bearer>'" + right
        if node_id == "webhook-trigger" and opts.get("path") == "ttd-p0-fake-ads-audit-v1":
            opts["path"] = "<fixture-webhook>"
        if node_id == "call-reasoner":
            if opts.get("url") == "http://reasoner-p0:8080/v1/reason":
                opts["url"] = "http://fixture-bridge/v1/reason"
            for header in opts.get("headerParameters", {}).get("parameters", []):
                if (header.get("name", "").lower() == "authorization"
                        and re.fullmatch(r"Bearer [A-Za-z0-9_.~+/=-]+", header.get("value", ""))):
                    header["value"] = "Bearer <fixture-bearer>"
        nodes[node_id] = item
    return {"nodes": nodes, "connections": workflow["connections"], "settings": workflow.get("settings") or {}}


def compare(published, public):
    auth = next(node["parameters"]["jsCode"] for node in public["nodes"] if node["id"] == "auth-router")
    expected = projected(public, auth)
    found = projected(published, auth)
    missing = sorted(expected["nodes"].keys() - found["nodes"].keys())
    deltas = {}
    for node_id in sorted(expected["nodes"].keys() & found["nodes"].keys()):
        left, right = found["nodes"][node_id], expected["nodes"][node_id]
        fields = {key for key in left.keys() | right.keys()
                  if key not in left or key not in right or left[key] != right[key]}
        if fields:
            deltas[node_id] = sorted(fields & NODE_FIELDS) + (["other_field"] if fields - NODE_FIELDS else [])
    equal = expected == found
    # Never emit a digest of unmatched real arguments, code, references, or settings.
    left = found["nodes"].get("call-reasoner", {}).get("parameters", {})
    right = expected["nodes"]["call-reasoner"]["parameters"]
    return {"projection_equal": equal, "candidate_projection_sha256": sha(canonical(expected)),
            "published_projection_sha256": sha(canonical(expected)) if equal else None,
            "connections_equal": found["connections"] == expected["connections"],
            "entity_settings_equal": found["settings"] == expected["settings"],
            "known_missing_nodes": missing, "unexpected_node_count": len(found["nodes"].keys() - expected["nodes"].keys()),
            "node_field_deltas": deltas,
            "known_bridge_parameter_deltas": sorted(key for key in right if key not in left or left[key] != right[key]),
            "unknown_bridge_parameter_count": len(left.keys() - right.keys()),
            "validator_matches_public_code": "validate-callback" not in deltas and "validate-callback" not in missing,
            "candidate_has_separate_receipt_node": False}


def metadata(helper):
    fields = ("Id", "Name", "Image", "State.Running", "State.Pid", "State.StartedAt", "Mounts", "Config.Labels")
    row, = helper.inspect_fields("container", [CONTAINER[1:]], fields)
    labels = row["Config.Labels"]
    need(row["Name"] == CONTAINER and row["State.Running"] and row["State.Pid"] > 0
         and labels.get("com.docker.compose.project") == PROJECT
         and labels.get("com.docker.compose.service") == "n8n-sandbox", "SANDBOX_IDENTITY_MISMATCH")
    mount, = (m for m in row["Mounts"] if m["Destination"] == MOUNT and m["Type"] == "bind")
    db = Path(mount["Source"]) / ".n8n/database.sqlite"
    need(db.resolve(strict=True) == db and db.is_file(), "SQLITE_BIND_MISMATCH")
    return (row["Id"], row["Image"], row["State.Pid"], row["State.StartedAt"]), db


def installed_package(pid):
    root = Path(f"/proc/{pid}/root")
    possibilities = ["usr/local/lib/node_modules/n8n/package.json", "usr/local/lib/node_modules/n8n/dist/package.json",
                     "usr/local/share/.config/yarn/global/node_modules/n8n/package.json"]
    for relative in possibilities:
        path = root / relative
        if path.is_file():
            value = json.loads(path.read_bytes())
            if value.get("name") == "n8n" and re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+(?:[-+][A-Za-z0-9.-]+)?",
                                                          value.get("version", "")):
                return value["version"]
    raise RuntimeError("INSTALLED_N8N_PACKAGE_NOT_FOUND")


def read_revision(db, public):
    with sqlite3.connect(db.as_uri() + "?mode=ro", uri=True, timeout=0.5) as con:
        con.execute("PRAGMA query_only=ON")
        con.execute("PRAGMA temp_store=MEMORY")
        sql = """
        SELECT w.activeVersionId,h.nodes,h.connections,w.settings
        FROM workflow_entity w JOIN workflow_history h
          ON h.versionId=w.activeVersionId AND h.workflowId=w.id
        WHERE w.id=? AND w.active=1
        """
        results = []
        for _ in range(2):
            row = con.execute(sql, (WORKFLOW,)).fetchone()
            need(row and row[0] and row[1] and row[2], "PUBLISHED_HISTORY_UNAVAILABLE")
            results.append(row)
        need(results[0] == results[1], "PUBLISHED_REVISION_DRIFT")
    version, nodes, connections, settings = results[0]
    return compare({"nodes": json.loads(nodes), "connections": json.loads(connections),
                    "settings": json.loads(settings) if settings else {}}, public) | {
        "revision_fingerprint": sha(("b2n-published-v1:" + version).encode()),
        "repeated_revision_equal": True, "published_join": True, "sqlite_mode": "ro"}


def fenced(db, public, fence):
    read, write = os.pipe()
    pid = os.fork()
    if pid == 0:
        os.close(read)
        try:
            need(fence(), "LANDLOCK_WRITE_FENCE_UNAVAILABLE")
            result = read_revision(db, public) | {"landlock_write_fence": True}
        except Exception as error:
            # Exception text can mention a private path or database details.
            result = {"failed": type(error).__name__}
        with os.fdopen(write, "wb") as channel:
            channel.write(canonical(result))
        os._exit(0)
    os.close(write)
    with os.fdopen(read, "rb") as channel:
        raw = channel.read(65536)
    _, status = os.waitpid(pid, 0)
    need(status == 0 and raw, "FENCED_HELPER_FAILED")
    return json.loads(raw)


def run():
    baseline = types.ModuleType("pinned_b2h")
    exec(compile(fetch(PROBE, SOURCE + "h6_b2h_preflight.py", PROBE_BLOB), "pinned-b2h", "exec"),
         baseline.__dict__)
    helper = baseline.load_baseline()
    public = candidate(fetch(BASE, SEED, SEED_BLOB), fetch(BASE, SOURCE + "workflow_gate_a.py", TRANSFORM_BLOB))
    identity, db = metadata(helper)
    _, image_id, pid, _ = identity
    image, = helper.inspect_fields("image", [image_id], ("Id", "RepoDigests", "Os", "Architecture"))
    need(image["Id"] == image_id and IMAGE_DIGEST.fullmatch(image_id), "IMAGE_IDENTITY_MISMATCH")
    digests = sorted({value.split("@")[1] for value in image["RepoDigests"] or []
                      if re.fullmatch(r"(?:docker\.n8n\.io/|docker\.io/)?n8nio/n8n@sha256:[a-f0-9]{64}", value)})
    need(image["Os"] == "linux" and image["Architecture"] in ("amd64", "arm64"), "UNEXPECTED_PLATFORM")
    version = installed_package(pid)
    print("B2N_IMAGE", json.dumps({"id": image_id, "known_n8n_registry_digests": digests, "os": image["Os"],
                                  "arch": image["Architecture"], "installed_version": version}), flush=True)
    result = fenced(db, public, baseline.block_filesystem_writes)
    need(metadata(helper) == (identity, db) and installed_package(pid) == version, "SANDBOX_CHANGED_DURING_PROBE")
    print("B2N_PROJECTION", json.dumps(result, sort_keys=True), flush=True)


if __name__ == "__main__":
    if sys.argv[1:] == ["--candidate"]:
        print(json.dumps(compare(
            (public := candidate(fetch(BASE, SEED, SEED_BLOB), fetch(BASE, SOURCE + "workflow_gate_a.py", TRANSFORM_BLOB))),
            public), sort_keys=True))
    else:
        try:
            run()
        except Exception as error:
            print("B2N_STOP", type(error).__name__, flush=True)
            raise SystemExit(1) from None
