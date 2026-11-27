"""KVM2 B1 mock-only rehearsal. Prepare and review before running the project."""

import hashlib
import json
import os
import re
import secrets
import shutil
import stat
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

STAGE_A = "a411114d0b485729a57d43eaf97fd2a5226d1585"
BASE_URL = "https://raw.githubusercontent.com/DuyKienTTD/Hosting/"
STAGE_A_FILES = (
    "compose.yaml", "compose.h6-stage-a.yaml", "guard.py", "h6_writer.py", "one_shot.py",
    "mock_contract.py", "provider_mock.py", "h6_stage_a_test.py", "one_shot_linux_test.py", "bridge.py",
)
IMAGE = "ghcr.io/hostinger/hvps-hermes-agent@sha256:0ea63377bd672cb76de6a8510aaaef619fe2a045558b771656c072ef527c344f"
SERVICES = {"guard", "provider-mock", "h6-writer"}
PROVIDER_TARGET = "/run/secrets/openai_provider_api_key"
LEDGER_TARGET = "/opt/ttd/ledger/level2-budget.json"
PROJECT_LABEL = "com.docker.compose.project"
B1_OVERLAY = "compose.h6-b1.yaml"


def docker(*args, timeout=40):
    result = subprocess.run(["docker", *args], check=False, capture_output=True, timeout=timeout,
                            env={"PATH": os.defpath, "HOME": "/nonexistent"})
    if result.returncode:
        raise RuntimeError(f"docker {args[0]} failed ({result.returncode}): {result.stderr.decode()[-1000:]}")
    return result.stdout


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def objects(kind):
    commands = {"container": ("ps", "-aq", "--no-trunc"),
                "network": ("network", "ls", "-q", "--no-trunc")}
    ids = docker(*commands[kind]).decode().splitlines()
    return json.loads(docker(kind, "inspect", *ids)) if ids else []


def project_of(container):
    return (container["Config"]["Labels"] or {}).get(PROJECT_LABEL)


def checksum(value):
    return hashlib.sha256(value).hexdigest()


def baseline(ports, project):
    containers = [c for c in objects("container") if project_of(c) != project]
    mounts = [(c, m) for c in containers for m in c["Mounts"]]
    guard, credential = next((c, m) for c, m in mounts if c["Name"] == "/ttd-gate-a-guard"
                             and m["Destination"] == PROVIDER_TARGET)
    secret_source = Path(credential["Source"]).resolve(strict=True)
    require(not credential["RW"] and sum(Path(m["Source"]).resolve() == secret_source
            or m["Destination"] == PROVIDER_TARGET for _, m in mounts) == 1, "provider mount isolation")
    require(stat.S_IMODE(secret_source.stat().st_mode) == 0o600, "provider file metadata")
    ledger_mount = next(m for m in guard["Mounts"] if m["Destination"] == LEDGER_TARGET)
    require(not ledger_mount["RW"], "Guard ledger mount drift")
    raw = Path(ledger_mount["Source"]).read_bytes()
    summary = json.loads(raw)
    require(summary["attempts"] == 1 and summary["kill_switch"] is True
            and not summary.get("one_shot_permits"), "real ledger baseline drift")
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    for port, path in zip(ports, ("/healthz", "/api/health"), strict=True):
        with opener.open(f"http://127.0.0.1:{port}{path}", timeout=4) as response:
            require(response.status == 200, "production health")
    proxies = [c for c in containers if c["Name"] == "/ttd-p0-provider-egress"]
    proxy_ips = sorted(n["IPAddress"] for c in proxies for n in c["NetworkSettings"]["Networks"].values()
                       if n["IPAddress"])
    require(proxy_ips, "existing proxy IP for local-only negative check")
    runtime = {c["Id"]: {"name": c["Name"], "status": c["State"]["Status"],
                         "started": c["State"]["StartedAt"], "restarts": c["RestartCount"],
                         "mounts": c["Mounts"], "ports": c["HostConfig"]["PortBindings"],
                         "networks": c["NetworkSettings"]["Networks"]} for c in containers}
    networks = {n["Id"]: sorted(n["Containers"] or {}) for n in objects("network")
                if (n["Labels"] or {}).get(PROJECT_LABEL) != project}
    return {"ledger": checksum(raw), "runtime": runtime, "networks": networks,
            "volumes": sorted(docker("volume", "ls", "-q").decode().splitlines()), "proxy_ips": proxy_ips}


