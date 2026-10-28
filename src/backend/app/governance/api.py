from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field
from typing import Literal
from sqlalchemy.orm import Session
from app.api.v1.admin_auth import require_session_user
from app.chat.api import ChatRoute
from app.db.session import get_db
from app.schemas.common import ApiResponse
from app.governance.preparation import prepare, prepare_object_session, list_candidates

router=APIRouter(prefix='/api/v1/chat',tags=['Governance'],route_class=ChatRoute)


class PreparationRequest(BaseModel):
    space_id: str = Field(min_length=1,max_length=64)
    repository_id: str = Field(min_length=1,max_length=64)
    object_id: str = Field(pattern=r'^(?:REQ|BUG)-\d{4}(?:-[a-z0-9-]+)?$')
    action: Literal['req-generate','bug-generate'] = 'req-generate'
    idempotency_key: str | None = Field(default=None,min_length=1,max_length=64,pattern=r"^[A-Za-z0-9_-]+$")


class ObjectSessionRequest(BaseModel):
    space_id: str = Field(min_length=1,max_length=64)
    repository_id: str = Field(min_length=1,max_length=64)
    object_id: str = Field(pattern=r'^(?:(?:REQ|BUG)-\d{4}(?:-[A-Za-z0-9_-]+)?|[a-z0-9][a-z0-9-]{0,100})$')
    action: str = Field(default='open-chat',min_length=1,max_length=64,pattern=r'^[A-Za-z0-9_-]+$')
    idempotency_key: str | None = Field(default=None,min_length=1,max_length=64,pattern=r"^[A-Za-z0-9_-]+$")


class ObjectSessionResponse(BaseModel):
    conversation_id: str | None
    object_id: str
    object_type: str | None = None
    title: str | None = None
    action: str | None = None
    reused_conversation: bool = False
    execution_state: Literal['idle', 'running', 'needs_review', 'validated', 'recovered_valid'] = 'idle'
    can_send: bool = True
    reason_code: str | None = None
    view_conversation_id: str | None = None


class GovernancePreparationResponse(ObjectSessionResponse):
    preparation_id: str | None
    prompt: str
    state: str


@router.post('/governance-preparations',response_model=ApiResponse[GovernancePreparationResponse],summary='准备治理动作与个人会话')
def create_preparation(payload:PreparationRequest,request:Request,user=Depends(require_session_user),db:Session=Depends(get_db)):
    request.state.chat_actor=str(user['id'])
    return ApiResponse(data=prepare(db,str(user['id']),payload.space_id,payload.repository_id,payload.object_id,
        action=payload.action,request_id=request.state.chat_request_id,idempotency_key=payload.idempotency_key))


@router.post('/object-sessions',response_model=ApiResponse[ObjectSessionResponse],summary='准备对象个人会话')
def create_object_session(payload:ObjectSessionRequest,request:Request,user=Depends(require_session_user),db:Session=Depends(get_db)):
    request.state.chat_actor=str(user['id'])
    return ApiResponse(data=prepare_object_session(db,str(user['id']),payload.space_id,payload.repository_id,payload.object_id,
        action=payload.action,request_id=request.state.chat_request_id,idempotency_key=payload.idempotency_key))


@router.get('/conversations/{cid}/governance-candidates',response_model=ApiResponse[dict],summary='读取不可变治理成果')
def get_candidates(cid:str,request:Request,user=Depends(require_session_user),db:Session=Depends(get_db)):
    request.state.chat_actor=str(user['id'])
    return ApiResponse(data=list_candidates(db,str(user['id']),cid))


class ApplicationRequest(BaseModel):
    expected_manifest_hash: str = Field(pattern=r"^[a-f0-9]{64}$")
    candidate_revision: int = Field(ge=1)
    idempotency_key: str = Field(min_length=1,max_length=64,pattern=r"^[A-Za-z0-9_-]+$")
    maintenance_confirmed: bool


@router.post('/governance-candidates/{candidate_id}/applications',response_model=ApiResponse[dict],status_code=202,summary='申请应用固定治理成果')
def post_application(candidate_id:str,payload:ApplicationRequest,request:Request,user=Depends(require_session_user),db:Session=Depends(get_db)):
    from app.governance.writer import apply_candidate
    request.state.chat_actor=str(user['id'])
    return ApiResponse(data=apply_candidate(db,str(user['id']),candidate_id,**payload.model_dump(exclude={'maintenance_confirmed'}),confirmed=payload.maintenance_confirmed,request_id=request.state.chat_request_id))


@router.get('/governance-applications/{operation_id}',response_model=ApiResponse[dict],summary='读取应用与恢复状态')
def get_application(operation_id:str,request:Request,user=Depends(require_session_user),db:Session=Depends(get_db)):
    from app.governance.writer import operation
    request.state.chat_actor=str(user['id'])
    return ApiResponse(data=operation(db,str(user['id']),operation_id))


class RecoveryRequest(BaseModel):
    expected_version: int = Field(ge=1)
    idempotency_key: str = Field(min_length=1, max_length=64, pattern=r"^[A-Za-z0-9_-]+$")
    confirmed: bool


