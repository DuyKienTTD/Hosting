"""KVM2-only mock rehearsal. Never mount or read the real ledger or credentials."""

import hashlib
import json
import os
import re
import secrets
import shutil
import stat
import subprocess
import sys
import urllib.request
from pathlib import Path

REPO = "https://raw.githubusercontent.com/DuyKienTTD/Hosting/"
B2_D = "cf36e593f8bf6121f8c8f0ac67078addf9c12ffe"
SOURCE = "sandbox/p0-hermes-gate-a/"
IMAGE = "ghcr.io/hostinger/hvps-hermes-agent@sha256:0ea63377bd672cb76de6a8510aaaef619fe2a045558b771656c072ef527c344f"
LEDGER = "/opt/ttd/mock-ledger"
LIVE_LEDGER = "/opt/ttd/ledger/level2-budget.json"
PROVIDER = "/run/secrets/openai_provider_api_key"
IPC = "/opt/ttd/h6-b2d-ipc"
AUTH = "/run/h6-b2d-auth"
CASES = "/opt/ttd/b2e-cases"
PROJECT_LABEL = "com.docker.compose.project"
OWNER_LABEL = "ttd.h6.b2e.fixture"
SERVICES = {"init", "writer", "guard", "tests"}
VOLUMES = {"ipc": IPC, "auth": AUTH, "test-auth": "/run/h6-b2d-test-auth", "guard-auth": "/run/secrets"}
CODE = {
    "init": {"h6_b2d_mock_test.py", "guard.py", "h6_writer.py", "h6_ipc_auth.py", "one_shot.py", "mock_contract.py"},
    "writer": {"h6_writer.py", "h6_ipc_auth.py", "one_shot.py", "mock_contract.py"},
    "guard": {"guard.py", "h6_writer.py", "h6_ipc_auth.py", "one_shot.py", "mock_contract.py"},
}
EXTRA_TEST_CODE = {"h6_stage_a_test.py", "bridge.py", "one_shot_linux_test.py", "h6_b2e_contract.py"}
CODE["tests"] = CODE["init"] | EXTRA_TEST_CODE


def need(condition, message):
    if not condition:
        raise RuntimeError(message)


def docker(*args, env=None, output=True, timeout=65):
    command_env = {"PATH": "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin", "HOME": "/nonexistent"}
    command_env.update(env or {})
    job = subprocess.run(["docker", *map(str, args)], stdout=subprocess.PIPE if output else None,
                         stderr=subprocess.PIPE if output else None, env=command_env, timeout=timeout, check=False)
    need(job.returncode == 0, f"docker {args[0]} failed (exit {job.returncode})")
    return job.stdout


def inspect_fields(kind, ids, fields):
    if not ids:
        return []
    template = "\t".join(
        '{{with index .State "Health"}}{{json .Status}}{{else}}null{{end}}' if field == "Health"
        else "{{json ." + field + "}}" for field in fields)
    return [dict(zip(fields, map(json.loads, line.split("\t")), strict=True))
            for line in docker(kind, "inspect", "--format", template, *ids).decode().splitlines()]


def inventory():
    containers = inspect_fields("container", docker("ps", "-aq", "--no-trunc").decode().splitlines(),
                                ("Id", "Name", "Config.Labels", "Config.User", "Image", "State.Status", "State.Running",
                                 "State.StartedAt", "State.Pid", "Health", "RestartCount",
                                 "Mounts", "HostConfig.PortBindings", "HostConfig.RestartPolicy",
                                 "HostConfig.NetworkMode", "NetworkSettings.Ports", "NetworkSettings.Networks"))
    # Select stable state fields without asking Docker for health logs or runtime environment.
    for container in containers:
        container["State"] = {k: container.pop("State." + k) for k in ("Status", "Running", "StartedAt", "Pid")}
    networks = inspect_fields("network", docker("network", "ls", "-q", "--no-trunc").decode().splitlines(),
                              ("Id", "Name", "Labels", "Containers"))
    return {key: sorted(rows, key=lambda row: row["Id"]) for key, rows in
            (("containers", containers), ("networks", networks))} | {
                "volume_names": sorted(docker("volume", "ls", "-q").decode().splitlines())}