def render(root, project):
    # Compose substitutes before merging. Its only variable is supplied via this private env file.
    args = ["compose", "--env-file", str(root / "compose.env"), "--project-directory", str(root / "src"),
            "-f", str(root / "src/compose.yaml"), "-f", str(root / "src/compose.h6-stage-a.yaml"),
            "-f", str(root / "src" / B1_OVERLAY),
            "-p", project, "--profile", "*", "config", "--format", "json"]
    return docker(*args)


def plan(root, project, config, existing):
    # Compose 5.6 keeps the known YAML extension in rendered JSON. It cannot create a resource.
    require(set(config) - {"x-b1-image-state"} == {"name", "services", "networks"}
            and config["name"] == project, "extra Compose resources")
    require(set(config["services"]) == SERVICES and set(config["networks"]) == {"h6_mock"}, "unexpected services")
    network = config["networks"]["h6_mock"]
    require(network.get("internal") and not network.get("external") and not network.get("enable_ipv6")
            and network["name"] == project + "_h6_mock", "unexpected network")
    expected_sources = {
        "guard": {"/opt/ttd/guard.py": ("src/guard.py", True), "/opt/ttd/one_shot.py": ("src/one_shot.py", True),
                  "/opt/ttd/mock_contract.py": ("src/mock_contract.py", True), "/opt/ttd/h6_writer.py": ("src/h6_writer.py", True),
                  "/run/secrets/guard_service_token": ("fixture/guard-service-token", True),
                  "/opt/ttd/h6-ipc": ("fixture/ipc", True)},
        "h6-writer": {"/opt/ttd/one_shot.py": ("src/one_shot.py", True),
                      "/opt/ttd/mock_contract.py": ("src/mock_contract.py", True), "/opt/ttd/h6_writer.py": ("src/h6_writer.py", True),
                      "/opt/ttd/mock-ledger": ("fixture/mock-ledger", False), "/opt/ttd/h6-ipc": ("fixture/ipc", False)},
        "provider-mock": {"/opt/ttd/provider_mock.py": ("src/provider_mock.py", True),
                          "/run/secrets/guard_service_token": ("fixture/guard-service-token", True)},
    }
    entrypoints = {"guard": ["python3", "/opt/ttd/guard.py"], "h6-writer": ["python3", "-B", "/opt/ttd/h6_writer.py"],
                   "provider-mock": ["python3", "/opt/ttd/provider_mock.py"]}
    mounts = {}
    for name, service in config["services"].items():
        require(service["image"] == IMAGE and service["pull_policy"] == "never" and service["read_only"]
                and service["entrypoint"] == entrypoints[name] and not service.get("command")
                and service["cap_drop"] == ["ALL"] and service["security_opt"] == ["no-new-privileges:true"],
                f"unexpected execution settings for {name}")
        require(not any(service.get(key) for key in ("ports", "secrets", "configs", "container_name", "privileged",
                    "cap_add", "devices", "extra_hosts", "dns", "links", "external_links", "pid", "ipc", "volumes_from",
                    "env_file", "build", "userns_mode")), f"forbidden service fields for {name}")
        require(service.get("user") == {"guard": "23061:23060", "h6-writer": "23062:23060",
                                        "provider-mock": None}[name], f"unexpected user for {name}")
        if name == "h6-writer":
            require(service.get("network_mode") == "none" and not service.get("networks"), "writer network")
        else:
            alias = "gate-a-" + name
            require(service.get("networks") == {"h6_mock": {"aliases": [alias]}}
                    and not service.get("network_mode"), "Guard/mock network")
        health = service["healthcheck"]["test"]
        guard_env = {"PYTHONDONTWRITEBYTECODE": "1", "TTD_H6_STAGE_A_SOCKET": "/opt/ttd/h6-ipc/writer.sock"}
        require(service.get("environment", {}) == (guard_env if name == "guard" else {}), f"unexpected env for {name}")
        # Entries are hash-pinned upstream. Check rendered commands and expected health endpoints as well.
        health_target = {"guard": "127.0.0.1:8081/healthz", "provider-mock": "127.0.0.1:8082/healthz",
                         "h6-writer": "/opt/ttd/h6-ipc/writer.sock"}[name]
        require(health[:3] == ["CMD", "python3", "-c"] and len(health) == 4 and health_target in health[3],
                f"healthcheck target for {name}")
        pairs = {}
        ram = []
        for mount in service["volumes"]:
            if mount["type"] == "tmpfs":
                ram.append(mount)
                continue
            path = Path(mount["source"])
            require(mount["type"] == "bind" and path.resolve(strict=True) == path and path.is_relative_to(root),
                    "bind path outside private fixture")
            pairs[mount["target"]] = (str(path.relative_to(root)), mount.get("read_only", False))
        require(len(ram) == 1 and ram[0]["target"] == "/opt/data"
                and str(ram[0]["tmpfs"]["size"]) == "8388608" and not ram[0].get("read_only")
                and pairs == expected_sources[name] and len(pairs) + 1 == len(service["volumes"]),
                f"unexpected mounts for {name}")
        mounts[name] = {target: [str(root / source), read_only] for target, (source, read_only) in pairs.items()}
    targets = {f"/{project}-{name}-1" for name in SERVICES} | {f"/{project}-contract"}
    require(not any(c["name"] in targets for c in existing["runtime"].values()), "container name collision")
    paths = [Path(item["Source"]).resolve() for c in existing["runtime"].values() for item in c["mounts"]]
    require(not any(root.is_relative_to(path) or path.is_relative_to(root) for path in paths), "overlapping existing bind")
    require(not any(n["Name"] == network["name"] for n in objects("network")), "network name collision")
    require(not any(v.startswith(project) for v in existing["volumes"]), "volume name collision")
    require(not any(project_of(c) == project for c in objects("container")), "existing project")
    return mounts


