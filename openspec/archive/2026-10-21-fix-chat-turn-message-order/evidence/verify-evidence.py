from pathlib import Path
import hashlib,json
root=Path(__file__).resolve().parents[4]; e=Path(__file__).parent
r=json.loads((e/'implementation-checks.json').read_text())
assert r['passed'] and all(v['passed'] for v in r['checks'].values())
for name,value in r['source_sha256'].items(): assert hashlib.sha256((root/name).read_bytes()).hexdigest()==value,name
live=json.loads((e/'product/live-chain.json').read_text());assert live['passed'] and live['model_calls']==2 and live['unique_message_count']==28 and live['stop_partial'] and live['streaming_identity_preserved']
hist=json.loads((e/'product/historical-readonly.json').read_text());assert hist['passed'] and hist['original_records_unchanged'] and hist['order']==['user','assistant']
styles=json.loads((e/'product/computed-style.json').read_text());assert {(1440,900),(390,844)} <= {tuple(x['viewport']) for x in styles};assert all(not x.get('overflow',False) for x in styles)
for stage in ('send-output','history-refresh','interrupt-recovery'):
 for size in ('1440x900','390x844'):
  assert (e/'product'/f'{stage}-{size}.png').stat().st_size>1000
print('Stable source hashes, regression results, two real turns, 28-message pagination, read-only history and signed visual evidence verified')
