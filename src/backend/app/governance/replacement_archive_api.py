"""Explicit archive execution, separate from proposal and installation approvals."""
from uuid import uuid5,NAMESPACE_URL
from fastapi import APIRouter,Depends,Request
from pydantic import BaseModel,ConfigDict,Field
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from app.api.v1.admin_auth import require_session_user
from app.chat.service import ChatError
from app.db.session import get_db
from app.schemas.common import ApiResponse
from . import scope,replacement_signer
from .replacement_schema import proposals,commits
from .replacement_api import object_access
from .replacement_observability import ReplacementRoute
from .replacement_coordinator import execute

router=APIRouter(prefix='/api/v1/chat/replacement-archive-operations',tags=['Governance'],route_class=ReplacementRoute)
command_router=APIRouter(prefix='/api/v1/chat/archive-commands',tags=['Governance'],route_class=ReplacementRoute)


class ArchiveObjectRequest(BaseModel):
    model_config=ConfigDict(extra='forbid')
    space_id:str=Field(min_length=1,max_length=64)
    repository_id:str=Field(min_length=1,max_length=64)
    object_id:str=Field(pattern=r'^(?:(?:REQ|BUG)-\d{4}-[A-Za-z0-9_-]+|[a-z0-9][a-z0-9-]{0,100})$')
    confirmed:bool=Field(strict=True)


class ArchiveObjectResponse(BaseModel):
    stage:str
    operations:list['ArchiveOperationResponse']


class ArchiveRequest(BaseModel):
    model_config=ConfigDict(extra='forbid')
    proposal_id:str=Field(min_length=1,max_length=64)
    expected_revision:int=Field(ge=1,strict=True)
    proposal_digest:str=Field(pattern=r'^[a-f0-9]{64}$')
    idempotency_key:str=Field(pattern=r'^[A-Za-z0-9_-]{1,64}$')
    confirmed:bool=Field(strict=True)


class ArchiveOperationResponse(BaseModel):
    operation_id:str
    stage:str
    revision:int | None=None
    replayed:bool=False


@command_router.post('',response_model=ApiResponse[ArchiveObjectResponse],summary='通过共同提交边界执行对象归档')
def command(payload:ArchiveObjectRequest,request:Request,user=Depends(require_session_user),db:Session=Depends(get_db)):
    request.state.chat_actor=user['id']
    if not payload.confirmed:raise ChatError(2606,'请确认执行当前对象归档',409)
    from .archive_dispatch import execute_object
    try:
        result=execute_object(db,actor=user['id'],space_id=payload.space_id,repository_id=payload.repository_id,
            object_id=payload.object_id,request_id=request.state.chat_request_id)
    except (ValueError,OSError,SQLAlchemyError):
        db.rollback()
        raise ChatError(2606,'对象归档未确认完成，请核验当前阻断后重试同一对象；系统会回读原操作。',409,
            kind='archive_command_unverified') from None
    return ApiResponse(data=result)


@router.post('',response_model=ApiResponse[ArchiveOperationResponse],summary='执行或恢复同一受控归档操作')
def create(payload:ArchiveRequest,request:Request,user=Depends(require_session_user),db:Session=Depends(get_db)):
    request.state.chat_actor=user['id']
    row=db.execute(select(proposals).where(proposals.c.id==payload.proposal_id)).mappings().first()
    if not row:raise ChatError(2601,'提案不存在或无权访问',404)
    if row['state'] != 'claimed':
        raise ChatError(2606,'旧版新归档入口已停止；只有已领取的原操作可恢复',409,
                        kind='legacy_replacement_retired')
    project=scope.authorize(db,user['id'],row['space_id'],row['repository_id'],write=True)
    object_access(db,user,project,row['change_id'],write=True)
    if not payload.confirmed:raise ChatError(2606,'归档须由独立执行动作发起',409)
    oid=str(uuid5(NAMESPACE_URL,'replacement-archive:'+project.key+':'+payload.idempotency_key))
    try:
        result=execute(db,actor=user['id'],space_id=project.space_id,repository_id=project.repository_id,
            proposal_id=payload.proposal_id,operation_id=oid,expected_revision=payload.expected_revision,
            proposal_digest=payload.proposal_digest,sign=replacement_signer.sign,request_id=request.state.chat_request_id)
    except (ValueError,OSError,SQLAlchemyError):
        db.rollback()
        raise ChatError(2606,'归档未确认完成，请回读原操作。可信部署、独立签署或输入变化仍可能阻断；不要重新建立操作。',409,
                        kind='controlled_archive_unverified',details={'operation_id':oid}) from None
    return ApiResponse(data=result)


@router.get('/{operation_id}',response_model=ApiResponse[ArchiveOperationResponse],summary='回读受控归档原操作检查点')
def read(operation_id:str,request:Request,user=Depends(require_session_user),db:Session=Depends(get_db)):
    request.state.chat_actor=user['id']
    row=db.execute(select(commits).where(commits.c.id==operation_id)).mappings().first()
    if not row:raise ChatError(2601,'操作不存在或无权访问',404)
    proposal=db.execute(select(proposals).where(proposals.c.id==row['proposal_id'])).mappings().one()
    project=scope.authorize(db,user['id'],proposal['space_id'],proposal['repository_id'])
    object_access(db,user,project,proposal['change_id'])
    return ApiResponse(data={'operation_id':row['id'],'stage':row['stage'],'revision':row['revision']})