def metadata(path):
    value = path.lstat()
    acl = {name: os.getxattr(path, name) for name in os.listxattr(path) if name.startswith("system.posix_acl_")}
    return (value.st_dev, value.st_ino, value.st_mode, value.st_uid, value.st_gid, value.st_nlink,
            value.st_mtime_ns, value.st_ctime_ns, value.st_size, acl)


def production_health(containers):
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    statuses = []
    for prefix, endpoint in (("/n8n-", "/healthz"), ("/hermes-agent-", "/api/health")):
        matches = [item for item in containers if item["Name"].startswith(prefix)]
        need(len(matches) == 1 and matches[0]["State"]["Running"], "production service identity/state")
        ports = {item["HostPort"] for mapping in (matches[0]["NetworkSettings.Ports"] or {}).values()
                 for item in (mapping or [])}
        need(len(ports) == 1, "ambiguous production health port")
        with opener.open(f"http://127.0.0.1:{ports.pop()}{endpoint}", timeout=5) as reply:
            statuses.append(reply.status)
    need(statuses == [200, 200], "production health drift")
    return statuses


def baseline():
    existing = inventory()
    named = {item["Name"]: item for item in existing["containers"]}
    guard = named["/ttd-gate-a-guard"]
    for name in ("guard", "bridge", "hermes", "provider-mock"):
        item = named[f"/ttd-gate-a-{name}"]
        need(item["State"]["Running"] and item["Health"] in (None, "healthy") and item["RestartCount"] == 0,
             "GATE A baseline drift")
    ledger_mount, = (item for item in guard["Mounts"] if item["Destination"] == LIVE_LEDGER)
    live = Path(ledger_mount["Source"])
    lock = live.with_suffix(".json.lock")
    need(ledger_mount["Type"] == "bind" and not ledger_mount["RW"] and live.resolve(strict=True) == live,
         "real ledger bind drift")
    ledger_metadata = [metadata(path) for path in (live, lock, live.parent)]
    for value, mode in zip(ledger_metadata, (stat.S_IFREG | 0o600, stat.S_IFREG | 0o600, stat.S_IFDIR | 0o700), strict=True):
        need(value[2:5] == (mode, 0, 0) and not value[-1], "real ledger owner/mode/ACL drift")
    need(ledger_metadata[0][0] == ledger_metadata[1][0] and ledger_metadata[0][1] != ledger_metadata[1][1],
         "real lock identity drift")
    level2 = named["/ttd-p0-reasoner"]
    need(not level2["State"]["Running"] and level2["Config.User"] in ("", "root", "0", "0:0")
         and level2["HostConfig.RestartPolicy"]["Name"] == "unless-stopped"
         and any(m["RW"] and Path(m["Source"]) == live.parent for m in level2["Mounts"]), "Level 2 mount/state drift")
    provider_mounts = [(item["Name"], mount) for item in existing["containers"] for mount in item["Mounts"]
                       if mount["Destination"] == PROVIDER]
    need(len(provider_mounts) == 1 and provider_mounts[0][0] == guard["Name"] and not provider_mounts[0][1]["RW"],
         "existing provider mount drift")
    options = json.loads(docker("info", "--format", "{{json .SecurityOptions}}"))
    need(not any("rootless" in entry or "userns" in entry for entry in options), "Docker identity mapping drift")
    return existing | {"ledger_metadata": ledger_metadata, "production_health": production_health(existing["containers"])}


