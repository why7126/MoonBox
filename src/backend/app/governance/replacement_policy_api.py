"""Separate first-installation approval; never reuse ordinary proposal approval."""
import json
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select, text
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.api.v1.admin_auth import require_session_user
from app.chat.api import ChatRoute
from app.chat.service import ChatError
from app.db.session import get_db
from app.schemas.common import ApiResponse
from . import scope, replacement_trust, replacement_signer, replacement_activation
from .replacement_bootstrap import Installation
from .replacement_schema import activations
from .replacement_authorization import require_owner
from .replacement_api import object_access
from .replacement_observability import ReplacementRoute

router=APIRouter(prefix='/api/v1/chat/replacement-policy',tags=['Governance'],route_class=ReplacementRoute)


class InstallationPrepare(BaseModel):
    model_config=ConfigDict(extra='forbid')
    space_id: str=Field(min_length=1,max_length=64)
    repository_id: str=Field(min_length=1,max_length=64)
    manifest: Installation
    ops_receipt: dict


class InstallationConfirm(BaseModel):
    model_config=ConfigDict(extra='forbid')
    space_id: str=Field(min_length=1,max_length=64)
    repository_id: str=Field(min_length=1,max_length=64)
    expected_revision: int=Field(ge=1,strict=True)
    manifest_hash: str=Field(pattern=r'^[a-f0-9]{64}$')
    confirmed: bool=Field(strict=True)


class PolicyStatus(BaseModel):
    state: str
    revision: int | None=None
    manifest_hash: str | None=None
    mechanism_change: str | None=None
    from_policy: str | None=None
    to_policy: str | None=None
    can_confirm: bool=False
    can_resume: bool=False
    operation_id: str | None=None
    trust_status: str
    can_prepare: bool=False
    review: dict | None=None
    stage: str | None=None
    blockers: list[str]=Field(default_factory=list)


class InstallationPreview(BaseModel):
    model_config=ConfigDict(extra='forbid')
    space_id: str=Field(min_length=1,max_length=64)
    repository_id: str=Field(min_length=1,max_length=64)
    mechanism_change: str=Field(pattern=r'^[a-z0-9][a-z0-9-]{0,100}$')


@router.post('/preview',response_model=ApiResponse[dict],summary='只读生成可独立审阅的精确策略转换清单')
def preview(payload:InstallationPreview,request:Request,user=Depends(require_session_user),db:Session=Depends(get_db)):
    raise ChatError(2606,'旧版首次启用流程已退出当前产品',409,kind='legacy_installation_retired')
    request.state.chat_actor=user['id']
    project=scope.authorize(db,user['id'],payload.space_id,payload.repository_id,write=True)
    object_access(db,user,project,payload.mechanism_change,write=True)
    existing=db.execute(select(activations).where(activations.c.scope_key==project.key)).mappings().first()
    from .replacement_installation import build,describe
    try:
        trust=replacement_trust.load(project.root)
        if existing:
            manifest=Installation.model_validate(json.loads(existing['manifest']))
            if manifest.mechanism_change!=payload.mechanism_change:raise ValueError('bootstrap_operation_exists')
            review=describe(project,manifest)
        else:
            review=build(project,payload.mechanism_change,trust)
    except (ValueError,OSError,KeyError,TypeError):
        raise ChatError(2606,'无法生成可信清单：请检查部署工具、当前验收和机制规格；已有操作须沿原清单处理。',409,kind='bootstrap_preview_blocked') from None
    return ApiResponse(data=review)


@router.get('',response_model=ApiResponse[PolicyStatus],summary='读取首次策略启用的独立授权状态')
def status(space_id:str,repository_id:str,request:Request,user=Depends(require_session_user),db:Session=Depends(get_db)):
    request.state.chat_actor=user['id']
    project=scope.authorize(db,user['id'],space_id,repository_id)
    try: trust=replacement_trust.load(project.root);trusted=True
    except ValueError: trusted=False
    row=db.execute(select(activations).where(activations.c.scope_key==project.key)).mappings().first()
    result={'state':'not_enabled','trust_status':'trusted' if trusted else 'policy_not_trusted',
            'can_prepare':not project.readonly,
            'blockers':[] if trusted else ['尚未配置仓库外可信根；请由运维完成部署检查。']}
    if row:
        manifest=Installation.model_validate(json.loads(row['manifest']))
        object_access(db,user,project,manifest.mechanism_change)
        owner=db.scalar(text('SELECT owner_id FROM admin_spaces WHERE id=:space'),{'space':project.space_id})
        authorization_current = False
        if trusted:
            try:
                bindings={'project_id':project.key,'binding_revision':project.binding_revision,
                    'installation_digest':row['manifest_hash'],'operation_id':manifest.operation_id,
                    'release_digest':trust.release_digest}
                trust.verify(json.loads(row['ops_receipt']),purpose='bootstrap.ops',bindings=bindings,
                    historical=row['state'] in {'activating','active'})
                if row['state'] in {'authorized','activating','active'}:
                    trust.verify(json.loads(row['owner_receipt']),purpose='bootstrap.owner',
                        bindings=bindings if row['state']=='active' else {**bindings,'actor_id':owner},
                        historical=row['state'] in {'activating','active'})
                authorization_current=True
            except (ValueError,TypeError,KeyError):
                pass
        result.update(state=row['state'],revision=row['revision'],manifest_hash=row['manifest_hash'],
            mechanism_change=manifest.mechanism_change,from_policy=manifest.from_policy,to_policy=manifest.to_policy,
            operation_id=row['operation_id'],
            can_confirm=authorization_current and not project.readonly and owner==user['id'] and row['state']=='prepared',
            can_resume=authorization_current and not project.readonly and row['state'] in {'authorized','activating'})
        result['stage']=row.get('stage')
        try:
            from .replacement_installation import describe
            result['review']=describe(project,manifest)
        except (ValueError,OSError,KeyError,TypeError):
            result['can_confirm']=False
            result['blockers'].append('精确转换详情与当前文件不一致；请核验原操作，不能凭旧摘要继续批准。')
        if not authorization_current:result['blockers'].append('独立运维授权缺失、过期或信任已变化，请由运维重新核验原清单。')
        if project.readonly:result['blockers'].append('当前项目或成员仅有读取权限。')
        elif owner!=user['id'] and row['state']=='prepared':result['blockers'].append('请由当前空间所有者独立确认本项目转换。')
    return ApiResponse(data=result)


