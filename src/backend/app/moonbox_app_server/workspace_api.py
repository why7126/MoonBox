"""Authenticated workspace API. Physical directory locators never cross this boundary."""
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.api.v1.admin_auth import require_session_user
from app.chat.api import ChatRoute
from app.db.session import get_db
from app.schemas.common import ApiResponse
from app.moonbox_core import service

router = APIRouter(prefix='/api/v1/chat/workspaces', tags=['Workspaces'], route_class=ChatRoute)


class WorkspaceView(BaseModel):
    id: str
    space_id: str
    repository_id: str
    purpose: str
    base_commit: str
    lifecycle: str
    revision: int
    change_id: str | None = None
    delivery_root: str | None = None
    execution_state: str = 'idle'
    integration_state: str | None = None


class WorkspaceList(BaseModel):
    items: list[WorkspaceView]
    can_create_development: bool = False
    reason_code: str = 'delivery_protection_not_ready'
    can_register_main: bool = False


class MainRequest(BaseModel):
    space_id: str = Field(min_length=1, max_length=64)
    repository_id: str = Field(min_length=1, max_length=64)


@router.get('', response_model=ApiResponse[WorkspaceList], summary='查询仓库工作区')
def list_workspaces(space_id: str, repository_id: str, request: Request,
                    user=Depends(require_session_user), db: Session = Depends(get_db)):
    actor = str(user['id']); request.state.chat_actor = actor
    from app.moonbox_exec_server.validation import provider
    capability = provider().capability()
    from app.governance.scope import authorize
    from app.chat.service import ChatError
    writable = True
    try:
        authorize(db, actor, space_id, repository_id, write=True)
    except ChatError:
        writable = False
    return ApiResponse(data=WorkspaceList(items=service.list_workspaces(db, actor, space_id, repository_id),
        can_register_main=writable, can_create_development=writable and capability['available'],
        reason_code=capability.get('reason_code') or ('ready' if writable else 'sprint_operation_forbidden')))


@router.post('/main', response_model=ApiResponse[WorkspaceView], summary='登记仓库主工作区')
def register_main(payload: MainRequest, request: Request,
                  user=Depends(require_session_user), db: Session = Depends(get_db)):
    actor = str(user['id']); request.state.chat_actor = actor
    return ApiResponse(data=service.register_main(db, actor, payload.space_id, payload.repository_id))


class WorkspaceScope(MainRequest):
    workspace_id: str = Field(min_length=1, max_length=64)


class DevelopmentRequest(MainRequest):
    change_id: str = Field(min_length=1, max_length=128, pattern=r'^[a-z0-9]+(?:-[a-z0-9]+)*$')


class SessionRequest(WorkspaceScope):
    request_id: str = Field(min_length=1, max_length=64)
    predecessor_id: str | None = Field(default=None, max_length=64)


class RecoverySelection(WorkspaceScope):
    before_id: str = Field(min_length=1, max_length=64)
    after_id: str = Field(min_length=1, max_length=64)
    paths: list[str] = Field(min_length=1, max_length=256)


class RestoreRequest(RecoverySelection):
    conversation_id: str = Field(min_length=1, max_length=64)
    fingerprint: str = Field(pattern=r'^[0-9a-f]{64}$')
    request_id: str = Field(min_length=1, max_length=64)


class ProtectionRequest(WorkspaceScope):
    point_id: str = Field(min_length=1, max_length=64)
    protected: bool


def _invoke(db, request, actor, call):
    from app.moonbox_worktree import WorktreeConflict
    from app.chat.service import ChatError
    from app.chat.workspace import WorkspaceError
    request.state.chat_actor = actor
    from app.moonbox_core.observability import request_context
    token = request_context.set(getattr(request.state, 'chat_request_id', None))
    try:
        return ApiResponse(data=call())
    except (WorktreeConflict, WorkspaceError, ValueError):
        db.rollback()
        raise ChatError(2606, '操作条件已变化或存在冲突，请刷新后查看工作区状态', 409) from None
    finally:
        request_context.reset(token)