def verify_h4(before):
    guard = next(c for c in before["containers"] if c["Name"] == "/ttd-gate-a-guard")
    labels = guard["Config.Labels"]
    live = Path(labels["com.docker.compose.project.working_dir"]).resolve(strict=True)
    names = ("compose.yaml", "compose.h4-provider-secret.yaml")
    config = tuple(live / name for name in names)
    need(tuple(Path(name) for name in labels["com.docker.compose.project.config_files"].split(",")) == config,
         "H4 active Compose source drift")
    candidates = [item for item in live.parent.glob("guard-mount-run.*") if item.is_dir() and not item.is_symlink()
                  and item.stat().st_uid == 0 and stat.S_IMODE(item.stat().st_mode) == 0o700
                  and all((item / name).is_file() and not (item / name).is_symlink() for name in names)]
    backups = [tuple(item / name for name in names) for item in candidates
               if all((item / name).read_bytes() == path.read_bytes() for name, path in zip(names, config, strict=True))]
    need(len(backups) == 1, "H4 rollback backup missing, changed or ambiguous")

    def render(paths, *options):
        return docker("compose", "--env-file", "/dev/null", "--project-directory", live, "-p", labels[PROJECT_LABEL],
                      "-f", paths[0], "-f", paths[1], "config", *options)

    need(json.loads(render(config, "--format", "json")) == json.loads(render(backups[0], "--format", "json")),
         "H4 rollback renders differently")
    current_hash = render(config, "--hash", "guard").decode().split()
    need(current_hash == ["guard", labels["com.docker.compose.config-hash"]], "H4 runtime config hash drift")
    print("PASS B2E H4: two backup files byte-identical, render equal, Guard runtime hash matches", flush=True)


def download(commit, path):
    with urllib.request.urlopen(f"{REPO}{commit}/{path}", timeout=15) as response:
        return response.read(512 * 1024 + 1)


def blob(raw):
    return hashlib.sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest()


def stage_sources(root, runner_commit, callback_blob):
    manifest = json.loads(download(B2_D, "reports/evidence/2026-11-22-ttd-hermes-gate-b-h6-b2-d-ipc-integration.json"))
    need(manifest["result"] == "H6_B2_D_CODE_MOCK_PASS", "B2-D pinned manifest")
    sources = set().union(*CODE.values()) | {"compose.h6-b2-d-mock.yaml"}
    for name in sorted(sources | {"level2-adapter.py"}):
        remote = SOURCE + name
        if name == "level2-adapter.py":
            remote = "sandbox/p0-level2/adapter.py"
        commit = runner_commit if name == "h6_b2e_contract.py" else B2_D
        expected = callback_blob if commit == runner_commit else manifest["source_blobs"].get(remote)
        if not expected:
            expected = LEGACY_BLOBS[name]
        raw = download(commit, remote)
        need(blob(raw) == expected, f"source SHA mismatch: {name}")
        if name == "level2-adapter.py":
            adapter = root / "src" / "sandbox" / "p0-level2"
            adapter.mkdir(parents=True, exist_ok=True)
            (adapter / "adapter.py").write_bytes(raw)
        else:
            (root / "src" / SOURCE / name).write_bytes(raw)
    print(f"PASS B2E source: {len(sources) + 1} pinned Git blobs", flush=True)


LEGACY_BLOBS = {
    "mock_contract.py": "d58d0bcf89bd557c313606d5908817f45ccd0129",
    "h6_stage_a_test.py": "298e19774cbbb045558e2406bc0b2cb5a6bc5062",
    "bridge.py": "191c670c84683deadfe0107f09463aca593ba700",
    "one_shot_linux_test.py": "2530525131812b823538e5b0f27b34d3b0f9929d",
}


def compose(root, project, file, *args, **kwargs):
    return docker("compose", "--env-file", "/dev/null", "--project-directory", root / "src" / SOURCE,
                  "-p", project, "--profile", "*", "-f", file, *args, **kwargs)


