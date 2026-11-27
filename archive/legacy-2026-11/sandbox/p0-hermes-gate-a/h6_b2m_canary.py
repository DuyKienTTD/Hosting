"""One dedicated KVM2 fake startup canary. Protected state is inspected by metadata only."""

from datetime import datetime, timedelta, timezone
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import secrets
import shutil
import signal
import socket
import stat
import subprocess
import sys
import time
import types
import urllib.request


PROJECT = "h6-b2-m-idle-canary"
NAME = PROJECT + "-writer"
OWNER_LABEL = "ttd.h6.b2m.owner"
PROJECT_LABEL = "com.docker.compose.project"
SOURCE = "sandbox/p0-hermes-gate-a/"
REPO = "https://raw.githubusercontent.com/DuyKienTTD/Hosting/"
IMAGE = "ghcr.io/hostinger/hvps-hermes-agent@sha256:0ea63377bd672cb76de6a8510aaaef619fe2a045558b771656c072ef527c344f"
B2E = "d32aff15fee7972d217e2f8c8a1f81fa5f987906"
B2L = "c4d540289329a3c71d4ded66f5aca248923bbdcf"
RUNTIME = {
    "h6_b2l_idle.py": "b994d00a550033c9ec163d90cfefd3251de57eee",
    "h6_writer.py": "98ce2e7c6d4109b004da058c49075e4c58411f1f",
    "h6_ipc_auth.py": "afa3f761189d36e87372596f31ea8c8eca38636d",
    "h6_p0.py": "8c0363498b180106c6220ce234dbeb614eb763b1",
    "one_shot.py": "3abbf97ace9473d2f79f728792a8d7111a293f4f",
    "mock_contract.py": "d58d0bcf89bd557c313606d5908817f45ccd0129",
}
FIXTURE_TARGET = "/tmp/h6-b2l-canary"
TMPFS = "/opt/data:rw,nosuid,nodev,noexec,size=8m"
ENTRYPOINT = ["python3", "-B", "/opt/b2m-src/h6_writer.py", "--b2-l-startup-fixture", FIXTURE_TARGET]
ENV = {"PATH": "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin", "HOME": "/nonexistent"}


def need(condition, detail):
    if not condition:
        raise RuntimeError(detail)


def report(label, value):
    print("B2M_" + label, json.dumps(value, sort_keys=True), flush=True)


def fetch(commit, name, blob):
    with urllib.request.urlopen(REPO + commit + "/" + SOURCE + name, timeout=15) as response:
        data = response.read(512 * 1024 + 1)
    actual = hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()
    need(len(data) <= 512 * 1024 and actual == blob, "pinned Git source mismatch")
    return data


def baseline_tool():
    raw = fetch(B2E, "h6_b2e_rehearsal.py", "dcb891284f44763480f4b6675960836fa9d2f64e")
    module = types.ModuleType("verified_b2e_inventory")
    exec(compile(raw, "pinned-b2e-inventory", "exec"), module.__dict__)
    return module


def compose(spec, root, owner, *args):
    call = ["docker", "compose", "--env-file", "/dev/null", "--project-directory", "/var/tmp",
            "-p", PROJECT, "--profile", "*", "-f", "-", *args]
    job = subprocess.run(call, input=spec, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         env=ENV | {"B2M_ROOT": str(root), "B2M_OWNER": owner}, timeout=45)
    need(job.returncode == 0, f"Compose {args[0]} returned {job.returncode}")
    return job.stdout


def mount_plan(root):
    return {
        "/opt/b2m-src": (str(root / "src"), True),
        FIXTURE_TARGET: (str(root / "fixture"), True),
        FIXTURE_TARGET + "/ipc": (str(root / "fixture" / "ipc"), False),
    }


def no_collision(before, root):
    need(not os.path.lexists(root) and not any(PROJECT in item for item in before["volume_names"]),
         "canary directory or volume collision")
    for network in before["networks"]:
        need(not network["Name"].startswith(PROJECT)
             and (network["Labels"] or {}).get(PROJECT_LABEL) != PROJECT, "canary network collision")
    for item in before["containers"]:
        need(not item["Name"].startswith("/" + PROJECT)
             and (item["Config.Labels"] or {}).get(PROJECT_LABEL) != PROJECT, "canary container collision")
        for mount in item["Mounts"]:
            source = mount.get("Source")
            if source and source.startswith("/"):
                path = Path(source).resolve()
                need(not root.is_relative_to(path) and not path.is_relative_to(root), "canary bind overlaps live mount")


