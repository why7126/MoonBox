"""Reentrant additive session migration. Legacy copies never become the main directory."""
import hashlib
import json
from pathlib import Path
from uuid import uuid5, NAMESPACE_URL
from sqlalchemy import insert, select, update
from app.chat.schema import conversations, turns, workspace_baselines
from app.chat.settings import repository_binding
from app.moonbox_worktree import Repository, WorktreeConflict
from .schema import session_bindings, workspaces, migrations
from .workspaces import register_main, _row, stamp
from .sessions import bound


def ensure_binding(db, parent):
    existing = bound(db, parent['id'])
    if existing:
        return existing
    config = repository_binding(parent['repository_id'], parent['space_id'])
    if not config or not config.get('source_root'):
        return None  # Unconfigured legacy/test deployments retain their explicit old adapter.
    locked = db.execute(select(conversations).where(conversations.c.id == parent['id']).with_for_update()).mappings().one()
    existing = bound(db, parent['id'])
    if existing:
        return existing
    if db.scalar(select(turns.c.id).where(turns.c.conversation_id == parent['id'],
            turns.c.status.in_(('connecting', 'running', 'stopping', 'unknown'))).limit(1)):
        raise WorktreeConflict('active_session_migration_forbidden')
    main = register_main(db, parent['space_id'], parent['repository_id'], config['source_root'])
    previous = locked['workspace_id']
    has_history = db.scalar(select(turns.c.id).where(turns.c.conversation_id == parent['id'],
        turns.c.status != 'queued').limit(1)) is not None
    row = main
    if previous not in (None, 'source') or (has_history and previous is None and config.get('workspace_mode') == 'copy'):
        if previous not in (None, parent['id']):
            raise WorktreeConflict('legacy_workspace_identity_unknown')
        if not config.get('workspace_root'):
            raise WorktreeConflict('legacy_workspace_missing')
        root = Path(config['workspace_root']) / parent['id']
        repo = Repository.open(root)
        identifier = str(uuid5(NAMESPACE_URL, 'moonbox.legacy:' + repo.identity + ':' + parent['id']))
        row = _row(identifier, parent['space_id'], parent['repository_id'], repo.identity,
                   'legacy', root, repo.head())
        if not db.scalar(select(workspaces.c.id).where(workspaces.c.id == identifier)):
            db.execute(insert(workspaces).values(**row))
    baseline = db.execute(select(workspace_baselines).where(
        workspace_baselines.c.conversation_id == parent['id'])).mappings().first()
    evidence = hashlib.sha256(json.dumps(dict(baseline) if baseline else {}, sort_keys=True).encode()).hexdigest()
    db.execute(insert(session_bindings).values(conversation_id=parent['id'], workspace_id=row['id']))
    db.execute(insert(migrations).values(conversation_id=parent['id'], schema_version=1,
        previous_workspace_id=previous, workspace_id=row['id'], baseline_digest=evidence, created_at=stamp()))
    from app.moonbox_rollout.migration import adopt
    adopt(db, row, parent['id'])
    # Historical workspace_id stays intact until execution validates the persisted binding.
    return row['id']
