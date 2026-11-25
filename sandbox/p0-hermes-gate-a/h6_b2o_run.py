"""Run and verify the B2-O integration delta on the isolated local Docker engine."""

import argparse
import hashlib
import json
from pathlib import Path
import secrets
import shutil
import tempfile

from h6_b2n_runtime import HERMES, HERE, N8N, PROJECTION, PYTHON, canonical, configure, docker, require, workflows


PROJECT = "ttd-b2o-local"
LABEL = "ttd.b2o.owner"
WORKFLOW = "b2oLocalFixture01"
ROLE_FILE = "h6_b2o_services.py"
NETWORKS = {
    "bridge": ("front", "runs", "binding"),
    "driver": ("front",),
    "guard": ("inference", "upstream", "accounting"),
    "hermes": ("runs", "inference"),
    "n8n": ("front", "callback"),
    "provider": ("upstream",),
    "receipt": ("binding", "callback"),
    "writer": ("accounting",),
}
ENV = {
    "bridge": ("WEBHOOK", "ADMIT", "ENGINE", "BIND", "EVENT_KEY", "RECEIPT_KEY"),
    "driver": ("WEBHOOK", "ADMIT"),
    "guard": ("GUARD", "WRITER", "UPSTREAM"),
    "provider": ("UPSTREAM",),
    "receipt": ("BIND", "RECEIVE", "EVENT_KEY", "RECEIPT_KEY"),
    "writer": ("WRITER",),
}
VOLUMES = {"bridge", "hermes", "n8n", "provider", "receipt", "writer"}
DEPENDENCIES = ("bridge.py", "config.yaml", "guard.py", ROLE_FILE, "h6_b2i_async_mock.py",
                "h6_b2k_services.py", "h6_ipc_auth.py", "h6_p0.py", "h6_provider.py",
                "h6_writer.py", "mock_contract.py", "one_shot.py", "provider_mock.py",
                "h6_b2n_runtime_fixture.py")


def scenario_workflow(tokens):
    _, workflow = workflows(tokens["WEBHOOK"], tokens["RECEIVE"])
    workflow.update(id=WORKFLOW, name="B2-O integrated fixture")
    nodes = {node["id"]: node["parameters"] for node in workflow["nodes"]}
    nodes["webhook-trigger"]["path"] = "b2o-integrated-fixture"
    admission = nodes["call-reasoner"]
    admission["url"] = "http://bridge:8080/jobs"
    admission["headerParameters"]["parameters"][0]["value"] = "Bearer " + tokens["ADMIT"]
    admission["options"]["response"] = {"response": {"fullResponse": True, "neverError": True}}
    nodes["respond-start"]["responseBody"] = "={{ JSON.stringify($json.body) }}"
    nodes["respond-start"]["options"]["responseCode"] = "={{ $json.statusCode }}"
    return workflow


def specification(path, owner):
    base = configure(path, owner)
    services = {role: base["services"][role] for role in ("n8n", "hermes")}
    tokens = {name: "fixture-" + secrets.token_hex(24) for names in ENV.values() for name in names}
    for name in DEPENDENCIES:
        shutil.copyfile(HERE / name, path / name)
    (path / "workflows.json").write_bytes(canonical([scenario_workflow(tokens)]))
    config = (HERE / "config.yaml").read_bytes().replace(b"gate-a-guard:8081", b"guard:8081")
    (path / "hermes.yaml").write_bytes(config)
    services["hermes"]["environment"].update(API_SERVER_KEY=tokens["ENGINE"], OPENAI_API_KEY=tokens["GUARD"],
                                              OPENAI_BASE_URL="http://guard:8081/v1")
    services["n8n"]["entrypoint"][-1] = (
        "if [ ! -f /home/node/.n8n/.b2o-seeded ]; then "
        "n8n import:workflow --input=/b2n-src/workflows.json; "
        f"n8n publish:workflow --id={WORKFLOW}; "
        "touch /home/node/.n8n/.b2o-seeded; fi; exec n8n start"
    )
    for role, names in ENV.items():
        base_service = base["services"]["driver"]
        code_mount = dict(base_service["volumes"][0])
        item = services[role] = {**base_service, "volumes": [code_mount], "environment": {
            "B2O_" + name: tokens[name] for name in names}}
        if role in VOLUMES:
            item["volumes"].append({"type": "volume", "source": role, "target": "/fixture-data"})
        if role == "driver":
            # The driver reuses the bounded fixture poller. It receives no other role's tokens.
            item["environment"].update({f"B2N_{name}_BEARER": "fixture-unused" for name in
                                        ("HTTP", "ENGINE", "RECEIPT", "PROVIDER")})
        else:
            item["entrypoint"] = ["python", "-B", "/b2n-src/" + ROLE_FILE, role]
    for role, item in services.items():
        item["networks"] = list(NETWORKS[role])
        item["labels"] = {LABEL: owner}
    return ({"services": services, "volumes": {role: {"labels": {LABEL: owner}} for role in sorted(VOLUMES)},
             "networks": {net: {"internal": True, "labels": {LABEL: owner}}
                          for net in sorted({net for nets in NETWORKS.values() for net in nets})}},
            hashlib.sha256(config).hexdigest())


