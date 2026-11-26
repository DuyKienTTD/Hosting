"""Exercise release.sh with real Postgres and an isolated registry/host fixture."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

SOURCE = Path(__file__).resolve().parent


def run(args, directory=None, env=None, stdin=None):
    return subprocess.run(args, cwd=directory, env=env, input=stdin, check=True,
                          text=True, capture_output=True).stdout.strip()


def fixture_bin(directory):
    binary = directory / "bin"
    binary.mkdir()
    transport = {name: os.environ[name] for name in ("PGHOST", "PGPORT", "PGUSER", "PGDATABASE",
        "LD_LIBRARY_PATH", "RELEASE_TEST_POSTGRES_CONTAINER", "RELEASE_TEST_DOCKER") if name in os.environ}
    (directory / "transport.json").write_text(json.dumps(transport))
    program = r'''#!/usr/bin/env python3
import json
import os
import pathlib
import subprocess
import sys
name = pathlib.Path(sys.argv[0]).name
args = sys.argv[1:]
root = pathlib.Path(sys.argv[0]).resolve().parent.parent
transport = json.loads((root / "transport.json").read_text())
with (root / "commands").open("a") as out:
    print(name, *args, file=out)
if name in ("psql", "pg_dump", "pg_restore"):
    os.execv(transport["RELEASE_TEST_DOCKER"], ["docker", "exec", "-i",
              "-e", "PGUSER=postgres", "-e", "PGDATABASE=postgres",
              transport["RELEASE_TEST_POSTGRES_CONTAINER"], name, *args])
if name == "gh":
    if args[:2] == ["attestation", "verify"]:
        assert "refs/heads/dev/ttd-zalo-mvp01" in args
    elif args[:2] == ["run", "list"]:
        print(123)
    elif args[:2] == ["run", "download"]:
        commit = args[args.index("--name") + 1].removeprefix("release-")
        target = pathlib.Path(args[args.index("--dir") + 1])
        (target / "release-manifest.json").write_bytes((root / (commit + ".json")).read_bytes())
    else:
        raise SystemExit("unexpected gh invocation")
elif name == "docker":
    assert not ({"AI_ROUTER_API_KEY", "ZALO_APP_SECRET", "OA_MODE", "COMPOSE_FILE"} & os.environ.keys())
    if args[0] == "pull":
        assert "@sha256:" in args[1]
    elif args[0] == "compose":
        action = args[7]
        assert args[1:3] == ["-p", "fixture"]
        if action == "config":
            values = dict(line.split("=", 1) for line in pathlib.Path(args[4]).read_text().splitlines())
            assert values["AI_ROUTER_API_KEY"] == "fixture_file_router"
            assert values["ZALO_APP_SECRET"] == "fixture_file_oa"
            if "RELEASE_TEST_DOCKER" in transport:
                output = subprocess.check_output([transport["RELEASE_TEST_DOCKER"], *args[:8], "--format", "json"])
                environment = json.loads(output)["services"]["runtime"]["environment"]
                assert environment["AI_ROUTER_API_KEY"] == values["AI_ROUTER_API_KEY"]
                assert environment["ZALO_APP_SECRET"] == values["ZALO_APP_SECRET"]
        if action == "exec":
            assert args[8:10] == ["-T", "postgres"]
            command = args[10:]
            if command[0] == "sh":
                sql = command[2]
                command = (["pg_dump", "-Fc"] if "pg_dump" in sql else
                           ["psql", "-X", "-q", "-v", "ON_ERROR_STOP=1", *command[4:]])
            os.execvpe(command[0], command, {**os.environ, **transport})
        assert action in ("stop", "up", "config")
    else:
        raise SystemExit("unexpected docker invocation")
elif name == "nginx":
    assert args == ["-t"]
    if "refuse-nginx" in (root / "site.conf").read_text():
        raise SystemExit(1)
elif name == "systemctl":
    assert args == ["reload", "nginx"]
elif name == "curl":
    path = args[-1].removeprefix("https://fixture.invalid")
    status = {"/health": 200, "/": 200, "/webhooks/zalo-oa": 200, "/internal": 404}[path]
    if path == "/webhooks/zalo-oa":
        assert "X-ZEvent-Signature: mac=invalid" in args
    pathlib.Path(args[args.index("--output") + 1]).write_text(json.dumps({"error": 0}))
    print(status, end="")
'''
    names = ["docker", "gh", "nginx", "systemctl", "curl"]
    if os.environ.get("RELEASE_TEST_POSTGRES_CONTAINER"):
        names.extend(["psql", "pg_dump", "pg_restore"])
    for name in names:
        path = binary / name
        path.write_text(program)
        path.chmod(0o755)
    return binary


def main():
    container = os.environ.get("RELEASE_TEST_POSTGRES_CONTAINER")
    if container:
        os.environ["RELEASE_TEST_DOCKER"] = shutil.which("docker")
    with tempfile.TemporaryDirectory() as folder:
        root = Path(folder)
        checkout = root / "src"
        deploy = checkout / "deploy"
        postgres = checkout / "apps/ttd-zalo-agent-server/postgres"
        ops = postgres.parent / "ops"
        postgres.mkdir(parents=True)
        ops.mkdir()
        (deploy / "nginx").mkdir(parents=True)
        for module in ("release.sh", "release-manifest.py"):
            shutil.copy(SOURCE / module, deploy / module)
        (deploy / "compose.prod.yml").write_text(
            "services:\n  runtime:\n    image: fixture:local\n    environment:\n"
            "      AI_ROUTER_API_KEY: ${AI_ROUTER_API_KEY:?missing}\n"
            "      ZALO_APP_SECRET: ${ZALO_APP_SECRET:?missing}\n")
        (ops / "fixture").touch()
        run(["git", "init", "-q"], checkout)
        run(["git", "config", "user.name", "Fixture"], checkout)
        run(["git", "config", "user.email", "fixture@example.invalid"], checkout)
        nginx = deploy / "nginx/cskh-https.conf"
        site = root / "site.conf"
        site.write_text("bootstrap nginx\n")
        initial = "BEGIN;\nCREATE TABLE public.fixture_data(id integer PRIMARY KEY);\nCOMMIT;\n"
        (postgres / "001.sql").write_text(initial)
        env_file = root / "fixture.env"
        other = "OA_MODE=live\nAI_MODE=mock\nCHANNEL_SMOKE_ONLY=1\nSMOKE_ALLOWLIST=fixture\nSTOP=1\nAI_ROUTER_API_KEY=fixture_file_router\nZALO_APP_SECRET=fixture_file_oa\n"
        env_file.write_text("DATA_APP_IMAGE=fixture/runtime:previous\nDATA_POSTGRES_IMAGE=fixture/postgres:previous\n" + other)
        env = {**os.environ, "PATH": str(fixture_bin(root)) + ":" + os.environ["PATH"],
               "AI_ROUTER_API_KEY": "fixture_shell_router", "ZALO_APP_SECRET": "fixture_shell_oa",
               "OA_MODE": "fixture_shell_mode", "COMPOSE_FILE": "/ignored/fixture.yml", "RELEASE_ENV_FILE": str(env_file),
               "RELEASE_STATE_DIR": str(root / "state"), "RELEASE_NGINX_SITE": str(site),
               "RELEASE_SMOKE_ORIGIN": "https://fixture.invalid", "RELEASE_COMPOSE_PROJECT": "fixture"}
        state = root / "state"
        run(["psql", "-X", "-v", "ON_ERROR_STOP=1"], env=env, stdin=initial + "INSERT INTO fixture_data VALUES(42);")

        def new_release(label):
            nginx.write_text(label + "\n")
            run(["git", "add", "."], checkout)
            run(["git", "commit", "-qm", label], checkout)
            commit = run(["git", "rev-parse", "HEAD"], checkout)
            manifest = root / (commit + ".json")
            digest = "sha256:" + hashlib.sha256(label.encode()).hexdigest()
            manifest.write_text(run(["python3", "deploy/release-manifest.py", "build", commit, digest, digest], checkout))
            return commit, manifest

        def release(*args, error=None):
            cmd = ["bash", deploy / "release.sh", *args]
            proc = subprocess.run(cmd, cwd=checkout, env=env, text=True, capture_output=True)
            if error:
                assert proc.returncode != 0 and error in proc.stderr, (proc.stdout, proc.stderr)
            else:
                assert proc.returncode == 0, (proc.stdout, proc.stderr)
                assert "Smoke passed:" in proc.stdout
            assert env_file.read_text().splitlines(keepends=True)[2:] == other.splitlines(keepends=True)
            return proc.stdout

        a, manifest_a = new_release("nginx release A")
        release(manifest_a, error="untracked database")
        release("--adopt-through", "001.sql", manifest_a)
        assert json.loads((state / "current.json").read_text())["commit"] == a
        old_env = env_file.read_bytes()

        _, bad = new_release("refuse-nginx")
        failure = subprocess.run(["bash", deploy / "release.sh", bad], cwd=checkout, env=env)
        assert failure.returncode != 0
        assert site.read_text() == "nginx release A\n" and env_file.read_bytes() == old_env
        assert json.loads((state / "current.json").read_text())["commit"] == a

        b, _ = new_release("nginx release B")
        release(b)
        assert site.read_text() == "nginx release B\n"
        release("--rollback")
        assert site.read_text() == "nginx release A\n" and env_file.read_bytes() == old_env

        (postgres / "003-next.sql").write_text("BEGIN;\nALTER TABLE fixture_data ADD COLUMN note text;\nCOMMIT;\n")
        c, manifest_c = new_release("nginx release C")
        assert "apply|003-next.sql|" in release(manifest_c)
        assert run(["psql", "-Atc", "SELECT id FROM fixture_data"], env=env) == "42"
        assert run(["psql", "-Atc", "SELECT count(*) FROM release_migrations"], env=env) == "2"
        dumps = list((state / "backups").glob(c + "-*.dump"))
        assert len(dumps) == 1
        with dumps[0].open("rb") as dump:
            listing = subprocess.run(["pg_restore", "-l"], stdin=dump, check=True, capture_output=True, env=env)
        assert b"fixture_data" in listing.stdout
        release("--rollback", manifest_a, error="not an exact prefix")
        assert "apply|" not in release(manifest_c)
        migration = postgres / "003-next.sql"
        original = migration.read_text()
        migration.write_text(original.replace("ADD COLUMN note text", "ADD COLUMN note varchar(10)"))
        _, changed = new_release("changed applied checksum")
        release(changed, error="not an exact prefix")
        assert run(["psql", "-Atc", "SELECT count(*) FROM release_migrations"], env=env) == "2"
        migration.write_text(original)


        (postgres / "005-broken.sql").write_text("BEGIN;\nCREATE TABLE fixture_partial(id integer);\nBAD SQL;\nCOMMIT;\n")
        _, broken = new_release("broken SQL")
        release(broken, error="App services stopped")
        assert run(["psql", "-Atc", "SELECT to_regclass('fixture_partial') IS NULL"], env=env) == "t"
        assert run(["psql", "-Atc", "SELECT count(*) FROM release_migrations"], env=env) == "2"
        assert json.loads((state / "current.json").read_text())["commit"] == c
        print("PASS: manifest and commit, adoption, pg_dump, ordered migration, Nginx recovery, rollback and smoke")


if __name__ == "__main__":
    main()
