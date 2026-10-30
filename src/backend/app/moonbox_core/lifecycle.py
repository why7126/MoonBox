"""Explicit cleanup preserves main, active operations and unmerged work."""
from sqlalchemy import select, update, delete
from app.moonbox_worktree import Repository, WorktreeConflict
from . import service, workspaces
from .schema import workspaces as table, main_bindings, claims, write_locks
from .integration_schema import candidates, operations


def remove(db, actor, space_id, repository_id, workspace_id, expected_revision):
    _, row, _ = service.scoped(db, actor, space_id, repository_id, workspace_id, write=True)
    if row['purpose'] == 'main':
        raise WorktreeConflict('main_workspace_protected')
    if row['purpose'] == 'legacy':
        raise WorktreeConflict('legacy_workspace_requires_manual_retention')
    if row['revision'] != expected_revision:
        raise WorktreeConflict('workspace_revision_changed')
    if row['lifecycle'] == 'removed':
        return workspaces.public(row)
    from app.moonbox_rollout.schema import references
    active_pin = db.scalar(select(references.c.point_id).where(references.c.workspace_id == workspace_id,
        references.c.protection_reason.is_not(None), references.c.owner_type.in_(
            ('manual', 'active_turn', 'restore_before', 'restore_after', 'merge_candidate'))).limit(1))
    if active_pin:
        raise WorktreeConflict('workspace_has_protected_references')
    if db.scalar(select(candidates.c.id).where(candidates.c.workspace_id == workspace_id,
        candidates.c.state.not_in(('integrated', 'invalidated'))).limit(1)):
        raise WorktreeConflict('workspace_has_merge_candidate')
    identifier = 'remove-' + workspace_id
    workspaces.acquire(db, workspace_id, identifier, expected_revision)
    main_id = db.scalar(select(main_bindings.c.workspace_id).where(main_bindings.c.space_id == space_id,
        main_bindings.c.repository_id == repository_id))
    main = workspaces.get(db, space_id, repository_id, main_id)
    repo = Repository.open(main['root_locator'])
    if repo.identity != row['git_identity']:
        raise WorktreeConflict('repository_identity_mismatch')
    db.execute(update(table).where(table.c.id == workspace_id).values(lifecycle='removing', updated_at=workspaces.stamp()))
    db.commit()
    from pathlib import Path
    target = Path(row['root_locator'])
    if target.exists() or target.is_symlink():
        repo.remove(target, integrated_into=repo.head())
    else:
        # A missing path alone does not prove a prior Git removal; verify registration.
        from app.moonbox_worktree.git import _run
        if (b'worktree ' + str(target).encode()) in _run(repo.root, 'worktree', 'list', '--porcelain', '-z').split(b'\0'):
            raise WorktreeConflict('workspace_removal_unknown')
    db.execute(delete(claims).where(claims.c.workspace_id == workspace_id))
    db.execute(update(table).where(table.c.id == workspace_id).values(lifecycle='removed', updated_at=workspaces.stamp()))
    workspaces.release(db, workspace_id, identifier, expected_revision)
    db.commit()
    return workspaces.public(row | {'lifecycle': 'removed'})
