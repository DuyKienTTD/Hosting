"""Render, rehearse and tear down a KVM2-only fake CONNECT/TLS Compose project."""

import collections
import hashlib
import json
import os
import re
import secrets
import shutil
import subprocess
import sys
import types
import urllib.request
from pathlib import Path

SOURCE = "sandbox/p0-hermes-gate-a/"
RAW = "https://raw.githubusercontent.com/DuyKienTTD/Hosting/"
B2_E = "d32aff15fee7972d217e2f8c8a1f81fa5f987906"
B2_F = "b670a65f90ae762a8270176978cf46edb4d50b9c"
BASELINE_BLOB = "dcb891284f44763480f4b6675960836fa9d2f64e"
CONTRACT_BLOB = "d58d0bcf89bd557c313606d5908817f45ccd0129"
LABEL = "ttd.h6.b2g.fixture"
IMAGE = "ghcr.io/hostinger/hvps-hermes-agent@sha256:0ea63377bd672cb76de6a8510aaaef619fe2a045558b771656c072ef527c344f"
FIXTURE = "h6_b2g_fixture.py"
ROLE_NETWORKS = {"guard": {"front"}, "proxy": {"front", "back"}, "provider": {"back"}, "writer": set()}
ROLE_MOUNTS = {
    "guard": {"ipc": ("/ipc", True), "auth": ("/ipc-auth", True), "trust": ("/trust", True)},
    "writer": {"ledger": ("/fake-ledger", False), "ipc": ("/ipc", False), "auth": ("/ipc-auth", True)},
    "proxy": {"proxy-audit": ("/audit", False)},
    "provider": {"provider-audit": ("/audit", False), "tls": ("/tls", True)},
}
BRIDGE = {"com.docker.network.bridge.gateway_mode_ipv4": "isolated"}
TMPFS = "/opt/data:rw,noexec,nosuid,nodev,size=8m"
RUNTIME_SOURCE = ("guard.py", "h6_ipc_auth.py", "h6_p0.py", "h6_provider.py", "h6_writer.py", "one_shot.py", "mock_contract.py")


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def fetch(commit, name, expected=None):
    with urllib.request.urlopen(f"{RAW}{commit}/{name}", timeout=15) as response:
        result = response.read(512 * 1024 + 1)
    require(len(result) <= 512 * 1024, "archive entry too large")
    if expected is not None:
        calculated = hashlib.sha1(f"blob {len(result)}\0".encode() + result).hexdigest()
        require(calculated == expected, f"pinned Git blob mismatch for {Path(name).name}")
    return result


def load_baseline():
    data = fetch(B2_E, SOURCE + "h6_b2e_rehearsal.py", BASELINE_BLOB)
    module = types.ModuleType("b2g_verified_baseline")
    exec(compile(data, "pinned-b2e-baseline", "exec"), module.__dict__)
    return module


def stage(root, commit, fixture_blob):
    code = root / "src"
    code.mkdir(mode=0o700)
    manifest = json.loads(fetch(B2_F, "reports/evidence/2026-11-22-ttd-hermes-gate-b-h6-b2-f-source-mock.json"))
    require(manifest["result"] == "B2_F_SOURCE_MOCK_PASS", "B2-F manifest")
    for file in RUNTIME_SOURCE:
        expected = CONTRACT_BLOB if file == "mock_contract.py" else manifest["source_blobs"][SOURCE + file]
        (code / file).write_bytes(fetch(B2_F, SOURCE + file, expected))
    (code / FIXTURE).write_bytes(fetch(commit, SOURCE + FIXTURE, fixture_blob))
    for directory in set().union(*ROLE_MOUNTS.values()):
        (root / directory).mkdir(mode=0o700)
    print("PASS B2G_SOURCE: seven pinned B2-F runtime blobs, fixture and B2-E baseline helper", flush=True)


