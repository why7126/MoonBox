"""Request authorization and deliberately bounded acceptance projections."""
import json
import hashlib
import time

from sqlalchemy import select

from app.chat import service as chat
from app.governance import scope
from app.verification.acceptance_schema import operations
from app.verification.acceptance_state import AcceptanceState, online


def authorize(db, actor, operation_id, *, write=False):
    row = db.execute(select(operations).where(
        operations.c.id == operation_id, operations.c.actor_id == actor,
    )).mappings().first()
    if row is None:
        raise chat.ChatError(2703, '验收操作不存在或无权访问', 404)
    parent = chat.conversation(db, actor, row['conversation_id'])
    source = chat.turn(db, actor, row['source_turn_id'])
    if (source['conversation_id'] != parent['id'] or
            parent['space_id'] != row['space_id'] or
            parent['repository_id'] != row['repository_id']):
        raise chat.ChatError(2703, '验收操作绑定不一致', 409)
    project = scope.authorize(db, actor, row['space_id'], row['repository_id'], write=write)
    if not scope.visible(db, actor, project, row['change_id']):
        raise chat.ChatError(2703, '验收对象不可访问', 403)
    if project.binding_revision != row['binding_revision']:
        raise chat.ChatError(2702, '项目绑定已变化，请重新核验', 409)
    return dict(row), project


def public(row, *, writable=False):
    """Never serialize stored plans, filesystem paths, actor or worker credentials."""
    view = {key: row[key] for key in (
        'id', 'conversation_id', 'source_turn_id', 'change_id', 'status', 'version',
        'cleanup_state', 'reason_code', 'expires_at', 'created_at', 'updated_at',
    )}
    view['cancel_requested'] = bool(row['cancel_requested'])
    view['ready'] = bool(row['ready'])
    messages={'acceptance_template_unavailable':'尚未配置批准的验收模板',
        'acceptance_storage_unconfigured':'尚未配置隔离验收存储',
        'identity_adapter_unavailable':'测试角色适配尚未就绪',
        'environment_concurrency_limit':'验收环境名额已占用',
        'input_changed':'代码或验收计划已变化，需要重新创建验收',
        'template_changed':'部署验收模板已变化，旧结果仅作历史参考',
        'source_execution_unconfirmed':'来源执行尚未确认结束',
        'worker_interrupted':'执行中断，可在资源回收后继续',
        'user_stopped':'已主动停止，不会自动继续'}
    view['reason_message']=messages.get(row['reason_code'],'执行条件尚未就绪，请重新核验' if row['reason_code'] else None)
    view['allowed_actions'] = ['verify']
    if writable and not row['cancel_requested'] and row['status'] not in {'passed', 'failed'}:
        view['allowed_actions'].append('stop')
    if writable and row['cleanup_state']=='cleanup_failed' and not row['lease_until']:
        view['allowed_actions'].append('cleanup-retries')
    if (writable and row['status']=='blocked' and not row['cancel_requested'] and not row['lease_until']
            and row['cleanup_state'] in {'released','not_created'}
            and (not row.get('checks_deadline') or row['checks_deadline'] > time.time())
            and (not row['expires_at'] or row['expires_at'] > time.time())):
        view['allowed_actions'].append('resume')
    view['checks'] = [{
        'ac_id': check['ac_id'], 'status': check['status'],
        'reason_code': check['reason_code'],
        'evidence_available': bool(json.loads(check['evidence_json'])) and online(check),
    } for check in row['checks']]
    if any(check['evidence_available'] for check in view['checks']):
        view['allowed_actions'].append('evidence')
    return view


def evidence(db,factory,actor,operation_id):
    authorize(db,actor,operation_id)
    row=AcceptanceState(factory).get(operation_id)
    available=[check for check in row['checks'] if check['evidence_json']!='{}' and online(check)]
    if not available and any(check['evidence_json']!='{}' for check in row['checks']):
        raise chat.ChatError(2705,'验收证据已过在线保留期',410)
    return {'operation_id':operation_id,'checks':[{'ac_id':check['ac_id'],'status':check['status'],
        'evidence':json.loads(check['evidence_json'])} for check in available]}