def prepare(ports):
    root = Path(tempfile.mkdtemp(prefix="ttd-h6-b1-", dir="/var/tmp")).resolve()
    project = root.name
    source = root / "src"
    source.mkdir(mode=0o755)
    fixture = root / "fixture"
    fixture.mkdir(mode=0o700)
    # Verify pinned Stage A blobs before parsing configuration or importing Python.
    expected = json.loads(Path(__file__).with_name("h6_b1_source.json").read_bytes())
    require(set(expected) == set(STAGE_A_FILES), "incomplete source manifest")
    for name in STAGE_A_FILES:
        url = BASE_URL + STAGE_A + "/sandbox/p0-hermes-gate-a/" + name
        with urllib.request.urlopen(url, timeout=12) as response:
            payload = response.read()
        require(checksum(payload) == expected[name], f"pinned source checksum for {name}")
        (source / name).write_bytes(payload)
        (source / name).chmod(0o644)
    overlay = Path(__file__).with_name(B1_OVERLAY).read_bytes()
    (source / B1_OVERLAY).write_bytes(overlay)
    expected[B1_OVERLAY] = checksum(overlay)
    sys.path.insert(0, str(source))
    import h6_stage_a_test as test
    import h6_writer as writer
    from guard import freeze_stage_a

    state_dir = fixture / "mock-ledger"
    ipc_dir = fixture / "ipc"
    for folder, mode in ((state_dir, 0o700), (ipc_dir, 0o750)):
        folder.mkdir(mode=mode)
        os.chown(folder, writer.WRITER_UID, writer.IPC_GID)
    token = fixture / "guard-service-token"
    token.write_text(secrets.token_hex(32) + "\n")
    os.chown(token, 0, writer.IPC_GID)
    token.chmod(0o640)
    _, digest = freeze_stage_a(test.BODY)
    test.make_fixture(state_dir / writer.FIXTURE_PATH.name, digest)
    (root / "compose.env").write_text(f"TTD_H6_FIXTURE_ROOT={fixture}\n")
    config = render(root, project)
    existing = baseline(ports, project)
    mounts = plan(root, project, json.loads(config), existing)
    (root / "baseline.json").write_text(json.dumps(existing))
    (root / "rendered.json").write_bytes(config)
    (root / "prepared.json").write_text(json.dumps({"project": project, "ports": ports, "sources": expected,
                                                    "digest": digest, "mounts": mounts}))
    print(f"B1_RENDER_GATE_PASS project={project} sha256={checksum(config)} directory={root} "
          f"existing_containers={len(existing['runtime'])} existing_networks={len(existing['networks'])}", flush=True)


