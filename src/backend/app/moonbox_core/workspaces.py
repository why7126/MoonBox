"""Workspace persistence. Public services must authorize before entering this module."""
from datetime import datetime, timezone
from contextlib import contextmanager
from pathlib import Path
from uuid import uuid4

from sqlalchemy import insert, select, delete, update
from sqlalchemy.exc import IntegrityError
from app.moonbox_worktree import Repository, WorktreeConflict
from .schema import workspaces, main_bindings, claims, write_locks


@contextmanager
def atomic_savepoint(db):
    # sqlite3 legacy mode does not BEGIN for SELECT/SAVEPOINT. Without an explicit
    # outer transaction, releasing the first savepoint makes a later rollback ineffective.
    connection = db.connection()
    if connection.dialect.name == 'sqlite' and not connection.connection.driver_connection.in_transaction:
        connection.exec_driver_sql('BEGIN')
    with db.begin_nested():
        yield


def stamp():
    return datetime.now(timezone.utc).isoformat()


def _row(identifier, space, repository, git, purpose, locator, base):
    now = stamp()
    return dict(id=identifier, created_at=now, updated_at=now, space_id=space,
        repository_id=repository, git_identity=git, purpose=purpose,
        root_locator=str(locator), base_commit=base, lifecycle='ready', revision=1)


def register_main(db, space, repository, root):
    repo = Repository.open(root)
    existing = db.execute(select(main_bindings).where(
        main_bindings.c.git_identity == repo.identity)).mappings().first()
    if existing:
        if (existing['space_id'], existing['repository_id']) != (space, repository):
            raise WorktreeConflict('repository_already_bound')
        result = get(db, space, repository, existing['workspace_id'])
        if Path(result['root_locator']) != repo.root:
            raise WorktreeConflict('main_directory_mismatch')
        return result
    row = _row(str(uuid4()), space, repository, repo.identity, 'main', repo.root, repo.head())
    try:
        with atomic_savepoint(db):
            db.execute(insert(workspaces).values(**row))
            db.execute(insert(main_bindings).values(git_identity=repo.identity,
                space_id=space, repository_id=repository, workspace_id=row['id']))
    except IntegrityError:
        existing = db.execute(select(main_bindings).where(
            main_bindings.c.git_identity == repo.identity).with_for_update()).mappings().first()
        if existing and (existing['space_id'], existing['repository_id']) == (space, repository):
            winner = get(db, space, repository, existing['workspace_id'], current=True)
            if Path(winner['root_locator']) == repo.root:
                return winner
        raise WorktreeConflict('repository_already_bound') from None
    return row


def get(db, space, repository, identifier, *, current=False):
    query = select(workspaces).where(workspaces.c.id == identifier,
        workspaces.c.space_id == space, workspaces.c.repository_id == repository)
    row = db.execute(query.with_for_update() if current else query).mappings().first()
    if not row:
        raise WorktreeConflict('workspace_not_found')
    return dict(row)


def reserve_development(db, main, delivery_root, managed_root):
    """Commit this reservation before executing Git; concurrent requests share one claim."""
    existing = db.execute(select(claims.c.workspace_id).where(
        claims.c.space_id == main['space_id'], claims.c.repository_id == main['repository_id'],
        claims.c.delivery_root == delivery_root)).scalar_one_or_none()
    if existing:
        return get(db, main['space_id'], main['repository_id'], existing)
    identifier = str(uuid4())
    repo = Repository.open(main['root_locator'])
    if repo.identity != main['git_identity']:
        raise WorktreeConflict('repository_identity_mismatch')
    # A task baseline cannot silently discard uncommitted governance or source changes.
    repo.require_clean()
    row = _row(identifier, main['space_id'], main['repository_id'], main['git_identity'],
        'development', Path(managed_root) / identifier, repo.head())
    row['lifecycle'] = 'preparing'
    try:
        with atomic_savepoint(db):
            db.execute(insert(workspaces).values(**row))
            db.execute(insert(claims).values(space_id=main['space_id'],
                repository_id=main['repository_id'], delivery_root=delivery_root, workspace_id=identifier))
    except IntegrityError:
        winner = db.scalar(select(claims.c.workspace_id).where(
            claims.c.space_id == main['space_id'], claims.c.repository_id == main['repository_id'],
            claims.c.delivery_root == delivery_root).with_for_update())
        if winner:
            return get(db, main['space_id'], main['repository_id'], winner, current=True)
        raise WorktreeConflict('workspace_creation_race') from None
    return row


def materialize(db, main, row):
    """Idempotently reconcile a committed reservation; never overwrite unknown contents."""
    if row['lifecycle'] not in ('preparing', 'ready'):
        raise WorktreeConflict('workspace_unavailable')
    repo = Repository.open(main['root_locator'])
    if repo.identity != main['git_identity'] or row['git_identity'] != repo.identity:
        raise WorktreeConflict('repository_identity_mismatch')
    target = Path(row['root_locator'])
    if target.exists():
        child = repo.verify(target)
        if row['lifecycle'] == 'preparing' and child.head() != row['base_commit']:
            raise WorktreeConflict('workspace_baseline_changed')
    else:
        if row['lifecycle'] == 'ready':
            raise WorktreeConflict('workspace_missing')
        repo.create(target.parent, row['id'], row['base_commit'])
    changed = db.execute(update(workspaces).where(workspaces.c.id == row['id'],
        workspaces.c.revision == row['revision'], workspaces.c.lifecycle.in_(('preparing', 'ready')))
        .values(lifecycle='ready', updated_at=stamp())).rowcount
    if changed != 1:
        raise WorktreeConflict('workspace_revision_changed')
    return {**row, 'lifecycle': 'ready'}


def acquire(db, workspace_id, operation_id, generation):
    try:
        with atomic_savepoint(db):
            db.execute(insert(write_locks).values(workspace_id=workspace_id,
                operation_id=operation_id, generation=generation, created_at=stamp()))
    except IntegrityError:
        row = db.execute(select(write_locks).where(write_locks.c.workspace_id == workspace_id)).mappings().one()
        if (row['operation_id'], row['generation']) != (operation_id, generation):
            raise WorktreeConflict('workspace_busy') from None


def release(db, workspace_id, operation_id, generation):
    """Only the verified terminating owner may release; no time-based lock stealing."""
    return db.execute(delete(write_locks).where(write_locks.c.workspace_id == workspace_id,
        write_locks.c.operation_id == operation_id, write_locks.c.generation == generation)).rowcount


def public(row):
    return {key: row[key] for key in ('id', 'space_id', 'repository_id', 'purpose',
        'base_commit', 'lifecycle', 'revision')}