def recipe(root, project):
    config = {"name": project, "services": {}, "networks": {
        name: {"name": f"{project}_{name}", "driver": "bridge", "internal": True,
               "driver_opts": dict(BRIDGE), "labels": {LABEL: project}} for name in ("front", "back")}}
    for role, networks in ROLE_NETWORKS.items():
        sources = {"src": ("/opt/b2g", True)} | ROLE_MOUNTS[role]
        volumes = []
        for item, (target, readonly) in sources.items():
            entry = {"type": "bind", "source": str(root / item), "target": target,
                     "bind": {"create_host_path": False, "propagation": "rprivate"}}
            if readonly:
                entry["read_only"] = True
            volumes.append(entry)
        command = [f"/opt/b2g/{FIXTURE}", role]
        if role == "guard":
            command = ["-c", "import sys,signal;sys.path.insert(0,'/opt/b2g');"
                       "import h6_b2g_fixture as f;f.posture('guard');signal.pause()"]
        service = {"image": IMAGE, "pull_policy": "never", "user": "0:0", "read_only": True,
                   "cap_drop": ["ALL"], "security_opt": ["no-new-privileges:true"], "pids_limit": 48,
                   "entrypoint": ["python3", "-B", "-u"], "command": command, "tmpfs": [TMPFS],
                   "labels": {LABEL: project}, "volumes": volumes}
        service.update({"networks": {network: {} for network in sorted(networks)}} if networks else {"network_mode": "none"})
        config["services"][f"b2g-{role}"] = service
    return config


def write_file(path, data):
    fd = os.open(path, os.O_WRONLY | os.O_EXCL | os.O_CREAT, 0o600)
    with os.fdopen(fd, "wb") as stream:
        stream.write(data)


def certificates(root):
    issuer, trust, tls = (root / name for name in ("issuer", "trust", "tls"))
    issuer.mkdir(mode=0o700)

    def openssl(*args):
        result = subprocess.run(["openssl", *map(str, args)], cwd=issuer, capture_output=True, timeout=15)
        require(result.returncode == 0, f"synthetic openssl {args[0]} failed")

    for label, name in (("ca", "Trusted"), ("wrong-ca", "Untrusted")):
        openssl("req", "-x509", "-newkey", "rsa:2048", "-nodes", "-sha256", "-days", "1",
                "-subj", f"/CN=B2G Synthetic {name} CA", "-addext", "basicConstraints=critical,CA:TRUE",
                "-addext", "keyUsage=critical,keyCertSign,cRLSign",
                "-keyout", issuer / f"{label}.key", "-out", trust / f"{label}.pem")
    (issuer / "index").touch()
    (issuer / "serial").write_text("1000\n")
    (issuer / "config").write_text(
        "[ca]\ndefault_ca=fixture\n[fixture]\ndatabase=index\nserial=serial\nnew_certs_dir=.\n"
        "certificate=../trust/ca.pem\nprivate_key=ca.key\npolicy=subject\ndefault_days=1\n"
        "default_md=sha256\nunique_subject=no\nx509_extensions=leaf\n[subject]\ncommonName=supplied\n"
        "[leaf]\nbasicConstraints=critical,CA:FALSE\nkeyUsage=critical,digitalSignature,keyEncipherment\n"
        "extendedKeyUsage=serverAuth\nsubjectAltName=DNS:*.b2g.invalid\n",
        encoding="ascii")
    for name in ("valid", "expired"):
        openssl("req", "-new", "-newkey", "rsa:2048", "-nodes", "-sha256", "-subj", "/CN=*.b2g.invalid",
                "-keyout", tls / f"{name}.key", "-out", f"{name}.csr")
        dates = () if name == "valid" else ("-startdate", "20200101000000Z", "-enddate", "20200102000000Z")
        openssl("ca", "-batch", "-config", "config", "-notext", "-in", f"{name}.csr", "-out", tls / f"{name}.crt", *dates)
        (tls / f"{name}.key").chmod(0o400)
    openssl("verify", "-CAfile", trust / "ca.pem", "-verify_hostname", "ok.b2g.invalid", tls / "valid.crt")
    write_file(root / "auth/ipc.key", os.urandom(32))
    (root / "auth/ipc.key").chmod(0o400)


