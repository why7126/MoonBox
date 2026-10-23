"""Read-only facts from the disposable Sprint archive runtime; no prompt export."""
import argparse
import json
import sqlite3
from pathlib import Path


def observe(root, sprint):
    root = Path(root).resolve()
    if root.parent != Path('/private/tmp') or not root.name.startswith('moonbox-governance-live-'):
        raise ValueError('isolated source required')
    with sqlite3.connect((root / 'moonbox.db').as_uri() + '?mode=ro', uri=True) as db:
        db.row_factory = sqlite3.Row
        sessions = db.execute('SELECT c.id FROM chat_conversations c JOIN chat_relations r ON r.conversation_id=c.id WHERE r.object_id=? AND r.role=?', (sprint, 'primary')).fetchall()
        rows = []
        for session in sessions:
            for turn in db.execute('SELECT id,status,error_code FROM chat_turns WHERE conversation_id=?', (session['id'],)):
                sync = []
                for event in db.execute("SELECT sequence,payload FROM chat_events WHERE turn_id=? AND event_type='execution.tool'", (turn['id'],)):
                    payload = json.loads(event['payload'])
                    command = (payload.get('arguments') or {}).get('command', '')
                    if payload.get('phase') == 'completed' and 'sync-workflow-status.py --event sprint.archive' in command and sprint in command:
                        sync.append({'sequence': event['sequence'], 'exit_code': payload.get('exit_code'), 'dry_run': '--dry-run' in command})
                rows.append({**dict(turn), 'conversation_id': session['id'], 'sync': sync})
        guards = [dict(row) for row in db.execute('SELECT object_id,state,action,operation_id,confirmed_stage,reason_code FROM governance_execution_guards WHERE object_id=?', (sprint,))]
        events = [dict(row) for row in db.execute("SELECT event_name,result,properties FROM usage_events WHERE event_name IN ('governance.prepare','chat.send')")]
        events = [{**row, 'properties': json.loads(row['properties'])} for row in events]
    return {'sample': sprint, 'source': 'isolated-live-product', 'session_count': len(sessions), 'turns': rows, 'guards': guards,
            'active_exists': (root / 'project/iterations/change' / sprint).exists(),
            'archive_exists': (root / 'project/iterations/archive' / sprint / 'sprint.yaml').is_file(),
            'behavior': [e for e in events if e['properties'].get('object_id') == sprint or e['properties'].get('conversation_id') in [r['id'] for r in sessions]]}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--root', required=True); parser.add_argument('--sprint', default='sprint-099'); parser.add_argument('--output', required=True)
    args = parser.parse_args(); result = observe(args.root, args.sprint)
    Path(args.output).write_text(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps({k: result[k] for k in ('sample', 'session_count', 'turns', 'guards', 'active_exists', 'archive_exists')}, ensure_ascii=False))