def check_render(raw, root, owner):
    config = json.loads(raw)
    need(config.keys() == {"name", "services"} and config["name"] == PROJECT
         and config["services"].keys() == {"writer"}, "unexpected resource in rendered project")
    item = config["services"]["writer"]
    allowed = {"profiles", "image", "pull_policy", "container_name", "user", "read_only", "network_mode",
               "cap_drop", "security_opt", "pids_limit", "mem_limit", "restart", "entrypoint", "command",
               "healthcheck", "labels", "tmpfs", "volumes"}
    expected = {"profiles": ["canary"], "image": IMAGE, "pull_policy": "never", "container_name": NAME,
                "user": "0:0", "read_only": True, "network_mode": "none", "cap_drop": ["ALL"],
                "security_opt": ["no-new-privileges:true"], "pids_limit": 24, "mem_limit": "100663296",
                "restart": "no", "entrypoint": ENTRYPOINT, "command": [], "healthcheck": {"disable": True},
                "labels": {OWNER_LABEL: owner}, "tmpfs": [TMPFS]}
    need(set(item) == allowed and all(
        str(item[key]) == value if key == "mem_limit" else item[key] == value
        for key, value in expected.items()), "rendered writer security or resource bounds changed")
    mounts = item["volumes"]
    need(len(mounts) == 3 and all(
        set(mount) <= {"type", "source", "target", "read_only", "bind"} and mount["type"] == "bind"
        and mount["bind"] == {"create_host_path": False, "propagation": "rprivate"} for mount in mounts),
        "unexpected rendered mount flags")
    need({mount["target"]: (mount["source"], mount.get("read_only", False)) for mount in mounts}
         == mount_plan(root), "rendered mount source/target crossed boundary")
    sanitized = json.dumps(config, sort_keys=True).replace(str(root), "<owned-root>").replace(owner, "<owner>")
    return hashlib.sha256(sanitized.encode()).hexdigest()


def write_new(path, raw, mode):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, mode)
    with os.fdopen(fd, "wb") as stream:
        stream.write(raw)


def stage(root, code):
    for piece in ("src", "fixture", "fixture/mock-ledger", "fixture/ipc"):
        (root / piece).mkdir(mode=0o700)
    for name, raw in code.items():
        write_new(root / "src" / name, raw, 0o400)
    sys.path.insert(0, str(root / "src"))
    import h6_b2l_idle as idle
    import h6_ipc_auth as ipc
    import h6_p0 as p0
    import one_shot
    from mock_contract import encode

    fixture = root / "fixture"
    ledger = fixture / "mock-ledger" / idle.LEDGER
    lock = ledger.with_suffix(".json.lock")
    key = secrets.token_bytes(32)
    write_new(fixture / "synthetic-ipc.key", key, 0o400)
    now = datetime.now(timezone.utc)
    budget = {"attempts": 1, "reserved_usd": 0.0035, "actual_usd": 0}
    record = {**budget, idle.MARKER: True, "kill_switch": True, "schema_version": 1,
              "model": one_shot.MODEL, "caps_usd": one_shot.CAPS, "max_calls": one_shot.MAX_CALLS,
              "days": {now.date().isoformat(): budget}, "tasks": {}, "one_shot_permits": {}}
    write_new(ledger, encode(record), 0o600)
    write_new(lock, b"", 0o600)
    one_shot.require_root_layout(ledger)
    return types.SimpleNamespace(idle=idle, ipc=ipc, p0=p0, one_shot=one_shot, key=key,
                                 ledger=ledger, lock=lock, record=record, fixture=fixture,
                                 address=fixture / "ipc" / "writer.sock")


def owned_ids(tool, owner):
    ids = tool.docker("ps", "-aq", "--no-trunc", "--filter", f"label={PROJECT_LABEL}={PROJECT}").decode().splitlines()
    rows = tool.inspect_fields("container", ids, ("Id", "Name", "Config.Labels"))
    need(len(rows) <= 1 and all(
        row["Name"] == "/" + NAME and row["Config.Labels"].get(OWNER_LABEL) == owner
        and row["Config.Labels"].get("com.docker.compose.service") == "writer" for row in rows),
        "refuse to operate on unowned project container")
    return ids


