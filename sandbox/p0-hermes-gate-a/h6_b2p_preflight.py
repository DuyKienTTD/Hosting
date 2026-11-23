"""Render a fake-only B2-P candidate locally. This module cannot start a project."""

import argparse
import ast
from copy import deepcopy
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import secrets
import tempfile

import h6_b2o_run as b2o
from h6_b2n_runtime import compare, target_workflow


PROJECT = "h6-b2-p-fake-candidate"
OWNER_LABEL = "ttd.b2p.owner"
CASE_PROFILE = "fake"
BASE_EVIDENCE = (b2o.HERE.parents[1] / "reports" / "evidence" /
                 "2026-11-22-ttd-hermes-gate-b-h6-b2-o-integrated-fake.json")
BASE = "d95f1619d3e82d9bfe38ea583d50b1f5b1a5a810"
# Pin the B2-O synthetic import template, independently of the published baseline.
CANDIDATE_PROJECTION_SHA256 = "439624f3e3dede91f75ad6f12df4fbd9d3104fab1f9bc41e227846acef0cde3a"
LIMITS = {
    "n8n": ("0.45", "640m"), "hermes": ("0.45", "1024m"), "bridge": ("0.10", "128m"),
    "guard": ("0.10", "128m"), "provider": ("0.10", "96m"), "receipt": ("0.10", "96m"),
    "writer": ("0.10", "96m"), "driver": ("0.10", "96m"),
}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def verified_projection(workflow):
    computed = compare(workflow, workflow)["candidate_projection_sha256"]
    b2o.require(computed == b2o.PROJECTION, "published workflow projection drift")
    return computed


def verify_timer(events):
    slow = [event for event in events if event["task"] == "b2o-46"]

    def observed(name, role):
        matched = [event["mono_ns"] for event in slow if event["event"] == name and event["role"] == role]
        b2o.require(len(matched) == 1 and type(matched[0]) is int, f"expected one {role}/{name} event")
        return matched[0]

    connected = observed("transport_connected", "guard")
    posted = observed("transport_post", "guard")
    dispatch = observed("provider_post_committed", "provider")
    timers = [event for event in slow if event["event"] == "guard_response_timer_fired"]
    b2o.require(len(timers) == 1 and timers[0].get("role") == "guard"
                and type(timers[0].get("mono_ns")) is int, "expected one Guard response timer for b2o-46")
    timer = timers[0]["mono_ns"]
    read_end = observed("transport_read_ended", "guard")
    late = observed("provider_response_attempt", "provider")
    b2o.require(connected <= posted <= dispatch < timer < read_end < late
                and 44.5 < (timer - connected) / 1e9 < 45.8, "Guard timer did not precede the read cutoff")
    return {"connected_to_timer_s": (timer - connected) / 1e9,
            "timer_to_read_end_s": (read_end - timer) / 1e9}


def verified_candidate_projection(raw, spec):
    """Pin the complete import JSON, normalizing only four generated fixture values."""
    try:
        services = spec["services"]
        bridge_env = services["bridge"]["environment"]
        webhook, admit = bridge_env["B2O_WEBHOOK"], bridge_env["B2O_ADMIT"]
        receive = services["receipt"]["environment"]["B2O_RECEIVE"]
        b2o.require(all(isinstance(token, str) and re.fullmatch(r"fixture-[a-f0-9]{48}", token)
                        for token in (webhook, admit, receive))
                    and len({webhook, admit, receive}) == 3, "invalid staged synthetic bearer values")
        b2o.require(services["driver"]["environment"]["B2O_WEBHOOK"] == webhook
                    and services["driver"]["environment"]["B2O_ADMIT"] == admit, "fixture bearer binding drift")
        workflow, = json.loads(raw)
        b2o.require(b2o.canonical([workflow]) == raw, "candidate workflow must use canonical import bytes")
        nodes = {node["id"]: node for node in workflow["nodes"]}
        b2o.require(len(nodes) == len(workflow["nodes"]), "duplicate candidate node identity")
        trigger = nodes["webhook-trigger"]
        b2o.require(re.fullmatch(r"[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}",
                                trigger["webhookId"]), "invalid generated webhook identity")
        trigger["webhookId"] = "<generated-webhook-uuid>"

        params = nodes["auth-router"]["parameters"]
        literal = f"'{webhook}'"
        b2o.require(params["jsCode"].count(literal) == 1, "candidate webhook bearer binding drift")
        params["jsCode"] = params["jsCode"].replace(literal, "'<generated-webhook-bearer>'", 1)

        for node, token, role in (("call-reasoner", admit, "admit"), ("b2n-call-receipt", receive, "receive")):
            header, = nodes[node]["parameters"]["headerParameters"]["parameters"]
            b2o.require(header == {"name": "Authorization", "value": f"Bearer {token}"},
                        "candidate HTTP bearer binding drift")
            header["value"] = f"Bearer <generated-{role}-bearer>"
    except (AttributeError, KeyError, TypeError, ValueError) as exc:
        raise RuntimeError("invalid candidate workflow import structure") from exc
    projection = digest(b2o.canonical([workflow]))
    b2o.require(projection == CANDIDATE_PROJECTION_SHA256, "staged candidate workflow projection drift")
    return projection


