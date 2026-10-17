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


@router.post('/governance-preparations',response_model=ApiResponse[dict],summary='准备治理动作与个人会话')
def create_preparation(payload:PreparationRequest,request:Request,user=Depends(require_session_user),db:Session=Depends(get_db)):
    request.state.chat_actor=str(user['id'])
    return ApiResponse(data=prepare(db,str(user['id']),payload.space_id,payload.repository_id,payload.object_id,
        action=payload.action,request_id=request.state.chat_request_id,idempotency_key=payload.idempotency_key))


@router.post('/object-sessions',response_model=ApiResponse[dict],summary='准备对象个人会话')
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
