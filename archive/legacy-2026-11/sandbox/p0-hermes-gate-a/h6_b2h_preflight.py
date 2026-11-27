"""Read-only KVM2 H6 preflight. The proposed overlay exists only in Compose stdin."""

import ast
import copy
import ctypes
import hashlib
import json
import os
import re
import sqlite3
import stat
import subprocess
import types
import urllib.request
from pathlib import Path

RAW = "https://raw.githubusercontent.com/DuyKienTTD/Hosting/"
B2E_REV = "d32aff15fee7972d217e2f8c8a1f81fa5f987906"
B2E_BLOB = "dcb891284f44763480f4b6675960836fa9d2f64e"
LIVE_TARGET = "/opt/ttd/ledger/level2-budget.json"
PROVIDER = "/run/secrets/openai_provider_api_key"
IPC_TARGET = "/opt/ttd/h6-b2f-live-ipc"
AUTH_TARGET = "/run/h6-b2f-live-auth"
WRITER_LEDGER = "/opt/ttd/p0-ledger"
SOURCE_TARGET = "/opt/ttd/h6-src"
WRITER_NAME = "ttd-gate-b-h6-writer"
WEBHOOK = "ttd-p0-fake-ads-audit-v1"


def require(value, message):
    if not value:
        raise RuntimeError(message)


def load_baseline():
    url = RAW + B2E_REV + "/sandbox/p0-hermes-gate-a/h6_b2e_rehearsal.py"
    with urllib.request.urlopen(url, timeout=15) as result:
        data = result.read(64 * 1024)
    require(hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest() == B2E_BLOB, "baseline source blob")
    module = types.ModuleType("b2h_pinned_read_only_helper")
    exec(compile(data, "b2e-read-only-helper", "exec"), module.__dict__)
    return module


def mount(container, target):
    entry, = (item for item in container["Mounts"] if item["Destination"] == target)
    return entry


def root_source(container, target, read_only):
    entry = mount(container, target)
    target_path = Path(entry["Source"])
    require(entry["Type"] == "bind" and entry["RW"] != read_only
            and target_path.resolve(strict=True) == target_path, "unexpected live bind/source")
    return target_path


def source(path):
    data = path.read_bytes()
    return data.decode(), hashlib.sha256(data).hexdigest()


def assignment(tree, name):
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == name for target in node.targets):
            if isinstance(node.value, ast.Constant):
                return node.value.value
    return None


def function(tree, name):
    return next(node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef) and node.name == name)


def name_of(call):
    return call.func.id if isinstance(call.func, ast.Name) else getattr(call.func, "attr", "")


def literal_timeouts(body, call_name):
    return sorted({keyword.value.value for node in ast.walk(body) if isinstance(node, ast.Call) and name_of(node) == call_name
                   for keyword in node.keywords if keyword.arg == "timeout" and isinstance(keyword.value, ast.Constant)
                   and type(keyword.value.value) in (int, float)})


def bridge_metadata(path):
    raw, sha = source(path)
    tree = ast.parse(raw)
    run = function(tree, "run_hermes")
    poll_budget = next(
        node.value.right.value for node in ast.walk(run)
        if isinstance(node, ast.Assign) and any(getattr(target, "id", "") == "deadline" for target in node.targets)
        and isinstance(node.value, ast.BinOp) and isinstance(node.value.right, ast.Constant))
    callback = function(tree, "callback")
    callback_targets_same_webhook = assignment(tree, "CALLBACK_URL") == f"http://n8n-p0-sandbox:5678/webhook/{WEBHOOK}"
    return {
        "source_sha256": sha, "run_poll_budget_seconds": poll_budget,
        "hermes_post_and_poll_socket_timeout_seconds": literal_timeouts(run, "request_json"),
        "callback_socket_timeout_seconds": literal_timeouts(callback, "request_json"),
        "callback_path_matches_sandbox": callback_targets_same_webhook,
        "callback_uses_bearer_file_reference": any(
            isinstance(node, ast.Call) and name_of(node) == "bearer"
            and any(getattr(arg, "id", "") == "P0_TOKEN_FILE" for arg in node.args) for node in ast.walk(callback)),
        "mock_callback_schema": "hermes_mock_succeeded" in raw and "gate-a-provider-mock" in raw,
        "references_capture": "/opt/ttd/capture" in raw,
    }