def verify_staged_workflow(path, expected_sha256):
    """Check a staged or copied import against the exact digest of its verified bytes."""
    b2o.require(isinstance(expected_sha256, str) and re.fullmatch(r"[a-f0-9]{64}", expected_sha256),
                "missing exact staged workflow digest")
    b2o.require(digest(path.read_bytes()) == expected_sha256, "staged workflow bytes changed")


def prepare(path, owner):
    b2o.require(re.fullmatch("[0-9a-f]{32}", owner), "invalid synthetic owner")
    spec, config_sha = b2o.specification(path, owner)
    staged = path / "workflows.json"
    raw = staged.read_bytes()
    workflow = {
        "stage": "LOCAL_TEMPORARY_STAGED_VERIFIED",
        "file": staged.name,
        "candidate_normalized_projection_sha256": verified_candidate_projection(raw, spec),
        "approved_candidate_projection_sha256": CANDIDATE_PROJECTION_SHA256,
        "candidate_staged_file_sha256": digest(raw),
        "kvm2_staging": "NOT_PERFORMED",
        "n8n_import": "NOT_RUN",
    }
    source = "/tmp/h6-b2p-src-" + owner
    for role, service in spec["services"].items():
        mount = service["volumes"][0]
        mount["source"] = source
        mount["bind"]["propagation"] = "rprivate"
        cpus, mem_limit = LIMITS[role]
        service.update(labels={OWNER_LABEL: owner}, profiles=[CASE_PROFILE],
                       platform="linux/amd64", cpus=cpus, mem_limit=mem_limit)
    for item in spec["volumes"].values():
        item["labels"] = {OWNER_LABEL: owner}
    for item in spec["networks"].values():
        item.update(labels={OWNER_LABEL: owner}, driver="bridge",
                    driver_opts={"com.docker.network.bridge.gateway_mode_ipv4": "isolated"})
    return spec, config_sha, source, workflow


def validate(render, expected, owner, source):
    b2o.require(render["name"] == PROJECT and render.keys() == expected.keys() | {"name"}, "bad project")
    for group in ("services", "networks", "volumes"):
        b2o.require(render[group].keys() == expected[group].keys(), f"unexpected {group}")
    for kind in ("networks", "volumes"):
        for name, row in render[kind].items():
            defaults = {"ipam": {}} if kind == "networks" else {}
            actual = expected[kind][name] | defaults | {"name": f"{PROJECT}_{name}"}
            b2o.require(row == actual, f"unexpected {kind} definition")
    for role, service in render["services"].items():
        wanted = expected["services"][role]
        b2o.require(service.keys() == wanted.keys(), "unexpected service fields")
        for key in service.keys() - {"networks", "cpus", "mem_limit"}:
            b2o.require(service[key] == wanted[key], f"render mismatch {role}.{key}")
        b2o.require(set(service["networks"]) == set(b2o.NETWORKS[role])
                    and all(not v for v in service["networks"].values()), "unexpected network options")
        cpus, memory = LIMITS[role]
        b2o.require(float(service["cpus"]) == float(cpus)
                    and int(service["mem_limit"]) == int(memory[:-1]) * 1024 ** 2, "resource limit mismatch")
        bind, *volumes = service["volumes"]
        b2o.require(bind == {"type": "bind", "source": source, "target": "/b2n-src", "read_only": True,
                             "bind": {"propagation": "rprivate", "create_host_path": False}}, "unsafe source bind")
        b2o.require(PurePosixPath(source).parent == PurePosixPath("/tmp")
                    and source == "/tmp/h6-b2p-src-" + owner, "unsafe staging path")
        b2o.require(len(volumes) == int(role in b2o.VOLUMES), "unowned persistent mount")
        for volume in volumes:
            b2o.require(volume["type"] == "volume" and volume["source"] == role
                        and render["volumes"][role]["labels"] == {OWNER_LABEL: owner}, "unowned volume")


