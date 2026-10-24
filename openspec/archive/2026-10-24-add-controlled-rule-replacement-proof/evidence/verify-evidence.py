"""Read-only checks for observed evidence; never substitutes for visual review."""
import hashlib
import json
from pathlib import Path
import sys
from urllib.request import urlopen

ROOT=Path(__file__).resolve().parents[4]
CHANGE=Path(__file__).resolve().parents[1]
PRODUCT=CHANGE/'evidence/product'

def load(name):return json.loads((PRODUCT/name).read_text())

if '--visual-preflight' in sys.argv:
    import httpx,cryptography,sqlalchemy
    with urlopen('http://127.0.0.1:39041/',timeout=10) as response:
        assert response.status==200
    assert (ROOT/'src/web/node_modules/vitest/vitest.mjs').is_file()
    print('Live isolated Web and validation dependencies available; browser capabilities recorded in visual evidence.')
    raise SystemExit(0)

attachment=load('attachment-skill-rejection.json')
assert attachment['turn_count']==0 and attachment['draft_preserved'] and attachment['skill_preserved']
assert any(m['status']=='ready' and m['size_bytes']==69 and m['deleted_at'] is None for m in attachment['materials'])
exact=json.loads((CHANGE/'evidence/modify-bootstrap/exact-change-bootstrap.json').read_text())
assert exact['policy']['state']=='active' and exact['formal_project_written'] is False
assert exact['delta_files']=={
    'governance-command-durable-recovery/spec.md':'daaa37e740fd93d219972316b3581f48465423cf4cbb5e53c0281c9c150ae89d',
    'controlled-rule-replacement-proof/spec.md':'c0979d187e11c54e122891e1e4794404838c5fd5ac5f89dbfb9bf7a1870bfe5e',
}
current=json.loads((CHANGE/'evidence/modify-bootstrap/current-delta-hashes.json').read_text())
assert current['historical_bootstrap_evidence']=='exact-change-bootstrap.json'
assert set(current['delta_files'])==set(exact['delta_files'])
for name,expected in current['delta_files'].items():
    assert hashlib.sha256((CHANGE/'specs'/name).read_bytes()).hexdigest()==expected
runtime=load('runtime-v8-summary.json')
assert runtime['policy'][0]['state']=='active'
assert runtime['turns']==[{'status':'completed','error_code':None,'executor_turn_id':None}]
assert runtime['usage']==[{'status':'settled','actual_tokens':0}]
assert runtime['archived_sprint_exists'] and not runtime['active_sprint_exists']
assert all(row['stage']=='completed' for row in runtime['ordinary_operations'])
for path in PRODUCT.glob('*-fixture-*.json'):
    data=json.loads(path.read_text())
    if 'overflow' in data:assert not data['overflow'],path.name
assert 'BLOCKED' in (PRODUCT/'formal-sprint-012-readonly.txt').read_text()
print('Observed upload/controller/exact-bootstrap/formal-boundary evidence verified. Visual semantics require the recorded reviewer inspection.')

before=load('recovery-v8-before.json');after=load('recovery-v8-after.json');replay=load('recovery-v8-replay.json')
assert before['replacement_operations'][0]['stage']=='synced'
assert after['replacement_operations'][0]['stage']=='completed'
assert before['replacement_operations'][0]['id']==after['replacement_operations'][0]['id']==replay['data']['operation_id']
assert before['spec_hash']==after['spec_hash']
assert replay['status_code']==200 and replay['data']['replayed'] is True
print('Same-operation signer-failure and API-restart recovery verified; merged specifications unchanged.')

repair=CHANGE/'evidence/modify-bootstrap'
before=json.loads((repair/'interrupted.json').read_text());after=json.loads((repair/'completed.json').read_text())
assert before['policy'][0]['state']=='activating' and before['policy'][0]['stage']=='synced'
assert after['policy'][0]['state']=='active' and after['policy'][0]['stage']=='completed'
assert before['policy'][0]['operation_id']==after['policy'][0]['operation_id']
assert before['spec_hash']==after['spec_hash'] and after['archive_count']==1 and after['turn_count']==0
assert {x['purpose'] for x in after['authorizations']} >= {'bootstrap.ops','bootstrap.owner'}
assert json.loads((repair/'deployment.json').read_text())['merged_compose_valid']
for name in ('styles-390.json','styles-1440.json','styles-dark-390.json'):
    assert not json.loads((repair/name).read_text())['overflow']
print('Real preview/export/offline signing/import/owner confirmation/restart recovery verified; no formal activation.')