def validate(render, spec):
    require(render.keys() == spec.keys() | {"name"} and render["name"] == PROJECT, "unexpected project")
    for group in ("services", "networks", "volumes"):
        require(render[group].keys() == spec[group].keys(), f"unexpected {group}")
    for group in ("networks", "volumes"):
        for name, expected in spec[group].items():
            defaults = {"ipam": {}} if group == "networks" else {}
            require(render[group][name] == expected | defaults | {"name": f"{PROJECT}_{name}"},
                    "external or unowned resource")
    for role, expected in spec["services"].items():
        item = render["services"][role]
        require(item.keys() == expected.keys(), "unapproved rendered fields: " + repr(item.keys() ^ expected.keys()))
        for key in item.keys() - {"networks", "volumes"}:
            require(item[key] == expected[key], f"render drift {role}.{key}")
        require(set(item["networks"]) == set(NETWORKS[role]), "wrong network")
        require(item["volumes"] == expected["volumes"], "wrong mount")


def verify_running(compose, spec, owner):
    for role, nets in NETWORKS.items():
        cid = compose("ps", "-q", role).decode().strip()
        require(len(cid) == 64, "fixture container not running")
        row, = json.loads(docker("inspect", cid))
        host = row["HostConfig"]
        expected = spec["services"][role]
        checks = {
            "running": row["State"]["Running"],
            "owner": row["Config"]["Labels"][LABEL] == owner,
            "image": row["Config"]["Image"] == expected["image"],
            "entrypoint": row["Config"]["Entrypoint"] == expected["entrypoint"],
            "rootfs": host["ReadonlyRootfs"],
            "host_exposure": not host["Privileged"] and not host["PortBindings"] and not host["Devices"],
            "capabilities": host["CapDrop"] == ["ALL"]
                and {cap.removeprefix("CAP_") for cap in (host["CapAdd"] or [])} == set(expected.get("cap_add", [])),
            "privilege_escalation": "no-new-privileges:true" in host["SecurityOpt"],
            "networks": set(row["NetworkSettings"]["Networks"]) == {f"{PROJECT}_{net}" for net in nets},
        }
        require(all(checks.values()), f"effective service drift: {role} " +
                ", ".join(key for key, passed in checks.items() if not passed))
        actual_env = dict(entry.split("=", 1) for entry in row["Config"]["Env"])
        require(all(actual_env.get(key) == val for key, val in expected["environment"].items()),
                "runtime environment mismatch")
        mounts = {mount["Destination"]: mount for mount in row["Mounts"] if mount["Type"] != "tmpfs"}
        require(set(mounts) == {item["target"] for item in expected["volumes"]}, "unexpected runtime mount")
        require(mounts["/b2n-src"]["Type"] == "bind" and not mounts["/b2n-src"]["RW"], "fixture bind not read-only")
        if role in VOLUMES:
            data = mounts[expected["volumes"][1]["target"]]
            require(data["Type"] == "volume" and data["Name"] == f"{PROJECT}_{role}" and data["RW"],
                    "wrong synthetic state volume")
    for net in spec["networks"]:
        row, = json.loads(docker("network", "inspect", f"{PROJECT}_{net}"))
        require(row["Internal"] and not row["EnableIPv6"] and row["Labels"][LABEL] == owner,
                "unexpected routing or network ownership")
    route_check = "assert all(r.split()[1]!='00000000' for r in open('/proc/net/route').readlines()[1:])"
    for role in ENV:
        compose("exec", "-T", role, "python", "-B", "-c", route_check)
    compose("exec", "-T", "n8n", "node", "-e",
            r"if(require('fs').readFileSync('/proc/net/route','utf8').split('\n').slice(1)"
            r".some(r=>r.split(/\s+/)[1]==='00000000'))process.exit(1)")
    compose("exec", "-T", "hermes", "/opt/hermes/.venv/bin/python", "-B", "-c", route_check + """
import socket
for name in ('provider', 'writer'):
    try:
        socket.getaddrinfo(name, 8082)
    except socket.gaierror:
        continue
    raise AssertionError('Hermes bypass DNS path')
""")


