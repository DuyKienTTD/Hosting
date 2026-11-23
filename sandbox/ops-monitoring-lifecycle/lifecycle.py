import json
from datetime import datetime, timezone

class Lifecycle:
    def __init__(self, resource='kvm2', rule='N8N_READINESS', rule_version='ops-01a-s2-v1', source='synthetic', cooldown_seconds=900):
        self.resource=resource; self.rule=rule; self.rule_version=rule_version; self.source=source; self.cooldown_seconds=cooldown_seconds
        self.state='NORMAL'; self.last_ts=None; self.last_alert_ts=None; self.bad_streak=0; self.good_streak=0; self.incident_seq=0
        self.seen={}; self.audit=[]
        # Dedicated in-memory, snapshot-persisted replay identity for accepted interruptions.
        self.interruption_replays={}
    def _dt(self, value):
        if not isinstance(value, str) or not value.endswith('Z'): raise ValueError('timestamp must be UTC Z')
        parsed=datetime.fromisoformat(value[:-1]+'+00:00')
        if parsed.tzinfo is None: raise ValueError('timestamp must be timezone-aware')
        return parsed.astimezone(timezone.utc)
    # Single-rule v1 envelope: ``rule`` may be absent in historical fixtures, but
    # a supplied rule MUST equal the configured rule. No live identity is inferred.
    _REQUIRED = frozenset(('sample_id', 'observed_at_utc', 'resource', 'source',
        'rule_version', 'freshness', 'health_status', 'signal'))
    _ALLOWED = _REQUIRED | frozenset(('rule',))
    _SID_LIMIT = 128
    _MAX_INTERRUPTION_IDS = 256
    _SNAPSHOT_VERSION = 2

    @classmethod
    def _valid_id(cls, sid):
        return (isinstance(sid, str) and 1 <= len(sid) <= cls._SID_LIMIT
                and all(c.isascii() and (c.isalnum() or c in '_.:-') for c in sid))

    def _canonical(self, sample):
        return json.dumps(sample, sort_keys=True, separators=(',', ':'),
                          allow_nan=False, check_circular=True)

    def _event(self, kind, sample, elapsed=None, notification_emitted=False):
        incident_id=f'{self.resource}:{self.rule}:{self.rule_version}:{self.incident_seq}'
        return {'kind':kind,'state':self.state,'sample_id':sample.get('sample_id'),'observed_at_utc':sample.get('observed_at_utc'),'rule_version':self.rule_version,'resource':self.resource,'incident_seq':self.incident_seq,'incident_id':incident_id,'sequence':self.incident_seq,'dedupe_key':incident_id,'cooldown_seconds':self.cooldown_seconds,'elapsed_since_alert_seconds':elapsed,'notification_emitted':notification_emitted}

    def _reject(self, kind, sample):
        # Only a strictly bounded, ASCII identifier enters audit. No sample body.
        sid = sample.get('sample_id') if isinstance(sample, dict) else None
        self.audit.append({'type':kind, 'sample_id':sid if self._valid_id(sid) else None})
        return []

    def _validate(self, sample):
        if not isinstance(sample, dict):
            return None, 'INVALID_PAYLOAD', None
        if not self._valid_id(sample.get('sample_id')):
            return None, 'INVALID_SAMPLE_ID', None
        if (not all(isinstance(key, str) for key in sample)
                or self._REQUIRED - sample.keys()
                or sample.keys() - self._ALLOWED):
            return None, 'INVALID_PAYLOAD', None
        # Reject hostile/unserializable payloads before any time/seen/streak change.
        try:
            canonical = self._canonical(sample)
        except (TypeError, ValueError, OverflowError, RecursionError):
            return None, 'INVALID_PAYLOAD', None
        if any(not isinstance(sample[key], str) for key in
               ('resource','source','rule_version','freshness','health_status','signal')):
            return None, 'INVALID_PAYLOAD', None
        if 'rule' in sample and not isinstance(sample['rule'], str):
            return None, 'INVALID_PAYLOAD', None
        try: now=self._dt(sample['observed_at_utc'])
        except (TypeError, ValueError, OverflowError):
            return None, 'INVALID_TIMESTAMP', None
        if sample['resource'] != self.resource:
            return None, 'IDENTITY_MISMATCH', None
        if sample['source'] != self.source:
            return None, 'SOURCE_MISMATCH', None
        if sample['rule_version'] != self.rule_version:
            return None, 'RULE_VERSION_MISMATCH', None
        if 'rule' in sample and sample['rule'] != self.rule:
            return None, 'RULE_MISMATCH', None
        # A fresh, correctly attributed UNKNOWN/stale/blocked observation is a
        # trusted interruption, not a bad/good sample and not a security reject.
        if (sample['freshness'] != 'fresh' or sample['health_status'] != 'observed'
                or sample['signal'] not in ('bad', 'good')):
            return now, 'TRUSTED_INTERRUPTION', canonical
        return now, None, canonical

    def ingest(self, sample):
        now, error, canonical = self._validate(sample)
        if error and error != 'TRUSTED_INTERRUPTION':
            return self._reject(error, sample)
        sid = sample['sample_id']  # verified string; hashable and bounded
        # Replay comes BEFORE advancing the clock (historical D1 invariant).
        if sid in self.seen:
            return self._reject('EXACT_REPLAY' if self.seen[sid] == canonical
                                else 'CONFLICTING_REPLAY', sample)
        if sid in self.interruption_replays:
            return self._reject('EXACT_REPLAY' if self.interruption_replays[sid] == canonical
                                else 'CONFLICTING_REPLAY', sample)
        # Fail closed at registry capacity: do not evict identity and permit a
        # duplicate interruption to mutate streaks again; stop all fresh ingest.
        if len(self.interruption_replays) >= self._MAX_INTERRUPTION_IDS:
            return self._reject('INTERRUPTION_REGISTRY_FULL', sample)
        if self.last_ts is not None and now <= self.last_ts:
            return self._reject('NON_ADVANCING_TIMESTAMP', sample)
        if error == 'TRUSTED_INTERRUPTION':
            # Replay identity is separate from valid-sample 'seen' and persists
            # through snapshot/restore. Watermark and incident remain untouched.
            self.interruption_replays[sid]=canonical
            self.bad_streak=0; self.good_streak=0
            return self._reject('TRUSTED_INTERRUPTION', sample)
        self.seen[sid]=canonical; self.last_ts=now
        if sample['signal']=='bad':
            self.good_streak=0; self.bad_streak+=1
            if self.bad_streak < 3: return []
            elapsed=None if self.last_alert_ts is None else (now-self.last_alert_ts).total_seconds(); self.bad_streak=0
            if self.state=='OPEN':
                if elapsed is not None and elapsed < self.cooldown_seconds: return [self._event('SUPPRESSED_COOLDOWN',sample,elapsed,False)]
                self.last_alert_ts=now; return [self._event('NOTIFICATION',sample,elapsed,True)]
            self.state='OPEN'; self.incident_seq += 1
            emit=elapsed is None or elapsed >= self.cooldown_seconds
            if emit: self.last_alert_ts=now
            return [self._event('OPEN',sample,elapsed,emit)]
        self.bad_streak=0
        if self.state=='OPEN':
            self.good_streak+=1
            if self.good_streak>=3: self.state='RECOVERED'; self.good_streak=0; return [self._event('RECOVERED',sample,None,False)]
        else: self.good_streak=0
        return []
    def control_snapshot(self):
        return json.dumps({'state':self.state,'last_ts':self.last_ts.isoformat() if self.last_ts else None,'last_alert_ts':self.last_alert_ts.isoformat() if self.last_alert_ts else None,'bad_streak':self.bad_streak,'good_streak':self.good_streak,'incident_seq':self.incident_seq,'seen':sorted(self.seen)},sort_keys=True)
    def snapshot(self):
        return json.dumps({'resource':self.resource,'rule':self.rule,'rule_version':self.rule_version,'source':self.source,'cooldown_seconds':self.cooldown_seconds,'state':self.state,'last_ts':self.last_ts.isoformat() if self.last_ts else None,'last_alert_ts':self.last_alert_ts.isoformat() if self.last_alert_ts else None,'bad_streak':self.bad_streak,'good_streak':self.good_streak,'incident_seq':self.incident_seq,'seen':self.seen,'audit':self.audit,'snapshot_version':self._SNAPSHOT_VERSION,'interruption_replays':self.interruption_replays},sort_keys=True)
    @classmethod
    def restore(cls, payload):
        d=json.loads(payload)
        version=d.get('snapshot_version',1)
        if version not in (1,cls._SNAPSHOT_VERSION):
            raise ValueError('UNSUPPORTED_SNAPSHOT_VERSION')
        if version==1:
            # Historical v1 snapshots lack authoritative interruption identities.
            # Refuse restoration if any accepted interruption appears in audit.
            if any(isinstance(a,dict) and a.get('type')=='TRUSTED_INTERRUPTION'
                   for a in d.get('audit',[])):
                raise ValueError('LEGACY_INTERRUPTION_REPLAY_UNAVAILABLE')
            interruptions={}
        else:
            interruptions=d.get('interruption_replays')
            if (not isinstance(interruptions,dict)
                    or len(interruptions)>cls._MAX_INTERRUPTION_IDS
                    or any(not cls._valid_id(k) or not isinstance(v,str)
                           for k,v in interruptions.items())):
                raise ValueError('INVALID_INTERRUPTION_REPLAY_REGISTRY')
        if any(k in d['seen'] for k in interruptions):
            raise ValueError('REPLAY_ID_COLLISION')
        x=cls(d['resource'],d['rule'],d['rule_version'],d['source'],d['cooldown_seconds'])
        x.state=d['state']
        x.last_ts=datetime.fromisoformat(d['last_ts']) if d['last_ts'] else None
        x.last_alert_ts=datetime.fromisoformat(d['last_alert_ts']) if d['last_alert_ts'] else None
        x.bad_streak=d['bad_streak']; x.good_streak=d['good_streak']; x.incident_seq=d['incident_seq']
        x.seen=d['seen']; x.audit=d.get('audit',[]); x.interruption_replays=interruptions
        return x
