from __future__ import annotations

import json
import logging
import time
from uuid import uuid4
from fastapi import APIRouter, Depends, Query, Request, Header, UploadFile, File
from fastapi.responses import JSONResponse, Response, StreamingResponse
from fastapi.routing import APIRoute
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import insert, select, update
from sqlalchemy.orm import Session
from app.api.v1.admin_auth import require_session_user
from app.chat import service
from app.chat.schema import audit, turns, messages
from app.chat.settings import repository_catalog, repository_branches
from app.db.session import get_db, get_session_factory
from app.schemas.common import ApiResponse, ErrorResponse

class ChatRoute(APIRoute):
    def get_route_handler(self):
        handler = super().get_route_handler()
        async def traced(request: Request):
            rid = str(uuid4()); request.state.chat_request_id=rid; start = time.monotonic(); response = None
            metadata = {}
            try:
                response = await handler(request)
            except service.ChatError as exc:
                response = JSONResponse(status_code=exc.status, content={'code': exc.code, 'message': exc.message, 'data': {'kind': exc.kind, 'request_id': rid} if exc.kind else None})
            except HTTPException as exc:
                response = JSONResponse(status_code=exc.status_code, content={'code':1001 if exc.status_code==401 else 1002,'message':'认证或权限校验失败','data':None})
            except RequestValidationError:
                response = JSONResponse(status_code=422,content={'code':1000,'message':'请求字段校验失败','data':None})
            finally:
                try:
                    audit_metadata = {}
                    try:
                        body = json.loads(response.body) if response and getattr(response, 'body', None) else {}
                        if isinstance(body, dict) and body.get('code') not in (None, 0):
                            audit_metadata['code'] = body.get('code')
                        data = body.get('data') if isinstance(body, dict) else None
                        if self.path == '/api/v1/chat/conversations/{cid}/turns' and request.method == 'POST' and isinstance(data, dict):
                            for key in ('image_count', 'file_count', 'skill_count'):
                                value = data.get(key)
                                if type(value) is int and 0 <= value <= 100:
                                    audit_metadata[key] = value
                    except Exception:
                        audit_metadata = {}
                    metadata = dict(audit_metadata)
                    with get_session_factory()() as db:
                        db.execute(insert(audit).values(**service.identity(), request_id=rid,
                            actor_id=getattr(request.state, 'chat_actor', None), route_template=self.path,
                            method=request.method, status_code=response.status_code if response else 500,
                            duration_ms=int((time.monotonic()-start)*1000), metadata=json.dumps(audit_metadata)))
                        if request.headers.get('X-Chat-Client')=='web' and getattr(request.state,'chat_actor',None):
                            from app.chat.observability import behavior
                            names={('/api/v1/chat/conversations','POST'):'chat.session_create',('/api/v1/chat/conversations/{cid}','PATCH'):'chat.session_update',('/api/v1/chat/conversations/{cid}','DELETE'):'chat.session_delete',('/api/v1/chat/conversations/{cid}/relations','PUT'):'chat.relations_save',('/api/v1/chat/conversations/{cid}/turns','POST'):'chat.send',('/api/v1/chat/turns/{tid}/interrupt','POST'):'chat.stop',('/api/v1/chat/turns/{tid}/retries','POST'):'chat.retry'}
                            names.update({('/api/v1/requirement-center/captures','POST'):'governance.capture',
                                ('/api/v1/chat/governance-preparations','POST'):'governance.prepare',
                                ('/api/v1/chat/governance-candidates/{candidate_id}/applications','POST'):'governance.apply'})
                            if self.path.startswith('/api/v1/requirement-center/') and request.method=='PUT':
                                names[(self.path,request.method)]='governance.document_save'
                            event=names.get((self.path,request.method))
                            if event:
                                success=response is not None and response.status_code<400
                                resource={}
                                if success:
                                    # Only successful authorized results may be linked to resource identifiers.
                                    payload=json.loads(response.body).get('data',{})
                                    if event == 'governance.capture':resource['operation_id']=payload.get('id')
                                    elif event in ('chat.send','chat.retry','chat.stop'):
                                        resource['turn_id']=payload.get('id')
                                        resource['image_count']=payload.get('image_count')
                                        resource['skill_count']=payload.get('skill_count')
                                        effective=payload.get('effective_config') or {}
                                        for key in ('agent','model','reasoning'):
                                            resource[key]=effective.get(key)
                                        if payload.get('config_fallback_reason'):
                                            resource['config_fallback']='applied'
                                    else:resource['conversation_id']=payload.get('id') or request.path_params.get('cid')
                                metadata={**metadata, **{key:value for key,value in resource.items() if key in ('image_count','file_count','skill_count','agent','model','reasoning','config_fallback') and value is not None}}
                                behavior(db,event,request.state.chat_actor,rid,'success' if success else 'failure','web',resource)
                        db.execute(update(audit).where(audit.c.request_id==rid).values(metadata=json.dumps(metadata, ensure_ascii=False, sort_keys=True)))
                        db.commit()
                except Exception:
                    logging.getLogger('moonbox.chat').exception('chat.request_log_unavailable')
            timings = getattr(getattr(request.state, 'governance_reader', None), 'timings', {})
            allowed_timings = ('snapshot_and_fences_ms', 'materialize_ms', 'object_authorization_ms', 'parse_ms', 'cleanup_ms', 'total_ms')
            if timings:
                response.headers['Server-Timing'] = ', '.join(
                    f"{name.removesuffix('_ms')};dur={timings[name]:.2f}" for name in allowed_timings if name in timings)
            response.headers['X-Request-ID'] = rid
            response.headers['Cache-Control'] = 'no-store'
            return response
        return traced