def traces(output):
    return [json.loads(line.split("B2O_EVENT ", 1)[1])
            for line in output.decode().splitlines() if "B2O_EVENT " in line]


def verify_results(results):
    events, rows = results["events"], results["snapshots"]
    require(rows["receipt"] == results["receipts_after_restart"], "receipt changed after local receiver restart")
    for role in ("bridge", "provider", "writer", "receipt"):
        require(len(rows[role]) == 2, f"unexpected number of {role} rows")
    for index, task in enumerate(("b2o-31", "b2o-46")):
        scoped = [event for event in events if event["task"] == task]

        def one(name, **fields):
            selected = [event for event in scoped if event["event"] == name
                        and all(event.get(key) == val for key, val in fields.items())]
            require(len(selected) == 1, f"{task} expected one {name} {fields}")
            return selected[0]

        short = index == 0
        expected = "mock_succeeded" if short else "outcome_unknown"
        state, writer, provider = (rows[role][index] for role in ("bridge", "writer", "provider"))
        receipt = next(row for row in rows["receipt"] if row["binding"]["task_id"] == task)
        binding = state["binding"]
        require(state["state"] == "delivered" and state["outcome"] == receipt["outcome"] == expected
                and binding == receipt["binding"]
                and state["receipt"] == one("receipt_committed")["receipt_sha256"] == one("callback_ack")["receipt_sha256"]
                and binding["run_id_sha256"] == state["stored_run_id_sha256"]
                == one("hermes_admission", http=202)["run_id_sha256"]
                and binding["request_sha256"] == one("n8n_admission", http=202)["request_sha256"]
                == one("admission_committed", http=202)["request_sha256"], f"{task} binding or delivery mismatch")
        require(provider["dispatches"] == 1 and provider["task"] == writer["task"] == task
                and provider["digest"] == writer["digest"] == one("transport_post")["wire_sha256"]
                == one("provider_post_committed")["wire_sha256"]
                and writer["success_count"] == int(short) and writer["state"] == ("settled" if short else "held")
                and writer["outcome"] == ("usage_recorded" if short else "outcome_unknown"),
                f"{task} physical dispatch or reserve/settlement mismatch")
        ordered = [one("reserve_committed"), one("writer_ack", operation="admit"),
                   one("transport_connect_start"), one("transport_connected"), one("transport_post"),
                   one("provider_post_committed")]
        ordered += ([one("provider_response_attempt"), one("transport_first_byte")] if short else
                    [one("transport_read_ended")])
        ordered += [one("writer_outcome_committed"), one("writer_ack", operation="settle"),
                    one("guard_http_response", http=200 if short else 503),
                    one("outcome_committed"), one("callback_sent"), one("receipt_committed"), one("callback_ack")]
        times = [event["mono_ns"] for event in ordered]
        require(times == sorted(times), f"{task} causal order mismatch")
        delay = (one("provider_response_attempt")["mono_ns"] - one("provider_post_committed")["mono_ns"]) / 1e9
        require(abs(delay - (31 if short else 46)) < 1, f"{task} synthetic delay mismatch")
        require(not any(event["event"] in {"adapter_deadline", "worker_stopped"} for event in scoped),
                f"{task} adapter interrupted")
        one("driver_observed_receipt", outcome=expected)
        if short:
            one("hermes_status_observed", app_status="completed")
        else:
            cutoff = (one("transport_read_ended")["mono_ns"] - one("transport_connected")["mono_ns"]) / 1e9
            require(44.5 < cutoff < 45.8 and one("transport_read_ended")["mono_ns"]
                    < one("provider_response_attempt")["mono_ns"]
                    and not any(event["event"] == "transport_first_byte" for event in scoped),
                    "first cutoff was not the Guard response budget")
            one("guard_outcome_unknown")
            require(any(event["event"] == "hermes_status_observed" and event["app_status"] in
                        {"failed", "unknown", "interrupted", "cancelled"} for event in scoped),
                    "Hermes terminal status unavailable")


