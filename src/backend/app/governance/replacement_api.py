"""Human review endpoints; approvals do not enqueue or execute archive commands."""
import json
from datetime import datetime, timezone
from typing import Literal
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import insert, select, text, update
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from app.api.v1.admin_auth import require_session_user
from app.chat.api import ChatRoute
from app.chat.service import ChatError, identity
from app.db.session import get_db
from app.schemas.common import ApiResponse
from . import scope, replacement_trust, replacement_signer
from .replacement_proof import Proposal, canonical, digest
from .replacement_schema import proposals, activations
from .replacement_authorization import require_owner, decide
from .replacement_inputs import validate
from .reader import ProjectReader
from .replacement_observability import ReplacementRoute, trace

router = APIRouter(prefix='/api/v1/chat/replacement-proposals', tags=['Governance'], route_class=ReplacementRoute)


def object_access(db, user, project, change, *, write=False):
    reader = ProjectReader(db, user['id'], project)
    reader.authorize_object(reader.snapshot(), change, change=True, root=project.root, write=write)


class Prepare(BaseModel):
    model_config = ConfigDict(extra='forbid')
    space_id: str = Field(min_length=1, max_length=64)
    repository_id: str = Field(min_length=1, max_length=64)
    proposal: Proposal


class Decision(BaseModel):
    model_config = ConfigDict(extra='forbid')
    expected_revision: int = Field(ge=1, strict=True)
    proposal_digest: str = Field(pattern=r'^[a-f0-9]{64}$')
    idempotency_key: str = Field(pattern=r'^[A-Za-z0-9_-]{1,64}$')
    confirmed: bool = Field(strict=True)
    reason: str = Field(default='', max_length=500)


class ReplacementReviewResponse(BaseModel):
    id: str
    revision: int
    digest: str
    state: str
    proposal: Proposal
    expires_at: str | None
    can_approve: bool
    can_reject: bool
    can_revoke: bool
    trust_status: str
    policy_state: str
    independent_signoff: str


class ReplacementListResponse(BaseModel):
    items: list[ReplacementReviewResponse]


class ReplacementDecisionResponse(BaseModel):
    id: str
    revision: int
    replayed: bool


class ReplacementAdmissionResponse(BaseModel):
    decision: Literal['ready', 'blocked', 'resume']
    reason_code: str
    blockers: list[str]
    proposal_revision: int
    proposal_digest: str
    policy_version: str | None
    input_fingerprint: str | None
    operation_id: str | None


@router.get('/{proposal_id}/admission', response_model=ApiResponse[ReplacementAdmissionResponse], summary='只读核验受控归档的当前权威准入')
def admission(proposal_id: str, request: Request, user=Depends(require_session_user), db: Session=Depends(get_db)):
    request.state.chat_actor = user['id']
    row = db.execute(select(proposals).where(proposals.c.id == proposal_id)).mappings().first()
    if not row:
        raise ChatError(2601, '提案不存在或无权访问', 404)
    project = scope.authorize(db, user['id'], row['space_id'], row['repository_id'])
    object_access(db, user, project, row['change_id'])
    from .replacement_admission import admit
    return ApiResponse(data=admit(db, project, user['id'], row))


def public(db, row, project, user):
    owner = db.scalar(text('SELECT owner_id FROM admin_spaces WHERE id=:space'), {'space': project.space_id})
    try:
        trust = replacement_trust.load(project.root)
        trusted = True
    except ValueError:
        trusted = False
    activation = db.execute(select(activations).where(activations.c.scope_key == project.key)).mappings().first()
    can_decide = owner == user['id'] and not project.readonly and trusted
    active = bool(trusted and activation and activation['state'] == 'active'
        and activation['policy_version'] == trust.policy_version
        and activation['binding_revision'] == project.binding_revision)
    return {'id': row['id'], 'revision': row['revision'], 'digest': row['digest'],
            'state': row['state'], 'proposal': json.loads(row['body']), 'expires_at': row['expires_at'],
            'can_approve': can_decide and active and row['state'] == 'prepared',
            'can_reject': can_decide and row['state'] == 'prepared',
            'can_revoke': can_decide and row['state'] == 'approved',
            'trust_status': 'trusted' if trusted else 'policy_not_trusted',
            'policy_state': activation['state'] if activation else 'not_enabled',
            'independent_signoff': 'required_at_archive'}


@router.get('', response_model=ApiResponse[ReplacementListResponse], summary='读取当前项目规则替代审阅列表')
def listing(space_id: str, repository_id: str, request: Request, user=Depends(require_session_user), db: Session=Depends(get_db)):
    request.state.chat_actor = user['id']
    project = scope.authorize(db, user['id'], space_id, repository_id)
    rows = db.execute(select(proposals).where(proposals.c.scope_key == project.key).order_by(proposals.c.created_at.desc()).limit(100)).mappings()
    visible = []
    for row in list(rows):
        try:
            object_access(db, user, project, row['change_id'])
        except ChatError as error:
            if error.status == 403: continue
            raise
        visible.append(public(db, row, project, user))
    return ApiResponse(data={'items': visible})