def selected(project):
    return [entry for entry in objects("container") if project_of(entry) == project]


def confirm_owned(root, project, mounts, complete=False):
    matches = selected(project)
    index = {}
    for container in matches:
        service = container["Config"]["Labels"]["com.docker.compose.service"]
        require(service in mounts and service not in index and container["Name"] == f"/{project}-{service}-1",
                "rollback resource identity")
        require(container["Config"]["Labels"]["com.docker.compose.project.working_dir"] == str(root / "src"),
                "rollback project directory")
        require({m["Destination"]: [m["Source"], not m["RW"]] for m in container["Mounts"]
                 if m["Type"] == "bind"} == mounts[service]
                and [(m["Type"], m["Destination"]) for m in container["Mounts"] if m["Type"] != "bind"]
                == [("tmpfs", "/opt/data")],
                "runtime bind mismatch")
        index[service] = container
    networks = [n for n in objects("network") if (n["Labels"] or {}).get(PROJECT_LABEL) == project]
    require(len(networks) <= 1, "ambiguous project networks")
    for network in networks:
        require(network["Internal"] and not network["EnableIPv6"] and network["Name"] == project + "_h6_mock"
                and set(network["Containers"] or {}) <= {item["Id"] for item in matches}, "rollback network identity")
    if complete:
        require(set(index) == SERVICES and len(networks) == 1, "incomplete runtime")
    return index, networks


def verify_runtime(index, network, config, image):
    require(set(network["Containers"]) == {index[name]["Id"] for name in ("guard", "provider-mock")},
            "unexpected internal network membership")
    for name, container in index.items():
        spec = config["services"][name]
        host = container["HostConfig"]
        mode = "none" if name == "h6-writer" else network["Name"]
        attached = set(container["NetworkSettings"]["Networks"] or {})
        require(attached in (set(), {"none"}) if mode == "none" else attached == {mode},
                f"unexpected live network attachments for {name}")
        require(container["Image"] == image["Id"] and container["Config"]["Entrypoint"] == spec["entrypoint"]
                and container["Config"]["User"] == spec.get("user", image["Config"]["User"])
                and container["Config"]["Healthcheck"]["Test"] == spec["healthcheck"]["test"]
                and host["NetworkMode"] == mode and host["ReadonlyRootfs"] and host["CapDrop"] == ["ALL"]
                and not host["Privileged"] and not host["PortBindings"] and container["State"]["Health"]["Status"] == "healthy",
                f"runtime mismatch for {name}")
        require(clean_environment(container["Config"]["Env"]),
                f"unexpected environment credential/proxy for {name}")


def clean_environment(entries):
    return not any(key in entry.split("=", 1)[0].upper() and entry.split("=", 1)[-1]
                   for entry in entries for key in ("API_KEY", "AUTH_TOKEN", "PROXY"))


NO_BYPASS = """
import os,socket,sys
from pathlib import Path
assert not Path('/opt/ttd/ledger/level2-budget.json').exists()
assert not Path('/run/secrets/openai_provider_api_key').exists()
if sys.argv[1] == 'h6-writer':
    assert set(os.listdir('/sys/class/net')) == {'lo'}
    assert not Path('/run/secrets/guard_service_token').exists()
else:
    assert not Path('/opt/ttd/mock-ledger').exists()
    assert not any(line.split()[1] == '00000000' for line in Path('/proc/net/route').read_text().splitlines()[1:])
if sys.argv[1] == 'provider-mock':
    assert not Path('/opt/ttd/h6-ipc').exists()
for host in sys.argv[2:]:
    try:
        with socket.create_connection((host,8888),timeout=.4):
            raise AssertionError('existing proxy reachable')
    except OSError:
        pass
"""