router = APIRouter(prefix='/api/v1/chat', tags=['Chat'], route_class=ChatRoute,
    responses={403: {'model': ErrorResponse},404: {'model': ErrorResponse},409: {'model': ErrorResponse},503: {'model': ErrorResponse}})

def actor(request: Request, user: dict = Depends(require_session_user), client_type: str|None=Header(None,alias="X-Chat-Client",max_length=24,description="可选调用端归因标记web，不用于认证或授权")):
    request.state.chat_actor = str(user['id'])
    return str(user['id'])

class ConversationCreate(BaseModel):
    client_request_id: str | None = Field(default=None, pattern=r'^[A-Za-z0-9_-]{1,64}$', description="可选创建幂等标识，同一用户重试使用原值；不作为授权依据")
    space_id: str = Field(min_length=1,max_length=64)
    repository_id: str = Field(min_length=1,max_length=64)
    branch_name: str | None = Field(default=None, min_length=1, max_length=128)
    title: str = Field(default='新会话',min_length=1,max_length=200)
    @field_validator('title')
    @classmethod
    def title_not_blank(cls, v):
        if not v.strip(): raise ValueError('标题不能为空')
        return v.strip()

class ConversationPatch(BaseModel):
    title: str | None = Field(default=None,min_length=1,max_length=200)
    pinned: bool | None = None
    archived: bool | None = None
    @field_validator('title')
    @classmethod
    def title_not_blank(cls,v):
        if v is None or not v.strip(): raise ValueError('标题不能为空')
        return v.strip()
    @field_validator('pinned','archived')
    @classmethod
    def not_null(cls,v):
        if v is None: raise ValueError('字段不能为空')
        return v

class TurnCreate(BaseModel):
    client_request_id: str = Field(pattern=r'^[A-Za-z0-9_-]{1,64}$')
    prompt: str = Field(default='',max_length=32000)
    attachments: list[dict] = Field(default_factory=list,max_length=5,description="客户端已选择图片的引用登记摘要，不包含二进制")
    skills: list[dict] = Field(default_factory=list,max_length=5,description="当前仓库Skill上下文引用摘要，不自动执行Skill命令")
    execution_config: dict | None = Field(default=None, description="本轮请求的 Agent、模型与推理配置稳定标识")
    @field_validator('prompt')
    @classmethod
    def clean_prompt(cls,v):
        return v

class ConversationRead(BaseModel):
    id: str
    space_id: str
    repository_id: str
    branch_name: str = 'main'
    title: str
    pinned: bool
    archived: bool
    active_turn_id: str | None
    write_scope: str = Field(default='read_only', pattern=r'^(read_only|governance_write|implementation_write)$')
    write_reason_code: str = Field(default='default_read_only', max_length=80)
    created_at: str
    updated_at: str

class ConversationPage(BaseModel):
    items: list[ConversationRead]
    total: int
    page: int
    page_size: int

class TurnRead(BaseModel):
    id: str
    conversation_id: str
    client_request_id: str
    status: str
    retry_of: str | None
    error_code: str | None
    created_at: str
    updated_at: str
    image_count: int | None = None
    file_count: int | None = None
    skill_count: int | None = None
    requested_config: dict = Field(default_factory=dict)
    effective_config: dict = Field(default_factory=dict)
    config_fallback_reason: str | None = None


