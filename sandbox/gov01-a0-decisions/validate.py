import json
from pathlib import Path
r=json.loads((Path(__file__).parent.parent/'reports/evidence/2026-11-23-hermes-gov01-s2-a0-register.json').read_text())
ds=r['decisions']; assert len(ds)==5
assert [d['id'] for d in ds]==['A0-1','A0-2','A0-3','A0-4','A0-5']
for d in ds:
    assert d['status']=='AWAITING_A0_DECISION'
    assert 2 <= len(d['options']) <= 3
    assert d['recommendation_status']=='PROPOSAL_NOT_APPROVED'
print(json.dumps({'schema':'PASS','decisions':5,'unique_ids':True,'all_pending':True,'implicit_approval':False}))
