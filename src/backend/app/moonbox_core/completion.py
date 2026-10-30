"""Reconcile terminal collection without treating expiry as proof of process termination."""
import re
import logging
import json
import subprocess
from sqlalchemy import select, update
from app.chat import service
from app.chat.schema import turns, conversations
from .schema import execution_receipts, write_locks
from .sessions import execution_workspace
from .workspaces import release


def reconcile(factory, limit=10):
    with factory() as db:
        pending = list(db.execute(select(turns.c.id, turns.c.conversation_id, turns.c.generation,
            turns.c.status, execution_receipts.c.executor_id, execution_receipts.c.executor_closed, execution_receipts.c.scope_json)
            .join(execution_receipts, execution_receipts.c.turn_id == turns.c.id)
            .join(write_locks, write_locks.c.operation_id == turns.c.id)
            .where(turns.c.status.in_(service.TERMINAL))
            .order_by(execution_receipts.c.last_checked_at, turns.c.id).limit(limit)).mappings())
        if pending:
            db.execute(update(execution_receipts).where(execution_receipts.c.turn_id.in_([row['id'] for row in pending]))
                .values(last_checked_at=service.now()))
            db.commit()
    completed = 0
    for item in pending:
        try:
            completed += int(_reconcile_one(factory, item))
        except Exception:
            # One inaccessible/stale task must not starve unrelated workspaces.
            # Retain its lease and receipt; never infer process death from this failure.
            logging.getLogger(__name__).warning('workspace_completion_pending')
    return completed


def _reconcile_one(factory, item):
    if not item['executor_closed']:
        name = item['executor_id']
        if not isinstance(name, str) or not re.fullmatch(r'moonbox-chat-session-[a-f0-9]{32}', name):
            return False
        checked = subprocess.run(['docker', 'ps', '-a', '--filter', 'name=^/' + name + '$',
            '--format', '{{.Names}}'], capture_output=True, text=True, timeout=10)
        if checked.returncode or checked.stdout.strip():
            return False
    with factory() as db:
        parent = db.execute(select(conversations).where(conversations.c.id == item['conversation_id'])).mappings().one()
        service.conversation(db, parent['owner_id'], parent['id'])
        managed = execution_workspace(db, parent)
        if not managed:
            return False
        from app.moonbox_rollout.schema import references
        active = db.scalar(select(references.c.point_id).where(references.c.workspace_id == managed[0]['id'],
            references.c.owner_type == 'active_turn', references.c.owner_id == item['id']))
        allowed = json.loads(item['scope_json'] or '[]')
    if active and allowed:
        from app.chat.snapshot_store import capture
        from app.moonbox_rollout.execution import publish_turn
        def fence(db):
            lease = db.execute(select(write_locks).where(write_locks.c.workspace_id == managed[0]['id'])).mappings().first()
            if not lease or (lease['operation_id'], lease['generation']) != (item['id'], item['generation']):
                raise ValueError('workspace_completion_fenced')
        snap = capture(factory, parent['id'], item['id'], managed[1], 'interrupted', fence=fence, policy_roots=allowed)
        with factory() as db:
            fence(db)
            publish_turn(db, managed[0], item['id'], snap, allowed, 'interrupted')
            db.commit()
    with factory() as db:
        from app.governance.preparation import collect
        collect(db, parent, item['id'], managed[1], item['status'])
        db.execute(update(execution_receipts).where(execution_receipts.c.turn_id == item['id']).values(
            executor_closed=1, files_collected=1))
        release(db, managed[0]['id'], item['id'], item['generation'])
        db.commit()
    return True
