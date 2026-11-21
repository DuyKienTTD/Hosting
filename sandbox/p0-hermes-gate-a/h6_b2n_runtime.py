"""Render, run and remove only a dedicated local synthetic B2-N Compose project."""

import argparse
from copy import deepcopy
import json
import os
from pathlib import Path
import re
import secrets
import shutil
import subprocess
import tempfile
import uuid

from h6_b2n_n8n_provenance import BASE, candidate, canonical, compare, sha


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROJECT = "ttd-b2n-local"
HERMES = "ghcr.io/hostinger/hvps-hermes-agent@sha256:0ea63377bd672cb76de6a8510aaaef619fe2a045558b771656c072ef527c344f"
N8N = "docker.n8n.io/n8nio/n8n@sha256:9a8d8dcea75667496695d7810d7e1fe018a65efb36cc499d347f3931b3957b5d"
PYTHON = "python@sha256:c5ba3deef00c7758561a0f03c26f44f10589263d40e732b8748e0d1f38f6dd89"
PROJECTION = "08aa63bcfaf27f9ced2a5374ce67f4683877f615ed00dafea086f608321dde0d"
SERVICES = {"n8n", "hermes", "provider", "receipt", "driver"}
VOLUMES = {"n8n", "hermes", "provider", "receipt", "driver"}


def require(condition, text):
    if not condition:
        raise RuntimeError(text)


def docker(*args, input_data=None, timeout=30):
    env = {key: value for key, value in os.environ.items()
           if not key.startswith(("COMPOSE_", "DOCKER_"))}
    proc = subprocess.run(["docker", *args], input=input_data, capture_output=True, timeout=timeout, env=env)
    if proc.returncode:
        # The local project contains generated fake values only. Keep captured diagnostics bounded.
        print(proc.stdout.decode(errors="replace")[-2000:], flush=True)
        print(proc.stderr.decode(errors="replace")[-2000:], flush=True)
        raise RuntimeError(f"Docker {args[0]} failed")
    return proc.stdout


def target_workflow():
    return candidate((ROOT / "sandbox/p0-level1/fake-ads-audit-v1.workflow.json").read_bytes(),
                     (HERE / "workflow_gate_a.py").read_bytes())


def workflows(auth, route):
    public = target_workflow()
    baseline = json.loads(json.dumps(public).replace("__P0_TOKEN__", auth))
    for node in baseline["nodes"]:
        if node["id"] == "call-reasoner":
            node["parameters"]["url"] = "http://receipt:8083/v1/reason"
    altered = deepcopy(baseline)
    altered.update(id="b2nReceiptFlowV1", name="b2n-local-receipt-fixture")
    webhook = next(node for node in altered["nodes"] if node["id"] == "webhook-trigger")
    webhook["parameters"]["path"] = "b2n-receipt-fixture"
    webhook["webhookId"] = str(uuid.uuid4())
    altered["connections"]["Callback Phase?"]["main"][0][0]["node"] = "B2N Persist Receipt"
    altered["nodes"].extend([
        {"id": "b2n-call-receipt", "name": "B2N Persist Receipt", "type": "n8n-nodes-base.httpRequest",
         "typeVersion": 4.2, "position": [300, 100], "parameters": {
             "method": "POST", "url": "http://receipt:8083/receipt", "sendHeaders": True,
             "headerParameters": {"parameters": [{"name": "Authorization", "value": "Bearer " + route}]},
             "sendBody": True, "specifyBody": "json", "jsonBody": "={{ JSON.stringify($json.body) }}",
             "options": {"timeout": 5000, "response": {"response": {"fullResponse": True, "neverError": True}}}}},
        {"id": "b2n-respond-receipt", "name": "B2N Respond Receipt", "type": "n8n-nodes-base.respondToWebhook",
         "typeVersion": 1.4, "position": [540, 100], "parameters": {
             "respondWith": "json", "responseBody": "={{ JSON.stringify($json.body) }}",
             "options": {"responseCode": "={{ $json.statusCode }}"}}},
    ])
    altered["connections"]["B2N Persist Receipt"] = {"main": [[
        {"node": "B2N Respond Receipt", "type": "main", "index": 0}]]}
    return [baseline, altered]


