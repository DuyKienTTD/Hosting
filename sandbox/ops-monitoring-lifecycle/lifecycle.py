import json
from datetime import datetime, timezone

class Lifecycle:
    def __init__(self, resource='kvm2', rule='N8N_READINESS', rule_version='ops-01a-s2-v1', source='synthetic', cooldown_seconds=900):
        self.resource=resource; self.rule=rule; self.rule_version=rule_version; self.source=source; self.cooldown_seconds=cooldown_seconds
        self.state='NORMAL'; self.last_ts=None; self.last_alert_ts=None; self.bad_streak=0; self.good_streak=0; self.incident_seq=0
        self.seen={}; self.audit=[]

    def _dt(self, value):
        if not isinstance(value, str) or not value.endswith('Z'): raise ValueError('timestamp must be UTC Z')
        parsed=datetime.fromisoformat(value[:-1]+'+00:00')
        if parsed.tzinfo is None: raise ValueError('timestamp must be timezone-aware')
        return parsed.astimezone(timezone.utc)

    def _canonical(self, sample): return json.dumps(sample, sort_keys=True, separators=(',', ':'))

    def _event(self, kind, sample, elapsed=None, notification_emitted=False):
        incident_id=f'{self.resource}:{self.rule}:{self.rule_version}:{self.incident_seq}'
        return {'kind':kind,'state':self.state,'sample_id':sample.get('sample_id'),'observed_at_utc':sample.get('observed_at_utc'),'rule_version':self.rule_version,'resource':self.resource,'incident_seq':self.incident_seq,'incident_id':incident_id,'sequence':self.incident_seq,'dedupe_key':incident_id,'cooldown_seconds':self.cooldown_seconds,'elapsed_since_alert_seconds':elapsed,'notification_emitted':notification_emitted}

    def _reject(self, kind, sample): self.audit.append({'type':kind,'sample_id':sample.get('sample_id')}); return []

    def _validate(self, sample):
        if not isinstance(sample, dict): return None, 'INVALID_SAMPLE'
        required=('sample_id','observed_at_utc','resource','source','rule_version','freshness','health_status','signal')
        if any(not sample.get(k) for k in required): return None, 'INVALID_IDENTITY_OR_FIELDS'
        try: now=self._dt(sample['observed_at_utc'])
        except Exception: return None, 'INVALID_TIMESTAMP'
        if sample['resource'] != self.resource: return None, 'IDENTITY_MISMATCH'
        if sample['source'] != self.source: return None, 'SOURCE_MISMATCH'
        if sample['rule_version'] != self.rule_version: return None, 'RULE_VERSION_MISMATCH'
        if sample['freshness'] not in ('fresh','stale') or sample['health_status'] not in ('observed','blocked') or sample['signal'] not in ('bad','good'):
            return None, 'UNKNOWN_SAMPLE'
        if self.last_ts is not None and now <= self.last_ts: return None, 'NON_ADVANCING_TIMESTAMP'
        return now, None

    def ingest(self, sample):
        now, error=self._validate(sample)
        if error: return self._reject(error, sample if isinstance(sample, dict) else {})
        sid=sample['sample_id']; canonical=self._canonical(sample)
        if sid in self.seen: return self._reject('EXACT_REPLAY' if self.seen[sid]==canonical else 'CONFLICTING_REPLAY', sample)
        self.seen[sid]=canonical; self.last_ts=now
        if sample['freshness'] != 'fresh' or sample['health_status'] != 'observed':
            self.bad_streak=0; self.good_streak=0; return self._reject('UNKNOWN_SAMPLE', sample)
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
        return json.dumps({'resource':self.resource,'rule':self.rule,'rule_version':self.rule_version,'source':self.source,'cooldown_seconds':self.cooldown_seconds,'state':self.state,'last_ts':self.last_ts.isoformat() if self.last_ts else None,'last_alert_ts':self.last_alert_ts.isoformat() if self.last_alert_ts else None,'bad_streak':self.bad_streak,'good_streak':self.good_streak,'incident_seq':self.incident_seq,'seen':self.seen,'audit':self.audit},sort_keys=True)

    @classmethod
    def restore(cls, payload):
        d=json.loads(payload); x=cls(d['resource'],d['rule'],d['rule_version'],d['source'],d['cooldown_seconds']); x.state=d['state']; x.last_ts=datetime.fromisoformat(d['last_ts']) if d['last_ts'] else None; x.last_alert_ts=datetime.fromisoformat(d['last_alert_ts']) if d['last_alert_ts'] else None; x.bad_streak=d['bad_streak']; x.good_streak=d['good_streak']; x.incident_seq=d['incident_seq']; x.seen=d['seen']; x.audit=d.get('audit',[]); return x
