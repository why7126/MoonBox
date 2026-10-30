"""Verify measured request evidence; missing data and failed samples fail closed."""
from pathlib import Path
import hashlib,json,statistics,sys
BASE=Path(__file__).resolve().parent
REPO=next(p for p in BASE.parents if (p/'AGENTS.md').is_file())

def read(name):
    return json.loads((BASE/name).read_text())

def samples(variant, scenario):
    name=f'fixed-final-{variant}-{scenario}'
    if scenario=='cold':
        rows=[read(f'{name}-{i}.json') for i in range(1,6)]
        values=[x for row in rows for x in row['samples']]
        assert len(values)==5
    else:
        rows=[read(name+'.json')]
        raw=rows[0]['samples']
        assert len(raw)==11, 'one warmup plus ten samples/batches required'
        values=raw[1:] if scenario=='warm' else [x for batch in raw[1:] for x in batch]
        assert len(values)==(10 if scenario=='warm' else 30)
    for row in rows:
        assert not row['blocked_actions']
        if variant=='candidate':
            for module, digest in row['executed_code_hashes'].items():
                assert hashlib.sha256((REPO/f'src/backend/app/governance/{module}.py').read_bytes()).hexdigest()==digest, module+' changed'
    return rows,values

def identity():
    fingerprints=set()
    for variant in ('baseline','candidate'):
        for scenario in ('cold','warm','concurrent'):
            rows,values=samples(variant,scenario)
            for row in rows: fingerprints.add(row['database_fixture_sha256'])
            for item in values:
                assert item['request_id'] and item['request_id_matches_prepare'] and item['audit_matches']
                assert item['http']==200 and item['error_type'] is None
                assert item['sql']['count']>0
                assert all(span['request_id']==item['request_id'] for span in item['spans'])
                assert sum(s['name']=='prepare' for s in item['spans'])==1
                for span in item['spans']:
                    intervals=sorted((s['start'],s['end']) for s in item['spans'] if s['parent']==span['id'])
                    end=span['start'];covered=0
                    for left,right in intervals:covered+=max(0,right-max(left,end));end=max(end,right)
                    assert abs(span['exclusive_ms']-max(0,span['duration_ms']-covered*1000))<0.01
    assert len(fingerprints)==1

def stats(values):
    times=[v['total_ms'] for v in values]
    return {'median_ms':statistics.median(times),'max_ms':max(times)}

def performance():
    identity();report={};all_revisions=set();all_resources=set()
    for scenario in ('cold','warm','concurrent'):
        comparison={}
        for variant in ('baseline','candidate'):
            rows,values=samples(variant,scenario)
            for row in rows:all_resources.add(json.dumps(row['resources'],sort_keys=True))
            for value in values:
                all_revisions.update((s['revision'],s['files'],s['bytes']) for s in value['spans'] if 'revision' in s)
                if variant=='candidate':assert not value['sql_errors'], 'candidate database error'
            comparison[variant]=stats(values)
            if scenario=='concurrent':
                assert len({v['object_id'] for v in values})==3
                for oid in {v['object_id'] for v in values}:
                    assert len({v['conversation_hash'] for v in values if v['object_id']==oid})==1
        b,c=comparison['baseline'],comparison['candidate'];report[scenario]=comparison
        if scenario=='warm':assert c['median_ms']<=2000 and c['max_ms']<=4000 and c['median_ms']<=b['median_ms']*.5
        elif scenario=='cold':assert c['median_ms']<=4000 and c['max_ms']<=6000 and c['median_ms']<=b['median_ms']*1.1
        else:assert c['median_ms']<=b['median_ms']*1.1 and c['max_ms']<=b['max_ms']*1.1
    assert len(all_revisions)==1 and len(all_resources)==1, 'dataset or resource mismatch'
    print(json.dumps(report))

def browser():
    data=read('natural-browser.json');values=data['samples']
    assert len(values)==11 and values[0]['warmup'] is True
    for path,digest in data['source_files_sha256'].items():
        assert hashlib.sha256((REPO/path).read_bytes()).hexdigest()==digest
    for row in values:
        assert row['request_id']==row['prepare_request_id'] and row['audit_matches']
        assert row['http']==200 and row['arrived'] and row['interactive']
        assert row['history_ms']>=0 and row['interactive_ms']>=0
    warm=values[1:]
    assert statistics.median(x['route_upper_bound_ms'] for x in warm)<=2500
    assert max(x['route_upper_bound_ms'] for x in warm)<=4500
    assert statistics.median(x['total_ms'] for x in warm)<=2000 and max(x['total_ms'] for x in warm)<=4000

def interactions():
    data=read('interaction-observation.json')
    assert data['double_click_requests']==1
    assert data['before_counts']==data['after_counts']
    assert data['fault_marker_consumed'] and len(data['controlled_failures'])==2
    cases={x['case']:x for x in data['observed_cases']}
    cancel=cases['navigate-away-during-preparation']
    assert cancel['was_pending'] and cancel['stayed_away_after_response']
    failed=cases['controlled-503-screenshot']
    assert failed['safe_error_visible'] and failed['remained_on_card'] and failed['retry_enabled']
    assert cases['retry-after-controlled-503-screenshot']['arrived']

def performance_browser():
    performance();browser()

def recovery():
    data=read('recovery.json')
    assert data['health_status']==200 and data['hook_absent'] and data['temporary_database_removed']
    assert data['original_hashes']==data['restored_hashes']
    assert data['web_original_manifest']==data['web_restored_manifest']

if __name__=='__main__':
    check={'identity':identity,'performance':performance,'browser':browser,'performance-browser':performance_browser,'interactions':interactions,'recovery':recovery}[sys.argv[1]]
    try:check()
    except (AssertionError,KeyError,FileNotFoundError,ValueError) as exc:
        print(json.dumps({'check':sys.argv[1],'status':'failed','reason':str(exc).replace(str(REPO),'.')}));raise SystemExit(1)
    print(json.dumps({'check':sys.argv[1],'status':'passed'}))
