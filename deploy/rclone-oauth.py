"""Prepare private rclone authorization input and consume its token response."""
import base64
import getpass
import warnings
import json
import re
import sys
from pathlib import Path


def authorize_blob(client_id, client_secret):
    payload = {"client_id": client_id, "client_secret": client_secret, "scope": "drive.file"}
    return base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")


def decode_token(response):
    response = response.strip()
    if re.fullmatch(r"[A-Za-z0-9_-]+", response):
        response = base64.b64decode(
            response + "=" * (-len(response) % 4), altchars=b"-_", validate=True
        ).decode()
    token = json.loads(response)
    if isinstance(token, dict) and isinstance(token.get("token"), str):
        token = json.loads(token["token"])
    if not isinstance(token, dict) or not all(
        isinstance(token.get(field), str) and token[field] for field in ("access_token", "refresh_token")
    ):
        raise ValueError("invalid token response")
    return token


def configure(directory, remote):
    if not re.fullmatch(r"[A-Za-z0-9_-]+", remote):
        raise ValueError("invalid remote name")
    client_id = getpass.getpass("OAuth Desktop client ID: ")
    client_secret = getpass.getpass("OAuth Desktop client secret: ")
    if not (re.fullmatch(r"[A-Za-z0-9._-]+", client_id)
            and re.fullmatch(r"[A-Za-z0-9._-]+", client_secret)):
        raise ValueError("invalid OAuth client fields")
    blob = directory / "authorize.blob"
    blob.write_text(authorize_blob(client_id, client_secret), encoding="ascii")
    print("Transfer authorize.blob privately to the browser machine. Treat it as a secret.")
    print(f"Temporary directory: {directory}")
    print('On that machine: rclone authorize drive "$(cat <PRIVATE_BLOB_FILE>)"')
    token = decode_token(getpass.getpass("Paste the rclone token response here: "))
    (directory / "rclone.conf").write_text(
        f"[{remote}]\ntype = drive\nscope = drive.file\nclient_id = {client_id}\n"
        f"client_secret = {client_secret}\ntoken = {json.dumps(token)}\n", encoding="ascii"
    )


if __name__ == "__main__":
    try:
        warnings.simplefilter("error", getpass.GetPassWarning)
        configure(Path(sys.argv[1]), sys.argv[2])
    except (ValueError, OSError, EOFError, KeyboardInterrupt, getpass.GetPassWarning):
        sys.exit("OAuth setup failed; no configuration installed.")