class BehaviorEventCreate(BaseModel):
    event_name: str = Field(pattern=r'^chat\.(image_add|image_remove|file_add|file_remove|skill_select|skill_remove|config_select)$')
    image_count: int = Field(default=0,ge=0,le=100)
    file_count: int = Field(default=0,ge=0,le=100)
    skill_count: int = Field(default=0,ge=0,le=100)
    agent: str | None = Field(default=None, pattern=r'^[A-Za-z0-9_.:-]{1,80}$')
    model: str | None = Field(default=None, pattern=r'^[A-Za-z0-9_.:-]{1,80}$')
    reasoning: str | None = Field(default=None, pattern=r'^[A-Za-z0-9_.:-]{1,80}$')

@router.get('/capabilities', response_model=ApiResponse[dict], summary='读取Chat执行就绪状态')
def capabilities(space_id: str = Query(max_length=64), uid: str = Depends(actor), db: Session = Depends(get_db)):
    service.authorize_space(db,uid,space_id)
    from app.chat.isolated import allowed
    ready=allowed(db,uid,space_id)
    repos = []
    for row in repository_catalog():
        if row['space_id'] == space_id:
            repos.append({**row, 'branches': repository_branches(row['id'], row['space_id'])})
    return ApiResponse(data={'execution_ready':ready,'reason':'仓库执行服务已就绪' if ready else '仓库执行服务尚未就绪或配置不完整',
        'repositories':repos, 'materials': service.material_capabilities(),
        'execution': service.execution_capabilities()})


@router.post('/behavior-events',response_model=ApiResponse[dict],summary='记录Chat前端材料操作行为')
def behavior_event(payload: BehaviorEventCreate,request: Request,uid: str=Depends(actor),db: Session=Depends(get_db)):
    from app.chat.observability import behavior
    behavior(db,payload.event_name,uid,request.state.chat_request_id,'success','web',
        {'image_count':payload.image_count,'file_count':payload.file_count,'skill_count':payload.skill_count,
            'agent':payload.agent,'model':payload.model,'reasoning':payload.reasoning})
    db.commit()
    return ApiResponse(data={'recorded': True})

@router.get('/conversations', response_model=ApiResponse[ConversationPage], summary='搜索本人会话')
def listing(space_id: str = Query(max_length=64), q: str = Query('',max_length=200), archived: bool=False, filter: str|None=Query(None,pattern=r'^(all|pinned)$'),
    page: int=Query(1,ge=1,le=10000), page_size: int=Query(20,ge=1,le=100), uid: str=Depends(actor), db: Session=Depends(get_db)):
    return ApiResponse(data=service.list_conversations(db,uid,space_id,q,archived,page,page_size,filter))

@router.post('/conversations',response_model=ApiResponse[ConversationRead],summary='创建个人会话')
def create(payload: ConversationCreate,uid: str=Depends(actor),db: Session=Depends(get_db)):
    return ApiResponse(data=service.create_conversation(db,uid,**payload.model_dump()))


@router.post('/materials',response_model=ApiResponse[dict],summary='上传Chat私有材料')
async def upload_material(space_id: str=Query(max_length=64),repository_id: str=Query(max_length=64),
    file: UploadFile=File(),uid: str=Depends(actor),db: Session=Depends(get_db)):
    from starlette.concurrency import run_in_threadpool
    try:
        content = await file.read(service.MATERIAL_LIMITS['max_file_bytes'] + 1)
        return ApiResponse(data=await run_in_threadpool(service.upload_material, db, uid, space_id, repository_id,
            file.filename or 'attachment', file.content_type or 'application/octet-stream', content))
    finally:
        await file.close()


@router.get('/materials/{material_id}/content',summary='授权读取Chat私有图片或文件')
def material_content(material_id: str,uid: str=Depends(actor),db: Session=Depends(get_db)):
    value=service.read_uploaded_material_content(db,uid,material_id)
    return Response(content=value['data'],media_type=value['content_type'],
        headers={'Cache-Control':'private, no-store','X-Content-Type-Options':'nosniff'})

@router.get('/conversations/{cid}',response_model=ApiResponse[ConversationRead],summary='读取个人会话')
def get(cid: str,uid: str=Depends(actor),db: Session=Depends(get_db)):
    return ApiResponse(data=service.public_conversation(service.conversation(db,uid,cid),db,uid))

@router.patch('/conversations/{cid}',response_model=ApiResponse[ConversationRead],summary='重命名置顶归档或恢复会话')
def patch(cid: str,payload: ConversationPatch,uid: str=Depends(actor),db: Session=Depends(get_db)):
    return ApiResponse(data=service.change_conversation(db,uid,cid,payload.model_dump(exclude_unset=True)))