def proxy_metadata(path):
    raw, sha = source(path)
    tree = ast.parse(raw)
    handler = function(tree, "do_CONNECT")
    numbers = [node.args[-1].value for node in ast.walk(handler) if isinstance(node, ast.Call)
               and name_of(node) == "select" and isinstance(node.args[-1], ast.Constant)]
    return {"source_sha256": sha, "port": assignment(tree, "PORT"),
            "allowlisted_openai_443": assignment(tree, "ALLOWED_TARGET") == "api.openai.com:443",
            "connect_socket_timeout_seconds": literal_timeouts(handler, "create_connection"),
            "idle_select_timeout_seconds": numbers}


def selected_hermes_env(b):
    # Go template projects timeout variable presence, plus one allowlisted route comparison.
    template = ('{{range .Config.Env}}{{ $p := split . "=" }}'
                '{{if or (eq (index $p 0) "HERMES_API_TIMEOUT") (eq (index $p 0) "HERMES_API_CALL_STALE_TIMEOUT")}}'
                '{{index $p 0}}{{println}}{{end}}'
                '{{if eq (index $p 0) "OPENAI_BASE_URL"}}'
                '{{if eq (index $p 1) "http://gate-a-guard:8081/v1"}}route_matches{{println}}{{end}}{{end}}{{end}}')
    return set(b.docker("container", "inspect", "--format", template, "ttd-gate-a-hermes").decode().split())


def hermes_metadata(b, container):
    root = Path("/proc") / str(container["State"]["Pid"]) / "root/opt/hermes"
    agent, agent_sha = source(root / "run_agent.py")
    _, gateway_sha = source(root / "gateway/platforms/api_server.py")
    _, routes_sha = source(root / "gateway/platforms/api_server_openai_routes.py")
    tree = ast.parse(agent)
    call = function(tree, "_resolved_api_call_timeout")
    api_default = next((node.args[1].value for node in ast.walk(call) if isinstance(node, ast.Call)
                        and name_of(node) == "env_float" and len(node.args) == 2
                        and getattr(node.args[0], "value", "") == "HERMES_API_TIMEOUT"), None)
    env = selected_hermes_env(b)
    return {"run_agent_source_sha256": agent_sha, "gateway_api_source_sha256": gateway_sha,
            "gateway_routes_source_sha256": routes_sha, "docker_env_route_matches_guard": "route_matches" in env,
            "api_timeout_default_seconds_from_installed_source": api_default,
            "docker_timeout_override_names_present": sorted(env - {"route_matches"}),
            "installed_source_allows_per_model_or_provider_override": "get_provider_request_timeout" in ast.unparse(call),
            "effective_model_transport_timeout_measured": False}


def block_filesystem_writes():
    # Apply an empty Landlock ruleset in the disposable query child only.
    # No file descriptors for the database or sidecars are open at this point.
    if os.uname().machine != "x86_64":
        return False
    libc = ctypes.CDLL(None, use_errno=True)
    libc.syscall.restype = ctypes.c_long
    abi = libc.syscall(444, None, 0, 1)
    if abi < 3:
        return False
    denied = ctypes.c_uint64((1 << 1) | (1 << 14) | sum(1 << bit for bit in range(4, 13)))
    fd = libc.syscall(444, ctypes.byref(denied), ctypes.sizeof(denied), 0)
    if fd < 0:
        return False
    try:
        return libc.prctl(38, 1, 0, 0, 0) == 0 and libc.syscall(446, fd, 0) == 0
    finally:
        os.close(fd)


