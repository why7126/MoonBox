"""Turn-to-point publication: every turn has history, only writable scopes retain points."""
from sqlalchemy import select, delete
from app.moonbox_worktree import Repository
from app.moonbox_exec_server.scope import policy_id
from . import catalog
from .schema import points, references


def publish_turn(db, workspace, turn_id, snapshot, allowed, phase):
    if not allowed:
        return None
    catalog.retention_count()
    point = catalog.publish(db, workspace['id'], snapshot['version_id'],
        policy_version=policy_id(allowed), head_commit=Repository.open(workspace['root_locator']).head(),
        changed=True, scope=allowed)
    if not db.scalar(select(references.c.point_id).where(references.c.workspace_id == workspace['id'],
            references.c.owner_type == 'initial')):
        catalog.reference(db, workspace['id'], point['id'], 'initial', 'baseline', 'initial_baseline')
    catalog.reference(db, workspace['id'], point['id'], 'turn_' + phase, turn_id)
    if phase == 'before':
        catalog.reference(db, workspace['id'], point['id'], 'active_turn', turn_id, 'in_flight')
    else:
        db.execute(delete(references).where(references.c.workspace_id == workspace['id'],
            references.c.owner_type == 'active_turn', references.c.owner_id == turn_id))
        catalog.rotate(db, workspace['id'])
    return point