def check_running(tool, container, root, image_id):
    fields = ("Image", "State.Running", "State.StartedAt", "Config.User", "Config.Entrypoint", "Config.Cmd", "Mounts",
              "HostConfig.ReadonlyRootfs", "HostConfig.NetworkMode", "HostConfig.Privileged", "HostConfig.CapAdd",
              "HostConfig.CapDrop", "HostConfig.SecurityOpt", "HostConfig.PortBindings", "HostConfig.Tmpfs",
              "HostConfig.PidsLimit", "HostConfig.Memory", "HostConfig.RestartPolicy",
              "NetworkSettings.Ports", "NetworkSettings.Networks")
    item, = tool.inspect_fields("container", [container], fields)
    need(item["Image"] == image_id and item["State.Running"] and item["Config.User"] == "0:0"
         and item["Config.Entrypoint"] == ENTRYPOINT and not item["Config.Cmd"] and item["HostConfig.ReadonlyRootfs"]
         and item["HostConfig.NetworkMode"] == "none" and not item["HostConfig.Privileged"]
         and not item["HostConfig.CapAdd"] and item["HostConfig.CapDrop"] == ["ALL"]
         and item["HostConfig.SecurityOpt"] == ["no-new-privileges:true"] and not item["HostConfig.PortBindings"]
         and not any((item["NetworkSettings.Ports"] or {}).values())
         and set(item["NetworkSettings.Networks"]) <= {"none"}
         and item["HostConfig.PidsLimit"] == 24 and item["HostConfig.Memory"] == 100663296
         and item["HostConfig.RestartPolicy"]["Name"] == "no"
         and item["HostConfig.Tmpfs"] == {"/opt/data": TMPFS.partition(":")[2]},
         "running writer security posture differs from render")
    binds = [mount for mount in item["Mounts"] if mount["Type"] == "bind"]
    need(len(binds) == 3 and all(mount["Propagation"] == "rprivate" for mount in binds)
         and {m["Destination"]: (m["Source"], not m["RW"]) for m in binds} == mount_plan(root)
         and all(mount["Type"] == "bind" or (mount["Type"] == "tmpfs" and mount["Destination"] == "/opt/data")
                 for mount in item["Mounts"]), "unexpected effective mount")
    script = """import json,os
v=dict(line.split(':',1) for line in open('/proc/1/status'))
def ro(path): return bool(os.statvfs(path).f_flag & os.ST_RDONLY)
print(json.dumps([os.getuid(),os.getgid(),sorted(os.listdir('/sys/class/net')),
all(int(v[x],16)==0 for x in ('CapInh','CapPrm','CapEff','CapBnd','CapAmb')),
int(v['NoNewPrivs']),ro('/'),ro('/opt/b2m-src'),ro('/tmp/h6-b2l-canary/mock-ledger'),
ro('/tmp/h6-b2l-canary/synthetic-ipc.key'),ro('/tmp/h6-b2l-canary/ipc')]))"""
    actual = json.loads(tool.docker("exec", container, "python3", "-B", "-c", script))
    need(actual == [0, 0, ["lo"], True, 1, True, True, True, True, False], "kernel writer posture differs")
    return item["State.StartedAt"]


def immutable(fixture):
    def info(path):
        s = path.lstat()
        return (s.st_dev, s.st_ino, s.st_atime_ns, s.st_mtime_ns, s.st_ctime_ns, s.st_mode, s.st_uid, s.st_gid)
    fd = os.open(fixture.ledger, os.O_RDONLY | os.O_NOFOLLOW | os.O_NOATIME)
    with os.fdopen(fd, "rb") as stream:
        data = stream.read(1024 * 1024 + 1)
    return data, info(fixture.ledger), info(fixture.lock)


def expect(fixture, state, healthy=True):
    reply = fixture.idle.call(fixture.address, fixture.key)
    need(reply == {"version": 1, "healthy": healthy, "status": state}, "health state mismatch")


def ready(fixture):
    deadline = time.monotonic() + 8
    while True:
        try:
            expect(fixture, "IDLE_NO_PERMIT")
            return
        except OSError:
            need(time.monotonic() < deadline, "writer IPC readiness timed out")
            time.sleep(0.1)


