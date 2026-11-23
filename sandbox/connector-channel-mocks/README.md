# ENG-01A-S2 synthetic read adapters

Use Python 3.12 or later and run only the S2 suite from the repository root. The package uses the standard library and reads its adjacent UTF-8 JSON fixture.

```powershell
python -X utf8 -B sandbox/connector-channel-mocks/test_channel_mocks.py
```

## Read interfaces

| Adapter | Arguments and result |
| --- | --- |
| `GA4Mock.run_report` | Requires dimensions `date, source, channel` in that order and any nonempty unique subset of fixture metrics `sessions, engaged_sessions, conversions`. Supply ISO dates and a row budget from 1 to 100. The inclusive period is at most 31 days and cannot end after the snapshot. Budget excess fails with 422. A valid empty result returns 200. Returns aggregates, deduplicated source records and the fixture's observation timestamp. |
| `WpWooMock.get` | Reads one record by fixture ID and locale from `site`, `posts`, `pages` or `products`. An absent fixture resource reports 404. Locale is exactly `en` or `vi`. |
| `WpWooMock.list` | Lists the same four resources by locale and page size 1–10. The cursor is bound to the resource, locale, page size, filter and fixture snapshot. Malformed/out-of-range cursors fail with 422. A changed scope or snapshot fails with 409. This deterministic cursor has no authorization function. |

WordPress/Woo lists sort by `(updated_at, source_record_id)`. `modified_since` takes that same compound exclusive watermark. The tie-breaker preserves distinct records with the same update time. The last page returns the high-water mark, or the input mark when the query is empty. Intermediate pages and synthetic errors do not advance it.

Read methods accept `scenario=ok|forbidden|quota|delayed` and a bounded logical deadline. Forced responses are 403, 429 with a synthetic retry hint, or 504 with `outcome_unknown`. There is no transport, scheduler, retry, persistent store or mutation method. The 504 is a deterministic logical deadline test. Response codes are in-process contract values.

## Normalized record v1

Each record has `schema_version`, `record_type`, `source_system`, `source_record_id`, `observed_at` (UTC), `data_classification=SYNTHETIC`, `source_status=SYNTHETIC`, `provenance=MOCK` and a type-specific `data` object.

| Type | Data and identity |
| --- | --- |
| `channel_event` | GA4 fixture aggregate at day/source/channel grain. Stable synthetic ID from that grain, a reference to `campaign_source` and selected KPI values with `unit=count`. |
| `campaign_source` | Source and channel identifiers from the same fixture. No campaign ID is inferred. |
| `content_asset` | WordPress fixture site/post/page ID, kind, synthetic title, locale and UTC update timestamp. |
| `product` | WooCommerce fixture product ID, title, locale, UTC update timestamp and an integer price in `minor_currency_unit` with explicit currency. |

Field allowlists cover only the packaged fabricated data. These normalizers do not sanitize or ingest arbitrary live data. The only relationship emitted by GA4 is aggregate to attribution source. A later opt-in lead relationship would require a separate subject reference, consent reference, provenance and retention decision owned by the business. The current schema does not create a lead, order, customer record or person-level join.

## Offline and future integration boundary

`LIVE_ENABLED=False`. Both adapters reject endpoint and credential configuration and never import a networking, credential or OAuth library. The S2 suite denies socket audit events. Calls are deterministic reads of a local fixture. Repeating a read is not S1 job replay and does not create a dispatch or receipt.

S1 remains on [PR #10 at `79dfe8a`](https://github.com/DuyKienTTD/Hosting/blob/79dfe8aae5c30d4e896c29333e0296ada1671b7e/sandbox/connector-contracts/README.md). S2 does not copy or import that dispatcher. For ENG-01B, after PR #10 lands, use the S1 job/idempotency and outbox/receipt boundaries from `sandbox/connector-contracts/offline_connector.py`. Bind channel, normalized request digest, deadline, approval and budget through an approved job payload extension. S1 currently accepts only synthetic mode payloads. Exercise that wiring in a separate integration delta. `INTEGRATION_PENDING_PR10`.

A live version requires approved GA4 property access, least-privilege OAuth scopes and dimension/metric compatibility, WordPress authorization and API-version/locale verification, Woo read-only key scope, quotas/rate limits, consent and retention, pricing and explicit owner approval. The fixture does not establish live API coverage or a multilingual plugin. `REAL_GA4_UNTESTED / REAL_WP_WOO_UNTESTED`.

Windows execution used CPython 3.12.3. Linux/WSL application runtime was unavailable under the task boundary. A future Linux delta should check case-sensitive fixture file resolution, UTF-8 locale behavior and canonical digest equality. The loader explicitly uses UTF-8 and the tests use a path relative to the module. `LINUX_NOT_RUN`.
