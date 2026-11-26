"""Probe the packaged web app through the production HTTPS Nginx template in CI."""

import json
import re
import secrets
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import urlparse, parse_qs

HOST = "cskh.thuanthanhdat.com.vn"
ORIGIN = "https://" + HOST


def main():
    certificate, password_file = sys.argv[1:]
    passphrase = Path(password_file).read_text().rstrip("\n")
    with tempfile.TemporaryDirectory() as directory:
        def request(path, expected, *, method="GET", body=None, session=None, ip="127.0.0.1", origin=ORIGIN):
            headers = Path(directory, "headers")
            command = ["curl", "--silent", "--show-error", "--max-time", "10",
                       "--noproxy", "*", "--resolve", f"{HOST}:443:127.0.0.1",
                       "--interface", ip, "--cacert", certificate, "--dump-header", str(headers), "--write-out", "\n%{http_code}"]
            command += ["--head"] if method == "HEAD" else ["--request", method]
            if session:
                command += ["--cookie", str(Path(directory, session)), "--cookie-jar", str(Path(directory, session))]
            payload = None
            if body is not None:
                command += ["--header", f"Origin: {origin}", "--header", "Content-Type: application/json", "--data-binary", "@-"]
                payload = json.dumps(body)
            result = subprocess.run(command + [ORIGIN + path], input=payload,
                                    check=True, capture_output=True, text=True).stdout
            content, code = result.rsplit("\n", 1)
            status = int(code)
            accepted = expected if isinstance(expected, tuple) else (expected,)
            assert status in accepted, (method, path, status)
            return content, headers.read_text().lower(), status

        def evidence(message, check):
            try:
                check()
            except Exception:
                print("FAIL " + message, flush=True)
                raise
            print("PASS " + message, flush=True)

        def frontend():
            html, headers, _ = request("/", 200)
            assert "content-type: text/html" in headers and 'id="root"' in html
            assert "frame-ancestors 'none'" in headers and "script-src 'self'" in headers
            script = re.search(r'src="(/assets/[\w-]+\.js)"', html).group(1)
            _, javascript, _ = request(script, 200)
            assert "content-type: text/javascript" in javascript

        def ingress():
            request("/health", 200, method="HEAD")
            health, _, _ = request("/health", 200)
            assert json.loads(health)["channel"] == "mock" and json.loads(health)["stopped"] is True
            for path in ("/internal", "/internal/nick-worker", "/operator"):
                request(path, 404)

        def sessions():
            request("/api/v1/workspace", 401)
            body, headers, _ = request("/api/v1/session", 200, method="POST", session="owner",
                                       body={"account": "fixture-owner", "passphrase": passphrase})
            assert json.loads(body)["role"] == "owner"
            cookie = next(line for line in headers.splitlines() if line.startswith("set-cookie:"))
            assert all(attribute in cookie for attribute in ("; secure", "; httponly", "; samesite=strict"))
            request("/api/v1/workspace", 200, session="owner")

        def roles():
            for role in ("sales", "support"):
                account = {"account": "fixture-" + role, "label": role, "role": role, "passphrase": secrets.token_hex(20)}
                request("/api/v1/operators", 201, method="POST", session="owner", body=account)
                body, _, _ = request("/api/v1/session", 200, method="POST", session=role,
                                     body={"account": account["account"], "passphrase": account["passphrase"], "role": "owner"})
                assert json.loads(body)["role"] == role
                request("/api/v1/operators", 403, method="POST", session=role, body=account)
            request("/api/v1/operators", 400, method="POST", session="owner",
                    body={"account": "other-owner", "label": "Fixture", "role": "owner", "passphrase": secrets.token_hex(20)})

        def oa_onboarding():
            request("/api/v1/oa/oauth/start", 403, method="POST", session="sales", body={})
            body, headers, _ = request("/api/v1/oa/oauth/start", 200, method="POST", session="owner", body={})
            url = urlparse(json.loads(body)["authorizationUrl"])
            assert url.netloc == "oauth.zaloapp.com" and url.path == "/v4/oa/permission"
            query = parse_qs(url.query)
            assert query["redirect_uri"] == [ORIGIN + "/api/v1/oa/oauth/callback"]
            assert len(query["state"][0]) == 64 and len(query["code_challenge"][0]) == 43
            assert "httponly; samesite=lax" in headers
            request("/api/v1/oa/oauth/callback?state=invalid", 403, session="owner")

        def csrf():
            request("/api/v1/operators", 403, method="POST", session="owner", origin="https://external.invalid",
                    body={"account": "csrf-fixture", "label": "Fixture", "role": "sales", "passphrase": secrets.token_hex(20)})

        def ip_limit():
            for index in range(30):
                request("/api/v1/session", 401 if index < 10 else 429, method="POST", ip="127.0.0.2",
                        body={"account": "ip-fixture-" + str(index), "passphrase": "invalid"})
            request("/api/v1/session", 200, method="POST", ip="127.0.0.3",
                    body={"account": "fixture-owner", "passphrase": passphrase})

        def account_limit():
            for index in range(6):
                name = "fixture-account" if index % 2 == 0 else " FIXTURE-ACCOUNT "
                request("/api/v1/session", 401 if index < 5 else 429, method="POST", ip=f"127.0.0.{20 + index}",
                        body={"account": name, "passphrase": "invalid"})

        evidence("03a HTTPS cookie Secure, HttpOnly, SameSite=Strict and authenticated workspace", sessions)
        evidence("03b CSRF rejected with 403", csrf)
        evidence("04a IP limit 429 after 10 failures; another account/IP still logs in after 30 attempts", ip_limit)
        evidence("04b normalized account limit 429 across multiple IPs", account_limit)
        evidence("05 Owner creates Sales/CSKH; other roles receive 403", roles)
        evidence("OA owner-only PKCE start and callback forwarded by Nginx", oa_onboarding)
        evidence("06 production SPA, JavaScript and CSP served by HTTPS Nginx", frontend)
        evidence("07 internal/operator 404; HEAD /health 200; mock and STOP preserved", ingress)

    print("HTTPS Nginx served the production SPA, secured sessions and authenticated APIs")


if __name__ == "__main__":
    main()
