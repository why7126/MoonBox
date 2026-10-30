"""Read-only native acceptance proof for the formal AC runner; no prompt export."""
import sqlite3

MODES = frozenset({'live', 'continuation', 'stopped', 'recovered'})


def read_proof(path, turn_id, operation_id, mode, expected_status='passed'):
    if mode not in MODES or expected_status not in {'passed', 'blocked', 'failed', 'cancelled'}:
        raise ValueError('invalid_acceptance_proof')
    with sqlite3.connect(path.resolve().as_uri()+'?mode=ro', uri=True) as db:
        db.row_factory=sqlite3.Row
        row=db.execute('''SELECT o.id,o.source_turn_id,o.conversation_id,o.attempt_id,o.input_digest,
            o.status,o.cleanup_state,o.resume_count,o.cancel_requested,t.status AS turn_status,
            t.conversation_id AS turn_conversation,e.executor_closed,e.files_collected
            FROM verification_operations o JOIN chat_turns t ON t.id=o.source_turn_id
            JOIN moonbox_execution_receipts e ON e.turn_id=t.id WHERE o.id=? AND t.id=?''',
            (operation_id,turn_id)).fetchone()
        result={'verified':False,'reason':'native-acceptance-proof-incomplete','turn_id':turn_id,'operation_id':operation_id}
        if not row:return result
        result.update(turn_status=row['turn_status'],operation_status=row['status'],cleanup_state=row['cleanup_state'],
                      resume_count=row['resume_count'],conversation_id=row['conversation_id'])
        if row['conversation_id']!=row['turn_conversation'] or row['status']!=expected_status or row['cleanup_state']!='released':return result
        if not row['executor_closed'] or not row['files_collected']:return result
        checks=db.execute('SELECT status FROM verification_ac_results WHERE attempt_id=?',(row['attempt_id'],)).fetchall()
        if expected_status=='passed' and (not checks or any(c['status']!='passed' for c in checks)):return result
        if mode=='live':
            wait=db.execute('SELECT state,generation FROM verification_tool_waits WHERE operation_id=? AND source_turn_id=?',
                            (operation_id,turn_id)).fetchone()
            generation=db.execute('SELECT generation FROM chat_turns WHERE id=?',(turn_id,)).fetchone()[0]
            valid=row['turn_status']=='completed' and row['resume_count']==0 and not row['cancel_requested'] and wait and wait['state']=='delivered' and wait['generation']==generation
        elif mode=='continuation':
            budget=db.execute('SELECT tokens,actual_tokens FROM chat_usage_reservations WHERE turn_id=?',(turn_id,)).fetchone()
            delivery=db.execute('''SELECT d.state,d.attempt_id,d.input_digest,d.target_turn_id,t.status,t.conversation_id,
                e.executor_closed,e.files_collected FROM verification_result_deliveries d
                JOIN chat_turns t ON t.id=d.target_turn_id JOIN moonbox_execution_receipts e ON e.turn_id=t.id
                WHERE d.operation_id=?''',(operation_id,)).fetchone()
            valid=(row['turn_status']=='failed' and row['resume_count']==1 and not row['cancel_requested'] and delivery
                and delivery['state']=='consumed' and delivery['attempt_id']==row['attempt_id'] and delivery['input_digest']==row['input_digest']
                and delivery['conversation_id']==row['conversation_id'] and delivery['status']=='completed'
                and delivery['executor_closed'] and delivery['files_collected'] and budget
                and (not budget['tokens'] or (budget['actual_tokens'] is not None and budget['actual_tokens']<budget['tokens'])))
            if delivery:result['target_turn_id']=delivery['target_turn_id']
        else:
            valid=(row['turn_status']=='stopped' and row['resume_count']==0
                   and bool(row['cancel_requested'])==(mode=='stopped'))
        if valid:result.update(verified=True,reason='native-acceptance-verified')
        return result