def workflow_projection(db):
    result = {}
    columns = {row[1] for row in db.execute("PRAGMA table_info(workflow_entity)")}
    published_ref = "activeVersionId" in columns
    history = {row[1] for row in db.execute("PRAGMA table_info(workflow_history)")}
    require({"id", "active", "nodes", "connections"}.issubset(columns), "unknown workflow schema")
    workflow_id = "ttdP0FakeAdsV1"
    result["sandbox_workflow_active"] = bool(db.execute("SELECT active FROM workflow_entity WHERE id=?", (workflow_id,)).fetchone()[0])
    if published_ref and {"versionId", "nodes", "connections"}.issubset(history):
        source_sql = ('SELECT h.nodes,h.connections FROM workflow_entity w JOIN workflow_history h '
                      'ON h.versionId=w.activeVersionId WHERE w.id=?')
        result["using_published_revision"] = bool(db.execute(f"SELECT EXISTS({source_sql})", (workflow_id,)).fetchone()[0])
    else:
        result["using_published_revision"] = False
    if not result["using_published_revision"]:
        source_sql = "SELECT nodes,connections FROM workflow_entity WHERE id=?"
    query = """
        WITH payload AS (SOURCE), nodes AS (
          SELECT json_extract(value,'$.id') AS id, value AS node FROM payload,json_each(payload.nodes)
        )
        SELECT
          (SELECT CAST(json_extract(node,'$.parameters.options.timeout') AS INTEGER) FROM nodes WHERE id='call-reasoner'),
          (SELECT coalesce(json_extract(node,'$.retryOnFail'),0) FROM nodes WHERE id='call-reasoner'),
          (SELECT json_extract(node,'$.parameters.url')='http://reasoner-p0:8080/v1/reason' FROM nodes WHERE id='call-reasoner'),
          (SELECT json_extract(node,'$.parameters.path')=? AND json_extract(node,'$.parameters.httpMethod')='POST' FROM nodes WHERE id='webhook-trigger'),
          (SELECT instr(json_extract(node,'$.parameters.jsCode'),'headers.authorization')>0
                  AND instr(json_extract(node,'$.parameters.jsCode'),'Bearer')>0
                  AND instr(json_extract(node,'$.parameters.jsCode'),'===')>0 FROM nodes WHERE id='auth-router'),
          (SELECT instr(json_extract(node,'$.parameters.jsCode'),'hermes_mock_succeeded')>0
                  AND instr(json_extract(node,'$.parameters.jsCode'),'i.paid === false')>0 FROM nodes WHERE id='validate-callback'),
          (SELECT json_extract(node,'$.parameters.options.responseCode')=401 FROM nodes WHERE id='respond-unauthorized'),
          (SELECT json_extract(node,'$.parameters.conditions.conditions[0].rightValue')='callback' FROM nodes WHERE id='is-callback'),
          (SELECT json_extract(connections,'$."Private Webhook".main[0][0].node')='Auth Router'
                  AND json_extract(connections,'$."Auth Router".main[0][0].node')='Authorized?'
                  AND json_extract(connections,'$."Authorized?".main[0][0].node')='Callback Phase?'
                  AND json_extract(connections,'$."Authorized?".main[1][0].node')='Respond Unauthorized' FROM payload)
    """
    keys = ("reasoner_timeout_ms", "reasoner_retry_on_fail", "routes_to_bridge", "callback_webhook_post_matches",
            "callback_bearer_check_present", "callback_validator_mock_only", "unauthorized_response_401",
            "callback_branch_selected_by_phase", "auth_precedes_callback_branch")
    row = db.execute(query.replace("SOURCE", source_sql), (workflow_id, WEBHOOK)).fetchone()
    result.update(zip(keys, row, strict=True))
    return result


def n8n_metadata(db_path):
    # A WAL read may try to open sidecars RW. Deny all file writes before the query.
    reader, writer = os.pipe()
    pid = os.fork()
    if pid == 0:
        os.close(reader)
        result = {"filesystem_write_deny": block_filesystem_writes(), "wal_visible": False}
        for options in (("mode=ro", "mode=ro&immutable=1") if result["filesystem_write_deny"] else ("mode=ro&immutable=1",)):
            try:
                with sqlite3.connect(db_path.as_uri() + "?" + options, uri=True, timeout=0.25) as db:
                    db.execute("PRAGMA query_only=ON")
                    db.execute("PRAGMA temp_store=MEMORY")
                    result.update(workflow_projection(db))
                result["wal_visible"] = options == "mode=ro"
                break
            except (OSError, sqlite3.Error, TypeError, RuntimeError) as error:
                result["read_error_class"] = type(error).__name__
        os.write(writer, json.dumps(result).encode())
        os._exit(0)
    os.close(writer)
    with os.fdopen(reader, "rb") as channel:
        raw = channel.read()
    _, status = os.waitpid(pid, 0)
    require(status == 0 and raw, "n8n read-only child failed")
    return json.loads(raw)


