from pathlib import Path
import json,statistics,hashlib,sys
p=Path(__file__).parent
root=next(x for x in p.parents if (x/'AGENTS.md').exists())
meta=json.loads((p/'matrix-environment.json').read_text())
for path,digest in meta['source_hashes'].items():assert hashlib.sha256((root/path).read_bytes()).hexdigest()==digest,path
fingerprints=set();resources=set();report={}
for kind in ['warm','cold','concurrent']:
 report[kind]={}
 for variant in ['baseline','candidate']:
  data=[json.loads(x.read_text()) for x in sorted(p.glob(f'matrix-{variant}-{kind}*.json'))]
  raw=[x for d in data for x in d['samples']]
  values=raw if kind=='cold' else raw[1:] if kind=='warm' else [x for batch in raw[1:] for x in batch]
  assert len(values)=={'warm':10,'cold':5,'concurrent':30}[kind]
  for d in data:
   fingerprints.add(d['database_fixture_sha256']);resources.add(json.dumps(d['resources'],sort_keys=True));assert not d['blocked_actions']
  for x in values:
   assert x['http']==200 and x['request_id_matches_prepare'] and x['audit_matches'] and not x['sql_errors']
   assert all(s['request_id']==x['request_id'] and 0<=s['exclusive_ms']<=s['duration_ms']+.01 for s in x['spans'])
  if kind=='concurrent':
   assert len({x['object_id'] for x in values})==3
   for oid in {x['object_id'] for x in values}:assert len({x['conversation_hash'] for x in values if x['object_id']==oid})==1
  times=[x['total_ms'] for x in values];report[kind][variant]={'median_ms':statistics.median(times),'max_ms':max(times)}
 b,c=report[kind]['baseline'],report[kind]['candidate']
 if kind=='warm':assert c['median_ms']<=2000 and c['max_ms']<=4000 and c['median_ms']<=b['median_ms']*.5
 elif kind=='cold':assert c['median_ms']<=4000 and c['max_ms']<=6000 and c['median_ms']<=b['median_ms']*1.1
 else:assert c['median_ms']<=b['median_ms']*1.1 and c['max_ms']<=b['max_ms']*1.1
assert len(fingerprints)==len(resources)==1
print(json.dumps({'status':'passed','scope':'entry-path-only; full-send-cost-reported-separately','result':report}))