def run(evidence):
    require(docker("context", "show").decode().strip() == "desktop-linux", "must use the local Docker Desktop context")
    for ref in (HERMES, N8N, PYTHON):
        require(docker("image", "inspect", "--format", "{{.Os}}/{{.Architecture}}", ref).decode().strip()
                == "linux/amd64", "pinned local image missing or wrong platform")
    kinds = {"container": ("ps", "-aq"), "network": ("network", "ls", "-q"), "volume": ("volume", "ls", "-q")}

    def resources():
        return {kind: docker(*command, "--filter", f"label=com.docker.compose.project={PROJECT}").decode().splitlines()
                for kind, command in kinds.items()}

    require(not any(resources().values()), "existing project resources")
    with tempfile.TemporaryDirectory(prefix="h6-b2o-fixture-") as directory:
        path, owner = Path(directory).resolve(), secrets.token_hex(16)
        spec, config_sha = specification(path, owner)

        def compose(*args, timeout=40):
            return docker("compose", "--project-directory", str(path), "-p", PROJECT, "--profile", "*", "-f", "-",
                          *args, input_data=canonical(spec), timeout=timeout)

        validate(json.loads(compose("config", "--format", "json")), spec)
        results = {"mode": "synthetic-local", "pre_up_all_profiles": True, "project": PROJECT,
                   "image_refs": {"hermes": HERMES, "n8n": N8N, "python": PYTHON},
                   "hermes_config_sha256": config_sha, "n8n_base_projection_sha256": PROJECTION,
                   "network_segments": NETWORKS, "fake_volumes": sorted(VOLUMES),
                   "events": [], "snapshots": {}, "verdict": "B2O_NOT_VERIFIED"}
        print("B2O_PRE_UP_PASS", flush=True)
        try:
            compose("up", "-d", "--no-build", "--pull", "never", timeout=90)
            verify_running(compose, spec, owner)
            results["effective_isolation_pass"] = True
            print("B2O_ISOLATION_PASS", flush=True)
            python = ["python", "-B", "/b2n-src/" + ROLE_FILE]
            results["events"] += traces(compose("exec", "-T", "driver", *python, "driver", timeout=175))
            for role in ("bridge", "guard", "provider", "receipt", "writer"):
                results["events"] += traces(compose("logs", "--no-color", role))
                if role != "guard":
                    results["snapshots"][role] = json.loads(compose("exec", "-T", role, *python, role, "snapshot"))
            compose("restart", "receipt")
            results["receipts_after_restart"] = json.loads(compose("exec", "-T", "receipt", *python, "receipt", "snapshot"))
            verify_results(results)
            results["verdict"] = "B2O_INTEGRATED_FAKE_PASS"
        except Exception:
            for role in ("bridge", "guard", "provider", "receipt", "writer"):
                observed = traces(compose("logs", "--no-color", role))
                print(json.dumps(observed[-10:]), flush=True)
            raise
        finally:
            for kind, ids in resources().items():
                field = ".Config.Labels" if kind == "container" else ".Labels"
                label = '{{index ' + field + ' "' + LABEL + '"}}'
                require(all(docker(kind, "inspect", "--format", label, item).decode().strip() == owner for item in ids),
                        "refuse cleanup of unowned project resource")
            compose("down", "--volumes", "--timeout", "2")
            require(not any(resources().values()), "synthetic resources remain")
            results["rollback_pass"] = True
            results["events"].sort(key=lambda event: event["mono_ns"])
            if evidence is not None:
                evidence.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
        print(results["verdict"], flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence", type=Path)
    run(parser.parse_args().evidence)
