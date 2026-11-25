import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

root = Path(__file__).resolve().parents[1]
operations = {
    "receiveMessage": {},
    "sendMessage": {"conversationId": "direct", "text": "Fixture"},
    "listGroups": {"limit": 10},
    "readGroupMessages": {"groupId": "group", "cursor": "cursor"},
    "postToGroup": {"groupId": "group", "text": "Fixture"},
    "createGroup": {"name": "Fixture", "memberIds": ["contact"]},
    "moderateGroup": {"groupId": "group", "action": "remove_member", "contactId": "contact"},
    "sendFriendRequest": {"contactId": "contact"},
    "onFriendAccepted": {},
    "getContact": {"contactId": "contact"},
}


def validator(name):
    schema = json.loads((root / "schemas" / f"{name}.schema.json").read_text())
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema, format_checker=FormatChecker())


command = validator("command")
for operation, payload in operations.items():
    value = {"version": 1, "accountId": "account", "idempotencyKey": "fixture", "operation": operation, "payload": payload}
    command.validate(value)
    assert not command.is_valid({key: item for key, item in value.items() if key != "idempotencyKey"})
    assert not command.is_valid({**value, "payload": {**payload, "unexpected": True}})

assert not command.is_valid({**value, "operation": "sendMessage", "payload": {"groupId": "group", "text": "Fixture"}})
event = validator("event")
base = {"version": 1, "accountId": "account", "eventId": "event", "occurredAt": "2026-11-26T00:00:00Z"}
event.validate({**base, "type": "messageReceived", "payload": {
    "messageId": "message", "senderId": "contact", "thread": {"kind": "group", "groupId": "group"}, "text": "Fixture",
}})
accepted = {**base, "type": "friendAccepted", "payload": {"contactId": "contact", "evidenceId": "event"}}
event.validate(accepted)
assert not event.is_valid({**accepted, "payload": {"contactId": "contact"}})
assert not event.is_valid({**accepted, "occurredAt": "invalid"})
error = validator("error")
for code in ("rate_limited", "auth", "not_supported", "unknown_delivery"):
    error.validate({"code": code})
assert not error.is_valid({"code": "provider_error"})
print("PASS: 10 command variants, required idempotency, route isolation, events, errors")
