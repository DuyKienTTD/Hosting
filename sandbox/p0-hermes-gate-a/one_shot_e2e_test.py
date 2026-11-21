"""One fake n8n task through Hermes and the mock guard; run inside bridge."""
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path


def post(value):
    token = Path("/run/secrets/existing_p0_token").read_text().strip()
    request = urllib.request.Request(
        "http://n8n-p0-sandbox:5678/webhook/ttd-p0-fake-ads-audit-v1",
        data=json.dumps(value, separators=(",", ":")).encode(), method="POST",
        headers={"Authorization": "Bearer " + token, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.status, json.loads(response.read())
    except urllib.error.HTTPError as error:
        return error.code, json.loads(error.read())


def main():
    task_id, correlation_id = sys.argv[1:3]
    value = {"phase": "start", "task_id": task_id, "correlation_id": correlation_id,
             "input": {"channel": "ads", "spend": 25, "clicks": 7}}
    status, first = post(value)
    replay_status, replay = post(value)
    result = {"first_http": status, "callback_http": first.get("callback_http_status"),
              "mode": first.get("mode"), "paid_inference": first.get("paid_inference"),
              "replay_http": replay_status, "replayed": replay.get("replayed")}
    print(json.dumps(result, sort_keys=True))
    assert status == 200 and first.get("callback_http_status") == 200
    assert first.get("paid_inference") is False and replay_status == 200 and replay.get("replayed") is True


if __name__ == "__main__":
    main()
