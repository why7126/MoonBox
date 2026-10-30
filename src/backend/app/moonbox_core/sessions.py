"""Immutable execution binding; historical sessions are never silently relocated."""
from pathlib import Path
from sqlalchemy import insert, select, update
from sqlalchemy.exc import IntegrityError
from app.chat.schema import conversations, turns
from app.moonbox_worktree import Repository, WorktreeConflict
from .schema import session_bindings
from .workspaces import get


def bound(db, conversation_id):
    return db.scalar(select(session_bindings.c.workspace_id).where(
        session_bindings.c.conversation_id == conversation_id))


def bind(db, parent, workspace_id):
    """Caller authenticates ownership and delivery ACL; lock parent against concurrent send."""
    won = db.execute(update(conversations).where(conversations.c.id == parent['id'],
        conversations.c.active_turn_id.is_(None), conversations.c.deleted_at.is_(None),
        conversations.c.archived == 0).values(updated_at=conversations.c.updated_at)).rowcount
    if won != 1:
        raise WorktreeConflict('session_busy_or_unavailable')
    parent = dict(db.execute(select(conversations).where(
        conversations.c.id == parent['id'])).mappings().one())
    previous = bound(db, parent['id'])
    if previous:
        if previous != workspace_id:
            raise WorktreeConflict('session_workspace_immutable')
        return get(db, parent['space_id'], parent['repository_id'], previous)
    if parent.get('workspace_id') or parent.get('thread_id') or db.scalar(
            select(turns.c.id).where(turns.c.conversation_id == parent['id']).limit(1)):
        raise WorktreeConflict('legacy_session_requires_explicit_migration')
    row = get(db, parent['space_id'], parent['repository_id'], workspace_id)
    if row['lifecycle'] != 'ready' or row['purpose'] not in ('main', 'development'):
        raise WorktreeConflict('workspace_unavailable')
    try:
        from .workspaces import atomic_savepoint
        with atomic_savepoint(db):
            db.execute(insert(session_bindings).values(conversation_id=parent['id'], workspace_id=workspace_id))
    except IntegrityError:
        raise WorktreeConflict('session_binding_race') from None
    return row


def execution_workspace(db, parent):
    identifier = bound(db, parent['id'])
    if not identifier:
        return None
    row = get(db, parent['space_id'], parent['repository_id'], identifier)
    if row['lifecycle'] != 'ready':
        raise WorktreeConflict('workspace_unavailable')
    repo = Repository.open(row['root_locator'])
    if repo.identity != row['git_identity']:
        raise WorktreeConflict('repository_identity_mismatch')
    return row, Path(row['root_locator'])