def stat_summary(path, metadata):
    info = path.lstat()
    return {"uid_gid": [info.st_uid, info.st_gid], "mode": format(stat.S_IMODE(info.st_mode), "04o"),
            "hardlinks": info.st_nlink, "acl_present": bool(metadata[-1])}


def resolve_inputs(b, items):
    guard = items["/ttd-gate-a-guard"]
    level2 = items["/ttd-p0-reasoner"]
    ledger = root_source(guard, LIVE_TARGET, True)
    lock = ledger.with_suffix(".json.lock")
    provider = root_source(guard, PROVIDER, True)
    stats = [b.metadata(path) for path in (ledger.parent, ledger, lock, provider)]
    require(root_source(level2, "/opt/ttd/state", False) == ledger.parent, "Level 2 ledger parent mismatch")
    require(ledger.parent == ledger.parent.resolve() and lock.resolve() == lock and
            [item[2:5] for item in stats] == [(stat.S_IFDIR | 0o700, 0, 0)] + [(stat.S_IFREG | 0o600, 0, 0)] * 3
            and all(not item[-1] for item in stats) and ledger.stat().st_dev == lock.stat().st_dev
            and ledger.stat().st_ino != lock.stat().st_ino, "ledger/key/lock DAC drift")
    return ledger, lock, provider, stats


def network_matrix(b, items):
    key = "ttd-gate-b-guard-private"
    guard, proxy, hermes, bridge, n8n = (items[name] for name in (
        "/ttd-gate-a-guard", "/ttd-p0-provider-egress", "/ttd-gate-a-hermes", "/ttd-gate-a-bridge", "/ttd-p0-n8n-sandbox"))
    membership = [name for name in items if key in items[name]["NetworkSettings.Networks"]]
    live, = b.inspect_fields("network", [key], ("Internal", "EnableIPv6", "Containers"))
    require(set(membership) == {guard["Name"], proxy["Name"]} and live["Internal"] and not live["EnableIPv6"]
            and set(live["Containers"]) == {guard["Id"], proxy["Id"]}, "dedicated Guard/proxy bridge drift")
    require("provider-egress" in proxy["NetworkSettings.Networks"][key]["Aliases"], "B2-F proxy alias missing")
    return {"private_proxy_endpoints": ["guard", "proxy"],
            "private_proxy_alias_matches_b2f": True,
            "dedicated_bridge_internal_ipv6_off": True,
            "guard_to_hermes_shared_networks": sorted(set(guard["NetworkSettings.Networks"]) & set(hermes["NetworkSettings.Networks"])),
            "bridge_to_n8n_shared_networks": sorted(set(bridge["NetworkSettings.Networks"]) & set(n8n["NetworkSettings.Networks"])),
            "non_guard_services_on_real_proxy_bridges": sorted(
                name.removeprefix("/") for name, item in items.items() if name not in (guard["Name"], proxy["Name"])
                and item["State"]["Running"] and set(item["NetworkSettings.Networks"]) & set(proxy["NetworkSettings.Networks"])),
            "listener_ports_published_by_guard_or_proxy": sum(
                len(x["HostConfig.PortBindings"] or {}) for x in (guard, proxy))}


def binding(source_path, target, read_only):
    result = {"type": "bind", "source": str(source_path), "target": target,
              "bind": {"create_host_path": False, "propagation": "rprivate"}}
    if read_only:
        result["read_only"] = True
    return result