def configure(path, owner):
    tokens = {f"B2N_{role}_BEARER": "fixture-" + secrets.token_hex(24)
              for role in ("HTTP", "ENGINE", "RECEIPT", "PROVIDER")}
    for name in ("h6_b2n_runtime_fixture.py", "provider_mock.py"):
        shutil.copyfile(HERE / name, path / name)
    (path / "workflows.json").write_bytes(canonical(workflows(tokens["B2N_HTTP_BEARER"], tokens["B2N_RECEIPT_BEARER"])))
    config = (HERE / "config.yaml").read_text(encoding="utf8").replace("gate-a-guard:8081", "provider:8082")
    (path / "hermes.yaml").write_text(config, encoding="utf8")
    fixture = {"type": "bind", "source": path.as_posix(), "target": "/b2n-src", "read_only": True,
               "bind": {"create_host_path": False}}
    def service(name, image, entrypoint, data, env):
        return {"image": image, "pull_policy": "never", "entrypoint": entrypoint, "command": [],
                "environment": env, "networks": ["private"], "read_only": True, "cap_drop": ["ALL"],
                "tmpfs": ["/tmp:rw,nosuid,nodev,size=64m"],
                "security_opt": ["no-new-privileges:true"], "pids_limit": 180,
                "labels": {"ttd.b2n.owner": owner}, "restart": "no",
                "volumes": [fixture, {"type": "volume", "source": name, "target": data}]}

    h_env = {"HOME": "/b2n-state/.hermes", "HERMES_HOME": "/b2n-state/.hermes",
             "API_SERVER_KEY": tokens["B2N_ENGINE_BEARER"], "OPENAI_API_KEY": tokens["B2N_PROVIDER_BEARER"],
             "OPENAI_BASE_URL": "http://provider:8082/v1", "HERMES_IGNORE_RULES": "1",
             "PYTHONDONTWRITEBYTECODE": "1", "HTTP_PROXY": "", "HTTPS_PROXY": "", "ALL_PROXY": "", "NO_PROXY": "*"}
    n_env = {"N8N_ENCRYPTION_KEY": "fixture-" + secrets.token_hex(24), "N8N_HOST": "n8n",
             "N8N_SECURE_COOKIE": "false", "N8N_DIAGNOSTICS_ENABLED": "false", "N8N_TEMPLATES_ENABLED": "false",
             "N8N_VERSION_NOTIFICATIONS_ENABLED": "false", "N8N_RUNNERS_ENABLED": "true",
             "N8N_HIRING_BANNER_ENABLED": "false", "N8N_ENFORCE_SETTINGS_FILE_PERMISSIONS": "true"}
    services = {
        "hermes": service("hermes", HERMES, ["/bin/sh", "-ec",
            "if [ ! -f /b2n-state/.b2n-initialized ]; then "
            "mkdir -p /b2n-state/.hermes; cp /b2n-src/hermes.yaml /b2n-state/.hermes/config.yaml; "
            "chown -R hermes:hermes /b2n-state/.hermes; touch /b2n-state/.b2n-initialized; fi; "
            "exec /command/s6-setuidgid hermes /opt/hermes/.venv/bin/hermes gateway run --no-supervise --force"],
            "/b2n-state", h_env),
        "n8n": service("n8n", N8N, ["/bin/sh", "-ec",
            "if [ ! -f /home/node/.n8n/.b2n-seeded ]; then "
            "n8n import:workflow --input=/b2n-src/workflows.json; "
            "n8n publish:workflow --id=ttdP0FakeAdsV1; "
            "n8n publish:workflow --id=b2nReceiptFlowV1; "
            "touch /home/node/.n8n/.b2n-seeded; fi; exec n8n start"], "/home/node/.n8n", n_env),
    }
    services["hermes"].update(user="0:0", init=True, cap_add=["CHOWN", "SETUID", "SETGID"])
    services["hermes"]["tmpfs"].append("/opt/data:rw,nosuid,nodev,noexec,size=8m")
    services["n8n"]["tmpfs"].append("/home/node/.cache:rw,nosuid,nodev,size=64m,mode=1777")
    for role in ("provider", "receipt", "driver"):
        runtime = ["python", "-B", "/b2n-src/h6_b2n_runtime_fixture.py", role]
        services[role] = service(role, PYTHON, runtime if role != "driver" else ["sleep", "infinity"],
                                 "/fixture-data", tokens)
    return {"services": services, "networks": {"private": {"internal": True, "labels": {"ttd.b2n.owner": owner}}},
            "volumes": {role: {"labels": {"ttd.b2n.owner": owner}} for role in VOLUMES}}


def validate(render, spec, path):
    require(render["name"] == PROJECT and set(render["services"]) == SERVICES
            and set(render["volumes"]) == VOLUMES and set(render["networks"]) == {"private"}
            and render.keys() == {"name", "services", "volumes", "networks"}, "unexpected resource")
    net = render["networks"]["private"]
    require(net["internal"] and not net.get("external") and not net.get("enable_ipv6"), "network gate")
    for role, item in render["services"].items():
        for key in ("image", "pull_policy", "entrypoint", "command", "environment", "read_only", "cap_drop",
                    "security_opt", "pids_limit", "labels", "tmpfs"):
            require(item[key] == spec["services"][role][key], f"render changed {role}.{key}")
        require(not (set(item) & {"ports", "privileged", "devices", "ipc", "pid", "network_mode", "extra_hosts",
                                  "env_file", "secrets", "volumes_from"}) and set(item["networks"]) == {"private"}
                and set(item.get("cap_add", [])) == ({"CHOWN", "SETUID", "SETGID"} if role == "hermes" else set()),
                "unapproved namespace, port, security or external dependency")
        code, data = item["volumes"]
        require(code["source"] == path.as_posix() and code["target"] == "/b2n-src"
                and code["type"] == "bind" and code["read_only"] and not code["bind"]["create_host_path"]
                and data["type"] == "volume" and data["source"] == role
                and data["target"] == spec["services"][role]["volumes"][1]["target"], "mount gate")