HTTP_TEST = """
import concurrent.futures,http.client,json,sys
from pathlib import Path
sys.path.insert(0,'/opt/ttd')
from guard import freeze_stage_a
body=json.loads(sys.argv[1])
expected=sys.argv[2]
assert freeze_stage_a(body)[1] == expected
def send(value, authenticated=True):
    conn=http.client.HTTPConnection('127.0.0.1',8081,timeout=6)
    try:
        headers={'Content-Type':'application/json'}
        if authenticated:
            headers['Authorization']='Bearer '+Path('/run/secrets/guard_service_token').read_text().strip()
        conn.request('POST','/v1/responses',json.dumps(value).encode(),headers)
        response=conn.getresponse()
        return response.status,response.read()
    finally:
        conn.close()
if sys.argv[3] == 'replay':
    assert send(body)[0] == 503
else:
    assert send(body,False)[0] == 401
    assert send(dict(body,instructions='tampered'))[0] == 503
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        results=list(pool.map(lambda i:send(dict(body,prompt_cache_key=str(i))),range(8)))
    assert sorted(status for status,_ in results) == [200]+[503]*7
    assert ('resp_mock_'+expected[:16]).encode() in next(raw for status,raw in results if status==200)
    assert send(body)[0] == 503
"""


def run(root):
    require(root.resolve() == root and root.parent == Path("/var/tmp")
            and re.fullmatch(r"ttd-h6-b1-[a-z0-9_]{8}", root.name), "fixture root identity")
    prepared = json.loads((root / "prepared.json").read_bytes())
    project = prepared["project"]
    require(project == root.name and root.stat().st_uid == 0 and stat.S_IMODE(root.stat().st_mode) == 0o700,
            "fixture root permissions")
    for name in (*STAGE_A_FILES, B1_OVERLAY):
        require(checksum((root / "src" / name).read_bytes()) == prepared["sources"][name], "source drift")
    before = baseline(prepared["ports"], project)
    require(before == json.loads((root / "baseline.json").read_bytes()), "pre-apply baseline drift")
    config_bytes = render(root, project)
    require(config_bytes == (root / "rendered.json").read_bytes(), "reviewed Compose changed")
    config = json.loads(config_bytes)
    mounts = plan(root, project, config, before)
    require(mounts == prepared["mounts"], "reviewed mounts changed")
    image = json.loads(docker("image", "inspect", IMAGE))[0]
    require(set(image["Config"]["Volumes"] or {}) == {"/opt/data"} and not image["Config"].get("ExposedPorts")
            and clean_environment(image["Config"]["Env"]), "unexpected pinned image defaults")
    sys.path.insert(0, str(root / "src"))
    from h6_stage_a_test import BODY

    test_name = project + "-contract"
    fixture_path = root / "fixture/mock-ledger/level2-budget.json"
    try:
        docker("compose", "--env-file", "/dev/null", "-f", str(root / "rendered.json"), "-p", project,
               "--project-directory", str(root / "src"), "up", "-d", "--no-build", "--pull", "never",
               "--wait", "--wait-timeout", "35", *sorted(SERVICES), timeout=45)
        index, networks = confirm_owned(root, project, mounts, complete=True)
        verify_runtime(index, networks[0], config, image)
        for name, container in index.items():
            docker("exec", container["Id"], "python3", "-B", "-c", NO_BYPASS, name, *before["proxy_ips"])
        writer_id = index["h6-writer"]["Id"]
        guard_id = index["guard"]["Id"]
        mock_id = index["provider-mock"]["Id"]
        socket_info = docker("exec", writer_id, "stat", "-c", "%u:%g:%a", "/opt/ttd/h6-ipc/writer.sock").decode().strip()
        require(socket_info == "23062:23060:660", "live writer socket identity")
        with fixture_path.open("rb") as old_file:
            docker("exec", guard_id, "python3", "-B", "-c", HTTP_TEST, json.dumps(BODY), prepared["digest"], "once")
            after = fixture_path.read_bytes()
            final = json.loads(after)
            require(json.load(old_file)["attempts"] == 1 and final["attempts"] == 2
                    and final["kill_switch"] is True and final["one_shot_permits"]["gate-b"]["state"] == "consumed"
                    and final["tasks"]["gate-b"]["state"] == "usage_recorded" and final["reserved_usd"] == 0.007,
                    "runtime disposable ledger result")
        docker("restart", "--timeout", "2", writer_id)
        for _ in range(25):
            status = json.loads(docker("container", "inspect", writer_id))[0]["State"]["Health"]["Status"]
            if status == "healthy":
                break
            time.sleep(0.4)
        require(status == "healthy", "writer restart health")
        docker("exec", guard_id, "python3", "-B", "-c", HTTP_TEST, json.dumps(BODY), prepared["digest"], "replay")
        require(fixture_path.read_bytes() == after, "restart changed disposable ledger")
        logs = docker("logs", mock_id).decode().splitlines()
        hits = sum(json.loads(line).get("path") == "/v1/responses" for line in logs if line.startswith('{"event"'))
        require(hits == 1, "mock dispatch total")
        matrix = docker("run", "--rm", "--name", test_name, "--label", "ttd.h6b1.contract=" + project,
                        "--network", "none", "--pull", "never", "--read-only", "--user", "0:0",
                        "--entrypoint", "python3", "--security-opt", "no-new-privileges:true",
                        "--tmpfs", "/tmp:rw,nosuid,size=24m",
                        "--mount", "type=tmpfs,target=/opt/data,tmpfs-size=8388608",
                        "--mount", f"type=bind,source={root / 'src'},target=/src,readonly",
                        "--workdir", "/src", "--pids-limit", "128", "--memory", "256m", "--cpus", "0.5",
                        IMAGE, "-B", "h6_stage_a_test.py", timeout=60)
        result = json.loads(matrix.decode().splitlines()[-1])
        require(result["result"] == "PASS" and len(result["cases"]) == 8, "contract matrix")
        print("B1_MOCK_RUNTIME_PASS " + json.dumps({"render_sha256": checksum(config_bytes), "mock_dispatches": hits,
                                                    "socket": socket_info, "matrix": result["cases"],
                                                    "mock_wire_sha256": prepared["digest"],
                                                    "writer_restart_ledger_unchanged": True,
                                                    "fixture_ledger_sha256": checksum(after)}), flush=True)
    finally:
        test = [c for c in objects("container") if c["Name"] == "/" + test_name]
        for c in test:
            require((c["Config"]["Labels"] or {}).get("ttd.h6b1.contract") == project, "ambiguous contract cleanup")
            docker("rm", "-f", c["Id"])
        index, networks = confirm_owned(root, project, mounts)
        for c in index.values():
            docker("rm", "-f", c["Id"])
        for network in networks:
            docker("network", "rm", network["Id"])
        require(not selected(project) and not any((n["Labels"] or {}).get(PROJECT_LABEL) == project
                                                  for n in objects("network")), "B1 cleanup incomplete")
        require(baseline(prepared["ports"], project) == before, "postflight baseline drift")
        shutil.rmtree(root)
        print("B1_ROLLBACK_PASS preexisting_baseline_equal=true project_removed=true fixture_removed=true", flush=True)


if __name__ == "__main__":
    require(os.geteuid() == 0, "host operator identity")
    if sys.argv[1:2] == ["prepare"] and len(sys.argv) == 4:
        prepare([int(port) for port in sys.argv[2:]])
    elif sys.argv[1:2] == ["run"] and len(sys.argv) == 3:
        run(Path(sys.argv[2]))
    else:
        raise SystemExit("usage: h6_b1_rehearsal.py prepare N8N_HEALTH_PORT HERMES_HEALTH_PORT | run PRIVATE_ROOT")