def public_projection(render, source):
    redacted = deepcopy(render)
    for role in redacted["services"].values():
        role["environment"] = {key: "<redacted-synthetic-config>" for key in sorted(role["environment"])}
        role["volumes"][0]["source"] = source[: -32] + "<owner-nonce>"
    for group in ("services", "networks", "volumes"):
        for row in redacted[group].values():
            row["labels"][OWNER_LABEL] = "<owner-nonce>"
    return redacted


def render_candidate():
    projection = verified_projection(target_workflow())
    baseline = json.loads(BASE_EVIDENCE.read_bytes())
    b2o.require(baseline["verdict"] == "B2O_INTEGRATED_FAKE_PASS"
                and baseline["n8n_base_projection_sha256"] == projection, "B2-O evidence mismatch")
    b2o.verify_results(baseline)
    trace = verify_timer(baseline["events"])
    parsed = ast.parse((b2o.HERE / "h6_provider.py").read_bytes())
    switches = [ast.literal_eval(node.value) for node in parsed.body if isinstance(node, ast.Assign)
                and any(isinstance(target, ast.Name) and target.id == "LIVE_ENABLED" for target in node.targets)]
    b2o.require(switches == [False], "live provider build is not locked")
    b2o.require(b2o.docker("context", "inspect", "desktop-linux", "--format", "{{.Endpoints.docker.Host}}"
                           ).decode().strip() == "npipe:////./pipe/dockerDesktopLinuxEngine", "local context mismatch")
    with tempfile.TemporaryDirectory(prefix="h6-b2p-render-") as directory:
        path, owner = Path(directory).resolve(), secrets.token_hex(16)
        spec, config_sha, source, workflow = prepare(path, owner)
        staged = path / workflow["file"]
        verify_staged_workflow(staged, workflow["candidate_staged_file_sha256"])
        opts = ("--context", "desktop-linux", "compose", "--project-directory", str(path), "-p", PROJECT,
                "--profile", "*", "-f", "-", "config", "--format", "json", "--no-path-resolution")
        wire = b2o.canonical(spec)
        first = b2o.docker(*opts, input_data=wire)
        second = b2o.docker(*opts, input_data=wire)
        b2o.require(first == second, "Compose render not reproducible")
        render = json.loads(first)
        validate(render, spec, owner, source)
        verify_staged_workflow(staged, workflow["candidate_staged_file_sha256"])
        public = public_projection(render, source)
        path_manifest = {name: digest((path / name).read_bytes()) for name in sorted(b2o.DEPENDENCIES)}
    return {
        "fixture_base_commit": BASE, "verdict": "B2P_LOCAL_RENDER_PASS",
        "live_enabled": False, "b2o_recorded_trace_timer_check": trace,
        "workflow_base_projection_verified_sha256": projection,
        "workflow_provenance": {
            "historical_b2o_base_projection_sha256": baseline["n8n_base_projection_sha256"],
            "source_base_projection_sha256": projection,
            **workflow,
        },
        "hermes_fixture_config_sha256": config_sha,
        "staged_source_file_sha256": path_manifest, "redacted_render_sha256": digest(b2o.canonical(public)),
        "render_repeat_equal": True, "compose_all_profiles": True, "redacted_render": public,
        "resource_caps": {"total_vcpu": 1.5, "total_memory_mib": 2304},
        "planned_owned_resources": {
            "project": PROJECT, "owner_label": OWNER_LABEL, "owner_match_required_before_cleanup": True,
            "container_names": sorted(f"{PROJECT}-{role}-1" for role in b2o.NETWORKS),
            "network_names": sorted(row["name"] for row in render["networks"].values()),
            "volume_names": sorted(row["name"] for row in render["volumes"].values()),
            "bind_root": "/tmp/h6-b2p-src-<owner-nonce>",
        },
        "proxy_tls_and_idle": "NOT_MEASURED",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()
    observed = render_candidate()
    args.evidence.write_text(json.dumps(observed, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(observed["verdict"], observed["redacted_render_sha256"])
