"""Probe the packaged web app through the production HTTPS Nginx template in CI."""

import json
import re
import secrets
import subprocess
import sys
import tempfile
from pathlib import Path

HOST = "cskh.thuanthanhdat.com.vn"
ORIGIN = "https://" + HOST


def main():
    certificate, password_file = sys.argv[1:]
    passphrase = Path(password_file).read_text().rstrip("\n")
    with tempfile.TemporaryDirectory() as directory:
        def request(path, expected, *, method="GET", body=None, session=None):
            headers = Path(directory, "headers")
            command = ["curl", "--silent", "--show-error", "--max-time", "10",
                       "--noproxy", "*", "--resolve", f"{HOST}:443:127.0.0.1",
                       "--cacert", certificate, "--dump-header", str(headers), "--write-out", "\n%{http_code}"]
            command += ["--head"] if method == "HEAD" else ["--request", method]
            if session:
                command += ["--cookie", str(Path(directory, session)), "--cookie-jar", str(Path(directory, session))]
            payload = None
            if body is not None:
                command += ["--header", f"Origin: {ORIGIN}", "--header", "Content-Type: application/json", "--data-binary", "@-"]
                payload = json.dumps(body)
            result = subprocess.run(command + [ORIGIN + path], input=payload,
                                    check=True, capture_output=True, text=True).stdout
            content, code = result.rsplit("\n", 1)
            status = int(code)
            accepted = expected if isinstance(expected, tuple) else (expected,)
            assert status in accepted, (method, path, status)
            return content, headers.read_text().lower(), status

        html, headers, _ = request("/", 200)
        assert "content-type: text/html" in headers
        assert "frame-ancestors 'none'" in headers and "script-src 'self'" in headers
        assert 'id="root"' in html
        script = re.search(r'src="(/assets/[\w-]+\.js)"', html).group(1)
        _, javascript, _ = request(script, 200)
        assert "content-type: text/javascript" in javascript
        request("/health", 200, method="HEAD")
        health, _, _ = request("/health", 200)
        assert json.loads(health)["channel"] == "mock" and json.loads(health)["stopped"] is True
        for path in ("/internal", "/internal/nick-worker", "/operator"):
            request(path, 404)

        request("/api/v1/workspace", 401)
        body, headers, _ = request("/api/v1/session", 200, method="POST", session="owner",
                                body={"account": "fixture-owner", "passphrase": passphrase})
        assert json.loads(body)["role"] == "owner"
        cookie = next(line for line in headers.splitlines() if line.startswith("set-cookie:"))
        assert all(attribute in cookie for attribute in ("; secure", "; httponly", "; samesite=strict"))
        request("/api/v1/workspace", 200, session="owner")

        for role in ("sales", "support"):
            account = {"account": "fixture-" + role, "label": role, "role": role, "passphrase": secrets.token_hex(20)}
            request("/api/v1/operators", 201, method="POST", session="owner", body=account)
            body, _, _ = request("/api/v1/session", 200, method="POST", session=role,
                              body={"account": account["account"], "passphrase": account["passphrase"], "role": "owner"})
            assert json.loads(body)["role"] == role
            request("/api/v1/operators", 403, method="POST", session=role, body=account)
        request("/api/v1/operators", 400, method="POST", session="owner",
                body={"account": "other-owner", "label": "Fixture", "role": "owner", "passphrase": secrets.token_hex(20)})
        wrong = {"account": "fixture-owner", "passphrase": secrets.token_hex(20)}
        for _ in range(65):
            _, _, status = request("/api/v1/session", (401, 429), method="POST", body=wrong)
            if status == 429:
                break
        else:
            raise AssertionError("Login limit did not return 429")
    print("HTTPS Nginx served the production SPA, secured sessions and authenticated APIs")


if __name__ == "__main__":
    main()
