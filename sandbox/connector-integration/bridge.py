"""S3 versioned binding for pinned S1 jobs and S2 synthetic reads."""

import json
import re


LIVE_ENABLED = False
FIELDS = {"contract_version", "synthetic", "approval", "idempotency_key", "operation",
          "arguments", "scenario", "budget", "deadline_ms"}
GA_ARGS = {"dimensions", "metrics", "start_date", "end_date", "row_budget"}
WP_GET_ARGS = {"resource", "locale", "record_id"}
WP_LIST_ARGS = {"resource", "locale", "limit", "cursor", "modified_since"}
OPERATIONS = {"ga4.run_report": (GA_ARGS, GA_ARGS), "wp_woo.get": (WP_GET_ARGS, WP_GET_ARGS),
              "wp_woo.list": ({"resource", "locale"}, WP_LIST_ARGS)}


class Bridge:
    def __init__(self, s1, s2, root, *, endpoint=None, credentials=None):
        if LIVE_ENABLED is not False or endpoint is not None or credentials is not None:
            raise s1.InvalidContract("bridge accepts local synthetic reads only")
        self.s1 = s1
        self.s2 = s2
        self.local = s1.OfflineAdapter(root)
        with self.local.tx() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS s3_intents (
                key TEXT PRIMARY KEY, request BLOB NOT NULL, request_sha256 TEXT NOT NULL,
                job_id TEXT NOT NULL UNIQUE, native_sha256 TEXT NOT NULL,
                read_attempts INTEGER NOT NULL DEFAULT 0, prepared_result BLOB
            )""")

    def _require(self, condition, message):
        if not condition:
            raise self.s1.InvalidContract(message)

    def _validate(self, intent):
        self._require(type(intent) is dict and intent.keys() == FIELDS, "invalid S3 envelope")
        key = intent["idempotency_key"]
        operation = intent["operation"]
        self._require(type(intent["contract_version"]) is int and intent["contract_version"] == 1
                      and intent["synthetic"] is True and intent["approval"] == "synthetic_approved"
                      and isinstance(key, str) and re.fullmatch(r"fake-[a-z0-9-]{1,48}", key)
                      and isinstance(operation, str) and operation in OPERATIONS
                      and intent["scenario"] in ("ok", "forbidden", "quota", "delayed"), "unsupported S3 request")
        args = intent["arguments"]
        required, allowed = OPERATIONS[operation]
        self._require(type(args) is dict and required <= args.keys() <= allowed, "invalid read arguments")
        for key, value in args.items():
            if key == "modified_since" and value is not None:
                self._require(type(value) is dict and value.keys() == {"updated_at", "source_record_id"}
                              and all(self._plain(v) for v in value.values()), "invalid watermark shape")
            elif key in ("dimensions", "metrics"):
                self._require(type(value) is list and len(value) <= 12
                              and all(self._plain(v) for v in value), "invalid requested fields")
            else:
                self._require(self._plain(value) or type(value) is int or value is None,
                              "arguments must be synthetic scalar data")

    @staticmethod
    def _plain(value):
        return isinstance(value, str) and re.fullmatch(r"[A-Za-z0-9_:. -]{1,120}", value) is not None

    def admit(self, intent, now_ms):
        self._validate(intent)
        wire, sha = self.s1.wire(intent), self.s1.sha(intent)
        key = intent["idempotency_key"]
        # S1 keeps its fixture schema. The derived native key commits to the
        # entire S3 intent, while the public key has an independent conflict gate.
        native = {
            "schema_version": 1, "synthetic": True, "idempotency_key": "fake-" + sha[:48],
            "channel": "fixture", "source": "synthetic", "approval": intent["approval"],
            "budget": intent["budget"], "deadline_ms": intent["deadline_ms"], "payload": {"mode": "success"},
        }
        self.s1.validate_request(native, now_ms)
        native_sha = self.s1.sha(native)
        job = "job-" + native_sha
        with self.local.tx() as db:
            prior = db.execute("SELECT request FROM s3_intents WHERE key=?", (key,)).fetchone()
            if prior and prior["request"] != wire:
                raise self.s1.Conflict("public idempotency key bound to a different intent")
            if not prior:
                self._require(0 < intent["deadline_ms"] - now_ms <= 60_000, "deadline outside admission window")
                db.execute("""INSERT INTO s3_intents(key,request,request_sha256,job_id,native_sha256)
                    VALUES(?,?,?,?,?)""", (key, wire, sha, job, native_sha))
            existing = db.execute("SELECT 1 FROM jobs WHERE job_id=?", (job,)).fetchone()
        admission = {"http": 200, "replayed": True}
        if not existing:
            # A crash may leave the intent reserved before native admission.
            # Only an identical retry can finish admission with this key.
            admission = self.local.admit(native, now_ms)
        bound = self.local.snapshot(job)
        self._require(bound["request_sha256"] == native_sha and bound["idempotency_key"] == native["idempotency_key"],
                      "native job binding drift")
        return {"http": admission["http"], "replayed": admission["replayed"], "job_id": job,
                "request_sha256": sha, "native_request_sha256": native_sha}

    def _intent(self, job_id):
        with self.local.tx() as db:
            row = db.execute("SELECT * FROM s3_intents WHERE job_id=?", (job_id,)).fetchone()
        self._require(row is not None, "unknown S3 job")
        return row

    def _read(self, intent, now_ms):
        operation = intent["operation"]
        if operation == "ga4.run_report":
            adapter = self.s2.GA4Mock()
            method = adapter.run_report
        else:
            adapter = self.s2.WpWooMock()
            method = adapter.get if operation == "wp_woo.get" else adapter.list
        try:
            return method(**intent["arguments"], scenario=intent["scenario"],
                          deadline_ms=min(1000, intent["deadline_ms"] - now_ms))
        except self.s2.ReadError as exc:
            return self.s2.reply(exc.status, adapter.observed_at, error="synthetic_read_rejected")

    def process(self, job_id, now_ms, checkpoint=lambda _: None):
        row = self._intent(job_id)
        request = json.loads(row["request"])
        prepared = None

        class ChannelWorker(self.s1.OfflineAdapter):
            def settle(worker, native_job, request_sha256, outcome, tick):
                outcome = prepared["outcome"] if prepared is not None else outcome
                return super().settle(native_job, request_sha256, outcome, tick)

        def on_checkpoint(name):
            nonlocal prepared
            if name == "working_after_dispatch":
                with self.local.tx() as db:
                    changed = db.execute("""UPDATE s3_intents SET read_attempts=1
                        WHERE job_id=? AND read_attempts=0""", (job_id,)).rowcount
                    if changed != 1:
                        raise self.s1.Conflict("read already claimed")
                prepared = self._read(request, now_ms)
                checkpoint("after_s2_read_before_receipt")
                with self.local.tx() as db:
                    db.execute("UPDATE s3_intents SET prepared_result=? WHERE job_id=?",
                               (self.s1.wire(prepared), job_id))
            else:
                checkpoint(name)

        ChannelWorker(self.local.root).process(job_id, now_ms, on_checkpoint)
        return self.snapshot(job_id)

    def snapshot(self, job_id):
        native = self.local.snapshot(job_id)
        row = self._intent(job_id)
        self._require(native["request_sha256"] == row["native_sha256"], "native job binding drift")
        event, receipt = native["callback"], native["receipt"]
        if event is not None:
            self._require(event["job_id"] == job_id and event["request_sha256"] == row["native_sha256"],
                          "native callback binding drift")
        if receipt is not None:
            self._require(event and receipt["job_id"] == job_id and receipt["callback_id"] == event["callback_id"]
                          and receipt["request_sha256"] == row["native_sha256"]
                          and receipt["outcome"] == native["outcome"]
                          and receipt["event_sha256"] == self.s1.sha(event), "native receipt binding drift")
        result = json.loads(row["prepared_result"]) if row["prepared_result"] else None
        # A prepared read can be orphaned by a crash. Expose it only once S1
        # acknowledges a matching outcome. S1 remains authoritative for unknown.
        terminal = native["state"] in self.s1.OUTCOMES
        if not terminal or result is None or result["outcome"] != native["outcome"]:
            result = None
        binding = None
        if terminal:
            self._require(receipt is not None, "terminal job lacks receipt")
            self._require(native["outcome"] == "outcome_unknown" or result is not None,
                          "known native outcome lacks a matching prepared result")
            binding = {"contract_version": 1, "s3_request_sha256": row["request_sha256"],
                       "native_request_sha256": row["native_sha256"], "native_receipt_id": receipt["receipt_id"],
                       "result_sha256": self.s1.sha(result) if result is not None else None,
                       "outcome": native["outcome"]}
            binding["binding_sha256"] = self.s1.sha(binding)
        return {"contract_version": 1, "request_sha256": row["request_sha256"], "native": native,
                "result": result, "receipt_binding": binding, "synthetic_read_attempts": row["read_attempts"],
                "external_effect_delivered": False}
