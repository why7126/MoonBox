"""Finish terminal candidate collection after a worker interruption.

The external turn is never restarted here. Collection re-reads its existing
workspace facts and is idempotent because it only acts on running candidates.
"""
import logging

from sqlalchemy import select

from app.chat.schema import conversations, governance_candidates as candidates, turns
from app.governance.preparation import collect


def reconcile_terminal_candidates(factory, resolve_workspace):
    with factory() as db:
        rows = list(db.execute(select(
            candidates.c.id, candidates.c.conversation_id, candidates.c.prepared_turn_id,
            turns.c.status,
        ).join(turns, turns.c.id == candidates.c.prepared_turn_id)
            .where(candidates.c.state == 'running',
                   turns.c.status.in_(('completed', 'failed', 'stopped')))
            .order_by(candidates.c.created_at, candidates.c.id).limit(50)).all())
    for candidate_id, conversation_id, turn_id, terminal in rows:
        try:
            with factory() as db:
                row = db.execute(select(candidates.c.state, turns.c.status,
                    conversations).join(turns, turns.c.id == candidates.c.prepared_turn_id)
                    .join(conversations, conversations.c.id == candidates.c.conversation_id)
                    .where(candidates.c.id == candidate_id)).mappings().first()
                if not row or row['state'] != 'running' or row['status'] != terminal:
                    continue
                if row['active_turn_id'] is not None:
                    continue
                _, workspace = resolve_workspace(conversation_id)
                if not workspace.is_dir():
                    raise OSError('candidate workspace unavailable')
                collect(db, row, turn_id, workspace, terminal)
        except Exception as error:
            logging.getLogger(__name__).warning(
                'candidate_recovery_blocked candidate_id=%s cause_type=%s',
                candidate_id, type(error).__name__)