def check_render(expected, actual, root, project, before, tooling):
    for service in actual.get("services", {}).values():
        for field in service.get("volumes", []):
            source = Path(field["source"])
            require(source.resolve(strict=True) == source and source.parent == root, "unsafe bind source")
    # Compose may express empty network endpoint options as null.
    for service in actual.get("services", {}).values():
        if "networks" in service:
            service["networks"] = {key: val or {} for key, val in service["networks"].items()}
    for network in actual.get("networks", {}).values():
        if network.get("ipam") == {}:
            network.pop("ipam")
    require(actual == expected, "full Compose render is not the exact allowlisted recipe")
    for item in before["containers"]:
        require(not item["Name"].startswith(f"/{project}-")
                and (item["Config.Labels"] or {}).get(tooling.PROJECT_LABEL) != project, "existing container overlap")
        for mount in item["Mounts"]:
            source = Path(mount["Source"]).resolve()
            require(not (source.is_relative_to(root) or root.is_relative_to(source)), "existing mount overlap")
    require(not any(item["Name"].startswith(project + "_") for item in before["networks"])
            and not any(name.startswith(project + "_") for name in before["volume_names"]), "existing network/volume overlap")
    image, = tooling.inspect_fields("image", [IMAGE], ("Id", "Config.Volumes", "Config.Env"))
    require(image["Config.Volumes"] == {"/opt/data": {}}
            and not any(entry.partition("=")[2] and any(key in entry.partition("=")[0].upper()
                        for key in ("API_KEY", "TOKEN", "PASSWORD", "PROXY")) for entry in image["Config.Env"]),
            "cached image unexpected inherited credential or volume")
    return image["Id"]


def check_running(tooling, call, config, project, image):
    ids, endpoints = {}, {}
    for name, service in config["services"].items():
        cid = call("ps", "-q", name).decode().strip()
        require(re.fullmatch(r"[0-9a-f]{12,64}", cid), "isolated service not running")
        item, = tooling.inspect_fields("container", [cid], ("Id", "Name", "Image", "Config.Labels", "Config.User",
            "Config.Entrypoint", "Config.Cmd", "Mounts", "NetworkSettings.Networks", "HostConfig.CapDrop",
            "HostConfig.PortBindings", "HostConfig.ReadonlyRootfs", "HostConfig.SecurityOpt", "HostConfig.NetworkMode",
            "HostConfig.Tmpfs"))
        role = name.removeprefix("b2g-")
        require(item["Name"] == f"/{project}-{name}-1" and item["Config.Labels"].get(LABEL) == project
                and item["Image"] == image and item["Config.User"] == "0:0"
                and item["Config.Entrypoint"] == service["entrypoint"] and item["Config.Cmd"] == service["command"]
                and item["HostConfig.ReadonlyRootfs"] and item["HostConfig.CapDrop"] == ["ALL"]
                and item["HostConfig.SecurityOpt"] == ["no-new-privileges:true"] and not item["HostConfig.PortBindings"]
                and set(item["HostConfig.Tmpfs"]) == {"/opt/data"}, "runtime posture differs from render")
        expected = {f"{project}_{suffix}" for suffix in ROLE_NETWORKS[role]}
        found = set(item["NetworkSettings.Networks"])
        require(found == expected if expected else found <= {"none"} and item["HostConfig.NetworkMode"] == "none",
                "runtime network membership differs")
        mounts = {pair["Destination"]: pair for pair in item["Mounts"] if pair["Type"] != "tmpfs"}
        require(set(mounts) == {pair["target"] for pair in service["volumes"]}, "unexpected runtime mounts")
        for pair in service["volumes"]:
            mounted = mounts[pair["target"]]
            require(mounted["Type"] == "bind" and mounted["Source"] == pair["source"]
                    and mounted["RW"] != pair.get("read_only", False) and mounted["Propagation"] == "rprivate",
                    "runtime bind differs")
        call("exec", "-T", "-w", "/opt/b2g", name, "python3", "-B", "-c",
             f"import h6_b2g_fixture as f;f.posture({role!r})", output=False)
        ids[role] = item["Id"]
        endpoints[role] = item["NetworkSettings.Networks"]
    networks = tooling.inspect_fields("network", list(config["networks"][key]["name"] for key in config["networks"]),
                                      ("Name", "Internal", "EnableIPv6", "Options", "Containers", "Labels"))
    for item in networks:
        suffix = item["Name"].rsplit("_", 1)[-1]
        require(item["Internal"] and not item["EnableIPv6"] and item["Options"] == BRIDGE and item["Labels"].get(LABEL) == project
                and set(item["Containers"]) == {ids[role] for role in ids if suffix in ROLE_NETWORKS[role]},
                "actual isolated bridge membership or driver option differs")
    return endpoints["provider"][f"{project}_back"]["IPAddress"]


def read_events(path):
    return [json.loads(line) for line in path.read_text().splitlines()]


