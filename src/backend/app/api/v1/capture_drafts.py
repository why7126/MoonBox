"""Capture draft endpoints keep candidate work separate from formal writes."""
from fastapi import APIRouter, Depends, Query, Request, UploadFile, File, Response
from app.governance.capture_observability import CaptureRoute
from app.api.v1.requirement_center import get_reader
from app.governance.reader import ProjectReader
from app.governance import capture_drafts as service, capture_confirmations as confirmation, capture_media
from app.schemas.common import ApiResponse
from app.schemas.capture_drafts import (DraftUpdate, DraftResult, DraftList, VersionInput, ConfirmInput,
    ConfirmationResult, MaterialResult, DeleteResult, CaptureErrorResponse)

router=APIRouter(prefix='/api/v1/requirement-center',tags=['Capture'],route_class=CaptureRoute,
    responses={status:{'model':CaptureErrorResponse} for status in (401,403,404,409,410,413,422,503)})

@router.post('/capture-drafts',response_model=ApiResponse[DraftResult],summary='创建未编号采集草稿')
def create(reader:ProjectReader=Depends(get_reader)):
    return ApiResponse(data=service.create(reader.db,reader.actor,reader.scope))

@router.get('/capture-drafts',response_model=ApiResponse[DraftList],summary='读取本人项目采集草稿')
def listing(page:int=Query(default=1,ge=1),page_size:int=Query(default=20,ge=1,le=50),reader:ProjectReader=Depends(get_reader)):
    return ApiResponse(data=service.listing(reader.db,reader.actor,reader.scope,page,page_size))

@router.get('/capture-drafts/{draft_id}',response_model=ApiResponse[DraftResult],summary='恢复采集草稿')
def get(draft_id:str,reader:ProjectReader=Depends(get_reader)):
    return ApiResponse(data=service.public(service.get(reader.db,reader.actor,reader.scope,draft_id)))

@router.patch('/capture-drafts/{draft_id}',response_model=ApiResponse[DraftResult],summary='按版本保存候选与材料')
def save(draft_id:str,payload:DraftUpdate,reader:ProjectReader=Depends(get_reader)):
    return ApiResponse(data=service.save(reader.db,reader.actor,reader.scope,draft_id,payload.expected_revision,
        payload.model_dump(exclude={'expected_revision'},exclude_none=True)))

@router.delete('/capture-drafts/{draft_id}',response_model=ApiResponse[DeleteResult],summary='删除未确认采集草稿')
def remove(draft_id:str,payload:VersionInput,reader:ProjectReader=Depends(get_reader)):
    return ApiResponse(data=service.remove(reader.db,reader.actor,reader.scope,draft_id,payload.expected_revision))

@router.post('/capture-drafts/{draft_id}/confirmations',response_model=ApiResponse[ConfirmationResult],status_code=202,summary='确认完整候选版本')
def confirm(draft_id:str,payload:ConfirmInput,request:Request,reader:ProjectReader=Depends(get_reader)):
    return ApiResponse(data=confirmation.confirm(reader.db,reader.actor,reader.scope,draft_id,payload.expected_revision,
        payload.idempotency_key,request.state.chat_request_id))

@router.get('/capture-confirmations/{task_id}',response_model=ApiResponse[ConfirmationResult],summary='查询原确认任务')
def status(task_id:str,reader:ProjectReader=Depends(get_reader)):
    return ApiResponse(data=confirmation.status(reader.db,reader.actor,reader.scope,task_id))

@router.post('/capture-drafts/{draft_id}/materials',response_model=ApiResponse[MaterialResult],summary='上传采集私有图片')
async def upload(draft_id:str,file:UploadFile=File(),reader:ProjectReader=Depends(get_reader)):
    from starlette.concurrency import run_in_threadpool
    try:
        content=await file.read(service.LIMITS['max_image_bytes']+1)
        return ApiResponse(data=await run_in_threadpool(capture_media.upload,reader.db,reader.actor,reader.scope,draft_id,content,file.content_type))
    finally:await file.close()

@router.get('/capture-materials/{media_id}/content',summary='授权读取采集图片')
def image(media_id:str,reader:ProjectReader=Depends(get_reader)):
    value=capture_media.read(reader.db,reader.actor,reader.scope,media_id)
    return Response(content=value.data,media_type=value.content_type,headers={'Cache-Control':'private, no-store','X-Content-Type-Options':'nosniff'})

from app.schemas.capture_drafts import OrganizeResult
from app.governance import capture_organizer

@router.post('/capture-drafts/{draft_id}/organize',response_model=ApiResponse[OrganizeResult],status_code=202,summary='只读整理图文候选')
def organize(draft_id:str,payload:VersionInput,request:Request,reader:ProjectReader=Depends(get_reader)):
    from app.chat.platform import allowed
    from app.chat.service import ChatError
    if not allowed(reader.db,reader.actor,reader.scope.space_id,reader.scope.repository_id):
        raise ChatError(2605,'图文整理服务未就绪，材料已保留，请稍后重试',503)
    return ApiResponse(data=capture_organizer.start(reader.db,reader.actor,reader.scope,draft_id,payload.expected_revision,request.state.chat_request_id))

@router.get('/capture-drafts/{draft_id}/organize-tasks/{task_id}',response_model=ApiResponse[OrganizeResult],summary='读取整理建议但不覆盖草稿')
def organized(draft_id:str,task_id:str,reader:ProjectReader=Depends(get_reader)):
    return ApiResponse(data=capture_organizer.status(reader.db,reader.actor,reader.scope,draft_id,task_id))

from app.schemas.capture_drafts import CapabilitiesResult

@router.get('/capture-capabilities',response_model=ApiResponse[CapabilitiesResult],summary='读取采集限制与服务状态')
def capabilities(reader:ProjectReader=Depends(get_reader)):
    from app.governance.readiness import status
    from app.chat.platform import allowed
    ready=allowed(reader.db,reader.actor,reader.scope.space_id,reader.scope.repository_id)
    writing=status(reader.db,reader.scope)
    return ApiResponse(data={'limits':service.LIMITS,'organize_ready':ready,
        'organize_reason':'' if ready else '图文整理服务未就绪','write_ready':writing['ready'],'write_reason':writing['reason']})

from app.schemas.capture_drafts import SourceResult

@router.post('/capture-confirmations/{task_id}/retries',response_model=ApiResponse[ConfirmationResult],summary='校验后续作原确认任务')
def retry(task_id:str,reader:ProjectReader=Depends(get_reader)):
    return ApiResponse(data=confirmation.retry(reader.db,reader.actor,reader.scope,task_id))

@router.get('/capture-sources/{issue_id}',response_model=ApiResponse[SourceResult],summary='读取已创建采集记录的授权来源')
def source(issue_id:str,reader:ProjectReader=Depends(get_reader)):
    return ApiResponse(data=confirmation.source(reader.db,reader.actor,reader.scope,issue_id))