def propose(b, items, ledger):
    guard = items["/ttd-gate-a-guard"]
    labels = guard["Config.Labels"]
    project = labels[b.PROJECT_LABEL]
    workdir = Path(labels["com.docker.compose.project.working_dir"])
    base, h4 = labels["com.docker.compose.project.config_files"].split(",")
    prefix = ["docker", "compose", "--env-file", "/dev/null", "-p", project,
              "--project-directory", str(workdir), "--profile", "*", "-f", base, "-f", h4]

    def render(overlay=None):
        argv = prefix + ([] if overlay is None else ["-f", "-"]) + ["config", "--format", "json"]
        job = subprocess.run(argv, input=overlay, capture_output=True, timeout=25,
                             env={"PATH": "/usr/local/bin:/usr/bin:/bin", "HOME": "/nonexistent"})
        require(job.returncode == 0, "proposed Compose render failed")
        return json.loads(job.stdout)

    old = render()
    before = old["services"]["guard"]
    stage = workdir / ".h6-b2h-preview-reference"
    require(not stage.exists() and not stage.is_symlink(), "preview paths must remain nonexistent")
    require(not any(name == "/" + WRITER_NAME for name in items)
            and all(service.get("container_name") != WRITER_NAME for service in old["services"].values())
            and all((item["Config.Labels"] or {}).get("com.docker.compose.service") != "h6-writer"
                    or (item["Config.Labels"] or {}).get(b.PROJECT_LABEL) != project for item in items.values()), "writer name collision")
    for existing in items.values():
        for entry in existing["Mounts"]:
            path = Path(entry["Source"]).resolve()
            require(not (path.is_relative_to(stage) or stage.is_relative_to(path)), "preview source collision")
    common = [binding(stage / "bundle", SOURCE_TARGET, True), binding(stage / "ipc-key-dir", AUTH_TARGET, True)]
    retained = [item for item in before["volumes"] if item["target"] in (PROVIDER, "/run/secrets/guard_service_token")]
    require(len(retained) == 2 and all(item.get("read_only") for item in retained), "must preserve both approved Guard key mounts")
    proposed_guard = {
        "entrypoint": ["python3", "-B", f"{SOURCE_TARGET}/guard.py"], "user": "0:0",
        "environment": {"TTD_H6_PROVIDER_MODE": "real"},
        "networks": {name: options or {} for name, options in before["networks"].items() if name != "gate_upstream"},
        "volumes": retained + common + [binding(stage / "ipc-dir", IPC_TARGET, True)],
        "tmpfs": before.get("tmpfs", []) + ["/opt/data:rw,noexec,nosuid,nodev,size=8m"],
    }
    require(set(proposed_guard["networks"]) == {"gate_provider", "gateb_guard"}, "Guard renderer unexpectedly changes unrelated networks")
    writer = {
        "image": before["image"], "pull_policy": "never", "container_name": WRITER_NAME, "profiles": ["b2h-preview"],
        "entrypoint": ["python3", "-B", f"{SOURCE_TARGET}/h6_writer.py", "--b2-f-real"],
        "network_mode": "none", "user": "0:0", "read_only": True, "cap_drop": ["ALL"],
        "security_opt": ["no-new-privileges:true"], "pids_limit": 48, "mem_limit": "128m", "cpus": 0.25,
        "tmpfs": ["/opt/data:rw,noexec,nosuid,nodev,size=8m"],
        "volumes": common + [binding(stage / "ipc-dir", IPC_TARGET, False), binding(ledger.parent, WRITER_LEDGER, False)],
    }
    lines = ["services:", "  guard:"]
    for key, value in proposed_guard.items():
        tag = "!override " if key in ("volumes", "networks", "tmpfs") else ""
        lines.append(f"    {key}: {tag}{json.dumps(value)}")
    lines.append(f"  h6-writer: {json.dumps(writer)}")
    overlay = ("\n".join(lines) + "\n").encode()
    new = render(overlay)
    hash_ready = lambda cfg: hashlib.sha256(json.dumps(cfg, sort_keys=True).encode()).hexdigest()
    require(render() == old and render(overlay) == new, "before/after render drift")
    require({key: value for key, value in old.items() if key != "services"} ==
            {key: value for key, value in new.items() if key != "services"}, "top-level resource drift")
    require({key: value for key, value in old["services"].items() if key != "guard"} ==
            {key: value for key, value in new["services"].items() if key not in ("guard", "h6-writer")},
            "unrelated service diff")
    changed = new["services"]["guard"]
    proposed_writer = new["services"]["h6-writer"]
    fields = sorted(key for key in before.keys() | changed.keys() if before.get(key) != changed.get(key))
    require(set(fields) == set(proposed_guard) and set(changed["networks"]) == {"gate_provider", "gateb_guard"}, "Guard diff exceeds allowlist")
    require(not any(proposed_writer.get(key) for key in ("ports", "networks", "env_file", "environment", "secrets", "privileged", "cap_add"))
            and proposed_writer.get("network_mode") == "none" and proposed_writer.get("cap_drop") == ["ALL"]
            and set(changed.get("environment", {})) == {"TTD_H6_PROVIDER_MODE"}
            and changed["environment"]["TTD_H6_PROVIDER_MODE"] == "real" and not changed.get("ports"),
            "proposed security or publish outside scope")
    require(pure_mounts(changed) == pure_mounts(proposed_guard) and pure_mounts(proposed_writer) == pure_mounts(writer),
            "rendered bind source/propagation drift")
    require(all(entry["target"] != LIVE_TARGET and entry.get("read_only") for entry in changed["volumes"]),
            "Guard must have no ledger bind and no writable file mounts")
    require({v["target"] for v in proposed_writer["volumes"] if not v.get("read_only")} == {WRITER_LEDGER, IPC_TARGET},
            "unexpected writer writable boundary")
    require(PROVIDER not in pure_mounts(proposed_writer), "writer sees provider key")
    return {
        "base_source_is_live_h4_layered": True, "before_sha256": hash_ready(old), "after_sha256": hash_ready(new),
        "unchanged_other_services": sorted(set(old["services"]) - {"guard"}),
        "existing_services_changed": ["guard"], "added_service": "h6-writer", "guard_changed_fields": fields,
        "guard_removed_bind_targets": sorted(set(pure_mounts(before)) - set(pure_mounts(changed))),
        "guard_added_bind_targets_ro": sorted(set(pure_mounts(changed)) - set(pure_mounts(before))),
        "guard_kept_ro_credentials": sorted(v["target"] for v in retained),
        "guard_removed_networks": ["gate_upstream"], "guard_kept_networks": sorted(changed["networks"]),
        "writer_uid_gid": proposed_writer["user"], "writer_network": proposed_writer["network_mode"],
        "writer_caps": proposed_writer["cap_drop"], "writer_profile": proposed_writer["profiles"],
        "writer_rw_rprivate_targets": sorted(v["target"] for v in proposed_writer["volumes"] if not v.get("read_only")),
        "writer_ro_targets": sorted(v["target"] for v in proposed_writer["volumes"] if v.get("read_only")),
        "guard_entrypoint": changed["entrypoint"], "writer_entrypoint": proposed_writer["entrypoint"],
        "guard_tmpfs_added": sorted(set(changed.get("tmpfs", [])) - set(before.get("tmpfs", []))),
        "writer_tmpfs": proposed_writer["tmpfs"], "guard_healthcheck_unchanged": changed["healthcheck"] == before["healthcheck"],
        "proxy_service_or_network_definition_changed": False, "new_ports": 0,
        "nonexistent_preview_refs_created": False, "applied": False,
    }


