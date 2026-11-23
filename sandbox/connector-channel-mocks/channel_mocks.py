"""S2 local fixture reads and normalized data. No network or job engine."""

from datetime import date, datetime
import hashlib
import json
from pathlib import Path
import re


LIVE_ENABLED = False
FIXTURE_FILE = Path(__file__).with_name("fixtures.json")
DIMENSIONS = ("date", "source", "channel")
METRICS = ("sessions", "engaged_sessions", "conversions")
ATTRIBUTION = {"demo-search": "organic_search", "demo-letter": "email", "demo-direct": "direct"}
RESOURCE_ID = {"site": "site", "posts": "post", "pages": "page", "products": "product"}
LOCALES = {"en", "vi"}


class ReadError(ValueError):
    def __init__(self, code, reason):
        super().__init__(reason)
        self.status = code


def require(condition, reason):
    if not condition:
        raise ReadError(422, reason)


def wire(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("ascii")


def digest(value):
    return hashlib.sha256(wire(value)).hexdigest()


def parse_day(value):
    require(isinstance(value, str) and re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value), "date format")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ReadError(422, "invalid date") from exc


def parse_stamp(value):
    require(isinstance(value, str) and re.fullmatch(
        r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z", value), "UTC timestamp format")
    try:
        return datetime.fromisoformat(value)
    except ValueError as exc:
        raise ReadError(422, "invalid UTC timestamp") from exc


def record(kind, system, identifier, observed_at, fields):
    parse_stamp(observed_at)
    return {"schema_version": 1, "record_type": kind, "source_system": system,
            "source_record_id": identifier, "observed_at": observed_at,
            "data_classification": "SYNTHETIC", "source_status": "SYNTHETIC",
            "provenance": "MOCK", "data": fields}


def normalize_ga4(row, observed_at, metrics=METRICS):
    require(type(row) is dict and row.keys() == set(DIMENSIONS + METRICS), "unexpected aggregate fields")
    parse_day(row["date"])
    source, channel = row["source"], row["channel"]
    require(isinstance(source, str) and source in ATTRIBUTION and ATTRIBUTION[source] == channel,
            "inconsistent source attribution")
    require(all(type(row[field]) is int and row[field] >= 0 for field in METRICS)
            and row["engaged_sessions"] <= row["sessions"], "invalid aggregate metrics")
    require(metrics and all(isinstance(field, str) and field in METRICS for field in metrics),
            "unsupported metric")
    source_id = "fake-source-" + source
    event_id = "fake-aggregate-" + digest([row["date"], source, channel])
    event = record("channel_event", "ga4", event_id, observed_at, {
        "date": row["date"], "grain": "day/source/channel", "attribution_source_id": source_id,
        "metrics": {field: {"value": row[field], "unit": "count"} for field in metrics},
    })
    attribution = record("campaign_source", "ga4", source_id, observed_at, {"source": source, "channel": channel})
    return event, attribution


def normalize_wp(row, observed_at):
    require(type(row) is dict and isinstance(row.get("resource"), str)
            and row["resource"] in RESOURCE_ID, "unknown WP mapping resource")
    resource = row["resource"]
    fields = {"resource", "id", "locale", "title", "updated_at"}
    if resource == "products":
        fields |= {"price_minor", "currency"}
    require(row.keys() == fields, "unexpected WP record fields")
    locale = row["locale"]
    require(isinstance(locale, str) and locale in LOCALES, "unsupported locale")
    identifier = row["id"]
    pattern = f"fake-{RESOURCE_ID[resource]}-{locale}(?:-[a-z0-9-]+)?"
    require(isinstance(identifier, str) and re.fullmatch(pattern, identifier), "inconsistent resource identity")
    require(isinstance(row["title"], str) and 1 <= len(row["title"]) <= 80, "invalid synthetic title")
    require(parse_stamp(row["updated_at"]) <= parse_stamp(observed_at), "update newer than fixture observation")
    data = {key: row[key] for key in ("title", "locale", "updated_at")}
    if resource == "products":
        require(type(row["price_minor"]) is int and row["price_minor"] >= 0
                and row["currency"] in ("USD", "VND"), "invalid synthetic price")
        return record("product", "woocommerce", identifier, observed_at,
                      data | {"price": {"value": row["price_minor"], "currency": row["currency"],
                                        "unit": "minor_currency_unit"}})
    return record("content_asset", "wordpress", identifier, observed_at, data | {"kind": RESOURCE_ID[resource]})


def reply(status, observed_at, *, records=(), **fields):
    outcome = "completed" if status == 200 else "outcome_unknown" if status == 504 else "failed"
    return {"status": status, "outcome": outcome, "observed_at": observed_at, "provenance": "MOCK",
            "source_status": "SYNTHETIC", "records": list(records), **fields}


def fault_reply(scenario, deadline_ms, observed_at):
    require(type(deadline_ms) is int and 1 <= deadline_ms <= 1000, "invalid logical deadline")
    require(scenario in ("ok", "forbidden", "quota", "delayed"), "unsupported synthetic scenario")
    if scenario == "forbidden":
        return reply(403, observed_at, error="synthetic_permission_denied")
    if scenario == "quota":
        return reply(429, observed_at, error="synthetic_quota_exhausted", retry_after_ms=100)
    if scenario == "delayed":
        return reply(504, observed_at, error="synthetic_deadline", elapsed_ms=deadline_ms)
    return None


class OfflineReadAdapter:
    def __init__(self, *, endpoint=None, credentials=None):
        require(LIVE_ENABLED is False and endpoint is None and credentials is None,
                "endpoints, real accounts and credentials are disabled")
        self._fixture = json.loads(FIXTURE_FILE.read_text(encoding="utf-8"))
        self.observed_at = self._fixture["observed_at"]
        parse_stamp(self.observed_at)


class GA4Mock(OfflineReadAdapter):
    def run_report(self, *, dimensions, metrics, start_date, end_date, row_budget,
                   scenario="ok", deadline_ms=100):
        require(isinstance(dimensions, (list, tuple)) and tuple(dimensions) == DIMENSIONS,
                "dimensions must be date, source and channel in order")
        require(isinstance(metrics, (list, tuple)) and metrics
                and all(isinstance(field, str) and field in METRICS for field in metrics)
                and len(set(metrics)) == len(metrics), "invalid metric selection")
        start, end = parse_day(start_date), parse_day(end_date)
        require(0 <= (end - start).days < 31 and end <= parse_stamp(self.observed_at).date(), "period outside bounds")
        require(type(row_budget) is int and 1 <= row_budget <= 100, "invalid aggregate row budget")
        fault = fault_reply(scenario, deadline_ms, self.observed_at)
        if fault is not None:
            return fault
        rows = sorted((row for row in self._fixture["ga4"] if start <= parse_day(row["date"]) <= end),
                      key=lambda row: (row["date"], row["source"], row["channel"]))
        require(len(rows) <= row_budget, "aggregate rows exceed budget")
        records, attribution, ids = [], {}, set()
        for row in rows:
            event, source = normalize_ga4(row, self.observed_at, metrics)
            identifier = event["source_record_id"]
            require(identifier not in ids, "duplicate aggregate grain")
            ids.add(identifier)
            records.append(event)
            attribution[source["source_record_id"]] = source
        return reply(200, self.observed_at, records=records, attribution=list(attribution.values()),
                     period={"start_date": start_date, "end_date": end_date}, aggregate_row_count=len(records))


def row_watermark(row):
    return row["data"]["updated_at"], row["source_record_id"]


def parse_watermark(value, observed_at):
    if value is None:
        return None
    require(type(value) is dict and value.keys() == {"updated_at", "source_record_id"}, "invalid watermark shape")
    identifier = value["source_record_id"]
    require(isinstance(identifier, str) and re.fullmatch(r"fake-[a-z0-9-]{1,80}", identifier),
            "watermark identity is outside the fixture")
    require(parse_stamp(value["updated_at"]) <= parse_stamp(observed_at), "watermark after snapshot")
    return value["updated_at"], identifier


class WpWooMock(OfflineReadAdapter):
    def _records(self, resource, locale):
        require(isinstance(resource, str) and isinstance(locale, str) and locale in LOCALES, "invalid read scope")
        if resource not in RESOURCE_ID:
            raise ReadError(404, "resource unavailable in read-only fixture")
        rows = [normalize_wp(row, self.observed_at) for row in self._fixture["wp_woo"]
                if row["resource"] == resource and row["locale"] == locale]
        require(len({row["source_record_id"] for row in rows}) == len(rows), "duplicate WP record identity")
        return sorted(rows, key=row_watermark)

    def get(self, resource, *, locale, record_id, scenario="ok", deadline_ms=100):
        require(isinstance(record_id, str) and re.fullmatch(r"fake-[a-z0-9-]{1,80}", record_id), "invalid record ID")
        fault = fault_reply(scenario, deadline_ms, self.observed_at)
        if fault is not None:
            return fault
        match = next((row for row in self._records(resource, locale) if row["source_record_id"] == record_id), None)
        if match is None:
            return reply(404, self.observed_at, error="synthetic_resource_missing")
        return reply(200, self.observed_at, records=[match])

    def list(self, resource, *, locale, limit=2, cursor=None, modified_since=None, scenario="ok", deadline_ms=100):
        require(type(limit) is int and 1 <= limit <= 10, "invalid page limit")
        since = parse_watermark(modified_since, self.observed_at)
        fault = fault_reply(scenario, deadline_ms, self.observed_at)
        if fault is not None:
            return fault
        rows = [row for row in self._records(resource, locale) if since is None or row_watermark(row) > since]
        fingerprint = digest([resource, locale, limit, modified_since, self.observed_at, rows])
        offset = 0
        if cursor is not None:
            require(isinstance(cursor, str) and re.fullmatch(r"[0-9a-f]{64}:[1-9][0-9]{0,3}", cursor),
                    "malformed cursor")
            bound, position = cursor.split(":")
            if bound != fingerprint:
                raise ReadError(409, "cursor scope or snapshot has changed")
            offset = int(position)
            require(offset % limit == 0 and offset < len(rows), "cursor out of range")
        stop = offset + limit
        next_cursor = f"{fingerprint}:{stop}" if stop < len(rows) else None
        watermark = None
        if next_cursor is None:
            watermark = (dict(zip(("updated_at", "source_record_id"), row_watermark(rows[-1])))
                         if rows else modified_since)
        return reply(200, self.observed_at, records=rows[offset:stop], next_cursor=next_cursor,
                     next_watermark=watermark)