@router.post('', response_model=ApiResponse[ReplacementReviewResponse], summary='准备绑定精确差异的规则替代提案')
def prepare(payload: Prepare, request: Request, user=Depends(require_session_user), db: Session=Depends(get_db)):
    raise ChatError(2606, '旧版规则替代准备入口已停止，请从对象归档阻断项查看当前修改', 409,
                    kind='legacy_replacement_retired')
    request.state.chat_actor = user['id']
    project = scope.authorize(db, user['id'], payload.space_id, payload.repository_id, write=True)
    object_access(db, user, project, payload.proposal.successor, write=True)
    try:
        trust = replacement_trust.load(project.root)
        validate(project, payload.proposal, trust)
    except (ValueError, OSError, KeyError, TypeError, SQLAlchemyError):
        raise ChatError(2606, '可信策略、差异映射或证据未通过核验，请检查部署与当前提案', 409, kind='replacement_not_ready') from None
    body = payload.proposal.model_dump()
    fingerprint = digest(body)
    row = db.execute(select(proposals).where(proposals.c.scope_key == project.key, proposals.c.digest == fingerprint)).mappings().first()
    if not row:
        row = {**identity(), 'scope_key': project.key, 'space_id': project.space_id, 'repository_id': project.repository_id,
               'binding_revision': project.binding_revision, 'change_id': payload.proposal.successor,
               'digest': fingerprint, 'body': canonical(body).decode(), 'prepared_by': user['id'], 'revision': 1,
               'state': 'prepared', 'expires_at': None}
        try:
            db.execute(insert(proposals).values(**row))
            trace(db,row['id'],'prepared',actor=user['id'],request_id=request.state.chat_request_id)
            db.commit()
        except IntegrityError:
            db.rollback()
            row = db.execute(select(proposals).where(proposals.c.scope_key == project.key,
                proposals.c.digest == fingerprint)).mappings().first()
            if row is None:
                raise ChatError(2606, '提案准备发生并发变化，请重新读取', 409) from None
    elif row['state'] in {'rejected', 'revoked'} or (row['state'] == 'approved' and row['expires_at'] and datetime.fromisoformat(row['expires_at']) <= datetime.now(timezone.utc)):
        # A new preparation is a new revision; old signed events remain intact.
        won = db.execute(update(proposals).where(proposals.c.id == row['id'], proposals.c.revision == row['revision']).values(
            state='prepared', revision=row['revision']+1, owner_id=None, expires_at=None, receipt=None)).rowcount
        if won != 1:
            raise ChatError(2606, '提案状态已变化，请重新读取', 409)
        db.commit()
        row = db.execute(select(proposals).where(proposals.c.id == row['id'])).mappings().one()
    return ApiResponse(data=public(db, row, project, user))


@router.post('/{proposal_id}/{action}', response_model=ApiResponse[ReplacementDecisionResponse], summary='独立确认批准、拒绝或撤销规则替代提案')
def decision(proposal_id: str, action: Literal['approve', 'reject', 'revoke'], payload: Decision, request: Request,
             user=Depends(require_session_user), db: Session=Depends(get_db)):
    raise ChatError(2606, '旧版规则替代审批入口已停止；历史决定仍可只读查看', 409,
                    kind='legacy_replacement_retired')
    request.state.chat_actor = user['id']
    row = db.execute(select(proposals).where(proposals.c.id == proposal_id)).mappings().first()
    if not row:
        raise ChatError(2601, '提案不存在或无权访问', 404)
    project = scope.authorize(db, user['id'], row['space_id'], row['repository_id'], write=True)
    object_access(db, user, project, row['change_id'], write=True)
    require_owner(db, user, project)
    if not payload.confirmed:
        raise ChatError(2606, '请独立确认当前精确版本', 409)
    try:
        trust = replacement_trust.load(project.root)
        if action == 'approve':
            validate(project, Proposal.model_validate(json.loads(row['body'])), trust)
        result = decide(db, project=project, proposal_id=proposal_id, actor_id=user['id'], action=action,
            expected_revision=payload.expected_revision, proposal_digest=payload.proposal_digest,
            request_key=payload.idempotency_key, reason=payload.reason, sign=replacement_signer.sign, trust=trust)
        if not result['replayed']:
            trace(db,proposal_id,{'approve':'approved','reject':'rejected','revoke':'revoked'}[action],actor=user['id'],request_id=request.state.chat_request_id)
        db.commit()
    except (ValueError, OSError, KeyError, TypeError, SQLAlchemyError):
        db.rollback()
        raise ChatError(2606, '授权未完成，请重新读取当前状态并核验可信服务和证据', 409, kind='authorization_unavailable') from None
    return ApiResponse(data={'id': proposal_id, 'revision': result['revision'], 'replayed': result['replayed']})
