"""Consume already human-confirmed operations; never manufactures a confirmation."""
import logging
from sqlalchemy import select, update, and_, or_
from app.chat.service import ChatError
from app.moonbox_worktree import WorktreeConflict
from .integration_schema import operations, candidates
from .integration import integrate, reconcile_applied


def tick(factory, limit=10):
    with factory() as db:
        rows = list(db.execute(select(operations.c.id, operations.c.actor_id, candidates.c.space_id,
            candidates.c.repository_id).join(candidates, candidates.c.id == operations.c.candidate_id).where(
                or_(operations.c.state.in_(('queued', 'confirmed', 'applying', 'recovery_required')), and_(operations.c.state == 'completed', operations.c.governance_state != 'completed')))
            .order_by(operations.c.updated_at, operations.c.id).limit(limit)).mappings())
    completed = 0
    for row in rows:
        try:
            if reconcile_applied(factory, row['id']):
                from .governance_projection import try_apply
                try_apply(factory, row['id'])
                completed += 1
                continue
            with factory() as db:
                if db.scalar(select(operations.c.state).where(operations.c.id == row['id'])) == 'recovery_required':
                    continue
            result = integrate(factory, row['actor_id'], row['space_id'], row['repository_id'], row['id'])
            completed += int(result['state'] == 'completed')
        except (ChatError, WorktreeConflict):
            with factory() as db:
                db.execute(update(operations).where(operations.c.id == row['id'], operations.c.state != 'completed').values(
                    state='recovery_required', error_code='current_authority_or_candidate_changed'))
                db.commit()
        except Exception:
            # Unknown persistence/Git outcomes keep locks and intent for reconciliation.
            logging.getLogger('moonbox.workspace').warning('merge_operation_reconcile_pending')
    return completed