@router.post('/development', response_model=ApiResponse[WorkspaceView], summary='按交付链路创建或复用独立开发工作区')
def create_development(payload: DevelopmentRequest, request: Request,
                       user=Depends(require_session_user), db: Session = Depends(get_db)):
    actor = str(user['id'])
    return _invoke(db, request, actor, lambda: service.create_development(db, actor, **payload.model_dump()))


@router.post('/sessions', response_model=ApiResponse[dict], summary='创建固定绑定工作区的新会话')
def create_workspace_session(payload: SessionRequest, request: Request,
                             user=Depends(require_session_user), db: Session = Depends(get_db)):
    actor = str(user['id'])
    return _invoke(db, request, actor, lambda: service.new_session(db, actor, **payload.model_dump()))


@router.get('/recovery-points', response_model=ApiResponse[dict], summary='查询工作区恢复点与保护原因')
def recovery_points(space_id: str, repository_id: str, workspace_id: str, request: Request,
                    before_sequence: int | None = None, user=Depends(require_session_user), db: Session = Depends(get_db)):
    actor = str(user['id']); request.state.chat_actor = actor
    project, _, _ = service.scoped(db, actor, space_id, repository_id, workspace_id)
    from sqlalchemy import select
    from app.moonbox_rollout.schema import points, references
    query = select(points).where(points.c.workspace_id == workspace_id)
    if before_sequence is not None:
        query = query.where(points.c.sequence < before_sequence)
    batch = list(db.execute(query.order_by(points.c.sequence.desc()).limit(51)).mappings())
    items = []
    from app.moonbox_rollout import catalog
    for row in batch[:50]:
        if not catalog.can_read(db, actor, project, row):
            continue
        pins = list(db.scalars(select(references.c.protection_reason).where(references.c.point_id == row['id'],
            references.c.protection_reason.is_not(None))))
        items.append({k: row[k] for k in ('id', 'sequence', 'manifest_hash', 'head_commit', 'state', 'created_at')} |
            {'protection_reasons': sorted(set(pins)), 'policy_version': row['policy_version']})
    return ApiResponse(data={'items': items, 'next_sequence': batch[49]['sequence'] if len(batch) > 50 else None})


@router.get('/recovery-files', response_model=ApiResponse[dict], summary='分页查询恢复点文件覆盖范围')
def recovery_files(space_id: str, repository_id: str, workspace_id: str, point_id: str, request: Request,
                   after: str = '', user=Depends(require_session_user), db: Session = Depends(get_db)):
    actor = str(user['id']); request.state.chat_actor = actor
    project, _, _ = service.scoped(db, actor, space_id, repository_id, workspace_id)
    from sqlalchemy import select
    from app.moonbox_rollout.schema import entries
    from app.moonbox_rollout.restore import _point
    def query():
        from app.moonbox_rollout import catalog
        catalog.require_read(db, actor, project, _point(db, workspace_id, point_id))
        batch = list(db.execute(select(entries).where(entries.c.point_id == point_id,
            entries.c.path_key > after).order_by(entries.c.path_key).limit(101)).mappings())
        return {'items': [{k: row[k] for k in ('path', 'kind', 'mode', 'digest', 'byte_count')} |
            {'restorable': row['kind'] == 'file' and row['object_id'] is not None} for row in batch[:100]],
            'next_cursor': batch[99]['path_key'] if len(batch) > 100 else None}
    return _invoke(db, request, actor, query)


@router.post('/recovery-preflight', response_model=ApiResponse[dict], summary='核对恢复前后与当前文件的三方差异')
def recovery_preflight(payload: RecoverySelection, request: Request,
                       user=Depends(require_session_user), db: Session = Depends(get_db)):
    from app.moonbox_rollout.restore import preview
    actor = str(user['id'])
    return _invoke(db, request, actor, lambda: preview(db, actor, payload.space_id, payload.repository_id,
        payload.workspace_id, payload.before_id, payload.after_id, payload.paths)[0])