@router.delete('/conversations/{cid}',response_model=ApiResponse[dict],summary='检查当前代码后删除会话历史，独立跟踪保留副本')
def delete(cid: str,expected_hash: str|None=Query(None,pattern=r'^[a-f0-9]{64}$'),uid: str=Depends(actor),db: Session=Depends(get_db)):
    from app.chat.cleanup import delete_history
    return ApiResponse(data=delete_history(db,uid,cid,expected_hash))

@router.post('/conversations/{cid}/turns',response_model=ApiResponse[TurnRead],summary='幂等提交轮次（执行门禁未通过时拒绝）')
def send(cid: str,payload: TurnCreate,request: Request,uid: str=Depends(actor),db: Session=Depends(get_db)):
    return ApiResponse(data=service.request_turn(db,uid,cid,payload.client_request_id,payload.prompt,images=payload.attachments,skills=payload.skills,execution_config=payload.execution_config,request_id=request.state.chat_request_id))

@router.get('/conversations/{cid}/turns',response_model=ApiResponse[dict],summary='读取轮次列表')
def history(cid: str,page: int=Query(1,ge=1,le=10000),page_size: int=Query(20,ge=1,le=100),uid: str=Depends(actor),db: Session=Depends(get_db)):
    service.conversation(db,uid,cid)
    rows=db.execute(select(turns).where(turns.c.conversation_id==cid).order_by(turns.c.created_at.desc(),turns.c.id).limit(page_size).offset((page-1)*page_size)).mappings()
    return ApiResponse(data={'items':[service.public_turn(r) for r in rows],'page':page,'page_size':page_size})

@router.get('/turns/{tid}',response_model=ApiResponse[TurnRead],summary='读取真实轮次状态')
def get_turn(tid: str,uid: str=Depends(actor),db: Session=Depends(get_db)):
    return ApiResponse(data=service.public_turn(service.turn(db,uid,tid)))

@router.post('/turns/{tid}/interrupt',response_model=ApiResponse[TurnRead],summary='请求中止当前运行')
def stop(tid: str,uid: str=Depends(actor),db: Session=Depends(get_db)):
    return ApiResponse(data=service.interrupt(db,uid,tid))

@router.get('/turns/{tid}/events',response_class=StreamingResponse,responses={200:{'content':{'text/event-stream':{}}}},summary='鉴权读取已持久化事件游标页')
def stream(tid: str,after: int=Query(0,ge=0),uid: str=Depends(actor),db: Session=Depends(get_db)):
    items=service.read_events(db,uid,tid,after)
    # Finite replay batches reauthorize on each reconnect; no token in URL.
    payload=''.join(f"id: {e['sequence']}\nevent: {e['type']}\ndata: {json.dumps(e['payload'],ensure_ascii=False)}\n\n" for e in items)
    return StreamingResponse(iter([payload or ': no-events\n\n']),media_type='text/event-stream',headers={'Cache-Control':'no-store','X-Accel-Buffering':'no'})

class DiffRead(BaseModel):
    available: bool
    reason: str | None = None
    before_hash: str | None = None
    after_hash: str | None = None
    initial_hash: str | None = None
    files: list[dict] = Field(default_factory=list)
    cumulative_files: list[dict] = Field(default_factory=list)


@router.get('/turns/{tid}/diff',response_model=ApiResponse[DiffRead],summary='读取可信差异快照')
def diff(tid: str,uid: str=Depends(actor),db: Session=Depends(get_db)):
    return ApiResponse(data=service.read_diff(db,uid,tid))


@router.get('/spaces',response_model=ApiResponse[list[dict[str,str]]],summary='读取本人可用Chat空间')
def spaces(uid: str=Depends(actor),db: Session=Depends(get_db)):
    from sqlalchemy import text
    candidates=db.execute(text('''SELECT s.id,s.name FROM admin_spaces s WHERE s.status='ACTIVE'
        AND s.deleted_at IS NULL AND (s.owner_id=:uid OR EXISTS
          (SELECT 1 FROM admin_space_members m WHERE m.space_id=s.id AND m.user_id=:uid))
        ORDER BY s.name,s.id'''),{'uid':uid}).mappings()
    result=[]
    for row in candidates:
        try:service.authorize_space(db,uid,row['id'])
        except service.ChatError:continue
        result.append({'id':row['id'],'name':row['name']})
    return ApiResponse(data=result)