def verify_matrix(root, guard_log, locks):
    fixture = types.ModuleType("b2g_fixture_contract")
    exec(compile((root / "src" / FIXTURE).read_bytes(), FIXTURE, "exec"), fixture.__dict__)
    match = re.search(r"^PASS B2G_GUARD wire_sha256=([0-9a-f]{64}) bytes=(\d+)$", guard_log, re.M)
    require(match, "missing signed Guard matrix")
    digest, size = match[1], int(match[2])
    proxies = read_events(root / "proxy-audit/events.jsonl")
    posts = read_events(root / "provider-audit/events.jsonl")
    require(all(row["event"] == "connect" for row in proxies) and
            collections.Counter(row["case"] for row in proxies) == collections.Counter([*fixture.HOSTS, "blocked"]),
            "proxy counts differ: redirect, retry or unexpected route")
    require(all(row["event"] in ("post", "drip") for row in posts), "unexpected HTTP method or fallback")
    sent = [row for row in posts if row["event"] == "post"]
    require(collections.Counter(row["case"] for row in sent) == collections.Counter(set(fixture.HOSTS) - fixture.NO_POST)
            and all(row["digest"] == digest and row["size"] == size and row["tls"] in ("TLSv1.2", "TLSv1.3") for row in sent),
            "stub POST count, actual digest or TLS version differs")
    drips = sum(row["event"] == "drip" and row["case"] == "slow" for row in posts)
    require(3 <= drips < 24, "slow-drip deadline did not close the fixture connection")
    for case in fixture.HOSTS:
        path = root / "ledger" / case / "level2-budget.json"
        state = json.loads(path.read_bytes())
        task, = state["tasks"].values()
        permit, = state["one_shot_permits"].values()
        outcome = "usage_recorded" if case in fixture.SUCCESS else "outcome_unknown"
        lock = path.with_suffix(".json.lock").stat()
        require((lock.st_dev, lock.st_ino) == locks[case] and task["state"] == outcome
                and task["fingerprint"] == digest and permit["state"] == "consumed"
                and state["attempts"] == 1 and state["reserved_usd"] == 0.0035 and state["kill_switch"] is True
                and (state["actual_usd"] > 0 if case in fixture.SUCCESS else state["actual_usd"] == 0),
                "synthetic settled state or lock inode differs")
    print(f"PASS B2G_MATRIX scenarios={len(fixture.HOSTS)} CONNECT={len(proxies)-1} denied_authority=1 POST={len(sent)} "
          f"exact_sha256={digest} bytes={size} slow_drip_chunks={drips} TLS={','.join(sorted({row['tls'] for row in sent}))}",
          flush=True)


def rollback(tooling, root, project, before):
    current = tooling.inventory()
    existing_ids = {item["Id"] for item in before["containers"]}
    containers = [item for item in current["containers"]
                  if (item["Config.Labels"] or {}).get(tooling.PROJECT_LABEL) == project]
    for item in containers:
        require(item["Id"] not in existing_ids and item["Config.Labels"].get(LABEL) == project and
                any(item["Name"] == f"/{project}-b2g-{role}-1" for role in ROLE_NETWORKS) and
                all(mount["Type"] == "tmpfs" and mount["Destination"] == "/opt/data" or
                    mount["Type"] == "bind" and Path(mount["Source"]).parent == root for mount in item["Mounts"]),
                "ambiguous container identity: no destructive cleanup")
    if containers:
        tooling.docker("rm", "-f", *(item["Id"] for item in containers))
    networks = [item for item in current["networks"] if (item["Labels"] or {}).get(tooling.PROJECT_LABEL) == project]
    for item in networks:
        require(item["Id"] not in {row["Id"] for row in before["networks"]} and
                item["Name"] in {f"{project}_front", f"{project}_back"} and item["Labels"].get(LABEL) == project,
                "ambiguous network identity: no destructive cleanup")
        active, = tooling.inspect_fields("network", [item["Id"]], ("Containers",))
        require(not active["Containers"], "refusing to delete network with endpoints")
        tooling.docker("network", "rm", item["Id"])
    require(tooling.baseline() == before, "post-teardown preexisting inventory or protected metadata drift")
    require(root.parent == Path("/var/tmp") and root.resolve(strict=True) == root
            and root.name == project and re.fullmatch(r"ttd-h6-b2g-[0-9a-f]{12}", project), "ambiguous fixture path")
    shutil.rmtree(root)
    require(not root.exists(), "fixture directory remains")
    print("PASS B2G_ROLLBACK: fixture removed, preexisting inventory and ledger metadata equal, production HTTP 200/200", flush=True)