@router.post('/restore', response_model=ApiResponse[dict], summary='持久记录并执行选定文件的安全恢复')
def restore_files(payload: RestoreRequest, request: Request,
                  user=Depends(require_session_user), db: Session = Depends(get_db)):
    from sqlalchemy.orm import sessionmaker
    from app.moonbox_rollout import restore
    actor = str(user['id'])
    def execute():
        operation = restore.start(db, actor, payload.space_id, payload.repository_id, payload.workspace_id,
            payload.conversation_id, payload.before_id, payload.after_id, payload.paths, payload.fingerprint, payload.request_id)
        return restore.run(sessionmaker(bind=db.get_bind()), actor, payload.space_id, payload.repository_id, operation['id'])
    return _invoke(db, request, actor, execute)


@router.post('/restore/{operation_id}/resume', response_model=ApiResponse[dict], summary='重新检查权限并续接未完成的恢复操作')
def resume_restore(operation_id: str, payload: MainRequest, request: Request,
                   user=Depends(require_session_user), db: Session = Depends(get_db)):
    from sqlalchemy.orm import sessionmaker
    from app.moonbox_rollout.restore import run
    actor = str(user['id'])
    return _invoke(db, request, actor, lambda: run(sessionmaker(bind=db.get_bind()), actor,
        payload.space_id, payload.repository_id, operation_id))


@router.post('/recovery-protection', response_model=ApiResponse[dict], summary='保护或解除自己手动保护的恢复点')
def protect_recovery(payload: ProtectionRequest, request: Request,
                     user=Depends(require_session_user), db: Session = Depends(get_db)):
    from app.moonbox_rollout import catalog
    actor = str(user['id'])
    def execute():
        project, _, _ = service.scoped(db, actor, payload.space_id, payload.repository_id, payload.workspace_id, write=True)
        from app.moonbox_rollout.restore import _point
        catalog.require_read(db, actor, project, _point(db, payload.workspace_id, payload.point_id))
        owner = actor + ':' + payload.point_id
        if payload.protected:
            catalog.reference(db, payload.workspace_id, payload.point_id, 'manual', owner, 'manual')
        else:
            catalog.unprotect_manual(db, payload.workspace_id, payload.point_id, owner)
        db.commit()
        return {'point_id': payload.point_id, 'protected': payload.protected}
    return _invoke(db, request, actor, execute)


class CandidateRequest(WorkspaceScope):
    request_id: str = Field(min_length=1, max_length=64)


class ConfirmationRequest(MainRequest):
    fingerprint: str = Field(pattern=r'^[0-9a-f]{64}$')
    request_id: str = Field(min_length=1, max_length=64)


@router.get('/merge-capability', response_model=ApiResponse[dict], summary='查询当前迭代操作权限与组合验证能力')
def merge_capability(space_id: str, repository_id: str, workspace_id: str, request: Request,
                     user=Depends(require_session_user), db: Session = Depends(get_db)):
    from app.moonbox_core.authority import delivery
    from app.moonbox_exec_server.validation import provider
    from app.chat.service import ChatError
    actor = str(user['id']); request.state.chat_actor = actor
    _, _, assignment = service.scoped(db, actor, space_id, repository_id, workspace_id)
    capability = provider().capability()
    allowed = False
    reason = 'delivery_workspace_required'
    if assignment:
        try:
            delivery(db, actor, space_id, repository_id, assignment['change_id'])
            allowed, reason = True, None
        except ChatError:
            reason = 'sprint_operation_forbidden'
    return ApiResponse(data={'can_operate_sprint': allowed, 'validation_available': capability['available'],
        'can_prepare': allowed, 'can_confirm': allowed and capability['available'],
        'reason_code': reason or capability.get('reason_code')})