def pure_mounts(service):
    return {item["target"]: (item["source"], item.get("read_only", False), item.get("bind", {}).get("propagation"),
                             item.get("bind", {}).get("create_host_path")) for item in service["volumes"]}


def audit():
    b = load_baseline()
    before = b.inventory()
    items = {entry["Name"]: entry for entry in before["containers"]}
    b.verify_h4(before)
    ledger, lock, provider, old_metadata = resolve_inputs(b, items)
    g, level2, n = (items[name] for name in ("/ttd-gate-a-guard", "/ttd-p0-reasoner", "/ttd-p0-n8n-sandbox"))
    pid = g["State"]["Pid"]
    kernel = Path("/proc") / str(pid)
    child, = (kernel / "task" / str(pid) / "children").read_text().split()
    agent = Path("/proc") / child
    process = dict(line.split(":", 1) for line in (agent / "status").read_text().splitlines())
    security = json.loads(b.docker("info", "--format", "{{json .SecurityOptions}}"))
    production = [{"service": role, "running": entry["State"]["Running"], "restarts": entry["RestartCount"]}
                  for role, prefix in (("n8n", "/n8n-"), ("hermes", "/hermes-agent-"))
                  for entry in items.values() if entry["Name"].startswith(prefix)]
    require(len(production) == 2 and all(item["running"] for item in production), "production inventory drift")
    db_root, = (item["Source"] for item in n["Mounts"] if item["Destination"] == "/home/node/.n8n")
    db = Path(db_root) / ".n8n/database.sqlite"
    require(db.resolve(strict=True) == db and db.is_file(), "unverified sandbox database location")
    n8n = n8n_metadata(db)
    config = {
        "baseline": {"containers": len(before["containers"]), "networks": len(before["networks"]),
                     "production_docker": production, "h4_backup_byte_and_render_equal": True,
                     "guard_compose_config_hash_matches_runtime": True,
                     "leftover_isolated_b2g_containers": sum(name.startswith("/ttd-h6-b2g-") for name in items),
                     "leftover_isolated_b2g_networks": sum(item["Name"].startswith("ttd-h6-b2g-") for item in before["networks"])},
        "ledger": {
            "parent": stat_summary(ledger.parent, old_metadata[0]), "file": stat_summary(ledger, old_metadata[1]),
            "lock": stat_summary(lock, old_metadata[2]), "provider_mount_metadata": stat_summary(provider, old_metadata[3]),
            "ledger_and_lock_share_device_distinct_inode": True, "level2_parent_bind_rw_matches": True,
            "level2_running": level2["State"]["Running"], "level2_restart_policy": level2["HostConfig.RestartPolicy"]["Name"],
            "level2_configured_user": level2["Config.User"] if level2["Config.User"] in ("root", "", "0", "0:0") else "other",
            "guard_file_bind_ro": True, "guard_lock_visible_adjacent": (kernel / "root" / LIVE_TARGET.lstrip("/")).with_suffix(".json.lock").exists(),
            "guard_root_uid_gid": [int(process["Uid"].split()[1]), int(process["Gid"].split()[1])],
            "guard_actual_caps_inh_prm_eff_bnd_amb": [int(process[key], 16) for key in ("CapInh", "CapPrm", "CapEff", "CapBnd", "CapAmb")],
            "guard_no_new_privileges": int(process["NoNewPrivs"]) == 1,
            "guard_and_host_same_userns": os.readlink(agent / "ns/user") == os.readlink("/proc/1/ns/user"),
            "docker_userns_or_rootless": any("rootless" in entry or "userns" in entry for entry in security),
            "guard_only_provider_mount": sum(entry["Destination"] == PROVIDER or entry["Source"] == str(provider)
                                              for item in items.values() for entry in item["Mounts"]) == 1,
        },
        "network": network_matrix(b, items),
        "guard_source_sha256": source(root_source(g, "/opt/ttd/guard.py", True))[1],
        "level2_source_sha256": source(root_source(level2, "/opt/ttd/adapter.py", True))[1],
        "proxy": proxy_metadata(root_source(items["/ttd-p0-provider-egress"], "/opt/ttd/egress_proxy.py", True)),
        "bridge": bridge_metadata(root_source(items["/ttd-gate-a-bridge"], "/opt/ttd/bridge.py", True)),
        "hermes": hermes_metadata(b, items["/ttd-gate-a-hermes"]),
        "sandbox_n8n": n8n | {"wal_present": Path(str(db) + "-wal").is_file()},
    }
    for key, value in config.items():
        print("B2H " + key + " " + json.dumps(value, separators=(",", ":"), sort_keys=True), flush=True)
    config = {"proposed_compose": propose(b, items, ledger)}
    identical = b.inventory() == before and [b.metadata(path) for path in (ledger.parent, ledger, lock, provider)] == old_metadata
    config["pre_post_metadata_and_inventory_equal"] = identical
    require(identical, "live metadata drift")
    return config


if __name__ == "__main__":
    for key, value in audit().items():
        print("B2H " + key + " " + json.dumps(value, separators=(",", ":"), sort_keys=True), flush=True)