def candidate(root, project):
    path = root / "src" / SOURCE / "compose.h6-b2-d-mock.yaml"
    base = json.loads(compose(root, project, path, "config", "--format", "json",
                              env={"TTD_H6_B2_D_FAKE_LEDGER": str(root / "mock-ledger")}))
    cfg = {key: val for key, val in base.items() if not key.startswith("x-")}
    need(set(cfg) == {"name", "services", "volumes"} and set(cfg["services"]) == SERVICES, "unexpected pinned Compose shape")
    for service in cfg["services"].values():
        service["image"] = IMAGE
        service["entrypoint"] = ["python3", "-B"]
        service["command"] = service["command"][2:]
        service["tmpfs"] = [*service.get("tmpfs", []), "/opt/data:rw,noexec,nosuid,nodev,size=8m"]
        service["labels"] = {OWNER_LABEL: project}
        if "healthcheck" in service:
            service["healthcheck"]["test"][1] = "python3"
    for volume in cfg["volumes"].values():
        volume["labels"] = {OWNER_LABEL: project}
    test = cfg["services"]["tests"]
    test["command"] = ["/opt/ttd/h6_b2e_contract.py"]
    for file in sorted(EXTRA_TEST_CODE):
        test["volumes"].append({"type": "bind", "source": str(root / "src" / SOURCE / file),
                                "target": f"/opt/ttd/{file}", "read_only": True, "bind": {"create_host_path": False}})
    test["volumes"].append({"type": "bind", "source": str(root / "cases"), "target": CASES,
                            "bind": {"create_host_path": False, "propagation": "rprivate"}})
    output = root / "compose.json"
    output.write_text(json.dumps(cfg), encoding="utf-8")
    return output


def mount_plan(root, project, cfg, before):
    need(set(cfg) == {"name", "services", "volumes"} and cfg["name"] == project
         and set(cfg["services"]) == SERVICES and set(cfg["volumes"]) == set(VOLUMES), "unexpected rendered resources")
    image, = inspect_fields("image", [IMAGE], ("Id", "Config.Volumes", "Config.Env", "Config.User"))
    need(image["Config.Volumes"] == {"/opt/data": {}} and not any(
        any(term in entry.partition("=")[0].upper() for term in ("API_KEY", "TOKEN", "PROXY", "PASSWORD"))
        and entry.partition("=")[2] for entry in image["Config.Env"]), "cached image isolation")
    rw = {
        "init": {LEDGER, IPC, AUTH, "/run/h6-b2d-test-auth", "/run/secrets"},
        "writer": {LEDGER, IPC},
        "guard": set(),
        "tests": {CASES},
    }
    shares = {"init": dict(VOLUMES), "writer": {"ipc": IPC, "auth": AUTH},
              "guard": {"ipc": IPC, "auth": AUTH, "guard-auth": "/run/secrets"}, "tests": {"test-auth": AUTH}}
    commands = {"init": ["/opt/ttd/h6_b2d_mock_test.py", "init"],
                "writer": ["/opt/ttd/h6_writer.py", "--b2-d-mock"], "guard": ["/opt/ttd/guard.py"],
                "tests": ["/opt/ttd/h6_b2e_contract.py"]}
    for name, volume in cfg["volumes"].items():
        need(set(volume) == {"name", "labels"} and volume["name"] == f"{project}_{name}"
             and volume["labels"] == {OWNER_LABEL: project}, "unexpected volume/rendered external mount")
    allowed = {"image", "pull_policy", "user", "network_mode", "cap_drop", "read_only", "security_opt", "pids_limit",
               "entrypoint", "command", "volumes", "healthcheck", "environment", "tmpfs", "labels"}
    mounts = {}
    for name, item in cfg["services"].items():
        need(set(item) <= allowed and item["image"] == IMAGE and item["pull_policy"] == "never"
             and item["network_mode"] == "none" and item["user"] == "0:0" and item["cap_drop"] == ["ALL"]
             and item["read_only"] and item["security_opt"] == ["no-new-privileges:true"] and item["pids_limit"] == 48
             and item["command"] == commands[name] and item["entrypoint"] == ["python3", "-B"]
             and item["labels"] == {OWNER_LABEL: project}, "unsafe rendered service")
        env = {"TTD_H6_B2_D_SOCKET": f"{IPC}/writer.sock"} if name == "guard" else {}
        need(item.get("environment", {}) == env, "unexpected environment or credential")
        expected_tmpfs = {"/opt/data:rw,noexec,nosuid,nodev,size=8m"}
        if name == "tests":
            expected_tmpfs.add("/tmp:rw,noexec,nosuid,nodev,mode=0700,size=16m")
        need(set(item["tmpfs"]) == expected_tmpfs, "unsafe tmpfs targets")
        health = item.get("healthcheck", {}).get("test", [])
        target = {"guard": "127.0.0.1:8081/healthz", "writer": f"{IPC}/writer.sock"}.get(name)
        need((len(health) == 5 and health[:4] == ["CMD", "python3", "-B", "-c"] and target in health[4])
             if target else not health, "unexpected healthcheck")
        expected = {f"/opt/ttd/{file}": ("bind", str(root / "src" / SOURCE / file)) for file in CODE[name]}
        expected.update({target: ("volume", volume) for volume, target in shares[name].items()})
        if name in ("init", "writer"):
            expected[LEDGER] = ("bind", str(root / "mock-ledger"))
        if name == "tests":
            expected["/opt/ttd/level2-adapter.py"] = ("bind", str(root / "src/sandbox/p0-level2/adapter.py"))
            expected[CASES] = ("bind", str(root / "cases"))
        seen = {}
        for mount in item["volumes"]:
            destination = mount["target"]
            need(destination not in seen and expected.get(destination) == (mount["type"], mount["source"])
                 and mount.get("read_only", False) == (destination not in rw[name]), "unexpected rendered mount")
            if mount["type"] == "bind":
                source = Path(mount["source"])
                need(source.resolve(strict=True) == source and source.is_relative_to(root), "bind escapes fixture")
                if destination in (LEDGER, CASES):
                    need(mount["bind"] == {"create_host_path": False, "propagation": "rprivate"}, "unsafe bind propagation")
            seen[destination] = mount
        need(set(seen) == set(expected), "incomplete rendered mounts")
        mounts[name] = seen
    need(not any(item["Name"].startswith(f"/{project}-") or (item["Config.Labels"] or {}).get(PROJECT_LABEL) == project
                 for item in before["containers"]), "container collision")
    need(not any(item["Name"].startswith(f"{project}_") for item in before["networks"])
         and not any(item.startswith(f"{project}_") for item in before["volume_names"]), "network/volume collision")
    for container in before["containers"]:
        for mount in container["Mounts"]:
            source = Path(mount["Source"]).resolve()
            need(not (source.is_relative_to(root) or root.is_relative_to(source)), "overlap with existing mount")
    return image["Id"], mounts