@router.post('/merge-candidates', response_model=ApiResponse[dict], summary='创建固定源和目标版本的合入候选并申请组合验证')
def prepare_merge(payload: CandidateRequest, request: Request,
                  user=Depends(require_session_user), db: Session = Depends(get_db)):
    from sqlalchemy.orm import sessionmaker
    from app.moonbox_core import integration
    actor = str(user['id'])
    def execute():
        row = integration.prepare(db, actor, **payload.model_dump())
        return integration.validate(sessionmaker(bind=db.get_bind()), actor, payload.space_id, payload.repository_id, row['id'])
    return _invoke(db, request, actor, execute)


@router.get('/merge-candidates', response_model=ApiResponse[dict], summary='查询工作区合入候选')
def list_merge_candidates(space_id: str, repository_id: str, workspace_id: str, request: Request,
                          user=Depends(require_session_user), db: Session = Depends(get_db)):
    from sqlalchemy import select
    from app.moonbox_core.integration_schema import candidates
    from app.moonbox_core.integration import public
    actor = str(user['id']); request.state.chat_actor = actor
    project, _, _ = service.scoped(db, actor, space_id, repository_id, workspace_id)
    from app.governance.scope import visible
    return ApiResponse(data={'items': [public(row) for row in db.execute(select(candidates).where(
        candidates.c.workspace_id == workspace_id).order_by(candidates.c.created_at.desc()).limit(50)).mappings() if visible(db, actor, project, row['change_id'])]})


@router.post('/merge-candidates/{candidate_id}/validate', response_model=ApiResponse[dict], summary='续接固定组合版本的验证')
def validate_merge(candidate_id: str, payload: MainRequest, request: Request,
                   user=Depends(require_session_user), db: Session = Depends(get_db)):
    from sqlalchemy.orm import sessionmaker
    from app.moonbox_core.integration import validate
    actor = str(user['id'])
    return _invoke(db, request, actor, lambda: validate(sessionmaker(bind=db.get_bind()), actor,
        payload.space_id, payload.repository_id, candidate_id))


@router.post('/merge-candidates/{candidate_id}/confirm', response_model=ApiResponse[dict], summary='由当前具备迭代操作权限的人确认并合入已验证候选')
def confirm_merge(candidate_id: str, payload: ConfirmationRequest, request: Request,
                  user=Depends(require_session_user), db: Session = Depends(get_db)):
    from sqlalchemy.orm import sessionmaker
    from app.moonbox_core import integration
    actor = str(user['id'])
    def execute():
        operation = integration.confirm(db, actor, payload.space_id, payload.repository_id, candidate_id,
            payload.fingerprint, payload.request_id)
        return integration.integrate(sessionmaker(bind=db.get_bind()), actor,
            payload.space_id, payload.repository_id, operation['id'])
    return _invoke(db, request, actor, execute)


@router.post('/merge-candidates/{candidate_id}/repair', response_model=ApiResponse[dict], summary='作废未确认候选并保留开发工作区继续返修')
def repair_merge(candidate_id: str, payload: MainRequest, request: Request,
                 user=Depends(require_session_user), db: Session = Depends(get_db)):
    from app.moonbox_core.integration import invalidate
    actor = str(user['id'])
    return _invoke(db, request, actor, lambda: invalidate(db, actor, payload.space_id, payload.repository_id, candidate_id))


@router.post('/merge-operations/{operation_id}/resume', response_model=ApiResponse[dict], summary='重新核验并续接合入操作')
def resume_merge(operation_id: str, payload: MainRequest, request: Request,
                 user=Depends(require_session_user), db: Session = Depends(get_db)):
    from sqlalchemy.orm import sessionmaker
    from app.moonbox_core.integration import integrate
    actor = str(user['id'])
    return _invoke(db, request, actor, lambda: integrate(sessionmaker(bind=db.get_bind()), actor,
        payload.space_id, payload.repository_id, operation_id))