def read(db, factory, actor, operation_id):
    _, project = authorize(db, actor, operation_id)
    row=AcceptanceState(factory).get(operation_id)
    if row['ready'] and row.get('template_digest'):
        from app.verification.acceptance_template import approved_template
        from app.verification.acceptance_state import Conflict
        try:
            if approved_template().key!=row['template_digest']:
                row.update(ready=False,reason_code='template_changed')
        except Conflict:
            row.update(ready=False,reason_code='acceptance_template_unavailable')
    view=public(row, writable=not project.readonly)
    from app.verification.acceptance_schema import archives,deliveries,tool_waits
    from app.chat.schema import turns
    if db.scalar(select(archives.c.id).where(archives.c.operation_id==operation_id,archives.c.state=='published').limit(1)):
        view['allowed_actions'].append('archive-evidence')
    linked=db.scalar(select(deliveries.c.target_turn_id).where(deliveries.c.operation_id==operation_id))
    waiting=db.scalar(select(tool_waits.c.source_turn_id).where(tool_waits.c.operation_id==operation_id,
        tool_waits.c.state.in_(['waiting','dispatching'])))
    active=db.scalar(select(turns.c.id).where(turns.c.id.in_([value for value in (linked,waiting) if value]),
        turns.c.status.in_(['queued','running','stopping'])).limit(1))
    if active and not project.readonly and not row['cancel_requested'] and 'stop' not in view['allowed_actions']:
        view['allowed_actions'].append('stop')
    return view


def stop(db, factory, actor, operation_id, version):
    authorize(db, actor, operation_id, write=True)
    return public(AcceptanceState(factory).cancel(operation_id, version))


def action(db, factory, actor, operation_id, version, action_name):
    from app.verification.acceptance_source import resolve, verify_files
    from app.verification.acceptance_state import Conflict
    row, project = authorize(db, actor, operation_id, write=True)
    state=AcceptanceState(factory)
    if action_name=='cleanup-retries':
        return public(state.request_cleanup(operation_id,version),writable=True)
    if action_name!='resume':raise Conflict('action_invalid')
    ref=json.loads(row['source_ref_json'])
    _,_,managed,point,recorded,_,source=resolve(db,actor,row['conversation_id'],row['source_turn_id'],row['change_id'],
        source_point_id=ref.get('point_id') if ref.get('kind')=='tool_checkpoint' else None)
    digest=verify_files(managed,point,recorded,project.binding_revision)
    current=hashlib.sha256(json.dumps([digest,source],sort_keys=True).encode()).hexdigest()
    if current!=row['input_digest']:raise Conflict('input_changed')
    return public(state.resume(operation_id,version),writable=True)


def list_for_conversation(db, factory, actor, conversation_id):
    chat.conversation(db, actor, conversation_id)
    identifiers = db.scalars(select(operations.c.id).where(
        operations.c.conversation_id == conversation_id, operations.c.actor_id == actor,
    ).order_by(operations.c.created_at.desc(), operations.c.id.desc()).limit(50)).all()
    return {'items': [read(db, factory, actor, identifier) for identifier in identifiers]}


def create(db, factory, actor, conversation_id, turn_id, change_id, request_key,request_id=None,*,source_point_id=None):
    from app.moonbox_core.schema import write_locks
    from app.moonbox_core.authority import delivery
    from app.verification.acceptance_source import resolve, verify_files
    from app.verification.acceptance_state import Conflict
    from app.verification.acceptance_schema import deliveries
    if db.scalar(select(deliveries.c.id).where(deliveries.c.target_turn_id==turn_id)):
        raise Conflict('resume_budget_exhausted')
    parent, project, managed, point, recorded, plan, source = resolve(
        db, actor, conversation_id, turn_id, change_id,source_point_id=source_point_id)
    holder=db.scalar(select(write_locks.c.operation_id).where(write_locks.c.workspace_id == managed[0]['id']))
    if holder and not (source_point_id and holder==turn_id):
        raise Conflict('source_workspace_busy')
    digest = verify_files(managed, point, recorded, project.binding_revision)
    # Work executes from the immutable checkpoint, never the mutable path checked here.
    input_digest = hashlib.sha256(json.dumps([digest, source], sort_keys=True).encode()).hexdigest()
    db.commit()
    # Recheck authorization after filesystem work and the repeatable-read boundary.
    current, _ = delivery(
        db, actor, parent['space_id'], parent['repository_id'], change_id)
    if current.binding_revision != project.binding_revision:
        raise Conflict('binding_changed')
    item = AcceptanceState(factory).create(actor=actor, space=parent['space_id'],
        repository=parent['repository_id'], conversation=conversation_id, turn=turn_id,
        change=change_id, request_key=request_key, binding=project.binding_revision,
        input_digest=input_digest, plan=plan, source_ref=source,request_id=request_id)
    return public(item, writable=True)