def verify_services(root, project, file, image, mounts):
    for service in ("writer", "guard"):
        cid = compose(root, project, file, "ps", "-q", service).decode().strip()
        info, = inspect_fields("container", [cid], ("Id", "Name", "Config.Labels", "Config.User", "Image", "Mounts",
            "HostConfig.NetworkMode", "HostConfig.ReadonlyRootfs", "HostConfig.SecurityOpt", "HostConfig.CapDrop",
            "HostConfig.PortBindings", "HostConfig.Tmpfs", "State.Pid", "State.Health.Status", "NetworkSettings.Networks"))
        need(info["Name"] == f"/{project}-{service}-1" and info["Image"] == image
             and info["Config.Labels"].get(OWNER_LABEL) == project and info["Config.User"] == "0:0"
             and info["HostConfig.NetworkMode"] == "none" and info["HostConfig.ReadonlyRootfs"]
             and info["HostConfig.CapDrop"] == ["ALL"] and info["HostConfig.SecurityOpt"] == ["no-new-privileges:true"]
             and not info["HostConfig.PortBindings"] and set(info["NetworkSettings.Networks"]) <= {"none"}
             and set(info["HostConfig.Tmpfs"]) == {"/opt/data"} and info["State.Health.Status"] == "healthy",
             "runtime isolation differs from render")
        actual = {m["Destination"]: m for m in info["Mounts"] if m["Type"] != "tmpfs"}
        need(set(actual) == set(mounts[service]), "runtime mount set differs from render")
        for target, plan in mounts[service].items():
            item = actual[target]
            correct = item["Name"] == f"{project}_{plan['source']}" if plan["type"] == "volume" else item["Source"] == plan["source"]
            need(correct and item["Type"] == plan["type"] and item["RW"] != plan.get("read_only", False)
                 and item["Propagation"] in ("", "rprivate"), "runtime mount differs from render")
        proc = Path("/proc") / str(info["State.Pid"])
        status = dict(line.split(":", 1) for line in (proc / "status").read_text().splitlines())
        need(all(int(status[key], 16) == 0 for key in ("CapEff", "CapPrm", "CapInh", "CapBnd", "CapAmb"))
             and int(status["NoNewPrivs"]) == 1 and status["Uid"].split() == ["0"] * 4
             and status["Gid"].split() == ["0"] * 4, "actual UID/caps drift")
        need(not any(line.split()[1] == "00000000" for line in (proc / "net/route").read_text().splitlines()[1:]),
             "unexpected default route")
        # Resolve absolute symlinks such as /var/run inside the container mount
        # namespace. Host-side stat through /proc/<pid>/root may follow /run on the host.
        docker("exec", cid, "python3", "-B", "-c", NO_BYPASS, service)
        if service == "writer":
            mount_line = next(line for line in (proc / "mountinfo").read_text().splitlines() if line.split()[4] == LEDGER)
            need(mount_line.split(" - ")[1].split()[0] == "ext4" and actual[LEDGER]["Propagation"] == "rprivate",
                 "writer is not using the isolated rprivate ext4 bind")
    print("PASS B2E runtime: root caps=0, NNP, RO rootfs, ext4 rprivate, RO key, no routes or sensitive mounts", flush=True)


