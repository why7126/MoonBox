"""Read-only export of isolated product facts; never creates or repairs a sample."""
import argparse,hashlib,json,sqlite3
from pathlib import Path
import yaml

PROJECT=Path(__file__).resolve().parents[3]
CHANGE=PROJECT/'openspec/changes/add-governance-command-durable-recovery'
SAMPLES=[f'{prefix}-{number}-recovery-{suffix}' for prefix in ('REQ','BUG') for number,suffix in (('9094','normal'),('9093','recovery'))]


def export(root):
    root=Path(root).resolve()
    if root.parent!=Path('/private/tmp') or not root.name.startswith('moonbox-governance-live-'):raise ValueError('isolated read-only source required')
    db=sqlite3.connect((root/'moonbox.db').as_uri()+'?mode=ro',uri=True);db.row_factory=sqlite3.Row
    rows=[]
    board_path=CHANGE/'evidence/live/board-readback.json'
    board=json.loads(board_path.read_text()) if board_path.exists() else {}
    for oid in SAMPLES:
        operation=db.execute('select * from governance_operations where object_id=? order by created_at desc limit 1',(oid,)).fetchone()
        if not operation:rows.append({'sample':oid,'passed':False,'reason':'not_collected'});continue
        turn=db.execute('select * from chat_turns where id=?',(operation['origin_turn_id'],)).fetchone()
        candidate=db.execute('select * from governance_candidates where id=?',(operation['candidate_id'],)).fetchone()
        apps=db.execute('select id,state,phase from governance_applications where candidate_id=?',(candidate['id'],)).fetchall()
        attempts=db.execute('select id,kind,state from governance_recovery_attempts where operation_id=?',(operation['id'],)).fetchall()
        before=json.loads((root/'private'/candidate['id']/'baseline.json').read_text())
        base=before['base_path'];target=base.replace('/plan/','/review/')
        original={p[len(base)+1:] for p in before['files'] if p.startswith(base+'/')}
        folder=root/'project'/target
        actual={str(p.relative_to(folder)) for p in folder.rglob('*') if p.is_file()} if folder.exists() else set()
        kind='requirements' if oid.startswith('REQ') else 'bugs';domain='req' if kind=='requirements' else 'bug'
        registry=yaml.safe_load((root/f'project/issues/{kind}/_registry.yaml').read_text())
        entry=next(e for e in registry['entries'] if e['id']==oid)
        trace=yaml.safe_load((folder/'trace.md').read_text().split('---',2)[1]) if folder.exists() else {}
        index=(root/f'project/issues/{kind}/CHANGELOG.md').read_text()
        index_rows=[line for line in index.splitlines() if line.startswith('| '+oid+' |')]
        proof=[]
        for event in db.execute("select sequence,payload from chat_events where turn_id=? and event_type='execution.tool'",(turn['id'],)):
            payload=json.loads(event['payload']);command=(payload.get('arguments') or {}).get('command','')
            if payload.get('phase')=='completed' and payload.get('exit_code')==0 and 'sync-workflow-status.py' in command and domain+'.review' in command:
                proof.append(event['sequence'])
        recovery=oid.endswith('-recovery')
        counts=db.execute('select count(*) from chat_turns where conversation_id=?',(turn['conversation_id'],)).fetchone()[0]
        model_counts=db.execute('select count(*) from chat_turns where conversation_id=? and executor_turn_id is not null',(turn['conversation_id'],)).fetchone()[0]
        restarts=json.loads((root/'restart-history.json').read_text()) if (root/'restart-history.json').exists() else []
        restart=next((r for r in restarts if r['turn_id']==turn['id']),None)
        conditions={
          'board_after_fresh_login':board.get('after_fresh_login') is True and any(r.get('sample')==oid and r.get('stage')=='approved' for r in board.get('samples',[])),
          'business_completed':operation['state']=='completed' and operation['stage']=='complete',
          'original_terminal_preserved':operation['execution_terminal']==turn['status'] and turn['status']=='completed',
          'unique_verified_application':len(apps)==1 and apps[0]['state']=='applied' and apps[0]['phase']=='verified',
          'whole_migration':actual==original|{'review.md'} and not (root/'project'/base).exists(),
          'registry_trace_index':entry['status']=='approved' and entry['path'].rstrip('/')==target and trace.get('status')=='approved' and trace.get('lifecycle_stage')=='review' and len(index_rows)==1 and 'approved' in index_rows[0] and target in index_rows[0],
          'same_turn_command_observed':bool(proof),
          'service_crash_preserved_identity_and_budgets':not recovery or bool(restart and restart.get('identity_and_budget_preserved') and ((restart.get('mode')=='service_crash' and restart['before']['application_id'] is None and restart['before']['status']=='running') or (restart.get('mode')=='service_crash_during_apply' and restart['application_id']==operation['application_id'] and any(s['span_name']=='governance.recovering' for s in restart['recovery_trace'])))),
          'recovery_without_new_model_turn':not recovery or bool(restart and model_counts==restart['before']['model_turn_count'] and counts==restart['before']['turn_count']),
        }
        rows.append({'sample':oid,'passed':all(conditions.values()),'checks':conditions,'turn_id':turn['id'],'conversation_id':turn['conversation_id'],'operation_id':operation['id'],'candidate_id':candidate['id'],'terminal':turn['status'],'application_ids':[a['id'] for a in apps],'attempt_ids':[a['id'] for a in attempts],'original_file_count':len(original),'final_file_count':len(actual),'command_event_sequences':proof,'turn_count':counts,'model_turn_count':model_counts,'restart':restart})
    result={'evidence_kind':'observed_product_readonly_export','passed':all(r['passed'] for r in rows),'samples':rows,'readback_runtime_fingerprints':json.loads((root/'runtime-fingerprints.json').read_text()),'fixture_preflight':json.loads((root/'fixture-preflight.json').read_text())}
    target=CHANGE/'evidence/live/observation.json';target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'passed':result['passed'],'samples':[{k:r[k] for k in ('sample','passed')} for r in rows]}))


def verify(path):
    data=json.loads(Path(path).read_text())
    assert data['evidence_kind']=='observed_product_readonly_export' and data['passed']
    assert {r['sample'] for r in data['samples']}==set(SAMPLES)
    assert all(r['passed'] and all(r['checks'].values()) for r in data['samples'])
    assert all(row['fixture_preflight']=='passed' for row in data['fixture_preflight'])
    for relative, digest in data['readback_runtime_fingerprints'].items():
        if relative.startswith('src/backend/app/'):
            assert hashlib.sha256((PROJECT/relative).read_bytes()).hexdigest()==digest, 'runtime input changed: '+relative
    print('固定 REQ/BUG 真实正常与恢复样本事实核验通过')

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--export');parser.add_argument('--verify');args=parser.parse_args()
    if args.export:export(args.export)
    elif args.verify:verify(args.verify)
    else:parser.error('choose export or verify')