class RecoveryOperationResponse(BaseModel):
    historical_result: str = "unverified"
    admission_state: str = "blocked"
    admission_reason: str | None = None
    last_checked_at: str | None = None
    verification_reason: str | None = None
    verification_actions: list[str] = Field(default_factory=list)
    verification_differences: list[str] = Field(default_factory=list)
    id: str
    object_id: str
    action: str
    stage: str
    state: str
    version: int
    execution_terminal: str | None
    reason_code: str | None
    auto_retry_count: int
    manual_count: int
    next_retry_at: str | None
    recovery_expires_at: str | None
    candidate_id: str | None
    application_id: str | None
    allowed_actions: list[str]


class RecoveryAttemptResponse(BaseModel):
    operation_id: str
    attempt_id: str
    state: str


@router.get('/governance-operations/{operation_id}', response_model=ApiResponse[RecoveryOperationResponse], summary='只读查询治理恢复操作')
def get_recovery_operation(operation_id: str, request: Request, user=Depends(require_session_user), db: Session=Depends(get_db)):
    from app.governance.recovery_service import detail
    request.state.chat_actor = str(user['id'])
    return ApiResponse(data=detail(db, str(user['id']), operation_id))


@router.post('/governance-operations/{operation_id}/recoveries', response_model=ApiResponse[RecoveryAttemptResponse], status_code=202, summary='确认续接治理操作')
def post_recovery_operation(operation_id: str, payload: RecoveryRequest, request: Request, user=Depends(require_session_user), db: Session=Depends(get_db)):
    from app.governance.recovery_service import request_recovery
    request.state.chat_actor = str(user['id'])
    return ApiResponse(data=request_recovery(db, str(user['id']), operation_id,
        **payload.model_dump(), request_id=request.state.chat_request_id))


class RecoveryDispositionRequest(BaseModel):
    expected_version: int = Field(ge=1)
    disposition: Literal['recheck', 'retain_7_days']


@router.post('/governance-operations/{operation_id}/retention-dispositions', response_model=ApiResponse[dict], summary='管理员处置恢复证据保留')
def post_recovery_disposition(operation_id: str, payload: RecoveryDispositionRequest, request: Request,
                              user=Depends(require_session_user), db: Session=Depends(get_db)):
    from app.governance.recovery_retention import dispose
    request.state.chat_actor = str(user['id'])
    return ApiResponse(data=dispose(db, str(user['id']), operation_id, **payload.model_dump()))


class CompletionVerificationResponse(BaseModel):
    historical_result: str
    admission_state: str
    reason_code: str | None = None
    last_checked_at: str | None = None
    verification_reason: str | None = None
    verification_actions: list[str] = Field(default_factory=list)
    verification_differences: list[str] = Field(default_factory=list)


@router.post('/governance-operations/{operation_id}/verifications', response_model=ApiResponse[CompletionVerificationResponse], summary='核验原操作完成证明与准入')
def verify_completed_operation(operation_id: str, request: Request, user=Depends(require_session_user), db: Session=Depends(get_db)):
    from app.governance.completion_handoff import verify_operation
    return ApiResponse(data=verify_operation(db, str(user['id']), operation_id))


class DirectVerificationRequest(BaseModel):
    expected_version: int = Field(ge=1)


class DirectVerificationDifference(BaseModel):
    path: str
    kind: str


class AutoVerificationStatus(BaseModel):
    state: Literal['pending', 'checking', 'confirmed', 'blocked', 'unavailable']
    reason_code: str | None = None


class DirectVerificationResponse(BaseModel):
    successor_evidence: dict[str, str] = Field(default_factory=dict)
    auto_verification: AutoVerificationStatus | None = None
    available: bool
    state: str
    version: int | None
    reason_code: str | None = None
    last_checked_at: str | None = None
    can_verify: bool
    historical_evidence_missing: bool = False
    differences: list[DirectVerificationDifference] = Field(default_factory=list)


@router.get('/turns/{turn_id}/completion-verification', response_model=ApiResponse[DirectVerificationResponse], summary='查询直接命令完成核验状态')
def direct_verification_status(turn_id: str, user=Depends(require_session_user), db: Session=Depends(get_db)):
    from app.governance.direct_completion import status
    return ApiResponse(data=status(db, str(user['id']), turn_id))


@router.post('/turns/{turn_id}/completion-verification', response_model=ApiResponse[DirectVerificationResponse], summary='安全核验直接命令当前成果')
def verify_direct_completion(turn_id: str, payload: DirectVerificationRequest,
                             user=Depends(require_session_user), db: Session=Depends(get_db)):
    from app.governance.direct_completion import recover, DirectProofError
    from app.chat.service import ChatError
    try:
        return ApiResponse(data=recover(db, str(user['id']), turn_id, payload.expected_version))
    except DirectProofError as error:
        db.rollback()
        raise ChatError(2606, '成果核验未通过，原成果及保护已保留', 409,
                        kind=str(error), details={'reason': str(error)}) from None