class CleanupRequest(WorkspaceScope):
    expected_revision: int = Field(ge=1)


@router.post('/cleanup', response_model=ApiResponse[WorkspaceView], summary='检查未合入成果和保护引用后清理独立目录')
def cleanup_workspace(payload: CleanupRequest, request: Request,
                      user=Depends(require_session_user), db: Session = Depends(get_db)):
    from app.moonbox_core.lifecycle import remove
    actor = str(user['id'])
    return _invoke(db, request, actor, lambda: remove(db, actor, **payload.model_dump()))


@router.get('/operations', response_model=ApiResponse[dict], summary='查询工作区恢复与合入操作的持久状态')
def workspace_operations(space_id: str, repository_id: str, workspace_id: str, request: Request,
                         user=Depends(require_session_user), db: Session = Depends(get_db)):
    from sqlalchemy import select
    from app.moonbox_rollout.schema import operations as restores
    from app.moonbox_rollout.restore import public as restore_public
    from app.moonbox_core.integration_schema import operations as merges, candidates
    from app.moonbox_core.integration import operation_public
    actor = str(user['id']); request.state.chat_actor = actor
    service.scoped(db, actor, space_id, repository_id, workspace_id)
    restore_rows = db.execute(select(restores).where(restores.c.workspace_id == workspace_id,
        restores.c.actor_id == actor).order_by(restores.c.created_at.desc()).limit(50)).mappings()
    merge_rows = db.execute(select(merges).join(candidates, candidates.c.id == merges.c.candidate_id).where(
        candidates.c.workspace_id == workspace_id, merges.c.actor_id == actor).order_by(merges.c.created_at.desc()).limit(50)).mappings()
    return ApiResponse(data={'restores': [restore_public(row) for row in restore_rows],
        'merges': [operation_public(row) for row in merge_rows]})


class RecoveryTreeRequest(WorkspaceScope):
    point_id: str = Field(min_length=1, max_length=64)
    request_id: str = Field(min_length=1, max_length=64)


@router.post('/recovery-directory', response_model=ApiResponse[dict], summary='将恢复点提取到独立恢复目录并保留当前工作区')
def create_recovery_directory(payload: RecoveryTreeRequest, request: Request,
                              user=Depends(require_session_user), db: Session = Depends(get_db)):
    from app.moonbox_rollout.recovery_tree import create
    actor = str(user['id'])
    return _invoke(db, request, actor, lambda: create(db, actor, **payload.model_dump()))


@router.get('/merge-candidates/{candidate_id}/files', response_model=ApiResponse[dict], summary='分页查看固定候选相对主线的文件差异')
def merge_files(candidate_id: str, space_id: str, repository_id: str, request: Request,
                offset: int = 0, user=Depends(require_session_user), db: Session = Depends(get_db)):
    from app.moonbox_core.integration import get
    from app.moonbox_core.workspaces import get as workspace
    from app.moonbox_worktree.git import _run
    from pathlib import Path
    actor = str(user['id'])
    def read():
        if offset < 0:
            raise ValueError('invalid_page')
        candidate = get(db, actor, space_id, repository_id, candidate_id)
        if not candidate['candidate_commit']:
            return {'items': [], 'next_offset': None}
        main = workspace(db, space_id, repository_id, candidate['main_workspace_id'])
        records = _run(Path(main['root_locator']), 'diff', '--numstat', '--no-renames', '-z',
            candidate['target_commit'], candidate['candidate_commit']).decode().split('\0')
        rows = []
        for value in filter(None, records):
            added, removed, path = value.split('\t', 2)
            rows.append({'path': path, 'added': int(added) if added != '-' else None,
                'removed': int(removed) if removed != '-' else None})
        return {'items': rows[offset:offset+100], 'next_offset': offset+100 if len(rows)>offset+100 else None}
    return _invoke(db, request, actor, read)
