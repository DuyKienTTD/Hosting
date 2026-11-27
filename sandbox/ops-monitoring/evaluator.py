import json
from datetime import datetime, timezone
from pathlib import Path
POLICY=json.loads((Path(__file__).parent/'policy.json').read_text())
def _ts(v): return datetime.fromisoformat(v.replace('Z','+00:00')).astimezone(timezone.utc)
def evaluate(samples):
 accepted=[]; audit=[]; seen=set(); previous=None
 for x in samples:
  sid=x.get('sample_id')
  if not sid or sid in seen: audit.append({'type':'DUPLICATE_SAMPLE','sample_id':sid}); continue
  seen.add(sid)
  try: cur=_ts(x['observed_at_utc'])
  except Exception: audit.append({'type':'INVALID_TIMESTAMP','sample_id':sid}); continue
  if previous and cur<previous: audit.append({'type':'OUT_OF_ORDER_SAMPLE','sample_id':sid}); continue
  previous=cur
  if x.get('resource_alias')!=POLICY['expected_resource_alias']: audit.append({'type':'IDENTITY_MISMATCH','sample_id':sid}); continue
  if x.get('source') not in POLICY['allowed_sources']: audit.append({'type':'SOURCE_UNKNOWN','sample_id':sid}); continue
  accepted.append(x)
 decisions=[]; emitted=set()
 def add(rule,state,refs,reason,severity='info',**extra):
  key=f"{POLICY['expected_resource_alias']}:{rule}"
  if key in emitted and state=='OPEN': audit.append({'type':'COOLDOWN_SUPPRESSED','rule':rule,'cooldown_seconds':POLICY['dedupe']['cooldown_seconds']}); return
  if state in ('OPEN','RECOVER'): emitted.add(key)
  d={'rule_version':POLICY['rule_version'],'rule':rule,'state':state,'sample_refs':refs,'reason':reason,'severity':severity}; d.update(extra); decisions.append(d)
 def valid(x,measure): return x.get('measure_name')==measure and x.get('health_status')=='observed' and x.get('freshness')=='fresh' and x.get('probe_origin') in ('fixture','read-only')
 readiness_open=False; failures=[]; goods=[]
 for x in accepted:
  if x.get('measure_name')!='n8n_readiness': continue
  if not valid(x,'n8n_readiness') or x.get('value') not in (200,503):
   failures=[]; goods=[]; decisions.append({'rule_version':POLICY['rule_version'],'rule':'N8N_READINESS','state':'UNKNOWN','sample_refs':[x['sample_id']],'reason':'missing/stale/blocked/invalid readiness resets streaks','severity':'medium'}); continue
  if x['value']==503:
   goods=[]; failures.append(x)
   if len(failures)>=3 and not readiness_open: add('N8N_READINESS','OPEN',[z['sample_id'] for z in failures[-3:]],'three chronological qualifying failures','high'); readiness_open=True
  else:
   failures=[]
   if readiness_open:
    goods.append(x)
    if len(goods)>=3: add('N8N_READINESS','RECOVER',[z['sample_id'] for z in goods[-3:]],'three chronological qualifying successes after OPEN','info'); readiness_open=False; goods=[]
   else: goods.append(x)
 for x in accepted:
  m=x.get('measure_name'); v=x.get('value')
  if m=='backup_age_hours':
   if x.get('schedule_verified') is not True: add('BACKUP_AGE','UNKNOWN',[x['sample_id']],'backup schedule unverified; no overdue inference','medium'); continue
   if isinstance(v,(int,float)) and v>192: add('BACKUP_AGE','OVERDUE',[x['sample_id']],'backup exceeds verified weekly schedule plus grace; restore UNKNOWN','medium',restore_status='UNKNOWN')
  if m=='p0_reasoner_state' and v=='exited_137' and x.get('oom_killed') is False: add('P0_REASONER','RISK',[x['sample_id']],'exit 137, OOMKilled false, root cause UNKNOWN','high',root_cause='UNKNOWN')
  if m=='tls_probe' and v in ('absent','blocked'): add('TLS','UNKNOWN',[x['sample_id']],'TLS source absent or blocked','medium')
 disk=[x for x in accepted if valid(x,'disk_used_pct') and isinstance(x.get('value'),(int,float))]
 for i in range(len(disk)-2):
  tri=disk[i:i+3]
  if all(x['value']>=90 for x in tri): add('DISK_HIGH','OPEN',[x['sample_id'] for x in tri],'three chronological samples at or above disk threshold','high'); break
 trend=[x for x in accepted if valid(x,'disk_trend_deadline_hours') and isinstance(x.get('value'),(int,float))]
 for i in range(len(trend)-2):
  tri=trend[i:i+3]
  if all(x['value']<=4 for x in tri): add('DISK_TREND_DEADLINE','OPEN',[x['sample_id'] for x in tri],'three chronological deadline samples','high'); break
 if any(x['type']=='IDENTITY_MISMATCH' for x in audit): add('IDENTITY','BLOCK',[],'identity mismatch; no health inference','high')
 if any(x['type']=='SOURCE_UNKNOWN' for x in audit): add('SOURCE','UNKNOWN',[],'source unknown; no health inference','medium')
 return {'rule_version':POLICY['rule_version'],'decisions':decisions,'audit':audit,'accepted_samples':len(accepted),'external_transport':False}
