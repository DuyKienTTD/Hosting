# OPS-01A/S2 lifecycle sandbox

This directory is an offline synthetic contract only. It does not read VPS/KVM2, production metrics, credentials, notification channels, cron, webhooks or paid providers.

## D1 contract

- Validate fields, UTC timestamp, resource, source, rule version, freshness, health and signal before control-state mutation.
- Reject exact and conflicting sample-ID replays before control-state mutation.
- Require strictly advancing UTC timestamps. Rejected samples do not advance trusted time or streaks; audit entries are diagnostic only.
- `OPEN` is an incident lifecycle state. A cooldown controls notification eligibility, not incident identity.
- `OPEN` + bad×3 never increments incident sequence. At `+899` notification is suppressed; at `+900` and `+901` a new notification is eligible when the bad×3 condition is present.
- `RECOVERED` + bad×3 starts a fresh incident independent of the previous notification cooldown. Notification emission remains separately reported.
- `incident_id` and `sequence` are stable for the active incident.
- S1 composition is represented only by the pinned minimal test fixture. No runtime S1 composition claim is made.
- Snapshot/replay is synthetic serialization only and must not create duplicate incidents or notifications.

The original S2 10/10 provenance remains historical; D1 evidence is reported separately.
