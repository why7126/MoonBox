"""Read-only restart snapshots for the explicitly controlled disposable runtime."""
import json,sqlite3,sys,time
from pathlib import Path
from uuid import uuid5,NAMESPACE_URL
r=Path(sys.argv[1]).resolve()
if r.parent!=Path('/private/tmp') or not r.name.startswith('moonbox-governance-live-'):raise ValueError('isolated root required')
marker=json.loads((r/'recovery-restart-needed.json').read_text());tid=marker['turn_id']
db=sqlite3.connect((r/'moonbox.db').as_uri()+'?mode=ro',uri=True);db.row_factory=sqlite3.Row
turn=dict(db.execute('select status,executor_turn_id from chat_turns where id=?',(tid,)).fetchone());op=dict(db.execute('select state,stage,auto_retry_count,manual_count,execution_terminal,application_id from governance_operations where origin_turn_id=?',(tid,)).fetchone())
tail=json.loads((r/'tail-observed.json').read_text());assert tail['conversation_id']==marker['conversation_id'] and tail['status']=='completed'
snapshot={**turn,**op,'observed_executor_terminal':tail['status'],'turn_count':db.execute('select count(*) from chat_turns where conversation_id=?',(marker['conversation_id'],)).fetchone()[0],'model_turn_count':db.execute('select count(*) from chat_turns where conversation_id=? and executor_turn_id is not null',(marker['conversation_id'],)).fetchone()[0]}
if sys.argv[2]=='after-application':
 # A missed generation window is not relabelled: verify the observed process
 # crash from the original application's persisted recovery chronology.
 app=db.execute('select * from governance_applications where id=?',(snapshot['application_id'],)).fetchone()
 trace=db.execute('select task_trace_id from task_traces where turn_id=?',('governance:'+app['id'],)).fetchone()
 spans=[dict(row) for row in db.execute('select span_name,created_at from task_trace_spans where task_trace_id=? order by created_at',(trace['task_trace_id'],))]
 recovered=next(row['created_at'] for row in spans if row['span_name']=='governance.recovering')
 applied=next(row['created_at'] for row in spans if row['span_name']=='governance.applied')
 assert app['state']=='applied' and app['phase']=='verified' and app['created_at']<recovered<applied
 prior_counts={name:db.execute('select count(*) from chat_turns where conversation_id=? and created_at<=?'+extra,(marker['conversation_id'],recovered)).fetchone()[0] for name,extra in [('turn_count',''),('model_turn_count',' and executor_turn_id is not null')]}
 assert all(snapshot[k]==v for k,v in prior_counts.items())
 assert snapshot['auto_retry_count']==snapshot['manual_count']==0
 entry={'turn_id':tid,'mode':'service_crash_during_apply','source':'operator_observed_process_crash_and_persisted_application_trace','initial_generation_window_check':'not_met','before':prior_counts,'after':snapshot,'application_id':app['id'],'recovery_trace':spans,'identity_and_budget_preserved':True}
 hist=r/'restart-history.json';rows=json.loads(hist.read_text()) if hist.exists() else [];rows.append(entry);hist.write_text(json.dumps(rows));(r/'recovery-restarted.json').write_text(json.dumps(marker));print('original application recovery chronology verified; observer released')
elif sys.argv[2]=='before':
 assert marker.get('mode')=='service_crash' and snapshot['status']=='running' and snapshot['application_id'] is None
 (r/'restart-before.json').write_text(json.dumps({'turn_id':tid,'before':snapshot,'started_at':time.time()}));print('actual post-model/pre-business checkpoint captured')
else:
 prior=json.loads((r/'restart-before.json').read_text());assert prior['turn_id']==tid
 for role in ('worker','controller'):
  p=r/'private'/str(uuid5(NAMESPACE_URL,'moonbox-recovery-runtime:'+role))/'operation.json';heartbeat=json.loads(p.read_text())['time'];assert heartbeat>prior['started_at'] and time.time()-heartbeat<10
 unchanged=all(snapshot[k]==prior['before'][k] for k in ('auto_retry_count','manual_count','executor_turn_id','turn_count','model_turn_count'));assert unchanged
 hist=r/'restart-history.json';rows=json.loads(hist.read_text()) if hist.exists() else [];rows.append({'turn_id':tid,'mode':'service_crash','before':prior['before'],'after':snapshot,'identity_and_budget_preserved':unchanged});hist.write_text(json.dumps(rows));(r/'recovery-restarted.json').write_text(json.dumps(marker));print('restart verified; observer released')