def rejected(action):
    try:
        action()
    except (OSError, ValueError, RuntimeError):
        return
    raise RuntimeError("unexpected authenticated operation acceptance")


def peer_negative(root, fixture):
    changes = ((root, 0o711, 0o700), (fixture.fixture, 0o711, 0o700),
               (fixture.address.parent, 0o711, 0o700), (fixture.address, 0o666, 0o600))
    try:
        for path, mode, _ in changes:
            path.chmod(mode)
        for uid, gid in ((65534, 0), (0, 65534)):
            pid = os.fork()
            if not pid:
                try:
                    os.setgroups([])
                    os.setgid(gid)
                    os.setuid(uid)
                    with socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET) as conn:
                        conn.settimeout(2)
                        conn.connect(str(fixture.address))
                        if conn.recv(1) == b"":
                            os._exit(0)
                finally:
                    os._exit(1)
            _, status = os.waitpid(pid, 0)
            need(os.WIFEXITED(status) and os.WEXITSTATUS(status) == 0, "wrong peer UID/GID was not rejected after connect")
    finally:
        for path, _, original in reversed(changes):
            path.chmod(original)


def test_delta(tool, container, root, f, image_id):
    before = immutable(f)
    date1 = check_running(tool, container, root, image_id)
    ready(f)
    for _ in range(10):
        expect(f, "IDLE_NO_PERMIT")
    tool.docker("restart", "--time", "1", container, timeout=15)
    date2 = check_running(tool, container, root, image_id)
    need(date2 != date1, "writer did not restart")
    ready(f)
    for _ in range(10):
        expect(f, "IDLE_NO_PERMIT")
    need(before == immutable(f), "immutable health changed fixture bytes or inode/timestamps")
    with f.lock.open("rb") as stream:
        fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        start = time.monotonic()
        expect(f, "UNAVAILABLE", False)
        elapsed = time.monotonic() - start
        need(f.idle.LOCK_WAIT <= elapsed < 2, "unbounded shared lock wait")
    expect(f, "IDLE_NO_PERMIT")
    rejected(lambda: f.idle.call(f.address, secrets.token_bytes(32)))
    peer_negative(root, f)
    expect(f, "IDLE_NO_PERMIT")
    for path in (f.ledger, f.lock):
        moved = path.with_suffix(".held")
        path.rename(moved)
        try:
            expect(f, "BLOCKED", False)
            if path == f.lock:
                write_new(path, b"", 0o600)
                try:
                    expect(f, "BLOCKED", False)
                finally:
                    path.unlink()
        finally:
            moved.rename(path)
        expect(f, "IDLE_NO_PERMIT")
    expiry = (datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat()
    scope = {"task_id": "fake-b2m", "key_hash": "a" * 64, "fingerprint": "b" * 64}
    permit = {**{k: v for k, v in scope.items() if k != "task_id"}, "state": "ready", "model": f.one_shot.MODEL,
              "expires_at": expiry, "provider_scope": {
                  "approval_sha256": "c" * 64, "counted_fingerprint": scope["fingerprint"], "input_tokens": 723,
                  "max_output_tokens": 600, "pricing_id": f.p0.PRICING_ID, "service_tier": "default",
                  "valid_until": expiry}}
    f.p0.checked_quote(permit, datetime.now(timezone.utc))
    f.record["one_shot_permits"][scope["task_id"]] = permit
    f.one_shot._durable_write(f.ledger, f.record)
    permitted = immutable(f)
    expect(f, "STARTUP_ONLY")
    for request in ({"op": "admit", **scope}, {"op": "settle", **scope}, {"op": "snapshot"}):
        rejected(lambda: f.ipc.exchange(f.address, f.key, f.idle.DOMAIN, request))
    need(immutable(f) == permitted, "rejected operation altered fixture")
    report("TEST", {"health_calls": 20, "starts": 2, "immutable_bytes_and_metadata": True,
                    "attempts": 1, "reserved_usd_fake": 0.0035, "invalid_key": "denied", "wrong_peers": 2,
                    "contention_ms": round(elapsed * 1000, 2), "contention_recovered": True,
                    "missing_ledger_or_lock": "blocked", "replaced_lock_inode": "blocked",
                    "valid_fake_permit_admit": "denied", "fake_post_paths": 0})


def run(commit, compose_blob):
    need(os.geteuid() == 0 and re.fullmatch("[0-9a-f]{40}", commit)
         and re.fullmatch("[0-9a-f]{40}", compose_blob), "explicit verified fixture inputs required")
    tool = baseline_tool()
    before = tool.baseline()
    report("BASELINE", {"containers": len(before["containers"]), "networks": len(before["networks"]),
                        "volumes": len(before["volume_names"]), "production_http": before["production_health"]})
    image, = tool.inspect_fields("image", [IMAGE], ("Id", "Config.Volumes", "Config.Env"))
    need(image["Config.Volumes"] == {"/opt/data": {}} and not any(
        item.partition("=")[2] for item in image["Config.Env"]
        if any(tag in item.partition("=")[0].upper() for tag in ("KEY", "TOKEN", "PASSWORD", "PROXY"))),
        "inherited image storage or credential environment drift")
    spec = fetch(commit, "h6_b2m_compose.yaml", compose_blob)
    code = {name: fetch(B2L, name, blob) for name, blob in RUNTIME.items()}
    owner = secrets.token_hex(16)
    root = Path("/var/tmp") / (PROJECT + "-" + owner)
    need(root.parent.resolve() == root.parent and shutil.disk_usage(root.parent).free >= 128 * 1024**2,
         "fixture staging disk unavailable")
    fs = subprocess.check_output(["findmnt", "-no", "FSTYPE", "-T", str(root.parent)], text=True).strip()
    need(fs == "ext4", "canary fixture must reside on ext4")
    no_collision(before, root)
    raw = compose(spec, root, owner, "config", "--format", "json")
    render_sha = check_render(raw, root, owner)
    need(compose(spec, root, owner, "config", "--format", "json") == raw and tool.baseline() == before,
         "render or protected inventory drift before staging")
    report("PRE_UP_PASS", {"image_id": image["Id"], "render_sha256_redacted": render_sha, "ext4": True,
                           "services_added": ["writer"], "bindings": 3, "networks_added": 0, "ports_added": 0,
                           "named_volumes_added": 0, "external_dependencies": 0})
    os.umask(0o077)
    previous_hup = signal.signal(signal.SIGHUP, signal.SIG_IGN)
    try:
        root.mkdir(mode=0o700)
        identity = (root.stat().st_dev, root.stat().st_ino)
        try:
            fixture = stage(root, code)
            need(all((root / "src" / name).read_bytes() == raw_source for name, raw_source in code.items())
                 and not owned_ids(tool, owner) and tool.baseline() == before
                 and compose(spec, root, owner, "config", "--format", "json") == raw,
                 "protected post-staging metadata or final render drift")
            compose(spec, root, owner, "up", "-d", "--no-build", "--pull", "never", "writer")
            container, = owned_ids(tool, owner)
            test_delta(tool, container, root, fixture, image["Id"])
            report("RUNTIME", {"uid_gid": [0, 0], "caps_zero": True, "nnp": True, "rootfs_ro": True,
                               "network_interfaces": ["lo"], "real_credentials_or_ledger_mounted": False,
                               "ledger_parent_mode": "0700", "ledger_and_lock_mode": "0600",
                               "fixture_key_mode": "0400", "fixture_key_bind_read_only": True})
        finally:
            for item in owned_ids(tool, owner):
                tool.docker("rm", "-f", item, timeout=15)
            need(not owned_ids(tool, owner), "owned container remained after rollback")
            current = root.lstat()
            need((current.st_dev, current.st_ino) == identity and stat.S_ISDIR(current.st_mode),
                 "refuse to remove changed fixture path")
            shutil.rmtree(root)
            after = tool.baseline()
            need(not root.exists() and after == before, "post-rollback protected metadata or inventory drift")
            report("ROLLBACK_PASS", {"pre_post_inventory_equal": True, "protected_ledger_metadata_equal": True,
                                     "fixture_removed": True, "production_http": after["production_health"],
                                     "project_containers_remaining": 0})
    finally:
        signal.signal(signal.SIGHUP, previous_hup)
    report("RESULT", "KVM2_FAKE_IDLE_CANARY_PASS")


if __name__ == "__main__":
    try:
        run(*sys.argv[1:])
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as error:
        report("STOP", str(error) if type(error) is RuntimeError else type(error).__name__)
        raise SystemExit(1) from None
