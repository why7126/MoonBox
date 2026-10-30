"""Execution overlay only; never changes the formal stage read from the main workspace."""
from sqlalchemy import select
from .schema import workspaces, assignments, write_locks
from .integration_schema import candidates


def delivery_overlay(db, space_id, repository_id, visible_ids):
    allowed = set(visible_ids)
    result = {}
    current_changes = {}
    rows = db.execute(select(assignments.c.change_id, assignments.c.delivery_root,
        assignments.c.workspace_id, assignments.c.state, write_locks.c.operation_id)
        .join(workspaces, workspaces.c.id == assignments.c.workspace_id)
        .outerjoin(write_locks, write_locks.c.workspace_id == workspaces.c.id)
        .where(workspaces.c.space_id == space_id, workspaces.c.repository_id == repository_id,
            workspaces.c.lifecycle != 'removed')).mappings()
    for row in rows:
        if row['change_id'] not in allowed:
            continue
        current_changes[row['delivery_root']] = row['change_id']
        for identity in (row['change_id'], row['delivery_root']):
            if identity in allowed:
                result[identity] = {'delivery_workspace_id': row['workspace_id'],
                    'workspace_execution_state': 'occupied' if row['operation_id'] else 'idle',
                    'integration_state': row['state']}
    for row in db.execute(select(candidates).where(candidates.c.space_id == space_id,
        candidates.c.repository_id == repository_id).order_by(candidates.c.created_at, candidates.c.id)).mappings():
        if row['change_id'] not in allowed:
            continue
        for identity in (row['change_id'], row['delivery_root']):
            if identity in allowed and row['state'] != 'invalidated':
                # A previous child Change must not override the current child's progress.
                if identity == row['delivery_root'] and current_changes.get(identity, row['change_id']) != row['change_id']:
                    continue
                result.setdefault(identity, {'delivery_workspace_id': row['workspace_id'], 'workspace_execution_state': 'idle'})['integration_state'] = row['state']
    return result