NO_BYPASS = """
import os, sys
from pathlib import Path
assert {p.name for p in Path('/sys/class/net').iterdir()} == {'lo'}
assert not any(os.path.lexists(p) for p in (
    '/run/secrets/openai_provider_api_key', '/opt/ttd/ledger/level2-budget.json',
    '/var/run/docker.sock', '/run/docker.sock'))
assert os.statvfs('/').f_flag & os.ST_RDONLY
assert os.statvfs('/run/h6-b2d-auth').f_flag & os.ST_RDONLY
if sys.argv[1] == 'guard':
    assert os.statvfs('/opt/ttd/h6-b2d-ipc').f_flag & os.ST_RDONLY
    assert not Path('/opt/ttd/mock-ledger').exists()
else:
    assert not Path('/run/secrets/guard_service_token').exists()
"""


GUARD_PROBE = """
import json, urllib.request
from pathlib import Path
from h6_ipc_auth import KEY_PATH, SOCKET_PATH
assert {p.name for p in Path('/sys/class/net').iterdir()} == {'lo'}
assert not Path('/opt/ttd/mock-ledger').exists()
assert SOCKET_PATH.stat().st_mode & 0o777 == 0o600
assert KEY_PATH.stat().st_mode & 0o777 == 0o400
with urllib.request.urlopen('http://127.0.0.1:8081/healthz', timeout=3) as response:
    status = json.load(response)
assert status['mode'] == 'h6_b2_d_mock' and status['ledger']['kill_switch']
"""
WRONG_PEER = """
import os, socket, time
from h6_ipc_auth import KEY_PATH, SOCKET_PATH, send
assert (os.getuid(), os.getgid()) == (0, 23060) and KEY_PATH.stat().st_size == 32
with socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET) as conn:
    conn.settimeout(2)
    conn.connect(str(SOCKET_PATH))
    try:
        send(conn, time.monotonic() + 2, client=os.urandom(32).hex())
        assert conn.recv(4097) == b''
    except (BrokenPipeError, ConnectionResetError):
        pass
"""


