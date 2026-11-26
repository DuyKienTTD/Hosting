---
id: z4-s3-nick-delivery
type: report
status: draft
updated_at: 2026-11-26
sensitivity: public
---

# Z4-S3-NICK delivery log

- Base: `a56ec820148ab0bdc4a3577808f25a4a9d3077b6`. PR target: `dev/z4-s1-data`.
- Added the Windows-oriented worker, selector v1 fixture, browser tests, Windows CI, and the [server protocol specification](../../docs/nick-worker-protocol.md).
- Local author verification: 14 tests passed with Node.js 24 and headless Chromium on Linux using synthetic HTML and in-process WebSocket message doubles. Covered visible direct inbox rotation, group exclusion, inbound ACK, authorization, hourly and daily caps, STOP, four UI safety signals, unknown delivery persistence, recipient changes, strangers, reconnect fencing, and heartbeat expiry.
- Windows run result lives in the PR's Z4 Nick worker check. Real Zalo selectors, capture outside visible inbox rows, VPS integration and independent acceptance are pending. No real account or customer data was exercised.

## Z4-S3-FIX1

A0 rejected HEAD `1c1dd1c` because a stranger with inbound history could receive a reply. Fixture selector v2 requires positive friendship evidence tied to the active peer before composition and again in the click operation. The worker reports `not_friend` or `friend_status_unknown` and retains the rejection on job replay.

Five Chromium regressions cover inbound from strangers, same-name contacts, friendship changing after composition, and missing evidence before composition or before clicking. All 19 local fixture tests passed. Final Windows CI evidence is attached to PR #76.

## Z4-S3-FIX2

A0 reproduced a stale permit dispatch after disconnect and reconnect at HEAD `7e2ba36`. The worker invalidates the connection epoch on disconnect and replacement and now consumes a permit synchronously at Chromium dispatch. Four new fixture regressions pause a validated permit before dispatch, then exercise reconnect, server STOP, expiry and explicit revocation. CI evidence is attached to PR #76.

## Z4-S3-FIX3

The third review found cancellation races after dispatch passed the Node-side check. Chromium now holds and consumes the single-use permit. Connection, STOP, policy disable and permit revocation updates clear the page gate. Five regressions pause immediately before evaluation or inside the renderer before the click task, confirm the gate is cleared before permit expiry, then verify zero clicks. CI evidence is attached to PR #76.

## Z4-S3-FIX4

Bound the renderer permit to the page, active conversation and URL. Tab focus, visibility, navigation and active conversation changes clear the permit. Documented synchronous permit consumption as the send commit point and added a durable worker audit outbox for owner alerts when revocation follows commit. The protocol requires the server to apply the corresponding send_log annotation. Regression coverage checks an actual tab switch, in-tab recipient and URL changes, and post-commit revocation. CI evidence is attached to PR #76.

## Z4-S3-FIX5

Rebased onto the #75 merge in `dev/ttd-zalo-mvp01`. The worker creates its own registered Chromium target, clears the permit and invalidates the epoch on target or navigation events, and refuses dispatch when another page is present. The headless fixture opens and foregrounds a real second tab and exercises new pages, popups and navigation.

The runtime now accepts authenticated audit outbox retries over WebSocket and atomically writes the send state and owner notice to the #75 Postgres schema. The integration test disconnects and restarts the endpoint, reopens the worker journal, and checks the persisted state and deduplicated notice. Scoped test evidence is attached to PR #76.