def run(commit, fixture_blob):
    require(os.geteuid() == 0 and all(re.fullmatch(r"[a-f0-9]{40}", value) for value in (commit, fixture_blob)),
            "runner inputs")
    baseline = load_baseline()
    before = baseline.baseline()
    require(not any((row["Config.Labels"] or {}).get(baseline.OWNER_LABEL) for row in before["containers"])
            and not any(name.startswith("ttd-h6-b2e-") for name in before["volume_names"])
            and not any(Path("/var/tmp").glob("ttd-h6-b2e-*")), "B2-E rollback not clean")
    baseline.verify_h4(before)
    print("PASS B2G_BASELINE: rollback B2-E clean, H4 backup matched, real ledger modes/ACL and production baseline checked", flush=True)
    project = "ttd-h6-b2g-" + secrets.token_hex(6)
    root = Path("/var/tmp") / project
    root.mkdir(mode=0o700)
    old_umask = os.umask(0o077)
    try:
        stage(root, commit, fixture_blob)
        config = recipe(root, project)
        control = root / "compose.json"
        write_file(control, json.dumps(config).encode())

        compose_args = ("compose", "--env-file", "/dev/null", "--project-directory", str(root),
                        "-p", project, "--profile", "*", "-f", str(control))

        def call(*args, **kwargs):
            return baseline.docker(*compose_args, *args, **kwargs)

        render = call("config", "--format", "json")
        image = check_render(config, json.loads(render), root, project, before, baseline)
        certificates(root)
        require(render == call("config", "--format", "json") and
                baseline.inventory() == {key: before[key] for key in ("containers", "networks", "volume_names")},
                "render or inventory drift before up")
        print(f"PASS B2G_PRE_UP services=4 internal_bridges=2 external=0 ports=0 volumes=0 collisions=0 "
              f"render_sha256={hashlib.sha256(render).hexdigest()}", flush=True)
        call("up", "-d", "--no-deps", output=False)
        provider_ip = check_running(baseline, call, config, project, image)
        print("PASS B2G_RUNTIME: cap sets=0, RO rootfs, fixture mounts only, front/back isolated and writer network none", flush=True)
        # Wait for the writer to finish seeding cases and for both TCP listeners.
        call("exec", "-T", "-w", "/opt/b2g", "b2g-guard", "python3", "-B", "-c",
             "import time,socket,sys;from pathlib import Path;from h6_b2g_fixture import HOSTS\n"
             "end=time.monotonic()+8\n"
             "while time.monotonic()<end:\n"
             " if all((Path('/ipc')/c/'w.sock').is_socket() for c in HOSTS):\n"
             "  try:\n"
             "   socket.create_connection(('b2g-proxy',8888),timeout=.3).close();sys.exit(0)\n"
             "  except OSError: pass\n"
             " time.sleep(.05)\n"
             "raise SystemExit('fixtures not ready')")
        locks = {}
        for path in (root / "ledger").glob("*/level2-budget.json.lock"):
            info = path.stat()
            require((info.st_mode & 0o777, info.st_uid, info.st_gid) == (0o600, 0, 0)
                    and path.parent.stat().st_mode & 0o777 == 0o700, "synthetic ledger modes")
            locks[path.parent.name] = (info.st_dev, info.st_ino)
        upstream, = (row for row in before["containers"] if row["Name"] == "/ttd-p0-provider-egress")
        outside = sorted({network["IPAddress"] for network in upstream["NetworkSettings.Networks"].values()
                          if network["IPAddress"]})
        run_guard = subprocess.run(["docker", *compose_args, "exec", "-T", "b2g-guard", "python3", "-B", "-u",
                                   f"/opt/b2g/{FIXTURE}", "guard", provider_ip, *outside], capture_output=True, timeout=95,
                                  env={"PATH": os.defpath, "HOME": "/nonexistent"})
        guard_result = run_guard.stdout.decode()
        print("\n".join(line for line in guard_result.splitlines() if line.startswith("PASS")), flush=True)
        if run_guard.returncode:
            print(run_guard.stderr.decode()[-2500:], flush=True)
        require(run_guard.returncode == 0, "Guard TLS fixture failed")
        verify_matrix(root, guard_result, locks)
    finally:
        os.umask(old_umask)
        rollback(baseline, root, project, before)
    print("H6_B2_G_KVM2_FAKE_TLS_PASS", flush=True)


if __name__ == "__main__":
    run(*sys.argv[1:])
