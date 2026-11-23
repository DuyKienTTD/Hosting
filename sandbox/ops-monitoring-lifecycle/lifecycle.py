import json
from datetime import datetime, timezone
class Lifecycle:
    def __init__(self, resource='kvm2', rule='N8N_READINESS', rule_version='ops-01a-s2-v1', source='synthetic', cooldown_seconds=900):
        self.resource=resource; self.rule=rule; self.rule_version=rule_version; self.source=source; self.cooldown_seconds=cooldown_seconds
        self.state='NORMAL'; self.last_ts=None; self.last_alert_ts=None; self.bad_streak=0; self.good_streak=0; self.incident_seq=0; self.seen=set(); self.audit=[]
    def _dt(self,v): return datetime.fromisoformat(v.replace('Z','+00:00')).astimezone(timezone.utc)
    def _event(self,kind,sample,elapsed=None):
        return {'kind':kind,'state':self.state,'sample_id':sample.get('sample_id'),'observed_at_utc':sample.get('observed_at_utc'),'rule_version':self.rule_version,'resource':self.resource,'incident_seq':self.incident_seq,'dedupe_key':f'{self.resource}:{self.rule}:{self.rule_version}:{self.incident_seq}','cooldown_seconds':self.cooldown_seconds,'elapsed_since_alert_seconds':elapsed}
    def ingest(self,s):
        sid=s.get('sample_id'); out=[]
        if not sid or sid in self.seen: self.audit.append({'type':'DUPLICATE_SAMPLE','sample_id':sid}); return out
        self.seen.add(sid)
        try: now=self._dt(s['observed_at_utc'])
        except Exception: self.audit.append({'type':'INVALID_TIMESTAMP','sample_id':sid}); return out
        if self.last_ts and now < self.last_ts: self.audit.append({'type':'OUT_OF_ORDER_SAMPLE','sample_id':sid}); return out
        self.last_ts=now
        if s.get('resource')!=self.resource: self.audit.append({'type':'IDENTITY_MISMATCH','sample_id':sid}); self.bad_streak=0; self.good_streak=0; return out
        if s.get('source')!=self.source: self.audit.append({'type':'SOURCE_MISMATCH','sample_id':sid}); self.bad_streak=0; self.good_streak=0; return out
        if s.get('freshness')!='fresh' or s.get('health_status')!='observed' or s.get('signal') not in ('bad','good'):
            self.audit.append({'type':'UNKNOWN_SAMPLE','sample_id':sid}); self.bad_streak=0; self.good_streak=0; out.append(self._event('UNKNOWN',s)); return out
        if s['signal']=='bad':
            self.good_streak=0; self.bad_streak+=1
            if self.bad_streak>=3:
                elapsed=None if self.last_alert_ts is None else (now-self.last_alert_ts).total_seconds()
                if self.state=='OPEN':
                    if elapsed is not None and elapsed < self.cooldown_seconds: out.append(self._event('SUPPRESSED_COOLDOWN',s,elapsed))
                    else: self.incident_seq+=1; self.last_alert_ts=now; out.append(self._event('REOPEN',s,elapsed))
                elif self.state in ('NORMAL','RECOVERED'):
                    if self.last_alert_ts is not None and elapsed < self.cooldown_seconds: out.append(self._event('SUPPRESSED_COOLDOWN',s,elapsed))
                    else: self.state='OPEN'; self.incident_seq+=1; self.last_alert_ts=now; out.append(self._event('OPEN',s,elapsed))
                self.bad_streak=0
        else:
            self.bad_streak=0
            if self.state=='OPEN':
                self.good_streak+=1
                if self.good_streak>=3: self.state='RECOVERED'; out.append(self._event('RECOVERED',s)); self.good_streak=0
            else: self.good_streak=0
        return out
    def snapshot(self):
        return json.dumps({'resource':self.resource,'rule':self.rule,'rule_version':self.rule_version,'source':self.source,'cooldown_seconds':self.cooldown_seconds,'state':self.state,'last_ts':self.last_ts.isoformat() if self.last_ts else None,'last_alert_ts':self.last_alert_ts.isoformat() if self.last_alert_ts else None,'bad_streak':self.bad_streak,'good_streak':self.good_streak,'incident_seq':self.incident_seq,'seen':sorted(self.seen),'audit':self.audit},sort_keys=True)
    @classmethod
    def restore(cls,payload):
        d=json.loads(payload); x=cls(d['resource'],d['rule'],d['rule_version'],d['source'],d['cooldown_seconds']); x.state=d['state']; x.last_ts=datetime.fromisoformat(d['last_ts']) if d['last_ts'] else None; x.last_alert_ts=datetime.fromisoformat(d['last_alert_ts']) if d['last_alert_ts'] else None; x.bad_streak=d['bad_streak']; x.good_streak=d['good_streak']; x.incident_seq=d['incident_seq']; x.seen=set(d['seen']); x.audit=d['audit']; return x
