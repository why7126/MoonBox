"""Common application operations used by Web and noninteractive authenticated callers."""
from sqlalchemy import select
from app.chat import service as chat_service
from app.governance.scope import authorize
from app.moonbox_worktree import WorktreeConflict
from app.chat.workspace import WorkspaceError
from . import workspaces as registry
from .schema import workspaces


def list_main(db, actor, space_id, repository_id):
    authorize(db, actor, space_id, repository_id)
    rows = db.execute(select(workspaces).where(workspaces.c.space_id == space_id,
        workspaces.c.repository_id == repository_id, workspaces.c.purpose == 'main')).mappings()
    return [registry.public(row) for row in rows]


def register_main(db, actor, space_id, repository_id):
    project = authorize(db, actor, space_id, repository_id, write=True)
    if project.source_root is None or project.source_root_unavailable:
        raise chat_service.ChatError(2602, '仓库主源码目录未配置或不可用', 503)
    try:
        row = registry.register_main(db, space_id, repository_id, project.source_root)
        db.commit()
    except (WorktreeConflict, WorkspaceError):
        db.rollback()
        raise chat_service.ChatError(2606, '主工作区不可登记，请检查仓库身份与目录状态', 409) from None
    return registry.public(row)


def scoped(db, actor, space_id, repository_id, workspace_id, *, write=False):
    """Every action rechecks space and current delivery ACL, including reads."""
    from app.governance.scope import visible
    from .schema import assignments, session_bindings
    from app.chat.schema import conversations
    project = authorize(db, actor, space_id, repository_id, write=write)
    row = registry.get(db, space_id, repository_id, workspace_id)
    assignment = db.execute(select(assignments).where(assignments.c.workspace_id == workspace_id)).mappings().first()
    if assignment and not visible(db, actor, project, assignment['change_id']):
        raise chat_service.ChatError(2601, '无权访问交付工作区', 403)
    if row['purpose'] == 'recovery':
        from app.moonbox_rollout.schema import points, references
        origin = db.execute(select(points).join(references, references.c.point_id == points.c.id).where(
            references.c.owner_type == 'recovery_tree', references.c.owner_id == workspace_id)).mappings().first()
        from app.moonbox_rollout.catalog import require_read
        if origin:
            require_read(db, actor, project, origin)
    if row['purpose'] == 'integration':
        from .integration_schema import candidates
        origin_change = db.scalar(select(candidates.c.change_id).where(candidates.c.integration_workspace_id == workspace_id))
        if origin_change and not visible(db, actor, project, origin_change):
            raise chat_service.ChatError(2601, '无权访问组合验收工作区', 403)
    if row['purpose'] == 'legacy' and not db.scalar(select(conversations.c.id).join(session_bindings,
        conversations.c.id == session_bindings.c.conversation_id).where(session_bindings.c.workspace_id == workspace_id,
        conversations.c.owner_id == actor, conversations.c.deleted_at.is_(None)).limit(1)):
        raise chat_service.ChatError(2601, '无权访问历史工作区', 403)
    return project, row, dict(assignment) if assignment else None


def list_workspaces(db, actor, space_id, repository_id):
    authorize(db, actor, space_id, repository_id)
    identifiers = list(db.scalars(select(workspaces.c.id).where(workspaces.c.space_id == space_id,
        workspaces.c.repository_id == repository_id).order_by(workspaces.c.created_at)))
    result = []
    from .schema import write_locks
    for identifier in identifiers:
        try:
            _, row, assignment = scoped(db, actor, space_id, repository_id, identifier)
        except chat_service.ChatError as error:
            if error.status == 403:
                continue
            raise
        lock = db.execute(select(write_locks).where(write_locks.c.workspace_id == identifier)).mappings().first()
        result.append(registry.public(row) | {'change_id': assignment['change_id'] if assignment else None,
            'delivery_root': assignment['delivery_root'] if assignment else None,
            'execution_state': 'occupied' if lock else 'idle',
            'integration_state': assignment['state'] if assignment else None})
    return result


def create_development(db, actor, space_id, repository_id, change_id):
    from pathlib import Path
    from sqlalchemy import insert, update
    from .authority import delivery
    from .schema import assignments
    from app.chat.settings import repository_binding
    project, context = delivery(db, actor, space_id, repository_id, change_id)
    from app.moonbox_exec_server.validation import provider
    if not provider().capability()['available']:
        raise chat_service.ChatError(2602, '独立组合验收能力尚未就绪，暂不开放新的开发工作区', 503,
            details={'reason': 'isolated_candidate_validation_unavailable'})
    if project.source_root is None or project.source_root_unavailable or project.root != project.source_root:
        raise chat_service.ChatError(2606, '主源码与正式治理目录需统一后才能创建开发工作区', 409)
    config = repository_binding(repository_id, space_id)
    if not config or not config.get('workspace_root'):
        raise chat_service.ChatError(2602, '独立工作区存储未配置', 503)
    main = registry.register_main(db, space_id, repository_id, project.source_root)
    row = registry.reserve_development(db, main, context['delivery_root'], Path(config['workspace_root']))
    # Serializes assignment changes independently from filesystem materialization.
    registry.get(db, space_id, repository_id, row['id'], current=True)
    assigned = db.execute(select(assignments).where(assignments.c.workspace_id == row['id'])).mappings().first()
    if assigned and assigned['change_id'] != change_id:
        if assigned['state'] != 'integrated':
            raise WorktreeConflict('delivery_change_in_progress')
        import hashlib
        assignment_operation = 'assign-' + hashlib.sha256((row['id'] + ':' + change_id).encode()).hexdigest()[:40]
        registry.acquire(db, row['id'], assignment_operation, row['revision'])
        registry.acquire(db, main['id'], assignment_operation, row['revision'])
        db.commit()
        from app.moonbox_worktree import Repository
        new_base = Repository.open(main['root_locator']).advance(row['root_locator'])
        db.execute(update(assignments).where(assignments.c.workspace_id == row['id']).values(change_id=change_id, state='developing'))
        db.execute(update(workspaces).where(workspaces.c.id == row['id']).values(base_commit=new_base, revision=row['revision'] + 1))
        registry.release(db, row['id'], assignment_operation, row['revision'])
        registry.release(db, main['id'], assignment_operation, row['revision'])
        row = {**row, 'base_commit': new_base, 'revision': row['revision'] + 1}
    elif not assigned:
        db.execute(insert(assignments).values(workspace_id=row['id'], change_id=change_id,
            delivery_root=context['delivery_root'], state='developing'))
    db.commit()
    row = registry.materialize(db, main, row)
    db.commit()
    return registry.public(row)


def new_session(db, actor, space_id, repository_id, workspace_id, request_id, predecessor_id=None):
    _, row, assignment = scoped(db, actor, space_id, repository_id, workspace_id, write=True)
    linkage = None
    if predecessor_id:
        parent = chat_service.conversation(db, actor, predecessor_id)
        if (parent['space_id'], parent['repository_id']) != (space_id, repository_id):
            raise WorktreeConflict('predecessor_scope_mismatch')
    if assignment:
        from .authority import delivery
        delivery(db, actor, space_id, repository_id, assignment['change_id'])
        if assignment['state'] != 'developing':
            raise WorktreeConflict('delivery_workspace_not_developing')
        linkage = dict(change_id=assignment['change_id'], delivery_root=assignment['delivery_root'], predecessor_id=predecessor_id)
    return chat_service.create_conversation(db, actor, space_id, repository_id, '工作区会话',
        client_request_id=request_id, execution_workspace_id=workspace_id, delivery_binding=linkage)