def run(args):
    require(args.projection == PROJECTION and compare(target_workflow(), target_workflow())[
        "candidate_projection_sha256"] == PROJECTION, "published workflow projection gate")
    require(docker("context", "show").decode().strip() == "desktop-linux", "local context required")
    for ref in (HERMES, N8N, PYTHON):
        platform = docker("image", "inspect", "--format", "{{.Os}}/{{.Architecture}}", ref).decode().strip()
        require(platform == "linux/amd64", "pinned image platform mismatch")
    def project_ids(resource):
        base = {"container": ["ps", "-aq"], "volume": ["volume", "ls", "-q"],
                "network": ["network", "ls", "-q"]}[resource]
        return docker(*base, "--filter", f"label=com.docker.compose.project={PROJECT}").decode().splitlines()
    kinds = ("container", "volume", "network")
    require(not any(project_ids(kind) for kind in kinds), "project collision")
    with tempfile.TemporaryDirectory(prefix="h6-b2n-fixture-") as directory:
        path = Path(directory).resolve()
        owner = secrets.token_hex(12)
        spec = configure(path, owner)
        def compose(*options, timeout=60):
            return docker("compose", "--project-directory", str(path), "-p", PROJECT, "--profile", "*",
                          "-f", "-", *options, input_data=canonical(spec), timeout=timeout)
        config = json.loads(compose("config", "--format", "json"))
        validate(config, spec, path)
        print("B2N_PRE_UP", json.dumps({"services": sorted(SERVICES), "private_internal": True,
              "ports": 0, "own_volume_count": len(VOLUMES), "published_projection": PROJECTION}), flush=True)
        try:
            compose("up", "-d", "--no-build", "--pull", "never", timeout=90)
            for role in sorted(SERVICES):
                cid = compose("ps", "-a", "-q", role).decode().strip()
                require(re.fullmatch("[a-f0-9]{12,64}", cid), "local container missing")
                row, = json.loads(docker("inspect", cid))
                host = row["HostConfig"]
                mounts = {m["Destination"]: m for m in row["Mounts"] if m["Type"] != "tmpfs"}
                private = row["NetworkSettings"]["Networks"]
                require(row["State"]["Running"] and not host["PortBindings"] and host["ReadonlyRootfs"]
                        and not host["Privileged"]
                        and host["CapDrop"] == ["ALL"] and set(private) == {PROJECT + "_private"}
                        and set(mounts) == {"/b2n-src", spec["services"][role]["volumes"][1]["target"]}
                        and not mounts["/b2n-src"]["RW"], "runtime isolation mismatch")
            network, = json.loads(docker("network", "inspect", PROJECT + "_private"))
            require(network["Internal"] and not network["EnableIPv6"], "running network not internal")
            compose("exec", "-T", "driver", "python", "-B", "-c",
                    "assert all(r.split()[1] != '00000000' for r in open('/proc/net/route').readlines()[1:])")
            print("B2N_RUNTIME_ISOLATION_PASS", flush=True)
            for stage in ("one", "two", "three"):
                if stage != "one":
                    compose("restart", "hermes" if stage == "two" else "receipt", timeout=45)
                print(compose("exec", "-T", "driver", "python", "-B", "/b2n-src/h6_b2n_runtime_fixture.py",
                              stage, timeout=120).decode(), end="", flush=True)
        except Exception:
            print(compose("logs", "--tail", "28", "hermes", "n8n", "receipt", timeout=15).decode(), flush=True)
            raise
        finally:
            for kind in kinds:
                label_path = ".Config.Labels" if kind == "container" else ".Labels"
                require(all(docker(kind, "inspect", "--format", '{{index ' + label_path + ' "ttd.b2n.owner"}}', item
                                   ).decode().strip() == owner for item in project_ids(kind)),
                        "refuse cleanup of unowned " + kind)
            compose("down", "--volumes", "--timeout", "2", timeout=40)
            require(not any(project_ids(kind) for kind in kinds), "fixture cleanup incomplete")
            print("B2N_ROLLBACK_PASS", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--projection", required=True)
    run(parser.parse_args())