def remove_owned(root, project, before):
    before_ids = {item["Id"] for item in before["containers"]}
    current = inventory()
    owned = [item for item in current["containers"] if (item["Config.Labels"] or {}).get(PROJECT_LABEL) == project]
    for item in owned:
        name = item["Name"].removeprefix("/")
        service = item["Config.Labels"].get("com.docker.compose.service")
        need(item["Id"] not in before_ids and item["Config.Labels"].get(OWNER_LABEL) == project and service in SERVICES
             and re.fullmatch(f"{project}-{service}-(1|run-[0-9a-f]+)", name), "cannot prove container belongs to B2-E")
        for mount in item["Mounts"]:
            valid = (Path(mount["Source"]).is_relative_to(root) if mount["Type"] == "bind" else
                     mount["Name"] in {f"{project}_{key}" for key in VOLUMES} if mount["Type"] == "volume" else
                     mount["Type"] == "tmpfs" and mount["Destination"] in ("/opt/data", "/tmp"))
            need(valid, "unexpected persistent mount in cleanup")
    if owned:
        docker("rm", "-f", *(item["Id"] for item in owned))
    expected = {f"{project}_{name}" for name in VOLUMES}
    volumes = expected & set(current["volume_names"])
    need(not (volumes & set(before["volume_names"])), "refusing to remove preexisting volume")
    for item in inspect_fields("volume", sorted(volumes), ("Name", "Labels", "Driver")):
        need(item["Labels"].get(PROJECT_LABEL) == project and item["Labels"].get(OWNER_LABEL) == project
             and item["Driver"] == "local", "cannot prove volume belongs to B2-E")
        docker("volume", "rm", item["Name"])
    need(not any(item["Name"].startswith(f"{project}_") for item in current["networks"]), "unexpected project network")
    after = baseline()
    need(after == before, "pre/post Docker or real-ledger metadata drift")
    need(root.parent == Path("/var/tmp") and root.name == project and root.resolve(strict=True) == root,
         "fixture cleanup path is not proven")
    shutil.rmtree(root)
    need(not root.exists(), "fixture directory remains")
    print("PASS B2E rollback: zero owned resources; GATE A and production unchanged; HTTP 200/200; real ledger/lock metadata unchanged", flush=True)


def run(commit, callback_blob, mode="run"):
    need(os.geteuid() == 0 and re.fullmatch(r"[0-9a-f]{40}", commit)
         and re.fullmatch(r"[0-9a-f]{40}", callback_blob) and mode in ("run", "plan"), "KVM2 runner inputs")
    before = baseline()
    verify_h4(before)
    print("PASS B2E baseline: real root:root 0700/0600 without ACL; Level 2 stopped; production HTTP 200/200", flush=True)
    project = "ttd-h6-b2e-" + secrets.token_hex(6)
    root = Path("/var/tmp") / project
    root.mkdir(mode=0o700)
    try:
        (root / "src" / SOURCE).mkdir(parents=True)
        (root / "mock-ledger").mkdir(mode=0o700)
        (root / "cases").mkdir(mode=0o700)
        stage_sources(root, commit, callback_blob)
        file = candidate(root, project)
        render = compose(root, project, file, "config", "--format", "json")
        image, mounts = mount_plan(root, project, json.loads(render), before)
        need(inventory() == {key: before[key] for key in ("containers", "networks", "volume_names")}
             and render == compose(root, project, file, "config", "--format", "json"), "pre-up render or inventory drift")
        print(f"PASS B2E PRE_UP: 4 services, 4 private volumes, 0 networks, 0 collisions; render sha256={hashlib.sha256(render).hexdigest()}",
              flush=True)
        if mode == "plan":
            return
        compose(root, project, file, "run", "--rm", "--no-deps", "-T", "init", output=False)
        compose(root, project, file, "up", "-d", "--wait", "--no-deps", "writer", output=False)
        compose(root, project, file, "up", "-d", "--wait", "--no-deps", "guard", output=False)
        verify_services(root, project, file, image, mounts)
        compose(root, project, file, "exec", "-T", "-w", "/opt/ttd", "guard", "python3", "-B", "-c", GUARD_PROBE)
        compose(root, project, file, "exec", "-T", "--user", "0:23060", "-w", "/opt/ttd",
                "guard", "python3", "-B", "-c", WRONG_PEER)
        print("PASS B2E signed Guard snapshot and wrong GID rejection (key file accessible)", flush=True)
        compose(root, project, file, "run", "--rm", "--no-deps", "-T", "tests", output=False, timeout=120)
    finally:
        remove_owned(root, project, before)
    print("H6_B2_E_KVM2_MOCK_PASS", flush=True)


if __name__ == "__main__":
    run(*sys.argv[1:])