@router.post('',response_model=ApiResponse[PolicyStatus],summary='准备已获运维制品授权的精确策略转换')
def prepare(payload:InstallationPrepare,request:Request,user=Depends(require_session_user),db:Session=Depends(get_db)):
    raise ChatError(2606,'旧版运维制品授权入口已停止',409,kind='legacy_installation_retired')
    request.state.chat_actor=user['id']
    project=scope.authorize(db,user['id'],payload.space_id,payload.repository_id,write=True)
    object_access(db,user,project,payload.manifest.mechanism_change,write=True)
    if len(json.dumps(payload.ops_receipt).encode())>16384:raise ChatError(2606,'运维收据超过允许大小',409)
    try:
        trust=replacement_trust.load(project.root)
        row=replacement_activation.prepare(db,project,payload.manifest,payload.ops_receipt,trust)
        db.commit()
    except (ValueError,OSError,KeyError,TypeError,SQLAlchemyError):
        db.rollback();raise ChatError(2606,'可信制品、精确转换或独立运维授权未通过核验',409,kind='policy_not_trusted') from None
    return ApiResponse(data={'state':row['state'],'revision':row['revision'],'manifest_hash':row['manifest_hash'],'trust_status':'trusted'})


@router.post('/confirm',response_model=ApiResponse[PolicyStatus],summary='所有者独立确认项目策略转换')
def confirm(payload:InstallationConfirm,request:Request,user=Depends(require_session_user),db:Session=Depends(get_db)):
    raise ChatError(2606,'旧版项目首次启用确认入口已停止；已开始的原操作可按检查点恢复',409,
                    kind='legacy_installation_retired')
    request.state.chat_actor=user['id']
    project=scope.authorize(db,user['id'],payload.space_id,payload.repository_id,write=True)
    operation=db.execute(select(activations).where(activations.c.scope_key==project.key)).mappings().first()
    if not operation:raise ChatError(2601,'转换清单不存在或无权访问',404)
    object_access(db,user,project,Installation.model_validate(json.loads(operation['manifest'])).mechanism_change,write=True)
    require_owner(db,user,project)
    if not payload.confirmed: raise ChatError(2606,'请确认精确转换清单',409)
    try:
        trust=replacement_trust.load(project.root)
        row=replacement_activation.confirm(db,project,user['id'],payload.expected_revision,payload.manifest_hash,trust,replacement_signer.sign)
        db.commit()
        from .replacement_bootstrap_executor import execute
        row=execute(db,actor=user['id'],space_id=project.space_id,repository_id=project.repository_id,
            manifest_hash=payload.manifest_hash,sign=replacement_signer.sign)
    except (ValueError,OSError,KeyError,TypeError,SQLAlchemyError):
        db.rollback();raise ChatError(2606,'转换尚未完成，请读取原操作状态并按恢复指引核验可信制品',409,kind='bootstrap_not_ready') from None
    return ApiResponse(data={**row,'trust_status':'trusted'})


@router.post('/resume',response_model=ApiResponse[PolicyStatus],summary='依据原清单恢复首次策略转换')
def resume(payload:InstallationConfirm,request:Request,user=Depends(require_session_user),db:Session=Depends(get_db)):
    request.state.chat_actor=user['id']
    project=scope.authorize(db,user['id'],payload.space_id,payload.repository_id,write=True)
    operation=db.execute(select(activations).where(activations.c.scope_key==project.key)).mappings().first()
    if not operation:raise ChatError(2601,'转换清单不存在或无权访问',404)
    object_access(db,user,project,Installation.model_validate(json.loads(operation['manifest'])).mechanism_change,write=True)
    if not payload.confirmed:raise ChatError(2606,'请确认继续原转换',409)
    if operation['revision']!=payload.expected_revision or operation['manifest_hash']!=payload.manifest_hash:
        raise ChatError(2606,'转换状态已变化，请重新读取原操作',409,kind='bootstrap_revision_changed')
    from .replacement_bootstrap_executor import execute
    try:
        row=execute(db,actor=user['id'],space_id=project.space_id,repository_id=project.repository_id,
            manifest_hash=payload.manifest_hash,sign=replacement_signer.sign)
    except (ValueError,OSError,KeyError,TypeError,SQLAlchemyError):
        db.rollback();raise ChatError(2606,'原转换仍有阻断，请核验可信服务、当前权限与现场状态',409,kind='bootstrap_recovery_blocked') from None
    return ApiResponse(data={**row,'trust_status':'trusted'})