@router.get('/conversations/{cid}/messages',response_model=ApiResponse[dict],summary='分页读取本人会话消息')
def conversation_messages(cid: str,page: int=Query(1,ge=1),page_size: int=Query(20,ge=1,le=100),uid: str=Depends(actor),db: Session=Depends(get_db)):
    service.conversation(db,uid,cid)
    rows=db.execute(select(messages.c.id,messages.c.turn_id,messages.c.role,messages.c.content,messages.c.created_at,
            turns.c.effective_config,turns.c.config_fallback_reason)
        .join(turns,messages.c.turn_id==turns.c.id).where(turns.c.conversation_id==cid)
        .order_by(messages.c.created_at.desc(),messages.c.id.desc()).limit(page_size).offset((page-1)*page_size)).mappings()
    items=[dict(row) for row in rows]
    material_map=service.read_turn_materials(db,[row['turn_id'] for row in items if row.get('turn_id')])
    for row in items:
        row['materials']=material_map.get(row.get('turn_id'),[])
        row['effective_config']=service._json_config(row.get('effective_config'))
    return ApiResponse(data={'items':items,'page':page,'page_size':page_size})


@router.get('/skills',response_model=ApiResponse[dict],summary='读取当前仓库Skill候选')
def skills(space_id: str=Query(max_length=64),repository_id: str=Query(max_length=64),uid: str=Depends(actor),db: Session=Depends(get_db)):
    return ApiResponse(data=service.skill_candidates(db,uid,space_id=space_id,repository_id=repository_id))


@router.get('/conversations/{cid}/skills',response_model=ApiResponse[dict],summary='读取会话仓库Skill候选')
def conversation_skills(cid: str,uid: str=Depends(actor),db: Session=Depends(get_db)):
    return ApiResponse(data=service.skill_candidates(db,uid,cid=cid))

class RelationsUpdate(BaseModel):
    primary: str | None = Field(default=None,max_length=128)
    references: list[str] = Field(default_factory=list,max_length=10)
    @field_validator('references')
    @classmethod
    def valid_references(cls, values):
        if any(not value or len(value)>128 for value in values): raise ValueError('invalid references')
        return values

@router.get('/conversations/{cid}/objects',response_model=ApiResponse[dict],summary='查询授权仓库对象候选')
def objects(cid: str,q: str=Query('',max_length=200),uid: str=Depends(actor),db: Session=Depends(get_db)):
    from app.chat.relations import candidates
    return ApiResponse(data=candidates(db,uid,service.conversation(db,uid,cid),q))

@router.get('/conversations/{cid}/relations',response_model=ApiResponse[dict],summary='读取当前关联')
def get_relations(cid: str,uid: str=Depends(actor),db: Session=Depends(get_db)):
    from app.chat.relations import read_relations
    return ApiResponse(data=read_relations(db,uid,cid))

@router.put('/conversations/{cid}/relations',response_model=ApiResponse[dict],summary='更新主对象与辅助引用')
def put_relations(cid: str,body: RelationsUpdate,uid: str=Depends(actor),db: Session=Depends(get_db)):
    from app.chat.relations import set_relations
    return ApiResponse(data=set_relations(db,uid,cid,body.primary,body.references))

@router.get('/turns/{tid}/context',response_model=ApiResponse[list[dict]],summary='读取本轮实际授权快照')
def get_context(tid: str,uid: str=Depends(actor),db: Session=Depends(get_db)):
    from app.chat.relations import read_snapshots
    return ApiResponse(data=read_snapshots(db,uid,tid))


class RetryCreate(BaseModel):
    client_request_id: str = Field(pattern=r'^[A-Za-z0-9_-]{1,64}$')

@router.post('/turns/{tid}/retries',response_model=ApiResponse[TurnRead],summary='幂等重试已确认失败或停止的轮次（执行门禁未通过时拒绝）')
def retry_turn(tid: str,payload: RetryCreate,request: Request,uid: str=Depends(actor),db: Session=Depends(get_db)):
    return ApiResponse(data=service.request_retry(db,uid,tid,payload.client_request_id,request_id=request.state.chat_request_id))


@router.get('/conversations/{cid}/deletion-check',response_model=ApiResponse[dict],summary='检查当前工作区与删除门禁')
def deletion_check(cid: str,uid: str=Depends(actor),db: Session=Depends(get_db)):
    from app.chat.cleanup import inspect_deletion
    return ApiResponse(data=inspect_deletion(db,uid,cid))

@router.get('/conversations/{cid}/cleanup',response_model=ApiResponse[dict],summary='查询已删除会话的副本清理进度')
def cleanup_status(cid: str,uid: str=Depends(actor),db: Session=Depends(get_db)):
    from app.chat.cleanup import status
    return ApiResponse(data=status(db,uid,cid))
